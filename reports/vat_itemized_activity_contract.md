# VAT 확정 청구 행 원천 계약

`vat_itemized_activity_evidence_v1`은 실제 확정 청구의 상품행과 명시된 사적 할인 조건을 공급가로 복원한다. `C_VAT_ITEMIZED_ACTIVITY` trace는 계산 근거를 기록한다. 복원된 거래는 기존 `vat_activity_evidence_v1` 해석기와 VAT engine을 통과하며 공개 답은 기존 11필드를 유지한다.

## 원천 형태

최상위 필수 필드는 아래와 같다.

```text
source_contract: vat_itemized_activity_evidence_v1
billing_policy: 비어 있지 않은 확정 청구 조건 설명
taxpayer_type: general
period_start: 2026-01-01
period_end: 2026-06-30
business_name: 비어 있지 않은 이름
business_type: individual | corporation
consumer_facing_business: strict boolean
receipt_credit_previously_claimed: nonnegative integer won
prepaid_assessed_vat: nonnegative integer won
operations: 기존 활동 계약의 원천 목록
activities: 기존 활동 계약의 원천 목록
transactions: 1..32개 문서 원천 행
```

선택 필드는 `scope_note`, `domain`, `synthetic_id`, `reference_period`, `prior_year_site_supply_base`, `prior_declared_vat_paid`, `vehicle_registry`, `supplier_status_records`, `site_year_records`, `filing_site_id`이다. 원천에는 전년도 사업장 공급가 scalar 또는 사업장 등록 원천이 있어야 한다. `domain`은 `C_vat`이고 `reference_period`는 `2026-H1`이다. 원천 라벨과 정책은 비어 있지 않은 문자열이다. 기존 등록 계약의 판정 및 충돌 검사를 그대로 적용한다.

각 거래 행의 정확한 필수 필드는 다음과 같다.

```text
transaction_id, document_id, direction, date, description,
taxable, evidence, invoice_issued, vat_separately_stated,
counterparty_consumer, invoice_lines, document_discount, freight_supply
```

선택 필드는 `activity_id`, `supplier_id`, `supplier_general`, `vehicle_id`, `vehicle_subject_excise`, `vehicle_direct_business`이다. 거래 방향은 `sale` 또는 `purchase`이고 증빙 종류는 기존 engine의 5종을 사용한다. 날짜는 실제 공급일의 `YYYY-MM-DD`이다. 모든 거래는 명시적으로 `taxable: true`인 국내 일반과세 공급이다. 실제 다음 기간 공급도 원천에는 포함할 수 있으며 현재 신고 포함 여부는 기존 기간 규칙으로 결정한다. 각 매입의 원천 활동과 실제 문서 집합 및 날짜가 일치해야 한다.

`invoice_lines`는 1..6개 행이다. 각 행의 정확한 필드는 `line_id`, `description`, `quantity`, `unit_supply_price`, `unit_discount`, `line_discount`이다. 거래 문서 안의 `line_id`는 유일하다. 설명과 ID는 비어 있지 않은 문자열이다. 수량은 1..10000의 strict integer이고 가격 및 할인은 strict nonnegative integer won이다. bool과 실수는 정수로 받지 않는다.

## 가격 조건과 상한

모든 입력 가격은 세액 별도 공급가이다.

```text
행 원금 = quantity × unit_supply_price
개당 할인 후 행 금액 = quantity × (unit_supply_price - unit_discount)
행 공급가 = 개당 할인 후 행 금액 - line_discount
상품 공급가 합계 = 모든 행 공급가의 합
최종 공급가 = 상품 공급가 합계 - document_discount + freight_supply
VAT = 최종 공급가 / 10
최종 공급대가 = 최종 공급가 + VAT
```

단가와 개당 할인 상한은 10억 원이다. 할인 전 행 원금도 10억 원 이하이다. 개당 할인은 단가를 넘을 수 없고 행 할인은 개당 할인 후 행 금액을 넘을 수 없다. 문서 할인은 상품 공급가 합계 이내이며 배송에는 적용하지 않는다. 배송 공급가 상한은 10억 원이다. 최종 거래 공급가는 양수이며 명시 상한은 100억 원이다. 6개 행과 배송의 더 작은 원천 상한에 따라 실제 도달 가능한 거래 상한은 70억 원이다.

무료 부속 행과 상품 전액 할인은 허용하되 전체 공급가가 양수여야 한다. 동일 공급자의 확정 청구에 포함된 과세 배송만 해당 문서에 더한다. 별도 운송업체의 공급은 별도 실제 거래로 기록한다.

