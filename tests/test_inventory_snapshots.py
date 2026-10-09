from copy import deepcopy
from itertools import permutations

import pytest

from rules.d_extract.inventory_snapshots import CONTRACT, RULE_ID, calculate

POLICY = "가상 조직의 확정 주문은 지정 창고에만 예약한다. 취소일 말에 잔여 예약을 해제하고 반품은 주문을 다시 열지 않는다."


def order(identity="O1", quantity=8, warehouse="W1", placed="2026-10-01", cancelled=None):
    return {
        "order_id": identity,
        "item_id": "A",
        "warehouse_id": warehouse,
        "quantity": quantity,
        "placed_on": placed,
        "cancelled_on": cancelled,
    }


def movement(
    identity,
    kind,
    quantity,
    day,
    outgoing=None,
    incoming=None,
    order_id=None,
    related=None,
    status="posted",
):
    return {
        "movement_id": identity,
        "item_id": "A",
        "date": day,
        "kind": kind,
        "quantity": quantity,
        "from_warehouse_id": outgoing,
        "to_warehouse_id": incoming,
        "order_id": order_id,
        "related_movement_id": related,
        "status": status,
    }


def source():
    return {
        "source_contract": CONTRACT,
        "processing_policy": POLICY,
        "opening_date": "2026-10-01",
        "snapshot_dates": ["2026-10-03", "2026-10-05", "2026-10-08"],
        "items": [{"item_id": "A", "name": "가상 실험 키트", "base_unit": "개"}],
        "warehouses": [
            {"warehouse_id": "W1", "name": "가상 서쪽 창고"},
            {"warehouse_id": "W2", "name": "가상 동쪽 창고"},
        ],
        "opening_balances": [
            {"item_id": "A", "warehouse_id": "W1", "quantity": 10},
            {"item_id": "A", "warehouse_id": "W2", "quantity": 2},
        ],
        "orders": [
            order(),
            order("O2", 7, "W2", "2026-10-02", "2026-10-05"),
            order("O3", 2, "W2", "2026-10-08"),
        ],
        "movements": [
            movement("R1", "receipt", 6, "2026-10-02", incoming="W1"),
            movement("T1", "transfer", 9, "2026-10-03", "W1", "W2"),
            movement("I1", "issue", 5, "2026-10-04", "W1", order_id="O1"),
            movement("C1", "customer_return", 2, "2026-10-05", incoming="W2", related="I1"),
            movement("S1", "supplier_return", 3, "2026-10-05", "W2", related="R1"),
            movement("R2", "receipt", 1, "2026-10-06", incoming="W1"),
            movement("I2", "issue", 3, "2026-10-06", "W1", order_id="O1"),
            movement("D1", "issue", 10, "2026-10-07", "W1", status="draft"),
            movement("F1", "receipt", 10, "2026-10-09", incoming="W1"),
        ],
    }


def stock(
    warehouse,
    opening,
    receipt,
    issued,
    transfer_in,
    transfer_out,
    customer_return,
    supplier_return,
    on_hand,
    reserved,
    available,
    shortfall,
):
    return {
        "item_id": "A",
        "warehouse_id": warehouse,
        "opening_quantity": opening,
        "receipt_quantity": receipt,
        "issued_quantity": issued,
        "transfer_in_quantity": transfer_in,
        "transfer_out_quantity": transfer_out,
        "customer_return_quantity": customer_return,
        "supplier_return_quantity": supplier_return,
        "on_hand": on_hand,
        "reserved_quantity": reserved,
        "available_quantity": available,
        "reservation_shortfall": shortfall,
    }


def order_result(identity, warehouse, quantity, issued, reserved, status):
    return {
        "order_id": identity,
        "item_id": "A",
        "warehouse_id": warehouse,
        "quantity": quantity,
        "issued_quantity": issued,
        "reserved_quantity": reserved,
        "status": status,
    }


