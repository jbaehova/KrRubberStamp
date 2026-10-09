"""Reconcile physical stock under an explicit synthetic private handling policy.

No value, tax treatment, sourcing priority or automatic allocation is inferred.
"""

from collections import defaultdict
from copy import deepcopy
from datetime import date

CONTRACT = "extract_inventory_snapshots_v1"
RULE_ID = "D_INVENTORY_SNAPSHOTS"
PARENT_FIELDS = {
    "source_contract",
    "processing_policy",
    "opening_date",
    "snapshot_dates",
    "items",
    "warehouses",
    "opening_balances",
    "orders",
    "movements",
}
ITEM_FIELDS = {"item_id", "name", "base_unit"}
WAREHOUSE_FIELDS = {"warehouse_id", "name"}
OPENING_FIELDS = {"item_id", "warehouse_id", "quantity"}
ORDER_FIELDS = {"order_id", "item_id", "warehouse_id", "quantity", "placed_on", "cancelled_on"}
MOVEMENT_FIELDS = {
    "movement_id",
    "item_id",
    "date",
    "kind",
    "quantity",
    "from_warehouse_id",
    "to_warehouse_id",
    "order_id",
    "related_movement_id",
    "status",
}
FLOW_FIELDS = (
    "receipt_quantity",
    "issued_quantity",
    "transfer_in_quantity",
    "transfer_out_quantity",
    "customer_return_quantity",
    "supplier_return_quantity",
)


def _text(value, name):
    if type(value) is not str or not value.strip():
        raise ValueError(f"Inventory {name} must be a nonempty string")
    return value


def _date(value, name):
    _text(value, name)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Inventory {name} must be an ISO calendar date") from error
    if parsed.isoformat() != value:
        raise ValueError(f"Inventory {name} must use YYYY-MM-DD")
    return value


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"Inventory {name} must be an integer at least {minimum}")
    return value


def _rows(value, fields, name, maximum):
    if type(value) is not list or len(value) > maximum:
        raise ValueError(f"Inventory {name} must be a list of at most {maximum} rows")
    for row in value:
        if type(row) is not dict or set(row) != fields:
            raise ValueError(f"Inventory {name} has unknown or missing fields")
    return value


def _deduplicate(rows, identity, maximum):
    originals, duplicates = {}, set()
    for row in rows:
        key = _text(row[identity], identity)
        if key in originals:
            old = originals[key]
            if old != row or any(type(old[field]) is not type(row[field]) for field in row):
                raise ValueError(f"Conflicting duplicate inventory {identity}: {key}")
            duplicates.add(key)
        originals[key] = row
    if len(originals) > maximum:
        raise ValueError(f"Inventory exceeds {maximum} unique {identity} rows")
    return [originals[key] for key in sorted(originals)], sorted(duplicates)


def _identities(rows, identity):
    by_id = {}
    for row in rows:
        key = _text(row[identity], identity)
        if key in by_id:
            raise ValueError(f"Duplicate inventory {identity}: {key}")
        _text(row["name"], "name")
        by_id[key] = row
    if not by_id:
        raise ValueError(f"Inventory requires at least one {identity}")
    return by_id


