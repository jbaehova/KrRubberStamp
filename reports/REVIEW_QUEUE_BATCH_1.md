# Batch 1 사람 검수 대기열

분야별 무작위 15문항, 총 60문항을 검수 대기 상태로 정리했습니다.

무작위 추출 시드는 20261009입니다. 추출은 문항 선택에만 쓰이며 사실이나 지시문을 생성하지 않습니다. 자동 게이트는 전문가의 독립적인 법률 해석 및 문항 다양성 검수를 대체하지 않습니다.

## B1_A043_1b254a19 (A_yearend, hard)

집필 제목: 주택이자와 카드 공제의 종합 한도 검토

업무 목적: 개별 공제 한도를 적용한 뒤 주택과 카드의 종합 소득공제 제한을 정산에 반영한다.

가상너울건축의 가상오지환 정산을 마감합니다. 주택이자와 카드 공제를 각각 한도 처리한 뒤 합산 제한도 확인해야 합니다. 주택 소득공제액과 카드 소득공제액 및 종합 한도 초과액을 적고, 연금계좌 공제와 최종 과세표준 및 소득세 결정세액을 구해 주세요.

설계 의도: 고정금리 비거치 장기대출과 큰 시장 및 교통 지출로 두 공제의 개별 한도 및 합산 제한이 순차 적용된다.

집필 원고 ID: `A043`, 전체 문항 SHA-256: `1b254a199687621409abf8b232e1799e1d8fd2d4345655066e1b57c890989aef`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A043_1b254a19/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_004_053.json)

입력 파일:

- [01_직원.hwpx](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/01_직원.hwpx) (hwpx)
- [02_급여.xlsx](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/02_급여.xlsx) (xlsx)
- [03_대출약정.pdf](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/03_대출약정.pdf) (pdf)
- [04_주택요건.hwpx](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/04_주택요건.hwpx) (hwpx)
- [05_이자납부.pdf](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/05_이자납부.pdf) (pdf)
- [06_일반카드.xlsx](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/06_일반카드.xlsx) (xlsx)
- [07_시장사용.xlsx](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/07_시장사용.xlsx) (xlsx)
- [08_교통사용.xlsx](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/08_교통사용.xlsx) (xlsx)
- [09_연금계좌.pdf](../data/batch_1/A_yearend/B1_A043_1b254a19/inputs/09_연금계좌.pdf) (pdf)

정답: [gold.json](../data/batch_1/A_yearend/B1_A043_1b254a19/gold.json)

```json
{
  "credit_card_deduction": 6000000,
  "final_national_tax": 1531500,
  "housing_income_deduction": 20000000,
  "income_deduction_limit_excess": 1000000,
  "pension_account_credit": 516000,
  "tax_base": 26450000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 1500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13050000, "salary_income": 52950000, "total_salary": 66000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 20000000 |
| A_CARD | 6000000 |
| A_PENSION_CREDIT | 516000 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 2707500 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 20000000, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "speci... |
| A_FINAL | 1531500 |
| A_LOCAL | 153150 |
| A_SETTLEMENT | {"local": 153150, "national": 1531500, "total": 1684650} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A043_1b254a19/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A049_93402a3c (A_yearend, hard)

집필 제목: 고령 장애인 한부모의 추가공제와 성년 딸 교육비

업무 목적: 경로우대와 장애인 및 한부모 공제를 누락이나 중복 없이 등록하고 교육기관별 범위를 구분한다.

가상은빛기록의 가상강미소 인적공제를 확인합니다. 직원과 성년 딸이 모두 장애인이고 직원은 일흔두 살의 사별 여성입니다. 기본공제와 추가공제액을 계산한 뒤 딸 대학원 학비와 특수교육비를 구분해 교육비 세액공제액을 구해 주세요. 직원의 두 종류 보험과 의료비 공제 및 최종 소득세도 필요합니다.

설계 의도: 성년 장애인 자녀의 나이 예외가 있어 한부모 추가공제가 적용된다. 가족의 일반 대학원 학비와 장애인 특수교육은 처리 범위가 다르다.

집필 원고 ID: `A049`, 전체 문항 SHA-256: `93402a3c06d2a04ac40227a381b01017ea457757e5fd4ab1721f799cf8290f06`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A049_93402a3c/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_004_053.json)

입력 파일:

- [01_인사.hwpx](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/01_인사.hwpx) (hwpx)
- [02_급여.xlsx](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/02_급여.xlsx) (xlsx)
- [03_딸소득.pdf](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/03_딸소득.pdf) (pdf)
- [04_딸장애.pdf](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/04_딸장애.pdf) (pdf)
- [05_직원장애.pdf](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/05_직원장애.pdf) (pdf)
- [06_대학원.pdf](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/06_대학원.pdf) (pdf)
- [07_특수교육.pdf](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/07_특수교육.pdf) (pdf)
- [08_직원보험.xlsx](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/08_직원보험.xlsx) (xlsx)
- [09_직원진료.pdf](../data/batch_1/A_yearend/B1_A049_93402a3c/inputs/09_직원진료.pdf) (pdf)

정답: [gold.json](../data/batch_1/A_yearend/B1_A049_93402a3c/gold.json)

```json
{
  "additional_deduction": 6000000,
  "basic_deduction": 3000000,
  "education_credit": 1410000,
  "final_national_tax": 0,
  "insurance_credit": 238800,
  "medical_credit": 478500
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 6000000, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 10800000, "salary_income": 26200000, "total_salary": 37000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 238800 |
| A_MEDICAL_CREDIT | 478500 |
| A_EDUCATION_CREDIT | 1410000 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 1320000 |
| A_EMPLOYMENT_CREDIT | 708000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 1410000, "hometown_credit": 0, "insurance_credit": 238800, "medical_credit": 478500, "political_credit": 0, "rent_credit": 0... |
| A_FINAL | 0 |
| A_LOCAL | 0 |
| A_SETTLEMENT | {"local": 0, "national": 0, "total": 0} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A049_93402a3c/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A072_3499a858 (A_yearend, medium)

집필 제목: 고령 형의 대학원 학비를 가족 교육비로 신청한 경우

업무 목적: 고령 형제의 기본공제 자격과 대학원 교육비 자격을 따로 확인한다.

가상동녘조명의 가상류한서는 무소득 예순네 살 형을 부양하면서 형의 대학원 학비를 냈습니다. 가족 기본공제 대상 인원과 기본공제액을 확인해 주세요. 본인이 부담했다는 이유만으로 형의 대학원 학비가 공제되는지 교육비 세액공제액도 계산합니다.

설계 의도: 성년 대학생 형제의 학부 수업료와 달리 가족 기본공제는 인정되지만 대학원 과정이 제출되었다. 같은 가족의 항목별 판정이 달라진다.

집필 원고 ID: `A072`, 전체 문항 SHA-256: `3499a858ad2366529754f10fd79a6627f0e44e36df2d8ef964583bee4ae97012`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A072_3499a858/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_054_103.json)

입력 파일:

- [01_가족신청.hwpx](../data/batch_1/A_yearend/B1_A072_3499a858/inputs/01_가족신청.hwpx) (hwpx)
- [02_급여기초.xlsx](../data/batch_1/A_yearend/B1_A072_3499a858/inputs/02_급여기초.xlsx) (xlsx)
- [03_형가족확인.pdf](../data/batch_1/A_yearend/B1_A072_3499a858/inputs/03_형가족확인.pdf) (pdf)
- [04_대학원등록금.pdf](../data/batch_1/A_yearend/B1_A072_3499a858/inputs/04_대학원등록금.pdf) (pdf)

정답: [gold.json](../data/batch_1/A_yearend/B1_A072_3499a858/gold.json)

```json
{
  "basic_deduction": 3000000,
  "education_credit": 0,
  "eligible_dependents": 1
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13200000, "salary_income": 55800000, "total_salary": 69000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 6912000 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special_inco... |
| A_FINAL | 6252000 |
| A_LOCAL | 625200 |
| A_SETTLEMENT | {"local": 625200, "national": 6252000, "total": 6877200} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A072_3499a858/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A099_a21276a0 (A_yearend, hard)

집필 제목: 요건이 다른 주택 이자와 가족 지출 영수증의 제외 사유 정리

업무 목적: 모두 영수증이 있는 가족 지출에서 서로 다른 제외 사유를 구분하고 인정 보험료를 남긴다.

가상별하위생의 가상연지수에게 주택 이자와 가족 지출 자료가 제출됐습니다. 대출 약정과 연말 세대원 주택 목록, 학비 장학금 및 병원비 납부자를 각각 대조해 주세요. 공제대상 가족 수와 기본공제액, 주택자금 소득공제액 및 교육비와 의료비와 보험료 세액공제액을 구합니다. 최종 과세표준과 소득세 결정세액도 필요합니다.

설계 의도: 대출 우대 조건은 좋지만 공통 주택 요건이 충족되지 않는다. 학교비는 전액 장학금이고 병원비는 배우자가 자기 돈으로 부담했으며 아버지 보험은 직원 부담이라 적용된다.

집필 원고 ID: `A099`, 전체 문항 SHA-256: `a21276a02b273c36cc3166342bc2c249c471c84ccab6cc930fe7d1b1c0c90cbd`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A099_a21276a0/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_054_103.json)

입력 파일:

- [01_신청범위.hwpx](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/01_신청범위.hwpx) (hwpx)
- [02_급여.xlsx](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/02_급여.xlsx) (xlsx)
- [03_대출요건.hwpx](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/03_대출요건.hwpx) (hwpx)
- [04_이자납부.pdf](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/04_이자납부.pdf) (pdf)
- [05_자녀가족.pdf](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/05_자녀가족.pdf) (pdf)
- [06_전액장학.xlsx](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/06_전액장학.xlsx) (xlsx)
- [07_아버지가족.pdf](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/07_아버지가족.pdf) (pdf)
- [08_아버지보험.pdf](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/08_아버지보험.pdf) (pdf)
- [09_배우자가족.pdf](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/09_배우자가족.pdf) (pdf)
- [10_배우자병원비.xlsx](../data/batch_1/A_yearend/B1_A099_a21276a0/inputs/10_배우자병원비.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/A_yearend/B1_A099_a21276a0/gold.json)

```json
{
  "basic_deduction": 6000000,
  "education_credit": 0,
  "eligible_dependents": 3,
  "final_national_tax": 2757500,
  "housing_income_deduction": 0,
  "insurance_credit": 120000,
  "medical_credit": 0,
  "tax_base": 33650000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"housing_mortgage.requirements_met": false} |
| A_PERSONAL | {"additional": 0, "basic": 6000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 12350000, "salary_income": 39650000, "total_salary": 52000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 120000 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 3787500 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 120000, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 2757500 |
| A_LOCAL | 275750 |
| A_SETTLEMENT | {"local": 275750, "national": 2757500, "total": 3033250} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A099_a21276a0/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A103_5baaaaee (A_yearend, hard)

집필 제목: 공제 합계가 큰 직원의 환급 한계를 정산 전표에 반영

업무 목적: 큰 공제가 있어도 결정세액과 실제 원천징수 환급을 혼동하지 않는 전표를 작성한다.

가상풀꽃재생의 가상비서안은 큰 의료비와 연금 납입 및 어머니 기부 자료로 세금이 음수가 될 것으로 예상했습니다. 자녀의 근로소득 확인과 보험 보전 및 연금 한도를 반영해 교육비와 의료비 및 연금계좌 공제액을 계산해 주세요. 산출세액과 근로소득세액공제 및 전체 세액공제 합계를 구하고 결정 소득세와 지방소득세를 적습니다. 기납부세액을 대조한 정산 합계를 구하되 환급은 음수로 표시합니다.

설계 의도: 공제 합계가 산출세액보다 커 결정세액이 영으로 제한되는 사례다. 자녀의 근로소득 특례 기준 초과와 의료 보전금 및 연금의 개별 및 합산 한도를 먼저 적용해야 한 뒤에야 환급 전표를 마감할 수 있다.

집필 원고 ID: `A103`, 전체 문항 SHA-256: `5baaaaee0b8a89645f22d783bba3f15e8a72087e52e5355e717775330879513f`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A103_5baaaaee/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_054_103.json)

입력 파일:

- [01_환급질의.hwpx](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/01_환급질의.hwpx) (hwpx)
- [02_급여확정.xlsx](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/02_급여확정.xlsx) (xlsx)
- [03_어머니부양.pdf](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/03_어머니부양.pdf) (pdf)
- [04_자녀근로소득.pdf](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/04_자녀근로소득.pdf) (pdf)
- [05_자녀학비.pdf](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/05_자녀학비.pdf) (pdf)
- [06_어머니진료.pdf](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/06_어머니진료.pdf) (pdf)
- [07_어머니보전금.xlsx](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/07_어머니보전금.xlsx) (xlsx)
- [08_연금저축.pdf](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/08_연금저축.pdf) (pdf)
- [09_IRP.pdf](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/09_IRP.pdf) (pdf)
- [10_어머니기부.pdf](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/10_어머니기부.pdf) (pdf)
- [11_원천징수누계.xlsx](../data/batch_1/A_yearend/B1_A103_5baaaaee/inputs/11_원천징수누계.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/A_yearend/B1_A103_5baaaaee/gold.json)

```json
{
  "computed_tax": 1407000,
  "education_credit": 0,
  "employment_credit": 740000,
  "final_local_tax": 0,
  "final_national_tax": 0,
  "medical_credit": 636900,
  "pension_account_credit": 1350000,
  "settlement_total": -1041800,
  "total_tax_credits": 3707000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 1000000, "basic": 3000000, "rejected": ["child"]} |
| A_SALARY | {"salary_deduction": 10020000, "salary_income": 21780000, "total_salary": 31800000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 1350000 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 636900 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 980100 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 1407000 |
| A_EMPLOYMENT_CREDIT | 740000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 980100, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 636900, "political_credit": 0, "rent_credit": 0}, "sp... |
| A_FINAL | 0 |
| A_LOCAL | 0 |
| A_SETTLEMENT | {"local": -94800, "national": -947000, "total": -1041800} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A103_5baaaaee/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A119_bd5e4305 (A_yearend, medium)

집필 제목: 부모 명의로 낸 기부 영수증의 공제 배정을 다시 확인

업무 목적: 직원의 송금 사실과 기부 영수증의 공제 배정을 구분해 가족 기부 등록을 정리한다.

가상라일락번역의 가상염서후는 아버지 계좌에 보낸 돈으로 발급된 기부 영수증을 제출했습니다. 아버지의 공제 배정 확인서와 영수증 명의를 맞춰 본인을 제외한 가족 수 및 기본공제액을 정리해 주세요. 본인 명의의 별도 기부까지 반영한 기부금 세액공제액도 계산합니다.

설계 의도: 직원이 송금한 돈이 포함되어도 아버지 공제를 다른 형제에게 배정한 사실은 그대로다. 직원 본인 영수증은 따로 존재해 모든 기부를 일괄 삭제하면 틀린다.

집필 원고 ID: `A119`, 전체 문항 SHA-256: `bd5e4305622682a229651889b660f02136195170594c30f38d5413ae43ff4730`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A119_bd5e4305/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_104_153.json)

입력 파일:

- [01_급여.xlsx](../data/batch_1/A_yearend/B1_A119_bd5e4305/inputs/01_급여.xlsx) (xlsx)
- [02_가족배정.hwpx](../data/batch_1/A_yearend/B1_A119_bd5e4305/inputs/02_가족배정.hwpx) (hwpx)
- [03_지원금송금.pdf](../data/batch_1/A_yearend/B1_A119_bd5e4305/inputs/03_지원금송금.pdf) (pdf)
- [04_아버지기부.pdf](../data/batch_1/A_yearend/B1_A119_bd5e4305/inputs/04_아버지기부.pdf) (pdf)
- [05_직원기부.pdf](../data/batch_1/A_yearend/B1_A119_bd5e4305/inputs/05_직원기부.pdf) (pdf)

정답: [gold.json](../data/batch_1/A_yearend/B1_A119_bd5e4305/gold.json)

```json
{
  "basic_deduction": 1500000,
  "donation_credit": 120000,
  "eligible_dependents": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 1500000, "rejected": ["father"]} |
| A_SALARY | {"salary_deduction": 12500000, "salary_income": 42500000, "total_salary": 55000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 120000 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 4890000 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 120000, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 4110000 |
| A_LOCAL | 411000 |
| A_SETTLEMENT | {"local": 411000, "national": 4110000, "total": 4521000} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A119_bd5e4305/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A133_4f2c7360 (A_yearend, medium)

집필 제목: 주택이자와 배우자가 부담한 직원 보험의 정산 칸 분리

업무 목적: 본인 명의 주택이자와 본인이 피보험자인 보험료의 실제 부담을 서로 다른 정산 항목으로 처리한다.

가상작약관리의 가상빈시우는 주택이자 증명과 직원 본인 대상 보험 영수증을 냈습니다. 보험료는 배우자가 자기 비용으로 냈습니다. 대출의 기간과 상환 방식을 확인해 주택자금 소득공제액을 구하고 보험료 세액공제액을 별도로 판단해 주세요. 과세표준과 최종 소득세도 필요합니다.

설계 의도: 비거치 장기대출의 이자는 정상 본인 부담이지만 보험의 피보험자와 납부자는 다르다. 두 자료의 직원 명의만으로 모두 개인 공제에 넣는 오류를 확인한다.

집필 원고 ID: `A133`, 전체 문항 SHA-256: `4f2c736065264276b8286b6cf24bd1a87732eb3d40ef73e0cd59b848d3ccfd93`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A133_4f2c7360/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_104_153.json)

입력 파일:

- [01_부담확인.hwpx](../data/batch_1/A_yearend/B1_A133_4f2c7360/inputs/01_부담확인.hwpx) (hwpx)
- [02_급여.xlsx](../data/batch_1/A_yearend/B1_A133_4f2c7360/inputs/02_급여.xlsx) (xlsx)
- [03_대출계약.pdf](../data/batch_1/A_yearend/B1_A133_4f2c7360/inputs/03_대출계약.pdf) (pdf)
- [04_이자납입.pdf](../data/batch_1/A_yearend/B1_A133_4f2c7360/inputs/04_이자납입.pdf) (pdf)
- [05_보험납부.pdf](../data/batch_1/A_yearend/B1_A133_4f2c7360/inputs/05_보험납부.pdf) (pdf)

정답: [gold.json](../data/batch_1/A_yearend/B1_A133_4f2c7360/gold.json)

