# 완전 월 급여 명세의 승인 개정 원천 계약

`rules/b_payroll/statement_revisions.py`는 선택 계약
`payroll_statement_revision_v1`을 제공한다. 가상 사업장이 공개한 문서 효력
정책에 따라 한 직원의 한 기관 부과월에서 승인된 최고 개정번호의 완전한 월
명세 하나를 고른다. 이 규칙은 사적 원본 선택 정책이며 정부가 확인한 세법이
아니다. source catalog 통합 시 `B_PAYROLL_STATEMENT_REVISION`은
`verified: false`로 기록한다.

기존 evidence와 급여 엔진 및 은행 대조 엔진은 수정하지 않았다. 원본을 선택한
뒤 기존 `payroll_bank_reconciliation_v1`으로 전체 급여 계산과 현금 대조를
수행한다. 원천징수나 월 보험을 개정본 사이에 나누지 않는다.

## 입력

최상위 정확한 필드는 `source_contract`, `processing_policy`, `processing_date`,
`as_of_date`, `statement_records`, `transfers`다. 날짜는 엄격한 `YYYY-MM-DD`이며
정책은 비어 있지 않은 문자열이다. `processing_date`는 발행 확인 기준일이고
`as_of_date`는 현금 누계 기준일이다. 현재 확인한 정정 명세와 과거 은행 상태를
대조할 수 있으므로 두 날짜에 별도의 대소관계를 강제하지 않는다.

원본 행의 정확한 필드는 `document_id`, `payroll_id`, `employee_id`,
`statement_scope`, `revision`, `status`, `issued_on`, `facts`다. ID는 비어 있지
않은 문자열이며 범위는 `complete_monthly`다. 개정번호는 bool을 제외한 양의
정수이고 상태는 `approved`, `draft`, `superseded` 중 하나다. 미래 발행 원본은
거절한다. 원본 행은 최대 128건이며 사본 제거 후 최대 64건이다. 직원과 기관
부과월 그룹은 최대 16개다. 이 유한 상한은 본 선택 계약의 입력 경계다.

그룹은 `employee_id` 및 `facts.insurance_assessment_month`로 구분한다.
한 그룹의 급여번호는 개정 전후 같아야 한다. 급여번호 하나를 서로 다른 직원
또는 부과월에 다시 사용하면 초안이어도 거절한다. 서로 다른 문서번호가 같은
그룹의 같은 개정번호를 주장하면 상태나 내용이 같아도 거절한다. 번호가 커질
때 발행일은 같거나 더 늦어야 한다. 같은 날 여러 개정은 허용한다. 새 부과월
발행 기한이나 법정 정정 규칙은 만들지 않았다.

같은 문서번호의 중첩 primitive 타입과 값까지 같은 사본만 중복 접수로 인정한다.
동일한 값처럼 보이는 정수와 float도 사본으로 혼동하지 않는다. 내용이 다르면
선택에서 버릴 초안이나 폐기본이어도 거절한다.

## 원본 전체 검증

`facts`는 `payroll_evidence_v1`만 허용하며 bank 및 revision을 중첩하지 않는다.
기본 필수 필드는 다음과 같다.

```
source_contract company_name employee_name pay_basis base_salary fixed_allowance
meal_allowance variable_allowance monthly_divisor_hours hourly_rate weekly_hours
weekly_holiday_included workplace_employee_count work_records holiday_dates
week_attendance payment_records meal_service pension_notified_income
health_notified_income employment_notified_income pension_due health_due
employment_due insurance_assessment_month family_count eligible_children
withholding_percent scope
```

선택 필드는 `employee_age`, `regular_schedule`, `paid_holiday_records`뿐이다.
회사와 직원 이름 및 scope는 비어 있지 않은 문자열이다. 금액과 인원과 시간
정수 필드는 bool 또는 float를 허용하지 않는다. 시급만 유한한 비음수 int 또는
float를 허용한다. 월 나눗시간과 가족 수는 양수다. 주 소정시간은 0부터 40이며
자녀 수는 가족 수보다 작다. 부과월은 2026년의 엄격한 `YYYY-MM`이다.
원천징수 선택은 정수 80, 100, 120이다. due와 주휴 포함 여부는 strict bool이다.

근무와 휴게, 소정 일정과 무급 부재, 주별 출근, 지급 기록과 유급 휴일 행은
기존 정의의 정확한 필드와 타입을 확인한다. 시각은 엄격한
`YYYY-MM-DD HH:MM`이다. draft나 superseded 근무행도 양의 24시간 이내 구간 및
구간 안의 겹치지 않는 휴게를 검증한다. 원본 선택에서 버릴 명세도 전체
`evidence.interpret` 및 기존 `engine.calculate`를 통과해야 한다. 기존 해석기의
승인 근무 개정 선택과 실제 구간 중복 방지 및 가족, 보험, 급여 유형과 음수
실수령 guard를 보존한다. 파생 계산값이나 알 수 없는 추가 필드는 거절한다.

