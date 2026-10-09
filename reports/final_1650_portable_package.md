# 1,650-case portable package verification

The packaged manuscripts contain exactly 1,650 individually written cases. Batch 1 contains 1,200 cases. Batch 2 contains 450 cases: 100 each in year-end tax, payroll, and VAT, and 150 in document extraction. No Batch 2 case beyond A100, B100, C100, or D150 is packaged. This verification neither adds cases to the release nor approves their editorial content.

## Verification performed

A wheel was built with `uv build --wheel` and installed into an isolated Python 3.12 virtual environment. The installed code ran from `/private/tmp` with Python isolated mode (`-I`) and `PYTHONPATH` removed. The checkout was absent from the import search path. All calculation, rendering, restoration, and CLI imports resolved to the installed package. The virtual environment and results remained in `tmp/verify_final1650_portable_package/`.

Both packaged batches passed `check_completed_cases`, including their contiguous IDs and exact domain and difficulty quotas. Every one of the 1,650 cases passed its required manuscript fields, calculation, projected gold schema, and exact gold self-grading. The package and checkout matched on every whole manuscript, full answer, full trace, and projected gold SHA-256. The configured gold answers contain 18,001 graded fields. The ordered comparison digest is `9cab0057c368a09ab68c0e1e052d82b6bdb3a3326310c63afe76ca268e106ec9`.

Four literal Batch 2 cases were rendered and restored through the installed package. Their restored facts and full calculated answers and traces matched the checkout:

| Case | Domain | Source contract | Actual documents |
| --- | --- | --- | ---: |
| A001 | Year-end tax | `yearend_pay_statement_v1` | 3 |
| B082 | Payroll | `payroll_statement_revision_v1` | 4 |
| C062 | VAT | `vat_itemized_activity_evidence_v1` | 2 |
| D123 | Document extraction | `extract_cart_procurement_v1` | 4 |

These 13 documents cover PDF, XLSX, and HWPX. Separately, B082 and C062 were each rendered into all three formats. Six physical source edits changed the selected payroll health-insurance notification basis or the per-unit VAT discount. Restoration reproduced the edited literal facts exactly, and the installed registry produced the complete expected edited answer and trace. Each original extraction map, gold file, and trace file remained byte-identical.

The wheel includes all 37 completed manuscript JSON files, all six source YAML files, the Korean font and its OFL license, the payroll tax table, dataset and code licenses, `DATA_SPEC.md`, and `DECISIONS.md`. It also includes the support reports for payroll statement revisions, itemized VAT pricing, VAT bank reconciliation, VAT batch allocation, and inventory snapshots. The installed font SHA-256 is `e9b3e57e87fe49cd8529b44818036256e55ac47104a58b604ab0800386d168ad`. The installed tax table SHA-256 is `1087397e3f6e4a1257aa194191112b4a925e17462e54854e9c4aa8e7abac6ae9`. Both match the checkout assets.

The installed CLI ran `generate --seed 165009 --n 4` with an explicit output directory inside this verification workspace. These four auxiliary smoke tasks are separate from the published individually written corpus. Validation passed 4/4. Oracle exact match and field accuracy were 1.0 over 98 fields. Null exact match and field accuracy were 0.0. No model API was invoked.

## Limits and evidence

The 1,650-case check compares deterministic calculation and schema behavior with the checkout. It does not constitute independent professional tax or legal review. The human expert review queue remains pending. Existing contract and rounding limits in `DATA_SPEC.md` apply, including the distinction between won-level VAT computation and actual national cash settlement.

The initial wheel contained eight accepted Batch 2 ledger chunks and was a preparation check. A subsequent complete wheel contained all nine accepted chunks, or 450 Batch 2 cases. After final export integration found that JSON reserialization changed reviewed manuscript bytes, the export writer was corrected to copy completed source files exactly. A new wheel was built with that correction and installed into a separate isolated environment. All 1,650 full manuscript, answer, trace, and gold comparisons passed again, with the same digest and 18,001 graded fields. The four representative renders, six physical source edits, and four-task CLI checks also passed again.

The installed export writer preserved the exact bytes of all 37 packaged manuscript files, covering all 1,650 cases. An additional deliberately irregular JSON formatting fixture retained its original bytes. Completed exports rejected missing cases, extra cases, and altered cases. A proper subset was accepted only in preview mode. The installed export module matched the current checkout byte for byte. All other packaged Python modules, calculation rules, manuscripts, and assets remained byte-identical to the earlier complete wheel.

The latest artifact hash, byte size, packaged ledger count, metadata hashes, and regression evidence are handed off separately in `tmp/verify_export_bytes_final_package/final_handoff.json`. They are not embedded in this report to avoid a wheel hashing its own changing hash. Earlier evidence remains in `tmp/verify_final1650_portable_package/final_handoff.json`.

Initial evidence files remain under `tmp/verify_final1650_portable_package/`. The fresh verification records are `checkout_reference.json`, `portable_result.json`, `export_snapshot_result.json`, `actual_edit_checks.json`, `cli_validation.json`, `cli_oracle.json`, and `cli_null.json` under `tmp/verify_export_bytes_final_package/`. The root owns the complete published corpus render, validation, export, GitHub checks, and Hugging Face publication. This workstream does not claim to have re-rendered all 1,650 published tasks.
