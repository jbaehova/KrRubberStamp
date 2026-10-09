# Batch 2 사람 검수 대기열

분야별 무작위 15문항, 총 60문항을 검수 대기 상태로 정리했습니다.

무작위 추출 시드는 20261009입니다. 추출은 문항 선택에만 쓰이며 사실이나 지시문을 생성하지 않습니다. 자동 게이트는 전문가의 독립적인 법률 해석 및 문항 다양성 검수를 대체하지 않습니다.

## B2_A011_e4c2a7a2 (A_yearend, easy)

집필 제목: 종교기부가 없는 공익기부의 남은 소득 한도

업무 목적: 종교기부가 없는 신청에서 특례기부 차감 후 공익기부 한도를 적용한다.

가상한낮정밀의 가상변주안은 구호 특례기부와 공익기부만 납부했습니다. 특례기부를 적용한 뒤 남은 근로소득금액을 기준으로 공익기부 한도를 계산해 기부금 세액공제와 결정 국세를 작성하세요.

설계 의도: 공익기부 한도는 총급여의 30%가 아니라 선순위 기부를 적용한 뒤의 근로소득금액에서 정한다. 종교기부가 있는 혼합한도 사례와 달리 정상 30% 한도만 요청한다.

집필 원고 ID: `A011`, 전체 문항 SHA-256: `e4c2a7a225251a2f0fd0115a89969048055131ca8bc29f92d5055245dc0ababb`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A011_e4c2a7a2/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_구호증명.pdf](../data/batch_2/A_yearend/B2_A011_e4c2a7a2/inputs/01_구호증명.pdf) (pdf)
- [02_공익증명.hwpx](../data/batch_2/A_yearend/B2_A011_e4c2a7a2/inputs/02_공익증명.hwpx) (hwpx)
- [03_소득자료.xlsx](../data/batch_2/A_yearend/B2_A011_e4c2a7a2/inputs/03_소득자료.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/A_yearend/B2_A011_e4c2a7a2/gold.json)

```json
{
  "donation_credit": 2385000,
  "final_national_tax": 0,
  "salary_income": 24500000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 1500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 10500000, "salary_income": 24500000, "total_salary": 35000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 2385000 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 2190000 |
| A_EMPLOYMENT_CREDIT | 724000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 2385000, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "specia... |
| A_FINAL | 0 |
| A_LOCAL | 0 |
| A_SETTLEMENT | {"local": 0, "national": 0, "total": 0} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A011_e4c2a7a2/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A013_accd50e7 (A_yearend, easy)

집필 제목: 부모 두 사람의 경로우대와 본인 장애 공제 분리

업무 목적: 동일 세대의 두 부모와 본인의 추가공제 사유를 사람별로 대조한다.

가상쌍솔원예의 가상제도윤은 장애인 직원이며 70세와 69세 부모 두 사람을 부양합니다. 가족 기본공제 인원과 기본공제액을 산출하고 본인 장애 및 부모 경로우대를 합한 추가공제액을 등록하세요.

설계 의도: 나이가 다른 두 부모 중 경로우대는 한 사람만 해당하고 장애인 공제는 직원 본인에게 있다. 모든 인적공제 사유를 동일인으로 잘못 몰아주는 입력을 확인한다.

집필 원고 ID: `A013`, 전체 문항 SHA-256: `accd50e743f3edf9feea64d66850e4985fdc53a6dfd7ff52fb015efe82d64b81`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A013_accd50e7/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_부모자격.pdf](../data/batch_2/A_yearend/B2_A013_accd50e7/inputs/01_부모자격.pdf) (pdf)
- [02_본인장애.hwpx](../data/batch_2/A_yearend/B2_A013_accd50e7/inputs/02_본인장애.hwpx) (hwpx)
- [03_급여.xlsx](../data/batch_2/A_yearend/B2_A013_accd50e7/inputs/03_급여.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/A_yearend/B2_A013_accd50e7/gold.json)

```json
{
  "additional_deduction": 3000000,
  "basic_deduction": 4500000,
  "eligible_dependents": 2
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 3000000, "basic": 4500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 12250000, "salary_income": 37750000, "total_salary": 50000000} |
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
| A_TAX_BRACKETS | 3277500 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special_inco... |
| A_FINAL | 2487500 |
| A_LOCAL | 248750 |
| A_SETTLEMENT | {"local": 248750, "national": 2487500, "total": 2736250} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A013_accd50e7/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A018_4de895cc (A_yearend, medium)

집필 제목: 적격 재활기관 수업의 학생 장애 자격 대조

업무 목적: 기관 유형과 학생 개인의 장애 자격을 별도 연결해 특수교육을 승인한다.

가상배움자격소의 가상강유하는 자녀 학교비와 법정 적격 특수교육 기관 수업료를 냈습니다. 기관 자격만으로 특수교육 공제를 승인하지 말고 학생의 세법상 장애인 증명을 대조하세요. 교육비 및 추가공제와 일반 자녀세액공제 결과를 작성합니다.

설계 의도: 기관은 적격이지만 해당 학생에게 장애인 자격이 없어 특수교육 비용을 인정하지 않는다. 정상 학교 교육비는 그대로 남고 학생 장애 자격이 바뀌면 교육비와 추가공제가 함께 변한다.

집필 원고 ID: `A018`, 전체 문항 SHA-256: `4de895ccbcb2ac374a95bf721e87472a2a4197d34ec954b43f73109e8cc60307`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A018_4de895cc/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_급여.xlsx](../data/batch_2/A_yearend/B2_A018_4de895cc/inputs/01_급여.xlsx) (xlsx)
- [02_학생자격.hwpx](../data/batch_2/A_yearend/B2_A018_4de895cc/inputs/02_학생자격.hwpx) (hwpx)
- [03_학교비.pdf](../data/batch_2/A_yearend/B2_A018_4de895cc/inputs/03_학교비.pdf) (pdf)
- [04_재활교육.pdf](../data/batch_2/A_yearend/B2_A018_4de895cc/inputs/04_재활교육.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A018_4de895cc/gold.json)

```json
{
  "additional_deduction": 0,
  "child_credit": 250000,
  "education_credit": 405000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"education.0.excluded": false, "education.1.excluded": false} |
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 12550000, "salary_income": 43450000, "total_salary": 56000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 405000 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 4807500 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 405000, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 3492500 |
| A_LOCAL | 349250 |
| A_SETTLEMENT | {"local": 349250, "national": 3492500, "total": 3841750} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A018_4de895cc/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A025_b6e2238e (A_yearend, medium)

집필 제목: 퇴직 후 미숙아 진료와 재직 중 자녀 진료를 분리

업무 목적: 높은 공제율 의료비라도 실제 납부가 근로기간 밖이면 제외하는 퇴직자 마감이다.

가상조용한항로의 가상허여울은 7세 자녀의 일반 치료와 갓 태어난 자녀의 미숙아 진료를 제출했습니다. 미숙아 진료의 실제 납부가 퇴직 뒤였는지 확인해 의료비 세액공제를 계산하고 두 자녀의 자녀세액공제를 작성하세요.

설계 의도: 두 아이 모두 여덟 살 미만이므로 일반 자녀세액공제와 출생 공제를 구별한다. 미숙아 지출의 고율은 기간 제외를 이길 수 없으며 재직 중 7세 아이 지출은 남는다.

집필 원고 ID: `A025`, 전체 문항 SHA-256: `b6e2238e4448d537c29423466b78d6a31d7d9e89142f93729bd9e3c2e7eb3269`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A025_b6e2238e/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_퇴직마감.xlsx](../data/batch_2/A_yearend/B2_A025_b6e2238e/inputs/01_퇴직마감.xlsx) (xlsx)
- [02_자녀등록.hwpx](../data/batch_2/A_yearend/B2_A025_b6e2238e/inputs/02_자녀등록.hwpx) (hwpx)
- [03_큰아이진료.pdf](../data/batch_2/A_yearend/B2_A025_b6e2238e/inputs/03_큰아이진료.pdf) (pdf)
- [04_아기진료.pdf](../data/batch_2/A_yearend/B2_A025_b6e2238e/inputs/04_아기진료.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A025_b6e2238e/gold.json)

```json
{
  "basic_deduction": 4500000,
  "child_credit": 500000,
  "medical_credit": 292500
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 4500000, "rejected": []} |
| A_SALARY | {"salary_deduction": 10500000, "salary_income": 24500000, "total_salary": 35000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 500000 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 292500 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 1740000 |
| A_EMPLOYMENT_CREDIT | 724000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 292500, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 223500 |
| A_LOCAL | 22350 |
| A_SETTLEMENT | {"local": 22350, "national": 223500, "total": 245850} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A025_b6e2238e/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A026_f40670e0 (A_yearend, medium)

집필 제목: 고교 졸업과 대학 입학 연도의 학교별 한도 연결

업무 목적: 학교에서 대학으로 바뀐 한 사람의 연간 교육비를 학교 순서와 무관하게 합산한다.

가상새학기기록의 가상전지후는 자녀의 고교 마지막 학기와 대학 첫 학기 납부증명을 제출했습니다. 학교급이 달라진 같은 자녀의 수업료를 각각의 제한과 연간 한도에 반영해 교육비 세액공제를 산출하세요. 자녀 기본공제와 일반 자녀세액공제도 적습니다.

설계 의도: 고교 원액과 대학 비용의 단순 합계는9백만원을 넘지만 고교 소한도를 먼저 적용하면 연간 인정액은870만원으로 내려간다. 마지막 영수증의 학교급으로 전체 한도를 고르는 계산을 점검한다.

집필 원고 ID: `A026`, 전체 문항 SHA-256: `f40670e091cd6cf024d1958f3fed0d8779b2bdf96bf04483f5398daa0ce3ba12`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A026_f40670e0/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_급여.xlsx](../data/batch_2/A_yearend/B2_A026_f40670e0/inputs/01_급여.xlsx) (xlsx)
- [02_자녀.hwpx](../data/batch_2/A_yearend/B2_A026_f40670e0/inputs/02_자녀.hwpx) (hwpx)
- [03_고교.pdf](../data/batch_2/A_yearend/B2_A026_f40670e0/inputs/03_고교.pdf) (pdf)
- [04_대학.pdf](../data/batch_2/A_yearend/B2_A026_f40670e0/inputs/04_대학.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A026_f40670e0/gold.json)

```json
{
  "basic_deduction": 3000000,
  "child_credit": 250000,
  "education_credit": 1305000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13000000, "salary_income": 52000000, "total_salary": 65000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 1305000 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 6090000 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 1305000, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "specia... |
| A_FINAL | 3875000 |
| A_LOCAL | 387500 |
| A_SETTLEMENT | {"local": 387500, "national": 3875000, "total": 4262500} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A026_f40670e0/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A030_a79bb236 (A_yearend, medium)

집필 제목: 학교 수업료와 학원 직불 사용의 이중 항목 정리

업무 목적: 학원 비용의 교육비 거절이 정상 카드 사용까지 취소하는지 확인한다.

가상가지교구의 가상권모아는 자녀 학교 수업료와 사설학원비를 제출했습니다. 학교급과 기관 유형을 대조해 교육비 세액공제를 작성하고, 별도 직불카드 명세의 학원 결제를 카드 소득공제로 처리하세요. 학교 수업료는 카드 명세에 포함되지 않았습니다.

설계 의도: 학교의 정상 수업료와 사설학원의 교육비 불인정은 기관 유형으로 분리한다. 학원비가 직불 일반 사용에 남는 연결 때문에 같은 제외를 카드 항목에 복제할 수 없다.

집필 원고 ID: `A030`, 전체 문항 SHA-256: `a79bb236663c312cafb6d2face77029fcbcb9d4a795e59e6bcfd364fec2f39ca`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A030_a79bb236/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_가족급여.xlsx](../data/batch_2/A_yearend/B2_A030_a79bb236/inputs/01_가족급여.xlsx) (xlsx)
- [02_학교.pdf](../data/batch_2/A_yearend/B2_A030_a79bb236/inputs/02_학교.pdf) (pdf)
- [03_학원.hwpx](../data/batch_2/A_yearend/B2_A030_a79bb236/inputs/03_학원.hwpx) (hwpx)
- [04_직불.pdf](../data/batch_2/A_yearend/B2_A030_a79bb236/inputs/04_직불.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A030_a79bb236/gold.json)

```json
{
  "child_credit": 250000,
  "credit_card_deduction": 450000,
  "education_credit": 195000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"cards.0.excluded": false, "cards.1.excluded": false, "education.0.excluded": false, "education.1.excluded": true} |
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 11550000, "salary_income": 30450000, "total_salary": 42000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 450000 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 195000 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 2790000 |
| A_EMPLOYMENT_CREDIT | 668000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 195000, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 1677000 |
| A_LOCAL | 167700 |
| A_SETTLEMENT | {"local": 167700, "national": 1677000, "total": 1844700} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A030_a79bb236/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A034_09c96501 (A_yearend, medium)

집필 제목: 연간 비과세 정정본으로 월세 공제율 마감

업무 목적: 지급총액이 같은 원천 정정이 월세율을 바꾸는 주거 접수를 마감한다.

가상고친주거의 가상민소율은 같은 지급기간의 두 원천증명서와 적격 월세 자료를 제출했습니다. 비과세가 정정된 최고 발급 수정차수로 연간 총급여를 확정한 다음 월세 공제율을 선택하세요. 채택 및 제외 번호와 비과세 합계 및 월세 계산 결과를 포함한 세금 객체를 회신합니다.

설계 의도: 새 발급본의 비과세는 7백만원으로 정정되어 총급여가 5천5백만원 이하가 된다. 이전본과 최신본은 서로 다른 급여가 아니며 이전 3백만원 비과세를 적용하면 적격 월세의 공제율만 낮아진다.

집필 원고 ID: `A034`, 전체 문항 SHA-256: `09c96501e0b595b6150ec932401f1e1980ff9cb9163a92cdf1c3989f1cbd5a6d`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A034_09c96501/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_원천이전.xlsx](../data/batch_2/A_yearend/B2_A034_09c96501/inputs/01_원천이전.xlsx) (xlsx)
- [02_원천정정.pdf](../data/batch_2/A_yearend/B2_A034_09c96501/inputs/02_원천정정.pdf) (pdf)
- [03_임대차.hwpx](../data/batch_2/A_yearend/B2_A034_09c96501/inputs/03_임대차.hwpx) (hwpx)
- [04_접수확인.pdf](../data/batch_2/A_yearend/B2_A034_09c96501/inputs/04_접수확인.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A034_09c96501/gold.json)

```json
{
  "excluded_statement_ids": [
    "SY-OLD"
  ],
  "non_taxable": 7000000,
  "tax_calculation": {
    "additional_deduction": 0,
    "basic_deduction": 1500000,
    "child_credit": 0,
    "computed_tax": 4605000,
    "credit_card_deduction": 0,
    "donation_credit": 0,
    "education_credit": 0,
    "eligible_dependents": 0,
    "employment_credit": 660000,
    "final_local_tax": 258500,
    "final_national_tax": 2585000,
    "hometown_credit": 0,
    "housing_income_deduction": 0,
    "income_deduction_limit_excess": 0,
    "insurance_credit": 0,
    "medical_credit": 0,
    "paid_local_tax": 450000,
    "paid_national_tax": 4500000,
    "pension_account_credit": 0,
    "pension_deduction": 0,
    "political_credit": 0,
    "rent_credit": 1360000,
    "salary_deduction": 12400000,
    "salary_income": 40600000,
    "settlement_local_tax": -191500,
    "settlement_national_tax": -1915000,
    "settlement_total": -2106500,
    "special_income_deduction": 0,
    "standard_credit": 0,
    "tax_base": 39100000,
    "total_salary": 53000000,
    "total_tax_credits": 2020000
  },
  "used_statement_ids": [
    "SY-NEW"
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PAY_STATEMENT_RECONCILIATION | {"annual_gross": 60000000, "employer_totals": [{"employer_id": "고친주거", "gross_pay": 60000000, "non_taxable_pay": 7000000, "withheld_local_tax": 450000, "withheld_national_tax": 4500000}], "excluded_statement_ids": ["SY-OLD"], "... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A034_09c96501/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A039_88d61485 (A_yearend, hard)

집필 제목: 일반 의료비 한도 뒤 남는 고율 진료의 합산 승인

업무 목적: 다수 의료 청구를 사람 자격과 순부담 및 공제율의 세 축으로 정리한다.

가상통합치료기록의 가상윤아리는 배우자 일반 치료와 본인 치료 및 난임 시술을 함께 제출했습니다. 사람별 일반 한도와 보전금을 정리하고 총급여 문턱을 공제율 순서에 맞게 사용해 의료비 세액공제를 계산하세요. 배우자 기본공제와 최종 국세도 작성합니다.

설계 의도: 배우자 일반 치료는 대응 보전금을 차감하면 문턱 이후 인정액이 7백만원보다 작지만 보전을 누락하면 제한에 걸린다. 본인 치료 및 난임은 별도율로 이어지고 미용 제외도 독립적으로 요청한 의료비를 바꾼다.

집필 원고 ID: `A039`, 전체 문항 SHA-256: `88d61485cef3e824bb5e4cdc6b73831982bf6ab76add8cbf3650c920452c735a`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A039_88d61485/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_급여.xlsx](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/01_급여.xlsx) (xlsx)
- [02_배우자.hwpx](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/02_배우자.hwpx) (hwpx)
- [03_입원.pdf](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/03_입원.pdf) (pdf)
- [04_실손.xlsx](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/04_실손.xlsx) (xlsx)
- [05_후속진료.pdf](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/05_후속진료.pdf) (pdf)
- [06_본인치료.pdf](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/06_본인치료.pdf) (pdf)
- [07_난임1.hwpx](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/07_난임1.hwpx) (hwpx)
- [08_난임2.pdf](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/08_난임2.pdf) (pdf)
- [09_미용.pdf](../data/batch_2/A_yearend/B2_A039_88d61485/inputs/09_미용.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A039_88d61485/gold.json)

```json
{
  "basic_deduction": 3000000,
  "final_national_tax": 2527500,
  "medical_credit": 2902500
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"medical.0.excluded": false, "medical.1.excluded": false, "medical.2.excluded": false, "medical.3.excluded": false, "medical.4.excluded": false, "medical.5.excluded": true} |
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 13000000, "salary_income": 52000000, "total_salary": 65000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 2902500 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 6090000 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 2902500, "political_credit": 0, "rent_credit": 0}, "specia... |
| A_FINAL | 2527500 |
| A_LOCAL | 252750 |
| A_SETTLEMENT | {"local": 252750, "national": 2527500, "total": 2780250} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A039_88d61485/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A043_f0337a1f (A_yearend, hard)

집필 제목: 같은 주소 세대원 월세와 배우자 배정 아이의 학비 마감

업무 목적: 주택 공제의 세대 중복과 가족 기본공제의 개인 배정을 별도로 마감한다.

가상나눠진집의 가상심하은은 세대원으로 월세를 납부했지만 세대주가 주택 공제를 신청했습니다. 부부가 서로 다른 아이를 배정한 최종 기록도 확인해 월세와 아이별 교육비 및 자녀세액공제 결과를 작성하세요. 직원 본인 일반보험은 정상 반영합니다.

설계 의도: 월세 주소와 무주택 사실은 정상이어도 세대주의 신청이 세대원 월세를 막는다. 아이 둘의 납부는 동일 학교지만 최종 배정이 달라 한쪽 학비만 남는다.

집필 원고 ID: `A043`, 전체 문항 SHA-256: `f0337a1ff6ecaddf0810de9b47870da077e369944d60f79fc319177ae61a56a1`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A043_f0337a1f/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_급여.xlsx](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/01_급여.xlsx) (xlsx)
- [02_가족배정.hwpx](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/02_가족배정.hwpx) (hwpx)
- [03_계약.pdf](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/03_계약.pdf) (pdf)
- [04_세대.hwpx](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/04_세대.hwpx) (hwpx)
- [05_상반기월세.xlsx](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/05_상반기월세.xlsx) (xlsx)
- [06_하반기월세.xlsx](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/06_하반기월세.xlsx) (xlsx)
- [07_첫아이학비.pdf](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/07_첫아이학비.pdf) (pdf)
- [08_둘째학비.pdf](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/08_둘째학비.pdf) (pdf)
- [09_본인보험.pdf](../data/batch_2/A_yearend/B2_A043_f0337a1f/inputs/09_본인보험.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A043_f0337a1f/gold.json)

```json
{
  "child_credit": 250000,
  "education_credit": 255000,
  "insurance_credit": 94800,
  "rent_credit": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"rent.address_matches": true, "rent.homeless_household": true} |
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": ["first"]} |
| A_SALARY | {"salary_deduction": 12450000, "salary_income": 41550000, "total_salary": 54000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 94800 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 255000 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 4522500 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 255000, "hometown_credit": 0, "insurance_credit": 94800, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "spe... |
| A_FINAL | 3262700 |
| A_LOCAL | 326270 |
| A_SETTLEMENT | {"local": 326270, "national": 3262700, "total": 3588970} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A043_f0337a1f/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A044_7e551535 (A_yearend, hard)

집필 제목: 지정 종료 종교기부가 공익 한도 계산에 남는지 확인

업무 목적: 불인정 종교 영수증의 존재만으로 혼합 종교 한도를 선택하지 않는다.

가상기부분류소의 가상유담서는 특례 및 공익과 종교기부를 제출했습니다. 지정이 종료된 종교 영수증을 먼저 정리하고 실제 인정 기부 종류에 따라 남은 소득 한도를 적용하세요. 근로소득금액과 일반 기부 세액공제를 각각 적고 가족 공제 인원도 확인합니다.

설계 의도: 일반 기부 한도 식은 인정 종교기부의 존재에 좌우된다. 지정 종료 종교 건과 다른 배정 가족의 기부를 제거하면 남은 공익 및 특례기부만으로 한도를 계산해야 한다.

집필 원고 ID: `A044`, 전체 문항 SHA-256: `7e5515350d182bebb9a5383db7f8513a6b14c6f50490ad40e820a2b4fa458dee`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A044_7e551535/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_001_050.json)

입력 파일:

- [01_급여.xlsx](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/01_급여.xlsx) (xlsx)
- [02_아버지.hwpx](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/02_아버지.hwpx) (hwpx)
- [03_특례대장.pdf](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/03_특례대장.pdf) (pdf)
- [04_공익대장.pdf](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/04_공익대장.pdf) (pdf)
- [05_종교대장.pdf](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/05_종교대장.pdf) (pdf)
- [06_첫특례.hwpx](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/06_첫특례.hwpx) (hwpx)
- [07_특례.pdf](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/07_특례.pdf) (pdf)
- [08_공익.pdf](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/08_공익.pdf) (pdf)
- [09_종교.pdf](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/09_종교.pdf) (pdf)
- [10_부모기부.pdf](../data/batch_2/A_yearend/B2_A044_7e551535/inputs/10_부모기부.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A044_7e551535/gold.json)

```json
{
  "donation_credit": 3654000,
  "eligible_dependents": 0,
  "final_national_tax": 2730000,
  "salary_income": 54850000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"donations.0.eligible_organization": true, "donations.1.eligible_organization": true, "donations.2.eligible_organization": true, "donations.3.eligible_organization": false, "donations.4.eligible_organization": true} |