```json
{
  "final_national_tax": 6784000,
  "housing_income_deduction": 18000000,
  "insurance_credit": 0,
  "tax_base": 54350000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 1500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 14150000, "salary_income": 73850000, "total_salary": 88000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 18000000 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 7284000 |
| A_EMPLOYMENT_CREDIT | 500000 |
| A_STANDARD | {"housing_deduction_applied": 18000000, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "speci... |
| A_FINAL | 6784000 |
| A_LOCAL | 678400 |
| A_SETTLEMENT | {"local": 678400, "national": 6784000, "total": 7462400} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A133_4f2c7360/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A134_eb1df8ce (A_yearend, medium)

집필 제목: 같은 대학의 장학금 수혜 학비와 발전기금 기부 구분

업무 목적: 동일 대학이 발급한 학비와 기부 자료를 실제 지출 목적에 맞춰 처리한다.

가상수선화조사의 가상묘하린은 대학 자녀의 등록금 증명과 본인 명의 대학 발전기금 기부 영수증을 냈습니다. 자녀 학비에 지급된 장학금을 반영해 교육비 세액공제액을 구해 주세요. 별도 공제 대상 발전기금의 기부금 세액공제액과 기본공제액도 작성합니다. 기관이 같다고 두 지출을 등록금으로 합치지 마세요.

설계 의도: 학비는 학교 장학금으로 전액 충당했지만 직원 본인의 발전기금 기부는 별도 실제 납부다. 교육비를 기부금으로 옮기거나 기부를 학비와 합치지 않고 각각 검토한다.

집필 원고 ID: `A134`, 전체 문항 SHA-256: `eb1df8ce322a09a6510ed0785bde75301b278e70e2f6e704b34b70b1e1596a25`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A134_eb1df8ce/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_104_153.json)

입력 파일:

- [01_가족신청.hwpx](../data/batch_1/A_yearend/B1_A134_eb1df8ce/inputs/01_가족신청.hwpx) (hwpx)
- [02_급여.xlsx](../data/batch_1/A_yearend/B1_A134_eb1df8ce/inputs/02_급여.xlsx) (xlsx)
- [03_등록금장학금.xlsx](../data/batch_1/A_yearend/B1_A134_eb1df8ce/inputs/03_등록금장학금.xlsx) (xlsx)
- [04_발전기금.pdf](../data/batch_1/A_yearend/B1_A134_eb1df8ce/inputs/04_발전기금.pdf) (pdf)

정답: [gold.json](../data/batch_1/A_yearend/B1_A134_eb1df8ce/gold.json)

```json
{
  "basic_deduction": 3000000,
  "donation_credit": 390000,
  "education_credit": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13300000, "salary_income": 57700000, "total_salary": 71000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 390000 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 7368000 |
| A_EMPLOYMENT_CREDIT | 500000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 390000, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 6228000 |
| A_LOCAL | 622800 |
| A_SETTLEMENT | {"local": 622800, "national": 6228000, "total": 6850800} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A134_eb1df8ce/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A155_8ccb0655 (A_yearend, easy)

집필 제목: 직원 일반보험과 장애인 자녀 전용보험의 두 공제 칸 등록

업무 목적: 서로 다른 보험 공제 한도를 적용하고 자녀의 인적공제를 함께 등록한다.

가상작약물류의 가상우다겸 보험 자료를 정산 시스템에 등록해 주세요. 본인 일반 보장성보험과 장애인 자녀의 전용 보장성보험을 확인하고 보험료 세액공제액을 합산합니다. 자녀를 반영한 기본공제액 및 추가공제액도 적어 주세요.

설계 의도: 두 계약은 각자의 피보험자와 상품 구분을 가진 정상 보험이다. 일반보험의 한도 초과액을 장애인 전용보험의 여유 한도로 옮기면 보험 공제액이 달라진다.

집필 원고 ID: `A155`, 전체 문항 SHA-256: `8ccb0655b0cee2b42ca3037d4ad789c7281750c0d3eddac69b1ba8f2d81af171`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A155_8ccb0655/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_154_203.json)

입력 파일:

- [01_가족보험신청.hwpx](../data/batch_1/A_yearend/B1_A155_8ccb0655/inputs/01_가족보험신청.hwpx) (hwpx)
- [02_보험납부증명.pdf](../data/batch_1/A_yearend/B1_A155_8ccb0655/inputs/02_보험납부증명.pdf) (pdf)
- [03_급여집계.xlsx](../data/batch_1/A_yearend/B1_A155_8ccb0655/inputs/03_급여집계.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/A_yearend/B1_A155_8ccb0655/gold.json)

```json
{
  "additional_deduction": 2000000,
  "basic_deduction": 3000000,
  "insurance_credit": 231000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 2000000, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13200000, "salary_income": 55800000, "total_salary": 69000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 231000 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 6432000 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 231000, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 5291000 |
| A_LOCAL | 529100 |
| A_SETTLEMENT | {"local": 529100, "national": 5291000, "total": 5820100} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A155_8ccb0655/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A172_4ccf780f (A_yearend, medium)

집필 제목: 세대주 주택공제 신청과 세대원 월세 신청의 중복 점검

업무 목적: 세대주의 주택공제 신청 사실을 확인해 세대원 월세 자료를 정산한다.

가상가죽나무검사의 가상정모은은 세대원으로 월세를 납부했습니다. 세대주 신청 확인서와 임대 증빙을 대조해 월세 세액공제액을 계산해 주세요. 별도로 낸 IRP의 세액공제액과 결정 국세도 적습니다.

설계 의도: 임차 주택과 주소가 정상이어도 세대원 신청에는 세대주의 공제 신청 사실이 영향을 준다. 개인 연금계좌의 정상 공제는 별도로 남아야 한다.

집필 원고 ID: `A172`, 전체 문항 SHA-256: `4ccf780f65910150a36f7e4971d667ffb05bca547923d60923e2247d0eb28e18`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A172_4ccf780f/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_154_203.json)

입력 파일:

- [01_세대주신청.hwpx](../data/batch_1/A_yearend/B1_A172_4ccf780f/inputs/01_세대주신청.hwpx) (hwpx)
- [02_임대계약.pdf](../data/batch_1/A_yearend/B1_A172_4ccf780f/inputs/02_임대계약.pdf) (pdf)
- [03_월세연금.xlsx](../data/batch_1/A_yearend/B1_A172_4ccf780f/inputs/03_월세연금.xlsx) (xlsx)
- [04_지급접수.pdf](../data/batch_1/A_yearend/B1_A172_4ccf780f/inputs/04_지급접수.pdf) (pdf)

정답: [gold.json](../data/batch_1/A_yearend/B1_A172_4ccf780f/gold.json)

```json
{
  "final_national_tax": 3457500,
  "pension_account_credit": 630000,
  "rent_credit": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"rent.address_matches": true, "rent.homeless_household": true} |
| A_PERSONAL | {"additional": 0, "basic": 1500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 12450000, "salary_income": 41550000, "total_salary": 54000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 630000 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 4747500 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special_inco... |
| A_FINAL | 3457500 |
| A_LOCAL | 345750 |
| A_SETTLEMENT | {"local": 345750, "national": 3457500, "total": 3803250} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A172_4ccf780f/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A175_69892bbe (A_yearend, medium)

집필 제목: 두 자녀의 가족 공제 배정을 교육비 증명과 맞추기

업무 목적: 자녀별 최종 신청 배정을 지출 자료에 적용해 가족 등록을 정정한다.

가상목련모형의 가상기하은이 두 자녀 학비를 냈습니다. 가족이 정한 공제 배정과 학교 납부자료를 맞춰 기본공제액과 자녀세액공제액 및 교육비 세액공제액을 계산해 주세요. 두 아이를 모두 직원에게 등록한 임시 표는 참고하지 않습니다.

설계 의도: 두 아이 모두 직원이 학비를 냈지만 한 아이의 공제 신청은 배우자에게 배정됐다. 결제자만으로 두 아이를 모두 등록하면 세 가지 요청값이 바뀐다.

집필 원고 ID: `A175`, 전체 문항 SHA-256: `69892bbe2fadd0b5a94d715a76b33e6f73689e691060d504d489aa76ad3d6e02`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A175_69892bbe/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_154_203.json)

입력 파일:

- [01_최종가족배정.hwpx](../data/batch_1/A_yearend/B1_A175_69892bbe/inputs/01_최종가족배정.hwpx) (hwpx)
- [02_딸학교.pdf](../data/batch_1/A_yearend/B1_A175_69892bbe/inputs/02_딸학교.pdf) (pdf)
- [03_아들학교.pdf](../data/batch_1/A_yearend/B1_A175_69892bbe/inputs/03_아들학교.pdf) (pdf)
- [04_급여정산.xlsx](../data/batch_1/A_yearend/B1_A175_69892bbe/inputs/04_급여정산.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/A_yearend/B1_A175_69892bbe/gold.json)

```json
{
  "basic_deduction": 3000000,
  "child_credit": 250000,
  "education_credit": 345000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": ["daughter"]} |
| A_SALARY | {"salary_deduction": 13000000, "salary_income": 52000000, "total_salary": 65000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 345000 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 6090000 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 345000, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 4835000 |
| A_LOCAL | 483500 |
| A_SETTLEMENT | {"local": 483500, "national": 4835000, "total": 5318500} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A175_69892bbe/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A199_d607d4c0 (A_yearend, hard)

집필 제목: 짧은 재직의 카드 기간과 고액 급여 문화비 및 주택이자 마감

업무 목적: 재직 구간 안의 이자와 카드 및 진료 지출을 확인하고 문화비에 실제 신용 결제수단의 공제율을 적용한다.

가상얼레지보수의 가상길다빈은 봄에 입사해 가을에 퇴직했습니다. 카드 승인일과 진료 납부일을 재직 기록에 맞춰 구별하고 문화비의 실제 결제수단도 확인해 주세요. 신용카드 등 소득공제액과 의료비 세액공제액, 주택자금 소득공제액 및 과세표준을 계산합니다.

설계 의도: 입사 전후 카드와 퇴직 후 진료 및 이자가 같은 연간 자료에 있다. 실제 납부일이 재직 기간 안에 드는 이자만 주택 공제에 사용한다. 문화비는 신용카드로 결제했으므로 고액 급여 기준을 놓쳐 우대율을 적용하면 요청한 카드 공제액이 달라진다. 실손 지급도 해당 진료 건에 직접 연결한다.

집필 원고 ID: `A199`, 전체 문항 SHA-256: `d607d4c085a84ac9ff57fa6eb4b8410d1c5826191481b9979ea3a6218fc8f187`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A199_d607d4c0/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_154_203.json)

입력 파일:

- [01_재직확인.hwpx](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/01_재직확인.hwpx) (hwpx)
- [02_급여누계.xlsx](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/02_급여누계.xlsx) (xlsx)
- [03_대출계약.pdf](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/03_대출계약.pdf) (pdf)
- [04_세대주택.hwpx](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/04_세대주택.hwpx) (hwpx)
- [05_이자납부.pdf](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/05_이자납부.pdf) (pdf)
- [06_입사전카드.pdf](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/06_입사전카드.pdf) (pdf)
- [07_재직중카드.xlsx](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/07_재직중카드.xlsx) (xlsx)
- [08_퇴직후시장.pdf](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/08_퇴직후시장.pdf) (pdf)
- [09_재직중진료.pdf](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/09_재직중진료.pdf) (pdf)
- [10_실손지급.xlsx](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/10_실손지급.xlsx) (xlsx)
- [11_퇴직후진료.hwpx](../data/batch_1/A_yearend/B1_A199_d607d4c0/inputs/11_퇴직후진료.hwpx) (hwpx)

정답: [gold.json](../data/batch_1/A_yearend/B1_A199_d607d4c0/gold.json)

```json
{
  "credit_card_deduction": 1200000,
  "housing_income_deduction": 3600000,
  "medical_credit": 96000,
  "tax_base": 52350000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"housing_mortgage.interest_paid": 3600000, "housing_mortgage.requirements_met": true} |
| A_PERSONAL | {"additional": 0, "basic": 1500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13350000, "salary_income": 58650000, "total_salary": 72000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 3600000 |
| A_CARD | 1200000 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 96000 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 6804000 |
| A_EMPLOYMENT_CREDIT | 500000 |
| A_STANDARD | {"housing_deduction_applied": 3600000, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 96000, "political_credit": 0, "rent_credit": 0}, "sp... |
| A_FINAL | 6208000 |
| A_LOCAL | 620800 |
| A_SETTLEMENT | {"local": 620800, "national": 6208000, "total": 6828800} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A199_d607d4c0/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A237_2adf2bcb (A_yearend, medium)

집필 제목: 주택이자 증빙 제출 뒤 확정한 표준공제 신청 처리

업무 목적: 증빙 보관 여부와 최종 공제 선택을 구분해 정산한다.

가상푸른씨실 가상추도윤의 최종 신청을 반영해 주세요. 주택이자 증빙은 남아 있지만 직원이 최종적으로 표준공제를 선택했습니다. 실제 적용하는 주택자금 소득공제액과 표준세액공제 및 결정세액을 적어 주세요.

설계 의도: 대출과 연말 주택 수는 적격이지만 최종 확정 신청이 표준이다. 세금을 비교해 유리한 방식을 임의로 고르지 않고 선택된 공제를 적용해야 한다.

집필 원고 ID: `A237`, 전체 문항 SHA-256: `2adf2bcba7e2476bfc831d74ace0bcc6672778b266399d7a7fdf24a50e8ea158`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A237_2adf2bcb/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_204_253.json)

입력 파일:

- [01_이자증명.pdf](../data/batch_1/A_yearend/B1_A237_2adf2bcb/inputs/01_이자증명.pdf) (pdf)
- [02_주택조회.xlsx](../data/batch_1/A_yearend/B1_A237_2adf2bcb/inputs/02_주택조회.xlsx) (xlsx)
- [03_최종선택.hwpx](../data/batch_1/A_yearend/B1_A237_2adf2bcb/inputs/03_최종선택.hwpx) (hwpx)
- [04_연간급여.pdf](../data/batch_1/A_yearend/B1_A237_2adf2bcb/inputs/04_연간급여.pdf) (pdf)

정답: [gold.json](../data/batch_1/A_yearend/B1_A237_2adf2bcb/gold.json)

```json
{
  "final_national_tax": 7599600,
  "housing_income_deduction": 0,
  "standard_credit": 130000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"housing_mortgage.requirements_met": true} |
| A_PERSONAL | {"additional": 0, "basic": 1500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13410000, "salary_income": 59790000, "total_salary": 73200000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 12600000 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 8229600 |
| A_EMPLOYMENT_CREDIT | 500000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special_inco... |
| A_FINAL | 7599600 |
| A_LOCAL | 759960 |
| A_SETTLEMENT | {"local": 759960, "national": 7599600, "total": 8359560} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A237_2adf2bcb/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A275_23032501 (A_yearend, medium)

집필 제목: 입사 뒤 추가 납부한 봄학기 등록금의 지급일 정산

업무 목적: 같은 봄학기에 귀속된 두 등록금 지급을 실제 납부일로 나눠 중도 입사자의 교육비 신청을 마감한다.

가상달맞이건재의 가상이채온은 3월 1일 처음 취업했고 아들의 봄학기 등록금을 입사 전 선납과 입사 후 추가 납부로 나눠 냈습니다. 학기 이름 대신 실제 지급일을 재직 기간과 맞춰 교육비 세액공제액을 계산해 주세요. 가을학기 납부도 반영하고 국세 결정세액과 이미 원천징수한 국세의 정산 차액을 회신해 주세요. 환급은 음수로 적습니다.

설계 의도: 봄학기 수업은 취업 이후에도 계속되지만 입사 전 선납분이 자동으로 재직 중 지출이 되는 것은 아니다. 반대로 봄학기 추가 청구분을 입사 후에 냈으므로 그 금액을 앞선 선납과 함께 제외하면 안 된다. 직원에게 정상 배정된 한 학생의 실제 지급일이 판단 기준이다.

집필 원고 ID: `A275`, 전체 문항 SHA-256: `230325017dd8d85cfd0b2a1bb7b4c906948079b48ba90dea20f5d662c6b15fda`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A275_23032501/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_254_300.json)

입력 파일:

- [01_첫취업확인.hwpx](../data/batch_1/A_yearend/B1_A275_23032501/inputs/01_첫취업확인.hwpx) (hwpx)
- [02_봄학기선납.pdf](../data/batch_1/A_yearend/B1_A275_23032501/inputs/02_봄학기선납.pdf) (pdf)
- [03_봄학기추가청구.xlsx](../data/batch_1/A_yearend/B1_A275_23032501/inputs/03_봄학기추가청구.xlsx) (xlsx)
- [04_가을학기.pdf](../data/batch_1/A_yearend/B1_A275_23032501/inputs/04_가을학기.pdf) (pdf)
- [05_학생배정.hwpx](../data/batch_1/A_yearend/B1_A275_23032501/inputs/05_학생배정.hwpx) (hwpx)
- [06_급여원천징수.xlsx](../data/batch_1/A_yearend/B1_A275_23032501/inputs/06_급여원천징수.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/A_yearend/B1_A275_23032501/gold.json)

```json
{
  "education_credit": 1005000,
  "final_national_tax": 121500,
  "settlement_national_tax": -728500
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"education.0.excluded": false, "education.1.excluded": false, "education.2.excluded": false} |
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 10650000, "salary_income": 25350000, "total_salary": 36000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 1005000 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 2092500 |
| A_EMPLOYMENT_CREDIT | 716000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 1005000, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "specia... |
| A_FINAL | 121500 |
| A_LOCAL | 12150 |
| A_SETTLEMENT | {"local": 12150, "national": -728500, "total": -716350} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A275_23032501/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_A276_791b72e8 (A_yearend, medium)

집필 제목: 두 장애 학생의 학부 수업료와 적격 특수교육 한도 구분

업무 목적: 장애 증명이 공통인 두 가족에게 교육기관 유형별로 다른 교육비 한도를 적용한다.

가상연못조명의 가상안노을이 장애인 성년 자녀의 대학 등록금과 장애인 배우자의 적격 특수교육 납입증명을 제출했습니다. 두 사람의 장애 증명과 교육기관 유형을 연결해 교육비 세액공제액을 계산해 주세요. 본인을 포함한 기본공제 합계와 두 가족의 장애인 추가공제 합계도 각각 알려 주세요.

설계 의도: 한 사람은 일반 대학 학부생이고 다른 사람은 적격 장애인 특수교육기관 수강생이다. 두 사람 모두 장애인이지만 일반 학부 등록금에 특수교육의 무한도를 적용할 수 없다. 학생 식별기호를 따로 유지해 가족 공제의 장애인 요건과 교육비의 기관별 한도를 연결한다.

집필 원고 ID: `A276`, 전체 문항 SHA-256: `791b72e8baca77fed291e12a6272bfd0a8ba09aad3fcb468bbfcfb4f1be0fcea`

[문항 메타데이터](../data/batch_1/A_yearend/B1_A276_791b72e8/task.yaml)와 [집필 원고](../authored/batch_1/A_yearend/cases_254_300.json)

입력 파일:

- [01_가족장애등록.hwpx](../data/batch_1/A_yearend/B1_A276_791b72e8/inputs/01_가족장애등록.hwpx) (hwpx)
- [02_자녀학부납입.pdf](../data/batch_1/A_yearend/B1_A276_791b72e8/inputs/02_자녀학부납입.pdf) (pdf)
- [03_배우자특수교육.pdf](../data/batch_1/A_yearend/B1_A276_791b72e8/inputs/03_배우자특수교육.pdf) (pdf)
- [04_급여.xlsx](../data/batch_1/A_yearend/B1_A276_791b72e8/inputs/04_급여.xlsx) (xlsx)
- [05_교육비접수.hwpx](../data/batch_1/A_yearend/B1_A276_791b72e8/inputs/05_교육비접수.hwpx) (hwpx)

정답: [gold.json](../data/batch_1/A_yearend/B1_A276_791b72e8/gold.json)