행별 공급가에는 별도 반올림을 적용하지 않는다. 최종 거래 공급가는 10원의 배수여야 한다. 기존 exact VAT split과 카드 발행 공제의 합산 후 정수 절사 규칙을 유지한다. 혼합 세율과 면세 공급, 외화, 단위 변환, 미확정 견적 및 가격 결정, 반품, 공급시기 특례, 공통매입 안분은 이 계약 범위에 포함하지 않는다.

## ID와 판정 경계

실제 거래는 1..16개이다. 서로 다른 실제 거래 ID는 금액이 같아도 별개로 계산한다. 동일 `document_id`의 완전 동일 원천 복사는 한 번만 읽고 중복 ID를 trace에 기록한다. 같은 문서 ID의 원천 내용이 다르면 신고 기간 밖 원천도 거절한다.

서로 다른 문서 ID가 같은 실제 거래를 나타내면 상품행 표현이 달라도 최종 공급가와 실제 거래 조건이 같아야 한다. 실제 활동과 공급자 및 차량 ID를 먼저 비교한 뒤 기존 engine이 실제 조건과 VAT split을 다시 비교한다. 증빙 종류는 기존대로 합쳐지고 전자 발급 사실은 발행 공제 판정에 우선 적용된다.

알 수 없는 필드와 누락된 필드를 거절한다. `amount`, `includes_vat`, `invoice_total`과 각종 계산 결과 및 세법 판정을 원천에 넣을 수 없다. 원천 내부의 nested `source_contract`도 거절한다. 등록 원천을 사용하면 기존 공급자 및 차량의 미리 판정한 flags 입력 금지를 유지한다.

## trace와 부모 계약

첫 trace의 입력은 중복을 제거하고 ID별로 정렬한 전체 raw 원천이다. 출력 `invoice_amounts`에는 문서별 행 원금과 할인 후 금액, 행 공급가, 상품 합계, 문서 할인, 배송 공급가, 최종 공급가 및 세액과 공급대가가 기록된다. 다음 trace는 기존 활동 연결이고 이후는 기존 engine의 VAT trace이다. 원천 목록 순열이 전체 답과 전체 trace를 바꾸지 않는다. 원천과 반환 답 및 trace 사이에 공유되는 변경 가능한 컨테이너가 없다.

`vat_bank_reconciliation_v1`은 새 원천 식별자를 child allowlist에 명시적으로 추가한다. 새 child에는 `billing_policy`와 원천 `transactions`가 필수이며 전체 itemized validator가 계산한다. 부모 및 nested child와 파생 ledger를 원천으로 받지 않는다. `vat_bank_batch_allocation_v1`은 기존 은행 부모 연결을 통해 같은 raw child를 사용한다. 부모의 현금 차이 계산과 배치 수수료 구분은 그대로 유지한다.

## 검증

개별 작성자가 동결한 두 full raw 예시를 test fixture로 복사했다. dataset 문항은 생성하거나 변경하지 않았다. 첫 예시의 수동 공급가는 350000원이며 VAT 35000원, 발행 공제 5005원, 납부액 29995원이다. 두 번째 예시의 현재 매입 공급가는 115000원이고 다음 기간 매입 200000원은 현재 신고에서 제외된다. 현재 매출 VAT 30000원에서 매입 VAT 11500원과 카드 공제 4290원을 차감한 납부액은 14210원이다. 두 예시의 전체 11답을 각각 대조했다.

신규 pytest 209개가 통과했다. 모든 가격 요소의 실제 변경과 전체 답, 문서 간 다른 행 표현, 독립된 동일 금액 거래, 원천 충돌, 실제 공급 기간, inclusive 상한, 무료 행, 배송과 문서 할인 경계, 전체 source 순열, deepcopy, 기존 활동 및 등록 제약, 은행 부모 및 배치 부모 연결을 검사했다. 기존 VAT 관련 검사를 함께 실행한 결과는 517개 통과이다. Ruff check와 format check도 통과했다.

기존 Batch 1 C300의 개별 집필 원천을 공개 registry로 다시 계산했다. 300개 모두 기존 projected gold와 full trace가 정확히 일치했다. 상세 체크와 gold 및 trace SHA는 `tmp/vat_itemized_activity_contract/legacy_C300.json`에 기록했다. 실제 PDF와 XLSX 및 HWPX 렌더링 통합과 공개 registry 새 분기 및 source catalog 연결은 root가 수행한다. 기존 VAT engine과 evidence interpreter 파일은 변경하지 않았다.
