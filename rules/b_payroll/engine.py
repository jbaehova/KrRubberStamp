"""Payroll for resident employees in 2026.

Insurance bases are notified facts, not estimates inferred from this month's pay.
The engine excludes bonuses with a multi-month assessment period, year-end insurance
adjustments, subsidies, nonresident exemptions and industrial-accident employer costs.
Minutes and rational arithmetic retain fractional hourly wages until settlement.
"""

from bisect import bisect_right
from datetime import date
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path


RULE_PREFIX = "B."


def floor_ten(value: int | Fraction) -> int:
    value = Fraction(value)
    return (value.numerator // (value.denominator * 10)) * 10


def wage_won(value: int | Fraction) -> int:
    """Synthetic contract: round each aggregated wage item upward to a whole won."""
    value = Fraction(value)
    return -(-value.numerator // value.denominator)


@lru_cache(maxsize=1)
def tax_table() -> dict:
    return json.loads(Path(__file__).with_name("income_tax_table.json").read_text("utf-8"))


def _family_cell(taxes: list[int], family_count: int) -> int:
    if family_count < 1:
        raise ValueError("family_count includes the employee and must be positive")
    if family_count <= 11:
        return taxes[family_count - 1]
    return max(0, taxes[10] - (taxes[9] - taxes[10]) * (family_count - 11))


def withholding_tax(
    taxable_pay: int,
    family_count: int = 1,
    eligible_children: int = 0,
    payment_date: str = "2026-10-25",
    withholding_percent: int = 100,
) -> tuple[int, dict]:
    """Read the official 646 rows; use annex formulas only above KRW 10 million.

    The 2026 March child credit is separate from the unchanged family/wage table.
    Elections and final assessment are truncated below ten won as in NTS examples.
    """
    paid = date.fromisoformat(payment_date)
    if paid.year != 2026:
        raise ValueError("this engine supports 2026 payment dates only")
    if taxable_pay < 0 or not 0 <= eligible_children < family_count:
        raise ValueError("invalid taxable pay or child/family count")
    if withholding_percent not in (80, 100, 120):
        raise ValueError("withholding_percent must be 80, 100, or 120")
    table = tax_table()
    if taxable_pay < 770000:
        base_tax, interval = Fraction(0), [0, 770000]
    elif taxable_pay < 10000000:
        rows = table["rows"]
        row = rows[bisect_right([r[0] for r in rows], taxable_pay) - 1]
        base_tax, interval = Fraction(_family_cell(row[2:], family_count)), row[:2]
    else:
        baseline = _family_cell(table["at_ten_million"], family_count)
        if taxable_pay == 10000000:
            extra = Fraction(0)
            interval = [10000000, 10000000]
        elif taxable_pay <= 14000000:
            extra = 25000 + Fraction((taxable_pay - 10000000) * 343, 1000)
            interval = [10000000, 14000000]
        elif taxable_pay <= 28000000:
            extra = 1397000 + Fraction((taxable_pay - 14000000) * 3724, 10000)
            interval = [14000000, 28000000]
        elif taxable_pay <= 30000000:
            extra = 6610600 + Fraction((taxable_pay - 28000000) * 392, 1000)
            interval = [28000000, 30000000]
        elif taxable_pay <= 45000000:
            extra = 7394600 + Fraction((taxable_pay - 30000000) * 40, 100)
            interval = [30000000, 45000000]
        elif taxable_pay <= 87000000:
            extra = 13394600 + Fraction((taxable_pay - 45000000) * 42, 100)
            interval = [45000000, 87000000]
        else:
            extra = 31034600 + Fraction((taxable_pay - 87000000) * 45, 100)
            interval = [87000000, None]
        base_tax = baseline + extra
    if eligible_children == 0:
        child_credit = 0
    elif paid >= date(2026, 3, 1):
        child_credit = (
            20830 if eligible_children == 1 else 45830 + max(0, eligible_children - 2) * 33330
        )
    else:
        child_credit = (
            12500 if eligible_children == 1 else 29160 + max(0, eligible_children - 2) * 25000
        )
    provisional_tax = floor_ten(
        max(Fraction(0), base_tax - child_credit) * withholding_percent / 100
    )
    # Income Tax Act article 86: waive withholding below KRW 1,000 per payment.
    tax = 0 if provisional_tax < 1000 else provisional_tax
    return tax, {
        "table_interval_won": interval,
        "table_tax_before_children_floor_won": int(base_tax),
        "family_count": family_count,
        "eligible_children": eligible_children,
        "child_credit": child_credit,
        "withholding_percent": withholding_percent,
        "payment_date": payment_date,
        "before_small_tax_waiver": provisional_tax,
        "small_tax_waiver_below_won": 1000,
        "source_table_sha256": table["source_sha256"],
    }


def pension_employee(base_income: int, month: int, due: bool = True) -> tuple[int, int]:
    """NPS notified income, thousand-won truncation, half-year bounds and 4.75%."""
    if base_income < 0 or not 1 <= month <= 12:
        raise ValueError("invalid pension basis or month")
    low, high = (400000, 6370000) if month <= 6 else (410000, 6590000)
    bounded = min(high, max(low, (base_income // 1000) * 1000))
    return (floor_ten(Fraction(bounded * 475, 10000)) if due else 0), bounded


def health_employee(base_income: int, due: bool = True) -> int:
    if base_income < 0:
        raise ValueError("invalid health basis")
    if not due:
        return 0
    # Whole 2026 보수월액보험료 bounds 20,160 / 9,183,480, split 50%.
    return min(4591740, max(10080, floor_ten(Fraction(base_income * 719, 20000))))


def calculate(scenario: dict) -> tuple[dict, list[dict]]:
    """Return whole-won wage fields, the effective date and rule-ID traces."""
    paid = date.fromisoformat(scenario["payment_date"])
    if paid.year != 2026:
        raise ValueError("this engine supports 2026 only")
    assessment_month = scenario.get("insurance_assessment_month")
    if not isinstance(assessment_month, str) or len(assessment_month) != 7:
        raise ValueError("insurance_assessment_month must be a 2026 YYYY-MM month")
    assessment = date.fromisoformat(assessment_month + "-01")
    if assessment.year != 2026 or assessment.isoformat()[:7] != assessment_month:
        raise ValueError("insurance_assessment_month must be a 2026 YYYY-MM month")
    trace = []

    def record(rule_id: str, inputs: dict, output: dict | int) -> None:
        trace.append({"rule_id": f"{RULE_PREFIX}{rule_id}", "inputs": inputs, "output": output})

    monthly_salary = scenario["base_salary"]
    fixed = scenario["fixed_allowance"]
    meals = scenario["meal_allowance"]
    variable = scenario["variable_allowance"]
    if any(x < 0 for x in (monthly_salary, fixed, meals, variable)):
        raise ValueError("wages must be nonnegative")
    ordinary_monthly = monthly_salary + fixed + meals
    paid_holiday_minutes = scenario.get("paid_holiday_minutes", 0)
    if type(paid_holiday_minutes) is not int or paid_holiday_minutes < 0:
        raise ValueError("paid_holiday_minutes must be nonnegative whole minutes")
    if scenario["pay_basis"] == "monthly":
        if paid_holiday_minutes:
            raise ValueError("Monthly salary already includes paid holiday wages")
        divisor = scenario["monthly_divisor_hours"]
        if divisor <= 0 or not scenario["weekly_holiday_included"]:
            raise ValueError("monthly scenario requires a positive divisor and included weekly pay")
        hourly = Fraction(ordinary_monthly, divisor)
        base_pay = monthly_salary
    elif scenario["pay_basis"] == "hourly":
        if ordinary_monthly or scenario["weekly_holiday_included"]:
            raise ValueError(
                "hourly scenario requires separate weekly pay and no monthly allowances"
            )
        hourly = Fraction(scenario["hourly_rate"])
        base_pay = wage_won(hourly * scenario["regular_minutes"] / 60)
    else:
        raise ValueError("pay_basis must be monthly or hourly")
    record(
        "ORDINARY",
        {
            "pay_basis": scenario["pay_basis"],
            "base_salary": monthly_salary,
            "fixed_allowance": fixed,
            "meal_allowance": meals,
            "monthly_divisor_hours": scenario["monthly_divisor_hours"],
            "hourly_rate": scenario["hourly_rate"],
            "regular_minutes": scenario["regular_minutes"],
        },
        {
            "ordinary_monthly_wage": ordinary_monthly,
            "hourly_exact_numerator": hourly.numerator,
            "hourly_exact_denominator": hourly.denominator,
        },
    )
    paid_holiday_pay = wage_won(hourly * paid_holiday_minutes / 60)
    if "paid_holiday_minutes" in scenario:
        record(
            "PAID_HOLIDAY",
            {"paid_holiday_minutes": paid_holiday_minutes, "pay_basis": scenario["pay_basis"]},
            paid_holiday_pay,
        )

    premium_applies = scenario["workplace_employee_count"] >= 5
    overtime_minutes = scenario["overtime_minutes"]
    night_minutes = scenario["night_minutes"]
    holiday_shifts = scenario["holiday_shifts"]
    if min(overtime_minutes, night_minutes, scenario["regular_minutes"]) < 0:
        raise ValueError("work minutes must be nonnegative")
    if any(
        s["minutes"] < 0 or not 0 <= s["holiday_night_minutes"] <= s["minutes"]
        for s in holiday_shifts
    ):
        raise ValueError("invalid holiday shift")
    if sum(s["holiday_night_minutes"] for s in holiday_shifts) > night_minutes:
        raise ValueError("night total must include holiday/night overlap")
    overtime = wage_won(hourly * overtime_minutes / 60 * (Fraction(3, 2) if premium_applies else 1))
    night = wage_won(hourly * night_minutes / 120) if premium_applies else 0
    holiday_exact = sum(
        (
            hourly
            * (
                Fraction(min(s["minutes"], 480) * 3, 120)
                + Fraction(max(0, s["minutes"] - 480) * 2, 60)
            )
            if premium_applies
            else hourly * s["minutes"] / 60
        )
        for s in holiday_shifts
    )
    holiday = wage_won(holiday_exact)
    record(
        "OVERTIME",
        {
            "overtime_minutes_excluding_holiday": overtime_minutes,
            "premium_applies": premium_applies,
        },
        overtime,
    )
    record(
        "NIGHT",
        {"night_minutes_including_overlap": night_minutes, "premium_applies": premium_applies},
        night,
    )
    record(
        "HOLIDAY", {"holiday_shifts": holiday_shifts, "premium_applies": premium_applies}, holiday
    )

    weekly_hours = scenario["weekly_hours"]
    if not 0 <= weekly_hours <= 40 or scenario["qualifying_weeks"] < 0:
        raise ValueError("invalid weekly hours or eligible weeks")
    weekly_entitlement = (
        wage_won(hourly * Fraction(weekly_hours, 5) * scenario["qualifying_weeks"])
        if weekly_hours >= 15
        else 0
    )
    weekly_pay = 0 if scenario["weekly_holiday_included"] else weekly_entitlement
    record(
        "WEEKLY",
        {
            "weekly_hours": weekly_hours,
            "qualifying_weeks": scenario["qualifying_weeks"],
            "already_included": scenario["weekly_holiday_included"],
        },
        {"weekly_holiday_entitlement": weekly_entitlement, "weekly_holiday_pay": weekly_pay},
    )

    exempt_meals = 0 if scenario["employer_provides_meals"] else min(200000, meals)
    gross = (
        base_pay
        + fixed
        + meals
        + variable
        + overtime
        + night
        + holiday
        + weekly_pay
        + paid_holiday_pay
    )
    taxable = gross - exempt_meals
    record(
        "MEAL_EXEMPT",
        {"meal_allowance": meals, "employer_provides_meals": scenario["employer_provides_meals"]},
        exempt_meals,
    )
    record(
        "GROSS",
        {
            "base_pay": base_pay,
            "fixed_allowance": fixed,
            "meal_allowance": meals,
            "variable_allowance": variable,
            "overtime_pay": overtime,
            "night_pay": night,
            "holiday_pay": holiday,
            "weekly_holiday_pay": weekly_pay,
            "paid_holiday_pay": paid_holiday_pay,
        },
        {"gross_pay": gross, "taxable_pay": taxable},
    )

    pension, bounded = pension_employee(
        scenario["pension_notified_income"], assessment.month, scenario["pension_due"]
    )
    record(
        "PENSION",
        {
            "notified_income": scenario["pension_notified_income"],
            "insurance_assessment_month": assessment_month,
            "month": assessment.month,
            "due": scenario["pension_due"],
            "employee_rate": "0.0475",
        },
        {"pension_base_income": bounded, "national_pension": pension},
    )
    health = health_employee(scenario["health_notified_income"], scenario["health_due"])
    record(
        "HEALTH",
        {
            "notified_income": scenario["health_notified_income"],
            "due": scenario["health_due"],
            "employee_rate": "0.03595",
        },
        health,
    )
    care = floor_ten(Fraction(health * 9448, 71900))
    record("LONG_TERM_CARE", {"health_premium": health, "ratio": "0.9448 / 7.19"}, care)
    employment_base = scenario["employment_notified_income"]
    if employment_base < 0:
        raise ValueError("invalid employment basis")
    employment = floor_ten(Fraction(employment_base * 9, 1000)) if scenario["employment_due"] else 0
    record(
        "EMPLOYMENT",
        {
            "notified_income": employment_base,
            "due": scenario["employment_due"],
            "employee_rate": "0.009",
        },
        employment,
    )
    income_tax, tax_details = withholding_tax(
        taxable,
        scenario["family_count"],
        scenario["eligible_children"],
        scenario["payment_date"],
        scenario["withholding_percent"],
    )
    record(
        "TAX_TABLE",
        {
            "taxable_pay": taxable,
            "family_count": scenario["family_count"],
            "table_interval_won": tax_details["table_interval_won"],
            "source_table_sha256": tax_details["source_table_sha256"],
        },
        tax_details["table_tax_before_children_floor_won"],
    )
    record(
        "CHILD_CREDIT",
        {
            "payment_date": scenario["payment_date"],
            "eligible_children": scenario["eligible_children"],
        },
        tax_details["child_credit"],
    )
    record("WITHHOLDING", {"taxable_pay": taxable, **tax_details}, income_tax)
    local_tax = floor_ten(Fraction(income_tax, 10))
    record("LOCAL_TAX", {"income_tax": income_tax, "rate": "0.1"}, local_tax)
    deductions = pension + health + care + employment + income_tax + local_tax
    if deductions > gross:
        raise ValueError("deductions exceed pay: unsupported arrears/low-pay scenario")
    record("NET", {"gross_pay": gross, "deductions": deductions}, gross - deductions)
    gold = {
        "effective_payment_date": paid.isoformat(),
        "ordinary_monthly_wage": ordinary_monthly,
        "ordinary_hourly_wage_floor": int(hourly),
        "base_pay": base_pay,
        "fixed_allowance": fixed,
        "meal_allowance": meals,
        "variable_allowance": variable,
        "overtime_pay": overtime,
        "night_pay": night,
        "holiday_pay": holiday,
        "weekly_holiday_pay": weekly_pay,
        "paid_holiday_pay": paid_holiday_pay,
        "gross_pay": gross,
        "taxable_pay": taxable,
        "non_taxable_pay": exempt_meals,
        "pension_base_income": bounded,
        "national_pension": pension,
        "health_insurance": health,
        "long_term_care": care,
        "employment_insurance": employment,
        "income_tax": income_tax,
        "local_income_tax": local_tax,
        "total_deductions": deductions,
        "net_pay": gross - deductions,
    }
    return gold, trace