```json
{
  "additional_deduction": 4000000,
  "basic_deduction": 4500000,
  "education_credit": 3030000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"education.0.excluded": false, "education.1.excluded": false} |
| A_PERSONAL | {"additional": 4000000, "basic": 4500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13840000, "salary_income": 67960000, "total_salary": 81800000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 3030000 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 8510400 |
| A_EMPLOYMENT_CREDIT | 500000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 3030000, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "specia... |
| A_FINAL | 4730400 |
| A_LOCAL | 473040 |
| A_SETTLEMENT | {"local": 473040, "national": 4730400, "total": 5203440} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/A_yearend/B1_A276_791b72e8/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B018_d2077988 (B_payroll, easy)

집필 제목: 급여 외주사의 지급 항목 합계 검산

업무 목적: 급여 자료를 넘기기 전에 항목 합계와 이체액 대조 값을 마련한다.

가상새벽로봇의 가상장온유 명세서를 외주 급여 담당자에게 넘기기 전에 합계를 검산합니다. 기본급과 직무수당 및 식대가 각 칸에 들어가도록 항목 금액을 확인하고 총지급액을 구해 주세요. 외주사 대조 값으로 통상임금과 실지급액도 함께 작성해 주세요.

설계 의도: 지급 항목별 출력과 통상임금 및 실지급액을 함께 요구하는 전사 검산이다. 지급 수당과 공제액의 서로 다른 단계가 중심이다.

집필 원고 ID: `B018`, 전체 문항 SHA-256: `d207798881ddd4ce4b9faa15025a7d24cb1c40b4b12c942befd7c22696e1b659`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B018_d2077988/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_004_053.json)

입력 파일:

- [01_외주전달급여.hwpx](../data/batch_1/B_payroll/B1_B018_d2077988/inputs/01_외주전달급여.hwpx) (hwpx)
- [02_외주전달마감.xlsx](../data/batch_1/B_payroll/B1_B018_d2077988/inputs/02_외주전달마감.xlsx) (xlsx)
- [03_외주검산기준.pdf](../data/batch_1/B_payroll/B1_B018_d2077988/inputs/03_외주검산기준.pdf) (pdf)

정답: [gold.json](../data/batch_1/B_payroll/B1_B018_d2077988/gold.json)

```json
{
  "base_pay": 2890000,
  "fixed_allowance": 266000,
  "gross_pay": 3300000,
  "meal_allowance": 144000,
  "net_pay": 2917630,
  "ordinary_monthly_wage": 3300000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.ORDINARY | {"hourly_exact_denominator": 19, "hourly_exact_numerator": 300000, "ordinary_monthly_wage": 3300000} |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 505264, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 144000 |
| B.GROSS | {"gross_pay": 3300000, "taxable_pay": 3156000} |
| B.PENSION | {"national_pension": 149910, "pension_base_income": 3156000} |
| B.HEALTH | 113450 |
| B.LONG_TERM_CARE | 14900 |
| B.EMPLOYMENT | 28400 |
| B.TAX_TABLE | 68830 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 68830 |
| B.LOCAL_TAX | 6880 |
| B.NET | 2917630 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B018_d2077988/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B098_2b8ead83 (B_payroll, hard)

집필 제목: 고령 신규 채용의 고액 산식 경계와 선택 신청

업무 목적: 확정 고령 신규 자격과 고액 원천세 경계 및 선택 비율을 한 명세서에 적용한다.

가상늘품실험실의 고령 신규 채용 직원에게 당월 고액 정액을 지급합니다. 기관별 부과 통지에서 국민연금과 고용보험을 확인하고 건강보험 및 장기요양을 계산해 주세요. 두 자녀 공제 후120% 신청을 적용한 소득세와 지방소득세 및 실지급액도 필요합니다. 과세급여의4500만원 경계는 첨부 공식 산식을 사용합니다.

설계 의도: 신규 채용의 기관 부과 상태는 확정 입력이며 이전 계속 가입으로 가정하지 않는다. 과세급여가 정확히4500만원이므로 이하 산식 끝점을 적용한 뒤 두 자녀와 선택 비율을 처리한다.

집필 원고 ID: `B098`, 전체 문항 SHA-256: `2b8ead83b142ef78694269c29a3c6609a109ab4f171a02df072f553e9d7220bc`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B098_2b8ead83/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_054_103.json)

입력 파일:

- [01_고령신규약정.pdf](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/01_고령신규약정.pdf) (pdf)
- [02_신규식대.hwpx](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/02_신규식대.hwpx) (hwpx)
- [03_신규연금.pdf](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/03_신규연금.pdf) (pdf)
- [04_신규건강.xlsx](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/04_신규건강.xlsx) (xlsx)
- [05_신규고용.hwpx](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/05_신규고용.hwpx) (hwpx)
- [06_신규가족.pdf](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/06_신규가족.pdf) (pdf)
- [07_신규선택.hwpx](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/07_신규선택.hwpx) (hwpx)
- [08_신규정상월.xlsx](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/08_신규정상월.xlsx) (xlsx)
- [09_4500경계참조.pdf](../data/batch_1/B_payroll/B1_B098_2b8ead83/inputs/09_4500경계참조.pdf) (pdf)

정답: [gold.json](../data/batch_1/B_payroll/B1_B098_2b8ead83/gold.json)

```json
{
  "employment_insurance": 0,
  "health_insurance": 1617750,
  "income_tax": 17423530,
  "local_income_tax": 1742350,
  "long_term_care": 212580,
  "national_pension": 0,
  "net_pay": 24203790,
  "taxable_pay": 45000000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 0, "payment_date": "2026-10-23", "qualifying_weeks": 0, "regular_minutes": 10080} |
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 45200000, "ordinary_monthly_wage": 45200000} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 200000 |
| B.GROSS | {"gross_pay": 45200000, "taxable_pay": 45000000} |
| B.PENSION | {"national_pension": 0, "pension_base_income": 6590000} |
| B.HEALTH | 1617750 |
| B.LONG_TERM_CARE | 212580 |
| B.EMPLOYMENT | 0 |
| B.TAX_TABLE | 14565440 |
| B.CHILD_CREDIT | 45830 |
| B.WITHHOLDING | 17423530 |
| B.LOCAL_TAX | 1742350 |
| B.NET | 24203790 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B098_2b8ead83/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B104_e95a88ed (B_payroll, easy)

집필 제목: 통상임금 마스터와 당월 실적 지급 분리

업무 목적: 당월 실적 지급을 통상임금 마스터와 원천세 급여란에 서로 맞는 범위로 기록한다.

가상나루기록사는 정액 계약의 통상임금 마스터와 4월 원천세 급여란을 따로 갱신합니다. 계약의 소정근로 대가와 당월 판매량에 따라 확정된 비정기 실적 수당을 구분해 통상 월 임금과 표시 시급을 작성해 주세요. 지급 총액, 비과세 식대 및 간이세액표용 과세급여도 구합니다.

설계 의도: 정액 소정근로 대가는 통상임금에 포함하며 이번 달 실적에 따라 발생한 별도 수당은 과세 지급에만 합산한다. 식대는 통상임금에 포함하면서 비과세 한도로 구분한다.

집필 원고 ID: `B104`, 전체 문항 SHA-256: `e95a88ed30405ef5282e5bbbd060b8569a4d86152f97a27dfb0b610c37f7a6a5`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B104_e95a88ed/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_104_153.json)

입력 파일:

- [01_채무발생.pdf](../data/batch_1/B_payroll/B1_B104_e95a88ed/inputs/01_채무발생.pdf) (pdf)
- [02_4월실적.xlsx](../data/batch_1/B_payroll/B1_B104_e95a88ed/inputs/02_4월실적.xlsx) (xlsx)
- [03_전표범위.hwpx](../data/batch_1/B_payroll/B1_B104_e95a88ed/inputs/03_전표범위.hwpx) (hwpx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B104_e95a88ed/gold.json)

```json
{
  "gross_pay": 3525000,
  "non_taxable_pay": 150000,
  "ordinary_hourly_wage_floor": 16267,
  "ordinary_monthly_wage": 3400000,
  "taxable_pay": 3375000,
  "variable_allowance": 125000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 3400000, "ordinary_monthly_wage": 3400000} |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 150000 |
| B.GROSS | {"gross_pay": 3525000, "taxable_pay": 3375000} |
| B.PENSION | {"national_pension": 154370, "pension_base_income": 3250000} |
| B.HEALTH | 116830 |
| B.LONG_TERM_CARE | 15350 |
| B.EMPLOYMENT | 29250 |
| B.TAX_TABLE | 87650 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 87650 |
| B.LOCAL_TAX | 8760 |
| B.NET | 3112790 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B104_e95a88ed/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B139_cff507e0 (B_payroll, medium)

집필 제목: 마감 직전 당월 실적금 추가로 달라진 세액표 행

업무 목적: 마감 직전 추가된 당월 실적금을 과세 행에 반영하면서 통상임금 기준은 구별한다.

가상살구교정실은 급여 계약 등록 후 당월 교정 성과금을 별도 승인했습니다. 성과금은 통상임금 기준에 포함하지 않는 당월 실적 대가입니다. 월 통상임금과 최종 과세급여를 구하고, 성과금을 누락한 이전 행 대신 사용할 소득세와 지방소득세를 계산해 주세요.

설계 의도: 성과금이 작아도 과세급여 행 선택에 영향을 줄 수 있다. 정액 통상임금에 더하는 오류와 세액표 행을 유지하는 오류를 각각 드러낸다.

집필 원고 ID: `B139`, 전체 문항 SHA-256: `cff507e0139cdb0d93ba8ff049174dba181e0ac627ba9fc0570cabd760d41358`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B139_cff507e0/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_104_153.json)

입력 파일:

- [01_살구정액.pdf](../data/batch_1/B_payroll/B1_B139_cff507e0/inputs/01_살구정액.pdf) (pdf)
- [02_당월성과.hwpx](../data/batch_1/B_payroll/B1_B139_cff507e0/inputs/02_당월성과.hwpx) (hwpx)
- [03_살구공단.xlsx](../data/batch_1/B_payroll/B1_B139_cff507e0/inputs/03_살구공단.xlsx) (xlsx)
- [04_살구범위.pdf](../data/batch_1/B_payroll/B1_B139_cff507e0/inputs/04_살구범위.pdf) (pdf)
- [05_행이동참조.xlsx](../data/batch_1/B_payroll/B1_B139_cff507e0/inputs/05_행이동참조.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B139_cff507e0/gold.json)

```json
{
  "income_tax": 74350,
  "local_income_tax": 7430,
  "ordinary_monthly_wage": 3198000,
  "taxable_pay": 3010000,
  "variable_allowance": 12000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 3198000, "ordinary_monthly_wage": 3198000} |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 200000 |
| B.GROSS | {"gross_pay": 3210000, "taxable_pay": 3010000} |
| B.PENSION | {"national_pension": 142400, "pension_base_income": 2998000} |
| B.HEALTH | 107770 |
| B.LONG_TERM_CARE | 14160 |
| B.EMPLOYMENT | 26980 |
| B.TAX_TABLE | 74350 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 74350 |
| B.LOCAL_TAX | 7430 |
| B.NET | 2836910 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B139_cff507e0/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B174_1408d21c (B_payroll, medium)

집필 제목: 두 짧은 야간 수당의 월합계 원 단수 정산

업무 목적: 여러 카드의 동일 수당을 월 단위로 합산한 뒤 정산한다.

가상행간편집실은 서로 다른 두 평일의 짧은 추가 작업을 승인했습니다. 정확한 통상시급을 유지하여 두 작업의 월 연장수당과 야간 가산 및 총지급액을 구해 주세요. 카드마다 원 단위를 먼저 올리지 않습니다. 원 미만을 버린 표시 통상시급도 적어 주세요.

설계 의도: 두 카드에서 발생한 소수 원을 먼저 올리면 월 수당 합계가 달라진다. 표시 시급과 지급용 정확한 시급도 구분한다.

집필 원고 ID: `B174`, 전체 문항 SHA-256: `1408d21cef140e8d605d6cf228309a00e8e3df9cbfd31641efb0ed4084583c4d`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B174_1408d21c/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_154_203.json)

입력 파일:

- [01_행간단가.pdf](../data/batch_1/B_payroll/B1_B174_1408d21c/inputs/01_행간단가.pdf) (pdf)
- [02_첫날카드.hwpx](../data/batch_1/B_payroll/B1_B174_1408d21c/inputs/02_첫날카드.hwpx) (hwpx)
- [03_둘째카드.xlsx](../data/batch_1/B_payroll/B1_B174_1408d21c/inputs/03_둘째카드.xlsx) (xlsx)
- [04_행간마감.pdf](../data/batch_1/B_payroll/B1_B174_1408d21c/inputs/04_행간마감.pdf) (pdf)

정답: [gold.json](../data/batch_1/B_payroll/B1_B174_1408d21c/gold.json)

```json
{
  "gross_pay": 3222299,
  "night_pay": 4340,
  "ordinary_hourly_wage_floor": 15316,
  "overtime_pay": 16848
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 34, "overtime_minutes": 44, "paid_holiday_minutes": 0, "payment_date": "2026-08-25", "qualifying_weeks": 0, "regular_minutes": 10080} |
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 3201111, "ordinary_monthly_wage": 3201111} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 16848 |
| B.NIGHT | 4340 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 180000 |
| B.GROSS | {"gross_pay": 3222299, "taxable_pay": 3042299} |
| B.PENSION | {"national_pension": 143490, "pension_base_income": 3021000} |
| B.HEALTH | 108600 |
| B.LONG_TERM_CARE | 14270 |
| B.EMPLOYMENT | 27180 |
| B.TAX_TABLE | 77770 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 77770 |
| B.LOCAL_TAX | 7770 |
| B.NET | 2843219 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B174_1408d21c/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B200_e12b9a23 (B_payroll, hard)

집필 제목: 야간 휴게 수정과 실행 뒤 미지급 계획 및 120퍼센트

업무 목적: 근로 승인과 지급 실행 및 선택 원천세의 서로 다른 권위를 연결한다.

가상쐐기검사실은 야간 추가 카드의 휴게 수정과 실제 은행 실행 뒤 작성된 후속 계획을 받았습니다. 유효 승인 시간으로 연장수당과 야간 가산을 계산하고 실제 지급일의 자녀 공제 뒤 120퍼센트 신청을 적용하여 세금과 실지급액을 산정해 주세요.

설계 의도: 수정 휴게는 실제 야간분을 줄이고 후속 미실행 계획은 실제 지급월을 바꾸지 못한다. 120퍼센트 선택은 자녀 공제 뒤 양수 세액에 적용된다.

집필 원고 ID: `B200`, 전체 문항 SHA-256: `e12b9a23096220713f11e2ffcc06b6864d87b8a29a86193a9caafb2a7536a57c`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B200_e12b9a23/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_154_203.json)

입력 파일:

- [01_쐐기계약.pdf](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/01_쐐기계약.pdf) (pdf)
- [02_추가이전.hwpx](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/02_추가이전.hwpx) (hwpx)
- [03_추가수정.xlsx](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/03_추가수정.xlsx) (xlsx)
- [04_쐐기일정.pdf](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/04_쐐기일정.pdf) (pdf)
- [05_2월실행.hwpx](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/05_2월실행.hwpx) (hwpx)
- [06_후속승인.xlsx](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/06_후속승인.xlsx) (xlsx)
- [07_쐐기선택.pdf](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/07_쐐기선택.pdf) (pdf)
- [08_쐐기기관.hwpx](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/08_쐐기기관.hwpx) (hwpx)
- [09_쐐기공식.pdf](../data/batch_1/B_payroll/B1_B200_e12b9a23/inputs/09_쐐기공식.pdf) (pdf)

정답: [gold.json](../data/batch_1/B_payroll/B1_B200_e12b9a23/gold.json)

```json
{
  "income_tax": 319950,
  "local_income_tax": 31990,
  "net_pay": 4671947,
  "night_pay": 12919,
  "overtime_pay": 116268,
  "total_deductions": 857240
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 60, "overtime_minutes": 180, "paid_holiday_minutes": 0, "payment_date": "2026-02-26", "qualifying_weeks": 0, "regular_minutes": 9600} |
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 5400000, "ordinary_monthly_wage": 5400000} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 116268 |
| B.NIGHT | 12919 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 200000 |
| B.GROSS | {"gross_pay": 5529187, "taxable_pay": 5329187} |
| B.PENSION | {"national_pension": 247000, "pension_base_income": 5200000} |
| B.HEALTH | 186940 |
| B.LONG_TERM_CARE | 24560 |
| B.EMPLOYMENT | 46800 |
| B.TAX_TABLE | 279130 |
| B.CHILD_CREDIT | 12500 |
| B.WITHHOLDING | 319950 |
| B.LOCAL_TAX | 31990 |
| B.NET | 4671947 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B200_e12b9a23/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B207_da3dd7d5 (B_payroll, easy)

집필 제목: 세 소정일로 끝난 안내 계약의 임금과 주휴 정리

업무 목적: 소정일 세 번의 근로 임금과 주휴를 종료 확인서의 서로 다른 칸에 기록한다.

가상색인안내소의 일주일 계약은 월요일부터 수요일까지 하루 여섯 시간입니다. 세 날을 모두 출근한 직원의 기본 근로 대가와 추가 주휴수당을 구하고 총지급액을 계약 종료 확인란에 적어 주세요.

설계 의도: 주 18시간을 하루 여섯 시간의 세 출근일과 연결하고 주휴는 통상 주40시간 계약에 비례한다.

집필 원고 ID: `B207`, 전체 문항 SHA-256: `da3dd7d5da0889634fed6f81953ae734bd28f9d43bee937b605cf66f0cf2049f`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B207_da3dd7d5/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_204_253.json)

입력 파일:

- [01_한주계약.hwpx](../data/batch_1/B_payroll/B1_B207_da3dd7d5/inputs/01_한주계약.hwpx) (hwpx)
- [02_종료주출근.xlsx](../data/batch_1/B_payroll/B1_B207_da3dd7d5/inputs/02_종료주출근.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B207_da3dd7d5/gold.json)

```json
{
  "base_pay": 230400,
  "gross_pay": 276480,
  "weekly_holiday_pay": 46080
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 0, "payment_date": "2026-11-09", "qualifying_weeks": 1, "regular_minutes": 1080} |
| B.ORDINARY | {"hourly_exact_denominator": 1, "hourly_exact_numerator": 12800, "ordinary_monthly_wage": 0} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 46080, "weekly_holiday_pay": 46080} |
| B.MEAL_EXEMPT | 0 |
| B.GROSS | {"gross_pay": 276480, "taxable_pay": 276480} |
| B.PENSION | {"national_pension": 40370, "pension_base_income": 850000} |
| B.HEALTH | 30550 |
| B.LONG_TERM_CARE | 4010 |
| B.EMPLOYMENT | 7650 |
| B.TAX_TABLE | 0 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 0 |
| B.LOCAL_TAX | 0 |
| B.NET | 193900 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B207_da3dd7d5/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B221_b64a33be (B_payroll, medium)

집필 제목: 건강 미부과 통지와 요양 연결 칸을 함께 확인

업무 목적: 한 기관의 미부과 사실을 연결 공제와 전체 급여 공제에 반영한다.

가상리본회람실의 건강보험 통지는 이번 부과가 없다고 적혀 있습니다. 건강보험과 장기요양보험 칸을 작성하고 다른 기관 및 세금을 포함한 총공제와 실지급액을 확인해 주세요.

설계 의도: 건강 고지 보수 숫자가 남아 있어도 미부과 통지가 우선이며 그 부담액을 기초로 하는 장기요양도 함께 계산한다.

집필 원고 ID: `B221`, 전체 문항 SHA-256: `b64a33be46ac2de6b9454fe6f58d94826d851f35e0f3ba25fe4c668258460f61`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B221_b64a33be/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_204_253.json)

입력 파일:

- [01_정액지급.pdf](../data/batch_1/B_payroll/B1_B221_b64a33be/inputs/01_정액지급.pdf) (pdf)
- [02_건강확인.hwpx](../data/batch_1/B_payroll/B1_B221_b64a33be/inputs/02_건강확인.hwpx) (hwpx)
- [03_다른기관.xlsx](../data/batch_1/B_payroll/B1_B221_b64a33be/inputs/03_다른기관.xlsx) (xlsx)
- [04_공제규정.xlsx](../data/batch_1/B_payroll/B1_B221_b64a33be/inputs/04_공제규정.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B221_b64a33be/gold.json)

