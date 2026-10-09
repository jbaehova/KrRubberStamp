# 2025 원천증명서 대조 계약

`yearend_pay_statement_v1`은 제출된 지급기간 원천증명서의 급여와 원천징수 금액을 합산하고 기존 2025 연말정산 계산 엔진으로 전달한다. 수정본을 선택하는 방법은 문항에 적는 합성 내부 확인 규약이다. 정부의 증명서 우선순위 규정이라고 주장하지 않으며 새 세율이나 공제를 추가하지 않는다.

구현은 [pay_statements.py](../rules/a_yearend/pay_statements.py), 독립 계산과 경계 검증은 [test_yearend_pay_statements.py](../tests/test_yearend_pay_statements.py)에 있다. 출처 항목 `A_PAY_STATEMENT_RECONCILIATION`은 [영역 출처](../rules/a_yearend/sources.yaml)에 `verified: false`로 추가했다. 기존 세금 계산은 기존 출처와 검증을 재사용한다.

## 입력 API

`calculate(source) -> (answer, trace)`이며 최상위 객체는 다음 다섯 필드만 받는다.

| 필드 | 조건 |
| --- | --- |
| `source_contract` | `yearend_pay_statement_v1` |
| `employee_id` | 합산 대상 직원의 비어 있지 않은 문자열 식별번호 |
| `processing_policy` | 문항에서 밝히는 합성 내부 확인 규약 문자열 |
| `calculation_facts` | 기존 A 계산 사실 객체. `reference_year: 2025`, 직원 이름과 정수 나이, 2025년 근무 시작일 및 종료일 필요 |
| `pay_statements` | 비어 있지 않은 증명서 객체 목록 |

`calculation_facts`는 기존 일반 계산 사실 또는 `yearend_evidence_v1` 계약만 지원한다. 새 계약의 재귀 중첩은 거부한다. 집계 전 정답이 노출되지 않도록 `annual_gross`, `non_taxable`, `paid_national_tax`, `paid_local_tax`를 미리 넣으면 거부한다. 영수증 배열의 의미 있는 순서는 보존한다.

증명서에는 다음 필드가 정확히 필요하다.

| 필드 | 조건 |
| --- | --- |
| `statement_id`, `employer_id`, `employee_id` | 비어 있지 않은 문자열 식별번호 |
| `period_start`, `period_end` | 엄격한 `YYYY-MM-DD` 형식의 2025년 날짜. 시작일이 종료일을 넘을 수 없음 |
| `revision` | 양의 정수. Boolean과 소수 거부 |
| `status` | `issued` 또는 `draft` |
| `gross_pay`, `non_taxable_pay` | 음수가 아닌 정수 원 금액. 비과세가 급여보다 클 수 없음 |
| `withheld_national_tax`, `withheld_local_tax` | 서로 독립된 음수가 아닌 정수 원 금액. Boolean과 소수 거부 |

원천증명서는 지급기간의 이미 제출된 금액을 뜻한다. 개별 급여 지급일에 대한 새 법률 해석은 하지 않는다.

## 문서 선택과 집계

같은 `statement_id`와 같은 내용의 반복 제출은 한 번만 센다. 같은 식별번호의 내용이 다르면 거부한다. 대상 직원의 동일 사용자 및 동일 기간에서 발급된 증명서 중 최고 수정차수를 선택한다. 초안은 수정차수가 높아도 제외한다. 최고 발급차수에 서로 다른 식별번호가 둘 이상이면 모호하므로 거부한다. 다른 직원의 증명서는 명시적으로 제외한다.

채택한 동일 사용자의 서로 다른 기간은 겹칠 수 없다. 양 끝 날짜를 포함하므로 전 기간의 종료일과 후 기간의 시작일이 같아도 겹친다. 다른 사용자에서 동시에 근무한 기간은 허용한다. 채택한 기간은 선언한 근무 시작일과 종료일 안에 있어야 한다. 적어도 하나의 대상 직원 발급본이 필요하다.

선택된 급여와 비과세 및 국세와 지방세 원천징수액을 사용자별로 합산한 뒤 네 연간 금액을 복사한 `calculation_facts`에 넣는다. 일반 사실은 기존 `engine.calculate`로 전달한다. 영수증 계약은 기존 `evidence.interpret`와 그 대조 trace를 거쳐 기존 계산으로 전달한다. 호출자의 자료는 수정하지 않는다.

## 출력 API

| 필드 | 값 |
| --- | --- |
| `employer_totals` | `employer_id` 순으로 정렬한 목록. 각 행에 `employer_id`, `gross_pay`, `non_taxable_pay`, `withheld_national_tax`, `withheld_local_tax` |
| `annual_gross`, `non_taxable` | 채택 증명서 급여와 비과세 연간 합계 |
| `paid_national_tax`, `paid_local_tax` | 독립된 국세 및 지방세 연간 기납부 합계 |
| `tax_calculation` | 기존 A 엔진의 전체 답안 객체 |
| `used_statement_ids`, `excluded_statement_ids` | 정렬된 채택 및 제외 증명서 식별번호 목록 |

trace는 `A_PAY_STATEMENT_RECONCILIATION` 하나를 반환한다. `inputs`에는 증명서 식별번호 순으로 정렬한 전체 제출 자료를 넣으며 동일본 반복 제출도 보존한다. `reconciliation`에는 중복 식별번호와 선택 및 제외 결과, 사용자별 집계와 네 연간 금액을 넣는다. `tax_derivations`에는 기존 A 계산 trace와 필요한 영수증 대조 trace를 그대로 넣는다. `output`은 최종 답안이다. 증명서 파일 순서는 답안과 trace에 영향을 주지 않는다.

## 독립 수기 검증

두 사용자의 급여가 각각 30,000,000원이고 비과세가 각각 1,000,000원이면 총급여는 58,000,000원이다. 근로소득공제 12,650,000원을 빼면 소득은 45,350,000원이며 본인 기본공제 후 과세표준은 43,850,000원이다. 산출세액은 5,317,500원이다. 근로소득세액공제 660,000원과 표준세액공제 130,000원을 적용하면 결정 국세는 4,527,500원이고 지방세는 452,750원이다.

각 사용자의 국세 기납부액 2,000,000원과 3,000,000원을 합하면 5,000,000원이다. 지방세 기납부액 120,000원과 280,000원은 별도로 합산하여 400,000원이 된다. 따라서 국세 정산은 -472,500원, 지방세 정산은 52,750원, 합계는 -419,750원이다. 기납부 지방세를 국세의 10%로 추정하지 않는다. 이 사례는 독립 수기 회귀검증이며 공식 숫자 예시라고 주장하지 않는다.

## 검증 결과

새 계약의 수정본과 초안 및 타 직원 제외를 검증했다. 같은 식별번호의 완전 중복과 충돌을 구분하고 기간 중복, 경계 날짜, 엄격한 정수 금액과 수정차수를 확인했다. 기존 영수증 계약 위임과 배열 순서, 호출자 자료 불변성도 검증했다. 관련 기존 연말정산 및 증빙 테스트와 Ruff를 통과했다.

별도 읽기 전용 검사에서 동결된 Batch 1 A 영역 300개를 현재 기존 경로로 다시 계산했다. 저장된 `gold.json`과 `trace.json`이 모두 바이트 단위로 일치했다. 작업 식별번호와 각 gold 및 trace SHA-256을 모은 증거의 SHA-256은 `db373f7ce1bd694f0d76dc7b05ccb5b0febc6a34878465bdbfb317dcfb93b28f`이다. 모델 호출은 0회다. 라우팅과 문서 복원 통합은 별도 통합 단계에서 검증한다.