def test_manual_complete_three_snapshot_answer_and_private_derivations():
    answer, trace = calculate(source())
    assert answer == {
        "stock_snapshots": [
            {
                "date": "2026-10-03",
                "stocks": [
                    stock("W1", 10, 6, 0, 0, 9, 0, 0, 7, 8, 0, 1),
                    stock("W2", 2, 0, 0, 9, 0, 0, 0, 11, 7, 4, 0),
                ],
            },
            {
                "date": "2026-10-05",
                "stocks": [
                    stock("W1", 10, 6, 5, 0, 9, 0, 0, 2, 3, 0, 1),
                    stock("W2", 2, 0, 0, 9, 0, 2, 3, 10, 0, 10, 0),
                ],
            },
            {
                "date": "2026-10-08",
                "stocks": [
                    stock("W1", 10, 7, 8, 0, 9, 0, 0, 0, 0, 0, 0),
                    stock("W2", 2, 0, 0, 9, 0, 2, 3, 10, 2, 8, 0),
                ],
            },
        ],
        "order_snapshots": [
            {
                "date": "2026-10-03",
                "orders": [
                    order_result("O1", "W1", 8, 0, 8, "active"),
                    order_result("O2", "W2", 7, 0, 7, "active"),
                    order_result("O3", "W2", 2, 0, 0, "not_yet"),
                ],
            },
            {
                "date": "2026-10-05",
                "orders": [
                    order_result("O1", "W1", 8, 5, 3, "active"),
                    order_result("O2", "W2", 7, 0, 0, "cancelled"),
                    order_result("O3", "W2", 2, 0, 0, "not_yet"),
                ],
            },
            {
                "date": "2026-10-08",
                "orders": [
                    order_result("O1", "W1", 8, 8, 0, "fulfilled"),
                    order_result("O2", "W2", 7, 0, 0, "cancelled"),
                    order_result("O3", "W2", 2, 0, 2, "active"),
                ],
            },
        ],
        "organization_item_snapshots": [
            {
                "date": "2026-10-03",
                "items": [
                    {
                        "item_id": "A",
                        "on_hand": 18,
                        "reserved_quantity": 15,
                        "available_quantity": 4,
                        "reservation_shortfall": 1,
                    }
                ],
            },
            {
                "date": "2026-10-05",
                "items": [
                    {
                        "item_id": "A",
                        "on_hand": 12,
                        "reserved_quantity": 3,
                        "available_quantity": 10,
                        "reservation_shortfall": 1,
                    }
                ],
            },
            {
                "date": "2026-10-08",
                "items": [
                    {
                        "item_id": "A",
                        "on_hand": 10,
                        "reserved_quantity": 2,
                        "available_quantity": 8,
                        "reservation_shortfall": 0,
                    }
                ],
            },
        ],
    }
    assert len(trace) == 1 and trace[0]["rule_id"] == RULE_ID
    assert trace[0]["output"]["comparison"] == answer
    assert trace[0]["output"]["snapshots"][2]["excluded_movement_ids"] == ["D1", "F1"]
    assert trace[0]["output"]["snapshots"][2]["pending_order_ids"] == ["O3"]


def simple():
    facts = source()
    facts["orders"] = []
    facts["movements"] = []
    facts["snapshot_dates"] = ["2026-10-03"]
    return facts


def test_transfer_conserves_organization_physical_stock_but_changes_local_availability():
    facts = simple()
    facts["orders"] = [order(quantity=8)]
    before, _ = calculate(facts)
    facts["movements"] = [movement("T", "transfer", 4, "2026-10-03", "W1", "W2")]
    after, _ = calculate(facts)
    assert before["organization_item_snapshots"][0]["items"] == [
        {
            "item_id": "A",
            "on_hand": 12,
            "reserved_quantity": 8,
            "available_quantity": 4,
            "reservation_shortfall": 0,
        }
    ]
    assert after["organization_item_snapshots"][0]["items"] == [
        {
            "item_id": "A",
            "on_hand": 12,
            "reserved_quantity": 8,
            "available_quantity": 6,
            "reservation_shortfall": 2,
        }
    ]


