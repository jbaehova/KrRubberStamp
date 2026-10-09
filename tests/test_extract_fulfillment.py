from copy import deepcopy

import pytest

from rules.d_extract.fulfillment import CONTRACT, RULE_ID, calculate


@pytest.fixture
def source():
    return {
        "source_contract": CONTRACT,
        "processing_policy": (
            "합성 거래 정산 약정이다. 마감일까지 실제 인수에서 반품을 빼고 포장 단가에 "
            "순인수 기초 단위 수량을 곱한 뒤 포장당 수량으로 나눠 원 미만을 버린다. "
            "포함가는 공급가액을 10/11로 버림 분리하고 별도가는 10%를 버림 가산한다. "
            "실행 선지급을 빼며 예정 이체와 견적은 제외한다. VAT 신고 판정은 아니다."
        ),
        "cutoff_date": "2026-05-10",
        "orders": [
            {
                "order_id": "O1",
                "vendor": "주식회사 솔빛",
                "date": "2026-05-01",
                "kind": "order",
                "lines": [
                    {
                        "line_id": "A",
                        "item": "A ４",
                        "base_unit": "개",
                        "ordered_packages": 3,
                        "units_per_package": 4,
                        "package_price": 11001,
                        "price_includes_vat": True,
                    },
                    {
                        "line_id": "B",
                        "item": "볼트",
                        "base_unit": "개",
                        "ordered_packages": 2,
                        "units_per_package": 5,
                        "package_price": 1003,
                        "price_includes_vat": False,
                    },
                ],
            },
            {
                "order_id": "O2",
                "vendor": "(주) 솔 빛",
                "date": "2026-05-02",
                "kind": "order",
                "lines": [
                    {
                        "line_id": "A",
                        "item": "a4",
                        "base_unit": "개",
                        "ordered_packages": 1,
                        "units_per_package": 3,
                        "package_price": 1000,
                        "price_includes_vat": True,
                    }
                ],
            },
            {
                "order_id": "Q1",
                "vendor": "견적업체",
                "date": "2026-05-01",
                "kind": "quote",
                "lines": [
                    {
                        "line_id": "Q",
                        "item": "견적 부품",
                        "base_unit": "개",
                        "ordered_packages": 1,
                        "units_per_package": 2,
                        "package_price": 1,
                        "price_includes_vat": False,
                    }
                ],
            },
        ],
        "events": [
            {
                "event_id": "R1",
                "order_id": "O1",
                "line_id": "A",
                "kind": "received",
                "date": "2026-05-04",
                "units": 7,
            },
            {
                "event_id": "A-return",
                "order_id": "O1",
                "line_id": "A",
                "kind": "returned",
                "date": "2026-05-04",
                "units": 1,
            },
            {
                "event_id": "R2",
                "order_id": "O1",
                "line_id": "B",
                "kind": "received",
                "date": "2026-05-05",
                "units": 8,
            },
            {
                "event_id": "T2",
                "order_id": "O1",
                "line_id": "B",
                "kind": "returned",
                "date": "2026-05-06",
                "units": 3,
            },
            {
                "event_id": "R3",
                "order_id": "O2",
                "line_id": "A",
                "kind": "received",
                "date": "2026-05-10",
                "units": 1,
            },
            {
                "event_id": "future",
                "order_id": "O1",
                "line_id": "A",
                "kind": "received",
                "date": "2026-05-11",
                "units": 100,
            },
        ],
        "payments": [
            {
                "payment_id": "P1",
                "order_id": "O1",
                "date": "2026-05-02",
                "status": "executed",
                "amount": 18000,
            },
            {
                "payment_id": "P2",
                "order_id": "O2",
                "date": "2026-05-10",
                "status": "executed",
                "amount": 1000,
            },
            {
                "payment_id": "future",
                "order_id": "O1",
                "date": "2026-05-11",
                "status": "executed",
                "amount": 44444,
            },
            {
                "payment_id": "planned",
                "order_id": "Q1",
                "date": "2026-04-30",
                "status": "planned",
                "amount": 99999,
            },
        ],
    }


