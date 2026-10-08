"""Deterministic, explicit-fact payroll scenarios for the 2026 benchmark."""

import calendar
import hashlib
import random

from rules.b_payroll.engine import calculate, tax_table


INSTRUCTIONS = [
    "이번 달 급여 마감 부탁드립니다. 계약서와 근태 자료를 보고 지급액과 공제액을 계산해 주세요.",
    "급여 이체 전에 한번 확인해 주세요. 자료에 있는 직원의 수당과 실지급액을 정리해 주시면 됩니다.",
    "첨부한 계약 조건으로 급여명세서 초안을 만들려고 합니다. 지급 항목과 보험료, 세금을 계산해 주세요.",
    "근태 반영해서 이번 달 급여를 확정해 주세요. 통상임금과 수당 계산도 함께 확인 부탁드립니다.",
    "월 급여 검산이 필요합니다. 첨부 자료 기준으로 총지급액부터 실지급액까지 계산해 주세요.",
    "급여 담당자에게 전달할 숫자를 정리해 주세요. 계약상 수당과 근로자 부담 공제액을 확인하면 됩니다.",
    "이번 급여 지급 건을 검토해 주세요. 근태 기록과 수당 규정을 모두 반영해서 답안을 작성해 주세요.",
    "급여 자료를 모아 두었습니다. 해당 직원에게 지급할 금액과 항목별 공제액을 산출해 주세요.",
    "급여 마감표에 넣을 값이 필요합니다. 지급 내역과 4대보험 근로자 부담분을 확인해 주세요.",
    "이번 달 급여 계산을 부탁드려요. 계약 조건과 근태를 적용하고 세후 이체 금액까지 알려 주세요.",
    "경리팀에서 급여명세서를 준비하고 있습니다. 첨부 자료에 따라 수당과 공제 내역을 채워 주세요.",
    "자료에 나온 급여를 다시 계산해 주세요. 통상임금을 기준으로 가산수당을 확인해 주시면 됩니다.",
    "급여 승인 전에 숫자를 맞춰 보려고 합니다. 지급 합계와 보험료, 원천세를 정리해 주세요.",
    "이번 직원 급여를 확인 부탁드립니다. 신고된 보험 기준액과 원천징수 선택 비율을 적용해 주세요.",
    "이체할 급여를 계산해 주세요. 첨부한 근로 조건과 수당 지급 기준을 빠짐없이 반영해 주세요.",
    "월말 급여 정산을 도와주세요. 문서에 적힌 근태와 과세 구분대로 항목별 금액을 구해 주세요.",
    "급여명세서 수치 검토 건입니다. 근로자 부담 보험료와 지방소득세까지 계산해 주세요.",
    "계약서 기준으로 급여를 산출해 주세요. 수당 지급액과 공제 합계를 확인한 뒤 실지급액을 정리해 주세요.",
    "담당자 부재로 급여 검산이 필요합니다. 첨부 문서의 숫자를 적용해 답안 항목을 채워 주세요.",
    "급여 이체 목록을 만들고 있습니다. 직원 한 명의 지급 항목과 원천징수 금액을 계산해 주세요.",
]