def test_completed_order_stays_fulfilled_after_return_to_other_warehouse():
    facts = simple()
    facts["orders"] = [order(quantity=5, cancelled="2026-10-03")]
    facts["movements"] = [
        movement("I", "issue", 5, "2026-10-02", "W1", order_id="O1"),
        movement("C", "customer_return", 5, "2026-10-03", incoming="W2", related="I"),
    ]
    answer, _ = calculate(facts)
    assert answer["order_snapshots"][0]["orders"] == [
        order_result("O1", "W1", 5, 5, 0, "fulfilled")
    ]
    assert [row["on_hand"] for row in answer["stock_snapshots"][0]["stocks"]] == [5, 7]


def test_partial_issue_on_cancellation_day_is_valid_and_only_unfulfilled_reservation_released():
    facts = simple()
    facts["snapshot_dates"] = ["2026-10-02", "2026-10-03"]
    facts["orders"] = [order(quantity=7, cancelled="2026-10-03")]
    facts["movements"] = [
        movement("I1", "issue", 2, "2026-10-02", "W1", order_id="O1"),
        movement("I2", "issue", 3, "2026-10-03", "W1", order_id="O1"),
    ]
    answer, _ = calculate(facts)
    assert answer["order_snapshots"] == [
        {"date": "2026-10-02", "orders": [order_result("O1", "W1", 7, 2, 5, "active")]},
        {"date": "2026-10-03", "orders": [order_result("O1", "W1", 7, 5, 0, "cancelled")]},
    ]
    assert answer["stock_snapshots"][1]["stocks"][0]["on_hand"] == 5


def test_equal_distinct_receipts_count_twice_but_transmitted_copy_counts_once():
    facts = simple()
    first = movement("R1", "receipt", 4, "2026-10-02", incoming="W1")
    facts["movements"] = [first, deepcopy(first), {**first, "movement_id": "R2"}]
    facts["orders"] = [order(quantity=3), order(quantity=3)]
    answer, trace = calculate(facts)
    assert answer["stock_snapshots"][0]["stocks"][0]["receipt_quantity"] == 8
    assert answer["stock_snapshots"][0]["stocks"][0]["reserved_quantity"] == 3
    assert trace[0]["output"]["deduplicated_movement_ids"] == ["R1"]
    assert trace[0]["output"]["deduplicated_order_ids"] == ["O1"]


def test_same_day_aggregate_permutation_is_valid_with_zero_opening_stock():
    facts = simple()
    facts["opening_balances"][0]["quantity"] = 0
    rows = [
        movement("I", "issue", 5, "2026-10-02", "W1"),
        movement("R", "receipt", 5, "2026-10-02", incoming="W1"),
        movement("T", "transfer", 2, "2026-10-02", "W2", "W1"),
    ]
    expected = None
    for variant in permutations(rows):
        facts["movements"] = list(variant)
        result = calculate(facts)
        expected = expected or result
        assert result == expected
    assert expected[0]["stock_snapshots"][0]["stocks"][0]["on_hand"] == 2


def test_canonical_source_permutation_and_no_mutable_aliasing():
    original = source()
    permuted = deepcopy(original)
    for field in (
        "items",
        "warehouses",
        "opening_balances",
        "orders",
        "movements",
        "snapshot_dates",
    ):
        permuted[field].reverse()
    answer, trace = calculate(original)
    assert calculate(permuted) == (answer, trace)
    saved_source, saved_trace = deepcopy(original), deepcopy(trace)
    answer["stock_snapshots"][0]["stocks"][0]["on_hand"] = -999
    assert original == saved_source and trace == saved_trace
    trace[0]["inputs"]["orders"][0]["quantity"] = -999
    assert original == saved_source
    assert trace[0]["output"]["comparison"]["stock_snapshots"][0]["stocks"][0]["on_hand"] == 7
    original["items"][0]["name"] = "changed"
    assert trace[0]["inputs"]["items"][0]["name"] == "가상 실험 키트"