def test_hand_calculated_partial_delivery_return_and_advance(source):
    answer, trace = calculate(source)
    # Independently worked: floor(11001*6/4)=16501 -> 15000+1501;
    # floor(1003*5/5)=1003 -> 1003+100; floor(1000/3)=333 -> 302+31.
    assert answer == {
        "line_settlements": [
            {
                "order_id": "O1",
                "line_id": "A",
                "item": "a4",
                "base_unit": "개",
                "ordered_units": 12,
                "received_units": 7,
                "returned_units": 1,
                "net_units": 6,
                "outstanding_units": 6,
                "supply": 15000,
                "vat": 1501,
                "total": 16501,
            },
            {
                "order_id": "O1",
                "line_id": "B",
                "item": "볼트",
                "base_unit": "개",
                "ordered_units": 10,
                "received_units": 8,
                "returned_units": 3,
                "net_units": 5,
                "outstanding_units": 5,
                "supply": 1003,
                "vat": 100,
                "total": 1103,
            },
            {
                "order_id": "O2",
                "line_id": "A",
                "item": "a4",
                "base_unit": "개",
                "ordered_units": 3,
                "received_units": 1,
                "returned_units": 0,
                "net_units": 1,
                "outstanding_units": 2,
                "supply": 302,
                "vat": 31,
                "total": 333,
            },
        ],
        "item_quantities": [
            {"item": "a4", "base_unit": "개", "net_units": 7},
            {"item": "볼트", "base_unit": "개", "net_units": 5},
        ],
        "vendor_balances": [
            {
                "vendor": "솔빛",
                "supply": 16305,
                "vat": 1632,
                "total": 17937,
                "paid": 19000,
                "balance": -1063,
            }
        ],
        "grand_total": 17937,
        "payment_total": 19000,
        "balance_total": -1063,
    }
    assert trace[0]["rule_id"] == RULE_ID
    assert trace[0]["output"]["excluded_after_cutoff_event_ids"] == ["future"]
    assert trace[0]["output"]["excluded_payment_ids"] == ["future", "planned"]
    assert trace[0]["output"]["settlement"] == answer


def test_source_and_trace_are_not_mutated_or_aliased(source):
    original = deepcopy(source)
    answer, trace = calculate(source)
    assert source == original
    source["orders"][0]["lines"][0]["item"] = "changed"
    answer["line_settlements"][0]["item"] = "changed"
    assert trace[0]["inputs"]["orders"][0]["lines"][0]["item"] == "A ４"
    assert trace[0]["output"]["settlement"]["line_settlements"][0]["item"] == "a4"


def test_document_and_line_order_invariance(source):
    original = calculate(source)
    source["orders"].reverse()
    source["events"].reverse()
    source["payments"].reverse()
    for order in source["orders"]:
        order["lines"].reverse()
    assert calculate(source) == original


def test_identical_event_and_payment_ids_are_counted_once(source):
    original, _ = calculate(source)
    source["events"].append(deepcopy(source["events"][0]))
    source["payments"].append(deepcopy(source["payments"][0]))
    answer, trace = calculate(source)
    assert answer == original
    assert trace[0]["output"]["deduplicated_event_ids"] == ["R1"]
    assert trace[0]["output"]["deduplicated_payment_ids"] == ["P1"]


@pytest.mark.parametrize("record_type,field", [("events", "units"), ("payments", "amount")])
def test_conflicting_duplicate_rejected_even_after_cutoff(source, record_type, field):
    changed = deepcopy(source[record_type][-2 if record_type == "payments" else -1])
    changed[field] += 1
    source[record_type].append(changed)
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        calculate(source)


@pytest.mark.parametrize("record_type", ["events", "payments"])
def test_quote_cannot_gain_actual_event_or_payment(source, record_type):
    row = source[record_type][0]
    row["order_id"] = "Q1"
    if record_type == "events":
        row["line_id"] = "Q"
    with pytest.raises(ValueError, match="Quote cannot"):
        calculate(source)


@pytest.mark.parametrize("record_type", ["events", "payments"])
def test_unknown_order_reference_rejected(source, record_type):
    source[record_type][0]["order_id"] = "missing"
    with pytest.raises(ValueError, match="Unknown fulfillment"):
        calculate(source)


def test_line_reference_is_scoped_to_order_not_global_line_id(source):
    source["events"][2]["order_id"] = "O2"
    with pytest.raises(ValueError, match="Unknown fulfillment event order line"):
        calculate(source)


@pytest.mark.parametrize("record_type", ["events", "payments"])
def test_actual_record_cannot_predate_order(source, record_type):
    source[record_type][0]["date"] = "2026-04-30"
    with pytest.raises(ValueError, match="predates"):
        calculate(source)


def test_return_cannot_be_financed_by_later_receipt(source):
    source["events"][1]["date"] = "2026-05-03"
    with pytest.raises(ValueError, match="Return exceeds"):
        calculate(source)


def test_same_day_receipt_precedes_return_regardless_of_id(source):
    answer, trace = calculate(source)
    assert answer["line_settlements"][0]["net_units"] == 6
    timeline = trace[0]["output"]["event_timeline"]
    assert timeline[:2] == [
        {"event_id": "R1", "net_units_after_event": 7},
        {"event_id": "A-return", "net_units_after_event": 6},
    ]


def test_cutoff_change_admits_later_receipt_and_payment(source):
    source["cutoff_date"] = "2026-05-11"
    answer, _ = calculate(source)
    assert answer["line_settlements"][0]["net_units"] == 106
    assert answer["line_settlements"][0]["outstanding_units"] == -94
    assert answer["line_settlements"][0]["total"] == 291526
    assert answer["payment_total"] == 63444
    assert answer["balance_total"] == 229518


