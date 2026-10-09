# 다품목 장바구니 구매 비교 계약

`extract_cart_procurement_v1`은 품목별 적격 견적 하나씩을 선택한 전체 구매 조합을 비교한다.
동일 공급사 ID의 상품 합계를 무료배송 기준과 대조하고 해당 공급사의 배송비를 한 번만 적용한다.
품목마다 배송비를 붙여 가장 싼 견적을 독립적으로 선택하는 방식과 최종 구매 선택이 달라질 수 있다.

이 계약은 입력 자료가 명시하는 합성 사적 구매 약정이다. 새로운 정부 규칙을 정의하지 않는다.
세금 이름을 가진 금액은 약정의 정수 산술이며 실제 세금 신고나 매입세액 공제 자격을 판단하지 않는다.
`processing_policy`에는 계산 순서와 적용 경계 및 동률 순서를 독자가 확인할 수 있게 작성해야 한다.
모듈은 해당 문자열이 비어 있지 않은지만 검사하며 자연어 뜻을 자동 판정하지 않는다.

## API와 정확한 입력 모양

[cart_procurement.py](../rules/d_extract/cart_procurement.py)의 공개 API는
`calculate(source) -> (answer, trace)`다. `CONTRACT`는 `extract_cart_procurement_v1`이며
`RULE_ID`는 `D.cart_procurement_comparison`이다. 기존 단품 비교 모듈의 문자열과 날짜 및
정수 검증과 세금 산술 함수를 재사용하지만 그 모듈은 변경하지 않는다.

모든 객체는 아래에 적힌 필드만 갖는다. 누락 필드와 추가 필드는 오류다.

| 최상위 필드 | 제약 |
| --- | --- |
| `source_contract` | `extract_cart_procurement_v1` |
| `processing_policy` | 비어 있지 않은 문자열 |
| `order_date` | 정확한 `YYYY-MM-DD` 달력 날짜 |
| `latest_delivery_date` | 같은 날짜 형식이며 주문일 이상 |
| `items` | 서로 다른 ID를 가진 품목 2개 이상 4개 이하 |
| `vendors` | 서로 다른 ID를 가진 공급사 1개 이상 8개 이하 |
| `offers` | 각 품목에 서로 다른 견적 ID 1개 이상 6개 이하 |

| 품목 필드 | 제약 |
| --- | --- |
| `item_id`, `name`, `base_unit` | 비어 있지 않은 문자열 |
| `required_units` | 양의 정수 |

| 공급사 필드 | 제약 |
| --- | --- |
| `vendor_id`, `name` | 비어 있지 않은 문자열 |
| `shipping_price` | 0 이상의 정수 |
| `shipping_price_includes_vat` | 실제 Boolean |
| `free_shipping_at` | `None` 또는 0 이상의 정수 |

| 견적 필드 | 제약 |
| --- | --- |
| `quote_id`, `item_id`, `vendor_id` | 비어 있지 않은 문자열이며 두 참조 ID는 실제 행과 일치 |
| `valid_from`, `valid_until` | 정확한 ISO 달력 날짜이며 시작일은 종료일 이하 |
| `pack_units`, `minimum_packs` | 양의 정수 |
| `pack_price`, `stock_packs`, `lead_days` | 0 이상의 정수 |
| `price_includes_vat` | 실제 Boolean |

정수에 Boolean이나 실수 또는 숫자 문자열을 허용하지 않는다. 업체명에는 기존
`normalize_vendor`를 적용하고 결과가 빈 문자열이면 오류다. ID에는 이름 정규화를 적용하지 않는다.
서로 다른 공급사 ID는 정규화 이름이 같더라도 배송 계정을 합치지 않는다. 서로 다른 품목 ID는
이름과 단위가 같더라도 각각 필요한 수량을 구매한다. 단위를 변환하지 않는다.

품목 ID와 공급사 ID 및 전체 견적 ID는 각각 고유하다. 같은 ID와 동일한 값 및 자료형의 재전송은
한 번만 계산하며 내용이 다르면 오류다. 개수 상한은 이 중복 제거 후 서로 다른 ID 수에 적용한다.
선택되지 않은 공급사는 배송비가 없다. 견적이 부적격이더라도 필드와 참조는 모두 검증한다.

## 계산과 선택