@pytest.mark.parametrize(
    "path,value",
    [
        (("opening_balances", 0, "quantity"), True),
        (("orders", 0, "quantity"), 2.0),
        (("movements", 0, "quantity"), "6"),
        (("movements", 0, "quantity"), 0),
        (("opening_balances", 0, "quantity"), -1),
        (("items", 0, "name"), " "),
        (("items", 0, "base_unit"), None),
        (("orders", 0, "order_id"), 1),
        (("warehouses", 0, "name"), []),
        (("processing_policy",), ""),
        (("opening_date",), "20261001"),
        (("snapshot_dates", 0), "2026-09-30"),
        (("movements", 0, "date"), "2026-10-01"),
        (("movements", 0, "date"), "2026-02-30"),
        (("orders", 0, "placed_on"), "2026-09-30"),
        (("orders", 0, "cancelled_on"), "2026-09-30"),
        (("movements", 0, "status"), "pending"),
        (("movements", 0, "kind"), "allocation"),
        (("orders", 0, "warehouse_id"), "missing"),
        (("orders", 0, "item_id"), "missing"),
        (("movements", 0, "item_id"), "missing"),
        (("movements", 0, "to_warehouse_id"), "missing"),
        (("source_contract",), "other"),
    ],
)
def test_strict_types_identity_dates_and_enums(path, value):
    facts = source()
    target = facts
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize(
    "field", ["items", "warehouses", "opening_balances", "orders", "movements"]
)
def test_unknown_and_missing_source_row_fields_rejected(field):
    facts = source()
    facts[field][0]["derived_on_hand"] = 0
    with pytest.raises(ValueError):
        calculate(facts)
    facts = source()
    del facts[field][0][next(iter(facts[field][0]))]
    with pytest.raises(ValueError):
        calculate(facts)


def test_top_level_unknown_fields_missing_zero_grid_duplicate_id_and_snapshots():
    variants = []
    facts = simple()
    facts["available_quantity"] = 12
    variants.append(facts)
    facts = simple()
    del facts["orders"]
    variants.append(facts)
    facts = simple()
    facts["opening_balances"].pop()
    variants.append(facts)
    facts = simple()
    facts["opening_balances"].append(deepcopy(facts["opening_balances"][0]))
    variants.append(facts)
    facts = simple()
    facts["items"].append(deepcopy(facts["items"][0]))
    variants.append(facts)
    facts = simple()
    facts["warehouses"].append(deepcopy(facts["warehouses"][0]))
    variants.append(facts)
    facts = simple()
    facts["snapshot_dates"] *= 2
    variants.append(facts)
    facts = simple()
    facts["snapshot_dates"] = []
    variants.append(facts)
    facts = simple()
    facts["items"] = []
    variants.append(facts)
    facts = simple()
    facts["warehouses"] = []
    variants.append(facts)
    for variant in variants:
        with pytest.raises(ValueError):
            calculate(variant)


@pytest.mark.parametrize("which", ["orders", "movements"])
def test_conflicting_same_id_copies_rejected(which):
    facts = source()
    copied = deepcopy(facts[which][0])
    copied["quantity"] += 1
    facts[which].append(copied)
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        calculate(facts)


@pytest.mark.parametrize(
    "change",
    [
        {"kind": "receipt", "from_warehouse_id": "W1"},
        {"kind": "receipt", "to_warehouse_id": None},
        {"kind": "transfer", "from_warehouse_id": "W1", "to_warehouse_id": "W1"},
        {"kind": "issue", "to_warehouse_id": "W2", "from_warehouse_id": "W1"},
        {"order_id": "O1"},
        {"related_movement_id": "I1"},
    ],
)
def test_movement_direction_and_unused_reference_fields(change):
    facts = source()
    facts["movements"][0].update(change)
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize(
    "change",
    [
        {"order_id": "unknown"},
        {"from_warehouse_id": "W2"},
        {"item_id": "unknown"},
        {"date": "2026-10-01"},
        {"quantity": 9},
    ],
)
def test_issue_order_constraints(change):
    facts = source()
    facts["movements"][2].update(change)
    with pytest.raises(ValueError):
        calculate(facts)


