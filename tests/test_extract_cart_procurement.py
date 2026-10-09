from copy import deepcopy

import pytest

from rules.d_extract.cart_procurement import CONTRACT, RULE_ID, calculate


POLICY = (
    "각 품목은 한 견적에서 필요한 포장 수와 최소 주문 수 중 큰 수만 구매한다. "
    "공급사 ID별 상품 세금 포함 합계를 무료배송 기준과 비교하고 배송비를 한 번 적용한다. "
    "달력일 납기와 유효기간 및 재고가 적합한 전체 조합의 최종 금액을 비교한다. "
    "상품과 배송비 각각 포함 세액은 금액×10//11로 공급가액을 나누고 별도 세액은 금액//10이다. "
    "동률이면 품목 ID 순으로 정규화 업체명과 업체 ID 및 견적 ID를 비교한다."
)


def item(identity, **changes):
    return {
        "item_id": identity,
        "name": identity,
        "base_unit": "개",
        "required_units": 1,
        **changes,
    }


def vendor(identity, **changes):
    return {
        "vendor_id": identity,
        "name": f"주식회사 {identity}",
        "shipping_price": 0,
        "shipping_price_includes_vat": False,
        "free_shipping_at": None,
        **changes,
    }


def offer(identity, item_id, vendor_id, price, **changes):
    return {
        "quote_id": identity,
        "item_id": item_id,
        "vendor_id": vendor_id,
        "valid_from": "2026-10-01",
        "valid_until": "2026-10-31",
        "pack_units": 1,
        "pack_price": price,
        "price_includes_vat": False,
        "minimum_packs": 1,
        "stock_packs": 10,
        "lead_days": 2,
        **changes,
    }


def source(**changes):
    return {
        "source_contract": CONTRACT,
        "processing_policy": POLICY,
        "order_date": "2026-10-09",
        "latest_delivery_date": "2026-10-11",
        "items": [item("A"), item("B")],
        "vendors": [vendor("V1", shipping_price=400), vendor("V2")],
        "offers": [
            offer("Q1", "A", "V1", 1000),
            offer("Q2", "B", "V1", 500),
            offer("Q3", "A", "V2", 1500),
            offer("Q4", "B", "V2", 800),
        ],
        **changes,
    }


def test_manual_whole_cart_cost_changes_independent_landed_price_choice():
    answer, trace = calculate(source())
    # V1 both: 1100 + 550 + 440 = 2090. V2 both: 1650 + 880 = 2530.
    # Mixed V1A/V2B = 2420; V2A/V1B = 2640. Individual landed picks are mixed.
    assert answer["grand_total"] == 2090
    assert answer["supply_total"] == 1900
    assert answer["vat_total"] == 190
    assert [row["quote_id"] for row in answer["chosen_offers"]] == ["Q1", "Q2"]
    assert answer["vendor_cart_totals"] == [
        {
            "vendor_id": "V1",
            "vendor": "v1",
            "merchandise_supply": 1500,
            "merchandise_vat": 150,
            "merchandise_total": 1650,
            "shipping_free": False,
            "shipping_supply": 400,
            "shipping_vat": 40,
            "shipping_total": 440,
            "supply": 1900,
            "vat": 190,
            "total": 2090,
        }
    ]
    assert answer["feasible_cart_count"] == 4
    assert len(trace) == 1 and trace[0]["rule_id"] == RULE_ID
    assert [row["grand_total"] for row in trace[0]["output"]["selection"]["evaluated_carts"]] == [
        2090,
        2420,
        2530,
        2640,
    ]
    assert trace[0]["inputs"]["processing_policy"] == POLICY


def test_aggregate_free_shipping_crosses_boundary_and_reverses_cheapest_cart():
    facts = source(
        vendors=[vendor("V1", shipping_price=500, free_shipping_at=1100), vendor("V2")],
        offers=[
            offer("Q1", "A", "V1", 500),
            offer("Q2", "B", "V1", 500),
            offer("Q3", "A", "V2", 550),
            offer("Q4", "B", "V2", 550),
        ],
    )
    answer, _ = calculate(facts)
    assert answer["grand_total"] == 1100
    assert answer["vendor_cart_totals"][0]["shipping_free"] is True
    assert all(row["merchandise_total"] < 1100 for row in answer["chosen_offers"])
    facts["vendors"][0]["free_shipping_at"] = 1101
    other, _ = calculate(facts)
    assert other["grand_total"] == 1210
    assert [row["quote_id"] for row in other["chosen_offers"]] == ["Q3", "Q4"]