1. 품목별 견적의 구매 포장 수는 `max(ceil(required_units / pack_units), minimum_packs)`다.
   정수만 사용해 올림한다. 확보 수량은 포장 수에 포장당 수량을 곱하고 필요 수량을 빼면 잉여다.
2. 견적별 상품 금액은 포장 수에 포장 가격을 곱한다. 포함 표시이면 공급가액은 `금액 * 10 // 11`이며
   나머지가 세액이다. 별도 표시이면 금액이 공급가액이고 세액은 `금액 // 10`이다.
   견적마다 먼저 나눈 후 공급사 합계를 구하며 합친 금액에서 세액을 다시 계산하지 않는다.
3. 주문일이 유효기간 양 끝을 포함해 범위 안에 있고 필요한 포장 수 이상의 재고가 있으며
   주문일에 달력일 `lead_days`를 더한 도착일이 최종 납기일 이하인 견적만 적격이다.
   주말이나 공휴일은 제외하지 않는다. 표현할 수 없는 도착일은 오류다.
4. 모든 품목에서 적격 견적 하나씩을 고른 조합을 열거한다. 최대 조합 수는 `6 ** 4 = 1296`이다.
   한 품목을 여러 견적으로 나누거나 무료배송을 위해 포장 수를 늘리지 않는다.
5. 선택한 견적을 공급사 ID별로 묶고 해당 상품의 세금 포함 총액을 합친다.
   이 합계가 해당 공급사의 `free_shipping_at` 이상이면 무료배송이다.
   `None`은 기준 없음이며 0은 실제 무료배송 기준이다.
   다른 공급사의 상품이나 미선택 견적 및 중복 전송 금액은 기준에 합산하지 않는다.
6. 무료배송이 아니면 해당 공급사의 배송비를 한 번 적용하고 배송비 자체의 포함 여부로 나눈다.
   배송 금액을 무료배송 판단의 기준에 다시 더하지 않는다.
7. 견적별 상품과 공급사별 실제 배송의 공급가액 및 세액을 합친 최종 총액이 가장 낮은 조합을 선택한다.
   동률이면 품목 ID 순서의 `(정규화 업체명, 공급사 ID, 견적 ID)` 튜플을 사전식으로 비교한다.
   잉여 수량이 작은 조합에 별도 우선권을 주지 않는다.

어떤 품목에서든 적격 견적이 없으면 완성 조합이 없다. 이때 선택 견적과 공급사 합계는 빈 목록이다.
세 가지 총액은 `None`이며 완성 조합 수는 0이다. 부적격 견적의 평가 결과는 남긴다.

## 출력과 추적

정확한 최상위 출력은 다음과 같다.

| 필드 | 내용 |
| --- | --- |
| `offer_comparisons` | 모든 견적 평가를 견적 ID 순서로 정렬 |
| `chosen_offers` | 선택 견적 평가를 품목 ID 순서로 정렬 |
| `vendor_cart_totals` | 선택한 공급사별 합계를 공급사 ID 순서로 정렬 |
| `supply_total`, `vat_total`, `grand_total` | 최종 공급가액과 세액 및 총액 또는 `None` |
| `feasible_cart_count` | 서로 다른 적격 전체 조합 수 |

견적 평가 행의 식별 필드는 `quote_id`, `item_id`, `vendor_id`, `vendor`다.
수량 필드는 `packs`, `obtained_units`, `leftover_units`다.
상품 필드는 `merchandise_supply`, `merchandise_vat`, `merchandise_total`이다.
적격 필드는 `delivery_date`, `valid_on_order`, `stock_sufficient`, `delivered_in_time`, `eligible`이다.
견적 행에는 배송비를 할당하지 않는다.

공급사 합계 행은 `vendor_id`와 `vendor` 및 같은 세 가지 상품 필드를 갖는다.
배송 필드는 `shipping_free`, `shipping_supply`, `shipping_vat`, `shipping_total`이다.
최종 합계 필드는 `supply`, `vat`, `total`이다.

추적은 `D.cart_procurement_comparison` 행 하나다. 원본 입력 전체를 복사하고 품목과 공급사 및
견적 목록을 각 ID 순서로 정렬한다. 정확한 중복의 원본 행은 입력 복사본에 남기고
`deduplicated_item_ids`, `deduplicated_vendor_ids`, `deduplicated_quote_ids`에도 기록한다.
`selection.evaluated_carts`에 모든 완성 조합의 총액과 동률 비교 튜플을 최종 선택 순서로 남긴다.
선택 튜플과 선택 이유 및 답 전체의 독립 복사본도 기록한다. 입력 목록 순서는 답이나 추적에
영향을 주지 않는다. 반환한 평가 행과 선택 행 및 추적은 원본을 변경하거나 서로 값을 공유하지 않는다.