def _validate(source):
    if type(source) is not dict or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown inventory snapshot source contract")
    if set(source) != PARENT_FIELDS:
        raise ValueError("Inventory source has unknown or missing fields")
    _text(source["processing_policy"], "processing_policy")
    opening_date = _date(source["opening_date"], "opening_date")
    snapshots = source["snapshot_dates"]
    if type(snapshots) is not list or not 1 <= len(snapshots) <= 3:
        raise ValueError("Inventory requires 1..3 snapshot dates")
    for day in snapshots:
        if _date(day, "snapshot_date") < opening_date:
            raise ValueError("Inventory snapshot predates opening balance")
    if len(set(snapshots)) != len(snapshots):
        raise ValueError("Inventory snapshot dates must be unique")
    items = _identities(_rows(source["items"], ITEM_FIELDS, "items", 4), "item_id")
    for item in items.values():
        _text(item["base_unit"], "base_unit")
    warehouses = _identities(
        _rows(source["warehouses"], WAREHOUSE_FIELDS, "warehouses", 4), "warehouse_id"
    )
    opening = {}
    for row in _rows(source["opening_balances"], OPENING_FIELDS, "opening_balances", 16):
        key = (_text(row["item_id"], "item_id"), _text(row["warehouse_id"], "warehouse_id"))
        if key[0] not in items or key[1] not in warehouses or key in opening:
            raise ValueError("Inventory opening balance has unknown or repeated item/warehouse")
        opening[key] = _integer(row["quantity"], "opening quantity")
    if set(opening) != {(item, warehouse) for item in items for warehouse in warehouses}:
        raise ValueError("Inventory requires the complete opening item/warehouse grid")
    raw_orders = _rows(source["orders"], ORDER_FIELDS, "orders", 80)
    for row in raw_orders:
        _text(row["order_id"], "order_id")
        if _text(row["item_id"], "item_id") not in items:
            raise ValueError("Inventory order references unknown item")
        if _text(row["warehouse_id"], "warehouse_id") not in warehouses:
            raise ValueError("Inventory order references unknown warehouse")
        _integer(row["quantity"], "order quantity", 1)
        if _date(row["placed_on"], "placed_on") < opening_date:
            raise ValueError("Inventory order predates opening balance")
        if row["cancelled_on"] is not None:
            if _date(row["cancelled_on"], "cancelled_on") < row["placed_on"]:
                raise ValueError("Inventory cancellation predates order")
    orders, duplicate_orders = _deduplicate(raw_orders, "order_id", 40)
    order_map = {row["order_id"]: row for row in orders}
    raw_movements = _rows(source["movements"], MOVEMENT_FIELDS, "movements", 120)
    for row in raw_movements:
        _text(row["movement_id"], "movement_id")
        if _text(row["item_id"], "item_id") not in items:
            raise ValueError("Inventory movement references unknown item")
        if _date(row["date"], "movement date") <= opening_date:
            raise ValueError("Inventory movement must follow opening balance date")
        _integer(row["quantity"], "movement quantity", 1)
        if _text(row["status"], "status") not in {"posted", "draft"}:
            raise ValueError("Unsupported inventory movement status")
        kind = _text(row["kind"], "kind")
        if kind not in {"receipt", "issue", "transfer", "customer_return", "supplier_return"}:
            raise ValueError("Unsupported inventory movement kind")
        for field in ("from_warehouse_id", "to_warehouse_id"):
            if row[field] is not None and _text(row[field], field) not in warehouses:
                raise ValueError("Inventory movement references unknown warehouse")
        for field in ("order_id", "related_movement_id"):
            if row[field] is not None:
                _text(row[field], field)
        outgoing, incoming = row["from_warehouse_id"], row["to_warehouse_id"]
        if kind in {"receipt", "customer_return"}:
            valid_direction = outgoing is None and incoming is not None
        elif kind in {"issue", "supplier_return"}:
            valid_direction = outgoing is not None and incoming is None
        else:
            valid_direction = outgoing is not None and incoming is not None and outgoing != incoming
        if not valid_direction:
            raise ValueError("Inventory movement has invalid warehouse direction")
        if kind != "issue" and row["order_id"] is not None:
            raise ValueError("Inventory order_id is only valid on issues")
        if (
            kind not in {"customer_return", "supplier_return"}
            and row["related_movement_id"] is not None
        ):
            raise ValueError("Inventory related_movement_id is only valid on returns")
        if kind in {"customer_return", "supplier_return"} and row["related_movement_id"] is None:
            raise ValueError("Inventory return requires its original movement")
    movements, duplicate_movements = _deduplicate(raw_movements, "movement_id", 60)
    movement_map = {row["movement_id"]: row for row in movements}
    issued, returned = defaultdict(int), defaultdict(int)
    for row in movements:
        order_id = row["order_id"]
        if order_id is not None:
            order = order_map.get(order_id)
            if order is None or (row["item_id"], row["from_warehouse_id"]) != (
                order["item_id"],
                order["warehouse_id"],
            ):
                raise ValueError("Inventory issue references incompatible order")
            if row["date"] < order["placed_on"] or (
                order["cancelled_on"] is not None and row["date"] > order["cancelled_on"]
            ):
                raise ValueError("Inventory issue falls outside its order lifetime")
            if row["status"] == "posted":
                issued[order_id] += row["quantity"]
        related_id = row["related_movement_id"]
        if related_id is not None:
            original = movement_map.get(related_id)
            expected = "issue" if row["kind"] == "customer_return" else "receipt"
            if (
                original is None
                or original["kind"] != expected
                or original["item_id"] != row["item_id"]
            ):
                raise ValueError("Inventory return references incompatible original movement")
            if row["date"] < original["date"]:
                raise ValueError("Inventory return predates original movement")
            if row["status"] == "posted":
                if original["status"] != "posted":
                    raise ValueError("Posted inventory return requires posted original")
                returned[related_id] += row["quantity"]
    if any(quantity > order_map[key]["quantity"] for key, quantity in issued.items()):
        raise ValueError("Inventory posted issues exceed order quantity")
    if any(quantity > movement_map[key]["quantity"] for key, quantity in returned.items()):
        raise ValueError("Inventory posted returns exceed original movement quantity")
    physical = dict(opening)
    by_date = defaultdict(list)
    for row in movements:
        if row["status"] == "posted":
            by_date[row["date"]].append(row)
    for day in sorted(by_date):
        for row in by_date[day]:
            item, quantity = row["item_id"], row["quantity"]
            if row["from_warehouse_id"] is not None:
                physical[(item, row["from_warehouse_id"])] -= quantity
            if row["to_warehouse_id"] is not None:
                physical[(item, row["to_warehouse_id"])] += quantity
        if any(quantity < 0 for quantity in physical.values()):
            raise ValueError(f"Inventory physical stock is negative at end of {day}")
    return opening, orders, movements, duplicate_orders, duplicate_movements


