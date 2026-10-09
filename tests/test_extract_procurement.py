from copy import deepcopy

import pytest

from rules.d_extract.procurement import CONTRACT, RULE_ID, calculate


POLICY = (
    "사적 구매 약정: 필요한 수량을 포장 단위로 올림하고 최소 포장 주문량을 적용한다. "
    "상품 포장금액 합계에서 포함 세액은 합계×10//11, 별도 세액은 합계//10으로 산출한다. "
    "상품 세금 포함 합계가 무료배송 기준 이상이면 배송비는 0원이며 배송비는 자체 세금표시로 "
    "따로 나눈다. 달력일 납기, 견적효력과 재고를 만족한 견적만 비교한다. "
    "최종 총액, 정규화 공급사, 견적 ID 오름차순으로 선택한다."
)


def test_common_registry_uses_actual_quote_documents(tmp_path):
    from KrRubberStamp.registry import calculate as registered_calculate
    from render.authored import render_authored
    from render.documents import restore_scenario

    facts = source(
        quote(quote_id="A", vendor="(주) 저단가"),
        quote(
            quote_id="B",
            vendor="㈜ 적정포장",
            pack_units=6,
            pack_price=600,
            shipping_price=700,
            free_shipping_at=1320,
        ),
    )
    documents = [
        {
            "filename": "구매요청.pdf",
            "format": "pdf",
            "title": "필요 수량과 실제 구매비 비교 약정",
            "note": "개당 표시 가격과 포장 구매 및 배송의 최종 금액을 구분합니다.",
            "fields": [
                "source_contract",
                "processing_policy",
                "item",
                "base_unit",
                "required_units",
                "order_date",
                "latest_delivery_date",
            ],
        },
        {
            "filename": "갑견적.xlsx",
            "format": "xlsx",
            "title": "첫 공급사 포장 판매와 배송 조건",
            "note": "최소 포장 수와 실제 주문 가능 재고를 함께 확인합니다.",
            "fields": ["quotes.0"],
        },
        {
            "filename": "을견적.hwpx",
            "format": "hwpx",
            "title": "다른 공급사의 무료배송 기준과 납기",
            "note": "상품 세금 포함 금액이 무료배송 기준에 도달하는지 대조합니다.",
            "fields": ["quotes.1"],
        },
    ]
    render_authored(facts, tmp_path, "D_extract", documents)
    restored = restore_scenario(tmp_path)
    assert restored == facts
    answer, trace = registered_calculate("D_extract", restored)
    assert answer["chosen_quote_id"] == "B"
    assert answer["chosen_total"] == 1320
    assert answer["quote_comparisons"][0]["total"] == 2530
    assert trace[0]["rule_id"] == RULE_ID


def quote(**changes):
    return {
        "quote_id": "Q1",
        "vendor": "주식회사 Alpha",
        "valid_from": "2026-10-01",
        "valid_until": "2026-10-31",
        "pack_units": 10,
        "pack_price": 900,
        "price_includes_vat": False,
        "minimum_packs": 1,
        "shipping_price": 500,
        "shipping_price_includes_vat": False,
        "free_shipping_at": None,
        "stock_packs": 10,
        "lead_days": 2,
        **changes,
    }


def source(*quotes, **changes):
    return {
        "source_contract": CONTRACT,
        "processing_policy": POLICY,
        "item": "Ａ ４ 용지",
        "base_unit": "장",
        "required_units": 11,
        "order_date": "2026-10-09",
        "latest_delivery_date": "2026-10-11",
        "quotes": list(quotes) or [quote()],
        **changes,
    }


