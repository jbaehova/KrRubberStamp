# 선택적 주문 정산 계약

`extract_fulfillment_v1`은 주문과 실제 부분 인수 및 반품을 대조하고 실행된 선지급을 차감하는 선택적 계약이다. 기존 D 문항의 계약과 채점 결과를 바꾸지 않는다. 구현 진입점은 `rules/d_extract/fulfillment.py`의 `calculate(source)`이며 반환값은 `(answer, trace)`이다. 원고를 자동 생성하지 않는다.

모든 업체와 금액은 합성 자료다. 공급가액과 VAT라는 필드명은 문서에서 제시한 정산 약정의 산술을 뜻한다. 실제 부가가치세 신고나 세금 환급 자격을 판정하지 않는다. 외부 법령이나 원문 라이선스를 추가하지 않는다. 출처 규칙 ID는 `D.fulfillment_reconciliation`이며 공개 출처 등록에서 `verified: false`로 표시한다.

## 입력 계약

최상위 `source_contract`는 계약 ID와 같아야 한다. `processing_policy`는 비어 있지 않은 문자열이다. 집필자는 실제 문서에 합성 정산 약정의 계산과 제외 기준을 적어야 한다. 구현은 정책 문장의 의미를 자동 판독하지 않는다. `cutoff_date`는 엄격한 `YYYY-MM-DD` 날짜다.

각 배열의 행에는 아래 필드가 정확히 있어야 한다. 정수 필드는 Boolean이나 float를 허용하지 않는다. 식별자는 비어 있지 않은 문자열이며 공백 제거 등의 정규화를 하지 않는다.

| 배열 | 행의 필드 | 제약 |
| --- | --- | --- |
| `orders` | `order_id`, `vendor`, `date`, `kind`, `lines` | 주문 ID 중복 금지. `kind`는 `order` 또는 `quote`. 업체 이름은 정규화 후에도 비어 있지 않아야 한다. |
| 주문의 `lines` | `line_id`, `item`, `base_unit`, `ordered_packages`, `units_per_package`, `package_price`, `price_includes_vat` | 주문 내 행 ID 중복 금지. 앞의 두 수량은 양의 정수. 포장 가격은 0 이상 정수. VAT 포함 여부는 Boolean. 품명과 기초 단위는 비어 있지 않은 문자열. |
| `events` | `event_id`, `order_id`, `line_id`, `kind`, `date`, `units` | `kind`는 `received` 또는 `returned`. 기초 단위 수량은 양의 정수. 주문과 행의 정확한 쌍을 참조해야 한다. |
| `payments` | `payment_id`, `order_id`, `date`, `status`, `amount` | `status`는 `executed` 또는 `planned`. 금액은 0 이상 정수. 존재하는 주문을 참조해야 한다. |

다른 주문의 동일한 `line_id`는 허용하며 참조는 항상 `(order_id, line_id)`로 구분한다. 이벤트와 지급 ID는 각 배열 안에서 내용과 값의 자료형까지 같은 중복만 한 번 계산한다. ID가 같고 내용이 다르면 거절한다. 주문 ID는 내용이 같아도 중복을 거절한다.

견적은 모든 정산에서 제외한다. 견적의 실제 인수나 반품 및 실행 지급은 거절한다. 견적에 연결된 예정 지급은 참조를 검사한 뒤 제외한다. 실제 이벤트와 실행 지급은 원주문 날짜보다 빠르면 거절한다. 모든 행의 참조와 형식은 마감 이후 자료를 포함해 검사한다.

## 스냅샷과 계산

마감일 당일을 포함한 이벤트와 실행 지급만 계산한다. 예정 지급은 날짜와 관계없이 제외한다. 미래 주문의 행도 출력하되 마감일까지 실제 인수가 없으면 0 인수로 표시한다.

날짜별로 실제 인수를 먼저 반영하고 그날 반품을 나중에 반영한다. 같은 날 인수분은 그날 반품에 사용할 수 있다. 어느 시점에도 누적 반품이 누적 인수를 초과하면 거절한다. 주문 수량을 넘긴 실제 인수는 허용하며 미인수 수량을 음수로 표시한다.

1. `ordered_units = ordered_packages * units_per_package`
2. `net_units = received_units - returned_units`
3. `outstanding_units = ordered_units - net_units`
4. `amount = floor(package_price * net_units / units_per_package)`
5. 포함가이면 `supply = amount * 10 // 11`, `vat = amount - supply`다. 별도가이면 `supply = amount`, `vat = supply // 10`이다.
6. 각 행에서 `total = supply + vat`를 구한 뒤 업체별로 합산한다. 업체 잔액은 `total - paid`다.

곱셈 후 정수 나눗셈만 사용한다. 먼저 기초 단위당 가격을 버리거나 업체 총액에서 일괄 세액을 계산하지 않는다. 원 미만 버림은 이 합성 정산 약정의 명시적 규칙이다.