| A_PERSONAL | {"additional": 0, "basic": 1500000, "rejected": ["father"]} |
| A_SALARY | {"salary_deduction": 13150000, "salary_income": 54850000, "total_salary": 68000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 0 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 3654000 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 7044000 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 3654000, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 0, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "specia... |
| A_FINAL | 2730000 |
| A_LOCAL | 273000 |
| A_SETTLEMENT | {"local": 273000, "national": 2730000, "total": 3003000} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A044_7e551535/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A060_02857b51 (A_yearend, easy)

집필 제목: 최신 원천의 재전송과 지난 기간의 같은 금액 지급 구별

업무 목적: 최신 발급본의 중복 전달 제거와 지급기간별 정정 효력을 함께 적용해 실제 두 기간의 원천 징수를 마감한다.

가상새봄의 원천 발급번호와 지급기간을 대조하세요. 하반기 최신본은 같은 번호와 내용으로 두 번 도착했고 상반기 지급은 금액이 같아도 별도 기간입니다. 최신 하반기를 한 번 선택하고 실제 상반기도 합산하여 연간 기납부액 및 전체 세금 객체를 제출합니다.

설계 의도: 정정 전 하반기 원천과 최신본 재전송을 서로 다른 이유로 제외한다. 최신본의 복사 전달은 한 번이고 같은 사용자에게 같은 금액을 받은 상반기는 남겨야 한다. 금액 중복 제거와 최대 차수 하나 선택을 어느 순서로 적용해도 실제 기간 귀속을 대신할 수 없다.

집필 원고 ID: `A060`, 전체 문항 SHA-256: `02857b5135fdc54ade359456582ac03761ee66454e1b8d75afddf5420a10d304`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A060_02857b51/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_051_100.json)

입력 파일:

- [01_상반기.pdf](../data/batch_2/A_yearend/B2_A060_02857b51/inputs/01_상반기.pdf) (pdf)
- [02_하반기.xlsx](../data/batch_2/A_yearend/B2_A060_02857b51/inputs/02_하반기.xlsx) (xlsx)
- [03_연간접수.hwpx](../data/batch_2/A_yearend/B2_A060_02857b51/inputs/03_연간접수.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/A_yearend/B2_A060_02857b51/gold.json)

