"""Deterministic 2025 employee evidence; no answer values enter the scenario."""

from __future__ import annotations

import hashlib
import random

INSTRUCTIONS = [
    "첨부한 자료로 2025년 연말정산 계산 부탁해요. 결정세액과 기납부세액, 차감징수세액을 답안 형식에 맞춰 정리해 주세요.",
    "연말정산 자료 모아 뒀어요. 공제 요건부터 확인하고 중간 계산값과 최종 세액을 answer.json에 넣어 주세요.",
    "이 직원 연말정산 한 번 봐 주세요. 가족별 공제 가능 여부를 확인해서 요청된 금액을 계산해 주시면 됩니다.",
    "2025년 귀속 정산 금액 확인 부탁드립니다. 첨부 증빙 기준으로 소득공제와 세액공제를 적용해 주세요.",
    "급여랑 간소화 자료 첨부했어요. 공제 한도까지 반영해서 최종 납부 또는 환급 금액 계산 부탁해요.",
    "연말정산 마감 전에 숫자 확인하려고요. 첨부 자료를 읽고 답안 스키마의 각 항목을 채워 주세요.",
    "가족 자료와 지출 증빙 같이 올렸어요. 중복 공제 여부도 확인해서 2025년 정산 결과를 정리해 주세요.",
    "이 건 연말정산 처리 부탁해요. 총급여부터 과세표준, 세액공제와 차감징수세액까지 계산해 주세요.",
    "첨부한 직원 자료의 정산 결과가 필요해요. 소득세와 지방소득세를 따로 계산해서 답안에 남겨 주세요.",
    "연말정산 계산서 만들고 있어요. 증빙에 적힌 지급액과 가족 요건 기준으로 필요한 금액을 채워 주세요.",
    "올해 공제 자료 다 모았습니다. 한도와 대상 요건 확인해서 최종 세액까지 정리 부탁드립니다.",
    "급여 담당자 확인용으로 연말정산 숫자가 필요해요. 요청된 중간값과 정산 금액을 원 단위로 계산해 주세요.",
    "첨부 파일 확인해서 2025년 근로소득 정산 부탁해요. 기납부세액도 반영해 차감징수 금액을 알려 주세요.",
    "이 직원의 공제 내역 검토 부탁드립니다. 지출 증빙에 맞춰 공제액을 계산하고 답안 파일로 정리해 주세요.",
    "연말정산 결과를 시스템에 입력해야 해요. 첨부 자료 기준으로 답안 항목의 숫자를 모두 계산해 주세요.",
    "2025년 정산 자료 전달드립니다. 가족별 요건과 지출 시기를 확인해 결정세액을 계산해 주세요.",
    "근로소득 원천징수 자료랑 공제 증빙 첨부해요. 환급이면 음수로 표시해서 정산 결과를 작성해 주세요.",
    "정산 금액 교차 확인 부탁해요. 자료에 나온 공제 방식대로 계산하고 소득세와 지방세 결과를 나눠 주세요.",
]

