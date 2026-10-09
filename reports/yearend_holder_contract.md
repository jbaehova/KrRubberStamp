# Year-end rent contract holder evidence

A027의 월세 계약 명의 판단을 입력의 최종 bool에서 계약자 식별번호와 인적관계 자료의 대조로 바꿨다. 기존 `yearend_evidence_v1`에 optional 분기를 추가했으며 다른49문항과 Batch1의300개 연말정산 정답 및 trace는 그대로다.

## Bounded schema

`rent.contract_holder_person_id`와 `rent.identity_records`는 함께 제출해야 한다. 이 분기에서는 `eligible_contract_holder`를 입력할 수 없다. 명부는 비어 있지 않은 배열이며 각 행은 정확히 `person_id`, `name`, `relation`을 가진다. 각 값은 비어 있지 않은 문자열이고 식별번호는 중복될 수 없다.

관계 값은 `self`, `spouse`, `parent`, `child`, `grandchild`, `sibling`, `friend`, `housemate`, `colleague`, `unrelated`다. `self` 행은 식별번호도 `self`여야 하며 이름을 NFKC 정규화하고 공백을 제거한 뒤 대소문자를 통일해 직원 이름과 대조한다. 가족 행은 같은 식별번호와 관계를 가진 기존 `dependents` 자료에 연결해야 한다. 기존 `basic_eligible`의 소득과 나이 및 실제 부양과 공제 신청자 판단을 재사용한다. 외부인 행은 직원이나 부양가족의 식별번호를 사용할 수 없다.

계약자 번호가 명부에 없거나 관계가 충돌하면 계산을 거부한다. 원자료를 바꾸지 않고 내부 `rent.eligible_contract_holder`를 도출한다. 원래 계약자 번호와 명부는 trace의 inputs에 그대로 남는다. 새 분기가 있을 때만 derivation output에 `rent.eligible_contract_holder`를 추가한다.

## Official basis and boundary

[국세청 2025년 연말정산 신고안내](https://webtv.nts.go.kr/comm/nttFileDownload.do?fileKey=88c482e8d69eb1653515871654a4ab42)의 책자203쪽(PDF221쪽)은 2017년부터 근로자의 기본공제대상자가 체결한 임대차 계약도 월세 공제가 가능하다고 설명한다. 2026-10-09에 기존 공식 PDF의 해당 쪽을 재확인했다. 적용 귀속기간은2025-01-01부터2025-12-31이다. 기존 기본공제 판정에 연결되는 한정된 구조화 자료 대조이며 이름의 자유문장 해석이나 모든 가족 관계 및 주택 자격의 자동 검증을 주장하지 않는다. 합성 원자료 연결에 대한 독립 공식 수치 예시가 없어 기존 rule의 `verified: false`를 유지했다.

## A027 and counterfactual

계약서 PDF에는 계약자 번호 `friend`가 적힌다. 세대관계 HWPX에는 직원 `self`와 친구 `friend`의 이름 및 실제 관계가 있다. 급여 XLSX와 본인 보험료 PDF는 독립된 다른 사실을 제공한다. 최종 명의 적격 bool이나 명의 판정 완료 문구는 자료와 질문에서 제거했다. Medium의4개 문서와1개 실제 예외를 유지했다.

| 판정 | 원본 친구 계약 | 계약자 번호만 self로 변경 |
| --- | ---: | ---: |
| 월세 공제액 | 0 | 1,428,000 |
| 보험료 공제액 | 112,800 | 112,800 |
| 최종 소득세 | 3,547,200 | 2,119,200 |

월세 연840만원에 총급여5100만원의17%를 적용하는 금액은1,428,000원이다. 본인 보장성보험94만원의12%는112,800원으로 계약자 변경에 영향을 받지 않는다. 두 입력의 PDF와 XLSX 및 HWPX를 실제 렌더링하고 복원한 결과가 각 원자료와 정확히 일치했다.

## Verification

- `uv run pytest tests/test_yearend.py tests/test_yearend_evidence.py -q`: 113 passed. 자기 명의 정규화와 배우자 소득 및 부모 나이의 유효 조건을 검증했다. 친구 등의 외부인 분기와 unknown reference 및 duplicate identity와 관계 충돌 및 raw/compiled 공존 거부도 확인했다.
- `uv run ruff check rules/a_yearend/evidence.py tests/test_yearend_evidence.py scenarios/a_yearend.py`: passed.
- 50개 preview를 실제 생성했고 전체50개 validate가 통과했다. 난도는 easy15와 medium23 및 hard12다.
- A027 계약서 PDF를 시각 확인했다. 항목과 계약자 식별번호 및 월세 납부액이 잘리지 않고 읽힌다.
- source 배열의 문항 순서는 그대로다. A027만 변경됐으며 나머지49개 객체의 canonical SHA-256 map은 변경 전후 동일하다.
- 기존 Batch1 연말정산300개 `calculate`의 정답과 trace를 변경 전후 canonical byte SHA로 비교해 모두 일치했다. 기존 분기에는 새 trace outcome을 추가하지 않았다.

| 식별자 | SHA-256 |
| --- | --- |
| source file | `09c244c0eea326bb9d3029d5bc75dcbbb7a299b7e21ceab7d9b8dfe3b46d030b` |
| A027 authoring case | `8d65af945234c0698341a3487e9c4d2794b36e85253620775ada60655ef998e6` |
| A027 facts | `81a839cfefec741b0fb8de673cbb0ab5a5093d909bab6319e320acc7412b7267` |
| 나머지49개 canonical hash map | `0692431148ead26762b1532fc33063905e9a7fb1219adeb6ed1c68565798840e` |

최종 preview 경로는 `tmp/yearend_rent_holder_contract/rendered/A_yearend/B2_A027_8d65af94`다. 반사실의 실물 문서 경로는 `tmp/yearend_rent_holder_contract/counterfactual_self`다. 상세 로컬 증거는 ignored `tmp/yearend_rent_holder_contract/verification.json`과 `validation.json`에 보관했다. 위 값은 합성 입력의 엔진 회귀 결과이며 공식 수치 예시라고 주장하지 않는다.
