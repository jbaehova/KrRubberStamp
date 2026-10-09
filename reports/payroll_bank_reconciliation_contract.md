# 급여명세와 은행 이체의 합성 내부 대조 계약

`rules/b_payroll/bank_reconciliation.py`는 선택 계약
`payroll_bank_reconciliation_v1`과 `calculate(source) -> (answer, trace)`를 제공한다.
이 계약은 완전한 월 급여명세를 은행 이체 원장에 연결하는 현금 대조다.
기존 급여 엔진의 통상임금이나 보험료를 변경하지 않는다. 원천징수 세액과
보험 부과월은 기존 급여 계약이 계산한 그대로 사용한다.

`B_PAYROLL_BANK_RECONCILIATION`의 source fragment는 `verified: false`다.
문항에 명시하는 가상 회사 내부 규약으로서 정부가 확인한 대조 규칙이 아니다.
새 법정 공제나 교정 법규를 추가하지 않았다.

## 입력과 범위

최상위 필드는 정확히 `source_contract`, `processing_policy`, `as_of_date`,
`payrolls`, `transfers`다. 정책은 비어 있지 않은 문자열이고 날짜는 엄격한
`YYYY-MM-DD`다. 명세 목록은 한 건 이상 필요하며 이체 목록은 비어 있어도 된다.

각 명세의 필드는 정확히 `payroll_id`, `employee_id`, `facts`다.
ID는 비어 있지 않은 문자열이고 급여 ID는 전역에서 유일하다. `facts`는 기존
plain 급여 계약 또는 `payroll_evidence_v1`의 완전한 literal 객체다. 새로운
은행 계약을 중첩하거나 알 수 없는 source contract를 사용하는 것은 거절한다.
raw 근태 계약은 기존 `interpret`, `derivation_trace`, `engine.calculate`를
차례로 호출한다. 기존 child의 의미가 있는 배열 순서와 trace 순서를 유지한다.

각 명세는 해당 직원의 보험 부과월 전체 월급을 나타낸다. 같은
`(employee_id, insurance_assessment_month)`의 두 명세를 거절한다. 이것은 한 월급을
인위적으로 나누어 원천징수하는 결과를 막는 입력 경계다. 서로 다른 보험 부과월의
같은 직원은 별도 완전한 명세로 표현할 수 있다.

각 이체의 필드는 정확히 `transfer_id`, `payroll_id`, `employee_id`, `date`,
`status`, `amount`다. 금액은 Boolean과 float를 허용하지 않는 0 이상 정수다.
상태는 `executed` 또는 `planned`다. 계획 이체와 미래 행도 급여 ID와 직원 ID가
정확히 일치해야 한다. 이름이나 동일 금액으로 신원을 추정하지 않는다.

실행 이체일은 기존 child가 계산한 `effective_payment_date`와 같아야 한다.
기준일 뒤에 있는 실행 행도 다른 지급일이면 거절한다. 지연 지급이나 서로 다른
지급일의 분할 지급에 대한 세금 판정은 이 계약의 범위 밖이다. 동일 지급일의
부분 지급 또는 초과 지급은 현금 대조로만 계산하며 추가 원천징수를 만들지 않는다.

같은 이체 ID의 값과 타입이 모두 같은 행은 한 번 계산한다. 충돌은 거절한다.
다른 이체 ID의 동일 금액은 별개 이체로 합산한다. 실행 상태이며 기준일 이내인
행만 지급 누계에 포함한다. 계획 또는 기준일 이후 행은 제외한다.

## 출력과 trace

`payroll_calculations`는 급여 ID 순서의 객체 배열이다. 각 객체는 `payroll_id`,
`employee_id`, `calculation`을 담고 `calculation`은 기존 엔진의 전체 answer다.