def test_issue_after_cancellation_and_cumulative_overfulfillment_rejected():
    facts = simple()
    facts["orders"] = [order(quantity=5, cancelled="2026-10-02")]
    facts["movements"] = [movement("I", "issue", 1, "2026-10-03", "W1", order_id="O1")]
    with pytest.raises(ValueError, match="lifetime"):
        calculate(facts)
    facts["orders"][0]["cancelled_on"] = None
    facts["movements"] = [
        movement("I", "issue", 3, "2026-10-02", "W1", order_id="O1"),
        movement("J", "issue", 3, "2026-10-03", "W1", order_id="O1"),
    ]
    with pytest.raises(ValueError, match="exceed order"):
        calculate(facts)


@pytest.mark.parametrize(
    "change",
    [
        {"related_movement_id": None},
        {"related_movement_id": "unknown"},
        {"related_movement_id": "R1"},
        {"related_movement_id": "S1"},
        {"date": "2026-10-03"},
        {"quantity": 6},
        {"order_id": "O1"},
    ],
)
def test_customer_return_reference_type_time_quantity_constraints(change):
    facts = source()
    facts["movements"][3].update(change)
    with pytest.raises(ValueError):
        calculate(facts)


def test_return_total_bound_and_posted_original_requirement():
    facts = source()
    facts["movements"].append(
        movement("C2", "customer_return", 4, "2026-10-08", incoming="W2", related="I1")
    )
    with pytest.raises(ValueError, match="exceed original"):
        calculate(facts)
    facts = source()
    facts["movements"][0]["status"] = "draft"
    with pytest.raises(ValueError, match="posted original"):
        calculate(facts)


def test_draft_return_can_reference_draft_original_without_physical_effect():
    facts = simple()
    facts["movements"] = [
        movement("I", "issue", 100, "2026-10-02", "W1", status="draft"),
        movement(
            "C", "customer_return", 100, "2026-10-03", incoming="W2", related="I", status="draft"
        ),
    ]
    assert calculate(facts)[0] == calculate(simple())[0]
    facts["movements"][1]["related_movement_id"] = "missing"
    with pytest.raises(ValueError):
        calculate(facts)


def test_physical_negative_on_any_ledger_day_including_after_last_snapshot():
    facts = simple()
    facts["movements"] = [movement("I", "issue", 11, "2026-10-09", "W1")]
    with pytest.raises(ValueError, match="negative"):
        calculate(facts)
    facts["movements"].append(movement("R", "receipt", 11, "2026-10-10", incoming="W1"))
    with pytest.raises(ValueError, match="2026-10-09"):
        calculate(facts)


def test_complete_four_by_four_opening_grid_and_all_zero_rows():
    facts = simple()
    facts["items"] = [
        {"item_id": f"I{i}", "name": f"가상 품목{i}", "base_unit": "개"} for i in range(4)
    ]
    facts["warehouses"] = [{"warehouse_id": f"W{i}", "name": f"가상 창고{i}"} for i in range(4)]
    facts["opening_balances"] = [
        {"item_id": item["item_id"], "warehouse_id": warehouse["warehouse_id"], "quantity": 0}
        for item in facts["items"]
        for warehouse in facts["warehouses"]
    ]
    answer, _ = calculate(facts)
    assert len(answer["stock_snapshots"][0]["stocks"]) == 16
    assert len(answer["organization_item_snapshots"][0]["items"]) == 4
    assert answer["order_snapshots"][0]["orders"] == []


def test_order_movement_unique_and_incoming_copy_bounds():
    facts = simple()
    facts["orders"] = [order(f"O{i:02}", 1) for i in range(40)]
    facts["movements"] = [
        movement(f"R{i:02}", "receipt", 1, "2026-10-02", incoming="W1") for i in range(60)
    ]
    facts["orders"] += deepcopy(facts["orders"])
    facts["movements"] += deepcopy(facts["movements"])
    answer, trace = calculate(facts)
    assert answer["stock_snapshots"][0]["stocks"][0]["receipt_quantity"] == 60
    assert len(trace[0]["output"]["deduplicated_order_ids"]) == 40
    assert len(trace[0]["output"]["deduplicated_movement_ids"]) == 60
    for field in ("orders", "movements"):
        variant = deepcopy(facts)
        variant[field].append(deepcopy(variant[field][0]))
        with pytest.raises(ValueError, match="at most"):
            calculate(variant)
    variant = simple()
    variant["orders"] = [order(f"O{i}", 1) for i in range(41)]
    with pytest.raises(ValueError, match="unique"):
        calculate(variant)
    variant = simple()
    variant["movements"] = [
        movement(f"R{i}", "receipt", 1, "2026-10-02", incoming="W1") for i in range(61)
    ]
    with pytest.raises(ValueError, match="unique"):
        calculate(variant)