LABELS = {
    "employee_id": "직원 식별번호",
    "processing_policy": "원천증명서 선택과 집계 기준",
    "calculation_facts": "연말정산 기본 사실과 공제 증빙",
    "pay_statements": "지급기간별 원천증명서",
    "statement_id": "원천증명서 번호",
    "employer_id": "사용자 식별번호",
    "period_start": "증명 지급기간 시작일",
    "period_end": "증명 지급기간 종료일",
    "revision": "증명 수정차수",
    "status": "증명 발급 상태",
    "gross_pay": "증명 총지급액",
    "non_taxable_pay": "증명 비과세 지급액",
    "withheld_national_tax": "증명 원천징수 소득세",
    "withheld_local_tax": "증명 원천징수 지방소득세",
    "reference_year": "귀속연도",
    "annual_gross": "연간 총지급액",
    "non_taxable": "연간 비과세 지급액",
    "employee_age": "근로자 연말 나이",
    "employee_sex": "근로자 성별",
    "employee_disabled": "근로자 장애인 여부",
    "marital_status": "혼인상태",
    "household_head": "세대주 여부",
    "employment_start": "근로제공 시작일",
    "employment_end": "근로제공 종료일",
    "deduction_choice": "신청 공제 방식",
    "special_deductions_requested": "특별소득공제와 특별세액공제 및 월세 공제 신청 여부",
    "public_pension_paid": "국민연금 본인 실제 납부액",
    "paid_national_tax": "기납부 소득세",
    "paid_local_tax": "기납부 지방소득세",
    "dependents": "부양가족 확인서",
    "person_id": "가족 식별기호",
    "relation": "근로자와의 관계",
    "age": "연말 나이",
    "income_amount": "연간 소득금액",
    "earned_income_only": "근로소득만 있는지 여부",
    "gross_salary": "가족의 연간 총급여",
    "disabled": "장애인 여부",
    "supported": "실제 부양 여부",
    "assigned_claimant": "가족이 합의한 실제 공제 신청자",
    "requested_by_self": "본인 신청서에 공제 요청 여부",
    "birth_order_this_year": "당해 출생 또는 입양 자녀의 누적 신고 순위",
    "social_insurance": "근로자 부담 사회보험 실제 납부액",
    "health": "건강보험료",
    "long_term_care": "장기요양보험료",
    "employment": "고용보험료",
    "pension_accounts": "연금계좌 납입증명",
    "pension_savings": "본인 연금저축 납입액",
    "irp": "본인 IRP 납입액",
    "cards": "카드와 현금영수증 지출 내역",
    "category": "카드 공제 지출 분류",
    "payment_method": "결제수단",
    "amount": "지출액",
    "date": "지출 또는 집계종료일",
    "excluded": "공제 제외 지출 여부",
    "exclusion_reason": "공제 제외 사유",
    "insurance": "보장성보험료 납입 증명",
    "kind": "증빙 분류",
    "paid_by_self": "근로자 본인이 실제 지출했는지 여부",
    "medical": "의료비 지급 증빙",
    "reimbursed": "실손보험 또는 공단 보전액",
    "education": "교육비 납입 증빙",
    "level": "교육기관 단계",
    "scholarship": "장학금 수령액",
    "donations": "기부금 영수증",
    "eligible_organization": "법정 공제대상 기부단체 여부",
    "rent": "월세 계약과 지급 증빙",
    "homeless_household": "무주택 세대 여부",
    "head_claims_housing": "세대주의 주택 공제 신청 여부",
    "address_matches": "계약과 주민등록 주소 일치 여부",
    "eligible_contract_holder": "본인 또는 기본공제 가족 명의 계약 여부",
    "contract_holder_person_id": "임대차 계약자 식별번호",
    "identity_records": "계약자 인적관계 대조 명부",
    "area_sqm": "주택 면적 제곱미터",
    "standard_value": "주택 기준시가",
    "payments": "월세 지급명세",
    "exceptions": "검토할 예외 사항",
    "scenario_id": "가상 직원 자료 묶음 번호",
    "scope_note": "계산 대상의 전제",
    "calculation_notes": "정산 계산 안내",
    "rule_reference": "적용 규정 안내",
    "housing_mortgage": "장기주택저당차입금 자료",
    "interest_payments": "주택대출 이자의 실제 납부일과 납부액",
    "payment_id": "이자 출금 식별번호",
    "requirements_met": "주택 및 차입자 공통 요건 확인",
    "borrowed_date": "차입 약정일",
    "term_years": "약정 상환 기간 연수",
    "fixed_rate": "고정금리 약정 여부",
    "non_deferred": "비거치식 상환 약정 여부",
    "interest_paid": "귀속연도 실제 납부 이자",
    "salary_segments": "근무처별 급여 자료",
    "gross": "총지급액",
    "tax_withheld": "원천징수 소득세",
    "local_withheld": "원천징수 지방소득세",
    "source_contract": "원자료 연결 규약",
    "contract_address": "임대차 계약의 주택 주소",
    "resident_registration_address": "주민등록 등본의 거주 주소",
    "treatment_purpose": "의료기관이 기록한 시술 목적",
    "billed_item": "카드 명세의 실제 청구 명목",
    "institution_type": "납입기관의 실제 종류",
    "household_homes_at_year_end": "귀속연도 말 세대원의 보유 주택",
    "other_common_requirements_attested": "주택 수 외 차입자 및 취득 조건 확인",
    "home_id": "주택 식별기호",
    "address": "주택 주소",
    "owner_person_id": "세대 내 소유자 식별기호",
    "organization_designations": "기부단체 지정 이력 대조표",
    "organization_id": "단체 식별기호",
    "valid_from": "지정 효력 시작일",
    "valid_to": "지정 효력 종료일",
}


def _dependent(person_id: str, relation: str, age: int, **kwargs) -> dict:
    return {
        "person_id": person_id,
        "relation": relation,
        "age": age,
        "income_amount": 0,
        "earned_income_only": False,
        "gross_salary": 0,
        "disabled": False,
        "supported": True,
        "assigned_claimant": "self",
        "requested_by_self": True,
        "birth_order_this_year": 0,
        **kwargs,
    }