`employee_settlements`는 직원 ID와 급여 ID 순서다. 각 객체는 `payroll_id`,
`employee_id`, `effective_payment_date`, `insurance_assessment_month`, `gross_pay`,
`total_deductions`, `net_pay`, `paid`, `balance`를 담는다.
`balance = net_pay - paid`이며 초과 지급 잔액은 음수다.

최상위 합계는 정수 `gross_total`, `deductions_total`, `net_total`, `paid_total`,
`balance_total`이다. 모든 완전한 명세를 합산하며 기준일은 지급 누계 필터에 적용한다.

trace는 rule ID 하나를 가진 배열이다. `inputs`에 전체 source를 깊게 복사하고
부모의 명세와 이체 배열만 ID 순서로 정렬한다. `output`에 급여 ID가 붙은 기존
child trace를 저장하고 승인된 이체 ID, 제외된 이체 ID, 중복 제거 ID를 담는다.
급여별 현금 합계와 최종 settlement도 담는다. 부모 파일의 행 순서를 바꿔도
answer와 trace가 동일하다. caller source, answer, trace는 가변 컨테이너를 공유하지
않으므로 하나를 수정해도 다른 결과가 바뀌지 않는다.

## 독립 손계산 예제

2026년 2월 25일 두 직원의 완전한 월급을 대조했다. 직원 A의 월급과 각 보험
통지 기준은 500,000원이다. 국민연금은 23,750원이다. 건강보험은 17,970원이며
장기요양은 `floor10(17,970 × 9,448 / 71,900) = 2,360`원이다. 고용보험은
4,500원이고 표상 소득세와 지방소득세는 0원이다. 공제 합계는 48,580원이며
실수령액은 451,420원이다.

직원 B의 월급은 3,500,000원이고 세 보험의 통지 기준은 2,000,000원이다.
국민연금은 95,000원이다. 건강보험은 71,900원이며 장기요양은 9,440원이다.
고용보험은 18,000원이다. 기존 공식 수치 회귀의 2월 가족 4명과 자녀 2명에
대한 소득세 20,180원을 재사용하고 지방소득세는 2,010원이다. 공제 합계는
216,530원이며 실수령액은 3,283,470원이다. 신규 계산법을 추가한 예시가 아니다.

두 직원의 총지급액은 4,000,000원이다. 공제 합계 265,110원을 빼면 실수령액
총합은 3,734,890원이다. 같은 지급일의 두 이체가 각 실수령액과 같을 때 지급
누계는 3,734,890원이고 잔액은 0원이다. 직원 A에게 100,000원만 이체하면 잔액은
351,420원이고 500,000원을 이체하면 잔액은 -48,580원이다.

## 검증

- 새 계약의 31개 검사가 통과했다. 독립 손계산과 동일 금액의 서로 다른 이체를 검사했다.
- 실제 지급일 불일치와 직원 또는 급여 ID 불일치는 기준일 및 계획 상태와 무관하게 거절했다.
- 같은 직원의 같은 보험 부과월 중복을 거절하고 다른 월의 명세는 각각 대조했다.
- 입력 순서 불변성과 child trace의 기존 JSON 순서를 확인했다.
- caller source와 반환 answer 및 trace의 상호 mutation 격리를 확인했다.
- 기존 급여 및 raw 근태 검사와 합해 `125 passed`였다. Ruff도 통과했다.
- Batch1의 B300 전체를 현재 registry로 재계산했다. 저장된 gold와 trace가 모두 동일했다.
- 모델 API 호출이나 benchmark 문항 생성은 없었다.

로컬 B300 검사 증거는 `tmp/payroll_bank_reconciliation/legacy_b300_integrity.json`에
보관했다. SHA-256은
`8761cc3aa050466878bf16b8726f57bb01f6af4d7f0caab30c35a8327c3bf918`이다.
이 구현은 registry 라우팅과 문서 label 및 최상위 source 집계 통합을 소유하지 않는다.
root가 이 통합을 완료한 뒤 개별 집필 문항에서 선택 계약을 사용할 수 있다.