```json
{
  "employer_totals": [
    {
      "employer_id": "가상인화소",
      "gross_pay": 56000000,
      "non_taxable_pay": 2000000,
      "withheld_local_tax": 270000,
      "withheld_national_tax": 2700000
    }
  ],
  "excluded_statement_ids": [
    "SB-SECOND-1"
  ],
  "paid_local_tax": 270000,
  "paid_national_tax": 2700000,
  "tax_calculation": {
    "additional_deduction": 0,
    "basic_deduction": 1500000,
    "child_credit": 0,
    "computed_tax": 4747500,
    "credit_card_deduction": 0,
    "donation_credit": 0,
    "education_credit": 0,
    "eligible_dependents": 0,
    "employment_credit": 660000,
    "final_local_tax": 395750,
    "final_national_tax": 3957500,
    "hometown_credit": 0,
    "housing_income_deduction": 0,
    "income_deduction_limit_excess": 0,
    "insurance_credit": 0,
    "medical_credit": 0,
    "paid_local_tax": 270000,
    "paid_national_tax": 2700000,
    "pension_account_credit": 0,
    "pension_deduction": 0,
    "political_credit": 0,
    "rent_credit": 0,
    "salary_deduction": 12450000,
    "salary_income": 41550000,
    "settlement_local_tax": 125750,
    "settlement_national_tax": 1257500,
    "settlement_total": 1383250,
    "special_income_deduction": 0,
    "standard_credit": 130000,
    "tax_base": 40050000,
    "total_salary": 54000000,
    "total_tax_credits": 790000
  },
  "used_statement_ids": [
    "SB-FIRST",
    "SB-SECOND-2"
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PAY_STATEMENT_RECONCILIATION | {"annual_gross": 56000000, "employer_totals": [{"employer_id": "가상인화소", "gross_pay": 56000000, "non_taxable_pay": 2000000, "withheld_local_tax": 270000, "withheld_national_tax": 2700000}], "excluded_statement_ids": ["SB-SECOND-... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A060_02857b51/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A069_f4bd2703 (A_yearend, medium)

집필 제목: 보너스 수정으로 근로세액공제 한도와 비과세 분리

업무 목적: 실제 보너스 수정이 근로세액공제의 급여별 제한을 바꾸는지 대조한다.

가상우림의 연간 보너스가 반영된 발급 정정본을 선택하세요. 비과세 지급을 분리하여 총급여와 근로소득세액공제 한도를 계산하고 채택 및 제외 번호와 전체 세금 계산 객체를 회신합니다.

설계 의도: 이전 지급은 7천만원 이하 한도 구간이고 보너스 정정 후에는 그 구간을 넘는다. 산출세액에서 계산한 공제 원액과 급여별 한도가 동시에 바뀌므로 보너스만 별도 세금으로 계산하지 않는다.

집필 원고 ID: `A069`, 전체 문항 SHA-256: `f4bd2703db34ece5c968b6082cf7f93156dcc46da895052d5dde19d784d16ce9`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A069_f4bd2703/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_051_100.json)

입력 파일:

- [01_기존.pdf](../data/batch_2/A_yearend/B2_A069_f4bd2703/inputs/01_기존.pdf) (pdf)
- [02_보너스.xlsx](../data/batch_2/A_yearend/B2_A069_f4bd2703/inputs/02_보너스.xlsx) (xlsx)
- [03_연금.hwpx](../data/batch_2/A_yearend/B2_A069_f4bd2703/inputs/03_연금.hwpx) (hwpx)
- [04_접수.pdf](../data/batch_2/A_yearend/B2_A069_f4bd2703/inputs/04_접수.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A069_f4bd2703/gold.json)

```json
{
  "annual_gross": 74000000,
  "excluded_statement_ids": [
    "WOO-OLD"
  ],
  "tax_calculation": {
    "additional_deduction": 0,
    "basic_deduction": 1500000,
    "child_credit": 0,
    "computed_tax": 7140000,
    "credit_card_deduction": 0,
    "donation_credit": 0,
    "education_credit": 0,
    "eligible_dependents": 0,
    "employment_credit": 500000,
    "final_local_tax": 651000,
    "final_national_tax": 6510000,
    "hometown_credit": 0,
    "housing_income_deduction": 0,
    "income_deduction_limit_excess": 0,
    "insurance_credit": 0,
    "medical_credit": 0,
    "paid_local_tax": 660000,
    "paid_national_tax": 6600000,
    "pension_account_credit": 0,
    "pension_deduction": 3400000,
    "political_credit": 0,
    "rent_credit": 0,
    "salary_deduction": 13350000,
    "salary_income": 58650000,
    "settlement_local_tax": -9000,
    "settlement_national_tax": -90000,
    "settlement_total": -99000,
    "special_income_deduction": 0,
    "standard_credit": 130000,
    "tax_base": 53750000,
    "total_salary": 72000000,
    "total_tax_credits": 630000
  },
  "used_statement_ids": [
    "WOO-NEW"
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PAY_STATEMENT_RECONCILIATION | {"annual_gross": 74000000, "employer_totals": [{"employer_id": "가상합금", "gross_pay": 74000000, "non_taxable_pay": 2000000, "withheld_local_tax": 660000, "withheld_national_tax": 6600000}], "excluded_statement_ids": ["WOO-OLD"], ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A069_f4bd2703/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A084_02ad0529 (A_yearend, medium)

집필 제목: 배우자 소유 주택과 가족 명의 임차의 무주택 확인

업무 목적: 가족 명의가 적격이어도 같은 세대 보유 주택이 월세에 미치는 영향을 확인한다.

가상태민의 배우자 명의 임대차와 연말 세대 주택 목록을 대조하세요. 가족 계약자 자격과 세대 무주택 요건을 각각 확인하고 배우자 자비 보험료를 별도로 처리해 월세 및 보험 공제액을 제출합니다.

설계 의도: 배우자는 무소득 기본공제 가족이어서 명의는 맞지만 배우자 소유 주택이 세대 주택 목록에 실제 존재한다. 가족 자격과 주택 보유 판단을 구분해야 보험은 유지하고 월세만 제외할 수 있다.

집필 원고 ID: `A084`, 전체 문항 SHA-256: `02ad05291d182ad386edbbe127da24ec1dbde2be33a25b92b1d0fab9cefd72b6`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A084_02ad0529/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_051_100.json)

입력 파일:

- [01_급여.xlsx](../data/batch_2/A_yearend/B2_A084_02ad0529/inputs/01_급여.xlsx) (xlsx)
- [02_임차.pdf](../data/batch_2/A_yearend/B2_A084_02ad0529/inputs/02_임차.pdf) (pdf)
- [03_주택.hwpx](../data/batch_2/A_yearend/B2_A084_02ad0529/inputs/03_주택.hwpx) (hwpx)
- [04_보험.pdf](../data/batch_2/A_yearend/B2_A084_02ad0529/inputs/04_보험.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A084_02ad0529/gold.json)

```json
{
  "eligible_dependents": 1,
  "insurance_credit": 110400,
  "rent_credit": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"rent.address_matches": true, "rent.eligible_contract_holder": true, "rent.homeless_household": false} |
| A_PERSONAL | {"additional": 0, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 12700000, "salary_income": 46300000, "total_salary": 59000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 0 |
| A_INSURANCE_CREDIT | 110400 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 0 |
| A_TAX_BRACKETS | 5235000 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 110400, "medical_credit": 0, "political_credit": 0, "rent_credit": 0}, "special... |
| A_FINAL | 4464600 |
| A_LOCAL | 446460 |
| A_SETTLEMENT | {"local": 446460, "national": 4464600, "total": 4911060} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A084_02ad0529/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A086_8dfcda80 (A_yearend, medium)

집필 제목: 고차수 전직장과 병행 사용자 이자로 소득공제 제한 확인

업무 목적: 사용자별 원천 선택과 주택 및 카드 종합 소득공제 제한의 순서를 마감한다.

가상나래의 전 직장 정정본과 별도 사용자 원천 자료를 모두 검토하세요. 합산 소득에 적격 장기 주택이자 및 본인 직불 소비를 반영하고 종합 소득공제 초과액까지 세금 계산 객체로 제출합니다.

설계 의도: 정정된 높은 차수는 같은 사용자의 이전본에만 적용한다. 다른 사용자 급여를 함께 계산해야 카드 문턱과 과세표준이 맞고 주택이자와 카드 제한은 다시 한 번 연간으로 적용한다.

집필 원고 ID: `A086`, 전체 문항 SHA-256: `8dfcda80403a7e877f9b5b0bafbd92fba3498c6310fce16f24b5aa60d2e85f06`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A086_8dfcda80/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_051_100.json)

입력 파일:

- [01_구본.pdf](../data/batch_2/A_yearend/B2_A086_8dfcda80/inputs/01_구본.pdf) (pdf)
- [02_수정.xlsx](../data/batch_2/A_yearend/B2_A086_8dfcda80/inputs/02_수정.xlsx) (xlsx)
- [03_교정.hwpx](../data/batch_2/A_yearend/B2_A086_8dfcda80/inputs/03_교정.hwpx) (hwpx)
- [04_주택.pdf](../data/batch_2/A_yearend/B2_A086_8dfcda80/inputs/04_주택.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A086_8dfcda80/gold.json)

```json
{
  "employer_totals": [
    {
      "employer_id": "가상교정",
      "gross_pay": 22000000,
      "non_taxable_pay": 0,
      "withheld_local_tax": 80000,
      "withheld_national_tax": 800000
    },
    {
      "employer_id": "가상인쇄",
      "gross_pay": 47000000,
      "non_taxable_pay": 1000000,
      "withheld_local_tax": 250000,
      "withheld_national_tax": 2500000
    }
  ],
  "excluded_statement_ids": [
    "NAR-A1"
  ],
  "tax_calculation": {
    "additional_deduction": 0,
    "basic_deduction": 1500000,
    "child_credit": 0,
    "computed_tax": 2992500,
    "credit_card_deduction": 6000000,
    "donation_credit": 0,
    "education_credit": 0,
    "eligible_dependents": 0,
    "employment_credit": 660000,
    "final_local_tax": 233250,
    "final_national_tax": 2332500,
    "hometown_credit": 0,
    "housing_income_deduction": 20000000,
    "income_deduction_limit_excess": 1000000,
    "insurance_credit": 0,
    "medical_credit": 0,
    "paid_local_tax": 330000,
    "paid_national_tax": 3300000,
    "pension_account_credit": 0,
    "pension_deduction": 0,
    "political_credit": 0,
    "rent_credit": 0,
    "salary_deduction": 13150000,
    "salary_income": 54850000,
    "settlement_local_tax": -96750,
    "settlement_national_tax": -967500,
    "settlement_total": -1064250,
    "special_income_deduction": 0,
    "standard_credit": 0,
    "tax_base": 28350000,
    "total_salary": 68000000,
    "total_tax_credits": 660000
  },
  "used_statement_ids": [
    "NAR-A4",
    "NAR-B1"
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_PAY_STATEMENT_RECONCILIATION | {"annual_gross": 69000000, "employer_totals": [{"employer_id": "가상교정", "gross_pay": 22000000, "non_taxable_pay": 0, "withheld_local_tax": 80000, "withheld_national_tax": 800000}, {"employer_id": "가상인쇄", "gross_pay": 47000000, "... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A086_8dfcda80/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_A087_c35c65d5 (A_yearend, medium)

집필 제목: 장애 성년 자녀 계약과 전용보험 피보험자 연결

업무 목적: 장애 증명을 가족 계약 명의의 나이 예외와 전용보험의 별도 세율에 각각 연결한다.

가상윤재의 성년 장애인 자녀 명의 임대차를 인적관계 명부에 연결하세요. 자녀의 기본공제 나이 예외와 장애인 전용 보장성보험의 피보험자 요건을 함께 검토하여 기본공제 및 추가공제와 월세 및 보험료 공제액을 제출합니다.

설계 의도: 자녀는 24세이지만 법정 장애인으로 기본공제에 포함되어 가족 명의 월세가 인정된다. 같은 person_id의 장애 사실은 전용보험 공제율에도 별도 작용하므로 성년 일반 자녀의 학부 교육 문제를 반복하지 않는다.

집필 원고 ID: `A087`, 전체 문항 SHA-256: `c35c65d5c6ffb8c11f72545ece4706999d68bc4e58c2f21e7a5377c6364977b8`

[문항 메타데이터](../data/batch_2/A_yearend/B2_A087_c35c65d5/task.yaml)와 [집필 원고](../authored/batch_2/A_yearend/cases_051_100.json)

입력 파일:

- [01_급여.xlsx](../data/batch_2/A_yearend/B2_A087_c35c65d5/inputs/01_급여.xlsx) (xlsx)
- [02_임차.pdf](../data/batch_2/A_yearend/B2_A087_c35c65d5/inputs/02_임차.pdf) (pdf)
- [03_세대.hwpx](../data/batch_2/A_yearend/B2_A087_c35c65d5/inputs/03_세대.hwpx) (hwpx)
- [04_전용보험.pdf](../data/batch_2/A_yearend/B2_A087_c35c65d5/inputs/04_전용보험.pdf) (pdf)

정답: [gold.json](../data/batch_2/A_yearend/B2_A087_c35c65d5/gold.json)

```json
{
  "additional_deduction": 3000000,
  "eligible_dependents": 1,
  "insurance_credit": 132000,
  "rent_credit": 1156000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| A_EVIDENCE_RECONCILIATION | {"rent.address_matches": true, "rent.eligible_contract_holder": true, "rent.homeless_household": true} |
| A_PERSONAL | {"additional": 3000000, "basic": 3000000, "rejected": []} |
| A_SALARY | {"salary_deduction": 12250000, "salary_income": 37750000, "total_salary": 50000000} |
| A_PENSION_DEDUCTION | 0 |
| A_SPECIAL_DEDUCTION | 0 |
| A_HOUSING | 0 |
| A_CARD | 0 |
| A_PENSION_CREDIT | 0 |
| A_CHILD | 250000 |
| A_INSURANCE_CREDIT | 132000 |
| A_MEDICAL_CREDIT | 0 |
| A_EDUCATION_CREDIT | 0 |
| A_DONATION_CREDIT | 0 |
| A_POLITICAL_CREDIT | 0 |
| A_HOMETOWN_CREDIT | 0 |
| A_RENT_CREDIT | 1156000 |
| A_TAX_BRACKETS | 3502500 |
| A_EMPLOYMENT_CREDIT | 660000 |
| A_STANDARD | {"housing_deduction_applied": 0, "special_credits_applied": {"donation_credit": 0, "education_credit": 0, "hometown_credit": 0, "insurance_credit": 132000, "medical_credit": 0, "political_credit": 0, "rent_credit": 1156000}, "s... |
| A_FINAL | 1304500 |
| A_LOCAL | 130450 |
| A_SETTLEMENT | {"local": 130450, "national": 1304500, "total": 1434950} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/A_yearend/B2_A087_c35c65d5/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B005_9b399ad1 (B_payroll, easy)

집필 제목: 시급 개근 대가와 주휴를 한 번 공제한 뒤 현금 대조

업무 목적: 시급제 월 명세의 실제근로와 주별 개근을 합쳐 공제한 뒤 실행 현금을 확인한다.

가상문화접수는 단시간 직원의 한 달 전체 근무와 개근 주를 마감했습니다. 출근 카드의 실제 근로와 주휴를 함께 계산하여 월 명세를 만들고 같은 지급일의 한 실행 이체와 대조해 주세요. payroll_calculations와 balance_total을 요청합니다. 주휴를 별도 명세로 원천징수하지 않습니다.

설계 의도: Batch1 B154의 출근 합산 이후에 완전 월 명세와 은행 실행의 차이를 확인한다. B004와 달리 근로 자체가 기본급이고 개근 주가 별도 지급을 만들며 두 자료가 은행 잔액에 합류한다.

집필 원고 ID: `B005`, 전체 문항 SHA-256: `9b399ad173e1ad3d7c26f0b4b73d68a55273679c22807ca3639a9dc0898ed4a3`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B005_9b399ad1/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_001_050.json)

입력 파일:

- [01_근로와개근.hwpx](../data/batch_2/B_payroll/B2_B005_9b399ad1/inputs/01_근로와개근.hwpx) (hwpx)
- [02_실행확인.xlsx](../data/batch_2/B_payroll/B2_B005_9b399ad1/inputs/02_실행확인.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B005_9b399ad1/gold.json)

```json
{
  "balance_total": 28120,
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 360000,
        "effective_payment_date": "2026-11-20",
        "employment_insurance": 3880,
        "fixed_allowance": 0,
        "gross_pay": 432000,
        "health_insurance": 0,
        "holiday_pay": 0,
        "income_tax": 0,
        "local_income_tax": 0,
        "long_term_care": 0,
        "meal_allowance": 0,
        "national_pension": 0,
        "net_pay": 428120,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 12000,
        "ordinary_monthly_wage": 0,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 410000,
        "taxable_pay": 432000,
        "total_deductions": 3880,
        "variable_allowance": 0,
        "weekly_holiday_pay": 72000
      },
      "employee_id": "CULTURE-11",
      "payroll_id": "CULTURE-NOV"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["CULTURE-PAY"], "cash_by_payroll": [{"paid": 400000, "payroll_id": "CULTURE-NOV"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": [], "payroll_derivations": [{"payroll_id": "CULTURE-NOV", ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B005_9b399ad1/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B025_e56fa436 (B_payroll, medium)

집필 제목: 완료금은 지급하되 추가 시급 분자에 넣지 않는 현금 정산

업무 목적: 변동 완료금의 지급 포함과 통상임금 제외가 하나의 최종 현금 잔액으로 이어짐을 확인한다.

가상목공실의 당월 완료금은 실제 지급하지만 소정근로 대가인 고정 수당은 아닙니다. 승인 추가근로의 정확한 통상시급에는 완료금을 제외한 뒤 완전 월 총지급과 공제를 계산하여 실제 두 송금과 대조하세요. payroll_calculations와 balance_total을 요청합니다.

설계 의도: B007에는 변동 완료금이 없지만 이 문항은 같은 사실이 총지급에는 포함되고 추가 시간 단가에서는 제외된다. 완료금과 추가근로를 독립 정상 계산으로 따로 요청하지 않고 완전 명세 및 실행에 합류시킨다.

집필 원고 ID: `B025`, 전체 문항 SHA-256: `e56fa4366de742b8bae984b911a134b17a1e88022e3c9cb63e214ac7f3be6828`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B025_e56fa436/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_001_050.json)

입력 파일:

- [01_지급기준.pdf](../data/batch_2/B_payroll/B2_B025_e56fa436/inputs/01_지급기준.pdf) (pdf)
- [02_완료및근태.hwpx](../data/batch_2/B_payroll/B2_B025_e56fa436/inputs/02_완료및근태.hwpx) (hwpx)
- [03_정기실행.xlsx](../data/batch_2/B_payroll/B2_B025_e56fa436/inputs/03_정기실행.xlsx) (xlsx)
- [04_완료금표제.xlsx](../data/batch_2/B_payroll/B2_B025_e56fa436/inputs/04_완료금표제.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B025_e56fa436/gold.json)

```json
{
  "balance_total": 91513,
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 2700000,
        "effective_payment_date": "2026-11-27",
        "employment_insurance": 25200,
        "fixed_allowance": 100000,
        "gross_pay": 3393063,
        "health_insurance": 100660,
        "holiday_pay": 0,
        "income_tax": 72250,
        "local_income_tax": 7220,
        "long_term_care": 13220,
        "meal_allowance": 200000,
        "national_pension": 133000,
        "net_pay": 3041513,
        "night_pay": 0,
        "non_taxable_pay": 200000,
        "ordinary_hourly_wage_floor": 14354,
        "ordinary_monthly_wage": 3000000,
        "overtime_pay": 43063,
        "paid_holiday_pay": 0,
        "pension_base_income": 2800000,
        "taxable_pay": 3193063,
        "total_deductions": 351550,
        "variable_allowance": 350000,
        "weekly_holiday_pay": 0
      },
      "employee_id": "WOOD-3",
      "payroll_id": "WOOD-NOV"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["WOOD-DONE", "WOOD-REG"], "cash_by_payroll": [{"paid": 2950000, "payroll_id": "WOOD-NOV"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": [], "payroll_derivations": [{"payroll_id": "WOOD-N... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B025_e56fa436/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B026_219aa61e (B_payroll, medium)

집필 제목: 80퍼센트 원천징수 선택 후 두 실행의 남은 지급액

업무 목적: 선택된 원천징수 비율이 전체 공제 및 남은 현금 지급을 바꾸는 관계를 확인한다.

가상교정실은 유효한80퍼센트 원천징수 선택을 제출했습니다. 공식 표 세액의 선택 적용과 지방세 및 확정 보험 공제를 계산하고 두 은행 실행과 대조하여 payroll_calculations와 balance_total을 작성해 주세요.

설계 의도: Batch1의 선택 세액 확인에서 한 걸음 더 나아가 실제 독립 실행 두 건과 차액을 대조한다. B024의 과세액 변경과 달리 과세 급여는 그대로이고 표 이후 선택 비율만 바뀐다.

집필 원고 ID: `B026`, 전체 문항 SHA-256: `219aa61eb3994a0e721b7b5fb38348a6e3e24a3f74c583fa15db2c05e926b9e2`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B026_219aa61e/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_001_050.json)

입력 파일:

- [01_선택적용.pdf](../data/batch_2/B_payroll/B2_B026_219aa61e/inputs/01_선택적용.pdf) (pdf)
- [02_신청과명세.hwpx](../data/batch_2/B_payroll/B2_B026_219aa61e/inputs/02_신청과명세.hwpx) (hwpx)
- [03_실행1.xlsx](../data/batch_2/B_payroll/B2_B026_219aa61e/inputs/03_실행1.xlsx) (xlsx)
- [04_실행2.xlsx](../data/batch_2/B_payroll/B2_B026_219aa61e/inputs/04_실행2.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B026_219aa61e/gold.json)

```json
{
  "balance_total": 229010,
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 3600000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 33300,
        "fixed_allowance": 100000,
        "gross_pay": 3900000,
        "health_insurance": 133010,
        "holiday_pay": 0,
        "income_tax": 101330,
        "local_income_tax": 10130,
        "long_term_care": 17470,
        "meal_allowance": 200000,
        "national_pension": 175750,
        "net_pay": 3429010,
        "night_pay": 0,
        "non_taxable_pay": 200000,
        "ordinary_hourly_wage_floor": 18660,
        "ordinary_monthly_wage": 3900000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 3700000,
        "taxable_pay": 3700000,
        "total_deductions": 470990,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "PROOF-7",
      "payroll_id": "PROOF-NOV"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["PROOF-A", "PROOF-B"], "cash_by_payroll": [{"paid": 3200000, "payroll_id": "PROOF-NOV"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": [], "payroll_derivations": [{"payroll_id": "PROOF-NO... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B026_219aa61e/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B035_7b986ab5 (B_payroll, medium)

집필 제목: 낮은 건강 통지의 하한과 요양 연결을 실제 송금에 반영

업무 목적: 건강보험 하한에서 요양 공제 및 실수령과 현금 잔액으로 이어지는 관계를 확인한다.

가상라벨실의 확정 건강보험 기준액은 낮지만 근로자 월 하한이 적용됩니다. 건강과 연동 요양 및 다른 공제를 적용하여 완전 월 명세를 계산하고 두 실제 송금과 비교하세요. payroll_calculations와 employee_settlements를 요청합니다.

설계 의도: B031의 건강 미부과0원과 달리 이 사례는 부과 대상의 낮은 통지로 건강 하한과0원이 아닌 요양이 남는다. 통지 금액을 현재 월급으로 대체하면 잔액이 바뀐다.

집필 원고 ID: `B035`, 전체 문항 SHA-256: `7b986ab578d7bc530dcdff2da245f5f209111ac4a37c71b1f372a53c9a05a6a3`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B035_7b986ab5/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_001_050.json)

입력 파일:

- [01_하한적용.pdf](../data/batch_2/B_payroll/B2_B035_7b986ab5/inputs/01_하한적용.pdf) (pdf)
- [02_확정부과.hwpx](../data/batch_2/B_payroll/B2_B035_7b986ab5/inputs/02_확정부과.hwpx) (hwpx)
- [03_월급실행.xlsx](../data/batch_2/B_payroll/B2_B035_7b986ab5/inputs/03_월급실행.xlsx) (xlsx)
- [04_잔여실행.xlsx](../data/batch_2/B_payroll/B2_B035_7b986ab5/inputs/04_잔여실행.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B035_7b986ab5/gold.json)

```json
{
  "employee_settlements": [
    {
      "balance": 158400,
      "effective_payment_date": "2026-11-27",
      "employee_id": "LABEL-6",
      "gross_pay": 2100000,
      "insurance_assessment_month": "2026-11",
      "net_pay": 1958400,
      "paid": 1800000,
      "payroll_id": "LABEL-NOV",
      "total_deductions": 141600
    }
  ],
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 1850000,
        "effective_payment_date": "2026-11-27",
        "employment_insurance": 17550,
        "fixed_allowance": 100000,
        "gross_pay": 2100000,
        "health_insurance": 10080,
        "holiday_pay": 0,
        "income_tax": 18210,
        "local_income_tax": 1820,
        "long_term_care": 1320,
        "meal_allowance": 150000,
        "national_pension": 92620,
        "net_pay": 1958400,
        "night_pay": 0,
        "non_taxable_pay": 150000,
        "ordinary_hourly_wage_floor": 10047,
        "ordinary_monthly_wage": 2100000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 1950000,
        "taxable_pay": 1950000,
        "total_deductions": 141600,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "LABEL-6",
      "payroll_id": "LABEL-NOV"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["LABEL-A", "LABEL-B"], "cash_by_payroll": [{"paid": 1800000, "payroll_id": "LABEL-NOV"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": [], "payroll_derivations": [{"payroll_id": "LABEL-NO... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B035_7b986ab5/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B050_9304f55f (B_payroll, hard)

집필 제목: 두 주휴일의 서로 다른 승인 단계와 당월 성과금 지급 종결

업무 목적: 휴일별 승인 단계와 당월 실적금을 구별하고 기관별 확정 공제를 적용해 월 은행 이체를 종결한다.

가상생활도구관 가상시후의11월은행이체를종결합니다. 첫일요일은최종휴게승인본을사용하고둘째일요일밤계획은미승인이므로제외합니다. 당월실적금은지급하되통상시급에넣지않습니다. holiday_pay, night_pay, ordinary_monthly_wage, gross_pay와net_pay를작성해유효소집및실적금과기관통지를연결해주세요.

설계 의도: 첫날은revision선택으로실제시간이달라지고둘째날은draft제외로야간판단이달라진다. 휴일별합산을한뒤실적금은지급합계에만더한다.

집필 원고 ID: `B050`, 전체 문항 SHA-256: `9304f55f020e7ac08bb1dd04774772a1b1b49e3e5e8ed19f191cfba0732c5702`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B050_9304f55f/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_001_050.json)

입력 파일:

- [01_월급.pdf](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/01_월급.pdf) (pdf)
- [02_실적금.pdf](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/02_실적금.pdf) (pdf)
- [03_첫날이전.xlsx](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/03_첫날이전.xlsx) (xlsx)
- [04_첫날최종.xlsx](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/04_첫날최종.xlsx) (xlsx)
- [05_둘째날낮.xlsx](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/05_둘째날낮.xlsx) (xlsx)
- [06_둘째날밤.xlsx](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/06_둘째날밤.xlsx) (xlsx)
- [07_휴일범위.hwpx](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/07_휴일범위.hwpx) (hwpx)
- [08_공단통지.pdf](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/08_공단통지.pdf) (pdf)
- [09_집행세무.hwpx](../data/batch_2/B_payroll/B2_B050_9304f55f/inputs/09_집행세무.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B050_9304f55f/gold.json)

```json
{
  "gross_pay": 5351579,
  "holiday_pay": 331579,
  "net_pay": 4604029,
  "night_pay": 0,
  "ordinary_monthly_wage": 4200000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [{"holiday_night_minutes": 0, "minutes": 480}, {"holiday_night_minutes": 0, "minutes": 180}], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 0, "payment_d... |
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 4200000, "ordinary_monthly_wage": 4200000} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 331579 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 200000 |
| B.GROSS | {"gross_pay": 5351579, "taxable_pay": 5151579} |
| B.PENSION | {"national_pension": 190000, "pension_base_income": 4000000} |
| B.HEALTH | 143800 |
| B.LONG_TERM_CARE | 18890 |
| B.EMPLOYMENT | 36000 |
| B.TAX_TABLE | 326240 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 326240 |
| B.LOCAL_TAX | 32620 |
| B.NET | 4604029 |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B050_9304f55f/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B052_4a4bfd4f (B_payroll, easy)

집필 제목: 동일한 통상임금의 식대 계약과 역할수당 계약 대조

업무 목적: 동일한 통상임금 및 현금 총액에서도 식대 비과세 때문에 다른 실수령을 구분한다.

가상기록대 두 직원은 기본급과 월 통상임금이 같습니다. 추가 현금의 명칭은 한쪽이 식대이고 다른 쪽이 역할수당입니다. 두 사람 모두 식사를 제공받지 않습니다. 각각의 과세 금액을 구분하고 동일 실행액과 비교한 payroll_calculations 및 employee_settlements를 작성하세요.

설계 의도: B051은 고정과 변동 구성 때문에 통상시급이 달라지는 비교다. 이 문제는 두 수당이 모두 통상임금에 들어가 시급은 같고 식대만 과세에서 빠지는 반대 불변량을 묻는다. 기존 단일 명세 식대 분류와 달리 동일 총액의 두 원장을 대조한다.

집필 원고 ID: `B052`, 전체 문항 SHA-256: `4a4bfd4f241b3d27010b0a4645b06ddc4cee4b6947a59f0c90f70e8a9f00d715`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B052_4a4bfd4f/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_정액.pdf](../data/batch_2/B_payroll/B2_B052_4a4bfd4f/inputs/01_정액.pdf) (pdf)
- [02_현금.hwpx](../data/batch_2/B_payroll/B2_B052_4a4bfd4f/inputs/02_현금.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B052_4a4bfd4f/gold.json)

```json
{
  "employee_settlements": [
    {
      "balance": 26320,
      "effective_payment_date": "2026-10-23",
      "employee_id": "DESK-A",
      "gross_pay": 3080000,
      "insurance_assessment_month": "2026-10",
      "net_pay": 2726320,
      "paid": 2700000,
      "payroll_id": "DESK-MEAL",
      "total_deductions": 353680
    },
    {
      "balance": 8910,
      "effective_payment_date": "2026-10-23",
      "employee_id": "DESK-B",
      "gross_pay": 3080000,
      "insurance_assessment_month": "2026-10",
      "net_pay": 2708910,
      "paid": 2700000,
      "payroll_id": "DESK-ROLE",
      "total_deductions": 371090
    }
  ],
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 2900000,
        "effective_payment_date": "2026-10-23",
        "employment_insurance": 26100,
        "fixed_allowance": 0,
        "gross_pay": 3080000,
        "health_insurance": 104250,
        "holiday_pay": 0,
        "income_tax": 65360,
        "local_income_tax": 6530,
        "long_term_care": 13690,
        "meal_allowance": 180000,
        "national_pension": 137750,
        "net_pay": 2726320,
        "night_pay": 0,
        "non_taxable_pay": 180000,
        "ordinary_hourly_wage_floor": 14736,
        "ordinary_monthly_wage": 3080000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 2900000,
        "taxable_pay": 2900000,
        "total_deductions": 353680,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "DESK-A",
      "payroll_id": "DESK-MEAL"
    },
    {
      "calculation": {
        "base_pay": 2900000,
        "effective_payment_date": "2026-10-23",
        "employment_insurance": 26100,
        "fixed_allowance": 180000,
        "gross_pay": 3080000,
        "health_insurance": 104250,
        "holiday_pay": 0,
        "income_tax": 81190,
        "local_income_tax": 8110,
        "long_term_care": 13690,
        "meal_allowance": 0,
        "national_pension": 137750,
        "net_pay": 2708910,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 14736,
        "ordinary_monthly_wage": 3080000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 2900000,
        "taxable_pay": 3080000,
        "total_deductions": 371090,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "DESK-B",
      "payroll_id": "DESK-ROLE"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["DESK-A-1", "DESK-B-1"], "cash_by_payroll": [{"paid": 2700000, "payroll_id": "DESK-MEAL"}, {"paid": 2700000, "payroll_id": "DESK-ROLE"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": [], ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B052_4a4bfd4f/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B056_ec262af0 (B_payroll, easy)

집필 제목: 같은 근로와 현재 임금에서 서로 다른 보험 통지의 현금 대조

업무 목적: 동일한 현재 임금에서도 서로 다른 과거 신고 기초가 개인별 실수령에 남는 것을 확인한다.

가상도장실 두 직원의 현재 임금과 근로 및 가족 조건은 같습니다. 기존 신고 이력이 달라 기관별 확정 기준액은 서로 다릅니다. 현재 임금을 공제 기초로 덮어쓰지 말고 기관 회신대로 각각 계산해 employee_settlements와 deductions_total을 제출하세요.

설계 의도: B008은 가족 열 차이, B034는 고령 고용 부과 차이다. 이 문제는 부과 여부와 세액 조건을 동일하게 고정하고 세 기관의 확정 보수 기초만 다른 비교를 요구한다.

집필 원고 ID: `B056`, 전체 문항 SHA-256: `ec262af04c886176bc5f1aabfb9ac17b3d8312f86762af25440a4b9996dc3dd3`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B056_ec262af0/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_동일급여.pdf](../data/batch_2/B_payroll/B2_B056_ec262af0/inputs/01_동일급여.pdf) (pdf)
- [02_동일이체.xlsx](../data/batch_2/B_payroll/B2_B056_ec262af0/inputs/02_동일이체.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B056_ec262af0/gold.json)

```json
{
  "deductions_total": 747090,
  "employee_settlements": [
    {
      "balance": 40580,
      "effective_payment_date": "2026-09-25",
      "employee_id": "SEAL-A",
      "gross_pay": 3100000,
      "insurance_assessment_month": "2026-09",
      "net_pay": 2740580,
      "paid": 2700000,
      "payroll_id": "SEAL-OLD",
      "total_deductions": 359420
    },
    {
      "balance": 12330,
      "effective_payment_date": "2026-09-25",
      "employee_id": "SEAL-B",
      "gross_pay": 3100000,
      "insurance_assessment_month": "2026-09",
      "net_pay": 2712330,
      "paid": 2700000,
      "payroll_id": "SEAL-NEW",
      "total_deductions": 387670
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["SEAL-A-X", "SEAL-B-X"], "cash_by_payroll": [{"paid": 2700000, "payroll_id": "SEAL-NEW"}, {"paid": 2700000, "payroll_id": "SEAL-OLD"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": [], "p... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B056_ec262af0/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B058_d53bd6f9 (B_payroll, easy)

집필 제목: 야간 가산만 있는 정규 계약과 낮 추가 계약의 같은 총지급액

업무 목적: 서로 다른 지급 항목이 같은 가산 합계를 만들더라도 기본 대가 포함 범위를 정확히 유지한다.

가상진열실에서 같은 기본 월급의 두 직원에게 서로 다른 작업을 배정했습니다. 한 직원은 소정 밤근로 세 시간이고 다른 직원은 낮 추가근로 한 시간입니다. 담당자 확정 분 집계와 월급 포함 범위로 각 항목을 계산하세요. 합계가 우연히 같아도 항목을 복사하지 말고 payroll_calculations를 제출하세요.

설계 의도: 같은 총액에서 구성을 바꾸는 B051은 통상임금 분자가 달라져 총 추가 대가도 달라진다. 여기서는 같은 시급의 정규 야간50퍼센트와 낮 추가150퍼센트가 총액에서만 상쇄되는 항목 대조다.

집필 원고 ID: `B058`, 전체 문항 SHA-256: `d53bd6f9ebe6905f9bc35721ed42cd06b7dec992ef2a1beb507f095a8dc53dc0`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B058_d53bd6f9/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_항목근거.pdf](../data/batch_2/B_payroll/B2_B058_d53bd6f9/inputs/01_항목근거.pdf) (pdf)
- [02_이체.xlsx](../data/batch_2/B_payroll/B2_B058_d53bd6f9/inputs/02_이체.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B058_d53bd6f9/gold.json)

```json
{
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 2508000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 22570,
        "fixed_allowance": 0,
        "gross_pay": 2526000,
        "health_insurance": 90160,
        "holiday_pay": 0,
        "income_tax": 36280,
        "local_income_tax": 3620,
        "long_term_care": 11840,
        "meal_allowance": 0,
        "national_pension": 119130,
        "net_pay": 2242400,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 12000,
        "ordinary_monthly_wage": 2508000,
        "overtime_pay": 18000,
        "paid_holiday_pay": 0,
        "pension_base_income": 2508000,
        "taxable_pay": 2526000,
        "total_deductions": 283600,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "SHOW-B",
      "payroll_id": "SHOW-DAY"
    },
    {
      "calculation": {
        "base_pay": 2508000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 22570,
        "fixed_allowance": 0,
        "gross_pay": 2526000,
        "health_insurance": 90160,
        "holiday_pay": 0,
        "income_tax": 36280,
        "local_income_tax": 3620,
        "long_term_care": 11840,
        "meal_allowance": 0,
        "national_pension": 119130,
        "net_pay": 2242400,
        "night_pay": 18000,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 12000,
        "ordinary_monthly_wage": 2508000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 2508000,
        "taxable_pay": 2526000,
        "total_deductions": 283600,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "SHOW-A",
      "payroll_id": "SHOW-NIGHT"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["SHOW-A-X", "SHOW-B-X"], "cash_by_payroll": [{"paid": 2200000, "payroll_id": "SHOW-DAY"}, {"paid": 2200000, "payroll_id": "SHOW-NIGHT"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": [], ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B058_d53bd6f9/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B060_6d28b821 (B_payroll, easy)

집필 제목: 유급 노동절 시간이 이미 집계된 직원과 별도 지급 직원 대조

업무 목적: 같은 법정 유급 기본 대가를 서로 다른 집계 방식에서 중복 없이 같은 총액으로 연결한다.

가상봉함실 두 시급제 직원의 노동절 기본 유급 대가를 마감합니다. 한쪽의 확정 정규 지급시간에는 유급 휴무 시간이 이미 들어가 있고 다른 쪽 집계에는 실제 근로만 들어 있습니다. 각각의 포함 사실을 확인하여 기본 유급을 한 번씩만 지급한 payroll_calculations를 제출하세요.

설계 의도: 기존 B040은 포함된 유급 한 명세와 실제 작업이다. 여기서는 실제 추가 작업이 없이 두 명세의 다른 집계 포함 위치만 대조해 base_pay와 paid_holiday_pay의 분해는 달라도 gross가 같아야 하는 관계를 요청한다.

집필 원고 ID: `B060`, 전체 문항 SHA-256: `6d28b8212f71f1e5cabfdcc7e5e56adc773faa57faa7cdec73636432d744ab18`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B060_6d28b821/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_유급집계.pdf](../data/batch_2/B_payroll/B2_B060_6d28b821/inputs/01_유급집계.pdf) (pdf)
- [02_현금.xlsx](../data/batch_2/B_payroll/B2_B060_6d28b821/inputs/02_현금.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B060_6d28b821/gold.json)

```json
{
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 240000,
        "effective_payment_date": "2026-05-29",
        "employment_insurance": 2590,
        "fixed_allowance": 0,
        "gross_pay": 288000,
        "health_insurance": 0,
        "holiday_pay": 0,
        "income_tax": 0,
        "local_income_tax": 0,
        "long_term_care": 0,
        "meal_allowance": 0,
        "national_pension": 0,
        "net_pay": 285410,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 12000,
        "ordinary_monthly_wage": 0,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 400000,
        "taxable_pay": 288000,
        "total_deductions": 2590,
        "variable_allowance": 0,
        "weekly_holiday_pay": 48000
      },
      "employee_id": "ENVELOPE-A",
      "payroll_id": "SEAL-INCLUDED"
    },
    {
      "calculation": {
        "base_pay": 192000,
        "effective_payment_date": "2026-05-29",
        "employment_insurance": 2590,
        "fixed_allowance": 0,
        "gross_pay": 288000,
        "health_insurance": 0,
        "holiday_pay": 0,
        "income_tax": 0,
        "local_income_tax": 0,
        "long_term_care": 0,
        "meal_allowance": 0,
        "national_pension": 0,
        "net_pay": 285410,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 12000,
        "ordinary_monthly_wage": 0,
        "overtime_pay": 0,
        "paid_holiday_pay": 48000,
        "pension_base_income": 400000,
        "taxable_pay": 288000,
        "total_deductions": 2590,
        "variable_allowance": 0,
        "weekly_holiday_pay": 48000
      },
      "employee_id": "ENVELOPE-B",
      "payroll_id": "SEAL-SEPARATE"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["ENV-A-X", "ENV-B-X"], "cash_by_payroll": [{"paid": 280000, "payroll_id": "SEAL-INCLUDED"}, {"paid": 280000, "payroll_id": "SEAL-SEPARATE"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B060_6d28b821/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B061_c44ffcee (B_payroll, easy)

집필 제목: 같은 복리 예산이 추가 대가와 과세액에 반대로 작용하는 급여

업무 목적: 동일한 약정 예산의 식대 및 성과 지급 성격이 추가대가와 원천세 입력을 서로 반대 방향으로 바꾸는 실제 명세를 비교한다.

가상사진분류실 두 계약의 기본급과 월 추가근로는 같습니다. 한 계약의18만원은 매달 동일하게 지급하는 소정근로 대가인 현금 식대이고 다른 계약의18만원은 해당 월 검수 성과 달성에 따른 변동 완료금입니다. 양쪽 총약정 예산이 같다는 이유로 같은 추가수당과 과세액을 복사하지 마세요. 완전 월 명세의 payroll_calculations와 employee_settlements를 제출하세요.

설계 의도: 기존 B051은 고정 및 변동 수당에서 추가대가만 갈라지고 B052는 식대 및 역할수당에서 과세만 갈라진다. 여기서는 한18만원 항목의 성격이 통상분자와 비과세를 동시에 바꾼다. 식대 계약은 실제 추가대가가 더 크지만 과세급여는 더 작아서 하나의 지급 기준을 두 단계에 복사할 수 없다.

집필 원고 ID: `B061`, 전체 문항 SHA-256: `c44ffceed063a43a1e24c0e1147b559648525971e6203a9cb8dbb16e0c647c5f`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B061_c44ffcee/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_지급성격.pdf](../data/batch_2/B_payroll/B2_B061_c44ffcee/inputs/01_지급성격.pdf) (pdf)
- [02_정상현금.xlsx](../data/batch_2/B_payroll/B2_B061_c44ffcee/inputs/02_정상현금.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B061_c44ffcee/gold.json)

```json
{
  "employee_settlements": [
    {
      "balance": 108240,
      "effective_payment_date": "2026-11-25",
      "employee_id": "PHOTO-31",
      "gross_pay": 3158800,
      "insurance_assessment_month": "2026-11",
      "net_pay": 2808240,
      "paid": 2700000,
      "payroll_id": "PHOTO-MEAL",
      "total_deductions": 350560
    },
    {
      "balance": 80960,
      "effective_payment_date": "2026-11-25",
      "employee_id": "PHOTO-32",
      "gross_pay": 3148000,
      "insurance_assessment_month": "2026-11",
      "net_pay": 2780960,
      "paid": 2700000,
      "payroll_id": "PHOTO-RESULT",
      "total_deductions": 367040
    }
  ],
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 2800000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 25200,
        "fixed_allowance": 0,
        "gross_pay": 3158800,
        "health_insurance": 100660,
        "holiday_pay": 0,
        "income_tax": 71350,
        "local_income_tax": 7130,
        "long_term_care": 13220,
        "meal_allowance": 180000,
        "national_pension": 133000,
        "net_pay": 2808240,
        "night_pay": 0,
        "non_taxable_pay": 180000,
        "ordinary_hourly_wage_floor": 14900,
        "ordinary_monthly_wage": 2980000,
        "overtime_pay": 178800,
        "paid_holiday_pay": 0,
        "pension_base_income": 2800000,
        "taxable_pay": 2978800,
        "total_deductions": 350560,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "PHOTO-31",
      "payroll_id": "PHOTO-MEAL"
    },
    {
      "calculation": {
        "base_pay": 2800000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 25200,
        "fixed_allowance": 0,
        "gross_pay": 3148000,
        "health_insurance": 100660,
        "holiday_pay": 0,
        "income_tax": 86330,
        "local_income_tax": 8630,
        "long_term_care": 13220,
        "meal_allowance": 0,
        "national_pension": 133000,
        "net_pay": 2780960,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 14000,
        "ordinary_monthly_wage": 2800000,
        "overtime_pay": 168000,
        "paid_holiday_pay": 0,
        "pension_base_income": 2800000,
        "taxable_pay": 3148000,
        "total_deductions": 367040,
        "variable_allowance": 180000,
        "weekly_holiday_pay": 0
      },
      "employee_id": "PHOTO-32",
      "payroll_id": "PHOTO-RESULT"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["PHOTO-X31", "PHOTO-X32"], "cash_by_payroll": [{"paid": 2700000, "payroll_id": "PHOTO-MEAL"}, {"paid": 2700000, "payroll_id": "PHOTO-RESULT"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids"... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B061_c44ffcee/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B068_96e0a4e1 (B_payroll, medium)

집필 제목: 같은 직원의 새 월에 초기화한 근태 수정번호를 별도로 마감

업무 목적: 같은 직원의 월별 근태번호 및 수정번호 재시작을 명세 범위 안에서 선택하여 새 월 실제작업을 보존한다.

가상삽지실 같은 직원의11월 및12월 근태 장부는 매월 카드01과 수정번호1부터 다시 시작합니다.11월 카드의최고 승인3번이12월의 새 승인1번보다 높다는 이유로12월 실제작업을 지우면 안 됩니다. 각 완전 월 명세 안에서 수정본을 선택한 payroll_calculations, employee_settlements 및 gross_total을 제출하세요.

설계 의도: B071은 서로 다른 직원의 동일 카드번호로 직원번호가 범위를 구분한다. 이 문제는 직원번호도 같고11월 승인revision3와12월 새 승인revision1이 공존한다. 직원과 카드번호까지 붙인 전역 최고revision 선택도12월을 없애므로 독립 완전 월 명세의 범위를 유지해야 한다. B003의 단순 두 월 현금과 달리 원천 승인 선택에도 월 범위가 필요하다.

집필 원고 ID: `B068`, 전체 문항 SHA-256: `96e0a4e1a2e8cbf1c60ea60b85f44e0f69649d8ca4106dc9670ce206181ceb41`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B068_96e0a4e1/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_11월장부.pdf](../data/batch_2/B_payroll/B2_B068_96e0a4e1/inputs/01_11월장부.pdf) (pdf)
- [02_12월장부.hwpx](../data/batch_2/B_payroll/B2_B068_96e0a4e1/inputs/02_12월장부.hwpx) (hwpx)
- [03_월별키.pdf](../data/batch_2/B_payroll/B2_B068_96e0a4e1/inputs/03_월별키.pdf) (pdf)
- [04_월별집행.xlsx](../data/batch_2/B_payroll/B2_B068_96e0a4e1/inputs/04_월별집행.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B068_96e0a4e1/gold.json)

```json
{
  "employee_settlements": [
    {
      "balance": 94130,
      "effective_payment_date": "2026-12-25",
      "employee_id": "INSERT-41",
      "gross_pay": 2580000,
      "insurance_assessment_month": "2026-12",
      "net_pay": 2294130,
      "paid": 2200000,
      "payroll_id": "INSERT-DEC",
      "total_deductions": 285870
    },
    {
      "balance": 76890,
      "effective_payment_date": "2026-11-25",
      "employee_id": "INSERT-41",
      "gross_pay": 2562000,
      "insurance_assessment_month": "2026-11",
      "net_pay": 2276890,
      "paid": 2200000,
      "payroll_id": "INSERT-NOV",
      "total_deductions": 285110
    }
  ],
  "gross_total": 5142000,
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 2508000,
        "effective_payment_date": "2026-12-25",
        "employment_insurance": 22570,
        "fixed_allowance": 0,
        "gross_pay": 2580000,
        "health_insurance": 90160,
        "holiday_pay": 0,
        "income_tax": 38340,
        "local_income_tax": 3830,
        "long_term_care": 11840,
        "meal_allowance": 0,
        "national_pension": 119130,
        "net_pay": 2294130,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 12000,
        "ordinary_monthly_wage": 2508000,
        "overtime_pay": 72000,
        "paid_holiday_pay": 0,
        "pension_base_income": 2508000,
        "taxable_pay": 2580000,
        "total_deductions": 285870,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "INSERT-41",
      "payroll_id": "INSERT-DEC"
    },
    {
      "calculation": {
        "base_pay": 2508000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 22570,
        "fixed_allowance": 0,
        "gross_pay": 2562000,
        "health_insurance": 90160,
        "holiday_pay": 0,
        "income_tax": 37650,
        "local_income_tax": 3760,
        "long_term_care": 11840,
        "meal_allowance": 0,
        "national_pension": 119130,
        "net_pay": 2276890,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 12000,
        "ordinary_monthly_wage": 2508000,
        "overtime_pay": 54000,
        "paid_holiday_pay": 0,
        "pension_base_income": 2508000,
        "taxable_pay": 2562000,
        "total_deductions": 285110,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "INSERT-41",
      "payroll_id": "INSERT-NOV"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["INSERT-X11", "INSERT-X12"], "cash_by_payroll": [{"paid": 2200000, "payroll_id": "INSERT-DEC"}, {"paid": 2200000, "payroll_id": "INSERT-NOV"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids"... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B068_96e0a4e1/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B069_a88f7a8e (B_payroll, medium)

집필 제목: 같은 고액 과세급여와 다른 통상임금을 가진 완료금 및 재계약 명세

업무 목적: 같은 고액 과세 합계와 공제기초에서 다른 임금성격 때문에 통상임금만 갈라지는 두 명세를 비교한다.

가상가등록실 두 직원의 이번 과세급여는 같습니다. 첫 직원은 당월 완료금이 합쳐진 것이고 두 번째 직원은 고정 기본급 재계약으로 같은 금액이 됐습니다. 기관별 확정 공제기초도 같지만 통상임금은 다릅니다. 각각의 원천세와 표시 시급을 계산한 payroll_calculations를 제출하세요. 같은 현재 과세액을 공통 통상임금으로 복사하지 마세요.

설계 의도: B051은 고정수당 대 완료금 차이가 실제 추가작업을 통해 지급총액도 바꾸는 비교다. 여기서는 추가작업이 없어서 현재 과세와 원천세는 같아야 하고 통상임금만 달라지는 반대 불변량을 확인한다. 기존 B276은 한명의 고액 완료금 산식으로 대조명세가 없다.

집필 원고 ID: `B069`, 전체 문항 SHA-256: `a88f7a8ea80580e6a508eecca590f68baa74d2c9a58841bfabdffe3dda0bbf95`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B069_a88f7a8e/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_완료금.pdf](../data/batch_2/B_payroll/B2_B069_a88f7a8e/inputs/01_완료금.pdf) (pdf)
- [02_고정인상.hwpx](../data/batch_2/B_payroll/B2_B069_a88f7a8e/inputs/02_고정인상.hwpx) (hwpx)
- [03_대조.pdf](../data/batch_2/B_payroll/B2_B069_a88f7a8e/inputs/03_대조.pdf) (pdf)
- [04_실행.xlsx](../data/batch_2/B_payroll/B2_B069_a88f7a8e/inputs/04_실행.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B069_a88f7a8e/gold.json)

```json
{
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 10500000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 31500,
        "fixed_allowance": 0,
        "gross_pay": 10500000,
        "health_insurance": 125820,
        "holiday_pay": 0,
        "income_tax": 1703900,
        "local_income_tax": 170390,
        "long_term_care": 16530,
        "meal_allowance": 0,
        "national_pension": 166250,
        "net_pay": 8285610,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 50239,
        "ordinary_monthly_wage": 10500000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 3500000,
        "taxable_pay": 10500000,
        "total_deductions": 2214390,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "REG-B",
      "payroll_id": "REGISTER-FIX"
    },
    {
      "calculation": {
        "base_pay": 3500000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 31500,
        "fixed_allowance": 0,
        "gross_pay": 10500000,
        "health_insurance": 125820,
        "holiday_pay": 0,
        "income_tax": 1703900,
        "local_income_tax": 170390,
        "long_term_care": 16530,
        "meal_allowance": 0,
        "national_pension": 166250,
        "net_pay": 8285610,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 16746,
        "ordinary_monthly_wage": 3500000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 3500000,
        "taxable_pay": 10500000,
        "total_deductions": 2214390,
        "variable_allowance": 7000000,
        "weekly_holiday_pay": 0
      },
      "employee_id": "REG-A",
      "payroll_id": "REGISTER-VAR"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["REG-A-X", "REG-B-X"], "cash_by_payroll": [{"paid": 9000000, "payroll_id": "REGISTER-FIX"}, {"paid": 9000000, "payroll_id": "REGISTER-VAR"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B069_a88f7a8e/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B074_80cdb5fe (B_payroll, medium)

집필 제목: 휴일 총량은 같아도 승인 날짜 분산으로 줄어든 초과 가산

업무 목적: 같은 휴일근로 총량과 범주를 보존하는 승인 날짜 정정이 날짜별8시간 분할에만 작용하도록 마감한다.

가상사진제본실 두 소집의 실제 시간과 근로 범주는 그대로이며 두번째 소집의 날짜만 다른 주휴일로 정정됐습니다. 현재 승인본을 고르면 월 휴일근로 총11시간은 같지만 한 날짜의8시간 초과는 없어집니다. 월 전체 시간에 일괄 초과가산을 적용하지 말고 holiday_pay, night_pay 및 net_pay를 제출하세요.

설계 의도: B070은 평일에서 휴일로 날짜가 옮겨 추가 범주와 같은 날 합산이 함께 바뀐다. 이 문제의 정정 전후는 모두 주휴일이고 월 휴일시간 및 야간은 고정이다. 최신 날짜를 다른 휴일에 귀속시킨 뒤 날짜별 초과구간만 제거되므로 휴일 총량만으로 계산하거나 범주만 정정해도 오답이다.

집필 원고 ID: `B074`, 전체 문항 SHA-256: `80cdb5fe9fa314553ec691397e8189eb6f8960feb1d89e773e6e6acd8e7c0080`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B074_80cdb5fe/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_월임금.pdf](../data/batch_2/B_payroll/B2_B074_80cdb5fe/inputs/01_월임금.pdf) (pdf)
- [02_소집날짜.xlsx](../data/batch_2/B_payroll/B2_B074_80cdb5fe/inputs/02_소집날짜.xlsx) (xlsx)
- [03_기관.hwpx](../data/batch_2/B_payroll/B2_B074_80cdb5fe/inputs/03_기관.hwpx) (hwpx)
- [04_휴일지급.pdf](../data/batch_2/B_payroll/B2_B074_80cdb5fe/inputs/04_휴일지급.pdf) (pdf)

정답: [gold.json](../data/batch_2/B_payroll/B2_B074_80cdb5fe/gold.json)

```json
{
  "holiday_pay": 198000,
  "net_pay": 2409230,
  "night_pay": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [{"holiday_night_minutes": 0, "minutes": 360}, {"holiday_night_minutes": 0, "minutes": 300}], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 0, "payment_d... |
| B.ORDINARY | {"hourly_exact_denominator": 1, "hourly_exact_numerator": 12000, "ordinary_monthly_wage": 2508000} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 198000 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 0 |
| B.GROSS | {"gross_pay": 2706000, "taxable_pay": 2706000} |
| B.PENSION | {"national_pension": 119130, "pension_base_income": 2508000} |
| B.HEALTH | 90160 |
| B.LONG_TERM_CARE | 11840 |
| B.EMPLOYMENT | 22570 |
| B.TAX_TABLE | 48250 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 48250 |
| B.LOCAL_TAX | 4820 |
| B.NET | 2409230 |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B074_80cdb5fe/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B083_00211542 (B_payroll, medium)

집필 제목: 부양 가족 수는 같고 자녀 공제 연령 확인만 다른 두 명세

업무 목적: 기본 공제 가족 등록과 별도 자녀 공제 연령 요건을 서로 다른 입력으로 유지하여 개인별 세액을 비교한다.

가상목록교환실 두 직원의 임금과 공제 가족수는 같습니다. 가족 중 자녀의 공제 연령 확인 결과가 달라 한 명세만 자녀 세액 공제가 있습니다. 가족수 자체를 줄이지 말고 payroll_calculations 및 employee_settlements를 제출하세요.

설계 의도: B008은 공제 가족수 차이로 표 열이 달라진다. 여기서는 같은 표 열을 고정한 두 개인의 별도 자녀 연령 공제만 달라져 원천세가 갈라진다. 가족수 및 자녀수를 같은 입력으로 합치면 두 단계 모두 잘못된다.

집필 원고 ID: `B083`, 전체 문항 SHA-256: `00211542cba59e34e90d8b453bace222511bb34079d2e47c60fa851df581a1fc`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B083_00211542/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_요건0.pdf](../data/batch_2/B_payroll/B2_B083_00211542/inputs/01_요건0.pdf) (pdf)
- [02_요건1.hwpx](../data/batch_2/B_payroll/B2_B083_00211542/inputs/02_요건1.hwpx) (hwpx)
- [03_구분.pdf](../data/batch_2/B_payroll/B2_B083_00211542/inputs/03_구분.pdf) (pdf)
- [04_현금.xlsx](../data/batch_2/B_payroll/B2_B083_00211542/inputs/04_현금.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/B_payroll/B2_B083_00211542/gold.json)

```json
{
  "employee_settlements": [
    {
      "balance": 34300,
      "effective_payment_date": "2026-11-25",
      "employee_id": "EXCHANGE-A",
      "gross_pay": 3800000,
      "insurance_assessment_month": "2026-11",
      "net_pay": 3334300,
      "paid": 3300000,
      "payroll_id": "EXCHANGE-OLD",
      "total_deductions": 465700
    },
    {
      "balance": 57210,
      "effective_payment_date": "2026-11-25",
      "employee_id": "EXCHANGE-B",
      "gross_pay": 3800000,
      "insurance_assessment_month": "2026-11",
      "net_pay": 3357210,
      "paid": 3300000,
      "payroll_id": "EXCHANGE-YOUNG",
      "total_deductions": 442790
    }
  ],
  "payroll_calculations": [
    {
      "calculation": {
        "base_pay": 3800000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 34200,
        "fixed_allowance": 0,
        "gross_pay": 3800000,
        "health_insurance": 136610,
        "holiday_pay": 0,
        "income_tax": 87680,
        "local_income_tax": 8760,
        "long_term_care": 17950,
        "meal_allowance": 0,
        "national_pension": 180500,
        "net_pay": 3334300,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 18181,
        "ordinary_monthly_wage": 3800000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 3800000,
        "taxable_pay": 3800000,
        "total_deductions": 465700,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "EXCHANGE-A",
      "payroll_id": "EXCHANGE-OLD"
    },
    {
      "calculation": {
        "base_pay": 3800000,
        "effective_payment_date": "2026-11-25",
        "employment_insurance": 34200,
        "fixed_allowance": 0,
        "gross_pay": 3800000,
        "health_insurance": 136610,
        "holiday_pay": 0,
        "income_tax": 66850,
        "local_income_tax": 6680,
        "long_term_care": 17950,
        "meal_allowance": 0,
        "national_pension": 180500,
        "net_pay": 3357210,
        "night_pay": 0,
        "non_taxable_pay": 0,
        "ordinary_hourly_wage_floor": 18181,
        "ordinary_monthly_wage": 3800000,
        "overtime_pay": 0,
        "paid_holiday_pay": 0,
        "pension_base_income": 3800000,
        "taxable_pay": 3800000,
        "total_deductions": 442790,
        "variable_allowance": 0,
        "weekly_holiday_pay": 0
      },
      "employee_id": "EXCHANGE-B",
      "payroll_id": "EXCHANGE-YOUNG"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B_PAYROLL_BANK_RECONCILIATION | {"accepted_transfer_ids": ["EX-A-X", "EX-B-X"], "cash_by_payroll": [{"paid": 3300000, "payroll_id": "EXCHANGE-OLD"}, {"paid": 3300000, "payroll_id": "EXCHANGE-YOUNG"}], "deduplicated_transfer_ids": [], "excluded_transfer_ids": ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B083_00211542/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_B084_d3d784ab (B_payroll, medium)

집필 제목: 당월 감액 면제 정액 약정의 양의 부재 기록 대조

업무 목적: 확정 정액 전액 지급 약정에서 근태 통계가 기본급 일할 감액이나 별도 주휴 재지급으로 이어지지 않는 것을 확인한다.

가상미색실은 월급을 일할 감액하지 않는 확정 정액 계약이고 무급 결근 기록은 근무 통계에만 남습니다. 월급 전액 지급 약정과 결근 주의 출근 기록을 확인해 base_pay, weekly_holiday_pay와 gross_pay를 제출하세요. 시간급 공식을 정액 월급에 적용하지 마세요.

설계 의도: 기존 B037/B026은 시급 무급 결근이 기본대가와 주휴를 줄인다. 이 문항은 노사 확정 정액 전액지급 약정이라 동일 근태 결손이 현재 기본급을 줄이지 않으며 월급 포함 주휴도 별도 지급하지 않는 반대 지급기준 관계다.

집필 원고 ID: `B084`, 전체 문항 SHA-256: `d3d784abd1e02fcb6d8e49810f1d324716932d098e07cdafcbfa356fcf39f9f0`

[문항 메타데이터](../data/batch_2/B_payroll/B2_B084_d3d784ab/task.yaml)와 [집필 원고](../authored/batch_2/B_payroll/cases_051_100.json)

입력 파일:

- [01_전액약정.pdf](../data/batch_2/B_payroll/B2_B084_d3d784ab/inputs/01_전액약정.pdf) (pdf)
- [02_통계.xlsx](../data/batch_2/B_payroll/B2_B084_d3d784ab/inputs/02_통계.xlsx) (xlsx)
- [03_기관.hwpx](../data/batch_2/B_payroll/B2_B084_d3d784ab/inputs/03_기관.hwpx) (hwpx)
- [04_지급.pdf](../data/batch_2/B_payroll/B2_B084_d3d784ab/inputs/04_지급.pdf) (pdf)

정답: [gold.json](../data/batch_2/B_payroll/B2_B084_d3d784ab/gold.json)

```json
{
  "base_pay": 2400000,
  "gross_pay": 2400000,
  "weekly_holiday_pay": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| B.EVIDENCE_RECONCILIATION | {"employer_provides_meals": false, "holiday_shifts": [], "night_minutes": 0, "overtime_minutes": 0, "paid_holiday_minutes": 0, "payment_date": "2026-11-25", "qualifying_weeks": 0, "regular_minutes": 9600} |
| B.ORDINARY | {"hourly_exact_denominator": 209, "hourly_exact_numerator": 2400000, "ordinary_monthly_wage": 2400000} |
| B.PAID_HOLIDAY | 0 |
| B.OVERTIME | 0 |
| B.NIGHT | 0 |
| B.HOLIDAY | 0 |
| B.WEEKLY | {"weekly_holiday_entitlement": 0, "weekly_holiday_pay": 0} |
| B.MEAL_EXEMPT | 0 |
| B.GROSS | {"gross_pay": 2400000, "taxable_pay": 2400000} |
| B.PENSION | {"national_pension": 114000, "pension_base_income": 2400000} |
| B.HEALTH | 86280 |
| B.LONG_TERM_CARE | 11330 |
| B.EMPLOYMENT | 21600 |
| B.TAX_TABLE | 32380 |
| B.CHILD_CREDIT | 0 |
| B.WITHHOLDING | 32380 |
| B.LOCAL_TAX | 3230 |
| B.NET | 2131180 |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/B_payroll/B2_B084_d3d784ab/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C012_bd4210f2 (C_vat, easy)

집필 제목: 정정된 부분 발급을 합산한 뒤 원 미만을 버리는 주문

업무 목적: 하나의 완료 공급에서 선택한 두 부분 발급을 합산한 뒤 공제 원 미만을 버린다.

가상소형나사점은 한 주문의 현금 부분 발급을 정정했고 별도 카드 부분 발급과 미발급 은행 수금을 함께 보냈습니다. 실제 지급 참조와 유효 발급 범위를 복원한 다음 합산하여 매출세액(output_vat) 및 발급 공제(receipt_credit)를 answer.json에 써 주세요.

설계 의도: 현금 오기2200원을 실제 부분 지급1100원의 확정 원본으로 대체하고 카드1210원을 함께 합산한다. 미발급 이체3190원은 전체 공급에 남지만 발급 모수에서 제외한다. 선택 모수2310원의 공제30원은 개별 전표 공제14원과15원을 더한29원과 다르고 전체 공급5500원을 쓰는71원과도 다르다. 정정 선택과 부분 범위 및 합산 절사가 실제 답에서 모두 작동한다.

집필 원고 ID: `C012`, 전체 문항 SHA-256: `bd4210f2a0dd2f0fafa00c939397525cb5d0293867e5e9c876a71a7dec645c6a`

[문항 메타데이터](../data/batch_2/C_vat/B2_C012_bd4210f2/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_001_050.json)

입력 파일:

- [01_나사인도.pdf](../data/batch_2/C_vat/B2_C012_bd4210f2/inputs/01_나사인도.pdf) (pdf)
- [02_실행발급.xlsx](../data/batch_2/C_vat/B2_C012_bd4210f2/inputs/02_실행발급.xlsx) (xlsx)
- [03_부분정정.hwpx](../data/batch_2/C_vat/B2_C012_bd4210f2/inputs/03_부분정정.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/C_vat/B2_C012_bd4210f2/gold.json)

```json
{
  "output_vat": 500,
  "receipt_credit": 30
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["현금오기"], "replacement_relations": [{"revoked_document_id": "현금오기", "valid_document_id": "현금확정"}], "selected_document_ids": ["카드발급", "현금확정"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["카드발급", "현금확정"], "documented_input_vat": 0, "eligible_input_document_ids": [], "gross": 5500, "invoice_issued": false, "issued_receipt_gross": 2310, "paid_gross": 5500, "supply_base": 5000, "transaction_id": ... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 2} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 5500, "supply_base": 5000, "vat": 500} |
| VAT_OUTPUT_10 | 500 |
| VAT_RECEIPT_BASE | {"eligible_gross": 2310} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 30 |
| VAT_CREDIT_ANNUAL_LIMIT | 30 |
| VAT_CREDIT_PAYABLE_LIMIT | 30 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 470 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 470, "noncreditable_vat": 0, "output_vat": 500, "payable_vat": 470, "prepaid_vat": 0, "receipt_credit": 30, "refund_vat": 0, "tax_base": 5000, "unique_transaction_count": 1} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C012_bd4210f2/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C025_26be26db (C_vat, medium)

집필 제목: 같은 미표시 전표 두 구매 중 하나만 전자 보완

업무 목적: 한 공급의 증빙 보완을 다른 독립 구매로 확장하지 않는다.

가상포일가공의 독립 자재 두 구매는 모두 전체 카드 전표의 세액 표시가 없으며 한 구매만 전체 적격 전자가 있습니다. 각 공급 참조를 연결하여 공제가능 매입세액(deductible_input_vat)과 불공제 매입세액(noncreditable_vat) 및 매입세액(input_vat)을 answer.json에 적어 주세요.

설계 의도: 금액과 카드 표시 부족은 같아도 전자의 거래 참조는 첫 구매 하나다. 증빙 보완의 공급 범위를 교차 구매까지 확대하는 오류를 검증한다.

집필 원고 ID: `C025`, 전체 문항 SHA-256: `26be26dbe25c974d827cf6d741e308c6df49b95a5a655da008669728fb423935`

[문항 메타데이터](../data/batch_2/C_vat/B2_C025_26be26db/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_001_050.json)

입력 파일:

- [01_반입.hwpx](../data/batch_2/C_vat/B2_C025_26be26db/inputs/01_반입.hwpx) (hwpx)
- [02_실행.xlsx](../data/batch_2/C_vat/B2_C025_26be26db/inputs/02_실행.xlsx) (xlsx)
- [03_미표시전표.pdf](../data/batch_2/C_vat/B2_C025_26be26db/inputs/03_미표시전표.pdf) (pdf)
- [04_은박전자.pdf](../data/batch_2/C_vat/B2_C025_26be26db/inputs/04_은박전자.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C025_26be26db/gold.json)

```json
{
  "deductible_input_vat": 40000,
  "input_vat": 80000,
  "noncreditable_vat": 40000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["동박카드"], "documented_input_vat": 0, "eligible_input_document_ids": [], "gross": 440000, "invoice_issued": false, "issued_receipt_gross": 440000, "paid_gross": 440000, "purchase_activity_facts": {"business_rel... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 2} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 440000, "supply_base": 400000, "vat": 40000} |
| VAT_INPUT_EVIDENCE | {"deductible": 0, "noncreditable": 40000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 440000, "supply_base": 400000, "vat": 40000} |
| VAT_INPUT_EVIDENCE | {"deductible": 40000, "noncreditable": 0} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -40000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 40000, "input_vat": 80000, "net_vat": -40000, "noncreditable_vat": 40000, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 40000, "tax_base": 0, "unique_transactio... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C025_26be26db/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C028_49959a5a (C_vat, medium)

집필 제목: 가족 사적 설치의 전체 전자와 부분 현금영수증

업무 목적: 증빙을 완성한 사적 구매의 업무 귀속을 확인한다.

가상무늬공방의 대표 가족 집에 설치한 가구는 일부 현금영수증과 전체 전자가 있습니다. 원본들의 실제 공급 범위와 설치 수령자를 대조하여 불공제 매입세액(noncreditable_vat)과 공제가능 매입세액(deductible_input_vat) 및 신고 거래 수(unique_transaction_count)를 answer.json에 적어 주세요.

설계 의도: 전체 적격 전자가 부분 지급 증빙을 보완하지만 실제 수령은 가족 집이다. 부분 지급 범위가 아닌 전체 구매의 사적 사용을 요청 불공제액에 반영한다.

집필 원고 ID: `C028`, 전체 문항 SHA-256: `49959a5aca218b685f9705c0c9625abc5cd7fe59dee210f0b1ebc1baf93b398e`

[문항 메타데이터](../data/batch_2/C_vat/B2_C028_49959a5a/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_001_050.json)

입력 파일:

- [01_신고범위.hwpx](../data/batch_2/C_vat/B2_C028_49959a5a/inputs/01_신고범위.hwpx) (hwpx)
- [02_설치수령.pdf](../data/batch_2/C_vat/B2_C028_49959a5a/inputs/02_설치수령.pdf) (pdf)
- [03_현금실행.xlsx](../data/batch_2/C_vat/B2_C028_49959a5a/inputs/03_현금실행.xlsx) (xlsx)
- [04_전체전자.pdf](../data/batch_2/C_vat/B2_C028_49959a5a/inputs/04_전체전자.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C028_49959a5a/gold.json)

```json
{
  "deductible_input_vat": 0,
  "noncreditable_vat": 150000,
  "unique_transaction_count": 1
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["가족전자", "가족현영"], "documented_input_vat": 150000, "eligible_input_document_ids": ["가족전자"], "gross": 1650000, "invoice_issued": true, "issued_receipt_gross": 550000, "paid_gross": 550000, "purchase_activity_fac... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 2} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1650000, "supply_base": 1500000, "vat": 150000} |
| VAT_NONBUSINESS | {"deductible": 0, "noncreditable": 150000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 0 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 150000, "net_vat": 0, "noncreditable_vat": 150000, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 0, "unique_transaction_count": 1} |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C028_49959a5a/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C044_270a5c7f (C_vat, hard)

집필 제목: 법인 매장의 전년 회수와 올해 세 발급 공급

업무 목적: 수금 시점과 현재 법인의 세액 공제 자격을 구분한다.

가상소형꽂이 법인의 수금 및 발급 자료를 확인해 주세요. 실제 공급일이 전년인 회수 주문을 분리하고 현재 신고 주체를 적용해 매출세액(output_vat), 영수증 발행세액공제(receipt_credit), 납부세액(payable_vat), 고유 거래 수(unique_transaction_count)를 answer.json에 써 주세요.

설계 의도: 전년 회수 주문을 빼는 기간 판단은 현재 세 발급 공급 전체를 남긴다. 소비자 소매라는 사업 사실과 법인 주체를 따로 확인하여 발행 공제를 개인 자격으로 계산하지 않는다.

집필 원고 ID: `C044`, 전체 문항 SHA-256: `270a5c7f913fcbdab98a1e398d90eb00557c79532d24b8b68a07d611d8d7724d`

[문항 메타데이터](../data/batch_2/C_vat/B2_C044_270a5c7f/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_001_050.json)

입력 파일:

- [01_수금.hwpx](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/01_수금.hwpx) (hwpx)
- [02_법인주체.pdf](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/02_법인주체.pdf) (pdf)
- [03_전년규모.xlsx](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/03_전년규모.xlsx) (xlsx)
- [04_공제이력.pdf](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/04_공제이력.pdf) (pdf)
- [05_전년원본.pdf](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/05_전년원본.pdf) (pdf)
- [06_카드현재.pdf](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/06_카드현재.pdf) (pdf)
- [07_현금현재.xlsx](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/07_현금현재.xlsx) (xlsx)
- [08_기관현재.pdf](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/08_기관현재.pdf) (pdf)
- [09_전년사진.png](../data/batch_2/C_vat/B2_C044_270a5c7f/inputs/09_전년사진.png) (png)

정답: [gold.json](../data/batch_2/C_vat/B2_C044_270a5c7f/gold.json)

```json
{
  "output_vat": 460000,
  "payable_vat": 460000,
  "receipt_credit": 0,
  "unique_transaction_count": 3
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1980000, "supply_base": 1800000, "vat": 180000} |
| VAT_OUTPUT_10 | 180000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 0} |
| VAT_PERIOD | false |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1650000, "supply_base": 1500000, "vat": 150000} |
| VAT_OUTPUT_10 | 150000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 1650000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1430000, "supply_base": 1300000, "vat": 130000} |
| VAT_OUTPUT_10 | 130000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 1430000} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 460000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 460000, "noncreditable_vat": 0, "output_vat": 460000, "payable_vat": 460000, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 4600000, "unique_transactio... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C044_270a5c7f/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C046_47b32f4c (C_vat, hard)

집필 제목: 대여 허가 말소와 전체 증빙 보완의 다른 효과

업무 목적: 허가 시점의 사용 요건과 증빙 보완 범위를 서로 구별한다.

가상남빛대여의 같은 차량은 허가 유효 중 일부 카드 정비를 받았고 말소 뒤에는 세액 미표시 전액 카드 정비를 받았습니다. 두 전체 전자와 허가 효력 및 실제 작업을 연결하여 공제가능 매입세액(deductible_input_vat)과 불공제 매입세액(noncreditable_vat) 및 거래 수(unique_transaction_count)를 answer.json에 적어 주세요.

설계 의도: 첫 부분 카드는 전체 전자로 정비 전량을 보완하고 둘째 미표시 카드도 전체 전자가 있지만 말소 이후 일반 사무 사용이다. 증빙을 완성한 뒤에도 차량 제한이 별도로 작동한다.

집필 원고 ID: `C046`, 전체 문항 SHA-256: `47b32f4cc806cec67a38ed673561ff8718f028c6ae06c19aed994149de3effd4`

[문항 메타데이터](../data/batch_2/C_vat/B2_C046_47b32f4c/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_001_050.json)

입력 파일:

- [01_신고범위.hwpx](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/01_신고범위.hwpx) (hwpx)
- [02_허가대장.xlsx](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/02_허가대장.xlsx) (xlsx)
- [03_허가공급.pdf](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/03_허가공급.pdf) (pdf)
- [04_말소공급.pdf](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/04_말소공급.pdf) (pdf)
- [05_직접사용.hwpx](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/05_직접사용.hwpx) (hwpx)
- [06_사무사용.hwpx](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/06_사무사용.hwpx) (hwpx)
- [07_실행.xlsx](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/07_실행.xlsx) (xlsx)
- [08_허가원본.pdf](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/08_허가원본.pdf) (pdf)
- [09_말소원본.pdf](../data/batch_2/C_vat/B2_C046_47b32f4c/inputs/09_말소원본.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C046_47b32f4c/gold.json)

```json
{
  "deductible_input_vat": 60000,
  "noncreditable_vat": 80000,
  "unique_transaction_count": 2
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["남빛부분카드", "남빛전자전"], "documented_input_vat": 60000, "eligible_input_document_ids": ["남빛전자전"], "gross": 660000, "invoice_issued": true, "issued_receipt_gross": 220000, "paid_gross": 220000, "purchase_activity_f... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 2} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 2} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 660000, "supply_base": 600000, "vat": 60000} |
| VAT_INPUT_EVIDENCE | {"deductible": 60000, "noncreditable": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 880000, "supply_base": 800000, "vat": 80000} |
| VAT_PASSENGER_CAR | {"deductible": 0, "noncreditable": 80000} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -60000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 60000, "input_vat": 140000, "net_vat": -60000, "noncreditable_vat": 80000, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 60000, "tax_base": 0, "unique_transacti... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C046_47b32f4c/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C047_21e54baa (C_vat, hard)

집필 제목: 강의 녹화와 판매 촬영 및 다음 달 설비 인수

업무 목적: 디지털 서비스 사용 목적과 설비 공급 기간을 독립 적용한다.

가상포개교구의 기관 납품 세 건과 세 구매를 정리해 주세요. 강의 녹화 용역의 전용 업무와 판매 촬영 용역을 구분하고 아직 다음 달에 인도한 설비를 공급일로 분리해 공제가능 매입세액(deductible_input_vat), 공제불가 매입세액(noncreditable_vat), 납부액(payable_vat), 고유 거래 수(unique_transaction_count)를 answer.json에 적어 주세요.

설계 의도: 면세 강의 녹화와 과세 판매 촬영은 같은 공급자라도 별도 용역이다. 제작 설비는 과세업무 전용이지만 7월 실제 인도이므로 목적이 정상이라는 이유로 현재 공제에 넣지 않는다.

집필 원고 ID: `C047`, 전체 문항 SHA-256: `21e54baabe8f35d6234a2105e3b3d68a5bff07dba079bef0c7ca6ea7556838bb`

[문항 메타데이터](../data/batch_2/C_vat/B2_C047_21e54baa/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_001_050.json)

입력 파일:

- [01_업무.hwpx](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/01_업무.hwpx) (hwpx)
- [02_기관1.pdf](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/02_기관1.pdf) (pdf)
- [03_기관2.xlsx](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/03_기관2.xlsx) (xlsx)
- [04_기관3.pdf](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/04_기관3.pdf) (pdf)
- [05_녹화.pdf](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/05_녹화.pdf) (pdf)
- [06_촬영.xlsx](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/06_촬영.xlsx) (xlsx)
- [07_절곡기.pdf](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/07_절곡기.pdf) (pdf)
- [08_영상사용.pdf](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/08_영상사용.pdf) (pdf)
- [09_설비인수.hwpx](../data/batch_2/C_vat/B2_C047_21e54baa/inputs/09_설비인수.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/C_vat/B2_C047_21e54baa/gold.json)

```json
{
  "deductible_input_vat": 46000,
  "noncreditable_vat": 85000,
  "payable_vat": 704000,
  "unique_transaction_count": 5
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| VAT_ACTIVITY_EVIDENCE | [{"business_related": true, "document_id": "포개-녹화전자", "purpose": "exempt_business", "transaction_id": "포개-강의녹화"}, {"business_related": true, "document_id": "포개-촬영전자", "purpose": "business", "transaction_id": "포개-판매촬영"}, {"busin... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 935000, "supply_base": 850000, "vat": 85000} |
| VAT_EXEMPT_LAND | {"deductible": 0, "noncreditable": 85000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 2750000, "supply_base": 2500000, "vat": 250000} |
| VAT_OUTPUT_10 | 250000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1980000, "supply_base": 1800000, "vat": 180000} |
| VAT_OUTPUT_10 | 180000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 3520000, "supply_base": 3200000, "vat": 320000} |
| VAT_OUTPUT_10 | 320000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 0} |
| VAT_PERIOD | false |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 506000, "supply_base": 460000, "vat": 46000} |
| VAT_INPUT_EVIDENCE | {"deductible": 46000, "noncreditable": 0} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 704000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 46000, "input_vat": 131000, "net_vat": 704000, "noncreditable_vat": 85000, "output_vat": 750000, "payable_vat": 704000, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 0, "tax_base": 7500000, "uniq... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C047_21e54baa/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C053_015a61fa (C_vat, easy)

집필 제목: 재료 전표의 세액 표시를 다시 받은 제작실

업무 목적: 일반 영수증과 취소 전표를 보관하면서도 유효 대체 전표의 표시를 사용한다.

가상풀잎제작의 직원이 재료 카드 원본의 세액 표시를 정정받았습니다. 원본 효력을 먼저 대조하고 실제 제작 사용을 확인하여 공제 매입세액(deductible_input_vat)과 환급액(refund_vat)을 answer.json에 정리하세요.

설계 의도: 별도 세액 없는 구 카드가 취소되고 같은 실제 지급의 적격 대체 카드가 유효하다. 전체 전자가 대신 보완하는 이전 문제와 달리 같은 지급의 표시 정정이 공제 근거다.

집필 원고 ID: `C053`, 전체 문항 SHA-256: `015a61fa17c01bf9fc41e2d2c16678b39f97e06c51d55dce7b5320a433871e91`

[문항 메타데이터](../data/batch_2/C_vat/B2_C053_015a61fa/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_제작인수.hwpx](../data/batch_2/C_vat/B2_C053_015a61fa/inputs/01_제작인수.hwpx) (hwpx)
- [02_지급원본.xlsx](../data/batch_2/C_vat/B2_C053_015a61fa/inputs/02_지급원본.xlsx) (xlsx)
- [03_표시정정.pdf](../data/batch_2/C_vat/B2_C053_015a61fa/inputs/03_표시정정.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C053_015a61fa/gold.json)

```json
{
  "deductible_input_vat": 50000,
  "refund_vat": 50000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["구카드"], "replacement_relations": [{"revoked_document_id": "구카드", "valid_document_id": "정정카드"}], "selected_document_ids": ["인수영수증", "정정카드"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["인수영수증", "정정카드"], "documented_input_vat": 50000, "eligible_input_document_ids": ["정정카드"], "gross": 550000, "invoice_issued": false, "issued_receipt_gross": 550000, "paid_gross": 550000, "purchase_activity_fac... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 2} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 550000, "supply_base": 500000, "vat": 50000} |
| VAT_INPUT_EVIDENCE | {"deductible": 50000, "noncreditable": 0} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -50000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 50000, "input_vat": 50000, "net_vat": -50000, "noncreditable_vat": 0, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 50000, "tax_base": 0, "unique_transaction_co... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C053_015a61fa/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C060_dc120371 (C_vat, easy)

집필 제목: 두 번 전달된 대체 전표와 취소된 독립 승인

업무 목적: 재전달된 유효 원본은 한 번만 사용하고 별도 실행의 취소 원본은 발급 모수에서 뺀다.

가상갈대패치는 대체 카드 원본을 경리와 매장에서 각각 전달했습니다. 원본 ID의 동일 재전달을 구별하고 별도 승인 취소를 확인하여 발행 공제(receipt_credit)와 매출세액(output_vat)을 answer.json에 작성하세요.

설계 의도: 대체 전표와 상태의 exact 재전달은 한 실제 지급이다. 다른 카드 실행은 같은 금액이라도 별도 원본이며 최종 취소됐다. ID 중복 정리와 원본 효력 선택을 함께 해야 모수가 맞는다.

집필 원고 ID: `C060`, 전체 문항 SHA-256: `dc120371725c2ff46027e6559c5d849a07fbe932375fa599d1f1f6204cd07361`

[문항 메타데이터](../data/batch_2/C_vat/B2_C060_dc120371/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_패치실행.pdf](../data/batch_2/C_vat/B2_C060_dc120371/inputs/01_패치실행.pdf) (pdf)
- [02_전달묶음.xlsx](../data/batch_2/C_vat/B2_C060_dc120371/inputs/02_전달묶음.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/C_vat/B2_C060_dc120371/gold.json)

```json
{
  "output_vat": 40000,
  "receipt_credit": 2860
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["구전표", "둘원본"], "replacement_relations": [{"revoked_document_id": "구전표", "valid_document_id": "대체원본"}], "selected_document_ids": ["대체원본"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["대체원본"], "documented_input_vat": 0, "eligible_input_document_ids": [], "gross": 440000, "invoice_issued": false, "issued_receipt_gross": 220000, "paid_gross": 440000, "supply_base": 400000, "transaction_id": ... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 440000, "supply_base": 400000, "vat": 40000} |
| VAT_OUTPUT_10 | 40000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 220000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 2860 |
| VAT_CREDIT_ANNUAL_LIMIT | 2860 |
| VAT_CREDIT_PAYABLE_LIMIT | 2860 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 37140 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 37140, "noncreditable_vat": 0, "output_vat": 40000, "payable_vat": 37140, "prepaid_vat": 0, "receipt_credit": 2860, "refund_vat": 0, "tax_base": 400000, "unique_transaction... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C060_dc120371/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C062_5b890dbb (C_vat, easy)

집필 제목: 개당 할인과 행 할인 및 상품 전체 할인 뒤 과세 배송 합산

업무 목적: 서로 다른 할인 단위와 상품 및 배송 범위를 복원해 한 완료 판매의 과세 공급액과 카드 발행 모수를 계산한다.

가상포개소매는 정상 완료 주문의 청구 행을 보냈습니다. 개당 할인은 수량에 곱하고 행 전체 할인은 한 번만 빼 주세요. 상품 전체 할인에는 배송을 넣지 않습니다. 확정 청구와 카드 발행 기초를 연결해 tax_base, output_vat, receipt_credit를 answer.json에 정리해 주세요.

설계 의도: 첫 행에는 개당500원 할인과 별도 행 전체2000원 할인이 있고 두 번째 행에는 할인이 없다. 두 상품행 합계에 전체10000원 할인을 적용한 뒤 별도로 과세 배송15000원을 더한다. 할인 단위를 섞거나 배송까지 상품 할인 범위로 다루면 현재 실제 공급액과 발행 공제가 함께 틀린다. scalar 거래액에 이름과 금액만 바꾸는 문제가 아니라 확정 청구의 세 가격 단위를 원천에서 구한다.

집필 원고 ID: `C062`, 전체 문항 SHA-256: `5b890dbbf840656cb59357182f50dd04471c41177a0a069975fae4df846c64ca`

[문항 메타데이터](../data/batch_2/C_vat/B2_C062_5b890dbb/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_청구행.xlsx](../data/batch_2/C_vat/B2_C062_5b890dbb/inputs/01_청구행.xlsx) (xlsx)
- [02_신고발행.pdf](../data/batch_2/C_vat/B2_C062_5b890dbb/inputs/02_신고발행.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C062_5b890dbb/gold.json)

```json
{
  "output_vat": 13500,
  "receipt_credit": 1930,
  "tax_base": 135000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_VAT_ITEMIZED_ACTIVITY | {"deduplicated_document_ids": [], "invoice_amounts": [{"document_discount": 10000, "document_id": "포개완납카드", "final_gross": 148500, "final_supply": 135000, "final_vat": 13500, "freight_supply": 15000, "lines": [{"after_unit_disc... |
| VAT_ACTIVITY_EVIDENCE | [] |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 148500, "supply_base": 135000, "vat": 13500} |
| VAT_OUTPUT_10 | 13500 |
| VAT_RECEIPT_BASE | {"eligible_gross": 148500} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 1930 |
| VAT_CREDIT_ANNUAL_LIMIT | 1930 |
| VAT_CREDIT_PAYABLE_LIMIT | 1930 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 11570 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 11570, "noncreditable_vat": 0, "output_vat": 13500, "payable_vat": 11570, "prepaid_vat": 0, "receipt_credit": 1930, "refund_vat": 0, "tax_base": 135000, "unique_transaction... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C062_5b890dbb/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C063_4db2f548 (C_vat, easy)

집필 제목: 발급 모수와 달리 공제 전에 세금이 없는 재고점

업무 목적: 유효 부분 발급을 찾았어도 공제 전 환급 상태를 먼저 확인한다.

가상여울끈은 취소된 전자와 유효 카드 판매를 정리하면서 새 재고를 인수했습니다. 현재 원본 효력과 매입을 함께 반영하여 발행 공제(receipt_credit) 및 환급액(refund_vat)을 answer.json에 회신하세요.

설계 의도: 판매 전자 취소로 유효 카드 대금은 발급 모수에 남지만 적격 재고 전자가 매출세액보다 커 실제 발행 공제는0이다. 재고 전자 효력을 취소하고 유효 일반 인수 원본만 남기면 liability가 양수로 바뀌고 판매 공제가 살아난다. 모수 선택이 다른 단계와 연결되는 쉬운 재고 마감이다.

집필 원고 ID: `C063`, 전체 문항 SHA-256: `4db2f54821f44d7b9abc025054a9e79cfaa8e18e84ad872622eef9109d3d3123`

[문항 메타데이터](../data/batch_2/C_vat/B2_C063_4db2f548/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_소매인수.hwpx](../data/batch_2/C_vat/B2_C063_4db2f548/inputs/01_소매인수.hwpx) (hwpx)
- [02_판매구매원본.xlsx](../data/batch_2/C_vat/B2_C063_4db2f548/inputs/02_판매구매원본.xlsx) (xlsx)
- [03_효력정리.pdf](../data/batch_2/C_vat/B2_C063_4db2f548/inputs/03_효력정리.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C063_4db2f548/gold.json)

```json
{
  "receipt_credit": 0,
  "refund_vat": 10000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["판매전자"], "replacement_relations": [], "selected_document_ids": ["재고전자", "재고종이", "판매발급"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["재고전자", "재고종이"], "documented_input_vat": 60000, "eligible_input_document_ids": ["재고전자"], "gross": 660000, "invoice_issued": true, "issued_receipt_gross": 0, "paid_gross": 660000, "purchase_activity_facts": {"... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 2} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 660000, "supply_base": 600000, "vat": 60000} |
| VAT_INPUT_EVIDENCE | {"deductible": 60000, "noncreditable": 0} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 550000, "supply_base": 500000, "vat": 50000} |
| VAT_OUTPUT_10 | 50000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 220000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 2860 |
| VAT_CREDIT_ANNUAL_LIMIT | 2860 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -10000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 60000, "input_vat": 60000, "net_vat": -10000, "noncreditable_vat": 0, "output_vat": 50000, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 10000, "tax_base": 500000, "unique_trans... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C063_4db2f548/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C070_f3bbb1a2 (C_vat, medium)

집필 제목: 오기 취소액을 빼면 연간 잔여 아래인 수금

업무 목적: 취소된 오기 발급액으로 연간 잔여를 소진하지 않는다.

가상복숭아매듭은 부분 수금 전표를 금액 정정받았습니다. 취소 원본을 제외한 실제 유효 발급 대금과 앞선 공제 이력을 맞춰 발행 공제(receipt_credit) 및 납부액(payable_vat)을 answer.json에 적으세요.

설계 의도: 실제유효부분발급220,000원의율공제2,860원은연간잔여3,000원보다작다. 취소오기330,000원을쓰면4,290원으로잘못잔여를전부사용한다. 같은지급의정정선택이연간캡의적용분기를바꾼다.

집필 원고 ID: `C070`, 전체 문항 SHA-256: `f3bbb1a26d593bc2e66a2c1635aa8856cb29cd570e540df4258a772b1d581c75`

[문항 메타데이터](../data/batch_2/C_vat/B2_C070_f3bbb1a2/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_이전확정.hwpx](../data/batch_2/C_vat/B2_C070_f3bbb1a2/inputs/01_이전확정.hwpx) (hwpx)
- [02_완료공급.pdf](../data/batch_2/C_vat/B2_C070_f3bbb1a2/inputs/02_완료공급.pdf) (pdf)
- [03_원본및지급.xlsx](../data/batch_2/C_vat/B2_C070_f3bbb1a2/inputs/03_원본및지급.xlsx) (xlsx)
- [04_정정효력.pdf](../data/batch_2/C_vat/B2_C070_f3bbb1a2/inputs/04_정정효력.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C070_f3bbb1a2/gold.json)

```json
{
  "payable_vat": 97140,
  "receipt_credit": 2860
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["큰오기"], "replacement_relations": [{"revoked_document_id": "큰오기", "valid_document_id": "실제대체"}], "selected_document_ids": ["실제대체"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["실제대체"], "documented_input_vat": 0, "eligible_input_document_ids": [], "gross": 1100000, "invoice_issued": false, "issued_receipt_gross": 220000, "paid_gross": 660000, "supply_base": 1000000, "transaction_id"... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1100000, "supply_base": 1000000, "vat": 100000} |
| VAT_OUTPUT_10 | 100000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 220000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 2860 |
| VAT_CREDIT_ANNUAL_LIMIT | 2860 |
| VAT_CREDIT_PAYABLE_LIMIT | 2860 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 97140 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 97140, "noncreditable_vat": 0, "output_vat": 100000, "payable_vat": 97140, "prepaid_vat": 0, "receipt_credit": 2860, "refund_vat": 0, "tax_base": 1000000, "unique_transacti... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C070_f3bbb1a2/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C072_2796fcd4 (C_vat, easy)

집필 제목: 공식 배송 차종과 확정된 적격 정비 원본

업무 목적: 적격 전표의 선택과 등록 차종의 공제 제한 여부를 다른 단계로 확인한다.

가상감람배송은 정비 카드의 표시 정정과 차량 등록 대장을 인계했습니다. 현재 유효 원본 및 실제 차량 ID를 대조하여 공제 매입세액(deductible_input_vat)과 불공제세액(noncreditable_vat)을 answer.json에 제출하세요.

설계 의도: 현재 비개별소비세 화물차 정비의 유효 표시 대체 전표는 정상 공제 자료다. 공식 차종과 정비 차량 ID 및 실제 작업 귀속을 확인하고 확정된 대체 원본만 읽는다. 이미 취소된 과거 미표시 원본은 현재 예외로 세지 않는다.

집필 원고 ID: `C072`, 전체 문항 SHA-256: `2796fcd435daf4252faff0f121c555de3ad081e1b46e33301ea0b585d2ecba41`

[문항 메타데이터](../data/batch_2/C_vat/B2_C072_2796fcd4/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_정비인수.hwpx](../data/batch_2/C_vat/B2_C072_2796fcd4/inputs/01_정비인수.hwpx) (hwpx)
- [02_등록차종.pdf](../data/batch_2/C_vat/B2_C072_2796fcd4/inputs/02_등록차종.pdf) (pdf)
- [03_지급및확정원본.xlsx](../data/batch_2/C_vat/B2_C072_2796fcd4/inputs/03_지급및확정원본.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/C_vat/B2_C072_2796fcd4/gold.json)

```json
{
  "deductible_input_vat": 40000,
  "noncreditable_vat": 0
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["정비구본"], "replacement_relations": [{"revoked_document_id": "정비구본", "valid_document_id": "정비대체"}], "selected_document_ids": ["정비대체", "정비종이"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["정비대체", "정비종이"], "documented_input_vat": 40000, "eligible_input_document_ids": ["정비대체"], "gross": 440000, "invoice_issued": false, "issued_receipt_gross": 440000, "paid_gross": 440000, "purchase_activity_fact... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 2} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 440000, "supply_base": 400000, "vat": 40000} |
| VAT_INPUT_EVIDENCE | {"deductible": 40000, "noncreditable": 0} |
| VAT_CREDIT_ELIGIBILITY | false |
| VAT_CREDIT_RATE_2026 | 0 |
| VAT_CREDIT_ANNUAL_LIMIT | 0 |
| VAT_CREDIT_PAYABLE_LIMIT | 0 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | -40000 |
| VAT_SETTLEMENT | {"deductible_input_vat": 40000, "input_vat": 40000, "net_vat": -40000, "noncreditable_vat": 0, "output_vat": 0, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 0, "refund_vat": 40000, "tax_base": 0, "unique_transaction_co... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C072_2796fcd4/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C075_b07a2558 (C_vat, medium)

집필 제목: 신고 점포의 전년 자격과 실제 유효 정정 발급

업무 목적: 다른 점포와 다른 연도의 큰 매출을 신고 점포 자격에 대신 쓰지 않는다.

가상앵두문고는 점포별 연도 대장과 발급 금액 정정을 보냈습니다. 신고 점포의 전년 공급가액 및 현재 유효한 실제 부분 발급을 찾아 발행 공제(receipt_credit)와 납부액(payable_vat)을 answer.json에 쓰세요.

설계 의도: 신고점포의2025년공급가액은정확히10억원이라자격이있고유효정정발급220,000원이모수다. 다른점포2025년과신고점포2024년은초과값이라행번호또는합계선택은틀린다. 효력선택과점포연도선택은각각공제액을바꾼다. 연간잔여제한은없어다른annual사례와전체graph가다르다.

집필 원고 ID: `C075`, 전체 문항 SHA-256: `b07a255801230a8a8d51479bcf64ee9e5a1ed02b48abf58ee9c17c9950050f56`

[문항 메타데이터](../data/batch_2/C_vat/B2_C075_b07a2558/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_신고점포.pdf](../data/batch_2/C_vat/B2_C075_b07a2558/inputs/01_신고점포.pdf) (pdf)
- [02_연도대장.xlsx](../data/batch_2/C_vat/B2_C075_b07a2558/inputs/02_연도대장.xlsx) (xlsx)
- [03_지급정정.hwpx](../data/batch_2/C_vat/B2_C075_b07a2558/inputs/03_지급정정.hwpx) (hwpx)
- [04_최종효력.pdf](../data/batch_2/C_vat/B2_C075_b07a2558/inputs/04_최종효력.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C075_b07a2558/gold.json)

```json
{
  "payable_vat": 77140,
  "receipt_credit": 2860
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["문구오기"], "replacement_relations": [{"revoked_document_id": "문구오기", "valid_document_id": "문구정정"}], "selected_document_ids": ["문구정정"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["문구정정"], "documented_input_vat": 0, "eligible_input_document_ids": [], "gross": 880000, "invoice_issued": false, "issued_receipt_gross": 220000, "paid_gross": 220000, "supply_base": 800000, "transaction_id": ... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 880000, "supply_base": 800000, "vat": 80000} |
| VAT_OUTPUT_10 | 80000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 220000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 2860 |
| VAT_CREDIT_ANNUAL_LIMIT | 2860 |
| VAT_CREDIT_PAYABLE_LIMIT | 2860 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 77140 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 0, "net_vat": 77140, "noncreditable_vat": 0, "output_vat": 80000, "payable_vat": 77140, "prepaid_vat": 0, "receipt_credit": 2860, "refund_vat": 0, "tax_base": 800000, "unique_transaction... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C075_b07a2558/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C085_e1b4c9cf (C_vat, medium)

집필 제목: 별도 면세 강의실의 구매가 소비자 발급 공제에 미치는 영향

업무 목적: 적격 장비 원본이 있어도 직접 면세 업무 사용 제한을 반영한 뒤 판매 공제를 계산한다.

가상파파야노트는 과세 노트 판매와 별도 강의실 전용 장비를 인계했습니다. 실제 업무 ID 및 현재 발급 효력을 연결하여 불공제세액(noncreditable_vat)과 발행 공제(receipt_credit) 및 순정산액(net_vat)을 answer.json에 적으세요.

설계 의도: 노트소매는과세이고구매장비는별도면세강의업무에직접설치돼50,000원불공제다. 소매현금부분110,000원은유효이고카드원본만취소라공제1,430원이남는다. 장비활동을별도과세촬영업무로연결하면입력공제가매출세액을넘어발급공제도0이된다. 목적이단순장식이아닌공제가능성의상위제약이다.

집필 원고 ID: `C085`, 전체 문항 SHA-256: `e1b4c9cfafca8c2c29442d016c1b885e9a20385d89b1d321f8d4502c9ea4c225`

[문항 메타데이터](../data/batch_2/C_vat/B2_C085_e1b4c9cf/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_별도업무.pdf](../data/batch_2/C_vat/B2_C085_e1b4c9cf/inputs/01_별도업무.pdf) (pdf)
- [02_전용인수.hwpx](../data/batch_2/C_vat/B2_C085_e1b4c9cf/inputs/02_전용인수.hwpx) (hwpx)
- [03_지급발급.xlsx](../data/batch_2/C_vat/B2_C085_e1b4c9cf/inputs/03_지급발급.xlsx) (xlsx)
- [04_최종효력.pdf](../data/batch_2/C_vat/B2_C085_e1b4c9cf/inputs/04_최종효력.pdf) (pdf)

정답: [gold.json](../data/batch_2/C_vat/B2_C085_e1b4c9cf/gold.json)

```json
{
  "net_vat": 18570,
  "noncreditable_vat": 50000,
  "receipt_credit": 1430
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["카드발급"], "replacement_relations": [], "selected_document_ids": ["장비전자", "현금발급"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["장비전자"], "documented_input_vat": 50000, "eligible_input_document_ids": ["장비전자"], "gross": 550000, "invoice_issued": true, "issued_receipt_gross": 0, "paid_gross": 0, "purchase_activity_facts": {"business_rela... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 550000, "supply_base": 500000, "vat": 50000} |
| VAT_EXEMPT_LAND | {"deductible": 0, "noncreditable": 50000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 220000, "supply_base": 200000, "vat": 20000} |
| VAT_OUTPUT_10 | 20000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 110000} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 1430 |
| VAT_CREDIT_ANNUAL_LIMIT | 1430 |
| VAT_CREDIT_PAYABLE_LIMIT | 1430 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 18570 |
| VAT_SETTLEMENT | {"deductible_input_vat": 0, "input_vat": 50000, "net_vat": 18570, "noncreditable_vat": 50000, "output_vat": 20000, "payable_vat": 18570, "prepaid_vat": 0, "receipt_credit": 1430, "refund_vat": 0, "tax_base": 200000, "unique_tra... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C085_e1b4c9cf/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_C096_f7407420 (C_vat, hard)

집필 제목: 전환 전후 자재와 면세 전용 장비가 발행 공제 캡을 바꾸는 정산

업무 목적: 공급자 자격과 직접 면세 사용 및 표시 정정을 서로 다른 구매에 적용해 판매 공제의 납부 제한을 판단한다.

가상브램블메모는 공급자 전환 전후 구매와 별도 강의 장비 및 현재 소매 발급을 인계했습니다. 실제 구매일과 업무 ID 및 유효 원본을 연결하여 공제 매입세액(deductible_input_vat)과 불공제세액(noncreditable_vat) 및 발행 공제(receipt_credit)를 answer.json에 제출하세요.

설계 의도: 4월자재60,000원은간이기간이라제한되고5월자재98,000원은일반전환후유효표시대체카드로공제한다. 별도면세강의장비30,000원은직접용도로제한된다. 소매세액100,000원에서공제후2,000원만남아유효부분발급율7,150원을제한한다. 5월대체효력과4월자격및강의귀속각변화가납부캡/환급분기를다르게바꾼다.

집필 원고 ID: `C096`, 전체 문항 SHA-256: `f740742034181b38d2c4c62c828355c94ecc4045e54930c3a9fb56495f7fa640`

[문항 메타데이터](../data/batch_2/C_vat/B2_C096_f7407420/task.yaml)와 [집필 원고](../authored/batch_2/C_vat/cases_051_100.json)

입력 파일:

- [01_업무범위.hwpx](../data/batch_2/C_vat/B2_C096_f7407420/inputs/01_업무범위.hwpx) (hwpx)
- [02_등록기간.pdf](../data/batch_2/C_vat/B2_C096_f7407420/inputs/02_등록기간.pdf) (pdf)
- [03_사월인수.hwpx](../data/batch_2/C_vat/B2_C096_f7407420/inputs/03_사월인수.hwpx) (hwpx)
- [04_오월인수.pdf](../data/batch_2/C_vat/B2_C096_f7407420/inputs/04_오월인수.pdf) (pdf)
- [05_강의인수.hwpx](../data/batch_2/C_vat/B2_C096_f7407420/inputs/05_강의인수.hwpx) (hwpx)
- [06_실제지급.xlsx](../data/batch_2/C_vat/B2_C096_f7407420/inputs/06_실제지급.xlsx) (xlsx)
- [07_소매원본.pdf](../data/batch_2/C_vat/B2_C096_f7407420/inputs/07_소매원본.pdf) (pdf)
- [08_사월카드.xlsx](../data/batch_2/C_vat/B2_C096_f7407420/inputs/08_사월카드.xlsx) (xlsx)
- [09_오월정정.hwpx](../data/batch_2/C_vat/B2_C096_f7407420/inputs/09_오월정정.hwpx) (hwpx)
- [10_강의전자.pdf](../data/batch_2/C_vat/B2_C096_f7407420/inputs/10_강의전자.pdf) (pdf)
- [11_최종효력.xlsx](../data/batch_2/C_vat/B2_C096_f7407420/inputs/11_최종효력.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/C_vat/B2_C096_f7407420/gold.json)

```json
{
  "deductible_input_vat": 98000,
  "noncreditable_vat": 90000,
  "receipt_credit": 2000
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| C_DOCUMENT_LIFECYCLE_SELECTION | {"excluded_document_ids": ["소매전자", "오월구본"], "replacement_relations": [{"revoked_document_id": "오월구본", "valid_document_id": "오월대체"}], "selected_document_ids": ["강의전자", "사월카드", "소매카드", "오월대체", "오월종이"]} |
| C_DOCUMENT_RECONCILIATION | [{"document_ids": ["소매카드"], "documented_input_vat": 0, "eligible_input_document_ids": [], "gross": 1100000, "invoice_issued": false, "issued_receipt_gross": 550000, "paid_gross": 550000, "supply_base": 1000000, "transaction_id"... |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": true, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 1} |
| VAT_DEDUP | {"counted_once": true, "invoice_issued": false, "occurrences": 2} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1100000, "supply_base": 1000000, "vat": 100000} |
| VAT_OUTPUT_10 | 100000 |
| VAT_RECEIPT_BASE | {"eligible_gross": 550000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 330000, "supply_base": 300000, "vat": 30000} |
| VAT_EXEMPT_LAND | {"deductible": 0, "noncreditable": 30000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 660000, "supply_base": 600000, "vat": 60000} |
| VAT_INPUT_EVIDENCE | {"deductible": 0, "noncreditable": 60000} |
| VAT_PERIOD | true |
| VAT_TAX_BASE | {"gross": 1078000, "supply_base": 980000, "vat": 98000} |
| VAT_INPUT_EVIDENCE | {"deductible": 98000, "noncreditable": 0} |
| VAT_CREDIT_ELIGIBILITY | true |
| VAT_CREDIT_RATE_2026 | 7150 |
| VAT_CREDIT_ANNUAL_LIMIT | 7150 |
| VAT_CREDIT_PAYABLE_LIMIT | 2000 |
| VAT_ASSESSMENT_VALIDITY | {"assessment_is_consistent": true, "prior_return_payment_deducted_again": false} |
| VAT_PREPAID | 0 |
| VAT_SETTLEMENT | {"deductible_input_vat": 98000, "input_vat": 188000, "net_vat": 0, "noncreditable_vat": 90000, "output_vat": 100000, "payable_vat": 0, "prepaid_vat": 0, "receipt_credit": 2000, "refund_vat": 0, "tax_base": 1000000, "unique_tran... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/C_vat/B2_C096_f7407420/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D004_7460c50e (D_extract, easy)

집필 제목: 분할 실행한 인쇄판 구매 대금의 남은 지급

업무 목적: 실제로 송금한 계약금과 중도금을 합쳐 남은 현금 지급액을 확인한다.

인쇄판을 인수한 금액과 두 번 실행한 송금을 대조하세요. 약정대로 인수 대금을 구한 뒤 실행 지급을 합쳐 차감합니다. answer.json에는 vendor_balances와 payment_total을 작성하세요. 업체명은 NFKC, 공백과 법인 표기 제거 후 소문자로 정리해 이름순으로 배열합니다.

설계 의도: 모든 인쇄판을 받았으나 송금은 두 지급 번호로 나뉘어 있다. 인수 정산과 실행 지급을 별도 원문에서 결합하는 현금 대조 업무로 직접 구성했다.

집필 원고 ID: `D004`, 전체 문항 SHA-256: `7460c50e091c974c9fa9848970a9eeefee69046f7da832ee463fd63110fbfc25`

[문항 메타데이터](../data/batch_2/D_extract/B2_D004_7460c50e/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_001_050.json)

입력 파일:

- [01_인쇄판약정.pdf](../data/batch_2/D_extract/B2_D004_7460c50e/inputs/01_인쇄판약정.pdf) (pdf)
- [02_인쇄판입고.hwpx](../data/batch_2/D_extract/B2_D004_7460c50e/inputs/02_인쇄판입고.hwpx) (hwpx)
- [03_인쇄판송금.xlsx](../data/batch_2/D_extract/B2_D004_7460c50e/inputs/03_인쇄판송금.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/D_extract/B2_D004_7460c50e/gold.json)

```json
{
  "payment_total": 190000,
  "vendor_balances": [
    {
      "balance": 74000,
      "paid": 190000,
      "supply": 240000,
      "total": 264000,
      "vat": 24000,
      "vendor": "가상인쇄판제작"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.fulfillment_reconciliation | {"accepted_event_ids": ["PLATE-IN"], "accepted_payment_ids": ["PLATE-DEPOSIT", "PLATE-MIDDLE"], "deduplicated_event_ids": [], "deduplicated_payment_ids": [], "event_timeline": [{"event_id": "PLATE-IN", "net_units_after_event": ... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D004_7460c50e/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D008_e9fbb95a (D_extract, easy)

집필 제목: 포함 포장가격의 실제 인수 행 세액

업무 목적: 부가세 포함 포장가격과 부분 포장 인수를 연결해 행 정산액을 기록한다.

촬영용 확산판을 실제 받은 수량으로 정산하세요. 포함 포장가격에 순인수량을 곱하고 포장당수량으로 나눈 뒤 버린 금액의 10/11을 다시 버려 공급가액을 구합니다. 차액은 세액입니다. answer.json에는 line_settlements를 작성하세요.

설계 의도: 완전한 포장 금액을 역산하는 것이 아니라 4개 포장에서 실제 3개 받은 대금을 먼저 비율 정산한다. 가격 환산과 세금 분리의 계산 순서를 직접 다르게 설계했다.

집필 원고 ID: `D008`, 전체 문항 SHA-256: `e9fbb95abb443d70db15c9907d92d067ff82abfef435222d0b42300532733a48`

[문항 메타데이터](../data/batch_2/D_extract/B2_D008_e9fbb95a/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_001_050.json)

입력 파일:

- [01_확산판계약.pdf](../data/batch_2/D_extract/B2_D008_e9fbb95a/inputs/01_확산판계약.pdf) (pdf)
- [02_확산판입고.xlsx](../data/batch_2/D_extract/B2_D008_e9fbb95a/inputs/02_확산판입고.xlsx) (xlsx)

정답: [gold.json](../data/batch_2/D_extract/B2_D008_e9fbb95a/gold.json)

```json
{
  "line_settlements": [
    {
      "base_unit": "개",
      "item": "촬영확산판",
      "line_id": "D",
      "net_units": 3,
      "order_id": "DIFFUSE-4",
      "ordered_units": 8,
      "outstanding_units": 5,
      "received_units": 3,
      "returned_units": 0,
      "supply": 7501,
      "total": 8252,
      "vat": 751
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.fulfillment_reconciliation | {"accepted_event_ids": ["DIFFUSE-IN"], "accepted_payment_ids": [], "deduplicated_event_ids": [], "deduplicated_payment_ids": [], "event_timeline": [{"event_id": "DIFFUSE-IN", "net_units_after_event": 3}], "excluded_after_cutoff... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D008_e9fbb95a/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D025_1ef89d92 (D_extract, medium)

집필 제목: 인수금액보다 선지급이 큰 보호문 잔액

업무 목적: 초과 선지급을 미지급 0원으로 지워버리지 않는다.

보호문 실제 인수 대금과 선지급을 대조하세요. 인수 대금보다 지급액이 크면 업체 잔액의 음수를 그대로 보고합니다. answer.json에는 vendor_balances와 balance_total을 작성하세요.

설계 의도: 부분 인수에 대한 정산금액보다 실행된 계약금이 더 크다. 미인수량과 현금 초과 집행을 혼동하지 않고 업체에게 남아 있는 선지급 잔액을 음수로 보여 준다.

집필 원고 ID: `D025`, 전체 문항 SHA-256: `1ef89d927a2088ed226f0e497f6bc1c47f266b23ccd71ed65874d72b36fd9e3e`

[문항 메타데이터](../data/batch_2/D_extract/B2_D025_1ef89d92/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_001_050.json)

입력 파일:

- [01_보호문계약.pdf](../data/batch_2/D_extract/B2_D025_1ef89d92/inputs/01_보호문계약.pdf) (pdf)
- [02_보호문입고.xlsx](../data/batch_2/D_extract/B2_D025_1ef89d92/inputs/02_보호문입고.xlsx) (xlsx)
- [03_보호문선지급.hwpx](../data/batch_2/D_extract/B2_D025_1ef89d92/inputs/03_보호문선지급.hwpx) (hwpx)
- [04_선지급대조.pdf](../data/batch_2/D_extract/B2_D025_1ef89d92/inputs/04_선지급대조.pdf) (pdf)

정답: [gold.json](../data/batch_2/D_extract/B2_D025_1ef89d92/gold.json)

```json
{
  "balance_total": -45000,
  "vendor_balances": [
    {
      "balance": -45000,
      "paid": 100000,
      "supply": 50000,
      "total": 55000,
      "vat": 5000,
      "vendor": "가상보호문"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.fulfillment_reconciliation | {"accepted_event_ids": ["GUARD-IN"], "accepted_payment_ids": ["GUARD-DEP"], "deduplicated_event_ids": [], "deduplicated_payment_ids": [], "event_timeline": [{"event_id": "GUARD-IN", "net_units_after_event": 1}], "excluded_after... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D025_1ef89d92/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D026_e9723041 (D_extract, medium)

집필 제목: 전량 반환한 커넥터와 남은 계약금

업무 목적: 반품으로 대금이 사라진 거래의 실행 지급을 환급 대조 대상으로 유지한다.

커넥터 인수와 전량 반품 및 이미 실행한 계약금을 대조하세요. 실제 순인수가 0이 되어도 원주문 행과 선지급을 남깁니다. answer.json에는 line_settlements와 vendor_balances를 작성하세요.

설계 의도: 모든 커넥터를 받았다가 모두 반환했으며 선지급은 실제로 실행됐다. 주문 행 삭제와 반품 정산은 다르므로 0 순수량과 음수 업체 잔액을 함께 확인한다.

집필 원고 ID: `D026`, 전체 문항 SHA-256: `e972304139517e677936c2a18406d9e64b7689bb57b2c1ae0396cb1e7698c739`

[문항 메타데이터](../data/batch_2/D_extract/B2_D026_e9723041/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_001_050.json)

입력 파일:

- [01_커넥터약정.pdf](../data/batch_2/D_extract/B2_D026_e9723041/inputs/01_커넥터약정.pdf) (pdf)
- [02_커넥터입고.xlsx](../data/batch_2/D_extract/B2_D026_e9723041/inputs/02_커넥터입고.xlsx) (xlsx)
- [03_커넥터반품.hwpx](../data/batch_2/D_extract/B2_D026_e9723041/inputs/03_커넥터반품.hwpx) (hwpx)
- [04_커넥터계약금.pdf](../data/batch_2/D_extract/B2_D026_e9723041/inputs/04_커넥터계약금.pdf) (pdf)

정답: [gold.json](../data/batch_2/D_extract/B2_D026_e9723041/gold.json)

```json
{
  "line_settlements": [
    {
      "base_unit": "개",
      "item": "연결커넥터",
      "line_id": "C",
      "net_units": 0,
      "order_id": "CONNECT-ALL-RETURN",
      "ordered_units": 8,
      "outstanding_units": 8,
      "received_units": 8,
      "returned_units": 8,
      "supply": 0,
      "total": 0,
      "vat": 0
    }
  ],
  "vendor_balances": [
    {
      "balance": -20000,
      "paid": 20000,
      "supply": 0,
      "total": 0,
      "vat": 0,
      "vendor": "가상연결커넥터"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.fulfillment_reconciliation | {"accepted_event_ids": ["CONNECT-BACK", "CONNECT-IN"], "accepted_payment_ids": ["CONNECT-PAY"], "deduplicated_event_ids": [], "deduplicated_payment_ids": [], "event_timeline": [{"event_id": "CONNECT-IN", "net_units_after_event"... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D026_e9723041/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D032_23e9c0e6 (D_extract, medium)

집필 제목: 수량이 같은 별도 두 납품 이벤트의 구별

업무 목적: 같은 물량으로 연달아 도착한 두 입고를 하나로 지우지 않는다.

검수 테이프의 실제 입고량을 대조하세요. 날짜와 수량이 같아도 event_id가 다르면 별도로 발생한 인수입니다. 내용 유사성으로 중복 제거하지 않습니다. answer.json에는 item_quantities와 line_settlements를 작성하세요.

설계 의도: 동일 주문의 낱개 입고가 두 이벤트로 같은 날짜에 발생했다. 원문 번호가 아니라 실제 입고 이벤트 ID를 기준으로 두 수량을 유지하는 수불 업무이다.

집필 원고 ID: `D032`, 전체 문항 SHA-256: `23e9c0e6f0310947980371cb2146f11f17aa8dcf65ddb0f1c1701cac37c7c6ae`

[문항 메타데이터](../data/batch_2/D_extract/B2_D032_23e9c0e6/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_001_050.json)

입력 파일:

- [01_테이프주문.pdf](../data/batch_2/D_extract/B2_D032_23e9c0e6/inputs/01_테이프주문.pdf) (pdf)
- [02_테이프인수1.xlsx](../data/batch_2/D_extract/B2_D032_23e9c0e6/inputs/02_테이프인수1.xlsx) (xlsx)
- [03_테이프인수2.hwpx](../data/batch_2/D_extract/B2_D032_23e9c0e6/inputs/03_테이프인수2.hwpx) (hwpx)
- [04_테이프식별.pdf](../data/batch_2/D_extract/B2_D032_23e9c0e6/inputs/04_테이프식별.pdf) (pdf)

정답: [gold.json](../data/batch_2/D_extract/B2_D032_23e9c0e6/gold.json)

```json
{
  "item_quantities": [
    {
      "base_unit": "개",
      "item": "검수테이프",
      "net_units": 30
    }
  ],
  "line_settlements": [
    {
      "base_unit": "개",
      "item": "검수테이프",
      "line_id": "T",
      "net_units": 30,
      "order_id": "TAPE-TWO-ARRIVALS",
      "ordered_units": 40,
      "outstanding_units": 10,
      "received_units": 30,
      "returned_units": 0,
      "supply": 72000,
      "total": 79200,
      "vat": 7200
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.fulfillment_reconciliation | {"accepted_event_ids": ["TAPE-ARRIVAL-1", "TAPE-ARRIVAL-2"], "accepted_payment_ids": [], "deduplicated_event_ids": [], "deduplicated_payment_ids": [], "event_timeline": [{"event_id": "TAPE-ARRIVAL-1", "net_units_after_event": 1... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D032_23e9c0e6/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D052_82dbf946 (D_extract, easy)

집필 제목: 포장마다가 아닌 주문 한 번의 고정 배송비

업무 목적: 구매 포장이 많아져도 고정 주문 운임을 한번만 더한다.

검수 봉투 10장의 두 구매안을 비교합니다. 운임은 구매포장마다가 아니라 주문 한 번에 붙습니다. quote_comparisons와 chosen_quote_id 및 chosen_total을 작성해 실제 주문 전체 비용을 확인해 주세요.

설계 의도: 기존 D158은 실제 부품비 합산이다. 신규는 낱개 포장의 많은 구매 수와 주문당 고정 운임을 분리한다. 수요가 커지면 고정 운임을 분담한 실제 구매비 순위가 달라진다.

집필 원고 ID: `D052`, 전체 문항 SHA-256: `82dbf946508579ab92cb19171fec5b36bded635f54e094a21ed540122c34a5b2`

[문항 메타데이터](../data/batch_2/D_extract/B2_D052_82dbf946/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_051_100.json)

입력 파일:

- [01_봉투주문.pdf](../data/batch_2/D_extract/B2_D052_82dbf946/inputs/01_봉투주문.pdf) (pdf)
- [02_개별견적.xlsx](../data/batch_2/D_extract/B2_D052_82dbf946/inputs/02_개별견적.xlsx) (xlsx)
- [03_열장견적.hwpx](../data/batch_2/D_extract/B2_D052_82dbf946/inputs/03_열장견적.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/D_extract/B2_D052_82dbf946/gold.json)

```json
{
  "chosen_quote_id": "ENV-TEN",
  "chosen_total": 2700,
  "quote_comparisons": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-01-29",
      "eligible": true,
      "leftover_units": 0,
      "merchandise_supply": 1818,
      "merchandise_total": 2000,
      "merchandise_vat": 182,
      "obtained_units": 10,
      "packs": 10,
      "quote_id": "ENV-EACH",
      "shipping_supply": 909,
      "shipping_total": 1000,
      "shipping_vat": 91,
      "stock_sufficient": true,
      "supply": 2727,
      "total": 3000,
      "valid_on_order": true,
      "vat": 273,
      "vendor": "가상봉투개별"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-01-29",
      "eligible": true,
      "leftover_units": 0,
      "merchandise_supply": 2454,
      "merchandise_total": 2700,
      "merchandise_vat": 246,
      "obtained_units": 10,
      "packs": 1,
      "quote_id": "ENV-TEN",
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "stock_sufficient": true,
      "supply": 2454,
      "total": 2700,
      "valid_on_order": true,
      "vat": 246,
      "vendor": "가상봉투열장"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.procurement_comparison | {"base_unit": "장", "comparison": {"chosen_leftover_units": 0, "chosen_quote_id": "ENV-TEN", "chosen_total": 2700, "chosen_vendor": "가상봉투열장", "eligible_quote_count": 2, "quote_comparisons": [{"delivered_in_time": true, "delivery... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D052_82dbf946/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D100_c796b7b7 (D_extract, hard)

집필 제목: 포장 올림 재고와 무료배송 경계의 최종 승인

업무 목적: 포장 올림으로 달라지는 재고 적격과 상품세액의 무료배송 조건을 함께 확인한다.

설치용 씰의 필요량은 마지막 포장을 올려야 합니다. 한 후보는 그 포장 재고가 없고 다른 후보는 세금 포함 상품총액에서 배송이 무료가 됩니다. quote_comparisons와 chosen_quote_id 및 chosen_total을 작성해 주세요.

설계 의도: 기존 D300은 개당가격과 업체 합계다. 신규는 필요한 마지막 구매포장이 후보 재고를 넘는지 확인하고 다른 후보의 별도 상품세액이 운임 제거를 만들어 실구매 선택을 바꾼다.

집필 원고 ID: `D100`, 전체 문항 SHA-256: `c796b7b7227e435c7e222c180b5923edb2422bab58739d0d8d70c301ef3dfa7e`

[문항 메타데이터](../data/batch_2/D_extract/B2_D100_c796b7b7/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_051_100.json)

입력 파일:

- [01_설치요청.pdf](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/01_설치요청.pdf) (pdf)
- [02_저가가격.xlsx](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/02_저가가격.xlsx) (xlsx)
- [03_저가기간.hwpx](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/03_저가기간.hwpx) (hwpx)
- [04_저가재고.pdf](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/04_저가재고.pdf) (pdf)
- [05_세액가격.xlsx](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/05_세액가격.xlsx) (xlsx)
- [06_세액기간.hwpx](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/06_세액기간.hwpx) (hwpx)
- [07_세액재고.pdf](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/07_세액재고.pdf) (pdf)
- [08_정액가격.xlsx](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/08_정액가격.xlsx) (xlsx)
- [09_정액이행.hwpx](../data/batch_2/D_extract/B2_D100_c796b7b7/inputs/09_정액이행.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/D_extract/B2_D100_c796b7b7/gold.json)

```json
{
  "chosen_quote_id": "FINAL-FREE",
  "chosen_total": 3300,
  "quote_comparisons": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-02-02",
      "eligible": true,
      "leftover_units": 1,
      "merchandise_supply": 3181,
      "merchandise_total": 3500,
      "merchandise_vat": 319,
      "obtained_units": 22,
      "packs": 2,
      "quote_id": "FINAL-FLAT",
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "stock_sufficient": true,
      "supply": 3181,
      "total": 3500,
      "valid_on_order": true,
      "vat": 319,
      "vendor": "가상씰정액"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-02-03",
      "eligible": true,
      "leftover_units": 0,
      "merchandise_supply": 3000,
      "merchandise_total": 3300,
      "merchandise_vat": 300,
      "obtained_units": 21,
      "packs": 3,
      "quote_id": "FINAL-FREE",
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "stock_sufficient": true,
      "supply": 3000,
      "total": 3300,
      "valid_on_order": true,
      "vat": 300,
      "vendor": "가상씰세액"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-02-01",
      "eligible": false,
      "leftover_units": 9,
      "merchandise_supply": 1363,
      "merchandise_total": 1500,
      "merchandise_vat": 137,
      "obtained_units": 30,
      "packs": 3,
      "quote_id": "FINAL-STOCK",
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "stock_sufficient": false,
      "supply": 1363,
      "total": 1500,
      "valid_on_order": true,
      "vat": 137,
      "vendor": "가상씰저가"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.procurement_comparison | {"base_unit": "개", "comparison": {"chosen_leftover_units": 0, "chosen_quote_id": "FINAL-FREE", "chosen_total": 3300, "chosen_vendor": "가상씰세액", "eligible_quote_count": 2, "quote_comparisons": [{"delivered_in_time": true, "delive... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D100_c796b7b7/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D105_d9f3f03b (D_extract, easy)

집필 제목: 작은 전용품 때문에 활성화되는 배송 계정의 대포장 선택

업무 목적: 필수품 배송에 동봉하는 큰 포장과 별도 배송하는 작은 포장의 실제 확보 원가를 비교한다.

전용 홀더 주문과 함께 쓰는 패드를 포장별로 비교합니다. 홀더 공급처의 패드는 더 큰 포장이지만 이미 발생하는 배송비를 공유합니다. chosen_offers와 grand_total 및 offer_comparisons를 작성해 주세요.

설계 의도: D051은 한 품목 포장비를 독립 비교하고 D102는 포장수가 같은 공용품 배정이다. 여기서는 포장 올림 잉여와 고정 계정 배송의 결합으로 소포장 선호가 뒤집힌다.

집필 원고 ID: `D105`, 전체 문항 SHA-256: `d9f3f03b13ded727357fa705c37aeee4785db3219e050b1a2e19fc0a05293f70`

[문항 메타데이터](../data/batch_2/D_extract/B2_D105_d9f3f03b/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_101_150.json)

입력 파일:

- [01_홀더패드.pdf](../data/batch_2/D_extract/B2_D105_d9f3f03b/inputs/01_홀더패드.pdf) (pdf)
- [02_홀더제작.xlsx](../data/batch_2/D_extract/B2_D105_d9f3f03b/inputs/02_홀더제작.xlsx) (xlsx)
- [03_소포장.hwpx](../data/batch_2/D_extract/B2_D105_d9f3f03b/inputs/03_소포장.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/D_extract/B2_D105_d9f3f03b/gold.json)

```json
{
  "chosen_offers": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-13",
      "eligible": true,
      "item_id": "HOLDER",
      "leftover_units": 0,
      "merchandise_supply": 10000,
      "merchandise_total": 11000,
      "merchandise_vat": 1000,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "KIT-H",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상홀더제작",
      "vendor_id": "KIT"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-13",
      "eligible": true,
      "item_id": "PAD",
      "leftover_units": 9,
      "merchandise_supply": 6000,
      "merchandise_total": 6600,
      "merchandise_vat": 600,
      "obtained_units": 20,
      "packs": 2,
      "quote_id": "KIT-P",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상홀더제작",
      "vendor_id": "KIT"
    }
  ],
  "grand_total": 20900,
  "offer_comparisons": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-13",
      "eligible": true,
      "item_id": "HOLDER",
      "leftover_units": 0,
      "merchandise_supply": 10000,
      "merchandise_total": 11000,
      "merchandise_vat": 1000,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "KIT-H",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상홀더제작",
      "vendor_id": "KIT"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-13",
      "eligible": true,
      "item_id": "PAD",
      "leftover_units": 9,
      "merchandise_supply": 6000,
      "merchandise_total": 6600,
      "merchandise_vat": 600,
      "obtained_units": 20,
      "packs": 2,
      "quote_id": "KIT-P",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상홀더제작",
      "vendor_id": "KIT"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-13",
      "eligible": true,
      "item_id": "PAD",
      "leftover_units": 1,
      "merchandise_supply": 4000,
      "merchandise_total": 4400,
      "merchandise_vat": 400,
      "obtained_units": 12,
      "packs": 2,
      "quote_id": "SMALL-P",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상패드소포장",
      "vendor_id": "SMALL"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.cart_procurement_comparison | {"comparison": {"chosen_offers": [{"delivered_in_time": true, "delivery_date": "2026-03-13", "eligible": true, "item_id": "HOLDER", "leftover_units": 0, "merchandise_supply": 10000, "merchandise_total": 11000, "merchandise_vat"... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D105_d9f3f03b/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D107_9d40f700 (D_extract, easy)

집필 제목: 전용 주문이 있는 업체의 최소 포장과 동봉 문턱

업무 목적: 공용품 최소 주문의 잉여 비용과 필수 주문의 무료배송 이득을 같은 실제 주문에서 비교한다.

전용 자와 공용 클립을 확보합니다. 자 공급처 클립은 최소 세 포장이며 그 실제 상품액을 자와 함께 무료배송 기준에 넣습니다. chosen_offers와 offer_comparisons 및 grand_total을 작성해 주세요.

설계 의도: D080은 한 품목의 최소 주문과 무료배송이다. 새 문제는 공용품 최소 주문을 다른 필수 품목 배송 계정에 연결하며 대안 업체에 배정하면 필수 주문 운임이 남는다.

집필 원고 ID: `D107`, 전체 문항 SHA-256: `9d40f700852332e8898e80fb577fcb393385dd675a8799b7d982bd313622080d`

[문항 메타데이터](../data/batch_2/D_extract/B2_D107_9d40f700/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_101_150.json)

입력 파일:

- [01_각도자요청.pdf](../data/batch_2/D_extract/B2_D107_9d40f700/inputs/01_각도자요청.pdf) (pdf)
- [02_각도자공방.xlsx](../data/batch_2/D_extract/B2_D107_9d40f700/inputs/02_각도자공방.xlsx) (xlsx)
- [03_클립창고.hwpx](../data/batch_2/D_extract/B2_D107_9d40f700/inputs/03_클립창고.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/D_extract/B2_D107_9d40f700/gold.json)

```json
{
  "chosen_offers": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-18",
      "eligible": true,
      "item_id": "CLIP",
      "leftover_units": 2,
      "merchandise_supply": 6000,
      "merchandise_total": 6600,
      "merchandise_vat": 600,
      "obtained_units": 6,
      "packs": 3,
      "quote_id": "RULER-C",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상각도자공방",
      "vendor_id": "RULER"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-18",
      "eligible": true,
      "item_id": "RULER",
      "leftover_units": 0,
      "merchandise_supply": 14000,
      "merchandise_total": 15400,
      "merchandise_vat": 1400,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "RULER-R",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상각도자공방",
      "vendor_id": "RULER"
    }
  ],
  "grand_total": 22000,
  "offer_comparisons": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-18",
      "eligible": true,
      "item_id": "CLIP",
      "leftover_units": 0,
      "merchandise_supply": 4000,
      "merchandise_total": 4400,
      "merchandise_vat": 400,
      "obtained_units": 4,
      "packs": 1,
      "quote_id": "CLIPS-C",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상클립창고",
      "vendor_id": "CLIPS"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-18",
      "eligible": true,
      "item_id": "CLIP",
      "leftover_units": 2,
      "merchandise_supply": 6000,
      "merchandise_total": 6600,
      "merchandise_vat": 600,
      "obtained_units": 6,
      "packs": 3,
      "quote_id": "RULER-C",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상각도자공방",
      "vendor_id": "RULER"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-18",
      "eligible": true,
      "item_id": "RULER",
      "leftover_units": 0,
      "merchandise_supply": 14000,
      "merchandise_total": 15400,
      "merchandise_vat": 1400,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "RULER-R",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상각도자공방",
      "vendor_id": "RULER"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.cart_procurement_comparison | {"comparison": {"chosen_offers": [{"delivered_in_time": true, "delivery_date": "2026-03-18", "eligible": true, "item_id": "CLIP", "leftover_units": 2, "merchandise_supply": 6000, "merchandise_total": 6600, "merchandise_vat": 60... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D107_9d40f700/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D110_bcbbdc13 (D_extract, easy)

집필 제목: 두 전용품 계정과 공용품 대안의 총액 동률

업무 목적: 이미 쓰는 두 업체 계정 사이의 동률 공용품 배정을 전체 품목 순서에 따라 결정한다.

전용 받침과 전용 고정대를 각각 주문하고 공용 덮개를 한 업체에 배정합니다. 완성 조합이 같은 총액이면 품목ID순 업체 비교 튜플을 사용합니다. chosen_offers와 grand_total을 작성해 주세요.

설계 의도: D076은 단일 견적의 업체 동률이다. 새 문제는 여러 견적의 조합이며 업체 이름 목록을 일괄 정렬하거나 잉여로 고르면 명시한 품목별 비교 튜플과 달라진다.

집필 원고 ID: `D110`, 전체 문항 SHA-256: `bcbbdc131d847069541cb21ee52b59b06b38c98dbb0ed4be551928188fddb7b2`

[문항 메타데이터](../data/batch_2/D_extract/B2_D110_bcbbdc13/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_101_150.json)

입력 파일:

- [01_설치품요청.pdf](../data/batch_2/D_extract/B2_D110_bcbbdc13/inputs/01_설치품요청.pdf) (pdf)
- [02_가람견적.xlsx](../data/batch_2/D_extract/B2_D110_bcbbdc13/inputs/02_가람견적.xlsx) (xlsx)
- [03_나루견적.hwpx](../data/batch_2/D_extract/B2_D110_bcbbdc13/inputs/03_나루견적.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/D_extract/B2_D110_bcbbdc13/gold.json)

```json
{
  "chosen_offers": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-25",
      "eligible": true,
      "item_id": "A-COVER",
      "leftover_units": 1,
      "merchandise_supply": 4000,
      "merchandise_total": 4400,
      "merchandise_vat": 400,
      "obtained_units": 3,
      "packs": 1,
      "quote_id": "FIRST-C",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상가람부품",
      "vendor_id": "FIRST"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-25",
      "eligible": true,
      "item_id": "B-BASE",
      "leftover_units": 0,
      "merchandise_supply": 10000,
      "merchandise_total": 11000,
      "merchandise_vat": 1000,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "FIRST-B",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상가람부품",
      "vendor_id": "FIRST"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-03-25",
      "eligible": true,
      "item_id": "C-FIX",
      "leftover_units": 0,
      "merchandise_supply": 15000,
      "merchandise_total": 16500,
      "merchandise_vat": 1500,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "SECOND-F",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상나루부품",
      "vendor_id": "SECOND"
    }
  ],
  "grand_total": 37400
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.cart_procurement_comparison | {"comparison": {"chosen_offers": [{"delivered_in_time": true, "delivery_date": "2026-03-25", "eligible": true, "item_id": "A-COVER", "leftover_units": 1, "merchandise_supply": 4000, "merchandise_total": 4400, "merchandise_vat":... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D110_bcbbdc13/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D111_e7714277 (D_extract, easy)

집필 제목: 전용품 주문에 두 공용품을 함께 붙여야 넘는 문턱

업무 목적: 두 공용 품목의 공동 배정으로만 생기는 무료배송을 필수 주문과 연결한다.

전용 거치대와 종이띠 및 고리를 주문합니다. 공용품 하나만 동봉하면 운임이 남고 둘을 같이 붙여야 전용품 공급처의 무료배송 조건을 채웁니다. chosen_offers와 vendor_cart_totals 및 grand_total을 작성해 주세요.

설계 의도: D106에서는 공용품 하나로 문턱을 충족한다. 여기서는 둘 중 하나만 움직이는 구매처 비교가 이득을 보이지 않아 두 공용품의 공동 배정 조합을 계산해야 한다.

집필 원고 ID: `D111`, 전체 문항 SHA-256: `e7714277f44420865ace4b3f3dc53c38dea328ae3d9b0089d007a78a8ecbc86a`

[문항 메타데이터](../data/batch_2/D_extract/B2_D111_e7714277/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_101_150.json)

입력 파일:

- [01_보관품요청.pdf](../data/batch_2/D_extract/B2_D111_e7714277/inputs/01_보관품요청.pdf) (pdf)
- [02_거치대공방.xlsx](../data/batch_2/D_extract/B2_D111_e7714277/inputs/02_거치대공방.xlsx) (xlsx)
- [03_소모품점.hwpx](../data/batch_2/D_extract/B2_D111_e7714277/inputs/03_소모품점.hwpx) (hwpx)

정답: [gold.json](../data/batch_2/D_extract/B2_D111_e7714277/gold.json)

```json
{
  "chosen_offers": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-04-04",
      "eligible": true,
      "item_id": "BAND",
      "leftover_units": 0,
      "merchandise_supply": 5000,
      "merchandise_total": 5500,
      "merchandise_vat": 500,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "STAND-B",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상거치대공방",
      "vendor_id": "STAND"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-04-04",
      "eligible": true,
      "item_id": "HOOK",
      "leftover_units": 0,
      "merchandise_supply": 5000,
      "merchandise_total": 5500,
      "merchandise_vat": 500,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "STAND-H",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상거치대공방",
      "vendor_id": "STAND"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-04-04",
      "eligible": true,
      "item_id": "STAND",
      "leftover_units": 0,
      "merchandise_supply": 20000,
      "merchandise_total": 22000,
      "merchandise_vat": 2000,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "STAND-S",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상거치대공방",
      "vendor_id": "STAND"
    }
  ],
  "grand_total": 33000,
  "vendor_cart_totals": [
    {
      "merchandise_supply": 30000,
      "merchandise_total": 33000,
      "merchandise_vat": 3000,
      "shipping_free": true,
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "supply": 30000,
      "total": 33000,
      "vat": 3000,
      "vendor": "가상거치대공방",
      "vendor_id": "STAND"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.cart_procurement_comparison | {"comparison": {"chosen_offers": [{"delivered_in_time": true, "delivery_date": "2026-04-04", "eligible": true, "item_id": "BAND", "leftover_units": 0, "merchandise_supply": 5000, "merchandise_total": 5500, "merchandise_vat": 50... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D111_e7714277/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D129_d966a200 (D_extract, medium)

집필 제목: 공급처 이름 동률과 품목ID 순서가 만나는 포장 선택

업무 목적: 정규화 이름 동률인 계정의 전체 조합을 품목별 공급사ID와 견적ID 순으로 결정한다.

출력판과 지지링을 같은 이름의 두 독립 계정 중에서 주문합니다. 공동 총액이 동률이면 품목ID순 비교에서 먼저 다른 공급사ID를 비교합니다. chosen_offers와 vendor_cart_totals를 작성해 주세요.

설계 의도: D077은 단품 견적ID 동률이고 D110은 이름이 다른 필수 계정이다. 여기서는 이름이 같아 공급사ID가 실제 공동 주문 동률을 정하며 낮은 견적ID만 먼저 고르면 잘못된 계정을 선택한다.

집필 원고 ID: `D129`, 전체 문항 SHA-256: `d966a200260e6f590d8c59f68afa81d9ddf5ab6248a599c2be759803310c1505`

[문항 메타데이터](../data/batch_2/D_extract/B2_D129_d966a200/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_101_150.json)

입력 파일:

- [01_출력품요청.pdf](../data/batch_2/D_extract/B2_D129_d966a200/inputs/01_출력품요청.pdf) (pdf)
- [02_계정가.xlsx](../data/batch_2/D_extract/B2_D129_d966a200/inputs/02_계정가.xlsx) (xlsx)
- [03_계정나.hwpx](../data/batch_2/D_extract/B2_D129_d966a200/inputs/03_계정나.hwpx) (hwpx)
- [04_출력품물량.pdf](../data/batch_2/D_extract/B2_D129_d966a200/inputs/04_출력품물량.pdf) (pdf)

정답: [gold.json](../data/batch_2/D_extract/B2_D129_d966a200/gold.json)

```json
{
  "chosen_offers": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-17",
      "eligible": true,
      "item_id": "A-PLATE",
      "leftover_units": 0,
      "merchandise_supply": 10000,
      "merchandise_total": 11000,
      "merchandise_vat": 1000,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "Z-PLATE",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상출력부품",
      "vendor_id": "ACCOUNT-A"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-17",
      "eligible": true,
      "item_id": "B-RING",
      "leftover_units": 0,
      "merchandise_supply": 5000,
      "merchandise_total": 5500,
      "merchandise_vat": 500,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "Z-RING",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상출력부품",
      "vendor_id": "ACCOUNT-A"
    }
  ],
  "vendor_cart_totals": [
    {
      "merchandise_supply": 15000,
      "merchandise_total": 16500,
      "merchandise_vat": 1500,
      "shipping_free": false,
      "shipping_supply": 2000,
      "shipping_total": 2200,
      "shipping_vat": 200,
      "supply": 17000,
      "total": 18700,
      "vat": 1700,
      "vendor": "가상출력부품",
      "vendor_id": "ACCOUNT-A"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.cart_procurement_comparison | {"comparison": {"chosen_offers": [{"delivered_in_time": true, "delivery_date": "2026-05-17", "eligible": true, "item_id": "A-PLATE", "leftover_units": 0, "merchandise_supply": 10000, "merchandise_total": 11000, "merchandise_vat... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D129_d966a200/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D131_f43b6ea0 (D_extract, medium)

집필 제목: 필수 부품은 사고 남은 공용품의 최소 주문 재고는 실패하는 승인

업무 목적: 최소포장 재고 실패 후 필수 주문에 호스가 동봉되지 않는 실제 배송 부담을 반영한다.

전용 탱크와 공용 호스를 함께 확보합니다. 탱크 업체의 호스는 필요량보다 많은 최소포장이 적용되어 재고에 실패합니다. chosen_offers와 offer_comparisons 및 vendor_cart_totals를 작성해 주세요.

설계 의도: D067은 단품 최소재고 실패다. 여기서는 호스의 최소 주문 탈락이 탱크 업체의 공동 배송 면제를 없애 필수품 운임과 외부 호스 주문이 함께 남는다.

집필 원고 ID: `D131`, 전체 문항 SHA-256: `f43b6ea08cc7ffd876dbc27709d5c1be8f0bec46e9b06253defc3b6c40c9d36f`

[문항 메타데이터](../data/batch_2/D_extract/B2_D131_f43b6ea0/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_101_150.json)

입력 파일:

- [01_탱크약정.pdf](../data/batch_2/D_extract/B2_D131_f43b6ea0/inputs/01_탱크약정.pdf) (pdf)
- [02_필요길이.xlsx](../data/batch_2/D_extract/B2_D131_f43b6ea0/inputs/02_필요길이.xlsx) (xlsx)
- [03_탱크제작.hwpx](../data/batch_2/D_extract/B2_D131_f43b6ea0/inputs/03_탱크제작.hwpx) (hwpx)
- [04_호스점.pdf](../data/batch_2/D_extract/B2_D131_f43b6ea0/inputs/04_호스점.pdf) (pdf)

정답: [gold.json](../data/batch_2/D_extract/B2_D131_f43b6ea0/gold.json)

```json
{
  "chosen_offers": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-22",
      "eligible": true,
      "item_id": "HOSE",
      "leftover_units": 0,
      "merchandise_supply": 4000,
      "merchandise_total": 4400,
      "merchandise_vat": 400,
      "obtained_units": 3,
      "packs": 1,
      "quote_id": "HO-H",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상호스점",
      "vendor_id": "HOSE"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-22",
      "eligible": true,
      "item_id": "TANK",
      "leftover_units": 0,
      "merchandise_supply": 25000,
      "merchandise_total": 27500,
      "merchandise_vat": 2500,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "TA-T",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상탱크제작",
      "vendor_id": "TANK"
    }
  ],
  "offer_comparisons": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-22",
      "eligible": true,
      "item_id": "HOSE",
      "leftover_units": 0,
      "merchandise_supply": 4000,
      "merchandise_total": 4400,
      "merchandise_vat": 400,
      "obtained_units": 3,
      "packs": 1,
      "quote_id": "HO-H",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상호스점",
      "vendor_id": "HOSE"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-22",
      "eligible": false,
      "item_id": "HOSE",
      "leftover_units": 6,
      "merchandise_supply": 6000,
      "merchandise_total": 6600,
      "merchandise_vat": 600,
      "obtained_units": 9,
      "packs": 3,
      "quote_id": "TA-H",
      "stock_sufficient": false,
      "valid_on_order": true,
      "vendor": "가상탱크제작",
      "vendor_id": "TANK"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-22",
      "eligible": true,
      "item_id": "TANK",
      "leftover_units": 0,
      "merchandise_supply": 25000,
      "merchandise_total": 27500,
      "merchandise_vat": 2500,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "TA-T",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상탱크제작",
      "vendor_id": "TANK"
    }
  ],
  "vendor_cart_totals": [
    {
      "merchandise_supply": 4000,
      "merchandise_total": 4400,
      "merchandise_vat": 400,
      "shipping_free": false,
      "shipping_supply": 2000,
      "shipping_total": 2200,
      "shipping_vat": 200,
      "supply": 6000,
      "total": 6600,
      "vat": 600,
      "vendor": "가상호스점",
      "vendor_id": "HOSE"
    },
    {
      "merchandise_supply": 25000,
      "merchandise_total": 27500,
      "merchandise_vat": 2500,
      "shipping_free": false,
      "shipping_supply": 5000,
      "shipping_total": 5500,
      "shipping_vat": 500,
      "supply": 30000,
      "total": 33000,
      "vat": 3000,
      "vendor": "가상탱크제작",
      "vendor_id": "TANK"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.cart_procurement_comparison | {"comparison": {"chosen_offers": [{"delivered_in_time": true, "delivery_date": "2026-05-22", "eligible": true, "item_id": "HOSE", "leftover_units": 0, "merchandise_supply": 4000, "merchandise_total": 4400, "merchandise_vat": 40... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D131_f43b6ea0/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D132_b7251041 (D_extract, medium)

집필 제목: 무상 소모품의 기준0 계정과 유상 필수품의 배송

업무 목적: 무상 상품을 외부 계정에서 받아도 기준0 배송은 면제되며 필수품 계정은 독립적으로 계산한다.

전용 판과 무상 시험쿠폰을 받습니다. 쿠폰 외부 공급처는 무료배송 기준이 실제0이며 판 업체는 기준이 없습니다. chosen_offers와 vendor_cart_totals 및 grand_total을 작성해 주세요.

설계 의도: D079는 단품 기준0과 없음이다. 새 문제는 필수품 배송 계정이 항상 남고 무상품 귀속을 어느 계정에 두느냐에 따라 독립 배송 자격과 동률 선택이 달라진다.

집필 원고 ID: `D132`, 전체 문항 SHA-256: `b7251041b3916757897e87d90097729dcaa5fa45c51d1c1c83527874c9b8266b`

[문항 메타데이터](../data/batch_2/D_extract/B2_D132_b7251041/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_101_150.json)

입력 파일:

- [01_시험판약정.pdf](../data/batch_2/D_extract/B2_D132_b7251041/inputs/01_시험판약정.pdf) (pdf)
- [02_시험품요청.xlsx](../data/batch_2/D_extract/B2_D132_b7251041/inputs/02_시험품요청.xlsx) (xlsx)
- [03_시험판점.hwpx](../data/batch_2/D_extract/B2_D132_b7251041/inputs/03_시험판점.hwpx) (hwpx)
- [04_쿠폰점.pdf](../data/batch_2/D_extract/B2_D132_b7251041/inputs/04_쿠폰점.pdf) (pdf)

정답: [gold.json](../data/batch_2/D_extract/B2_D132_b7251041/gold.json)

```json
{
  "chosen_offers": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-24",
      "eligible": true,
      "item_id": "COUPON",
      "leftover_units": 0,
      "merchandise_supply": 0,
      "merchandise_total": 0,
      "merchandise_vat": 0,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "CO-C",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상가람쿠폰",
      "vendor_id": "COUPON"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-05-24",
      "eligible": true,
      "item_id": "PLATE",
      "leftover_units": 0,
      "merchandise_supply": 20000,
      "merchandise_total": 22000,
      "merchandise_vat": 2000,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "PL-P",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상나루시험판",
      "vendor_id": "PLATE"
    }
  ],
  "grand_total": 25300,
  "vendor_cart_totals": [
    {
      "merchandise_supply": 0,
      "merchandise_total": 0,
      "merchandise_vat": 0,
      "shipping_free": true,
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "supply": 0,
      "total": 0,
      "vat": 0,
      "vendor": "가상가람쿠폰",
      "vendor_id": "COUPON"
    },
    {
      "merchandise_supply": 20000,
      "merchandise_total": 22000,
      "merchandise_vat": 2000,
      "shipping_free": false,
      "shipping_supply": 3000,
      "shipping_total": 3300,
      "shipping_vat": 300,
      "supply": 23000,
      "total": 25300,
      "vat": 2300,
      "vendor": "가상나루시험판",
      "vendor_id": "PLATE"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.cart_procurement_comparison | {"comparison": {"chosen_offers": [{"delivered_in_time": true, "delivery_date": "2026-05-24", "eligible": true, "item_id": "COUPON", "leftover_units": 0, "merchandise_supply": 0, "merchandise_total": 0, "merchandise_vat": 0, "ob... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D132_b7251041/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

## B2_D137_cabe8841 (D_extract, medium)

집필 제목: 동률인 통합 주문보다 세 계정이 먼저 선택되는 배정

업무 목적: 전체 공급이 가능한 통합 계정과 품목별 전문점 연결을 총액 동률 규칙으로 비교하여 실제 세 계정 배정과 유효 조합 수를 확정한다.

세 부속품은 통합센터에서 모두 받을 수도 있고 전문점별로 받을 수도 있습니다. 모든 유효 조합의 비용이 같아도 계정 수가 적다는 이유로 통합 주문을 먼저 고르면 안 됩니다. 아직 시작하지 않은 필터 전문점 견적을 제외하고 chosen_offers와 vendor_cart_totals 및 feasible_cart_count를 작성해 주세요.

설계 의도: D110은 서로 다른 필수 계정이 이미 고정된 공용품 동률이다. D129는 전체품목을 모두 취급하는 두 계정 중 하나로 모으는 선택이다. 이번에는 통합센터가 모든 품목을 공급할 수 있지만 품목별 앞선 전문점들이 서로 달라 전체 업체 수 최소화와 품목별 정렬이 다른 배정을 낸다. 미래 효력의 첫 전문점 연결은 실제 첫 품목의 귀속을 바꾼다.

집필 원고 ID: `D137`, 전체 문항 SHA-256: `cabe884199657b98405920fc751b2004ca8dc8850d6ee5d01c4ec6b3398b270e`

[문항 메타데이터](../data/batch_2/D_extract/B2_D137_cabe8841/task.yaml)와 [집필 원고](../authored/batch_2/D_extract/cases_101_150.json)

입력 파일:

- [01_세품목요청.pdf](../data/batch_2/D_extract/B2_D137_cabe8841/inputs/01_세품목요청.pdf) (pdf)
- [02_필터전문점.xlsx](../data/batch_2/D_extract/B2_D137_cabe8841/inputs/02_필터전문점.xlsx) (xlsx)
- [03_두전문점.hwpx](../data/batch_2/D_extract/B2_D137_cabe8841/inputs/03_두전문점.hwpx) (hwpx)
- [04_통합센터.pdf](../data/batch_2/D_extract/B2_D137_cabe8841/inputs/04_통합센터.pdf) (pdf)

정답: [gold.json](../data/batch_2/D_extract/B2_D137_cabe8841/gold.json)

```json
{
  "chosen_offers": [
    {
      "delivered_in_time": true,
      "delivery_date": "2026-06-10",
      "eligible": true,
      "item_id": "A-FILTER",
      "leftover_units": 0,
      "merchandise_supply": 2000,
      "merchandise_total": 2200,
      "merchandise_vat": 200,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "CENTER-A",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상하늘통합센터",
      "vendor_id": "CENTER"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-06-10",
      "eligible": true,
      "item_id": "B-HOLDER",
      "leftover_units": 0,
      "merchandise_supply": 2000,
      "merchandise_total": 2200,
      "merchandise_vat": 200,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "HOLDER-B",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상나루홀더",
      "vendor_id": "HOLDER"
    },
    {
      "delivered_in_time": true,
      "delivery_date": "2026-06-10",
      "eligible": true,
      "item_id": "C-CLIP",
      "leftover_units": 0,
      "merchandise_supply": 2000,
      "merchandise_total": 2200,
      "merchandise_vat": 200,
      "obtained_units": 1,
      "packs": 1,
      "quote_id": "CLIP-C",
      "stock_sufficient": true,
      "valid_on_order": true,
      "vendor": "가상다솔집게",
      "vendor_id": "CLIP"
    }
  ],
  "feasible_cart_count": 4,
  "vendor_cart_totals": [
    {
      "merchandise_supply": 2000,
      "merchandise_total": 2200,
      "merchandise_vat": 200,
      "shipping_free": false,
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "supply": 2000,
      "total": 2200,
      "vat": 200,
      "vendor": "가상하늘통합센터",
      "vendor_id": "CENTER"
    },
    {
      "merchandise_supply": 2000,
      "merchandise_total": 2200,
      "merchandise_vat": 200,
      "shipping_free": false,
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "supply": 2000,
      "total": 2200,
      "vat": 200,
      "vendor": "가상다솔집게",
      "vendor_id": "CLIP"
    },
    {
      "merchandise_supply": 2000,
      "merchandise_total": 2200,
      "merchandise_vat": 200,
      "shipping_free": false,
      "shipping_supply": 0,
      "shipping_total": 0,
      "shipping_vat": 0,
      "supply": 2000,
      "total": 2200,
      "vat": 200,
      "vendor": "가상나루홀더",
      "vendor_id": "HOLDER"
    }
  ]
}
```

계산 trace 요약:

| 규칙 | 결과 |
|---|---|
| D.cart_procurement_comparison | {"comparison": {"chosen_offers": [{"delivered_in_time": true, "delivery_date": "2026-06-10", "eligible": true, "item_id": "A-FILTER", "leftover_units": 0, "merchandise_supply": 2000, "merchandise_total": 2200, "merchandise_vat"... |

전체 계산 입력과 중간값: [trace.json](../data/batch_2/D_extract/B2_D137_cabe8841/trace.json)

검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.

<!-- authored-task-set-sha256: d26a2dbb25d89364b8efadee3dc7b85e81c2c97a0c8f7800e509056269fb6291 -->