def generate(seed: int, difficulty: str) -> dict:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("difficulty must be easy, medium or hard")
    rng = random.Random(seed)
    annual_salary = rng.choice([28, 32, 38, 45, 52, 55, 62, 70, 78, 90, 105, 125]) * 1_000_000
    annual_salary += rng.randrange(0, 99) * 10_000
    start = "2025-01-01"
    exceptions = []
    sex = "male"
    family = []
    marital = rng.choice(["single", "married"])
    if marital == "married":
        family.append(_dependent("F1", "spouse", rng.randint(29, 47)))
        for child in range(rng.randrange(0, 4)):
            family.append(_dependent(f"C{child + 1}", "child", rng.choice([3, 6, 8, 12, 16, 19])))
    elif rng.randrange(3) == 0:
        family.append(_dependent("P1", "parent", rng.randrange(60, 80)))
    if difficulty == "medium":
        start = rng.choice(["2025-03-01", "2025-05-01", "2025-07-01"])
        annual_salary = annual_salary * (13 - int(start[5:7])) // 12
        exceptions.append("중도 입사 전 의료비와 카드 사용액이 포함되어 있음")
    if difficulty == "hard":
        marital = "married"
        # This family's agreed claim belongs to the spouse, despite the employee's draft request.
        family = [
            _dependent(
                "F1",
                "spouse",
                rng.randint(30, 48),
                income_amount=24_000_000,
                gross_salary=36_000_000,
                earned_income_only=True,
                assigned_claimant="none",
                requested_by_self=False,
            ),
            _dependent("C1", "child", rng.choice([8, 12, 16]), assigned_claimant="spouse"),
            _dependent("C2", "child", rng.choice([3, 9, 17])),
            _dependent("P1", "parent", rng.randint(61, 78), income_amount=1_200_000),
        ]
        exceptions.extend(
            [
                "배우자가 공제하는 첫째 자녀를 본인 신청서에서도 중복 요청함",
                "부모의 연간 소득금액이 기본공제 소득요건을 초과함",
            ]
        )
    non_taxable = rng.choice([1_200_000, 2_400_000])
    months = 13 - int(start[5:7])
    opaque_id = hashlib.sha256(f"yearend:{seed}".encode()).hexdigest()[:14]
    s = {
        "scenario_id": f"가상YE-{opaque_id}",
        "reference_year": 2025,
        "scope_note": "국내 거주자로 근로소득만 있음. 주택 소득공제, 이월기부금, 혼인세액공제, 세액감면은 신청하지 않음.",
        "calculation_notes": [
            "itemized는 개별 특별소득공제와 특별세액공제를 신청한 방식이며 표준세액공제는 함께 적용하지 않음.",
            "standard를 신청한 경우 특별소득공제와 특별세액공제 및 월세 세액공제를 적용하지 않고 13만원 표준세액공제를 적용함.",
            "이 자료의 결정세액은 원 단위로 계산하며 원 미만 금액은 버림. 지방소득세 결정세액은 소득세 결정세액의 10%로 계산한 뒤 원 미만을 버림.",
            "영수증 차감징수세액은 원 단위 결정세액에서 기납부세액을 빼며 10원 단위로 절사하지 않음. 환급은 음수로 표시하고 두 차감징수액을 합쳐 정산합계로 보고함. 실제 납부 단계 끝수 처리는 이 답안 범위에 포함하지 않음.",
            "카드 항목은 서로 중복하지 않는 분류별 사용액임. culture는 공제대상 도서나 문화 관람료이며 2025년 7월 이후 적격 체육시설 이용료만 포함함.",
            "보험료와 의료비 및 교육비는 근로제공 기간에 실제 지출한 금액만 검토함. 기부금은 입사 전 지출도 검토함.",
            "assigned_claimant의 self는 이 근로자, spouse는 배우자를 의미함. 배우자에게 배정한 가족을 본인 신청서에 중복 요청해도 본인 공제에서 제외함.",
        ],
        "rule_reference": [
            "2025년 근로소득공제: 총급여 500만원까지 70%. 1500만원까지는 350만원과 500만원 초과분 40%. 4500만원까지는 750만원과 1500만원 초과분 15%.",
            "1억원까지 근로소득공제는 1200만원과 4500만원 초과분 5%. 1억원 초과는 1475만원과 1억원 초과분 2%. 공제한도 2000만원.",
            "기본공제는 본인과 적격 가족 각 150만원. 가족 소득금액 100만원 이하 또는 근로소득만 있으면 총급여 500만원 이하. 자녀 20세 이하, 부모 60세 이상. 장애인은 나이요건 제외.",
            "경로우대 70세 이상 100만원, 장애인 200만원. 한부모는 적격 자녀가 있으면 100만원. 부녀자 50만원과 중복되는 경우 한부모만 적용.",
            "국민연금 본인 납부액과 건강보험, 장기요양보험 및 고용보험 본인 납부액은 소득공제 대상.",
            "카드공제 문턱은 총급여 25%. 신용카드 15%, 체크와 현금영수증 및 문화비 30%, 전통시장과 대중교통 40%. 문턱은 15% 항목부터 차감함.",
            "카드공제 기본한도는 총급여 7000만원 이하 300만원, 초과 250만원. 초과공제액과 전통시장 및 대중교통의 공제금액 합계 중 작은 금액을 추가하되 총급여 7000만원 이하자는 문화비도 합쳐 300만원 한도, 초과자는 200만원 한도.",
            "연금저축 납입액 600만원, IRP 포함 900만원 한도. 총급여 5500만원 이하 세액공제율 15%, 초과 12%.",
            "기본공제 대상 자녀와 손자녀 중 8세 이상은 1명 25만원, 2명 55만원, 3명부터 추가 40만원. 당해연도 출생 또는 입양 자녀는 첫째 30만원, 둘째 50만원, 셋째부터 70만원 추가.",
            "보장성보험료 100만원 한도 12%. 장애인전용 보장성보험료는 별도 100만원 한도 15%.",
            "의료비는 실손보험 보전액을 뺀 뒤 총급여 3% 초과분 대상. 일반 가족은 700만원 한도 15%. 본인 및 6세 이하, 65세 이상과 장애인은 한도 없이 15%. 미숙아 20%, 난임 30%.",
            "교육비는 장학금을 차감하고 15%. 본인은 한도 없음. 가족의 학교 교육비 1인 300만원, 대학 900만원 한도. 가족 대학원과 부모 일반 교육비는 제외.",
            "기부금은 특례가 근로소득금액 전액, 일반은 30% 한도. 세액공제는 1000만원까지 15%, 초과 30%.",
            "월세는 총급여 8000만원 이하 무주택 세대와 전입주소 일치 등 요건 충족 시 연 1000만원 한도. 총급여 5500만원 이하 17%, 초과 15%. 주택 85제곱미터 이하 또는 기준시가 4억원 이하.",
            "과세표준별 세율과 누진공제: 1400만원 이하 6%와 0원, 5000만원 이하 15%와 126만원, 8800만원 이하 24%와 576만원, 1억5000만원 이하 35%와 1544만원.",
            "3억원 이하 세율38%와 누진공제1994만원, 5억원 이하 40%와 2594만원, 10억원 이하 42%와 3594만원, 10억원 초과 45%와 6594만원. 산출세액은 과세표준에 세율을 곱한 후 누진공제를 차감함.",
            "근로소득세액공제는 산출세액130만원 이하55%, 초과는71만5000원과130만원 초과분30%. 총급여3300만원 이하 한도74만원, 7000만원 이하 한도는74만원에서3300만원 초과급여의0.8%를 빼되 최저66만원.",
            "총급여7000만원 초과1억2000만원 이하는 근로소득세액공제 한도66만원에서7000만원 초과급여의50%를 빼되 최저50만원. 1억2000만원 초과는50만원에서1억2000만원 초과급여의50%를 빼되 최저20만원.",
        ],
        "annual_gross": annual_salary + non_taxable,
        "non_taxable": non_taxable,
        "employee_age": rng.randint(29, 58),
        "employee_sex": sex,
        "employee_disabled": False,
        "marital_status": marital,
        "household_head": True,
        "employment_start": start,
        "employment_end": "2025-12-31",
        "deduction_choice": "itemized",
        "public_pension_paid": rng.randint(110_000, 250_000) // 10 * 10 * months,
        "social_insurance": {
            "health": rng.randint(90_000, 220_000) // 10 * 10 * months,
            "long_term_care": rng.randint(12_000, 28_000) // 10 * 10 * months,
            "employment": rng.randint(25_000, 80_000) // 10 * 10 * months,
        },
        "pension_accounts": {
            "pension_savings": rng.choice([0, 1_200_000, 3_600_000, 6_000_000, 7_200_000]),
            "irp": rng.choice([0, 2_000_000, 3_000_000, 6_000_000]),
        },
        "paid_national_tax": rng.randint(120, 1200) * 10_000,
        "paid_local_tax": 0,
        "dependents": family,
        "cards": [],
        "insurance": [],
        "medical": [],
        "education": [],
        "donations": [],
        "rent": {},
        "exceptions": exceptions,
    }
    s["paid_local_tax"] = s["paid_national_tax"] // 10
    categories = ["credit", "debit", "culture", "market", "transit"]
    ranges = [
        (6_000_000, 26_000_000),
        (1_000_000, 12_000_000),
        (100_000, 1_500_000),
        (100_000, 3_000_000),
        (300_000, 2_000_000),
    ]
    for category, (low, high) in zip(categories, ranges, strict=True):
        s["cards"].append(
            {
                "person_id": "self",
                "category": category,
                "payment_method": "credit" if category == "credit" else "debit",
                "amount": rng.randrange(low // 1000, high // 1000) * 1000,
                "date": "2025-12-15",
                "excluded": False,
                "exclusion_reason": "없음",
            }
        )
    s["insurance"].append(
        {
            "person_id": "self",
            "kind": "general",
            "paid_by_self": True,
            "amount": rng.choice([600_000, 1_200_000, 1_800_000]),
            "date": "2025-12-10",
        }
    )
    s["medical"].append(
        {
            "person_id": "self",
            "kind": "ordinary",
            "paid_by_self": True,
            "amount": rng.randrange(20, 800) * 10_000,
            "reimbursed": 0,
            "date": "2025-12-09",
            "excluded": False,
        }
    )
    if family:
        beneficiary = next((p for p in family if p["relation"] == "child"), family[0])
        s["medical"].append(
            {
                "person_id": beneficiary["person_id"],
                "kind": "ordinary",
                "paid_by_self": True,
                "amount": rng.randrange(20, 500) * 10_000,
                "reimbursed": 0,
                "date": "2025-11-20",
                "excluded": False,
            }
        )
        if beneficiary["relation"] == "child":
            s["education"].append(
                {
                    "person_id": beneficiary["person_id"],
                    "level": "school",
                    "paid_by_self": True,
                    "amount": rng.randrange(10, 450) * 10_000,
                    "scholarship": 0,
                    "date": "2025-11-15",
                    "excluded": False,
                }
            )
    s["education"].append(
        {
            "person_id": "self",
            "level": "graduate",
            "paid_by_self": True,
            "amount": rng.choice([0, 1_000_000, 3_000_000, 6_000_000]),
            "scholarship": 0,
            "date": "2025-10-01",
            "excluded": False,
        }
    )
    s["donations"].append(
        {
            "person_id": "self",
            "kind": rng.choice(["public", "statutory"]),
            "amount": rng.choice([100_000, 300_000, 1_000_000, 2_000_000]),
            "eligible_organization": True,
            "date": "2025-12-24",
        }
    )
    if rng.randrange(3) == 0:
        s["rent"] = {
            "homeless_household": True,
            "household_head": True,
            "head_claims_housing": False,
            "address_matches": True,
            "eligible_contract_holder": True,
            "area_sqm": rng.choice([24, 38, 59, 84]),
            "standard_value": rng.randrange(100, 380) * 1_000_000,
            "payments": [
                {"date": f"2025-{month:02d}-25", "amount": rng.choice([450_000, 650_000, 850_000])}
                for month in range(int(start[5:7]), 13)
            ],
        }
    if difficulty == "medium":
        s["medical"].append(
            {
                "person_id": "self",
                "kind": "ordinary",
                "paid_by_self": True,
                "amount": rng.randrange(20, 150) * 10_000,
                "reimbursed": 0,
                "date": "2025-01-10",
                "excluded": False,
            }
        )
        s["cards"].append(
            {
                "person_id": "self",
                "category": "credit",
                "payment_method": "credit",
                "amount": rng.randrange(100, 400) * 10_000,
                "date": "2025-02-01",
                "excluded": False,
                "exclusion_reason": "입사 전 지출",
            }
        )
    if difficulty == "hard":
        s["medical"][0]["reimbursed"] = s["medical"][0]["amount"] // 3
        s["cards"].append(
            {
                "person_id": "C1",
                "category": "debit",
                "payment_method": "debit",
                "amount": rng.randrange(20, 100) * 10_000,
                "date": "2025-12-01",
                "excluded": False,
                "exclusion_reason": "없음",
            }
        )
    return s
