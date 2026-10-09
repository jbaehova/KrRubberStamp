# VAT bank reconciliation contract

`vat_bank_reconciliation_v1` adds a bounded private cash reconciliation around the existing VAT calculations. It does not change a deduction rule, create a filing deadline, establish a refund entitlement, or authorize an offset between taxpayers. Authored documents must present `processing_policy` as a fictional internal reconciliation policy.

The implementation lives in `rules/c_vat/bank_reconciliation.py`. Its single parent trace uses `C_VAT_BANK_RECONCILIATION`. The root owns registry routing, render labels, source catalog metadata, public documentation, and actual PDF/XLSX/HWPX integration.

## Literal source and bounds

The parent requires exactly `source_contract`, `processing_policy`, `as_of_date`, `filings`, and `transfers`. Policy must be a nonempty strict string. All bank dates use strict `YYYY-MM-DD` calendar dates.

There are one to three filings. Each has exactly `filing_id`, `taxpayer_id`, `registration_id`, `business_name`, and `facts`. All four identifying strings must be nonempty. Filing IDs are unique. Taxpayer IDs and registration IDs are separately unique, so this contract does not aggregate several sites belonging to one taxpayer. Parent business name must exactly match the child's business name.

There are zero to 200 literal transfer rows, with at most 100 unique transfer IDs after deduplication. Each row has exactly `transfer_id`, `filing_id`, `registration_id`, `date`, `status`, `kind`, and `amount`. Amount is a nonnegative strict integer; booleans, strings, and floats are rejected. Filing and registration references must both match the same filing, including on excluded rows.

An exact row copy with the same ID is a retransmission and counts once. Two distinct IDs with the same amount count separately. A conflicting same-ID row is rejected, even if both rows would otherwise be excluded. The identity bounds keep the proof and rendering scope finite. They are internal contract bounds, not tax law.

## Existing child calculations

The only child contracts are `vat_activity_evidence_v1`, `vat_document_reconciliation_v1`, and `vat_document_lifecycle_v1`. Bare derived engine inputs, another bank contract, and any nested `source_contract` are rejected. Each child explicitly identifies a general taxpayer and the period from `2026-01-01` through `2026-06-30`.

The bank wrapper uses a narrow child source schema. It requires the common tax fields and the raw collections belonging to the chosen child contract. It allows the existing supplier, vehicle, and site registers. It allows `scope_note`, `domain`, `synthetic_id`, `reference_period`, and `prior_declared_vat_paid`. It accepts either the literal prior-year site supply amount or the existing site-year register. Arbitrary extra contextual fields from other authored manuscripts are outside this wrapper. Put internal bank reconciliation instructions in the parent's visible policy instead.

For activity children, raw transaction rows have exact recognized factual fields and strict boolean values. All child sources recursively reject tax and reconciliation outcomes. The existing child contract still validates actual supply, evidence, activity, supplier, and vehicle links. A lifecycle child's `processing_date` must not exceed the parent's `as_of_date`. Its existing lifecycle validation also requires each status confirmation by that processing date.

After these scope checks, a late registry import calculates a deep copy of each child. Its complete original VAT answer and trace are preserved exactly. The wrapper does not reorder the child's internal collections, change its source selections, or derive additional tax amounts from the bank.

## Private cash arithmetic

Accepted rows have `status=executed`, a date on or before `as_of_date`, and kind `settlement_payment` or `settlement_refund`. Planned rows and future rows are excluded. Every `assessed_prepayment` row is excluded because the child's declared assessed prepayment has already affected its VAT settlement. The bank amount neither supplies nor checks that child assessment amount.

Executed settlement rows may have any strict calendar date under the visible internal policy. There is no invented July 25 cutoff, equality with a government payment deadline, or same-day requirement.

For each registration:

```text
tax_due = child.payable_vat - child.refund_vat
paid = sum(accepted settlement_payment amounts)
received = sum(accepted settlement_refund amounts)
net_outflow = paid - received
balance = tax_due - net_outflow
```

All signed balances are unmatched internal ledger amounts. A negative result can describe an overpaid ledger or a not-yet-received refund amount. A transfer's explicit private kind is preserved even when it reveals a discrepancy; the wrapper does not infer government eligibility from its direction. Separate registration positions remain visible even when aggregate totals are zero.

The answer contains `filing_calculations` with each full old child answer, `registration_settlements` with all subject IDs and the amounts above, and four totals: `tax_due_total`, `paid_total`, `received_total`, and `balance_total`. Filings sort by filing ID. Registration settlements sort by registration ID.

The single parent trace preserves canonical parent inputs and child traces keyed by filing ID. It records accepted IDs, excluded IDs with all applicable reasons, deduplicated IDs, the cash arithmetic for each registration, and the settlement answer. Input transfer copies are reduced to the unique sorted rows, while duplicate IDs remain in the trace. Parent row permutation preserves the complete answer and trace. Adding an exact retransmission preserves the answer while truthfully adding the deduplication marker. Caller data, returned answer, and returned trace do not share mutable containers.

## Independent arithmetic evidence

The tests compute complete small-money answers independently:

- A supply base of 100,000 with invoice evidence gives VAT due of 10,000. An accepted payment of 8,000 leaves balance 2,000.
- A second independent taxpayer has a deductible 10,000 purchase VAT refund. A received refund of 8,000 leaves its balance at -2,000. Combined tax due and combined balance are zero, while both registrations retain their own nonzero discrepancy.
- Distinct 4,000 payment IDs sum to 8,000. Exact retransmissions of either ID do not increase that total.
- A supply base of 10,000,000 produces output VAT of 1,000,000. The child's 500,000 assessed prepayment leaves due of 500,000. Its 500,000 settlement payment closes the ledger; a separate bank prepayment row is excluded rather than deducted again.
- A 12,000 payment against 10,000 due leaves balance -2,000. Receipt of only 3,000 from a 10,000 refund leaves balance -7,000.

Other tests cover all three raw child contracts, unchanged complete child answers and traces, planned/future/excluded rows, conflicting IDs on excluded rows, strict types, unknown or missing fields, subject mismatches, confirmation cutoffs, collection bounds, canonical parent permutation, and mutable-container isolation.

Validation command:

```sh
uv run pytest tests/test_vat_bank_reconciliation.py tests/test_vat_document_reconciliation.py::test_all_300_frozen_batch_one_vat_answers_and_traces_are_unchanged
```

Result: **95 passed**, comprising 94 new contract tests and the frozen Batch1 VAT regression over all 300 existing answers and traces. Ruff check and formatting pass for the two new Python files. Actual document rendering is reserved for root integration and is not claimed by this module handoff.

No dataset cases, generated benchmark factories, model APIs, old VAT engines, or root-owned integration files were changed by this worker.

The child payable_vat and refund_vat values are integer-won filing calculations. National treasury collection/payment discards fractions below ten won under [National Treasury Management Act Article 47](https://law.go.kr/lsLinkCommonInfo.do?lsJoLnkSeq=1031453583), a separate step outside the unchanged VAT engine. Signed balance here is a private comparison with actual bank cash, not a statutory arrears amount or an adjudicated refund entitlement.