## 독립 수기 검산

A와 B가 각 1개 필요하다. V1은 별도 배송비 400원이고 A는 별도 1,000원이며 B는 별도 500원이다.
V2는 배송비가 없고 A는 별도 1,500원이며 B는 별도 800원이다.

| 선택 | 상품과 배송 총액 산식 | 최종 총액 |
| --- | --- | --- |
| 둘 다 V1 | `1100 + 550 + 440` | 2,090원 |
| 둘 다 V2 | `1650 + 880` | 2,530원 |
| A는 V1, B는 V2 | `1100 + 440 + 880` | 2,420원 |
| A는 V2, B는 V1 | `1650 + 550 + 440` | 2,640원 |

품목별 독립 배송 포함 비교에서는 A는 V1이고 B는 V2지만 전체 구매에서는 V1을 함께 선택한다.
배송비를 품목마다 붙이면 이 결과를 얻지 못한다. V1 전체의 공급가액은 1,900원이고 세액은 190원이다.

무료배송 반전 사례에서는 V1의 두 상품이 각각 별도 500원이며 배송비는 별도 500원이다.
V2의 두 상품은 각각 별도 550원이고 배송비는 없다. V1 무료배송 기준이 1,100원이면 개별 상품은
기준 아래지만 두 상품 합계가 정확히 기준에 도달하여 V1 전체 1,100원이 선택된다.
기준을 1,101원으로 바꾸면 V1 전체는 배송 포함 1,650원이며 V2 전체 1,210원이 선택된다.

혼합 표시에서는 V1의 첫 상품 포함 1,101원이 공급가액 1,000원과 세액 101원이다.
둘째 상품 별도 1,009원은 공급가액 1,009원과 세액 100원이다.
별도 배송 101원은 공급가액 101원과 세액 10원이다. 공급가액 2,110원과 세액 211원의
최종 총액은 2,321원이다. 포함 2원 상품 두 행은 각각 공급가액 1원과 세액 1원으로 먼저 나눈다.
두 상품의 합계 4원에서 공급가액을 한 번 계산한 3원으로 대신하지 않는다.

## 검증과 인계

전용 검사 159개는 위 수기 기대값과 실제 무료배송 반전 및 독립 공급사 계정을 확인한다.
최대 1,296개 완성 조합과 동률 순서 및 잉여 수량 우선권 없음도 확인한다.
무료배송을 노린 구매 수량 증가와 미선택 대안 합산 및 중복 금액 합산을 허용하지 않는지 확인한다.
잘못된 필드와 참조 및 자료형과 날짜를 거절하고 순서 불변 및 입력 비변경을 검사한다.

```text
uv run pytest tests/test_extract_cart_procurement.py tests/test_extract_procurement.py tests/test_extract.py tests/test_extract_evidence.py tests/test_extract_fulfillment.py
337 passed, 5 warnings

uv run ruff check rules/d_extract/cart_procurement.py tests/test_extract_cart_procurement.py
All checks passed!

uv run ruff format --check rules/d_extract/cart_procurement.py tests/test_extract_cart_procurement.py
2 files already formatted
```

기존 Batch 1 D 300개 전체의 답과 추적을 구현 전후 각각 계산하고 동일성을 확인했다.
증거는 `tmp/cart_procurement_contract/legacy_integrity.json`이며 전후 직렬화 SHA-256은
`e28e6e2cf1cd14ac34a60bfd900adc82406a895fa1898c4affcf13b3e0cc6f48`이다.
경고 5개는 기존 PDF 왕복 검사에서 PyMuPDF 확장 자료형의 deprecation이다.
모델 API를 호출하지 않았고 벤치마크 문항을 만들지 않았다.

통합 담당 root가 선택적 라우팅과 한글 필드 및 DATA_SPEC과 전체 출처 집계를 연결한다.
실제 PDF와 XLSX 및 HWPX 왕복도 root가 확인한다. 이 변경은 새 모듈과 전용 테스트 및
D 출처의 새 규칙 행과 이 계약 문서에 한정된다.