def test_item_warehouse_and_snapshot_upper_bounds():
    for field in ("items", "warehouses"):
        facts = simple()
        facts[field] *= 5
        with pytest.raises(ValueError, match="at most"):
            calculate(facts)
    facts = simple()
    facts["snapshot_dates"] = [f"2026-10-0{i}" for i in range(1, 5)]
    with pytest.raises(ValueError, match="1..3"):
        calculate(facts)


def test_supplier_return_after_relocation_with_original_receipt_and_cumulative_limit():
    facts = simple()
    facts["movements"] = [
        movement("R", "receipt", 5, "2026-10-02", incoming="W1"),
        movement("T", "transfer", 5, "2026-10-02", "W1", "W2"),
        movement("S", "supplier_return", 3, "2026-10-03", "W2", related="R"),
        movement("S2", "supplier_return", 2, "2026-10-03", "W2", related="R"),
    ]
    answer, _ = calculate(facts)
    assert [row["on_hand"] for row in answer["stock_snapshots"][0]["stocks"]] == [10, 2]
    assert answer["stock_snapshots"][0]["stocks"][1]["supplier_return_quantity"] == 5
    facts["movements"][-1]["quantity"] = 3
    with pytest.raises(ValueError, match="exceed original"):
        calculate(facts)


def test_return_wrong_item_and_supplier_wrong_original_rejected():
    facts = source()
    facts["items"].append({"item_id": "B", "name": "가상 다른 키트", "base_unit": "개"})
    facts["opening_balances"] += [
        {"item_id": "B", "warehouse_id": warehouse, "quantity": 10} for warehouse in ("W1", "W2")
    ]
    facts["movements"][3]["item_id"] = "B"
    with pytest.raises(ValueError, match="incompatible original"):
        calculate(facts)
    facts = source()
    facts["movements"][4]["related_movement_id"] = "I1"
    with pytest.raises(ValueError, match="incompatible original"):
        calculate(facts)


def test_draft_and_future_issue_refs_are_validated_even_when_excluded():
    for status, day in (("draft", "2026-10-02"), ("posted", "2026-10-09")):
        facts = simple()
        facts["movements"] = [
            movement("I", "issue", 1, day, "W1", order_id="unknown", status=status)
        ]
        with pytest.raises(ValueError, match="incompatible order"):
            calculate(facts)


def test_valid_draft_overfulfillment_does_not_consume_order_or_stock():
    facts = simple()
    facts["orders"] = [order(quantity=1)]
    facts["movements"] = [
        movement("I", "issue", 100, "2026-10-02", "W1", order_id="O1", status="draft")
    ]
    answer, _ = calculate(facts)
    assert answer["order_snapshots"][0]["orders"] == [order_result("O1", "W1", 1, 0, 1, "active")]
    assert answer["stock_snapshots"][0]["stocks"][0]["on_hand"] == 10


def test_opening_date_snapshot_has_no_movement_and_reserves_same_day_order():
    facts = simple()
    facts["snapshot_dates"] = ["2026-10-01"]
    facts["orders"] = [order(quantity=12)]
    answer, _ = calculate(facts)
    assert answer["stock_snapshots"][0]["stocks"][0] == stock(
        "W1", 10, 0, 0, 0, 0, 0, 0, 10, 12, 0, 2
    )


@pytest.mark.parametrize(
    "field", ["items", "warehouses", "opening_balances", "orders", "movements", "snapshot_dates"]
)
def test_source_arrays_must_be_lists(field):
    facts = simple()
    facts[field] = tuple(facts[field])
    with pytest.raises(ValueError):
        calculate(facts)