```json
{
  "health_insurance": 0,
  "long_term_care": 0,
  "net_pay": 3068420,
  "total_deductions": 281580
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 3350000, "ordinary_monthly_wage": 3350000} |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 150000 |
| B.GROSS | {"gross_pay": 3350000, "taxable_pay": 3200000} |
| B.PENSION | {"national_pension": 152000, "pension_base_income": 3200000} |
| B.HEALTH | 0 |
| B.LONG_TERM_CARE | 0 |
| B.EMPLOYMENT | 28980 |
| B.TAX_TABLE | 91460 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 91460 |
| B.LOCAL_TAX | 9140 |
| B.NET | 3068420 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B221_b64a33be/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B231_0980b834 (B_payroll, medium)

집필 제목: 자녀 공제 후 선택 원천세로 바뀐 납부 금액

업무 목적: 선택 원천징수 신청을 세무 납부액과 직원 지급액에 반영한다.

가상대장검인실의 직원은 원천징수 120퍼센트를 신청했습니다. 승인 가족과 자녀를 반영하여 소득세 및 지방소득세를 계산하고 총공제액과 실지급액을 작성해 주세요.

설계 의도: 공식 표 세액에 비율을 먼저 곱하는 대신 적격 자녀 공제 후 신청 비율을 적용한다.

집필 원고 ID: `B231`, 전체 문항 SHA-256: `0980b834fe5cf4dd18574b0eae1e4871ee0dde404f7ddb7a83884f89b566583d`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B231_0980b834/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_204_253.json)

입력 파일:

- [01_원천세신청.hwpx](../data/batch_1/B_payroll/B1_B231_0980b834/inputs/01_원천세신청.hwpx) (hwpx)
- [02_정액지급.pdf](../data/batch_1/B_payroll/B1_B231_0980b834/inputs/02_정액지급.pdf) (pdf)
- [03_기관기초.xlsx](../data/batch_1/B_payroll/B1_B231_0980b834/inputs/03_기관기초.xlsx) (xlsx)
- [04_선택원문.xlsx](../data/batch_1/B_payroll/B1_B231_0980b834/inputs/04_선택원문.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B231_0980b834/gold.json)

```json
{
  "income_tax": 223400,
  "local_income_tax": 22340,
  "net_pay": 4555650,
  "total_deductions": 744350
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 5300000, "ordinary_monthly_wage": 5300000} |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 200000 |
| B.GROSS | {"gross_pay": 5300000, "taxable_pay": 5100000} |
| B.PENSION | {"national_pension": 242250, "pension_base_income": 5100000} |
| B.HEALTH | 185860 |
| B.LONG_TERM_CARE | 24420 |
| B.EMPLOYMENT | 46080 |
| B.TAX_TABLE | 232000 |
| B.CHILD_CREDIT | 45830 |
| B.WITHHOLDING | 223400 |
| B.LOCAL_TAX | 22340 |
| B.NET | 4555650 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B231_0980b834/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B239_a4869a01 (B_payroll, medium)

집필 제목: 7월 실행과 6월 보험 고지의 낮은 연금 기초 구분

업무 목적: 은행 실행일과 보험 부과월을 분리하여 낮은 연금 고지의 적용 값을 등록한다.

가상서식점검소의 6월 보험 고지를 7월 초 급여에서 공제했습니다. 실행 기록으로 지급일을 확인하고, 보험 통지의 부과월에 맞춰 연금 기준소득월액과 근로자 부담을 계산해 주세요.

설계 의도: 실제 지급일은 답의 날짜를 확정하고 6월 고지월은 보험 하한을 결정한다. 두 날짜의 용도를 섞으면 연금 공제가 달라진다.

집필 원고 ID: `B239`, 전체 문항 SHA-256: `a4869a01dd53dc04040e3b861a605c7afa9a3bcb37b8ca990b3611707c82cc6a`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B239_a4869a01/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_204_253.json)

입력 파일:

- [01_지급약정.hwpx](../data/batch_1/B_payroll/B1_B239_a4869a01/inputs/01_지급약정.hwpx) (hwpx)
- [02_7월실행.xlsx](../data/batch_1/B_payroll/B1_B239_a4869a01/inputs/02_7월실행.xlsx) (xlsx)
- [03_6월보험.pdf](../data/batch_1/B_payroll/B1_B239_a4869a01/inputs/03_6월보험.pdf) (pdf)
- [04_반기원문.xlsx](../data/batch_1/B_payroll/B1_B239_a4869a01/inputs/04_반기원문.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B239_a4869a01/gold.json)

```json
{
  "effective_payment_date": "2026-07-02",
  "national_pension": 19000,
  "pension_base_income": 400000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 0, "payment_date": "2026-07-02", "qualifying_weeks": 0, "regular_minutes": 0} |
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 2570000, "ordinary_monthly_wage": 2570000} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 170000 |
| B.GROSS | {"gross_pay": 2570000, "taxable_pay": 2400000} |
| B.PENSION | {"national_pension": 19000, "pension_base_income": 400000} |
| B.HEALTH | 89150 |
| B.LONG_TERM_CARE | 11710 |
| B.EMPLOYMENT | 21780 |
| B.TAX_TABLE | 32380 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 32380 |
| B.LOCAL_TAX | 3230 |
| B.NET | 2392750 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B239_a4869a01/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B242_780a90b2 (B_payroll, hard)

집필 제목: 어린이날 야간 수정 카드와 별도 유급 대가의 시급 마감

업무 목적: 공휴일의 기본 유급 대가와 실제 야간 근로 대가를 한 시급 지급서의 별도 항목으로 확정한다.

가상흰색문서실은 어린이날 야간 작업의 휴게와 종료를 수정 승인했습니다. 소정일 출근과 최종 승인 카드를 대조하여 기본 근로 대가, 유급휴일 대가와 주휴수당을 따로 구해 주세요. 실제 휴일근로 수당과 야간 가산을 더한 총지급액도 작성해 주세요.

설계 의도: 공휴일 유급 대가는 실제 출동 유무와 다른 자료에서 나오고 최종 카드의 하루 실제 근로는 8시간을 넘는다. 카드 수정은 휴일과 야간 두 수당에 함께 작용한다.

집필 원고 ID: `B242`, 전체 문항 SHA-256: `780a90b27981ec60209434800cf5926a426fd147527e54e746ac4bf25a38c897`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B242_780a90b2/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_204_253.json)

입력 파일:

- [01_종료약정.pdf](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/01_종료약정.pdf) (pdf)
- [02_소정출근.xlsx](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/02_소정출근.xlsx) (xlsx)
- [03_유급기초.hwpx](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/03_유급기초.hwpx) (hwpx)
- [04_초기출동.pdf](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/04_초기출동.pdf) (pdf)
- [05_수정출동.xlsx](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/05_수정출동.xlsx) (xlsx)
- [06_은행실행.hwpx](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/06_은행실행.hwpx) (hwpx)
- [07_연금통지.pdf](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/07_연금통지.pdf) (pdf)
- [08_다른공제.xlsx](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/08_다른공제.xlsx) (xlsx)
- [09_원문기준.xlsx](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/09_원문기준.xlsx) (xlsx)
- [10_초기출동스캔.png](../data/batch_1/B_payroll/B1_B242_780a90b2/inputs/10_초기출동스캔.png) (png)

정답: [gold.json](../data/batch_1/B_payroll/B1_B242_780a90b2/gold.json)

```json
{
  "base_pay": 235200,
  "gross_pay": 610050,
  "holiday_pay": 205800,
  "night_pay": 51450,
  "paid_holiday_pay": 58800,
  "weekly_holiday_pay": 58800
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [{"holiday_night_minutes": 420, "minutes": 540}], "night_minutes": 420, "overtime_minutes": 0, "paid_holiday_minutes": 240, "payment_date": "2026-05-11", "qualifying_weeks": ... |
| B.ORDINARY | {"hourly_exact_denominator": 1, "hourly_exact_numerator": 14700, "ordinary_monthly_wage": 0} |
| B.PAID_HOLIDAY | 58800 |
| B.OVERTIME | 0 |
| B.NIGHT | 51450 |
| B.HOLIDAY | 205800 |
| B.WEEKLY | {"weekly_holiday_entitlement": 58800, "weekly_holiday_pay": 58800} |
| B.MEAL_EXEMPT | 0 |
| B.GROSS | {"gross_pay": 610050, "taxable_pay": 610050} |
| B.PENSION | {"national_pension": 57950, "pension_base_income": 1220000} |
| B.HEALTH | 44930 |
| B.LONG_TERM_CARE | 5900 |
| B.EMPLOYMENT | 11160 |
| B.TAX_TABLE | 0 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 0 |
| B.LOCAL_TAX | 0 |
| B.NET | 490110 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B242_780a90b2/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B270_d51dfbdd (B_payroll, medium)

집필 제목: 7월 지급대장과 6월 저소득 연금 고지를 따로 등록

업무 목적: 늦은 지급대장의 은행 날짜와 보험 고지 기준월을 각각 등록한다.

가상둥근표지관은 6월 보험 공제를 7월에 실행한 종료 임금에서 보관합니다. 은행 날짜를 effective_payment_date에 YYYY-MM-DD로 적고 고지 부과월에 맞는 연금 기준소득과 국민연금 공제액을 작성해 주세요.

설계 의도: 연금 하한은 공단 부과월에 따르며 은행 실행월의 하한으로 바꾸지 않는다.

집필 원고 ID: `B270`, 전체 문항 SHA-256: `d51dfbdd4ba37e72b30a1181bf7fc9fc02c248acd94d65ced13573a3ed8c52c9`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B270_d51dfbdd/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_254_300.json)

입력 파일:

- [01_종료임금.pdf](../data/batch_1/B_payroll/B1_B270_d51dfbdd/inputs/01_종료임금.pdf) (pdf)
- [02_육월연금.xlsx](../data/batch_1/B_payroll/B1_B270_d51dfbdd/inputs/02_육월연금.xlsx) (xlsx)
- [03_칠월실행.hwpx](../data/batch_1/B_payroll/B1_B270_d51dfbdd/inputs/03_칠월실행.hwpx) (hwpx)
- [04_다른기관.xlsx](../data/batch_1/B_payroll/B1_B270_d51dfbdd/inputs/04_다른기관.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B270_d51dfbdd/gold.json)

```json
{
  "effective_payment_date": "2026-07-03",
  "national_pension": 19000,
  "pension_base_income": 400000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 0, "payment_date": "2026-07-03", "qualifying_weeks": 0, "regular_minutes": 0} |
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 2690000, "ordinary_monthly_wage": 2690000} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 150000 |
| B.GROSS | {"gross_pay": 2690000, "taxable_pay": 2540000} |
| B.PENSION | {"national_pension": 19000, "pension_base_income": 400000} |
| B.HEALTH | 92750 |
| B.LONG_TERM_CARE | 12180 |
| B.EMPLOYMENT | 22860 |
| B.TAX_TABLE | 36970 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 36970 |
| B.LOCAL_TAX | 3690 |
| B.NET | 2502550 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B270_d51dfbdd/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B271_2c76f3e1 (B_payroll, medium)

집필 제목: 3월 계획보다 앞선 2월 실행을 가족 원천세에 연결

업무 목적: 실제 지급분의 가족 세액을 계획서와 혼동하지 않고 등록한다.

가상매듭기록실에는 3월 지급 계획과 이미 완료한 2월 은행 실행이 함께 남았습니다. 실제 지급일을 effective_payment_date에 YYYY-MM-DD로 적고 두 자녀 등록 직원의 소득세와 지방소득세를 계산해 주세요.

설계 의도: 실행 상태가 있는 날짜를 선택하면 3월 개정 자녀 공제 기준을 앞당겨 적용하지 않게 된다.

집필 원고 ID: `B271`, 전체 문항 SHA-256: `2c76f3e1e45c9002e9da349fa340b76fd60348238720cba22511f544b11e8994`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B271_2c76f3e1/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_254_300.json)

입력 파일:

- [01_정액계약.pdf](../data/batch_1/B_payroll/B1_B271_2c76f3e1/inputs/01_정액계약.pdf) (pdf)
- [02_지급기록.xlsx](../data/batch_1/B_payroll/B1_B271_2c76f3e1/inputs/02_지급기록.xlsx) (xlsx)
- [03_가족인계.hwpx](../data/batch_1/B_payroll/B1_B271_2c76f3e1/inputs/03_가족인계.hwpx) (hwpx)
- [04_기관및표.xlsx](../data/batch_1/B_payroll/B1_B271_2c76f3e1/inputs/04_기관및표.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B271_2c76f3e1/gold.json)

```json
{
  "effective_payment_date": "2026-02-27",
  "income_tax": 169300,
  "local_income_tax": 16930
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 0, "payment_date": "2026-02-27", "qualifying_weeks": 0, "regular_minutes": 0} |
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 5050000, "ordinary_monthly_wage": 5050000} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 200000 |
| B.GROSS | {"gross_pay": 5050000, "taxable_pay": 4850000} |
| B.PENSION | {"national_pension": 230370, "pension_base_income": 4850000} |
| B.HEALTH | 181540 |
| B.LONG_TERM_CARE | 23850 |
| B.EMPLOYMENT | 44010 |
| B.TAX_TABLE | 198460 |
| B.CHILD_CREDIT | 29160 |
| B.WITHHOLDING | 169300 |
| B.LOCAL_TAX | 16930 |
| B.NET | 4384000 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B271_2c76f3e1/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B285_cdbc88ce (B_payroll, medium)

집필 제목: 주10시간 세 명 사업장의 근로자의 날 유급 대가

업무 목적: 짧은 계약의 근로자의 날 유급 지급을 일반 공휴일 및 주휴 요건과 구분한다.

가상짧은분류실의 시급 직원은 주10시간 근무하고 근로자의 날에는 쉬었습니다. 실제 네 소정일의 기본 대가와 근로자의 날 유급액을 따로 계산해 주세요. 주휴수당과 총지급액도 작성해 주세요.

설계 의도: 근로자의 날 유급 대가는 사업장 인원이나 주15시간 미만 여부로 없어지지 않는다.

집필 원고 ID: `B285`, 전체 문항 SHA-256: `cdbc88ce956eeec95e516f19575847a1dbaec93d840a163778b71638d05e968c`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B285_cdbc88ce/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_254_300.json)

입력 파일:

- [01_짧은계약.hwpx](../data/batch_1/B_payroll/B1_B285_cdbc88ce/inputs/01_짧은계약.hwpx) (hwpx)
- [02_네날출근.xlsx](../data/batch_1/B_payroll/B1_B285_cdbc88ce/inputs/02_네날출근.xlsx) (xlsx)
- [03_근로자의날.pdf](../data/batch_1/B_payroll/B1_B285_cdbc88ce/inputs/03_근로자의날.pdf) (pdf)
- [04_유급공제원문.xlsx](../data/batch_1/B_payroll/B1_B285_cdbc88ce/inputs/04_유급공제원문.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/B_payroll/B1_B285_cdbc88ce/gold.json)