def test_same_item_different_base_units_not_combined(source):
    source["orders"][1]["lines"][0]["base_unit"] = "장"
    answer, _ = calculate(source)
    assert answer["item_quantities"][:2] == [
        {"item": "a4", "base_unit": "개", "net_units": 6},
        {"item": "a4", "base_unit": "장", "net_units": 1},
    ]


def test_subwon_floor_and_no_receipt_still_keep_order_line(source):
    source["orders"][1]["lines"][0]["package_price"] = 1
    answer, trace = calculate(source)
    assert answer["line_settlements"][2]["total"] == 0
    assert trace[0]["output"]["line_arithmetic"][2]["amount_after_floor"] == 0
    source["events"] = []
    answer, _ = calculate(source)
    assert len(answer["line_settlements"]) == 3
    assert answer["grand_total"] == 0
    assert answer["balance_total"] == -19000


def test_future_order_zero_line_visible_but_future_actual_receipt_excluded(source):
    source["orders"][1]["date"] = "2026-05-11"
    source["events"][4]["date"] = "2026-05-11"
    source["payments"][1]["date"] = "2026-05-11"
    answer, _ = calculate(source)
    assert answer["line_settlements"][2]["net_units"] == 0
    assert answer["payment_total"] == 18000


@pytest.mark.parametrize("date_value", ["20260510", "2026-W19-7", "2026-5-10", "2026-02-30"])
def test_strict_calendar_iso_date(source, date_value):
    source["cutoff_date"] = date_value
    with pytest.raises(ValueError):
        calculate(source)


@pytest.mark.parametrize("field,value", [("units_per_package", True), ("package_price", -1)])
def test_integer_facts_reject_booleans_and_negatives(source, field, value):
    source["orders"][0]["lines"][0][field] = value
    with pytest.raises(ValueError, match="must be an integer"):
        calculate(source)


def test_order_and_scoped_line_identity_must_be_unique(source):
    source["orders"].append(deepcopy(source["orders"][0]))
    with pytest.raises(ValueError, match="Duplicate fulfillment order_id"):
        calculate(source)
    source["orders"].pop()
    source["orders"][0]["lines"].append(deepcopy(source["orders"][0]["lines"][0]))
    with pytest.raises(ValueError, match="Duplicate fulfillment order line"):
        calculate(source)


@pytest.mark.parametrize("policy", ["", "   ", None])
def test_visible_policy_required(source, policy):
    source["processing_policy"] = policy
    with pytest.raises(ValueError, match="policy"):
        calculate(source)


def test_policy_semantics_are_authored_not_language_detected(source):
    source["processing_policy"] = "Synthetic settlement agreement with explicit line rounding."
    answer, _ = calculate(source)
    assert answer["grand_total"] == 17937


@pytest.mark.parametrize("value", [True, 1.0])
def test_duplicate_identity_requires_exact_content_types(source, value):
    changed = deepcopy(source["events"][4])
    changed["units"] = value
    source["events"].insert(0, changed)
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        calculate(source)


def test_registry_reconciles_facts_restored_from_all_primary_formats(source, tmp_path):
    import pymupdf

    from KrRubberStamp.registry import calculate as registered_calculate
    from render.authored import render_authored
    from render.documents import restore_scenario

    documents = [
        {
            "filename": "발주.pdf",
            "format": "pdf",
            "title": "분할 입고 포장 단가와 정산 약정",
            "note": "발주 수량 전체가 아닌 실제 순입고 수량으로 정산합니다.",
            "fields": ["source_contract", "processing_policy", "cutoff_date", "orders"],
        },
        {
            "filename": "입고반품.xlsx",
            "format": "xlsx",
            "title": "품목 행별 실제 입고와 반품 대장",
            "note": "발주 번호와 품목 행 번호를 함께 대조합니다.",
            "fields": ["events"],
        },
        {
            "filename": "지급.hwpx",
            "format": "hwpx",
            "title": "예정 이체와 실행 선지급 기록",
            "note": "정산 기준일까지 실행된 지급만 잔액에서 차감합니다.",
            "fields": ["payments"],
        },
    ]
    render_authored(source, tmp_path, "D_extract", documents)
    restored = restore_scenario(tmp_path)
    assert restored == source
    answer, trace = registered_calculate("D_extract", restored)
    assert answer == calculate(source)[0]
    assert (answer["grand_total"], answer["payment_total"], answer["balance_total"]) == (
        17937,
        19000,
        -1063,
    )
    assert trace[0]["rule_id"] == RULE_ID
    with pymupdf.open(tmp_path / "inputs/발주.pdf") as pdf:
        text = "".join(page.get_text() for page in pdf)
    assert "포장당 낱개 수" in text and "발주 또는 견적 번호" in text