def test_floor_each_offer_before_vendor_sum_and_shipping_independently():
    answer, _ = calculate(
        source(
            vendors=[vendor("V1", shipping_price=11, shipping_price_includes_vat=True)],
            offers=[
                offer("Q1", "A", "V1", 2, price_includes_vat=True),
                offer("Q2", "B", "V1", 2, price_includes_vat=True),
            ],
        )
    )
    # Each 2 is supply1/tax1; pooling 4 would incorrectly give supply3/tax1.
    assert (answer["supply_total"], answer["vat_total"], answer["grand_total"]) == (12, 3, 15)
    facts = source(
        vendors=[vendor("V1")],
        offers=[offer("Q1", "A", "V1", 6), offer("Q2", "B", "V1", 6)],
    )
    answer, _ = calculate(facts)
    # Separate excluded-VAT 6+6 rows each truncate tax0; pooling would incorrectly tax1.
    assert (answer["supply_total"], answer["vat_total"], answer["grand_total"]) == (12, 0, 12)


def test_mixed_merchandise_vat_flags_with_independent_shipping_split():
    answer, _ = calculate(
        source(
            vendors=[vendor("V1", shipping_price=101)],
            offers=[
                offer("Q1", "A", "V1", 1101, price_includes_vat=True),
                offer("Q2", "B", "V1", 1009),
            ],
        )
    )
    # Included1101 gives 1000+101, excluded1009 gives 1009+100,
    # excluded101 shipping adds 101+10 once.
    assert (answer["supply_total"], answer["vat_total"], answer["grand_total"]) == (2110, 211, 2321)


def test_distinct_vendor_ids_do_not_merge_normalized_names_or_thresholds():
    answer, _ = calculate(
        source(
            vendors=[
                vendor("V1", name="주식회사 Alpha", shipping_price=100, free_shipping_at=1000),
                vendor("V2", name="㈜ A l p h a", shipping_price=100, free_shipping_at=1000),
            ],
            offers=[offer("Q1", "A", "V1", 500), offer("Q2", "B", "V2", 500)],
        )
    )
    assert answer["grand_total"] == 1320
    assert len(answer["vendor_cart_totals"]) == 2
    assert [row["vendor"] for row in answer["vendor_cart_totals"]] == ["alpha", "alpha"]
    assert all(not row["shipping_free"] for row in answer["vendor_cart_totals"])


def test_unused_alternatives_and_duplicate_rows_do_not_reach_free_threshold():
    facts = source(
        vendors=[vendor("V1", shipping_price=100, free_shipping_at=1100)],
        offers=[
            offer("Q1", "A", "V1", 100),
            offer("Q2", "B", "V1", 100),
            offer("Q3", "A", "V1", 2000, stock_packs=0),
        ],
    )
    facts["offers"].append(deepcopy(facts["offers"][0]))
    answer, trace = calculate(facts)
    assert answer["grand_total"] == 330
    assert answer["vendor_cart_totals"][0]["merchandise_total"] == 220
    assert answer["vendor_cart_totals"][0]["shipping_free"] is False
    assert answer["feasible_cart_count"] == 1
    assert trace[0]["output"]["deduplicated_quote_ids"] == ["Q1"]


def test_item_ids_preserve_independent_identical_name_unit_requirements():
    answer, _ = calculate(
        source(
            items=[item("A", name="볼펜"), item("B", name="볼펜")],
            vendors=[vendor("V1")],
            offers=[offer("Q1", "A", "V1", 100), offer("Q2", "B", "V1", 100)],
        )
    )
    assert answer["grand_total"] == 220
    assert [row["item_id"] for row in answer["chosen_offers"]] == ["A", "B"]


def test_equal_total_uses_vendor_name_then_id_then_quote_per_item_not_leftover():
    answer, trace = calculate(
        source(
            vendors=[
                vendor("Z", name="Alpha"),
                vendor("A", name="Alpha"),
                vendor("B", name="Zebra"),
            ],
            offers=[
                offer("Q0", "A", "Z", 100),
                offer("Q2", "A", "A", 100),
                offer("Q1", "A", "A", 100, pack_units=4),
                offer("Q3", "A", "B", 100),
                offer("Q4", "B", "A", 100),
            ],
        )
    )
    assert [row["quote_id"] for row in answer["chosen_offers"]] == ["Q1", "Q4"]
    assert answer["chosen_offers"][0]["leftover_units"] == 3
    assert trace[0]["output"]["selection"]["chosen_tie_tuple"] == [
        ["alpha", "A", "Q1"],
        ["alpha", "A", "Q4"],
    ]