def test_manual_pack_purchase_beats_lower_unit_price():
    # A: unit price 90, buy 20 for 1,800 + 180 tax + 500 + 50 shipping = 2,530.
    # B: unit price 100, buy 12 for 1,200 + 120 tax and free shipping = 1,320.
    answer, trace = calculate(
        source(
            quote(quote_id="A", vendor="(주) 저단가"),
            quote(
                quote_id="B",
                vendor="㈜ 적정포장",
                pack_units=6,
                pack_price=600,
                shipping_price=700,
                free_shipping_at=1320,
            ),
        )
    )
    assert answer == {
        "quote_comparisons": [
            {
                "quote_id": "A",
                "vendor": "저단가",
                "packs": 2,
                "obtained_units": 20,
                "leftover_units": 9,
                "merchandise_supply": 1800,
                "merchandise_vat": 180,
                "merchandise_total": 1980,
                "shipping_supply": 500,
                "shipping_vat": 50,
                "shipping_total": 550,
                "supply": 2300,
                "vat": 230,
                "total": 2530,
                "delivery_date": "2026-10-11",
                "valid_on_order": True,
                "stock_sufficient": True,
                "delivered_in_time": True,
                "eligible": True,
            },
            {
                "quote_id": "B",
                "vendor": "적정포장",
                "packs": 2,
                "obtained_units": 12,
                "leftover_units": 1,
                "merchandise_supply": 1200,
                "merchandise_vat": 120,
                "merchandise_total": 1320,
                "shipping_supply": 0,
                "shipping_vat": 0,
                "shipping_total": 0,
                "supply": 1200,
                "vat": 120,
                "total": 1320,
                "delivery_date": "2026-10-11",
                "valid_on_order": True,
                "stock_sufficient": True,
                "delivered_in_time": True,
                "eligible": True,
            },
        ],
        "chosen_quote_id": "B",
        "chosen_vendor": "적정포장",
        "chosen_total": 1320,
        "chosen_leftover_units": 1,
        "eligible_quote_count": 2,
    }
    assert len(trace) == 1
    assert trace[0]["rule_id"] == RULE_ID
    assert trace[0]["inputs"]["processing_policy"] == POLICY
    assert trace[0]["output"]["normalized_item"] == "a4용지"
    assert trace[0]["output"]["base_unit"] == "장"
    assert trace[0]["output"]["selection"]["chosen_tie_break_tuple"] == [1320, "적정포장", "B"]


@pytest.mark.parametrize("required,minimum,packs", [(10, 1, 1), (11, 1, 2), (10, 3, 3)])
def test_minimum_order_and_integer_ceiling_boundaries(required, minimum, packs):
    answer, _ = calculate(source(quote(minimum_packs=minimum), required_units=required))
    row = answer["quote_comparisons"][0]
    assert row["packs"] == packs
    assert row["obtained_units"] == packs * 10
    assert row["leftover_units"] == packs * 10 - required


@pytest.mark.parametrize(
    "threshold,shipping", [(None, 550), (1981, 550), (1980, 0), (1979, 0), (0, 0)]
)
def test_free_shipping_uses_tax_included_merchandise_boundary(threshold, shipping):
    answer, _ = calculate(source(quote(free_shipping_at=threshold)))
    row = answer["quote_comparisons"][0]
    assert row["merchandise_total"] == 1980
    assert row["shipping_total"] == shipping


def test_manual_component_vat_splits_without_per_unit_rounding():
    # Included goods: 2 * 1101 = 2202; supply floor(22020/11) = 2001, tax = 201.
    # Excluded shipping: 101 + floor(101/10) = 111. Final = 2313.
    # Excluded goods: 2 * 1009 = 2018; tax = 201. Included shipping 111 => 100+11.
    answer, _ = calculate(
        source(
            quote(
                quote_id="IN",
                pack_units=3,
                pack_price=1101,
                price_includes_vat=True,
                shipping_price=101,
            ),
            quote(
                quote_id="EX",
                pack_units=3,
                pack_price=1009,
                shipping_price=111,
                shipping_price_includes_vat=True,
            ),
            required_units=4,
        )
    )
    excluded, included = answer["quote_comparisons"]
    assert (included["merchandise_supply"], included["merchandise_vat"]) == (2001, 201)
    assert (included["shipping_supply"], included["shipping_vat"]) == (101, 10)
    assert (included["supply"], included["vat"], included["total"]) == (2102, 211, 2313)
    assert (excluded["merchandise_supply"], excluded["merchandise_vat"]) == (2018, 201)
    assert (excluded["shipping_supply"], excluded["shipping_vat"]) == (100, 11)
    assert (excluded["supply"], excluded["vat"], excluded["total"]) == (2118, 212, 2330)
    assert answer["chosen_quote_id"] == "IN"