LABELS = {
    "employee_name": "가상 직원 표시명",
    "company_name": "가상 사업장 표시명",
    "employee_age": "직원 만 나이",
    "synthetic_id": "가상 급여 자료 식별번호",
    "payment_date": "급여 지급일",
    "effective_payment_date": "실행 또는 최종 승인 기록으로 확정한 실제 급여 지급일",
    "insurance_assessment_month": "공단 통지서의 보험 부과월",
    "pay_basis": "급여 방식(monthly=월급제, hourly=시급제)",
    "base_salary": "월 정액 기본급(원)",
    "fixed_allowance": "정기적 일률적 소정근로 대가인 직무수당(원)",
    "meal_allowance": "정기적 일률적 소정근로 대가인 현금 식대(원)",
    "variable_allowance": "당월 실적 연동 수당(과세, 통상임금 제외, 원)",
    "monthly_divisor_hours": "월급제 통상임금 산정 기준 시간(시간)",
    "hourly_rate": "시급제 계약 시급(원)",
    "regular_minutes": "근태상 정규 유급 근로시간(분)",
    "weekly_hours": "4주 평균 1주 소정근로시간(시간)",
    "qualifying_weeks": "소정근로일 개근 및 주휴 요건 충족 주수(주)",
    "weekly_holiday_included": "정액 월급에 주휴수당 이미 포함 여부",
    "workplace_employee_count": "사업장 상시 근로자수(명)",
    "overtime_minutes": "평일 연장근로(휴일근로 제외, 휴게 제외, 분)",
    "night_minutes": "22시부터 06시까지 야간근로 합계(연장 및 휴일 중복 포함, 분)",
    "holiday_shifts": "별도 실제 법정 유급휴일 근로 기록(기본급에 미포함)",
    "minutes": "해당 휴일 실제 근로시간(휴게 제외, 분)",
    "holiday_night_minutes": "해당 휴일의 야간근로시간(월 야간 합계에 이미 포함, 분)",
    "employer_provides_meals": "사업장에서 식사 또는 음식물 별도 제공 여부",
    "pension_notified_income": "공단이 통지한 국민연금 월 기준소득 신고액(상하한 적용 전, 원)",
    "health_notified_income": "당월 건강보험 고지 보수월액(정산분 없음, 원)",
    "employment_notified_income": "당월 고용보험 고지 월평균보수(정산분 없음, 원)",
    "pension_due": "당월 국민연금 사업장가입 보험료 부과 대상 여부",
    "health_due": "당월 건강보험 직장가입 보험료 부과 대상 여부",
    "employment_due": "당월 실업급여 보험료 부과 대상 여부",
    "family_count": "간이세액표 공제대상 가족수(본인 포함, 명)",
    "eligible_children": "기본공제 대상 중 만 8세부터 20세까지 자녀수(명)",
    "withholding_percent": "신청된 간이세액표 원천징수 비율(%)",
    "contract_scope": "계약과 보험 부과 전제",
    "settlement_policy": "지급 및 공제의 단수 처리 약정",
    "attendance_scope": "근태 집계 범위와 중복 처리 지침",
    "exceptions": "확인해야 할 예외 사항",
    "withholding_reference": "공식 근로소득 간이세액표 발췌(비과세 제외 월급여, 원)",
    "law_reference": "원문 법정 계산 기준",
    "source_url": "공식 원문 주소",
    "effective_period": "적용 기간",
    "wage_from_won": "월급여 하한(이상, 원)",
    "wage_below_won": "월급여 상한(미만, 원)",
    "table_rows": "공식 표 인접 행",
    "tax_at_ten_million": "월급여 정확히 1000만원인 행의 가족수별 소득세",
    "high_income_formulas": "월급여 1000만원 초과 공식 산식",
    "formula": "공식 산식(금액 단위 원)",
    "children_credit_january_february": "1월과 2월 지급분 자녀 공제 기준",
    "children_credit_march_december": "3월부터 12월 지급분 자녀 공제 기준",
    "ordinary_rule": "통상임금과 수당 계산 기준",
    "weekly_rule": "주휴수당 계산 기준",
    "meal_rule": "식대 비과세 기준",
    "pension_rule": "국민연금 요율 및 시기별 상하한",
    "health_rule": "건강보험 요율 및 보험료 상하한",
    "care_rule": "장기요양보험 정확한 계산 비율",
    "employment_rule": "고용보험 근로자 부담 요율",
    "tax_rounding_rule": "세금 단수 처리 및 소액 부징수",
    "local_tax_rule": "지방소득세 계산 기준",
    "ordinary_monthly_wage": "월 통상임금(원)",
    "ordinary_hourly_wage_floor": "통상시급 표시액(원 미만 버림, 수당 계산은 원래 분수 유지)",
    "base_pay": "기본급 지급액(원)",
    "overtime_pay": "연장수당(실제 근로 대가와 가산분 합계, 원)",
    "night_pay": "야간 가산분만 별도 지급(원)",
    "holiday_pay": "휴일수당(실제 근로 대가와 가산분 합계, 원)",
    "weekly_holiday_pay": "정액급여 외 추가 주휴수당(원)",
    "gross_pay": "총지급액(원)",
    "taxable_pay": "원천징수용 과세 월 급여액(원)",
    "non_taxable_pay": "비과세 지급액(원)",
    "pension_base_income": "상하한과 천원 단수를 반영한 국민연금 기준소득월액(원)",
    "national_pension": "국민연금 근로자 부담액(원)",
    "health_insurance": "건강보험 근로자 부담액(원)",
    "long_term_care": "장기요양보험 근로자 부담액(원)",
    "employment_insurance": "고용보험 근로자 부담액(원)",
    "income_tax": "원천징수 소득세(원)",
    "local_income_tax": "특별징수 지방소득세(원)",
    "total_deductions": "공제 합계(원)",
    "net_pay": "실지급액(원)",
}
LABELS.update({f"family_tax_{i}": f"본인 포함 가족 {i}명 표 세액(원)" for i in range(1, 12)})