def test_no_feasible_cart_keeps_ineligible_comparisons():
    facts = source()
    for row in facts["offers"]:
        if row["item_id"] == "B":
            row["stock_packs"] = 0
    answer, trace = calculate(facts)
    assert answer["chosen_offers"] == [] and answer["vendor_cart_totals"] == []
    assert answer["supply_total"] is answer["vat_total"] is answer["grand_total"] is None
    assert answer["feasible_cart_count"] == 0 and len(answer["offer_comparisons"]) == 4
    assert trace[0]["output"]["selection"]["evaluated_carts"] == []
    assert trace[0]["output"]["selection"]["reason"] == "no_feasible_complete_cart"


def test_order_and_exact_duplicate_invariance_without_mutation_or_shared_containers():
    facts = source()
    for field in ("items", "vendors", "offers"):
        facts[field].append(deepcopy(facts[field][0]))
    before = deepcopy(facts)
    answer, trace = calculate(facts)
    reverse = deepcopy(facts)
    for field in ("items", "vendors", "offers"):
        reverse[field].reverse()
    assert calculate(reverse) == (answer, trace)
    assert facts == before
    assert trace[0]["output"]["deduplicated_item_ids"] == ["A"]
    assert trace[0]["output"]["deduplicated_vendor_ids"] == ["V1"]
    assert trace[0]["output"]["deduplicated_quote_ids"] == ["Q1"]
    clean_answer, _ = calculate(source())
    assert clean_answer == answer
    answer["offer_comparisons"][0]["packs"] = -1
    assert answer["chosen_offers"][0]["packs"] == 1
    answer["vendor_cart_totals"][0]["total"] = -1
    trace[0]["inputs"]["offers"][0]["pack_price"] = -1
    assert facts == before
    assert trace[0]["output"]["comparison"] == clean_answer
    assert calculate(facts)[0] == clean_answer


@pytest.mark.parametrize(
    "field,change",
    [
        ("items", {"name": "other"}),
        ("vendors", {"shipping_price": 1}),
        ("offers", {"pack_price": 1}),
    ],
)
def test_conflicting_duplicate_ids_rejected(field, change):
    facts = source()
    facts[field].append({**facts[field][0], **change})
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        calculate(facts)


@pytest.mark.parametrize("field,ref", [("item_id", "missing"), ("vendor_id", "missing")])
def test_dangling_offer_reference_rejected_even_if_ineligible(field, ref):
    facts = source()
    facts["offers"][0].update({field: ref, "stock_packs": 0})
    with pytest.raises(ValueError, match="dangling"):
        calculate(facts)


@pytest.mark.parametrize("field", ["source", "items", "vendors", "offers"])
@pytest.mark.parametrize("action", ["missing", "extra"])
def test_all_object_shapes_exact(field, action):
    facts = source()
    row = facts if field == "source" else facts[field][0]
    if action == "missing":
        row.pop(
            "processing_policy"
            if field == "source"
            else "name"
            if field != "offers"
            else "lead_days"
        )
    else:
        row["extra"] = 1
    with pytest.raises(ValueError, match="fields"):
        calculate(facts)


@pytest.mark.parametrize("field", ["items", "vendors", "offers"])
@pytest.mark.parametrize("bad", [None, {}, [], "rows", [1]])
def test_array_types_and_nonempty_structural_requirements(field, bad):
    with pytest.raises(ValueError):
        calculate(source(**{field: bad}))


@pytest.mark.parametrize(
    "field,key",
    [
        ("items", "required_units"),
        ("vendors", "shipping_price"),
        ("vendors", "free_shipping_at"),
        ("offers", "pack_units"),
        ("offers", "pack_price"),
        ("offers", "minimum_packs"),
        ("offers", "stock_packs"),
        ("offers", "lead_days"),
    ],
)
@pytest.mark.parametrize("bad", [True, False, 1.0, "1", -1])
def test_integer_quantities_money_and_bounds_are_strict(field, key, bad):
    facts = source()
    facts[field][0][key] = bad
    with pytest.raises(ValueError, match="integer"):
        calculate(facts)


@pytest.mark.parametrize(
    "field,key",
    [("items", "required_units"), ("offers", "pack_units"), ("offers", "minimum_packs")],
)
def test_positive_integer_fields_reject_zero(field, key):
    facts = source()
    facts[field][0][key] = 0
    with pytest.raises(ValueError, match="integer"):
        calculate(facts)


@pytest.mark.parametrize(
    "field,key", [("vendors", "shipping_price_includes_vat"), ("offers", "price_includes_vat")]
)
@pytest.mark.parametrize("bad", [0, 1, "true", None])
def test_vat_flags_are_booleans(field, key, bad):
    facts = source()
    facts[field][0][key] = bad
    with pytest.raises(ValueError, match="boolean"):
        calculate(facts)


