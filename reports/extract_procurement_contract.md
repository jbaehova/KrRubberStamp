# 선택적 포장 구매비 비교 계약

`extract_procurement_v1`은 같은 필요한 수량을 구매할 때 포장 올림, 최소 주문량,
배송비와 무료배송 경계를 함께 계산한다. 견적 효력, 보유 재고, 달력일 납기를
만족한 견적 중 실제 총액이 가장 낮은 견적을 선택한다. 개당 표시 단가만 낮은
공급사가 항상 선택되는 것은 아니다.

이 모듈은 문항에서 명시한 합성 사적 구매 약정을 계산한다. VAT 이름을 가진
숫자는 해당 약정의 산술이며 실제 세금 신고나 매입세액 공제 여부의 법적 판단을
뜻하지 않는다. `processing_policy`에 아래 계산 순서와 경계 및 동률 순서를
작성자가 독자에게 명시해야 한다. 모듈은 비어 있지 않은 문자열 여부를 검증하며
자연어 약정이 이 계약과 같은 뜻인지 판단하지 않는다.

## API와 입력

구현은 [procurement.py](../rules/d_extract/procurement.py)이며 공개 진입점은
`calculate(source) -> (answer, trace)`이다. `CONTRACT`는
`extract_procurement_v1`, `RULE_ID`는 `D.procurement_comparison`이다.
기존 D 엔진, 증거 결합 계약과 입고 정산 계약은 수정하지 않았다.

| 최상위 필드 | 제약 |
| --- | --- |
| `source_contract` | `extract_procurement_v1` |
| `processing_policy` | 계산 약정을 명시한 비어 있지 않은 문자열 |
| `item`, `base_unit` | 비어 있지 않은 문자열 |
| `required_units` | Boolean과 실수를 허용하지 않는 양의 정수 |
| `order_date`, `latest_delivery_date` | 정확한 `YYYY-MM-DD` 달력 날짜, 납기일은 주문일 이상 |
| `quotes` | 비어 있지 않은 견적 목록 |

견적은 아래 필드를 모두 갖고 다른 필드를 갖지 않는다.

| 견적 필드 | 제약 |
| --- | --- |
| `quote_id`, `vendor` | 비어 있지 않은 문자열 |
| `valid_from`, `valid_until` | 정확한 ISO 날짜, 시작일은 종료일 이하 |
| `pack_units`, `minimum_packs` | 양의 정수 |
| `pack_price`, `shipping_price`, `stock_packs`, `lead_days` | 0 이상의 정수 |
| `price_includes_vat`, `shipping_price_includes_vat` | 실제 Boolean |
| `free_shipping_at` | `None` 또는 0 이상의 정수 |

정수 필드는 `True`, `False`, 실수와 숫자 문자열을 거절한다. 같은 견적 ID는
원래 내용과 값 자료형이 모두 같을 때만 한 번 계산한다. 다른 내용의 같은 ID는
거절한다. 공급사에는 기존 `normalize_vendor`를 적용하며 빈 정규화 결과를
거절한다. 품목은 NFKC, 공백 제거와 casefold로 정규화한다. `base_unit`은
원문 그대로 보존하며 서로 다른 단위를 변환하거나 합치지 않는다.

## 명시할 계산 약정

1. 필요한 포장 수는 `ceil(required_units / pack_units)`이다. 이를 최소 주문
   포장 수와 비교해 큰 값을 주문한다. 포장 수 계산은 정수 연산만 사용한다.
2. 확보 수량은 포장 수에 포장당 수량을 곱한 값이며 잉여 수량은 확보 수량에서
   필요 수량을 뺀 값이다.
3. 상품금액은 주문 포장 수에 포장 가격을 곱한다. 포함 표시는 공급가액을
   `금액 * 10 // 11`로 하고 나머지를 세액으로 한다. 별도 표시는 공급가액을
   금액으로 하고 세액을 `금액 // 10`으로 한다.
4. 상품 공급가액과 세액을 더한 총액을 무료배송 기준과 비교한다. 기준 이상은
   무료배송이다. `None`은 기준 없음이며 0은 유효한 무료배송 기준이다. 배송비는
   자체 포함 또는 별도 표시로 분리 계산한다. 배송비까지 합친 금액을 다시
   무료배송 판정에 사용하지 않는다.
5. 상품과 배송의 공급가액 및 세액을 각각 더한다. 단위당 먼저 버림하거나
   공급사별로 재반올림하지 않는다.
6. 주문일에 `lead_days` 달력일을 더해 도착일을 구한다. 주말과 휴일을 자동으로
   제외하지 않는다. Python 달력 범위를 벗어나는 도착일은 거절한다.
7. 주문일이 견적 시작일과 종료일 사이에 포함되고 재고 포장 수가 주문 포장 수
   이상이며 도착일이 최종 납기일 이하인 견적만 적격이다.
8. 적격 견적의 `(최종 총액, 정규화 공급사, 견적 ID)`를 오름차순 비교한다.
   적격 견적이 없으면 선택 필드는 `None`이다.

## 출력과 추적