def _table_row(values: list[int]) -> dict:
    return {
        "wage_from_won": values[0],
        "wage_below_won": values[1],
        **{f"family_tax_{i}": values[i + 1] for i in range(1, 12)},
    }


def _add_rule_evidence(scenario: dict) -> None:
    """Provide published input evidence, not this employee's final computed tax."""
    table = tax_table()
    taxable = calculate(scenario)[0]["taxable_pay"]
    rows = table["rows"]
    index = next((i for i, r in enumerate(rows) if r[0] <= taxable < r[1]), None)
    if index is None:
        excerpt = rows[:2] if taxable < 770000 else rows[-2:]
    else:
        excerpt = rows[max(0, index - 1) : min(len(rows), index + 2)]
    scenario["withholding_reference"] = {
        "source_url": table["source"],
        "effective_period": "원문 별표 개정 2026-02-27. 가족수별 기본 표 세액은 2023년 표와 동일.",
        "table_rows": [_table_row(r) for r in excerpt],
        "family_count_over_eleven": (
            "소득세법 시행령 별표2 제4호: 공제대상가족이 11명을 초과하면 "
            "11명 표 세액에서 (10명 표 세액 - 11명 표 세액) 곱하기 11명 초과 가족 수를 차감한다. "
            "음수 결과는 0원으로 처리한다."
        ),
        "children_credit_january_february": (
            "8세부터 20세까지 기본공제 자녀 1명 12,500원. "
            "2명 29,160원. 3명 이상 29,160원에 2명 초과 자녀당 25,000원을 가산. "
            "기본 표 세액에서 공제하며 음수는 0원."
        ),
        "children_credit_march_december": (
            "8세부터 20세까지 기본공제 자녀 1명 20,830원. "
            "2명 45,830원. 3명 이상 45,830원에 2명 초과 자녀당 33,330원을 가산. "
            "기본 표 세액에서 공제하며 음수는 0원."
        ),
    }
    if taxable >= 10000000:
        scenario["withholding_reference"].update(
            {
                "tax_at_ten_million": {
                    f"family_tax_{i}": table["at_ten_million"][i - 1] for i in range(1, 12)
                },
                "high_income_formulas": [
                    {
                        "formula": "1000만원 초과 1400만원 이하: 1000만원 해당 가족세액 + 25,000 + (월급여-10,000,000)*98%*35%"
                    },
                    {
                        "formula": "1400만원 초과 2800만원 이하: 1000만원 해당 가족세액 + 1,397,000 + (월급여-14,000,000)*98%*38%"
                    },
                    {
                        "formula": "2800만원 초과 3000만원 이하: 1000만원 해당 가족세액 + 6,610,600 + (월급여-28,000,000)*98%*40%"
                    },
                    {
                        "formula": "3000만원 초과 4500만원 이하: 1000만원 해당 가족세액 + 7,394,600 + (월급여-30,000,000)*40%"
                    },
                    {
                        "formula": "4500만원 초과 8700만원 이하: 1000만원 해당 가족세액 + 13,394,600 + (월급여-45,000,000)*42%"
                    },
                    {
                        "formula": "8700만원 초과: 1000만원 해당 가족세액 + 31,034,600 + (월급여-87,000,000)*45%"
                    },
                ],
            }
        )
    scenario["law_reference"] = {
        "ordinary_rule": (
            "근로기준법 제56조 및 고용노동부 2025-02-06 통상임금 지침. "
            "월 기본급에 정기적 일률적 소정근로 대가인 직무수당과 식대를 더해 통상임금을 산정한다. "
            "5인 이상은 평일 연장 1.5배. 야간 가산분은 0.5배 추가. "
            "휴일 1일 8시간 이내는 1.5배, 초과 시간은 2배이며 연장 가산을 다시 더하지 않는다."
        ),
        "weekly_rule": (
            "근로기준법 제18조 및 제55조. 주 15시간 이상이고 해당 주 소정근로일에 개근한 경우 "
            "주40시간 통상근로자에 비례하여 주휴시간 = 주 소정근로시간/40*8. "
            "월급에 포함된 주휴수당을 추가 지급액에 중복해서 더하지 않는다."
        ),
        "meal_rule": "소득세법 제12조 제3호 러목: 식사를 별도 제공받지 않는 근로자의 월 20만원 이하 식대 비과세.",
        "pension_rule": (
            "국민연금공단 2026 안내: 근로자 4.75%. 신고액의 천원 미만 버림. "
            "공단 보험 부과월 2026-01~06 하한 400,000원, 상한 6,370,000원. "
            "2026-07~12 하한 410,000원, 상한 6,590,000원. 적용 기준소득월액에 요율을 곱한다."
        ),
        "health_rule": (
            "건강보험공단 2026 안내: 보수월액 7.19%의 50%인 근로자 3.595%. "
            "근로자 월 보험료 하한 10,080원, 상한 4,591,740원."
        ),
        "care_rule": "건강보험공단 2026 안내: 근로자 건강보험료 * (0.9448% / 7.19%). 비율의 중간 반올림 없음.",
        "employment_rule": "고용노동부 고용보험 안내: 근로자 실업급여 보험료 = 고지 월평균보수 * 0.9%.",
        "tax_rounding_rule": (
            "소득세법 시행령 제194조의 원천징수 선택 비율은 자녀 공제 후 적용한다. "
            "소득세법 제86조: 한 번의 지급에 대한 원천징수 소득세 1,000원 미만은 징수하지 않는다. "
            "세금은 10원 미만 버림한다."
        ),
        "local_tax_rule": "지방세법 제103조의13: 원천징수 소득세의 10%를 개인지방소득세로 특별징수.",
    }