```json
{
  "base_pay": 131200,
  "gross_pay": 164000,
  "paid_holiday_pay": 32800,
  "weekly_holiday_pay": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 120, "payment_date": "2026-05-04", "qualifying_weeks": 1, "regular_minutes": 480} |
| B.ORDINARY | {"hourly_exact_denominator": 1, "hourly_exact_numerator": 16400, "ordinary_monthly_wage": 0} |
| B.PAID_HOLIDAY | 32800 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 0 |
| B.GROSS | {"gross_pay": 164000, "taxable_pay": 164000} |
| B.PENSION | {"national_pension": 23750, "pension_base_income": 500000} |
| B.HEALTH | 18330 |
| B.LONG_TERM_CARE | 2400 |
| B.EMPLOYMENT | 4410 |
| B.TAX_TABLE | 0 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 0 |
| B.LOCAL_TAX | 0 |
| B.NET | 115110 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B285_cdbc88ce/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_B294_b5c05250 (B_payroll, hard)

집필 제목: 공휴일 카드를 소정에서 추가로 정정한 긴 야간 시급 지급

업무 목적: 공휴일 소정 유급과 잘못 분류한 실제 작업을 정리한 시급 전표를 승인한다.

가상닫힌표본국의 어린이날 작업 카드는 소정으로 잘못 적었다가 추가 근로로 다시 승인됐습니다. 실제 소정 기본 대가와 공휴일 유급액 및 주휴수당을 구해 주세요. 최종 승인된 긴 휴일 작업의 수당과 야간 가산 및 총지급액도 작성해 주세요.

설계 의도: 공휴일에 쉰 소정시간은 유급 기본 대가이고 오후 추가 작업은 별도다. 정정된 카드의 긴 실제 근로는 하루 8시간을 넘으며 휴게가 야간 경계에 걸친다.

집필 원고 ID: `B294`, 전체 문항 SHA-256: `b5c052504c98bed246a916e41399f9a81b9adca5ca7849b1fe7e7f2732726c0e`

[문항 메타데이터](../data/batch_1/B_payroll/B1_B294_b5c05250/task.yaml)와 [집필 원고](../authored/batch_1/B_payroll/cases_254_300.json)

입력 파일:

- [01_표본국계약.pdf](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/01_표본국계약.pdf) (pdf)
- [02_실제소정.xlsx](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/02_실제소정.xlsx) (xlsx)
- [03_휴일기초.hwpx](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/03_휴일기초.hwpx) (hwpx)
- [04_주별개근.pdf](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/04_주별개근.pdf) (pdf)
- [05_구분초기.pdf](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/05_구분초기.pdf) (pdf)
- [06_구분최종.hwpx](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/06_구분최종.hwpx) (hwpx)
- [07_지급실행.pdf](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/07_지급실행.pdf) (pdf)
- [08_기관세무.xlsx](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/08_기관세무.xlsx) (xlsx)
- [09_공휴일원문.xlsx](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/09_공휴일원문.xlsx) (xlsx)
- [10_초기카드스캔.png](../data/batch_1/B_payroll/B1_B294_b5c05250/inputs/10_초기카드스캔.png) (png)

정답: [gold.json](../data/batch_1/B_payroll/B1_B294_b5c05250/gold.json)

```json
{
  "base_pay": 234400,
  "gross_pay": 584169,
  "holiday_pay": 205100,
  "night_pay": 27469,
  "paid_holiday_pay": 58600,
  "weekly_holiday_pay": 58600
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [{"holiday_night_minutes": 225, "minutes": 540}], "night_minutes": 225, "overtime_minutes": 0, "paid_holiday_minutes": 240, "payment_date": "2026-05-11", "qualifying_weeks": ... |
| B.ORDINARY | {"hourly_exact_denominator": 1, "hourly_exact_numerator": 14650, "ordinary_monthly_wage": 0} |
| B.PAID_HOLIDAY | 58600 |
| B.OVERTIME | 0 |
| B.NIGHT | 27469 |
| B.HOLIDAY | 205100 |
| B.WEEKLY | {"weekly_holiday_entitlement": 58600, "weekly_holiday_pay": 58600} |
| B.MEAL_EXEMPT | 0 |
| B.GROSS | {"gross_pay": 584169, "taxable_pay": 584169} |
| B.PENSION | {"national_pension": 82170, "pension_base_income": 1730000} |
| B.HEALTH | 62910 |
| B.LONG_TERM_CARE | 8260 |
| B.EMPLOYMENT | 15390 |
| B.TAX_TABLE | 0 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 0 |
| B.LOCAL_TAX | 0 |
| B.NET | 415439 |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/B_payroll/B1_B294_b5c05250/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C047_3db3cd8d (C_vat, hard)

집필 제목: 임대 차량과 대표 차량을 함께 산 렌트업

업무 목적: 같은 사업자가 구입한 승용차라도 실제 투입 용도에 따라 신고를 구별한다.

가상열린렌트는 고객 임대용 차량과 대표 이동용 차량을 같은 달에 샀습니다. 등록 분류와 차량 배치 기록을 연결해 매입세액(input_vat), 공제불가 세액(noncreditable_vat), 공제가능 매입세액(deductible_input_vat)을 구분해 주세요. 임대 매출과 납부한 예정고지 세액(prepaid_vat)을 반영한 순세액(net_vat) 및 환급액(refund_vat)을 answer.json에 정수로 작성해 주세요.

설계 의도: 두 차량 모두 개별소비세 대상이지만 한 대는 임대 영업에 직접 투입되고 다른 한 대는 대표 이동에 쓴다. 큰 임대 차량 매입으로 생긴 환급에 선납까지 반영해야 한다.

집필 원고 ID: `C047`, 전체 문항 SHA-256: `3db3cd8dca55892e60f304ec1aeeee85eeb1bab1a91e7e7b9d0a7fac4a7d6123`

[문항 메타데이터](../data/batch_1/C_vat/B1_C047_3db3cd8d/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_004_053.json)

입력 파일:

- [01_렌트법인_의뢰.hwpx](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/01_렌트법인_의뢰.hwpx) (hwpx)
- [02_전년_신고.pdf](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/02_전년_신고.pdf) (pdf)
- [03_예정고지_납부.xlsx](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/03_예정고지_납부.xlsx) (xlsx)
- [04_임대_용역.pdf](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/04_임대_용역.pdf) (pdf)
- [05_배차용_차량.pdf](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/05_배차용_차량.pdf) (pdf)
- [06_대표_차량.xlsx](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/06_대표_차량.xlsx) (xlsx)
- [07_배차_정비.pdf](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/07_배차_정비.pdf) (pdf)
- [08_차량배치_기록.hwpx](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/08_차량배치_기록.hwpx) (hwpx)
- [09_배차차량_사진.png](../data/batch_1/C_vat/B1_C047_3db3cd8d/inputs/09_배차차량_사진.png) (png)

정답: [gold.json](../data/batch_1/C_vat/B1_C047_3db3cd8d/gold.json)

```json
{
  "deductible_input_vat": 3090000,
  "input_vat": 5290000,
  "net_vat": -2530000,
  "noncreditable_vat": 2200000,
  "prepaid_vat": 740000,
  "refund_vat": 2530000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "가상-C047-임대차수취", "purpose": "passenger_car_purchase", "transaction_id": "가상-C047-임대차구입"}, {"business_related": true, "document_id": "가상-C047-이동차수취", "purpose": "passenger_car_purchase"... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 24200000, "supply_base": 22000000, "vat": 2200000} |
| VAT_PASSENGER_CAR | {"deductible": 0, "noncreditable": 2200000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 14300000, "supply_base": 13000000, "vat": 1300000} |
| VAT_OUTPUT_10 | 1300000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 33000000, "supply_base": 30000000, "vat": 3000000} |
| VAT_INPUT_EVIDENCE | {"deductible": 3000000, "noncreditable": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 990000, "supply_base": 900000, "vat": 90000} |
| VAT_INPUT_EVIDENCE | {"deductible": 90000, "noncreditable": 0} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -2530000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 3090000, "input_vat": 5290000, "net_vat": -2530000, "noncreditable_vat": 2200000, "output_vat": 1300000, "payable_vat": 0, "prepaid_vat": 740000, "receipt_credit": 0, "refund_vat": 2530000, "tax_base": ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C047_3db3cd8d/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C097_3c25b6ef (C_vat, hard)

집필 제목: 취소된 고객 방문과 가족 가게의 장비 수령

업무 목적: 계획 단계 문서와 실제 사용 문서를 대조하여 환급 자금을 확정한다.

가상조립방은 고객 방문 계획과 가족 가게의 구매 대금을 한 경리 파일에 넣었습니다. 실제 식사 참석자와 별도 사업자의 장비 수령을 확인하세요. 전체 매입세액(input_vat), 불공제 세액(noncreditable_vat), 공제가능 매입세액(deductible_input_vat), 발행세액공제(receipt_credit), 환급액(refund_vat)을 answer.json에 정수로 적어 주세요.

설계 의도: 초청했던 고객은 오지 않았고 실제 식사는 직원뿐이다. 대표가 대신 결제한 장비는 가족의 다른 사업자가 사용하며 정상 재고 매입은 별도로 커서 환급 상태에서 발행 공제를 더할 수 없다.

집필 원고 ID: `C097`, 전체 문항 SHA-256: `3c25b6ef1c997279d1840054cf0b380cd754fc079a6279eaba205f33eaa504d2`

[문항 메타데이터](../data/batch_1/C_vat/B1_C097_3c25b6ef/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_054_103.json)

입력 파일:

- [01_조립방_사업.hwpx](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/01_조립방_사업.hwpx) (hwpx)
- [02_영업과_선납.xlsx](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/02_영업과_선납.xlsx) (xlsx)
- [03_소품판매_카드.pdf](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/03_소품판매_카드.pdf) (pdf)
- [04_방문예정일_점심.xlsx](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/04_방문예정일_점심.xlsx) (xlsx)
- [05_고객방문_취소.hwpx](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/05_고객방문_취소.hwpx) (hwpx)
- [06_실제_직원식사.pdf](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/06_실제_직원식사.pdf) (pdf)
- [07_가족장비_계산서.xlsx](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/07_가족장비_계산서.xlsx) (xlsx)
- [08_가족가게_장비인수.hwpx](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/08_가족가게_장비인수.hwpx) (hwpx)
- [09_정상판매재고_입고.pdf](../data/batch_1/C_vat/B1_C097_3c25b6ef/inputs/09_정상판매재고_입고.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C097_3c25b6ef/gold.json)

```json
{
  "deductible_input_vat": 510000,
  "input_vat": 710000,
  "noncreditable_vat": 200000,
  "receipt_credit": 0,
  "refund_vat": 760000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "C097-식사카드", "purpose": "business", "transaction_id": "C097-점심"}, {"business_related": false, "document_id": "C097-장비계산서", "purpose": "private", "transaction_id": "C097-가족장비"}, {"busin... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 2200000, "supply_base": 2000000, "vat": 200000} |
| VAT_NONBUSINESS | {"deductible": 0, "noncreditable": 200000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 5500000, "supply_base": 5000000, "vat": 500000} |
| VAT_OUTPUT_10 | 500000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 5500000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 220000, "supply_base": 200000, "vat": 20000} |
| VAT_INPUT_EVIDENCE | {"deductible": 20000, "noncreditable": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 5390000, "supply_base": 4900000, "vat": 490000} |
| VAT_INPUT_EVIDENCE | {"deductible": 490000, "noncreditable": 0} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 71500 |
| VAT_CREDIT_ANNUAL_LIMIT | 71500 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -760000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 510000, "input_vat": 710000, "net_vat": -760000, "noncreditable_vat": 200000, "output_vat": 500000, "payable_vat": 0, "prepaid_vat": 750000, "receipt_credit": 0, "refund_vat": 760000, "tax_base": 500000... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C097_3c25b6ef/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C110_42bcd645 (C_vat, easy)

집필 제목: 출장 세탁 서비스의 노선별 수금

업무 목적: 노선별 수금 봉투를 하나의 사업장 신고에 합친다.

가상주말세탁의 출장 노선 기록으로 공급가액(tax_base), 발행 공제(receipt_credit), 거래 수(unique_transaction_count)를 answer.json으로 정리해 주세요.

설계 의도: 노선 운행 횟수와 개별 손님 공급은 다르다. 세 손님의 완료 세탁과 현금영수증을 한 사업장의 발행 공제로 연결한다.

집필 원고 ID: `C110`, 전체 문항 SHA-256: `42bcd64517fd2d036f6fef915d597283be9cb72fd2b34b8e70d8804436f636e4`

[문항 메타데이터](../data/batch_1/C_vat/B1_C110_42bcd645/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_104_153.json)

입력 파일:

- [01_노선봉투.hwpx](../data/batch_1/C_vat/B1_C110_42bcd645/inputs/01_노선봉투.hwpx) (hwpx)
- [02_손님별영수증.xlsx](../data/batch_1/C_vat/B1_C110_42bcd645/inputs/02_손님별영수증.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/C_vat/B1_C110_42bcd645/gold.json)

```json
{
  "receipt_credit": 5005,
  "tax_base": 350000,
  "unique_transaction_count": 3
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 88000, "supply_base": 80000, "vat": 8000} |
| VAT_OUTPUT_10 | 8000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 88000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 121000, "supply_base": 110000, "vat": 11000} |
| VAT_OUTPUT_10 | 11000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 121000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 176000, "supply_base": 160000, "vat": 16000} |
| VAT_OUTPUT_10 | 16000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 176000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 5005 |
| VAT_CREDIT_ANNUAL_LIMIT | 5005 |
| VAT_CREDIT_PAYABLE_LIMIT | 5005 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 29995 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 29995, "noncreditable_vat": 0, "output_vat": 35000, "payable_vat": 29995, "prepaid_vat": 0, "receipt_credit": 5005, "refund_vat": 0, "tax_base": 350000, "unique_transaction... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C110_42bcd645/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C176_3d869234 (C_vat, medium)

집필 제목: 예정신고 후 남은 발행 공제의 연간 몫

업무 목적: 올해 이미 청구한 공제를 제외한 연간 잔여를 적용한다.

가상가방장식의 앞선 신고와 이번 발행 자료를 확인해 매출세액(output_vat), 발행 공제(receipt_credit), 납부액(payable_vat)을 answer.json에 적어 주세요.

설계 의도: 이번 발행 대금의 계산액은 연간 잔여보다 크다. 앞선 신고의 매출을 다시 합산하거나 앞선 납부액을 이번 세금에서 한 번 더 빼지 않는다.

집필 원고 ID: `C176`, 전체 문항 SHA-256: `3d8692341fe26e1be597b5038fd75554a19c5af492195cbe9cf2855e2b8f059d`

[문항 메타데이터](../data/batch_1/C_vat/B1_C176_3d869234/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_154_203.json)

입력 파일:

- [확정인계.hwpx](../data/batch_1/C_vat/B1_C176_3d869234/inputs/확정인계.hwpx) (hwpx)
- [예정접수.pdf](../data/batch_1/C_vat/B1_C176_3d869234/inputs/예정접수.pdf) (pdf)
- [카드공급.xlsx](../data/batch_1/C_vat/B1_C176_3d869234/inputs/카드공급.xlsx) (xlsx)
- [현금공급.pdf](../data/batch_1/C_vat/B1_C176_3d869234/inputs/현금공급.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C176_3d869234/gold.json)

```json
{
  "output_vat": 2000000,
  "payable_vat": 1780000,
  "receipt_credit": 220000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 15400000, "supply_base": 14000000, "vat": 1400000} |
| VAT_OUTPUT_10 | 1400000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 15400000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 6600000, "supply_base": 6000000, "vat": 600000} |
| VAT_OUTPUT_10 | 600000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 6600000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 286000 |
| VAT_CREDIT_ANNUAL_LIMIT | 220000 |
| VAT_CREDIT_PAYABLE_LIMIT | 220000 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 1780000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 1780000, "noncreditable_vat": 0, "output_vat": 2000000, "payable_vat": 1780000, "prepaid_vat": 0, "receipt_credit": 220000, "refund_vat": 0, "tax_base": 20000000, "unique_t... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C176_3d869234/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C182_146906fd (C_vat, medium)

집필 제목: 허가 대여 차량을 다른 사업 직원 이동에 사용한 달

업무 목적: 대여 허가 차량이라도 실제 비용이 귀속된 업무를 확인한다.

가상겸업이동의 차량 등록과 실제 사용 업무를 연결하여 불공제세액(noncreditable_vat), 공제 매입세액(deductible_input_vat), 순세액(net_vat)을 answer.json에 적어 주세요.

설계 의도: 차량의 허가 업무는 대여업이지만 해당 정비 기간의 사용 기록은 별도 과세 장치 설치업의 직원 이동이다. 허가 유무만 보지 않고 permitted_operation_id와 실제 operation_id를 맞춘다.

집필 원고 ID: `C182`, 전체 문항 SHA-256: `146906fd0d7b6d079d283785d1732010199a44b00abd789e18b3d5ed78399e54`

[문항 메타데이터](../data/batch_1/C_vat/B1_C182_146906fd/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_154_203.json)

입력 파일:

- [겸업인계.hwpx](../data/batch_1/C_vat/B1_C182_146906fd/inputs/겸업인계.hwpx) (hwpx)
- [대여등록.pdf](../data/batch_1/C_vat/B1_C182_146906fd/inputs/대여등록.pdf) (pdf)
- [사용일지.xlsx](../data/batch_1/C_vat/B1_C182_146906fd/inputs/사용일지.xlsx) (xlsx)
- [차량정비.pdf](../data/batch_1/C_vat/B1_C182_146906fd/inputs/차량정비.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C182_146906fd/gold.json)

```json
{
  "deductible_input_vat": 0,
  "net_vat": 0,
  "noncreditable_vat": 76000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "정비카드", "purpose": "passenger_car_maintenance", "transaction_id": "C182-정비"}, {"transaction_id": "C182-정비", "vehicle_direct_business": false, "vehicle_id": "가상-R182", "vehicle_subject_... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 836000, "supply_base": 760000, "vat": 76000} |
| VAT_PASSENGER_CAR | {"deductible": 0, "noncreditable": 76000} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 0 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 76000, "net_vat": 0, "noncreditable_vat": 76000, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 0, "unique_transaction_count": 1} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C182_146906fd/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C186_7c4704f4 (C_vat, medium)

집필 제목: 사업자 고객이 산 소매점 진열 바구니

업무 목적: 소비자 상대 소매업의 사업자 고객 카드 판매를 정리한다.

가상바구니소매의 고객별 카드 공급에서 공급가액(tax_base), 발행 공제(receipt_credit), 납부액(payable_vat)을 answer.json에 적어 주세요.

설계 의도: 이번 고객은 모두 사업자이나 사업장은 소비자 상대 소매업이라는 확정 사실이 있다. 개별 고객의 유형과 업종 자격을 혼동하지 않고 계산서 없는 카드 발행을 확인한다.

집필 원고 ID: `C186`, 전체 문항 SHA-256: `7c4704f4146806788afd451461b0f17fec974f881d23b0f1fa86e4038a9ce116`

[문항 메타데이터](../data/batch_1/C_vat/B1_C186_7c4704f4/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_154_203.json)

입력 파일:

- [소매업정보.hwpx](../data/batch_1/C_vat/B1_C186_7c4704f4/inputs/소매업정보.hwpx) (hwpx)
- [식당공급.pdf](../data/batch_1/C_vat/B1_C186_7c4704f4/inputs/식당공급.pdf) (pdf)
- [꽃집공급.xlsx](../data/batch_1/C_vat/B1_C186_7c4704f4/inputs/꽃집공급.xlsx) (xlsx)
- [서점공급.pdf](../data/batch_1/C_vat/B1_C186_7c4704f4/inputs/서점공급.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C186_7c4704f4/gold.json)

```json
{
  "payable_vat": 282810,
  "receipt_credit": 47190,
  "tax_base": 3300000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1210000, "supply_base": 1100000, "vat": 110000} |
| VAT_OUTPUT_10 | 110000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 1210000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 880000, "supply_base": 800000, "vat": 80000} |
| VAT_OUTPUT_10 | 80000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 880000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1540000, "supply_base": 1400000, "vat": 140000} |
| VAT_OUTPUT_10 | 140000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 1540000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 47190 |
| VAT_CREDIT_ANNUAL_LIMIT | 47190 |
| VAT_CREDIT_PAYABLE_LIMIT | 47190 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 282810 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 282810, "noncreditable_vat": 0, "output_vat": 330000, "payable_vat": 282810, "prepaid_vat": 0, "receipt_credit": 47190, "refund_vat": 0, "tax_base": 3300000, "unique_transa... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C186_7c4704f4/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C200_1640423d (C_vat, hard)

집필 제목: 대여 등록 전후 정비를 마친 작은 카드 매출

업무 목적: 등록 시점별 정비 공제와 잔여 납부세액 제한을 함께 적용한다.

가상초봄대여의 차량 기간별 등록과 정비 및 카드 공급을 연결해 불공제세액(noncreditable_vat), 공제 매입세액(deductible_input_vat), 발행 공제(receipt_credit), 순세액(net_vat)을 answer.json에 적어 주세요.

설계 의도: 세 정비는 같은 차량에 대한 것이나 첫 정비는 영업 등록 전이다. 이후 두 정비를 공제하면 남은 세금보다 카드 발행 공제 계산액이 커진다.

집필 원고 ID: `C200`, 전체 문항 SHA-256: `1640423d4bc4151630171cb7e14a8e9c8289fb48def251a580523ee63065a170`

[문항 메타데이터](../data/batch_1/C_vat/B1_C200_1640423d/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_154_203.json)

입력 파일:

- [대여신고.hwpx](../data/batch_1/C_vat/B1_C200_1640423d/inputs/대여신고.hwpx) (hwpx)
- [대여허가.xlsx](../data/batch_1/C_vat/B1_C200_1640423d/inputs/대여허가.xlsx) (xlsx)
- [등록기간.pdf](../data/batch_1/C_vat/B1_C200_1640423d/inputs/등록기간.pdf) (pdf)
- [겨울완료.hwpx](../data/batch_1/C_vat/B1_C200_1640423d/inputs/겨울완료.hwpx) (hwpx)
- [봄완료.hwpx](../data/batch_1/C_vat/B1_C200_1640423d/inputs/봄완료.hwpx) (hwpx)
- [여름완료.xlsx](../data/batch_1/C_vat/B1_C200_1640423d/inputs/여름완료.xlsx) (xlsx)
- [겨울전표.pdf](../data/batch_1/C_vat/B1_C200_1640423d/inputs/겨울전표.pdf) (pdf)
- [봄전표.pdf](../data/batch_1/C_vat/B1_C200_1640423d/inputs/봄전표.pdf) (pdf)
- [여름전표.pdf](../data/batch_1/C_vat/B1_C200_1640423d/inputs/여름전표.pdf) (pdf)
- [대여공급.xlsx](../data/batch_1/C_vat/B1_C200_1640423d/inputs/대여공급.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/C_vat/B1_C200_1640423d/gold.json)

```json
{
  "deductible_input_vat": 80000,
  "net_vat": 0,
  "noncreditable_vat": 20000,
  "receipt_credit": 10000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "겨울카드", "purpose": "passenger_car_maintenance", "transaction_id": "C200-겨울정비"}, {"business_related": true, "document_id": "봄카드", "purpose": "passenger_car_maintenance", "transaction_id... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 220000, "supply_base": 200000, "vat": 20000} |
| VAT_PASSENGER_CAR | {"deductible": 0, "noncreditable": 20000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 990000, "supply_base": 900000, "vat": 90000} |
| VAT_OUTPUT_10 | 90000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 990000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 220000, "supply_base": 200000, "vat": 20000} |
| VAT_INPUT_EVIDENCE | {"deductible": 20000, "noncreditable": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 660000, "supply_base": 600000, "vat": 60000} |
| VAT_INPUT_EVIDENCE | {"deductible": 60000, "noncreditable": 0} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 12870 |
| VAT_CREDIT_ANNUAL_LIMIT | 12870 |
| VAT_CREDIT_PAYABLE_LIMIT | 10000 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 0 |
| VAT_SETTLEMENT | {"deductible_input_vat": 80000, "input_vat": 100000, "net_vat": 0, "noncreditable_vat": 20000, "output_vat": 90000, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 10000, "refund_vat": 0, "tax_base": 900000, "unique_trans... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C200_1640423d/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C211_9bd9166f (C_vat, easy)

집필 제목: 조경용 표지대 판매의 두 인도 장소

업무 목적: 서로 다른 고객에게 완료한 표지대 공급을 합친다.

가상초록표지의 두 납품 자료에서 공급가액(tax_base)과 거래 수(unique_transaction_count)를 answer.json에 적어 주세요.

설계 의도: 같은 품목이지만 인도 장소와 주문 번호가 서로 다르다. 한 공급은 총액이며 다른 공급은 세액 별도 금액이다.

집필 원고 ID: `C211`, 전체 문항 SHA-256: `9bd9166fc2ab6846f6d0e359e068b02caaf1724e7930f88a7aac148ffb7963b6`

[문항 메타데이터](../data/batch_1/C_vat/B1_C211_9bd9166f/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_204_253.json)

입력 파일:

- [인도인계.pdf](../data/batch_1/C_vat/B1_C211_9bd9166f/inputs/인도인계.pdf) (pdf)
- [납품발급.xlsx](../data/batch_1/C_vat/B1_C211_9bd9166f/inputs/납품발급.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/C_vat/B1_C211_9bd9166f/gold.json)

```json
{
  "tax_base": 1650000,
  "unique_transaction_count": 2
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1012000, "supply_base": 920000, "vat": 92000} |
| VAT_OUTPUT_10 | 92000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 803000, "supply_base": 730000, "vat": 73000} |
| VAT_OUTPUT_10 | 73000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 0} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 165000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 165000, "noncreditable_vat": 0, "output_vat": 165000, "payable_vat": 165000, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 1650000, "unique_transactio... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C211_9bd9166f/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C222_c585f22b (C_vat, medium)