`quote_comparisons`는 견적 ID 순서다. 각 행은 아래 값을 갖는다.

- 식별과 수량: `quote_id`, `vendor`, `packs`, `obtained_units`, `leftover_units`
- 상품: `merchandise_supply`, `merchandise_vat`, `merchandise_total`
- 배송: `shipping_supply`, `shipping_vat`, `shipping_total`
- 합계: `supply`, `vat`, `total`
- 적격 판정: `delivery_date`, `valid_on_order`, `stock_sufficient`,
  `delivered_in_time`, `eligible`

최상위 선택 결과는 `chosen_quote_id`, `chosen_vendor`, `chosen_total`,
`chosen_leftover_units`, `eligible_quote_count`다.

추적은 한 개의 `D.procurement_comparison` 행이다. 전체 입력의 복사본과 견적 ID
순서로 정렬한 원본 견적 행을 보존한다. 계산 부분은 포장 올림, 최소 주문 적용,
상품 계산 전 금액과 세금 표시, 무료배송 비교 기준과 판정, 배송 계산 전 금액을
기록한다. 선택 부분은 실제 적격 비교 튜플과 선택 튜플 및 최종 결과를 기록한다.
입력 견적 순서는 답과 추적을 바꾸지 않는다. 정확한 중복 추가는 답을 바꾸지
않으며 추적의 원본 입력과 `deduplicated_quote_ids`에는 중복 사실이 남는다.
입력 객체를 변경하지 않으며 반환값과 추적도 원본과 독립적인 복사본이다.

## 독립 수기 검산

필요 수량은 11개다. A는 10개 포장당 900원 별도이고 배송비는 500원 별도다.
2포장을 사야 하므로 20개를 확보한다. 상품은 공급가액 1,800원과 세액 180원,
배송은 공급가액 500원과 세액 50원이다. 총액은 2,530원이며 잉여는 9개다.

B는 6개 포장당 600원 별도이고 상품 세금 포함 총액 1,320원 이상이면 무료배송이다.
2포장을 사면 12개를 확보한다. 상품 공급가액 1,200원과 세액 120원의 총액이
무료배송 기준과 정확히 같아 배송비는 0원이다. 총액은 1,320원이며 잉여는 1개다.
A의 개당 표시 단가 90원이 B의 100원보다 낮지만 최종 구매 총액은 B가 낮다.

상품과 배송의 세금 표시를 따로 처리하는 예시는 필요 4개와 3개 포장이다.
포장당 포함 1,101원 상품 2포장의 2,202원은 공급가액 2,001원과 세액 201원이다.
별도 배송 101원은 공급가액 101원과 세액 10원이므로 최종 공급가액 2,102원,
세액 211원과 총액 2,313원이다. 반대 표시는 별도 포장당 1,009원 상품 2포장의
공급가액 2,018원과 세액 201원에 포함 배송 111원의 공급가액 100원과 세액
11원을 더해 공급가액 2,118원, 세액 212원과 총액 2,330원이 된다.

## 검증과 인계

[전용 테스트](../tests/test_extract_procurement.py)는 위 수기 기대값을 직접
기록했다. 최소 주문과 포장 올림 경계, 무료배송의 바로 아래와 같은 값 및 바로 위,
재고와 효력 및 납기의 포함 경계, 윤년 달력일, 부적격 저가 견적 제외, 대상 없음과
동률을 확인했다. 중복과 순서 불변, 충돌 중복, 엄격한 자료형, 잘못된 날짜와
필드, 큰 정수의 정확한 올림 및 입력 비변경도 확인했다.

검증 명령은 다음과 같다.

```text
uv run pytest tests/test_extract_procurement.py tests/test_extract.py tests/test_extract_evidence.py tests/test_extract_fulfillment.py
177 passed, 5 warnings in 1.04s

uv run ruff check rules/d_extract/procurement.py tests/test_extract_procurement.py
All checks passed!

uv run ruff format --check rules/d_extract/procurement.py tests/test_extract_procurement.py
2 files already formatted
```

경고 5개는 기존 PDF 왕복 테스트의 PyMuPDF 확장 자료형에 관한 deprecation이다.
모델 API를 호출하지 않았고 벤치마크 문항을 만들지 않았다. 이번 변경은 독립
모듈과 테스트 및 이 문서에 한정된다. 선택적 라우팅, 한글 필드 이름, 합성 출처
등록, 문서 왕복과 기존 Batch 1의 전체 무결성 확인은 통합 담당 root에게 인계한다.
해당 세 파일의 원본 쓰기 잠금을 반환한다.

root 통합에서 선택적 계산 라우팅과 한국어 원천 필드 및 합성 규칙 출처를 연결했다. 실제 구매 요청 PDF와 두 공급사의 XLSX 및 HWPX 견적을 렌더링하고 복원하여2530원과1320원의 비교 및 후자의 선택을 확인했다. 새 계약과 기존 D 관련 검사178개가 통과했고 Ruff도 통과했다. 개별 집필 문항의 의미 관계와 전체 원고 검증은 이 계약 검사와 별도로 수행한다.