def calculate(source: dict) -> tuple[dict, list[dict]]:
    """Return end-of-day physical quantities and confirmed unfulfilled reservations."""
    opening, orders, movements, duplicate_orders, duplicate_movements = _validate(source)
    answer = {"stock_snapshots": [], "order_snapshots": [], "organization_item_snapshots": []}
    snapshot_derivations = []
    for day in sorted(source["snapshot_dates"]):
        flows = {key: dict.fromkeys(FLOW_FIELDS, 0) for key in opening}
        issued = defaultdict(int)
        accepted = []
        for row in movements:
            if row["status"] != "posted" or row["date"] > day:
                continue
            accepted.append(row["movement_id"])
            item, quantity, kind = row["item_id"], row["quantity"], row["kind"]
            if kind == "transfer":
                flows[(item, row["from_warehouse_id"])]["transfer_out_quantity"] += quantity
                flows[(item, row["to_warehouse_id"])]["transfer_in_quantity"] += quantity
            else:
                warehouse = (
                    row["to_warehouse_id"]
                    if kind in {"receipt", "customer_return"}
                    else row["from_warehouse_id"]
                )
                field = {
                    "receipt": "receipt_quantity",
                    "issue": "issued_quantity",
                    "customer_return": "customer_return_quantity",
                    "supplier_return": "supplier_return_quantity",
                }[kind]
                flows[(item, warehouse)][field] += quantity
            if row["order_id"] is not None:
                issued[row["order_id"]] += quantity
        reservations = defaultdict(int)
        order_rows = []
        for order in orders:
            quantity = issued[order["order_id"]]
            if order["placed_on"] > day:
                status = "not_yet"
            elif quantity == order["quantity"]:
                status = "fulfilled"
            elif order["cancelled_on"] is not None and order["cancelled_on"] <= day:
                status = "cancelled"
            else:
                status = "active"
            reserved = order["quantity"] - quantity if status == "active" else 0
            reservations[(order["item_id"], order["warehouse_id"])] += reserved
            order_rows.append(
                {
                    "order_id": order["order_id"],
                    "item_id": order["item_id"],
                    "warehouse_id": order["warehouse_id"],
                    "quantity": order["quantity"],
                    "issued_quantity": quantity,
                    "reserved_quantity": reserved,
                    "status": status,
                }
            )
        stock_rows = []
        for (item, warehouse), initial in sorted(opening.items()):
            flow = flows[(item, warehouse)]
            on_hand = (
                initial
                + flow["receipt_quantity"]
                + flow["transfer_in_quantity"]
                + flow["customer_return_quantity"]
                - flow["issued_quantity"]
                - flow["transfer_out_quantity"]
                - flow["supplier_return_quantity"]
            )
            reserved = reservations[(item, warehouse)]
            stock_rows.append(
                {
                    "item_id": item,
                    "warehouse_id": warehouse,
                    "opening_quantity": initial,
                    **flow,
                    "on_hand": on_hand,
                    "reserved_quantity": reserved,
                    "available_quantity": max(on_hand - reserved, 0),
                    "reservation_shortfall": max(reserved - on_hand, 0),
                }
            )
        organization = []
        for item in sorted({key[0] for key in opening}):
            rows = [row for row in stock_rows if row["item_id"] == item]
            organization.append(
                {
                    "item_id": item,
                    **{
                        field: sum(row[field] for row in rows)
                        for field in (
                            "on_hand",
                            "reserved_quantity",
                            "available_quantity",
                            "reservation_shortfall",
                        )
                    },
                }
            )
        answer["stock_snapshots"].append({"date": day, "stocks": stock_rows})
        answer["order_snapshots"].append({"date": day, "orders": order_rows})
        answer["organization_item_snapshots"].append({"date": day, "items": organization})
        snapshot_derivations.append(
            {
                "date": day,
                "posted_movement_ids": accepted,
                "excluded_movement_ids": [
                    row["movement_id"] for row in movements if row["movement_id"] not in accepted
                ],
                "pending_order_ids": [
                    row["order_id"] for row in order_rows if row["status"] == "active"
                ],
                "physical_formula": "opening + receipts + transfer_in + customer_returns - issues - transfer_out - supplier_returns",
                "reservation_formula": "active confirmed quantity - posted linked issues; returns do not reopen orders",
                "organization_availability_formula": "sum warehouse max(on_hand - reserved, 0); sum warehouse max(reserved - on_hand, 0)",
            }
        )
    canonical = deepcopy(source)
    canonical["snapshot_dates"].sort()
    for field, identity in (
        ("items", "item_id"),
        ("warehouses", "warehouse_id"),
        ("orders", "order_id"),
        ("movements", "movement_id"),
    ):
        canonical[field].sort(key=lambda row: row[identity])
    canonical["opening_balances"].sort(key=lambda row: (row["item_id"], row["warehouse_id"]))
    trace = {
        "rule_id": RULE_ID,
        "inputs": canonical,
        "output": {
            "deduplicated_order_ids": duplicate_orders,
            "deduplicated_movement_ids": duplicate_movements,
            "snapshots": snapshot_derivations,
            "comparison": deepcopy(answer),
        },
    }
    return answer, [trace]
