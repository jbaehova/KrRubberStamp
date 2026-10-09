# 일괄 은행 실행의 확정 분배 원천 계약

`vat_bank_batch_allocation_v1`은 가상 관리조직의 실제 세금 정산 은행 실행과 확정된 구성 지시 원본을 읽는다. 세금 계산은 기존 독립 신고 엔진이 담당한다. 납세자 사이의 법률상 상계와 미집행 수탁금의 납부 간주 및 수수료 매입 공제를 판단하지 않는다.

정확한 최상위 키는 source_contract, processing_policy, as_of_date, filings, bank_executions, allocation_instructions다. filings의1~3개 독립 납세자는 [독립 은행 대조 계약](vat_bank_reconciliation_contract.md)과 같은 전체 원천 및 형식과 범위를 따른다. 같은 납세자의 여러 지점 신고와 다른 부모 계약의 재귀 입력을 지원하지 않는다.

bank_executions는1~20개 원본이다. 각 행은 execution_id, date, status, direction, amount, bank_fee만 갖는다. status는 executed 또는 planned이고 direction은 debit 또는 credit이다. 금액은 bool을 허용하지 않는0이상 정수다. 환급 입금의 수수료는0이어야 한다. date는 정확한 ISO 날짜다.

allocation_instructions는1~60개 원본이다. 각 행은 instruction_id, execution_id, filing_id, registration_id, kind, amount만 갖는다. 구성 금액은 양의 정수이며 실행과 신고 및 등록번호 참조가 모두 맞아야 한다. 출금에는 settlement_payment 또는 assessed_prepayment만, 입금에는 settlement_refund만 연결한다. 같은 실행에 같은 신고의 여러 독립 구성 지시가 있어도 각 원금은 그대로 합산한다.

각 실행은 구성 지시를 하나 이상 갖고 은행 금액은 지시 원금 합계와 수수료의 합이어야 한다. 미분배 잔액을 추정하거나 수수료를 납세자 원금에 나눠 넣지 않는다. 실행 ID와 지시 ID의 중복은 같은 내용이어도 이 좁은 계약에서 거절한다. 사본 우선순위와 개정 원본 선택을 수행하지 않는다. 계획 및 미래 실행도 제외하기 전에 모든 형식과 참조 및 원금 보존을 검사한다.

기준일 안에 실제 실행한 구성 지시만 기존 납세자별 현금 대조로 전달한다. 예정고지 납부는 하위 신고에 이미 반영되어 정산 현금에서 다시 빼지 않는다. 은행 실행 상태와 날짜는 실행 원본에서 읽고 분배 지시에서 추정하지 않는다.

답에는 기존 filing_calculations, registration_settlements와 전체 합계를 유지하고 execution_reconciliations 및 bank_cash_totals를 추가한다. 실행별 원금은 정산 원금과 고지 원금으로 나눠 보고하며 계획 및 미래 실행도 원본 구성 값과 included=false를 보고한다. 은행 합계는 실제 기준일 안의 출금과 입금 및 수수료와 고지 원금을 따로 집계한다. settlement_net_outflow는 debit_total에서 credit_total과 fee_total 및 assessed_debit_total을 뺀 값으로 기존 paid_total에서 received_total을 뺀 값과 같다.

정수 산술과 원금 보존 및 신고별 잔액은 사적 장부 대조 규약이다. 새 정부 법률이나 법정 납부기한을 추가하지 않는다. trace에는 정렬한 실행 및 구성 지시와 기존 은행 대조 및 하위 신고 계산을 남긴다. 답과 trace 및 호출자 원본 사이의 가변 객체를 공유하지 않는다.

직접 쓴 두 전체 수기 예시와 엄격한 오류 및 보존 경계를 포함한 새31개 시험이 통과했다. PDF와 XLSX 및 HWPX 실제 분배 셀을 수정한3개 시험에서도 신고와 은행 실행 합계를 유지한 채 두 등록별 잔액이 각각5,000원 및-5,000원으로 바뀌었다. 추출 맵과 gold 및 trace 바이트는 유지했다. 테스트 예시는 `tests/fixtures/vat_batch_allocation.yaml`에 있고 공개 문항 수량을 생성하는 도구가 아니다. 공식 수치 예시가 없는 사적 규약이므로 verified는 false다.