초안 전용 그룹은 유효한 형식으로 확인하되 현재 명세를 만들지 않는다. 전체에
승인 원본이 하나도 없으면 거절한다. 초안 전용 급여번호에 계획 은행행을 붙여도
최종 은행 계약의 참조 검증에서 거절한다.

## 은행 대조와 출력

이체 행은 기존 은행 계약의 정확한 필드 및 정책을 따른다. 원본 행은 최대
200건이며 유일 이체번호는 최대 100개다. 계획 이체와 현금 기준일 뒤의 행도
직원 및 급여번호와 타입을 확인한다. 실행 이체일은 최종 승인 명세의
`effective_payment_date`와 정확히 같아야 한다. 이전 명세의 잘못된 지급일을
강제하지 않지만 최종 명세의 지급일이 바뀌면 실제 은행도 그 지급일을 확인해야
한다. 이틀에 나눈 지급이나 체불 정산을 허용하는 새 규칙은 추가하지 않았다.

정답은 기존 은행 계약의 7개 필드 그대로다.

```
payroll_calculations employee_settlements gross_total deductions_total
net_total paid_total balance_total
```

선택 trace의 rule ID는 `B_PAYROLL_STATEMENT_REVISION`이다. 입력 원본은
사본 제거 후 문서번호 순서로 기록하며 그룹 및 ID 목록도 정렬한다. 선택한 문서와
제외한 문서, 원본 사본 ID, 그룹의 안정적 급여번호와 선택 개정번호 및 은행에
전달한 완전 명세를 기록한다. 뒤에는 기존 bank trace를 그대로 반환한다.
입력 행 순서를 바꾸어도 answer와 trace는 같다. 동일 사본을 추가해도 정답은
같으며 사본 접수 여부는 trace에 남는다. caller와 answer 및 trace는 mutable
container를 공유하지 않는다. 원본 근무 배열 등 child 의미 순서는 보존한다.

## 독립 전체 검산

동결된 literal 두 예시는 `tests/fixtures/payroll_statement_revisions.json`에
그대로 보존했다. 테스트 예시이며 데이터셋 승인 문항으로 세지 않는다.

첫 예시의 승인 개정2는 실제 20시간과 시급 12,500원으로 기본 250,000원이며
주휴는 `20 / 5 × 12,500 = 50,000`원이다. 총지급 300,000원에서 고용보험
2,700원만 빼면 실수령 297,300원이다. 실제 이체 290,000원과 잔액은 7,300원이다.
개정1의 60분 오류가 남으면 총지급 287,500원과 실수령 284,800원이 된다.
개정2만 선택하므로 같은 월 고용보험을 두 번 부과하지 않는다.

둘째 예시의 승인 개정2는 통상시급 `(2,508,000 + 104,500) / 209 = 12,500`원이다.
추가 2시간은 37,500원이며 실제 야간 1시간은 6,250원이다. 총지급은
2,656,250원이다. 연금 118,750원과 건강 89,870원 및 요양 11,800원에 고용
22,500원을 더하면 보험 합계 242,920원이다. 저장된 공식 표의 2,650,000원부터
2,660,000원 미만 가족1열 소득세는 43,970원이고 지방세는 4,390원이다.
총공제는 291,280원이며 실수령은 2,364,970원이다. 실제 이체 2,400,000원과
대조한 잔액은 -35,030원이다. 개정3 초안의 기본급을 섞지 않는다. 개정1은
실수령 2,260,420원으로 독립 수기도 확인했다.

두 전체 정답은 독립 Fraction 및 공식 표 행 확인 후 모든 answer 필드의 JSON
순서와 값까지 대조했다. 기존 bank를 직접 호출한 trace와 새 trace의 후반부도
같았다. 가족과 자녀를 현재 승인 명세에서 고르는 검사 및 원천징수 80과 120의
10원 절사 및 기관 보험 due 사실 선택도 확인했다.

## 검증 및 통합 책임

- 새 계약의 93개 검사가 통과했다.
- 기존 급여와 raw evidence 및 bank 검사와 합해 221개 검사가 통과했다.
- 실제 Batch1 B300을 문서에서 모두 복원했다. 저장된 gold와 전체 trace가 같았다.
- B300의 직접 evidence 및 engine 계산과 공개 registry 계산도 모두 같았다.
- Ruff 검사 및 포맷 검사가 통과했다.
- 모델 API 호출이나 데이터셋 문항 생성은 없었다.

증거는 `tmp/payroll_statement_revision_contract/`의
`manual_confirmation.json`, `legacy_B300.json`, `test_results.txt` 및 `handoff.json`에
보관했다. registry 라우팅과 실제 PDF 및 XLSX 및 HWPX 통합은 root가 소유한다.
문서 label 및 export와 source catalog 통합도 root가 완료한다. 전문가 법률 검수는
이 구현으로 완료됐다고 표시하지 않는다.