집필 제목: 기술 시연 당일 고객과의 저녁

업무 목적: 고객 동석 식사의 매입 신고 여부를 정리한다.

가상시연테이블의 시연 뒤 식사 자료에서 매입세액(input_vat), 불공제세액(noncreditable_vat), 순세액(net_vat)을 answer.json에 적어 주세요.

설계 의도: 회사 직원 명의 카드라도 실제 참석 명부에 외부 구매 고객이 있다. 시연 장치 업무와 연결하되 식사 상대를 따로 확인한다.

집필 원고 ID: `C222`, 전체 문항 SHA-256: `c585f22b90778530cada154add1a020ebbf59e532abce6ec160ece44ffd4adf3`

[문항 메타데이터](../data/batch_1/C_vat/B1_C222_c585f22b/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_204_253.json)

입력 파일:

- [시연업무.hwpx](../data/batch_1/C_vat/B1_C222_c585f22b/inputs/시연업무.hwpx) (hwpx)
- [행사배정.xlsx](../data/batch_1/C_vat/B1_C222_c585f22b/inputs/행사배정.xlsx) (xlsx)
- [저녁명부.hwpx](../data/batch_1/C_vat/B1_C222_c585f22b/inputs/저녁명부.hwpx) (hwpx)
- [식사승인.pdf](../data/batch_1/C_vat/B1_C222_c585f22b/inputs/식사승인.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C222_c585f22b/gold.json)

```json
{
  "input_vat": 41000,
  "net_vat": 0,
  "noncreditable_vat": 41000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "저녁카드9", "purpose": "hospitality", "transaction_id": "시연식사9"}] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 451000, "supply_base": 410000, "vat": 41000} |
| VAT_HOSPITALITY | {"deductible": 0, "noncreditable": 41000} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 0 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 41000, "net_vat": 0, "noncreditable_vat": 41000, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 0, "unique_transaction_count": 1} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C222_c585f22b/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C237_654707d0 (C_vat, medium)

집필 제목: 이미 한도를 쓴 마당 조명점의 추가 판매

업무 목적: 연간 한도가 소진된 사업장의 추가 발급을 정산한다.

가상밤마당의 기신고 공제와 추가 판매로 매출세액(output_vat), 발행 공제(receipt_credit), 납부액(payable_vat)을 answer.json에 써 주세요.

설계 의도: 1분기에 이미 1000만원을 실제 공제했으며 추가 판매는 별도로 남았다. 발행 영수증 금액이 생겨도 연간 남은 한도는 0원이다.

집필 원고 ID: `C237`, 전체 문항 SHA-256: `654707d0477a3cdce13c94a75e1bf28d3e0330c7847eefa1b0d2f5660117f76e`

[문항 메타데이터](../data/batch_1/C_vat/B1_C237_654707d0/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_204_253.json)

입력 파일:

- [조명점범위.pdf](../data/batch_1/C_vat/B1_C237_654707d0/inputs/조명점범위.pdf) (pdf)
- [예정신고.hwpx](../data/batch_1/C_vat/B1_C237_654707d0/inputs/예정신고.hwpx) (hwpx)
- [납부구분.xlsx](../data/batch_1/C_vat/B1_C237_654707d0/inputs/납부구분.xlsx) (xlsx)
- [추가발급.pdf](../data/batch_1/C_vat/B1_C237_654707d0/inputs/추가발급.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C237_654707d0/gold.json)

```json
{
  "output_vat": 540000,
  "payable_vat": 540000,
  "receipt_credit": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 5940000, "supply_base": 5400000, "vat": 540000} |
| VAT_OUTPUT_10 | 540000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 5940000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 77220 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 540000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 540000, "noncreditable_vat": 0, "output_vat": 540000, "payable_vat": 540000, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 5400000, "unique_transactio... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C237_654707d0/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C245_94d75e9d (C_vat, hard)

집필 제목: 유효기간이 다른 포장상 구매와 토지 배수 정리

업무 목적: 공급일별 공급자 자격과 토지 자체 작업을 분리해 신고한다.

가상상자뜨락의 공급자 이력과 작업 지번으로 매입세액(input_vat), 공제 매입세액(deductible_input_vat), 불공제세액(noncreditable_vat), 환급액(refund_vat)을 answer.json에 적어 주세요.

설계 의도: 종이 포장 구매 두 건 사이에 공급자가 일반과세자로 전환했다. 별도 토지 자체 배수 정리는 공급자 자격이 충분해도 그 사용 성격으로 판단한다.

집필 원고 ID: `C245`, 전체 문항 SHA-256: `94d75e9d15d072a2a6bcb42c908285f1309b6ec94d762eb33e68a4f153298f73`

[문항 메타데이터](../data/batch_1/C_vat/B1_C245_94d75e9d/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_204_253.json)

입력 파일:

- [뜨락신고.hwpx](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/뜨락신고.hwpx) (hwpx)
- [제작업무.pdf](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/제작업무.pdf) (pdf)
- [공급기간.xlsx](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/공급기간.xlsx) (xlsx)
- [이월반입.hwpx](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/이월반입.hwpx) (hwpx)
- [삼월반입.xlsx](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/삼월반입.xlsx) (xlsx)
- [배수작업.hwpx](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/배수작업.hwpx) (hwpx)
- [이월결제.pdf](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/이월결제.pdf) (pdf)
- [삼월결제.pdf](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/삼월결제.pdf) (pdf)
- [배수발급.pdf](../data/batch_1/C_vat/B1_C245_94d75e9d/inputs/배수발급.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C245_94d75e9d/gold.json)

```json
{
  "deductible_input_vat": 175000,
  "input_vat": 625000,
  "noncreditable_vat": 450000,
  "refund_vat": 175000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "종이카드이월", "purpose": "business", "transaction_id": "종이이월인수"}, {"business_related": true, "document_id": "종이카드삼월", "purpose": "business", "transaction_id": "종이삼월인수"}, {"business_related... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 3520000, "supply_base": 3200000, "vat": 320000} |
| VAT_EXEMPT_LAND | {"deductible": 0, "noncreditable": 320000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1925000, "supply_base": 1750000, "vat": 175000} |
| VAT_INPUT_EVIDENCE | {"deductible": 175000, "noncreditable": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1430000, "supply_base": 1300000, "vat": 130000} |
| VAT_INPUT_EVIDENCE | {"deductible": 0, "noncreditable": 130000} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -175000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 175000, "input_vat": 625000, "net_vat": -175000, "noncreditable_vat": 450000, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 175000, "tax_base": 0, "unique_trans... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C245_94d75e9d/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C250_3afddb27 (C_vat, hard)

집필 제목: 법인 명판 매장의 카드 매출과 직원 급식

업무 목적: 법인 소매 매출의 공제 자격과 서로 다른 매입의 사용을 정리한다.

가상문패법인의 사업자 유형, 식사 수령, 차량 자료를 모아 발행 공제(receipt_credit), 공제 매입세액(deductible_input_vat), 불공제세액(noncreditable_vat), 납부액(payable_vat)을 answer.json에 적어 주세요.

설계 의도: 소매 단말기 매출이 있어도 공급자는 법인이다. 직원 급식과 관리 승용차 수리에는 실제 참가자 및 등록증을 각기 연결한다.

집필 원고 ID: `C250`, 전체 문항 SHA-256: `3afddb272c78efa2a6ca4ad929d7f73cc67e27bc1e01150fb14174727c78dba6`

[문항 메타데이터](../data/batch_1/C_vat/B1_C250_3afddb27/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_204_253.json)

입력 파일:

- [명판신고.hwpx](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/명판신고.hwpx) (hwpx)
- [법인등록.pdf](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/법인등록.pdf) (pdf)
- [명판업무.xlsx](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/명판업무.xlsx) (xlsx)
- [관리차등록.pdf](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/관리차등록.pdf) (pdf)
- [급식수령.hwpx](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/급식수령.hwpx) (hwpx)
- [차량작업.xlsx](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/차량작업.xlsx) (xlsx)
- [명판판매.pdf](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/명판판매.pdf) (pdf)
- [급식발급.pdf](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/급식발급.pdf) (pdf)
- [정비결제.pdf](../data/batch_1/C_vat/B1_C250_3afddb27/inputs/정비결제.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C250_3afddb27/gold.json)

```json
{
  "deductible_input_vat": 64000,
  "noncreditable_vat": 96000,
  "payable_vat": 786000,
  "receipt_credit": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "급식전자", "purpose": "business", "transaction_id": "명판급식주문"}, {"business_related": true, "document_id": "관리차카드", "purpose": "passenger_car_maintenance", "transaction_id": "문패관리차정비"}, {"t... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 704000, "supply_base": 640000, "vat": 64000} |
| VAT_INPUT_EVIDENCE | {"deductible": 64000, "noncreditable": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 9350000, "supply_base": 8500000, "vat": 850000} |
| VAT_OUTPUT_10 | 850000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 9350000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1056000, "supply_base": 960000, "vat": 96000} |
| VAT_PASSENGER_CAR | {"deductible": 0, "noncreditable": 96000} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 786000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 64000, "input_vat": 160000, "net_vat": 786000, "noncreditable_vat": 96000, "output_vat": 850000, "payable_vat": 786000, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 8500000, "uniq... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C250_3afddb27/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C274_fd46adc1 (C_vat, medium)

집필 제목: 훈련용 교재점의 면세 강의 전용 음료

업무 목적: 직원용 지출이어도 직접 면세 업무에 쓰인 비용을 구별한다.

가상교구줄의 직원 음료 영수증과 부서 사용 기록을 보고 불공제세액(noncreditable_vat), 공제 매입세액(deductible_input_vat)을 answer.json에 남겨 주세요.

설계 의도: 사업자는 과세 교구 판매와 별도 면세 강의를 한다. 음료는 면세 강의실 직원 전용으로 사용했고 공통 지출이 아니다. 직원 복지라는 표현만으로 과세사업 공제로 판단하지 않는다.

집필 원고 ID: `C274`, 전체 문항 SHA-256: `fd46adc154b227fcd29b5ee7e1df9079f77dbc7e10b55591508dfdf7ea2ef885`

[문항 메타데이터](../data/batch_1/C_vat/B1_C274_fd46adc1/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_254_300.json)

입력 파일:

- [부서사업.hwpx](../data/batch_1/C_vat/B1_C274_fd46adc1/inputs/부서사업.hwpx) (hwpx)
- [음료사용.xlsx](../data/batch_1/C_vat/B1_C274_fd46adc1/inputs/음료사용.xlsx) (xlsx)
- [음료전표.pdf](../data/batch_1/C_vat/B1_C274_fd46adc1/inputs/음료전표.pdf) (pdf)
- [검토범위.pdf](../data/batch_1/C_vat/B1_C274_fd46adc1/inputs/검토범위.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C274_fd46adc1/gold.json)

```json
{
  "deductible_input_vat": 0,
  "noncreditable_vat": 29000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "음료카드", "purpose": "exempt_business", "transaction_id": "음료-274"}] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 319000, "supply_base": 290000, "vat": 29000} |
| VAT_EXEMPT_LAND | {"deductible": 0, "noncreditable": 29000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 0 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 29000, "net_vat": 0, "noncreditable_vat": 29000, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 0, "unique_transaction_count": 1} |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C274_fd46adc1/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C279_8ac60ecd (C_vat, medium)

집필 제목: 영수증 발행 정산을 법인 명의로 확정한 잠금점

업무 목적: 소비자 카드 판매가 있는 법인의 발행 공제 자격을 검토한다.

가상잠금주머니의 사업 형태 확인서와 카드 판매를 보고 발행 공제(receipt_credit), 납부세액(payable_vat)을 answer.json에 기록해 주세요.

설계 의도: 작은 소비자 점포여도 신고 사업자는 법인이다. 대표 개인의 규모가 아닌 사업 형태 확인서의 신고 주체를 적용한다.

집필 원고 ID: `C279`, 전체 문항 SHA-256: `8ac60ecda7099f41544d805e3f97b93eb52c0d48c159a56b0a769d82f3e489d9`

[문항 메타데이터](../data/batch_1/C_vat/B1_C279_8ac60ecd/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_254_300.json)

입력 파일:

- [사업형태.pdf](../data/batch_1/C_vat/B1_C279_8ac60ecd/inputs/사업형태.pdf) (pdf)
- [단말판매.xlsx](../data/batch_1/C_vat/B1_C279_8ac60ecd/inputs/단말판매.xlsx) (xlsx)
- [소비자업종.hwpx](../data/batch_1/C_vat/B1_C279_8ac60ecd/inputs/소비자업종.hwpx) (hwpx)
- [신고조건.pdf](../data/batch_1/C_vat/B1_C279_8ac60ecd/inputs/신고조건.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C279_8ac60ecd/gold.json)

```json
{
  "payable_vat": 480000,
  "receipt_credit": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 5280000, "supply_base": 4800000, "vat": 480000} |
| VAT_OUTPUT_10 | 480000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 5280000} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 480000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 480000, "noncreditable_vat": 0, "output_vat": 480000, "payable_vat": 480000, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 4800000, "unique_transactio... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C279_8ac60ecd/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_C299_5615dbc2 (C_vat, hard)

집필 제목: 옛 지점 파일을 받은 매장의 공급자 조회와 고지 잔액

업무 목적: 지점 자격 오류와 공급자 자격 오류를 고친 뒤 유효 고지 잔액을 계산한다.

가상유리받침의 신고 지점 전년 자료와 재고 공급자 조회를 확인해서 발행 공제(receipt_credit), 불공제세액(noncreditable_vat), 선납세액(prepaid_vat), 환급세액(refund_vat)을 answer.json에 적어 주세요.

설계 의도: 신고 지점은 전년 10억원 이하인데 인계 파일 첫 행의 다른 지점은 초과한다. 재고 영수증 공급자는 발급 의무 없는 간이과세자라 공제되지 않는다. 유효 고지 실제 납부액은 마지막에 차감한다.

집필 원고 ID: `C299`, 전체 문항 SHA-256: `5615dbc2489dc6f0553704d8351bf32831e35e67037597b31dbbe815ccf9f985`

[문항 메타데이터](../data/batch_1/C_vat/B1_C299_5615dbc2/task.yaml)와 [집필 원고](../authored/batch_1/C_vat/cases_254_300.json)

입력 파일:

- [신고지점.pdf](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/신고지점.pdf) (pdf)
- [전년지점.xlsx](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/전년지점.xlsx) (xlsx)
- [공급자확인.hwpx](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/공급자확인.hwpx) (hwpx)
- [실제입고.pdf](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/실제입고.pdf) (pdf)
- [유리현금.pdf](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/유리현금.pdf) (pdf)
- [현금스캔.png](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/현금스캔.png) (png)
- [받침판매.xlsx](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/받침판매.xlsx) (xlsx)
- [고지지급.hwpx](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/고지지급.hwpx) (hwpx)
- [반기검토.pdf](../data/batch_1/C_vat/B1_C299_5615dbc2/inputs/반기검토.pdf) (pdf)

정답: [gold.json](../data/batch_1/C_vat/B1_C299_5615dbc2/gold.json)