@pytest.mark.parametrize(
    "changes,flag,expected",
    [
        ({"valid_from": "2026-10-09"}, "valid_on_order", True),
        ({"valid_until": "2026-10-09"}, "valid_on_order", True),
        ({"valid_from": "2026-10-10"}, "valid_on_order", False),
        ({"valid_until": "2026-10-08"}, "valid_on_order", False),
        ({"stock_packs": 2}, "stock_sufficient", True),
        ({"stock_packs": 1}, "stock_sufficient", False),
        ({"lead_days": 2}, "delivered_in_time", True),
        ({"lead_days": 3}, "delivered_in_time", False),
    ],
)
def test_eligibility_inclusive_boundaries(changes, flag, expected):
    answer, _ = calculate(source(quote(**changes)))
    row = answer["quote_comparisons"][0]
    assert row[flag] is expected
    assert row["eligible"] is expected
    assert answer["eligible_quote_count"] == int(expected)
    assert (answer["chosen_quote_id"] == "Q1") is expected


def test_calendar_delivery_crosses_leap_day():
    answer, _ = calculate(
        source(
            quote(valid_from="2028-02-01", valid_until="2028-03-31"),
            order_date="2028-02-28",
            latest_delivery_date="2028-03-01",
        )
    )
    assert answer["quote_comparisons"][0]["delivery_date"] == "2028-03-01"
    assert answer["chosen_quote_id"] == "Q1"


def test_ineligible_low_cost_quote_cannot_win_and_no_eligible_returns_none():
    answer, _ = calculate(
        source(quote(quote_id="FREE", pack_price=0, stock_packs=0), quote(quote_id="PAID"))
    )
    assert answer["chosen_quote_id"] == "PAID"
    answer, trace = calculate(source(quote(stock_packs=0)))
    assert answer["eligible_quote_count"] == 0
    assert all(
        answer[field] is None
        for field in ("chosen_quote_id", "chosen_vendor", "chosen_total", "chosen_leftover_units")
    )
    assert trace[0]["output"]["selection"]["reason"] == "no_eligible_quote"


def test_total_tie_uses_normalized_vendor_then_quote_id():
    answer, trace = calculate(
        source(
            quote(quote_id="Q0", vendor="주식회사 Zebra"),
            quote(quote_id="Q2", vendor="주식회사 ALPHA"),
            quote(quote_id="Q1", vendor="㈜ A l p h a"),
        )
    )
    assert answer["chosen_quote_id"] == "Q1"
    assert trace[0]["output"]["selection"]["eligible_tie_break_tuples"] == [
        [2530, "alpha", "Q1"],
        [2530, "alpha", "Q2"],
        [2530, "zebra", "Q0"],
    ]


def test_duplicate_and_input_order_invariance_without_mutation():
    q1 = quote(quote_id="Q1")
    q2 = quote(quote_id="Q2", pack_price=700)
    original = source(q2, q1, deepcopy(q2))
    before = deepcopy(original)
    answer, trace = calculate(original)
    reversed_input = deepcopy(original)
    reversed_input["quotes"].reverse()
    assert calculate(reversed_input) == (answer, trace)
    unique_answer, unique_trace = calculate(source(q1, q2))
    assert answer == unique_answer
    assert trace[0]["output"]["deduplicated_quote_ids"] == ["Q2"]
    assert unique_trace[0]["output"]["deduplicated_quote_ids"] == []
    assert original == before
    answer["quote_comparisons"][0]["total"] = -1
    trace[0]["inputs"]["quotes"][0]["pack_price"] = -1
    assert original == before
    assert trace[0]["output"]["comparison"] == unique_answer


@pytest.mark.parametrize("changes", [{"pack_price": 901}, {"vendor": "Alpha"}, {"lead_days": 3}])
def test_conflicting_duplicate_rejected(changes):
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        calculate(source(quote(), quote(**changes)))


@pytest.mark.parametrize(
    "field",
    [
        "pack_units",
        "pack_price",
        "minimum_packs",
        "shipping_price",
        "free_shipping_at",
        "stock_packs",
        "lead_days",
    ],
)
@pytest.mark.parametrize("value", [True, False, 1.0, "1", -1])
def test_quote_integers_reject_bool_float_strings_and_negative(field, value):
    with pytest.raises(ValueError, match="integer"):
        calculate(source(quote(**{field: value})))


