# Private inventory snapshot source contract

`extract_inventory_snapshots_v1` is an optional literal-source contract implemented in `rules/d_extract/inventory_snapshots.py`. Its single rule is `D_INVENTORY_SNAPSHOTS`. It reconciles physical quantities using visible synthetic private handling instructions. It does not determine monetary valuation, tax treatment, accounting compliance, FIFO, sourcing priority or automatic allocation.

The root-frozen bounded proposal is implemented without semantic changes. `calculate(source)` returns `(answer, [trace])`. Public registry routing, dataset source metadata, rendering labels, export support and actual document reconstruction belong to the parent integration. This report does not claim those checks completed.

## Source shape

The exact top-level fields are `source_contract`, `processing_policy`, `opening_date`, `snapshot_dates`, `items`, `warehouses`, `opening_balances`, `orders` and `movements`. Unknown, derived or missing fields are rejected. Nonempty strings and strict ISO calendar dates are required. Quantity fields accept integers and reject booleans, floats and numeric strings.

Items have `item_id`, `name` and `base_unit`. Warehouses have `warehouse_id` and `name`. Each array has 1..4 rows with unique IDs. Opening balances have `item_id`, `warehouse_id` and nonnegative `quantity`. They must cover the complete item and warehouse cross-grid, including zero quantities, with no repeated pair.

There are 1..3 distinct snapshot dates, each on or after the opening date. Orders have `order_id`, `item_id`, `warehouse_id`, positive `quantity`, `placed_on` and nullable `cancelled_on`. Orders are already-confirmed private reservations. They cannot precede the opening date, and cancellation cannot precede placement. There are at most 40 unique orders and 80 incoming order rows.

Movements have `movement_id`, `item_id`, `date`, `kind`, positive `quantity`, `from_warehouse_id`, `to_warehouse_id`, `order_id`, `related_movement_id` and `status`. All fields must be present, with unused references explicitly null. There are at most 60 unique movements and 120 incoming movement rows. Dates must follow the opening date. Status is `posted` or `draft`.

Movement kinds are `receipt`, `issue`, `transfer`, `customer_return` and `supplier_return`. Receipt and customer return flow into a known warehouse. Issue and supplier return flow out. Transfer moves the same physical quantity atomically between distinct known warehouses. Only an issue can reference an order. Its item and origin warehouse must match the order, and its date must lie between placement and cancellation inclusive. Posted issues collectively cannot exceed their order quantity.

Customer returns reference an original same-item issue and may enter another warehouse. Supplier returns reference an original same-item receipt and may leave a warehouse reached by internal relocation. Return dates cannot precede the original. Posted returns require posted originals, and their collective quantity cannot exceed that original quantity. Draft returns may reference posted or draft originals but still require valid type, item and date. Return-to-return chains are rejected.

Exact transmitted copies of an order or movement ID are deduplicated. Conflicting same-ID rows are rejected. Distinct IDs retain separate effects even when all quantities and other fields are equal. Item IDs, warehouse IDs and opening grid pairs cannot be repeated.

## Physical and reservation semantics

All posted movements in the complete supplied ledger participate in physical validation. The engine aggregates each actual posted day before checking nonnegative warehouse stock. Input order never implies within-day ordering. A negative physical balance on any posted day is rejected, including days later than the last requested historical snapshot. Drafts do not affect physical quantities.

At a snapshot, physical flows include posted movements dated on or before that date. Confirmed unfulfilled orders reserve their named warehouse stock. Cancellation takes effect at the end of its date and releases the unfulfilled remainder, while a same-date posted issue remains valid. Customer returns restore stock at their actual receiving warehouse and do not reopen fulfillment. Fully issued orders have status `fulfilled`, including after cancellation. Other statuses are `active`, `cancelled` and `not_yet`.

Warehouse availability is `max(on_hand - reserved_quantity, 0)`. Its reservation shortage is `max(reserved_quantity - on_hand, 0)`. Organization availability and shortage sum these warehouse results independently. Stock at another warehouse cannot offset a local reservation shortage. Physical organization quantity is conserved by transfer.

## Stable answer constructor

The answer has exactly three arrays:

- `stock_snapshots`: each row has `date` and `stocks`.
- `order_snapshots`: each row has `date` and `orders`.
- `organization_item_snapshots`: each row has `date` and `items`.

Every stock row has `item_id`, `warehouse_id`, `opening_quantity`, `receipt_quantity`, `issued_quantity`, `transfer_in_quantity`, `transfer_out_quantity`, `customer_return_quantity`, `supplier_return_quantity`, `on_hand`, `reserved_quantity`, `available_quantity` and `reservation_shortfall`.

Every order row has `order_id`, `item_id`, `warehouse_id`, `quantity`, `issued_quantity`, `reserved_quantity` and `status`. Every organization row has `item_id`, `on_hand`, `reserved_quantity`, `available_quantity` and `reservation_shortfall`.

Dates sort ascending. Stock rows sort by item ID then warehouse ID. Order rows sort by order ID. Organization rows sort by item ID. All grid rows are present, including zeros. Canonical trace inputs sort source arrays and preserve transmitted copies. Trace output lists deduplicated IDs, per-date posted and excluded movement IDs, active order IDs, explicit private derivation formulas and a separate copy of the complete answer. Caller source, returned answer and trace do not share mutable aliases.

## Worker verification

The 74 new tests passed. A combined run of the new tests and the existing extraction, extraction evidence, fulfillment, procurement and cart procurement suites passed 412 tests. Ruff checks and formatting passed for the two worker-owned Python files.

A full manually specified three-snapshot answer verifies a two-warehouse transfer, local shortage despite remote surplus, partial then complete fulfillment, cancellation release, customer return into another warehouse, supplier return after relocation, future receipts and draft exclusions. Additional manual checks cover completed orders staying fulfilled after returns, same-date cancellation issues, identical transmitted copies versus equal distinct receipts, zero opening quantities, all 16 rows of a four-by-four grid, and independent organization quantity and availability changes.

Boundary checks cover strict row shapes, scalar types, ISO dates, array types, ID conflicts, all source references even when excluded by a historical snapshot, return type and cumulative quantity limits, issue lifetimes, posted and draft distinctions, all source bounds, caller mutation isolation and same-day permutation invariance.

The existing Batch1 D300 literal-source cases were calculated through the public registry once and compared against their released projected gold and full traces. All 300 remained equal. Evidence is frozen in `tmp/inventory_snapshots_contract/worker/legacy_D300.json`. This legacy check does not claim actual document reconstruction or full Batch1 integrity, which remain parent-owned.

No authored dataset cases, dataset generators or model API calls were introduced by this worker. Dataset authors retain literal question ownership. The final project scope remains exactly 2,400 cases across Batch1 and Batch2.