@pytest.mark.parametrize(
    "field,key",
    [
        ("source", "processing_policy"),
        ("items", "item_id"),
        ("items", "name"),
        ("items", "base_unit"),
        ("vendors", "vendor_id"),
        ("vendors", "name"),
        ("offers", "quote_id"),
        ("offers", "item_id"),
        ("offers", "vendor_id"),
    ],
)
@pytest.mark.parametrize("bad", ["", "  ", None, 1])
def test_text_fields_are_nonempty_strings(field, key, bad):
    facts = source()
    (facts if field == "source" else facts[field][0])[key] = bad
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize(
    "field,key",
    [
        ("source", "order_date"),
        ("source", "latest_delivery_date"),
        ("offers", "valid_from"),
        ("offers", "valid_until"),
    ],
)
@pytest.mark.parametrize("bad", ["20261009", "2026-10-9", "2026-02-30", None])
def test_strict_iso_calendar_dates(field, key, bad):
    facts = source()
    (facts if field == "source" else facts[field][0])[key] = bad
    with pytest.raises(ValueError):
        calculate(facts)


def test_reversed_calendar_period_and_overflow_are_rejected():
    with pytest.raises(ValueError, match="predates"):
        calculate(source(latest_delivery_date="2026-10-08"))
    facts = source()
    facts["offers"][0]["valid_from"] = "2026-11-01"
    with pytest.raises(ValueError, match="validity"):
        calculate(facts)
    facts["offers"][0]["valid_from"] = "2026-10-01"
    facts["offers"][0]["lead_days"] = 10**30
    with pytest.raises(ValueError, match="calendar range"):
        calculate(facts)


@pytest.mark.parametrize(
    "change,flag,expected",
    [
        ({"valid_from": "2026-10-09"}, "valid_on_order", True),
        ({"valid_until": "2026-10-09"}, "valid_on_order", True),
        ({"valid_from": "2026-10-10"}, "valid_on_order", False),
        ({"valid_until": "2026-10-08"}, "valid_on_order", False),
        ({"lead_days": 2}, "delivered_in_time", True),
        ({"lead_days": 3}, "delivered_in_time", False),
        ({"stock_packs": 1}, "stock_sufficient", True),
        ({"stock_packs": 0}, "stock_sufficient", False),
    ],
)
def test_offer_eligibility_boundaries(change, flag, expected):
    facts = source()
    facts["offers"][0].update(change)
    answer, _ = calculate(facts)
    assert answer["offer_comparisons"][0][flag] is expected
    assert answer["offer_comparisons"][0]["eligible"] is expected
    assert answer["feasible_cart_count"] == (4 if expected else 2)


def test_pack_ceiling_minimum_and_exact_integer_precision():
    required = 2**60 + 1
    answer, _ = calculate(
        source(
            items=[item("A", required_units=required), item("B", required_units=2)],
            vendors=[vendor("V1")],
            offers=[
                offer("Q1", "A", "V1", 1, pack_units=2, stock_packs=required),
                offer("Q2", "B", "V1", 0, pack_units=3, minimum_packs=4),
            ],
        )
    )
    a, b = answer["chosen_offers"]
    assert (a["packs"], a["obtained_units"], a["leftover_units"]) == (2**59 + 1, 2**60 + 2, 1)
    assert (b["packs"], b["obtained_units"], b["leftover_units"]) == (4, 12, 10)


def test_zero_free_threshold_is_distinct_from_null_for_zero_goods():
    facts = source(
        vendors=[vendor("V1", shipping_price=100, free_shipping_at=0)],
        offers=[offer("Q1", "A", "V1", 0), offer("Q2", "B", "V1", 0)],
    )
    answer, _ = calculate(facts)
    assert answer["grand_total"] == 0 and answer["vendor_cart_totals"][0]["shipping_free"]
    facts["vendors"][0]["free_shipping_at"] = None
    answer, _ = calculate(facts)
    assert answer["grand_total"] == 110 and not answer["vendor_cart_totals"][0]["shipping_free"]