## 정답 필드

최상위에는 아래 여섯 필드가 있다. 문자열 정렬은 Python 문자열 순서이며 모든 수치는 정수다. 품명은 NFKC 정규화 후 공백 제거 및 casefold를 적용한다. 업체는 기존 `normalize_vendor`를 사용한다. `base_unit`은 문서의 문자열을 그대로 사용하므로 다른 단위를 합치지 않는다.

| 필드 | 자료형과 내부 필드 | 순서 |
| --- | --- | --- |
| `line_settlements` | 객체 배열. 문자열 `order_id`, `line_id`, `item`, `base_unit`. 정수 `ordered_units`, `received_units`, `returned_units`, `net_units`, `outstanding_units`, `supply`, `vat`, `total`. | `(order_id, line_id)` |
| `item_quantities` | 객체 배열. 문자열 `item`, `base_unit`. 정수 `net_units`. | `(item, base_unit)` |
| `vendor_balances` | 객체 배열. 문자열 `vendor`. 정수 `supply`, `vat`, `total`, `paid`, `balance`. | 정규화 업체명 |
| `grand_total` | 모든 업체의 `total` 합계 | 단일 정수 |
| `payment_total` | 모든 업체의 `paid` 합계 | 단일 정수 |
| `balance_total` | 모든 업체의 `balance` 합계 | 단일 정수 |

미인수 수량과 잔액은 음수가 될 수 있다. 나머지 수량과 금액은 0 이상이다. 실제 주문은 인수가 없더라도 행 및 업체별 합계에 포함한다. 견적만 있는 빈 스냅샷은 빈 배열과 0 합계를 반환한다.

## 추적과 검증

trace는 규칙 ID `D.fulfillment_reconciliation`인 한 행이다. 입력에는 전체 주문과 이벤트 및 지급 원천을 담으며 문서 순서를 정렬해 보존한다. 결과에는 적용 및 제외된 ID와 중복 ID를 남긴다. 순인수 수량의 이벤트별 변화와 각 행의 버림 전 분자 및 포장당 수량을 기록하고 최종 정답을 함께 넣는다. 입력 문서의 순서를 바꾸어도 정답과 trace가 모두 같다. 원천 입력을 수정하지 않고 결과와 trace의 가변 객체를 분리한다.

수기로 정한 검산은 다음과 같다. 첫 번째 포함가 행은 4개 포장 11,001원이며 7개 인수 후 1개 반품했다. `floor(11,001 * 6 / 4) = 16,501`원이므로 공급가액 15,000원과 VAT 1,501원이다. 두 번째 별도가 행은 5개 포장 1,003원이며 8개 인수 후 3개 반품했다. 공급가액 1,003원과 VAT 100원이다. 별도 주문의 세 번째 포함가 행은 3개 포장 1,000원 중 1개만 인수했으므로 총액 333원이며 공급가액 302원과 VAT 31원이다.

합계는 17,937원이다. 실행 선지급 19,000원을 빼면 잔액은 -1,063원이다. 마감 이후 인수 100개와 마감 이후 지급 44,444원은 이 스냅샷에서 제외한다. 견적의 예정 지급 99,999원도 제외한다. 두 실제 주문의 `line_id`가 같아도 서로 섞이지 않는다.

`uv run pytest tests/test_extract_fulfillment.py`의 32개 테스트가 통과했다. 수기 정답 전체 일치와 문서 순서 불변을 검증했다. 참조 오류와 상충 중복 및 날짜 역전도 검사했다. 같은 날 인수 후 반품과 원 미만 버림을 확인했다. 마감일 이동에 따른 초과 인수와 선지급 변화도 확인했다. `uv run ruff check rules/d_extract/fulfillment.py tests/test_extract_fulfillment.py`도 통과했다.

기존 D 계산과 증빙 계약 테스트를 함께 실행한 `uv run pytest tests/test_extract.py tests/test_extract_evidence.py tests/test_extract_fulfillment.py`는 51개 모두 통과했다. 기존 실제 문서 검증 경로에서 SWIG 관련 deprecation 경고 5개가 출력됐다. 새 모듈과 테스트의 Ruff 형식 검사도 통과했다.

통합 단계에서 선택적 라우팅과 한국어 원천 필드 표시를 연결했다. PDF의 발주 약정과 XLSX의 입고 및 반품 대장, HWPX의 지급 기록을 렌더링한 뒤 실제 파일에서 사실을 복원했다. 복원된 원천을 공통 계산 진입점으로 처리하여 수기 정산액과 지급액 및 잔액을 확인했다. 기존 D 검사와 새 계약 및 내보내기와 게시 도구의 관련 검사 65개가 모두 통과했다. 새 문항마다 직접 집필한 관계와 원천 복원 검증은 별도로 수행한다.
