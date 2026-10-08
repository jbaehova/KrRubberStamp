"""Exact, integer-won 2025 Korean employment-income tax calculation.

The supported case is a resident with employment income only, no tax reductions,
no prior-year carryovers and no foreign tax. Expense ownership, claimant and
employment dates are evidence, rather than an assumed eligibility flag.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy


def salary_deduction(salary: int) -> int:
    if salary <= 5_000_000:
        value = salary * 70 // 100
    elif salary <= 15_000_000:
        value = 3_500_000 + (salary - 5_000_000) * 40 // 100
    elif salary <= 45_000_000:
        value = 7_500_000 + (salary - 15_000_000) * 15 // 100
    elif salary <= 100_000_000:
        value = 12_000_000 + (salary - 45_000_000) * 5 // 100
    else:
        value = 14_750_000 + (salary - 100_000_000) * 2 // 100
    return min(value, 20_000_000)


def national_tax(tax_base: int) -> int:
    """2023-2025 progressive table, with fractional won discarded."""
    for ceiling, percentage, progressive_offset in (
        (14_000_000, 6, 0),
        (50_000_000, 15, 1_260_000),
        (88_000_000, 24, 5_760_000),
        (150_000_000, 35, 15_440_000),
        (300_000_000, 38, 19_940_000),
        (500_000_000, 40, 25_940_000),
        (1_000_000_000, 42, 35_940_000),
        (10**30, 45, 65_940_000),
    ):
        if tax_base <= ceiling:
            return max(0, tax_base * percentage // 100 - progressive_offset)
    raise AssertionError("unreachable")


def employment_credit(salary: int, computed_tax: int) -> int:
    raw = (
        computed_tax * 55 // 100
        if computed_tax <= 1_300_000
        else 715_000 + (computed_tax - 1_300_000) * 30 // 100
    )
    if salary <= 33_000_000:
        cap = 740_000
    elif salary <= 70_000_000:
        cap = max(660_000, 740_000 - (salary - 33_000_000) * 8 // 1000)
    elif salary <= 120_000_000:
        cap = max(500_000, 660_000 - (salary - 70_000_000) // 2)
    else:
        cap = max(200_000, 500_000 - (salary - 120_000_000) // 2)
    return min(raw, cap)


def child_credit(count: int) -> int:
    if count <= 0:
        return 0
    if count == 1:
        return 250_000
    return 550_000 + max(0, count - 2) * 400_000


def birth_credit(order: int) -> int:
    return 0 if order <= 0 else 300_000 if order == 1 else 500_000 if order == 2 else 700_000


def income_eligible(person: dict) -> bool:
    return (
        person.get("income_amount", 0) <= 1_000_000
        or person.get("earned_income_only", False)
        and person.get("gross_salary", 0) <= 5_000_000
    )


def basic_eligible(person: dict) -> bool:
    if not person.get("supported", False) or person.get("assigned_claimant") != "self":
        return False
    if not income_eligible(person):
        return False
    relation, age = person["relation"], person["age"]
    if person.get("disabled", False) or relation == "spouse":
        return True
    if relation in {"child", "grandchild"}:
        return age <= 20
    if relation == "parent":
        return age >= 60
    if relation == "sibling":
        return age <= 20 or age >= 60
    return False


def credit_card_deduction(salary: int, buckets: dict[str, int]) -> int:
    """Exclusive spending buckets; threshold consumes 15%, then 30%, then 40%."""
    # Keep quarter-won thresholds exact until the final integer deduction.
    threshold_quarters = salary
    rates = (("credit", 15), ("debit", 30), ("culture", 30), ("market", 40), ("transit", 40))
    raw_hundredths_quarters = 0
    for kind, rate in rates:
        amount_quarters = buckets.get(kind, 0) * 4
        used = min(amount_quarters, threshold_quarters)
        threshold_quarters -= used
        raw_hundredths_quarters += (amount_quarters - used) * rate
    raw = raw_hundredths_quarters // 400
    basic_cap = 3_000_000 if salary <= 70_000_000 else 2_500_000
    extra_cap = 3_000_000 if salary <= 70_000_000 else 2_000_000
    additional_base = (
        (buckets.get("market", 0) + buckets.get("transit", 0)) * 40
        + (buckets.get("culture", 0) * 30 if salary <= 70_000_000 else 0)
    ) // 100
    return min(raw, basic_cap) + min(max(raw - basic_cap, 0), extra_cap, additional_base)


def _in_employment(row: dict, scenario: dict) -> bool:
    return scenario["employment_start"] <= row["date"] <= scenario["employment_end"]


def _owner_ok(person: dict, *, income: bool = True) -> bool:
    return (
        person.get("relation") == "self"
        or person.get("supported", False)
        and person.get("assigned_claimant") == "self"
        and (not income or income_eligible(person))
    )


def _special_credits(s: dict, people: dict, salary: int, income: int) -> dict:
    ordinary_insurance = disabled_insurance = 0
    for row in s.get("insurance", []):
        person = people[row["person_id"]]
        if not _in_employment(row, s) or not row.get("paid_by_self", True):
            continue
        if person["relation"] != "self" and not basic_eligible(person):
            continue
        if row["kind"] == "general":
            ordinary_insurance += row["amount"]
        elif row["kind"] == "disabled" and person.get("disabled", False):
            disabled_insurance += row["amount"]
    insurance = min(ordinary_insurance, 1_000_000) * 12 // 100
    insurance += min(disabled_insurance, 1_000_000) * 15 // 100

    medical = defaultdict(int)
    glasses_by_person = defaultdict(int)
    postpartum_by_birth = defaultdict(int)
    for row in s.get("medical", []):
        person = people[row["person_id"]]
        if not _in_employment(row, s) or not _owner_ok(person, income=False):
            continue
        if not row.get("paid_by_self", True) or row.get("excluded", False):
            continue
        amount = max(0, row["amount"] - row.get("reimbursed", 0))
        kind = row["kind"]
        if kind == "glasses":
            amount = min(amount, max(0, 500_000 - glasses_by_person[row["person_id"]]))
            glasses_by_person[row["person_id"]] += amount
            kind = "ordinary"
        elif kind == "postpartum":
            birth = row["birth_event"]
            amount = min(amount, max(0, 2_000_000 - postpartum_by_birth[birth]))
            postpartum_by_birth[birth] += amount
            kind = "ordinary"
        if kind == "ordinary":
            uncapped = (
                person["relation"] == "self"
                or person["age"] <= 6
                or person["age"] >= 65
                or person.get("disabled", False)
                or person.get("special_medical", False)
            )
            kind = "uncapped" if uncapped else "ordinary"
        if kind not in {"ordinary", "uncapped", "premature", "infertility"}:
            raise ValueError(f"unsupported medical expense: {kind}")
        medical[kind] += amount
    threshold_hundredths = salary * 3
    medical_numerator = 0
    for kind, rate in (("ordinary", 15), ("uncapped", 15), ("premature", 20), ("infertility", 30)):
        amount_hundredths = medical[kind] * 100
        used = min(amount_hundredths, threshold_hundredths)
        threshold_hundredths -= used
        eligible_hundredths = amount_hundredths - used
        if kind == "ordinary":
            eligible_hundredths = min(eligible_hundredths, 7_000_000 * 100)
        medical_numerator += eligible_hundredths * rate
    medical_credit = medical_numerator // 10_000

    education_by_person = defaultdict(int)
    education_levels = {}
    for row in s.get("education", []):
        person = people[row["person_id"]]
        if not _in_employment(row, s) or not row.get("paid_by_self", True):
            continue
        if not _owner_ok(person) or person["relation"] == "parent":
            if not (
                row["level"] == "special_disabled"
                and _owner_ok(person, income=False)
                and person.get("disabled", False)
            ):
                continue
        if row.get("excluded", False):
            continue
        if person["relation"] != "self" and row["level"] == "graduate":
            continue
        education_by_person[row["person_id"]] += max(0, row["amount"] - row.get("scholarship", 0))
        education_levels[row["person_id"]] = row["level"]
    education_base = 0
    for person_id, amount in education_by_person.items():
        if (
            people[person_id]["relation"] == "self"
            or education_levels[person_id] == "special_disabled"
        ):
            education_base += amount
        else:
            cap = 9_000_000 if education_levels[person_id] == "university" else 3_000_000
            education_base += min(amount, cap)

    donation = defaultdict(int)
    political = hometown = 0
    for row in s.get("donations", []):
        person = people[row["person_id"]]
        if not _owner_ok(person) or not row.get("eligible_organization", True):
            continue
        if row["kind"] == "political":
            if person["relation"] == "self":
                political += row["amount"]
            continue
        if row["kind"] == "hometown":
            if row.get("special_disaster", False):
                raise ValueError("special disaster hometown donations are outside Batch 1 scope")
            if person["relation"] == "self":
                hometown += row["amount"]
            continue
        if row["kind"] not in {"statutory", "public", "religious"}:
            raise ValueError("employee stock and carryover donations are outside Batch 1 scope")
        donation[row["kind"]] += row["amount"]
    political = min(income, political)
    political_credit = min(political, 100_000) * 100 // 110
    political_credit += min(max(0, political - 100_000), 29_900_000) * 15 // 100
    political_credit += max(0, political - 30_000_000) * 25 // 100
    hometown = min(20_000_000, hometown, max(0, income - political))
    hometown_credit = min(hometown, 100_000) * 100 // 110
    hometown_credit += max(0, hometown - 100_000) * 15 // 100
    statutory = min(max(0, income - political - hometown), donation["statutory"])
    remaining = max(0, income - political - hometown - statutory)
    if donation["religious"]:
        public_cap = remaining * 10 // 100 + min(remaining * 20 // 100, donation["public"])
    else:
        public_cap = remaining * 30 // 100
    public_total = min(public_cap, donation["public"] + donation["religious"])
    donation_base = statutory + public_total
    donation_credit = min(donation_base, 10_000_000) * 15 // 100
    donation_credit += max(0, donation_base - 10_000_000) * 30 // 100

    rent = s.get("rent", {})
    rent_ok = (
        salary <= 80_000_000
        and rent.get("homeless_household", False)
        and (rent.get("household_head", False) or not rent.get("head_claims_housing", True))
        and rent.get("address_matches", False)
        and rent.get("eligible_contract_holder", False)
        and (rent.get("area_sqm", 999) <= 85 or rent.get("standard_value", 10**12) <= 400_000_000)
    )
    eligible_rent = (
        min(
            10_000_000,
            sum(row["amount"] for row in rent.get("payments", []) if _in_employment(row, s)),
        )
        if rent_ok
        else 0
    )
    rent_credit = eligible_rent * (17 if salary <= 55_000_000 else 15) // 100
    return {
        "insurance_credit": insurance,
        "medical_credit": medical_credit,
        "education_credit": education_base * 15 // 100,
        "donation_credit": donation_credit,
        "political_credit": political_credit,
        "hometown_credit": hometown_credit,
        "rent_credit": rent_credit,
    }


def _housing_deduction(housing: dict) -> int:
    """2025 mortgage-interest caps, for evidence-certified qualifying loans since 2012."""
    if not housing or not housing.get("requirements_met", False):
        return 0
    if housing["borrowed_date"] < "2012-01-01":
        raise ValueError("pre-2012 mortgage transitional choices are outside Batch 1 scope")
    years = housing["term_years"]
    fixed, amortizing = housing["fixed_rate"], housing["non_deferred"]
    if years >= 15:
        cap = (
            20_000_000 if fixed and amortizing else 18_000_000 if fixed or amortizing else 8_000_000
        )
    elif years >= 10 and (fixed or amortizing):
        cap = 6_000_000
    else:
        return 0
    return min(cap, housing["interest_paid"])


def _special_application(s: dict) -> bool:
    """Application facts, including rejected claims, determine standard eligibility."""
    if "special_deductions_requested" in s:
        if type(s["special_deductions_requested"]) is not bool:
            raise ValueError("special_deductions_requested must be a boolean application fact")
        return s["special_deductions_requested"]
    return bool(
        s.get("social_insurance")
        or s.get("housing_mortgage")
        or s.get("insurance")
        or s.get("medical")
        or s.get("education")
        or s.get("rent", {}).get("payments")
        or any(
            row["kind"] in {"statutory", "public", "religious"} for row in s.get("donations", [])
        )
    )


def calculate(scenario: dict) -> tuple[dict, list[dict]]:
    s = deepcopy(scenario)
    if s.get("reference_year", 2025) != 2025:
        raise ValueError("A_yearend only supports 2025")
    salary = s["annual_gross"] - s["non_taxable"]
    if salary < 0:
        raise ValueError("non_taxable cannot exceed annual_gross")
    trace = []

    def record(rule_id, inputs, output):
        trace.append({"rule_id": rule_id, "inputs": inputs, "output": output})

    people = {
        "self": {
            "relation": "self",
            "age": s["employee_age"],
            "disabled": s.get("employee_disabled", False),
        }
    }
    for person in s.get("dependents", []):
        if person["person_id"] in people:
            raise ValueError("person IDs must be unique")
        people[person["person_id"]] = person
    accepted = [p for p in s.get("dependents", []) if basic_eligible(p)]
    rejected = [p["person_id"] for p in s.get("dependents", []) if not basic_eligible(p)]
    basic = (1 + len(accepted)) * 1_500_000
    additional = (
        sum(1_000_000 for p in accepted if p["age"] >= 70)
        + sum(2_000_000 for p in accepted if p.get("disabled", False))
        + (2_000_000 if s.get("employee_disabled", False) else 0)
        + (1_000_000 if s["employee_age"] >= 70 else 0)
    )
    # Widowed/unmarried with a basic-eligible child: single-parent precedes female deduction.
    single_parent = s.get("marital_status", "single") != "married" and any(
        p["relation"] in {"child", "grandchild"} for p in accepted
    )
    income = salary - salary_deduction(salary)
    woman = (
        s.get("employee_sex") == "female"
        and income <= 30_000_000
        and (
            s.get("marital_status") == "married"
            or s.get("household_head", False)
            and bool(accepted)
        )
    )
    additional += 1_000_000 if single_parent else 500_000 if woman else 0
    record(
        "A_PERSONAL",
        {"dependents": s.get("dependents", [])},
        {"basic": basic, "additional": additional, "rejected": rejected},
    )
    record(
        "A_SALARY",
        {"annual_gross": s["annual_gross"], "non_taxable": s["non_taxable"]},
        {
            "total_salary": salary,
            "salary_deduction": salary_deduction(salary),
            "salary_income": income,
        },
    )
    pension = s.get("public_pension_paid", 0)
    record("A_PENSION_DEDUCTION", {"public_pension_paid": pension}, pension)
    special = sum(s.get("social_insurance", {}).values())
    record("A_SPECIAL_DEDUCTION", s.get("social_insurance", {}), special)
    housing = _housing_deduction(s.get("housing_mortgage", {}))
    record("A_HOUSING", s.get("housing_mortgage", {}), housing)

    card_buckets = defaultdict(int)
    for row in s.get("cards", []):
        person = people[row["person_id"]]
        if not _in_employment(row, s) or not _owner_ok(person):
            continue
        if person["relation"] == "sibling" or row.get("excluded", False):
            continue
        kind = row["category"]
        if kind == "culture" and salary > 70_000_000:
            kind = row["payment_method"]
        if kind not in {"credit", "debit", "culture", "market", "transit"}:
            raise ValueError(f"unsupported card category: {kind}")
        card_buckets[kind] += row["amount"]
    cards = credit_card_deduction(salary, card_buckets)
    record("A_CARD", {"salary": salary, "spending": dict(card_buckets)}, cards)
    account = s.get("pension_accounts", {})
    account_base = min(
        9_000_000, min(account.get("pension_savings", 0), 6_000_000) + account.get("irp", 0)
    )
    account_credit = account_base * (15 if salary <= 55_000_000 else 12) // 100
    record("A_PENSION_CREDIT", {"salary": salary, "accounts": account}, account_credit)
    child_count = sum(p["relation"] in {"child", "grandchild"} and p["age"] >= 8 for p in accepted)
    children = child_credit(child_count) + sum(
        birth_credit(p.get("birth_order_this_year", 0))
        for p in accepted
        if p["relation"] == "child"
    )
    record(
        "A_CHILD",
        {
            "eligible_children_age_8_plus": child_count,
            "birth_orders": [p.get("birth_order_this_year", 0) for p in accepted],
        },
        children,
    )
    special_credits = _special_credits(s, people, salary, income)
    for key, value in special_credits.items():
        record(
            "A_" + key.removesuffix("_credit").upper() + "_CREDIT",
            {
                "expenses": s.get(
                    "donations"
                    if key in {"donation_credit", "political_credit", "hometown_credit"}
                    else key.removesuffix("_credit"),
                    {},
                ),
                "salary": salary,
            },
            value,
        )
    requested_special = _special_application(s)
    choice = s.get("deduction_choice", "itemized" if requested_special else "standard")
    if choice not in {"itemized", "standard"}:
        raise ValueError("deduction_choice must be itemized or standard")
    standard = 130_000 if choice == "standard" else 0
    if standard:
        special = 0
        housing = 0
        special_credits = {
            key: value if key in {"political_credit", "hometown_credit"} else 0
            for key, value in special_credits.items()
        }
    deduction_limit_excess = max(0, cards + housing - 25_000_000)
    tax_base = max(
        0,
        income - basic - additional - pension - special - housing - cards + deduction_limit_excess,
    )
    computed = national_tax(tax_base)
    earned_credit = employment_credit(salary, computed)
    credits = earned_credit + children + account_credit + sum(special_credits.values()) + standard
    final_raw = max(0, computed - credits)
    # NTS 2025 worked receipt keeps won in final-minus-paid settlement fields.
    final_national = final_raw
    final_local = final_national // 10
    paid_national = s.get("paid_national_tax", 0)
    paid_local = s.get("paid_local_tax", 0)
    settlement_national = final_national - paid_national
    settlement_local = final_local - paid_local
    gold = {
        "total_salary": salary,
        "salary_deduction": salary_deduction(salary),
        "salary_income": income,
        "eligible_dependents": len(accepted),
        "basic_deduction": basic,
        "additional_deduction": additional,
        "pension_deduction": pension,
        "special_income_deduction": special,
        "housing_income_deduction": housing,
        "income_deduction_limit_excess": deduction_limit_excess,
        "credit_card_deduction": cards,
        "tax_base": tax_base,
        "computed_tax": computed,
        "employment_credit": earned_credit,
        "child_credit": children,
        "pension_account_credit": account_credit,
        **special_credits,
        "standard_credit": standard,
        "total_tax_credits": credits,
        "final_national_tax": final_national,
        "final_local_tax": final_local,
        "paid_national_tax": paid_national,
        "paid_local_tax": paid_local,
        "settlement_national_tax": settlement_national,
        "settlement_local_tax": settlement_local,
        "settlement_total": settlement_national + settlement_local,
    }
    record("A_TAX_BRACKETS", {"tax_base": tax_base}, computed)
    record("A_EMPLOYMENT_CREDIT", {"salary": salary, "computed_tax": computed}, earned_credit)
    record(
        "A_STANDARD",
        {"deduction_choice": choice, "special_deductions_requested": requested_special},
        {
            "standard_credit": standard,
            "special_income_deduction_applied": special,
            "housing_deduction_applied": housing,
            "special_credits_applied": special_credits,
        },
    )
    record("A_FINAL", {"computed_tax": computed, "total_tax_credits": credits}, final_national)
    record("A_LOCAL", {"final_national_tax": final_national}, final_local)
    record(
        "A_SETTLEMENT",
        {
            "final_national": final_national,
            "final_local": final_local,
            "paid_national": paid_national,
            "paid_local": paid_local,
        },
        {
            "national": settlement_national,
            "local": settlement_local,
            "total": settlement_national + settlement_local,
        },
    )
    return gold, trace