@pytest.mark.parametrize("field", ["pack_units", "minimum_packs"])
def test_positive_pack_counts_reject_zero(field):
    with pytest.raises(ValueError, match="integer"):
        calculate(source(quote(**{field: 0})))


@pytest.mark.parametrize("value", [True, False, 1.0, "1", 0, -1, None])
def test_required_units_strict_positive_integer(value):
    with pytest.raises(ValueError, match="integer"):
        calculate(source(required_units=value))


@pytest.mark.parametrize("field", ["price_includes_vat", "shipping_price_includes_vat"])
@pytest.mark.parametrize("value", [0, 1, "true", None])
def test_vat_flags_require_actual_booleans(field, value):
    with pytest.raises(ValueError, match="boolean"):
        calculate(source(quote(**{field: value})))


@pytest.mark.parametrize("field", ["valid_from", "valid_until"])
@pytest.mark.parametrize("value", ["20261009", "2026-10-9", "2026-02-30", None])
def test_quote_dates_require_strict_iso_calendar_date(field, value):
    with pytest.raises(ValueError):
        calculate(source(quote(**{field: value})))


@pytest.mark.parametrize("field", ["order_date", "latest_delivery_date"])
@pytest.mark.parametrize("value", ["20261009", "2026-10-9", "2026-02-30", None])
def test_top_dates_require_strict_iso_calendar_date(field, value):
    with pytest.raises(ValueError):
        calculate(source(**{field: value}))


def test_reversed_dates_and_unrepresentable_delivery_rejected():
    with pytest.raises(ValueError, match="validity"):
        calculate(source(quote(valid_from="2026-11-01")))
    with pytest.raises(ValueError, match="predates"):
        calculate(source(latest_delivery_date="2026-10-08"))
    with pytest.raises(ValueError, match="calendar range"):
        calculate(source(quote(lead_days=10**30)))


@pytest.mark.parametrize("field", ["quote_id", "vendor"])
@pytest.mark.parametrize("value", ["", "  ", None, 1])
def test_quote_identity_nonempty_strings(field, value):
    with pytest.raises(ValueError):
        calculate(source(quote(**{field: value})))


@pytest.mark.parametrize("field", ["processing_policy", "item", "base_unit"])
@pytest.mark.parametrize("value", ["", "  ", None, 1])
def test_top_text_requires_nonempty_strings(field, value):
    with pytest.raises(ValueError):
        calculate(source(**{field: value}))


def test_empty_normalized_vendor_and_malformed_quote_shape_rejected():
    with pytest.raises(ValueError, match="normalizes"):
        calculate(source(quote(vendor="주식회사")))
    malformed = quote()
    malformed.pop("lead_days")
    with pytest.raises(ValueError, match="fields"):
        calculate(source(malformed))
    with pytest.raises(ValueError, match="fields"):
        calculate(source(quote(extra="ignored")))
    with pytest.raises(ValueError, match="fields"):
        calculate(source(quotes=["not a row"]))


@pytest.mark.parametrize("value", [[], None, {}, "not a list"])
def test_quotes_require_nonempty_list(value):
    with pytest.raises(ValueError, match="nonempty list"):
        calculate(source(quotes=value))


@pytest.mark.parametrize("value", [None, [], {}, {"source_contract": "wrong"}])
def test_unknown_contract_rejected(value):
    with pytest.raises(ValueError, match="source contract"):
        calculate(value)


def test_zero_cost_quote_and_base_unit_preserved():
    answer, trace = calculate(
        source(quote(pack_price=0, shipping_price=0, stock_packs=2), base_unit="세트 ")
    )
    assert answer["chosen_total"] == 0
    assert trace[0]["output"]["base_unit"] == "세트 "


def test_large_integer_ceiling_is_exact_above_float_precision():
    units = 2**60 + 1
    answer, _ = calculate(
        source(quote(pack_units=2, stock_packs=units, pack_price=1), required_units=units)
    )
    row = answer["quote_comparisons"][0]
    assert row["packs"] == 2**59 + 1
    assert row["obtained_units"] == 2**60 + 2
    assert row["leftover_units"] == 1
