"""Exact VAT ledger calculation, with transaction-level duplicate reconciliation.

Batch 1 supports domestic taxable supplies with exact integer supply/tax splits.
Mixed exempt/common-input allocation, penalties and other tax credits are outside
the generated scope. Receipt credit cannot turn a tax liability into a refund;
prepaid assessed tax is deducted afterwards, as on the official return form.
"""

from collections import defaultdict
from datetime import date

EVIDENCE = {"tax_invoice", "card_receipt", "cash_receipt", "cash_ledger", "receipt"}
PURPOSES = {
    "business",
    "hospitality",
    "private",
    "passenger_car_purchase",
    "passenger_car_rental",
    "passenger_car_maintenance",
    "exempt_business",
    "land",
}


def _money(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer won amount")
    return value


def _split(row):
    amount = _money(row["amount"], "amount")
    if not isinstance(row["includes_vat"], bool):
        raise ValueError("includes_vat must be a boolean")
    if not row["taxable"]:
        raise ValueError("Batch 1 VAT engine does not support exempt sales or purchases")
    # Exact input monetary amounts are intentional. No implicit rounding policy.
    divisor = 11 if row["includes_vat"] else 10
    if amount % divisor:
        raise ValueError("amount must admit an exact 10% integer-won VAT split")
    vat = amount // divisor
    base = amount - vat if row["includes_vat"] else amount
    return base, vat, base + vat


def calculate(scenario: dict) -> tuple[dict, list[dict]]:
    """Return public answer fields and a JSON-serializable rule trace.

    A transaction may appear in several documents. All financial/business facts
    must agree; its evidence kinds are unioned and invoice issuance dominates
    receipt-credit classification. Distinct transaction IDs are never collapsed.
    """
    if scenario.get("taxpayer_type", "general") != "general":
        raise ValueError("only general VAT taxpayers are supported")
    start = date.fromisoformat(scenario["period_start"])
    end = date.fromisoformat(scenario["period_end"])
    if (start, end) != (date(2026, 1, 1), date(2026, 6, 30)):
        raise ValueError("only 2026 first-half is supported")
    trace = []

    def record(rule_id, inputs, output):
        trace.append({"rule_id": rule_id, "inputs": inputs, "output": output})

    grouped = defaultdict(list)
    for row in scenario["transactions"]:
        if row["direction"] not in {"sale", "purchase"}:
            raise ValueError("direction must be sale or purchase")
        if row["evidence"] not in EVIDENCE or row["purpose"] not in PURPOSES:
            raise ValueError("unsupported evidence or purchase purpose")
        if not isinstance(row["transaction_id"], str) or not row["transaction_id"]:
            raise ValueError("transaction_id is required")
        grouped[row["transaction_id"]].append(row)

    canonical = []
    agree = (
        "direction",
        "date",
        "taxable",
        "business_related",
        "purpose",
        "supplier_general",
        "vat_separately_stated",
        "vehicle_subject_excise",
        "vehicle_direct_business",
        "counterparty_consumer",
    )
    for transaction_id, rows in sorted(grouped.items()):
        row = rows[0]
        split = _split(row)
        for item in rows:
            if "issued_receipt_gross" in item:
                issued = _money(item["issued_receipt_gross"], "issued_receipt_gross")
                if item["direction"] != "sale" or issued > split[2]:
                    raise ValueError("Issued receipt gross exceeds or mismatches the supply")
            if "documented_input_vat" in item:
                documented = _money(item["documented_input_vat"], "documented_input_vat")
                if item["direction"] != "purchase" or documented not in {0, split[1]}:
                    raise ValueError("Only full or absent documentary input VAT is supported")
        for other in rows[1:]:
            if (
                _split(other) != split
                or any(other[k] != row[k] for k in agree)
                or any(
                    other.get(k) != row.get(k)
                    for k in ("issued_receipt_gross", "documented_input_vat")
                )
            ):
                raise ValueError(f"conflicting duplicate facts: {transaction_id}")
        evidence = {r["evidence"] for r in rows}
        invoice = any(r["invoice_issued"] for r in rows) or "tax_invoice" in evidence
        canonical.append((transaction_id, row, split, evidence, invoice))
        record(
            "VAT_DEDUP",
            {
                "transaction_id": transaction_id,
                "document_ids": [r["document_id"] for r in rows],
                "evidence": sorted(evidence),
            },
            {"occurrences": len(rows), "invoice_issued": invoice, "counted_once": True},
        )

    tax_base = output_vat = input_vat = noncreditable = receipt_base = 0
    in_period = 0
    for transaction_id, row, (base, vat, gross), evidence, invoice in canonical:
        included = start <= date.fromisoformat(row["date"]) <= end
        record("VAT_PERIOD", {"date": row["date"], "transaction_id": transaction_id}, included)
        if not included:
            continue
        in_period += 1
        record(
            "VAT_TAX_BASE",
            {
                "transaction_id": transaction_id,
                "amount": row["amount"],
                "includes_vat": row["includes_vat"],
            },
            {"supply_base": base, "vat": vat, "gross": gross},
        )
        if row["direction"] == "sale":
            tax_base += base
            output_vat += vat
            record("VAT_OUTPUT_10", {"supply_base": base}, vat)
            qualifies = bool(evidence & {"card_receipt", "cash_receipt"}) and not invoice
            issued_gross = row.get("issued_receipt_gross", gross)
            if qualifies:
                receipt_base += issued_gross
            receipt_inputs = {
                "transaction_id": transaction_id,
                "evidence": sorted(evidence),
                "invoice_issued": invoice,
                "counterparty_consumer": row["counterparty_consumer"],
            }
            if "issued_receipt_gross" in row:
                receipt_inputs["issued_receipt_gross"] = issued_gross
            record(
                "VAT_RECEIPT_BASE",
                receipt_inputs,
                {"eligible_gross": issued_gross if qualifies else 0},
            )
            continue

        input_vat += vat
        blocked_rule = None
        if not row["business_related"] or row["purpose"] == "private":
            blocked_rule = "VAT_NONBUSINESS"
        elif row["purpose"] == "hospitality":
            blocked_rule = "VAT_HOSPITALITY"
        elif (
            row["purpose"].startswith("passenger_car")
            and row["vehicle_subject_excise"]
            and not row["vehicle_direct_business"]
        ):
            blocked_rule = "VAT_PASSENGER_CAR"
        elif row["purpose"] in {"exempt_business", "land"}:
            blocked_rule = "VAT_EXEMPT_LAND"
        elif not evidence & {"tax_invoice", "card_receipt", "cash_receipt"}:
            blocked_rule = "VAT_INPUT_EVIDENCE"
        elif not row["supplier_general"] or not row["vat_separately_stated"]:
            blocked_rule = "VAT_INPUT_EVIDENCE"
        documented = row.get("documented_input_vat", vat)
        deducted = 0 if blocked_rule else documented
        excluded = vat - deducted
        noncreditable += excluded
        evidence_inputs = {
            "transaction_id": transaction_id,
            "purpose": row["purpose"],
            "business_related": row["business_related"],
            "evidence": sorted(evidence),
            "supplier_general": row["supplier_general"],
            "vat_separately_stated": row["vat_separately_stated"],
            "vehicle_subject_excise": row["vehicle_subject_excise"],
            "vehicle_direct_business": row["vehicle_direct_business"],
        }
        if "documented_input_vat" in row:
            evidence_inputs["documented_input_vat"] = documented
        record(
            blocked_rule or "VAT_INPUT_EVIDENCE",
            evidence_inputs,
            {"deductible": deducted, "noncreditable": excluded},
        )

    deductible = input_vat - noncreditable
    prior_supply = _money(scenario["prior_year_site_supply_base"], "prior_year_site_supply_base")
    prior_credit = _money(
        scenario["receipt_credit_previously_claimed"], "receipt_credit_previously_claimed"
    )
    if scenario["business_type"] not in {"individual", "corporation"}:
        raise ValueError("unsupported business_type")
    eligible = (
        scenario["business_type"] == "individual"
        and scenario["consumer_facing_business"]
        and prior_supply <= 1_000_000_000
    )
    record(
        "VAT_CREDIT_ELIGIBILITY",
        {
            "business_type": scenario["business_type"],
            "prior_year_site_supply_base": prior_supply,
            "consumer_facing_business": scenario["consumer_facing_business"],
        },
        eligible,
    )
    if prior_credit > 10_000_000:
        raise ValueError("prior receipt credit exceeds the annual limit")
    raw_credit = receipt_base * 13 // 1000 if eligible else 0
    record(
        "VAT_CREDIT_RATE_2026",
        {
            "eligible_gross": receipt_base,
            "eligible": eligible,
            "rate_numerator": 13,
            "rate_denominator": 1000,
        },
        raw_credit,
    )
    annual_credit = min(raw_credit, 10_000_000 - prior_credit)
    record(
        "VAT_CREDIT_ANNUAL_LIMIT",
        {"raw_credit": raw_credit, "already_claimed": prior_credit, "annual_limit": 10_000_000},
        annual_credit,
    )
    liability = output_vat - deductible
    credit = min(annual_credit, max(liability, 0))
    record(
        "VAT_CREDIT_PAYABLE_LIMIT",
        {"annual_credit": annual_credit, "liability_before_credit": liability},
        credit,
    )
    prepaid = _money(scenario["prepaid_assessed_vat"], "prepaid_assessed_vat")
    if prepaid and (prepaid < 500_000 or prepaid % 1000):
        raise ValueError("Assessed VAT notice must be at least 500000 and a multiple of 1000")
    prior_declared = _money(scenario.get("prior_declared_vat_paid", 0), "prior_declared_vat_paid")
    if prepaid and (prior_credit or prior_declared):
        raise ValueError("Prior return and current assessed notice cannot both be claimed")
    record(
        "VAT_ASSESSMENT_VALIDITY",
        {
            "assessed_notice": prepaid,
            "prior_declared_vat_paid": prior_declared,
            "minimum_notice": 500_000,
        },
        {"assessment_is_consistent": True, "prior_return_payment_deducted_again": False},
    )
    net = liability - credit - prepaid
    record(
        "VAT_PREPAID",
        {"liability_after_credit": liability - credit, "prepaid_assessed_vat": prepaid},
        net,
    )
    gold = {
        "tax_base": tax_base,
        "output_vat": output_vat,
        "input_vat": input_vat,
        "noncreditable_vat": noncreditable,
        "deductible_input_vat": deductible,
        "receipt_credit": credit,
        "prepaid_vat": prepaid,
        "net_vat": net,
        "payable_vat": max(net, 0),
        "refund_vat": max(-net, 0),
        "unique_transaction_count": in_period,
    }
    record(
        "VAT_SETTLEMENT",
        {
            "output_vat": output_vat,
            "deductible_input_vat": deductible,
            "receipt_credit": credit,
            "prepaid_vat": prepaid,
        },
        gold,
    )
    return gold, trace