def generate(seed: int, difficulty: str) -> dict:
    if difficulty not in ("easy", "medium", "hard"):
        raise ValueError("difficulty must be easy, medium, or hard")
    rng = random.Random(seed)
    month = rng.randint(1, 12)
    hourly = rng.randrange(11000, 27501, 100)
    meals = rng.choice([100000, 150000, 200000])
    fixed = rng.choice([0, 100000, 150000, 200000])
    # Choosing an integer ordinary hourly rate is realistic and keeps easy cases accessible.
    monthly = hourly * 209
    weekdays = sum(
        calendar.weekday(2026, month, day) < 5
        for day in range(1, calendar.monthrange(2026, month)[1] + 1)
    )
    families = rng.randint(1, 5)
    child_count = rng.randint(0, min(2, families - 1))
    notified = monthly - meals
    reference = hashlib.sha256(f"KrRubberStamp B_payroll {seed}".encode()).hexdigest()[:12]
    scenario = {
        "synthetic_id": f"가상급여-{reference}",
        "employee_name": f"가상직원-{reference[:8]}",
        "company_name": f"가상사업장-{rng.randrange(10000):04d}",
        "employee_age": rng.randint(26, 57),
        "payment_date": f"2026-{month:02d}-25",
        "insurance_assessment_month": f"2026-{month:02d}",
        "pay_basis": "monthly",
        "base_salary": monthly - meals - fixed,
        "fixed_allowance": fixed,
        "meal_allowance": meals,
        "variable_allowance": 0,
        "monthly_divisor_hours": 209,
        "hourly_rate": 0,
        "regular_minutes": weekdays * 8 * 60,
        "weekly_hours": 40,
        "qualifying_weeks": 4,
        "weekly_holiday_included": True,
        "workplace_employee_count": rng.choice([6, 12, 28, 65, 140]),
        "overtime_minutes": rng.choice([0, 120, 240, 480, 600, 720, 960]),
        "night_minutes": 0,
        "holiday_shifts": [],
        "employer_provides_meals": False,
        "pension_notified_income": notified,
        "health_notified_income": notified,
        "employment_notified_income": notified,
        "pension_due": True,
        "health_due": True,
        "employment_due": True,
        "family_count": families,
        "eligible_children": child_count,
        "withholding_percent": 100,
        "contract_scope": (
            "거주자 계속근로 직원이며 월 60시간 이상 근무한다. "
            "전월부터 동일 사업장 가입 중이다. 보험료 지원 및 정산분은 없다. "
            "별도 상여금과 학자금은 지급하지 않는다. 근로자 부담 산재보험은 없다. "
            "가족수는 소득 및 연령 요건을 충족하여 승인된 기본공제 대상자 수다. "
            "시급제에는 월 정액 통상임금이 없으므로 월 통상임금 답안은 0원으로 표시한다."
        ),
        "settlement_policy": (
            "통상시급은 원래 분수를 유지하며 답안 표시액만 원 미만 버림한다. "
            "지급수당은 항목별로 월 합산한 뒤 원 미만을 올림한다. "
            "보험 근로자 부담액과 소득세 및 지방소득세는 항목별 10원 미만을 버림한다."
        ),
        "attendance_scope": (
            "정규 근로분의 임금은 기본급에 포함된다. 평일 연장 분에는 휴일 근로를 넣지 않았다. "
            "야간 합계에는 평일 연장과 휴일의 야간 중복 분을 포함했다. "
            "휴일 목록은 법정 유급휴일이며 각 행은 서로 다른 날짜다. "
            "시급제의 주휴수당은 정규 유급 근로 분에 포함하지 않았다."
        ),
        "exceptions": [],
    }
    if difficulty == "medium":
        exception = rng.choice(
            [
                "monthly_variable_allowance",
                "withholding_election",
                "hourly_contract",
                "weekday_overtime_night_overlap",
            ]
        )
        scenario["exceptions"] = [exception]
        if exception == "monthly_variable_allowance":
            scenario["variable_allowance"] = rng.randrange(50000, 450001, 10000)
        elif exception == "withholding_election":
            scenario["withholding_percent"] = rng.choice([80, 120])
        elif exception == "weekday_overtime_night_overlap":
            scenario["overtime_minutes"] = rng.choice([480, 600, 720, 960])
            scenario["night_minutes"] = rng.choice([120, 180, 240, 360])
        else:
            weekly = rng.choice([20, 25, 30])
            hourly_rate = rng.randrange(11000, 25001, 100)
            notified = hourly_rate * (weekly * 4 + weekly // 5 * 4)
            scenario.update(
                {
                    "pay_basis": "hourly",
                    "base_salary": 0,
                    "fixed_allowance": 0,
                    "meal_allowance": 0,
                    "hourly_rate": hourly_rate,
                    "monthly_divisor_hours": 0,
                    "weekly_hours": weekly,
                    "regular_minutes": weekly * 4 * 60,
                    "overtime_minutes": 0,
                    "weekly_holiday_included": False,
                    "pension_notified_income": notified,
                    "health_notified_income": notified,
                    "employment_notified_income": notified,
                }
            )
    elif difficulty == "hard":
        hourly = rng.randrange(35000, 55001, 100)
        monthly = hourly * 209
        notified = monthly - meals
        holiday_minutes = rng.choice([540, 600, 660, 720])
        holiday_night = rng.choice([120, 180, 240])
        scenario.update(
            {
                "base_salary": monthly - meals - fixed,
                "pension_notified_income": notified,
                "health_notified_income": notified,
                "employment_notified_income": notified,
                "overtime_minutes": rng.choice([240, 480, 600, 720]),
                "night_minutes": holiday_night + rng.choice([120, 180]),
                "holiday_shifts": [
                    {"minutes": holiday_minutes, "holiday_night_minutes": holiday_night}
                ],
                "family_count": rng.randint(4, 6),
                "eligible_children": rng.choice([2, 3]),
                "exceptions": ["holiday_over_eight_hours_with_night_overlap", "pension_cap"],
            }
        )
        if rng.randrange(2):
            scenario["withholding_percent"] = rng.choice([80, 120])
            scenario["exceptions"].append("withholding_election")
        if rng.randrange(2):
            scenario["variable_allowance"] = rng.randrange(50000, 400001, 10000)
            scenario["exceptions"].append("monthly_variable_allowance")
    _add_rule_evidence(scenario)
    return scenario


LABELS.update(
    {
        "source_contract": "원시 증빙 대조 계약",
        "regular_schedule": "계약상 정규근로 배정",
        "working_days": "해당 월 정규 배정 일수",
        "minutes_per_day": "하루 정규 배정 근로 분수",
        "unpaid_absences": "승인된 무급 결근 기록",
        "week_attendance": "주별 소정근로일과 출근일",
        "week_id": "주 구분",
        "scheduled_days": "소정근로일 수",
        "attended_days": "출근한 소정근로일 수",
        "work_records": "출퇴근과 승인 이력",
        "record_id": "증빙 기록 번호",
        "revision": "수정 차수",
        "status": "승인 또는 실행 상태",
        "category": "정규 배정 또는 추가 작업",
        "start": "시작 시각",
        "end": "종료 시각",
        "breaks": "휴게 구간",
        "holiday_dates": "계약상 법정 유급휴일 날짜",
        "payment_records": "급여 이체 계획과 실행 기록",
        "meal_service": "근무일 식사 제공 방식",
        "evidence_handling_policy": "승인본과 지급 기록 처리 규약",
        "family_count_over_eleven": "공제대상가족 11명 초과 계산 규정",
        "payroll_column": "당시 급여대장의 입력란",
        "paid_holiday_minutes": "정규 임금 외 별도 유급휴일 임금 대상 시간(분)",
        "paid_holiday_pay": "실제 근로 대가와 별도인 유급휴일 임금(원)",
        "paid_holiday_records": "주휴와 구분한 공휴일 유급 임금의 원시 근거",
        "kind": "공휴일 또는 노동절 구분",
        "four_week_scheduled_minutes": "직전 4주 소정근로 시간(분)",
        "normal_worker_four_week_days": "비교 통상근로자의 4주 소정근로일 수",
        "included_in_regular_pay": "해당 유급휴일 임금이 정규 임금에 이미 포함되었는지",
    }
)