def test_cart_enumeration_maximum_1296_and_structural_bounds():
    facts = source(
        items=[item(key) for key in "ABCD"],
        vendors=[vendor("V1")],
        offers=[offer(f"{key}{i}", key, "V1", 0) for key in "ABCD" for i in range(6)],
    )
    answer, trace = calculate(facts)
    assert answer["feasible_cart_count"] == 1296
    assert len(trace[0]["output"]["selection"]["evaluated_carts"]) == 1296
    assert [row["quote_id"] for row in answer["chosen_offers"]] == ["A0", "B0", "C0", "D0"]
    facts["offers"].append(offer("A6", "A", "V1", 0))
    with pytest.raises(ValueError, match="1..6"):
        calculate(facts)
    facts["offers"].pop()
    facts["items"].append(item("E"))
    with pytest.raises(ValueError, match="2..4"):
        calculate(facts)
    facts = source(items=[item("A")])
    with pytest.raises(ValueError, match="2..4"):
        calculate(facts)
    facts = source(vendors=[vendor(f"V{i}") for i in range(9)])
    with pytest.raises(ValueError, match="1..8"):
        calculate(facts)
    facts = source(offers=[offer("Q1", "A", "V1", 0)])
    with pytest.raises(ValueError, match="1..6"):
        calculate(facts)


def test_delivery_leap_day_and_empty_normalized_vendor_identity():
    facts = source(order_date="2028-02-28", latest_delivery_date="2028-03-01")
    for row in facts["offers"]:
        row.update(valid_from="2028-02-01", valid_until="2028-03-31")
    answer, _ = calculate(facts)
    assert all(row["delivery_date"] == "2028-03-01" for row in answer["offer_comparisons"])
    facts["vendors"][0]["name"] = "주식회사"
    with pytest.raises(ValueError, match="normalizes"):
        calculate(facts)


@pytest.mark.parametrize("bad", [None, [], {}, {"source_contract": "wrong"}])
def test_unknown_source_contract(bad):
    with pytest.raises(ValueError, match="source contract"):
        calculate(bad)


def test_no_quantity_growth_to_chase_free_shipping():
    answer, _ = calculate(
        source(
            vendors=[vendor("V1", shipping_price=1000, free_shipping_at=1100)],
            offers=[offer("Q1", "A", "V1", 100), offer("Q2", "B", "V1", 100)],
        )
    )
    assert [row["packs"] for row in answer["chosen_offers"]] == [1, 1]
    assert answer["vendor_cart_totals"][0]["merchandise_total"] == 220
    assert answer["grand_total"] == 1320
    # Buying extra merchandise for 1100 to avoid shipping is outside the stated contract.


def test_public_cart_route_reads_actual_three_format_sources_and_changed_freight(tmp_path):
    import json
    from openpyxl import load_workbook
    from KrRubberStamp.registry import calculate as registered_calculate
    from render.authored import render_authored
    from render.documents import restore_scenario, _label

    facts = source()
    documents = [
        {
            "filename": "구매요청.pdf",
            "format": "pdf",
            "title": "서로 다른 두 품목의 구매 요청",
            "note": "품목별 수량을 확보한 전체 구매 조합의 실제 총액을 비교합니다.",
            "fields": [
                "source_contract",
                "processing_policy",
                "order_date",
                "latest_delivery_date",
                "items",
            ],
        },
        {
            "filename": "공급사배송.xlsx",
            "format": "xlsx",
            "title": "공급사 식별번호별 배송 조건",
            "note": "선택된 동일 공급사의 상품 합계에 배송비를 한 번 적용합니다.",
            "fields": ["vendors"],
        },
        {
            "filename": "품목견적.hwpx",
            "format": "hwpx",
            "title": "각 품목의 독립 포장 견적",
            "note": "각 견적을 품목과 공급사 식별번호에 연결합니다.",
            "fields": ["offers"],
        },
    ]
    render_authored(facts, tmp_path, "D_extract", documents)
    restored = restore_scenario(tmp_path)
    assert restored == facts
    answer, trace = registered_calculate("D_extract", restored)
    assert answer["grand_total"] == 2090
    assert [row["quote_id"] for row in answer["chosen_offers"]] == ["Q1", "Q2"]
    assert trace[0]["rule_id"] == RULE_ID
    assert _label(["vendors", 0, "name"], "D_extract").endswith("업체명")
    mapping = json.loads((tmp_path / "extraction_map.json").read_text())
    record = next(
        row for row in mapping["records"] if row["path"] == ["vendors", 0, "shipping_price"]
    )
    workbook = load_workbook(tmp_path / record["file"])
    selector = record["selector"]
    workbook[selector["sheet"]][selector["cell"]] = 1000
    workbook.save(tmp_path / record["file"])
    workbook.close()
    after, _ = registered_calculate("D_extract", restore_scenario(tmp_path))
    assert after["grand_total"] == 2530
    assert [row["quote_id"] for row in after["chosen_offers"]] == ["Q3", "Q4"]