```json
{
  "noncreditable_vat": 230000,
  "prepaid_vat": 811000,
  "receipt_credit": 74360,
  "refund_vat": 365360
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "유리현금", "purpose": "business", "transaction_id": "재고-299"}, {"filing_site_id": "받침점-299", "prior_year_site_supply_base": 992000000}, {"supplier_general": false, "supplier_id": "유리상-299... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 5720000, "supply_base": 5200000, "vat": 520000} |
| VAT_OUTPUT_10 | 520000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 5720000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 2530000, "supply_base": 2300000, "vat": 230000} |
| VAT_INPUT_EVIDENCE | {"deductible": 0, "noncreditable": 230000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 74360 |
| VAT_CREDIT_ANNUAL_LIMIT | 74360 |
| VAT_CREDIT_PAYABLE_LIMIT | 74360 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -365360 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 230000, "net_vat": -365360, "noncreditable_vat": 230000, "output_vat": 520000, "payable_vat": 0, "prepaid_vat": 811000, "receipt_credit": 74360, "refund_vat": 365360, "tax_base": 5200000... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/C_vat/B1_C299_5615dbc2/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D008_6c100c82 (D_extract, easy)

집필 제목: 야간 자전거 교실의 반사 용품 재구매 기준

업무 목적: 다음 기수의 반사 용품별 재구매 후보를 확인한다.

야간 자전거 교실의 다음 기수를 준비합니다. 지난 구매에서 반사 용품마다 가장 낮았던 공급가액 단가와 판매처를 찾아 재주문 기준을 남겨 주세요. answer.json에는 cheapest_by_item을 작성해 주세요.

설계 의도: 휠 반사판은 두 판매처에서 샀지만 팔 반사띠와 안장 반사덮개는 각각 한 판매처에서만 샀다. 전체 품목을 억지로 두 업체가 모두 공급하도록 만들지 않고 실제 구매 이력에 있는 선택 범위로 재발주 표를 작성한다.

집필 원고 ID: `D008`, 전체 문항 SHA-256: `6c100c82bf9b9d803d1450f0714eb2e4871ed92b7aecd173ee1929b3a427ed4f`

[문항 메타데이터](../data/batch_1/D_extract/B1_D008_6c100c82/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_004_053.json)

입력 파일:

- [01_반사판과팔띠_인수.pdf](../data/batch_1/D_extract/B1_D008_6c100c82/inputs/01_반사판과팔띠_인수.pdf) (pdf)
- [02_반사덮개_추가구매.xlsx](../data/batch_1/D_extract/B1_D008_6c100c82/inputs/02_반사덮개_추가구매.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/D_extract/B1_D008_6c100c82/gold.json)

```json
{
  "cheapest_by_item": [
    {
      "item": "안장반사덮개",
      "unit_price": 4100,
      "vendor": "가상빛자전거"
    },
    {
      "item": "팔반사띠",
      "unit_price": 3200,
      "vendor": "가상밤길안전"
    },
    {
      "item": "휠반사판",
      "unit_price": 1650,
      "vendor": "가상빛자전거"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 72000, "total": 79200, "vat": 7200} |
| D.vat_split | {"supply": 64000, "total": 70400, "vat": 6400} |
| D.vendor_normalize | "가상밤길안전" |
| D.vat_split | {"supply": 39600, "total": 43560, "vat": 3960} |
| D.vat_split | {"supply": 49200, "total": 54120, "vat": 4920} |
| D.vendor_normalize | "가상빛자전거" |
| D.aggregate | {"cheapest_by_item": [{"item": "안장반사덮개", "unit_price": 4100, "vendor": "가상빛자전거"}, {"item": "팔반사띠", "unit_price": 3200, "vendor": "가상밤길안전"}, {"item": "휠반사판", "unit_price": 1650, "vendor": "가상빛자전거"}], "grand_total": 247280, "supp... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D008_6c100c82/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D016_ced6f3c1 (D_extract, easy)

집필 제목: 기록 사진 인화비의 공급가액 확인

업무 목적: 인화비 결제액에서 공급가액과 부가세를 분리해 기록한다.

마을 기록 사진의 인화비를 지원금 장부에 입력하려 합니다. 소형 사진과 전시용 사진의 인수 수량을 기준으로 공급가액과 부가세를 나누어 주세요. answer.json에는 supply_total과 vat_total을 적어 주세요.

설계 의도: 사진 촬영 용역과 인화 구매를 혼합하지 않고 인화물 두 규격의 실제 수량만 작성했다. 작은 사진과 전시용 큰 사진의 단가가 다르므로 품목별 계산 후 합산하는 기본적인 장부 업무이다.

집필 원고 ID: `D016`, 전체 문항 SHA-256: `ced6f3c1d992efea858ea183a220c02316998827e1437abec32387f4ca294d1f`

[문항 메타데이터](../data/batch_1/D_extract/B1_D016_ced6f3c1/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_004_053.json)

입력 파일:

- [01_기록사진_인화명세.pdf](../data/batch_1/D_extract/B1_D016_ced6f3c1/inputs/01_기록사진_인화명세.pdf) (pdf)

정답: [gold.json](../data/batch_1/D_extract/B1_D016_ced6f3c1/gold.json)

```json
{
  "supply_total": 282000,
  "vat_total": 28200
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 120000, "total": 132000, "vat": 12000} |
| D.vat_split | {"supply": 162000, "total": 178200, "vat": 16200} |
| D.vendor_normalize | "가상기록인화" |
| D.aggregate | {"cheapest_by_item": [{"item": "기록사진소형인화", "unit_price": 500, "vendor": "가상기록인화"}, {"item": "전시사진대형인화", "unit_price": 9000, "vendor": "가상기록인화"}], "grand_total": 310200, "supply_total": 282000, "unique_document_count": 1, "vat_t... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D016_ced6f3c1/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D049_1cc81b2d (D_extract, hard)

집필 제목: 한파 대피실 개설비의 여러 법인명 정산

업무 목적: 각 대피실에서 보낸 개설 물품비를 실제 거래처별로 모아 전체 사업비를 결산한다.

한파 대피실을 순차 개설하며 산 물품의 결산서를 작성해 주세요. 각 대피실의 납품 자료를 거래처별로 합치고 사업 전체의 공급가액과 부가세, 지급 총액을 확인해 주세요. answer.json에는 vendor_totals와 supply_total, vat_total과 grand_total을 적어 주세요.

설계 의도: 난방비나 숙박비가 아닌 실제 개설 물품만을 대상으로 작성했다. 침상 덮개와 담요 주머니 및 안내품은 대피실별로 필요한 시점이 달라 따로 인수했다. 한 업체의 여러 법인 표기를 묶어야 지급 내역이 맞고 판매처마다 세금 표현도 다르다. 모든 아홉 자료가 실제 거래이므로 서류 수를 중복본으로 늘리지 않았다.

집필 원고 ID: `D049`, 전체 문항 SHA-256: `1cc81b2d60d118bfdf8020136516710e2f96a3b58974c5fdce07c386bf3b8b5d`

[문항 메타데이터](../data/batch_1/D_extract/B1_D049_1cc81b2d/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_004_053.json)

입력 파일:

- [01_침상덮개_명세.pdf](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/01_침상덮개_명세.pdf) (pdf)
- [02_담요주머니_대장.xlsx](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/02_담요주머니_대장.xlsx) (xlsx)
- [03_입구안내판_확인.hwpx](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/03_입구안내판_확인.hwpx) (hwpx)
- [04_반사포_명세.pdf](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/04_반사포_명세.pdf) (pdf)
- [05_보호매트_대장.xlsx](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/05_보호매트_대장.xlsx) (xlsx)
- [06_순서표홀더_확인.hwpx](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/06_순서표홀더_확인.hwpx) (hwpx)
- [07_물품상자_명세.pdf](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/07_물품상자_명세.pdf) (pdf)
- [08_번호표_대장.xlsx](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/08_번호표_대장.xlsx) (xlsx)
- [09_보온컵_확인.hwpx](../data/batch_1/D_extract/B1_D049_1cc81b2d/inputs/09_보온컵_확인.hwpx) (hwpx)

정답: [gold.json](../data/batch_1/D_extract/B1_D049_1cc81b2d/gold.json)

```json
{
  "grand_total": 2223540,
  "supply_total": 2021400,
  "vat_total": 202140,
  "vendor_totals": [
    {
      "supply": 490000,
      "total": 539000,
      "vat": 49000,
      "vendor": "가상겨울준비"
    },
    {
      "supply": 256400,
      "total": 282040,
      "vat": 25640,
      "vendor": "가상대피안내"
    },
    {
      "supply": 1275000,
      "total": 1402500,
      "vat": 127500,
      "vendor": "가상온기비품"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 420000, "total": 462000, "vat": 42000} |
| D.vendor_normalize | "가상온기비품" |
| D.vat_split | {"supply": 144000, "total": 158400, "vat": 14400} |
| D.vendor_normalize | "가상온기비품" |
| D.vat_split | {"supply": 168000, "total": 184800, "vat": 16800} |
| D.vendor_normalize | "가상대피안내" |
| D.vat_split | {"supply": 240000, "total": 264000, "vat": 24000} |
| D.vendor_normalize | "가상겨울준비" |
| D.vat_split | {"supply": 441000, "total": 485100, "vat": 44100} |
| D.vendor_normalize | "가상온기비품" |
| D.vat_split | {"supply": 50000, "total": 55000, "vat": 5000} |
| D.vendor_normalize | "가상대피안내" |
| D.vat_split | {"supply": 270000, "total": 297000, "vat": 27000} |
| D.vendor_normalize | "가상온기비품" |
| D.vat_split | {"supply": 38400, "total": 42240, "vat": 3840} |
| D.vendor_normalize | "가상대피안내" |
| D.vat_split | {"supply": 250000, "total": 275000, "vat": 25000} |
| D.vendor_normalize | "가상겨울준비" |
| D.aggregate | {"cheapest_by_item": [{"item": "개인물품보관상자", "unit_price": 9000, "vendor": "가상온기비품"}, {"item": "담요보관주머니", "unit_price": 4000, "vendor": "가상온기비품"}, {"item": "대피실순서표홀더", "unit_price": 2500, "vendor": "가상대피안내"}, {"item": "대피실입구안내판",... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D049_1cc81b2d/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D051_218af802 (D_extract, hard)

집필 제목: 공동 재봉실 두 보관 스캔과 법인명 정산

업무 목적: 서로 다른 법인 표기와 두 스캔 사본을 대조하여 재봉실 비품 정산을 인계한다.

공동 재봉실의 지급 대장을 인계하려 합니다. 종이 명세와 보관 스캔을 대조하고 판매처 이름을 맞춰 업체별 지급 내역을 모아 주세요. 전체 부가세와 집행액, 실제 구매 건수도 필요합니다. answer.json에는 vendor_totals와 vat_total, grand_total과 unique_document_count를 담아 주세요.

설계 의도: 재봉실이 개설되고 작업 모임이 늘면서 바늘통과 실 정리판 및 패턴 보관품을 차례로 구입한 이력이다. 두 종이 원본을 각각 스캔해 담당자 폴더에 두었지만 원본도 모두 인계되었다. 같은 업체의 세 납품 자료는 법인 표기가 다르고 일부 단가는 세금 포함이어서 거래처별 지급 내역과 세액을 함께 정리해야 한다.

집필 원고 ID: `D051`, 전체 문항 SHA-256: `218af8029133df3fe18a25759d4249bc27119f115ebaa7fc66f25a51128c2ddb`

[문항 메타데이터](../data/batch_1/D_extract/B1_D051_218af802/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_004_053.json)

입력 파일:

- [01_바늘통_원본.pdf](../data/batch_1/D_extract/B1_D051_218af802/inputs/01_바늘통_원본.pdf) (pdf)
- [02_실정리판_원본.pdf](../data/batch_1/D_extract/B1_D051_218af802/inputs/02_실정리판_원본.pdf) (pdf)
- [03_패턴봉투_대장.xlsx](../data/batch_1/D_extract/B1_D051_218af802/inputs/03_패턴봉투_대장.xlsx) (xlsx)
- [04_작업클립_확인.hwpx](../data/batch_1/D_extract/B1_D051_218af802/inputs/04_작업클립_확인.hwpx) (hwpx)
- [05_가위케이스_명세.pdf](../data/batch_1/D_extract/B1_D051_218af802/inputs/05_가위케이스_명세.pdf) (pdf)
- [06_색상표찰_구매.xlsx](../data/batch_1/D_extract/B1_D051_218af802/inputs/06_색상표찰_구매.xlsx) (xlsx)
- [07_보호매트_확인.hwpx](../data/batch_1/D_extract/B1_D051_218af802/inputs/07_보호매트_확인.hwpx) (hwpx)
- [08_바늘통_스캔.png](../data/batch_1/D_extract/B1_D051_218af802/inputs/08_바늘통_스캔.png) (png)
- [09_실정리판_스캔.png](../data/batch_1/D_extract/B1_D051_218af802/inputs/09_실정리판_스캔.png) (png)

정답: [gold.json](../data/batch_1/D_extract/B1_D051_218af802/gold.json)

```json
{
  "grand_total": 640090,
  "unique_document_count": 7,
  "vat_total": 58190,
  "vendor_totals": [
    {
      "supply": 138000,
      "total": 151800,
      "vat": 13800,
      "vendor": "가상실보관"
    },
    {
      "supply": 232500,
      "total": 255750,
      "vat": 23250,
      "vendor": "가상작업재봉"
    },
    {
      "supply": 211400,
      "total": 232540,
      "vat": 21140,
      "vendor": "가상재봉정돈"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 54400, "total": 59840, "vat": 5440} |
| D.vendor_normalize | "가상재봉정돈" |
| D.vat_split | {"supply": 96000, "total": 105600, "vat": 9600} |
| D.vendor_normalize | "가상실보관" |
| D.vat_split | {"supply": 60000, "total": 66000, "vat": 6000} |
| D.vendor_normalize | "가상재봉정돈" |
| D.vat_split | {"supply": 64500, "total": 70950, "vat": 6450} |
| D.vendor_normalize | "가상작업재봉" |
| D.vat_split | {"supply": 97000, "total": 106700, "vat": 9700} |
| D.vendor_normalize | "가상재봉정돈" |
| D.vat_split | {"supply": 42000, "total": 46200, "vat": 4200} |
| D.vendor_normalize | "가상실보관" |
| D.vat_split | {"supply": 168000, "total": 184800, "vat": 16800} |
| D.vendor_normalize | "가상작업재봉" |
| D.aggregate | {"cheapest_by_item": [{"item": "가위보관케이스", "unit_price": 9700, "vendor": "가상재봉정돈"}, {"item": "실색상표찰", "unit_price": 350, "vendor": "가상실보관"}, {"item": "실정리판", "unit_price": 8000, "vendor": "가상실보관"}, {"item": "재봉바늘통", "unit_price"... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D051_218af802/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D063_30a405f3 (D_extract, easy)

집필 제목: 안내 데스크 비품을 구매한 업체와 품목의 서로 다른 배열

업무 목적: 한 구매 묶음에서 지급 자료와 다음 구매 자료를 각각 작성한다.

안내 데스크 비품의 지급 자료와 보충 구매 기준을 함께 만듭니다. vendor_totals와 cheapest_by_item을 보내 주세요. 두 배열의 이름 처리 및 계산 기준은 추가 벨 인수서에 있습니다.

설계 의도: 업체별 지급 합산은 업체를 기준으로 읽지만 보충 구매 후보는 품목을 기준으로 읽는다. 한 업체는 두 품목을 공급하고 다른 업체는 안내벨만 공급하는 비대칭 구성이라 자료를 한 순서대로 옮겨 쓸 수 없다.

집필 원고 ID: `D063`, 전체 문항 SHA-256: `30a405f3f0b0b41b3dc19214b1c4e6037df1c6f705ee8e1666603f25b235ef6a`

[문항 메타데이터](../data/batch_1/D_extract/B1_D063_30a405f3/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_054_103.json)

입력 파일:

- [01_초기비품.pdf](../data/batch_1/D_extract/B1_D063_30a405f3/inputs/01_초기비품.pdf) (pdf)
- [02_추가벨.hwpx](../data/batch_1/D_extract/B1_D063_30a405f3/inputs/02_추가벨.hwpx) (hwpx)

정답: [gold.json](../data/batch_1/D_extract/B1_D063_30a405f3/gold.json)

```json
{
  "cheapest_by_item": [
    {
      "item": "리플릿거치대",
      "unit_price": 19600,
      "vendor": "가상응대물품"
    },
    {
      "item": "안내벨",
      "unit_price": 11700,
      "vendor": "가상방문안내"
    }
  ],
  "vendor_totals": [
    {
      "supply": 46800,
      "total": 51480,
      "vat": 4680,
      "vendor": "가상방문안내"
    },
    {
      "supply": 84400,
      "total": 92840,
      "vat": 8440,
      "vendor": "가상응대물품"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 25600, "total": 28160, "vat": 2560} |
| D.vat_split | {"supply": 58800, "total": 64680, "vat": 5880} |
| D.vendor_normalize | "가상응대물품" |
| D.vat_split | {"supply": 46800, "total": 51480, "vat": 4680} |
| D.vendor_normalize | "가상방문안내" |
| D.aggregate | {"cheapest_by_item": [{"item": "리플릿거치대", "unit_price": 19600, "vendor": "가상응대물품"}, {"item": "안내벨", "unit_price": 11700, "vendor": "가상방문안내"}], "grand_total": 144320, "supply_total": 131200, "unique_document_count": 2, "vat_total... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D063_30a405f3/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D103_9e8506aa (D_extract, hard)

집필 제목: 행 순서가 다른 표지와 단가표의 실내 센서 부품 정산

업무 목적: 자료의 행 순서 대신 연결 번호를 써서 실제 센서 부품 지출과 가격을 확인한다.

센서 자료는 표지와 품목표 수신 순서가 다릅니다. 연결 번호 및 인수 이력으로 거래를 복원해 vendor_totals, cheapest_by_item, grand_total을 답하세요. 표기와 가격 처리 계약은 현장 대장에 있습니다.

설계 의도: 첫 수신 품목표는 세 번째 표지에 연결되고 마지막 품목표는 첫 표지에 연결되도록 수신 순서를 직접 정했다. 한 표지는 인수 없는 주문이며 품목명이 다른 표기여도 같은 SensorMount를 가리킨다. 거래 조건을 위치로 붙이면 공급처와 포함 여부가 바뀐다.

집필 원고 ID: `D103`, 전체 문항 SHA-256: `9e8506aa3cfc5e81da65607c9e1025b2aa87b1b99fd8c8ef2794ea6f870eac32`

[문항 메타데이터](../data/batch_1/D_extract/B1_D103_9e8506aa/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_054_103.json)

입력 파일:

- [01_동쪽표지.pdf](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/01_동쪽표지.pdf) (pdf)
- [02_첫수신품목.xlsx](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/02_첫수신품목.xlsx) (xlsx)
- [03_추가주문표지.hwpx](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/03_추가주문표지.hwpx) (hwpx)
- [04_둘째수신품목.pdf](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/04_둘째수신품목.pdf) (pdf)
- [05_중앙표지.pdf](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/05_중앙표지.pdf) (pdf)
- [06_셋째수신품목.xlsx](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/06_셋째수신품목.xlsx) (xlsx)
- [07_서쪽표지.hwpx](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/07_서쪽표지.hwpx) (hwpx)
- [08_마지막수신품목.pdf](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/08_마지막수신품목.pdf) (pdf)
- [09_현장이력.xlsx](../data/batch_1/D_extract/B1_D103_9e8506aa/inputs/09_현장이력.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/D_extract/B1_D103_9e8506aa/gold.json)

```json
{
  "cheapest_by_item": [
    {
      "item": "sensormount",
      "unit_price": 11000,
      "vendor": "가상관측고정"
    },
    {
      "item": "배선고정홈",
      "unit_price": 2800,
      "vendor": "가상벽부품"
    }
  ],
  "grand_total": 329560,
  "vendor_totals": [
    {
      "supply": 98000,
      "total": 107800,
      "vat": 9800,
      "vendor": "가상관측고정"
    },
    {
      "supply": 84000,
      "total": 92400,
      "vat": 8400,
      "vendor": "가상벽부품"
    },
    {
      "supply": 117600,
      "total": 129360,
      "vat": 11760,
      "vendor": "가상실내센서"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.evidence_reconciliation | {"excluded_document_ids": ["ROOMSENSOR-0115-P"], "joined_document_records_before_deduplication": 3, "received_document_ids": ["ROOMSENSOR-0112-A", "ROOMSENSOR-0120-B", "ROOMSENSOR-0128-C"]} |
| D.vat_split | {"supply": 92800, "total": 102080, "vat": 9280} |
| D.vat_split | {"supply": 24800, "total": 27280, "vat": 2480} |
| D.vendor_normalize | "가상실내센서" |
| D.vat_split | {"supply": 77000, "total": 84700, "vat": 7700} |
| D.vat_split | {"supply": 21000, "total": 23100, "vat": 2100} |
| D.vendor_normalize | "가상관측고정" |
| D.vat_split | {"supply": 67200, "total": 73920, "vat": 6720} |
| D.vat_split | {"supply": 16800, "total": 18480, "vat": 1680} |
| D.vendor_normalize | "가상벽부품" |
| D.aggregate | {"cheapest_by_item": [{"item": "sensormount", "unit_price": 11000, "vendor": "가상관측고정"}, {"item": "배선고정홈", "unit_price": 2800, "vendor": "가상벽부품"}], "grand_total": 329560, "supply_total": 299600, "unique_document_count": 3, "vat_... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D103_9e8506aa/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D177_45a3e13b (D_extract, medium)

집필 제목: 현장 기록 수첩의 표지와 내지 가격표 세액 구분

업무 목적: 가격 조건만 있는 표지와 원문 번호만 있는 품목표를 맞춰 회계 금액을 계산한다.

현장 기록 수첩비를 세금 제외 비용과 부가세로 나눠 주세요. 표지와 품목표를 원문 번호로 맞춘 supply_total 및 vat_total을 답합니다.

설계 의도: 첫 구매는 포함 단가로 납품한 완성 수첩이고 두 번째는 별도 단가의 교체 내지다. 각 원문 번호가 표지와 품목표 양쪽에 보이도록 자료를 설계했다. 파일 순서나 품목 종류를 근거로 세금 조건을 추정할 수 없는 실제 회계 전사 관계다.

집필 원고 ID: `D177`, 전체 문항 SHA-256: `45a3e13bceb3aacb071e096f079a2e3c729efaf06cbac94da83a019a1ff2e48c`

[문항 메타데이터](../data/batch_1/D_extract/B1_D177_45a3e13b/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_154_203.json)

입력 파일:

- [01_완성수첩표지.pdf](../data/batch_1/D_extract/B1_D177_45a3e13b/inputs/01_완성수첩표지.pdf) (pdf)
- [02_교체내지품목.xlsx](../data/batch_1/D_extract/B1_D177_45a3e13b/inputs/02_교체내지품목.xlsx) (xlsx)
- [03_교체내지표지.hwpx](../data/batch_1/D_extract/B1_D177_45a3e13b/inputs/03_교체내지표지.hwpx) (hwpx)
- [04_완성수첩품목.xlsx](../data/batch_1/D_extract/B1_D177_45a3e13b/inputs/04_완성수첩품목.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/D_extract/B1_D177_45a3e13b/gold.json)

```json
{
  "supply_total": 157232,
  "vat_total": 15723
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 107115, "total": 117827, "vat": 10712} |
| D.vendor_normalize | "가상현장수첩" |
| D.vat_split | {"supply": 50117, "total": 55128, "vat": 5011} |
| D.vendor_normalize | "가상현장수첩" |
| D.aggregate | {"cheapest_by_item": [{"item": "현장기록수첩", "unit_price": 6300, "vendor": "가상현장수첩"}, {"item": "현장수첩교체내지", "unit_price": 2179, "vendor": "가상현장수첩"}], "grand_total": 172955, "supply_total": 157232, "unique_document_count": 2, "vat_to... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D177_45a3e13b/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D200_a31f9636 (D_extract, hard)

집필 제목: 문서 보존 전등의 제안 및 대체 주문 단가 기준

업무 목적: 단가 비교에 쓸 실제 인수 범위를 결정한 뒤 포함 가격을 공급가액으로 맞춘다.

문서 보존 작업용 전등의 실제 구매 기준과 집행액을 정리해 주세요. cheapest_by_item과 grand_total을 answer.json에 담습니다.

설계 의도: 작업등은 두 곳에서 실제로 구매했고 보호커버는 다른 실제 인수다. 작업등 견적 두 건과 더 큰 규격의 취소 주문도 함께 있다. 견적이 실제보다 낮고 두 실제 작업등은 포함 조건이 달라 표시 가격만으로 선택할 수 없다. 더 큰 규격은 취소 상태와 별개로 품목명에 보존한다.

집필 원고 ID: `D200`, 전체 문항 SHA-256: `a31f96360d34a178f8f08afbd437af0af32996ce82fc0334f35f3a60068c2885`

[문항 메타데이터](../data/batch_1/D_extract/B1_D200_a31f9636/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_154_203.json)

입력 파일:

- [01_첫작업등표지.pdf](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/01_첫작업등표지.pdf) (pdf)
- [02_나머지조달표지.hwpx](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/02_나머지조달표지.hwpx) (hwpx)
- [03_작업등제안품목.xlsx](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/03_작업등제안품목.xlsx) (xlsx)
- [04_큰작업등품목.pdf](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/04_큰작업등품목.pdf) (pdf)
- [05_첫작업등품목.xlsx](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/05_첫작업등품목.xlsx) (xlsx)
- [06_다른작업등품목.hwpx](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/06_다른작업등품목.hwpx) (hwpx)
- [07_보호커버품목.pdf](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/07_보호커버품목.pdf) (pdf)
- [08_작업실인수.xlsx](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/08_작업실인수.xlsx) (xlsx)
- [09_후속주문처리.hwpx](../data/batch_1/D_extract/B1_D200_a31f9636/inputs/09_후속주문처리.hwpx) (hwpx)

정답: [gold.json](../data/batch_1/D_extract/B1_D200_a31f9636/gold.json)

```json
{
  "cheapest_by_item": [
    {
      "item": "보존등보호커버",
      "unit_price": 8900,
      "vendor": "가상보존조명"
    },
    {
      "item": "보존작업등20w",
      "unit_price": 48000,
      "vendor": "가상보존조명"
    }
  ],
  "grand_total": 378180
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.evidence_reconciliation | {"excluded_document_ids": ["CONSERVE-BIG-14", "CONSERVE-QA-27", "CONSERVE-QB-28"], "joined_document_records_before_deduplication": 3, "received_document_ids": ["CONSERVE-A-11", "CONSERVE-B-12", "CONSERVE-COVER-13"]} |
| D.vat_split | {"supply": 192000, "total": 211200, "vat": 19200} |
| D.vendor_normalize | "가상보존조명" |
| D.vat_split | {"supply": 98400, "total": 108240, "vat": 9840} |
| D.vendor_normalize | "가상문서등" |
| D.vat_split | {"supply": 53400, "total": 58740, "vat": 5340} |
| D.vendor_normalize | "가상보존조명" |
| D.aggregate | {"cheapest_by_item": [{"item": "보존등보호커버", "unit_price": 8900, "vendor": "가상보존조명"}, {"item": "보존작업등20w", "unit_price": 48000, "vendor": "가상보존조명"}], "grand_total": 378180, "supply_total": 343800, "unique_document_count": 3, "vat_... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D200_a31f9636/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D210_d6749895 (D_extract, easy)

집필 제목: 커피 교실 원두 보관품의 세금 구분

업무 목적: 밀폐통과 건조제의 결제액에서 공급가액과 세액을 분리한다.

커피 교실 원두 보관품 결제액을 세금 구분표로 옮겨 주세요. supply_total과 vat_total을 제출해 주세요.

설계 의도: 원두 자체가 아니라 실제로 구매한 보관 비품의 금액을 다룬다. 두 물품의 수량과 단가를 먼저 곱한 후 포함 가격 규칙을 행별로 적용한다.

집필 원고 ID: `D210`, 전체 문항 SHA-256: `d6749895958f2ca6e92f0241a2de27b1f0cf9415bacb49c094f67ad374a0b352`

[문항 메타데이터](../data/batch_1/D_extract/B1_D210_d6749895/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_204_253.json)

입력 파일:

- [01_원두보관비품.pdf](../data/batch_1/D_extract/B1_D210_d6749895/inputs/01_원두보관비품.pdf) (pdf)

정답: [gold.json](../data/batch_1/D_extract/B1_D210_d6749895/gold.json)

```json
{
  "supply_total": 95500,
  "vat_total": 9550
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 85500, "total": 94050, "vat": 8550} |
| D.vat_split | {"supply": 10000, "total": 11000, "vat": 1000} |
| D.vendor_normalize | "가상향보관" |
| D.aggregate | {"cheapest_by_item": [{"item": "보관건조제묶음", "unit_price": 2500, "vendor": "가상향보관"}, {"item": "원두밀폐통1l", "unit_price": 9500, "vendor": "가상향보관"}], "grand_total": 105050, "supply_total": 95500, "unique_document_count": 1, "vat_total... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D210_d6749895/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D213_175ede63 (D_extract, easy)

집필 제목: 대관실 소모 전구의 규격별 재주문 가격

업무 목적: 구입처별로 다른 전구 규격을 빠짐없이 재주문 표에 남긴다.

대관실 소모 전구를 다시 주문할 때 쓸 가격표를 만들어 주세요. cheapest_by_item만 필요합니다.

설계 의도: 한 업체는 소형 전구와 큰 전구를 함께 판매했고 다른 업체는 소형만 판매했다. 가장 싼 거래 한 건을 고르는 대신 규격마다 실제 구입 가격을 비교하는 요청이다.

집필 원고 ID: `D213`, 전체 문항 SHA-256: `175ede6378f1c3a28aeb0bb146f6ed502bce9f8f6eca658c58b610acb8a77a36`

[문항 메타데이터](../data/batch_1/D_extract/B1_D213_175ede63/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_204_253.json)

입력 파일:

- [01_소빛전구명세.pdf](../data/batch_1/D_extract/B1_D213_175ede63/inputs/01_소빛전구명세.pdf) (pdf)
- [02_보충전구명세.xlsx](../data/batch_1/D_extract/B1_D213_175ede63/inputs/02_보충전구명세.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/D_extract/B1_D213_175ede63/gold.json)

```json
{
  "cheapest_by_item": [
    {
      "item": "전구e14-5w",
      "unit_price": 2600,
      "vendor": "가상전기매대"
    },
    {
      "item": "전구e27-12w",
      "unit_price": 5700,
      "vendor": "가상소빛전구"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 33600, "total": 36960, "vat": 3360} |
| D.vat_split | {"supply": 45600, "total": 50160, "vat": 4560} |
| D.vendor_normalize | "가상소빛전구" |
| D.vat_split | {"supply": 7800, "total": 8580, "vat": 780} |
| D.vendor_normalize | "가상전기매대" |
| D.aggregate | {"cheapest_by_item": [{"item": "전구e14-5w", "unit_price": 2600, "vendor": "가상전기매대"}, {"item": "전구e27-12w", "unit_price": 5700, "vendor": "가상소빛전구"}], "grand_total": 95700, "supply_total": 87000, "unique_document_count": 2, "vat_t... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D213_175ede63/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D220_2780faf1 (D_extract, medium)

집필 제목: 공방 장갑 구입의 한 법인과 다른 지점 지급 계정

업무 목적: 법인 표현의 차이는 합하고 지점 이름이 있는 별개 계정은 보존한다.

공방 보호 장갑 구입을 판매처 계정으로 정리해 주세요. vendor_totals와 grand_total이 필요합니다.

설계 의도: 첫 두 명세의 판매처는 법인 표기만 다르다. 세 번째 판매처 이름에는 지점 글자가 남는다. 모든 이름을 앞부분만 잘라 합치면 서로 다른 지급 계정의 금액이 바뀐다.

집필 원고 ID: `D220`, 전체 문항 SHA-256: `2780faf155143b48d626b96e2aef0db6e63666f3e4ea6186519c730f0e77f129`

[문항 메타데이터](../data/batch_1/D_extract/B1_D220_2780faf1/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_204_253.json)

입력 파일:

- [01_법인첫명세.pdf](../data/batch_1/D_extract/B1_D220_2780faf1/inputs/01_법인첫명세.pdf) (pdf)
- [02_추가구매표지.hwpx](../data/batch_1/D_extract/B1_D220_2780faf1/inputs/02_추가구매표지.hwpx) (hwpx)
- [03_추가품목.xlsx](../data/batch_1/D_extract/B1_D220_2780faf1/inputs/03_추가품목.xlsx) (xlsx)
- [04_동쪽점명세.pdf](../data/batch_1/D_extract/B1_D220_2780faf1/inputs/04_동쪽점명세.pdf) (pdf)

정답: [gold.json](../data/batch_1/D_extract/B1_D220_2780faf1/gold.json)

```json
{
  "grand_total": 99275,
  "vendor_totals": [
    {
      "supply": 74250,
      "total": 81675,
      "vat": 7425,
      "vendor": "가상안전직물"
    },
    {
      "supply": 16000,
      "total": 17600,
      "vat": 1600,
      "vendor": "가상안전직물동쪽점"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 42000, "total": 46200, "vat": 4200} |
| D.vendor_normalize | "가상안전직물" |
| D.vat_split | {"supply": 32250, "total": 35475, "vat": 3225} |
| D.vendor_normalize | "가상안전직물" |
| D.vat_split | {"supply": 16000, "total": 17600, "vat": 1600} |
| D.vendor_normalize | "가상안전직물동쪽점" |
| D.aggregate | {"cheapest_by_item": [{"item": "보호장갑l", "unit_price": 2150, "vendor": "가상안전직물"}, {"item": "보호장갑m", "unit_price": 2100, "vendor": "가상안전직물"}, {"item": "얇은보호장갑", "unit_price": 1600, "vendor": "가상안전직물동쪽점"}], "grand_total": 99275, "... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D220_2780faf1/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D258_889bf180 (D_extract, easy)

집필 제목: 수족관 여과솜의 실제 구입 단가 확인

업무 목적: 동일 여과솜 규격의 실구매 단가 중 낮은 값을 찾는다.

동일 규격 여과솜을 두 판매처에서 인수했습니다. 다음 발주 때 참고할 cheapest_by_item을 두 실제 구매 자료에서 작성해 주세요.

설계 의도: 필요 수량을 나눠 구입했으므로 거래 총액이 작은 업체와 단가가 낮은 업체가 다를 수 있다. 모두 공급가액 단가라 같은 기준으로 비교한다.

집필 원고 ID: `D258`, 전체 문항 SHA-256: `889bf1805156ef1b46efcb841bbb61abc6ae2a9c411af67c8aa291f6b679e4b6`

[문항 메타데이터](../data/batch_1/D_extract/B1_D258_889bf180/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_254_300.json)

입력 파일:

- [01_첫여과솜.hwpx](../data/batch_1/D_extract/B1_D258_889bf180/inputs/01_첫여과솜.hwpx) (hwpx)
- [02_보충여과솜.pdf](../data/batch_1/D_extract/B1_D258_889bf180/inputs/02_보충여과솜.pdf) (pdf)

정답: [gold.json](../data/batch_1/D_extract/B1_D258_889bf180/gold.json)

```json
{
  "cheapest_by_item": [
    {
      "item": "여과솜50x30",
      "unit_price": 8900,
      "vendor": "가상어항공급"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 18800, "total": 20680, "vat": 1880} |
| D.vendor_normalize | "가상수조자재" |
| D.vat_split | {"supply": 80100, "total": 88110, "vat": 8010} |
| D.vendor_normalize | "가상어항공급" |
| D.aggregate | {"cheapest_by_item": [{"item": "여과솜50x30", "unit_price": 8900, "vendor": "가상어항공급"}], "grand_total": 108790, "supply_total": 98900, "unique_document_count": 2, "vat_total": 9890, "vendor_totals": [{"supply": 18800, "total": 2068... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D258_889bf180/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D261_28ea01d2 (D_extract, easy)

집필 제목: 꽃가게 냉장 진열 보강의 세액과 지급액

업무 목적: 냉장 진열 보강품의 세액 계정과 결제 계정을 맞춘다.

냉장 진열대 보강 부품을 장부에 등록해 주세요. 실제 영수증의 vat_total과 grand_total을 answer.json에 적어 주세요.

설계 의도: 유리 선반과 고무 받침이 하나의 영수증에 있다. 각 품목 행에서 포함 단가를 분리한 뒤 두 계정을 각각 합산해야 한다.

집필 원고 ID: `D261`, 전체 문항 SHA-256: `28ea01d27afb03b13511dda51fee104fc70c94272382b08db5251aadd7ef0218`

[문항 메타데이터](../data/batch_1/D_extract/B1_D261_28ea01d2/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_254_300.json)

입력 파일:

- [01_진열대보강.hwpx](../data/batch_1/D_extract/B1_D261_28ea01d2/inputs/01_진열대보강.hwpx) (hwpx)

정답: [gold.json](../data/batch_1/D_extract/B1_D261_28ea01d2/gold.json)

```json
{
  "grand_total": 100980,
  "vat_total": 9180
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 87000, "total": 95700, "vat": 8700} |
| D.vat_split | {"supply": 4800, "total": 5280, "vat": 480} |
| D.vendor_normalize | "가상진열수선" |
| D.aggregate | {"cheapest_by_item": [{"item": "선반고무받침", "unit_price": 400, "vendor": "가상진열수선"}, {"item": "유리선반40", "unit_price": 29000, "vendor": "가상진열수선"}], "grand_total": 100980, "supply_total": 91800, "unique_document_count": 1, "vat_total... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D261_28ea01d2/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D264_d501efe6 (D_extract, easy)

집필 제목: 중고책 포장재 구매의 세 가지 합계

업무 목적: 책 포장재 한 원본의 세금 제외 금액과 세액 및 지급액을 맞춘다.

판매한 책을 포장할 상자와 완충지를 인수했습니다. supply_total과 vat_total 및 grand_total을 원가표에 옮겨 주세요.

설계 의도: 상자와 완충지는 같은 구매 원본이다. 행별 세액 분리를 거쳐 전체 세 금액의 합계 관계를 확인하는 정산이다.

집필 원고 ID: `D264`, 전체 문항 SHA-256: `d501efe6d97a8e3aef2d9171a1c2eb1ea702a162544ef712f02389d139549201`

[문항 메타데이터](../data/batch_1/D_extract/B1_D264_d501efe6/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_254_300.json)

입력 파일:

- [01_책포장구매.xlsx](../data/batch_1/D_extract/B1_D264_d501efe6/inputs/01_책포장구매.xlsx) (xlsx)

정답: [gold.json](../data/batch_1/D_extract/B1_D264_d501efe6/gold.json)

```json
{
  "grand_total": 63360,
  "supply_total": 57600,
  "vat_total": 5760
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.vat_split | {"supply": 33600, "total": 36960, "vat": 3360} |
| D.vat_split | {"supply": 24000, "total": 26400, "vat": 2400} |
| D.vendor_normalize | "가상책포장" |
| D.aggregate | {"cheapest_by_item": [{"item": "종이완충지한롤", "unit_price": 12000, "vendor": "가상책포장"}, {"item": "책상자b5", "unit_price": 420, "vendor": "가상책포장"}], "grand_total": 63360, "supply_total": 57600, "unique_document_count": 1, "vat_total": ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D264_d501efe6/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B1_D276_953771be (D_extract, medium)

집필 제목: 입장권 프린터 별첨을 표지의 세금 가격 조건에 연결

업무 목적: 품목표의 표지 참조에서 부가세 포함 조건을 찾아 실제 소모품 원가와 세액을 정한다.

박물관 입장권 프린터 소모품의 표지 두 장과 뒤섞인 별첨을 받았습니다. 별첨이 참조한 표지의 가격 조건을 적용해 supply_total과 vat_total을 제출해 주세요. 별첨을 받은 순서로 표지에 붙이면 안 됩니다.

설계 의도: 품목 별첨에는 가격 포함 여부가 없고 두 표지의 조건이 다르다. 첫 번째와 세 번째 별첨은 포함 가격 표지에 속하며 가운데 별첨은 별도 가격 표지에 속한다. 동일 물품에 일괄적으로 포함 또는 별도 조건을 적용하거나 표지 연결을 바꾸면 두 합계가 달라진다.

집필 원고 ID: `D276`, 전체 문항 SHA-256: `953771beb621d6a425d5852aa50f59cfdabc3058a6d1f7df7664449c389c7490`

[문항 메타데이터](../data/batch_1/D_extract/B1_D276_953771be/task.yaml)와 [집필 원고](../authored/batch_1/D_extract/cases_254_300.json)

입력 파일:

- [01_가격조건표지.hwpx](../data/batch_1/D_extract/B1_D276_953771be/inputs/01_가격조건표지.hwpx) (hwpx)
- [02_별첨접수.xlsx](../data/batch_1/D_extract/B1_D276_953771be/inputs/02_별첨접수.xlsx) (xlsx)
- [03_롤소모품인수.pdf](../data/batch_1/D_extract/B1_D276_953771be/inputs/03_롤소모품인수.pdf) (pdf)
- [04_리본인수.hwpx](../data/batch_1/D_extract/B1_D276_953771be/inputs/04_리본인수.hwpx) (hwpx)

정답: [gold.json](../data/batch_1/D_extract/B1_D276_953771be/gold.json)

```json
{
  "supply_total": 47960,
  "vat_total": 4796
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.evidence_reconciliation | {"excluded_document_ids": [], "joined_document_records_before_deduplication": 2, "received_document_ids": ["MUSEUM-RIBBON-32", "MUSEUM-TICKET-31"]} |
| D.vat_split | {"supply": 21160, "total": 23276, "vat": 2116} |
| D.vat_split | {"supply": 7000, "total": 7700, "vat": 700} |
| D.vendor_normalize | "가상입장인쇄재" |
| D.vat_split | {"supply": 19800, "total": 21780, "vat": 1980} |
| D.vendor_normalize | "가상표권소모품" |
| D.aggregate | {"cheapest_by_item": [{"item": "입장권롤60", "unit_price": 920, "vendor": "가상입장인쇄재"}, {"item": "프린터리본r2", "unit_price": 9900, "vendor": "가상표권소모품"}, {"item": "프린터청소카드", "unit_price": 1400, "vendor": "가상입장인쇄재"}], "grand_total": 52756... |

전체 계산 입력과 중간값: [trace.json](../data/batch_1/D_extract/B1_D276_953771be/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

<!-- authored-task-set-sha256: f52c5b067719881279f96d39358132cb01955090905f1305704d9a59050f68ac -->
