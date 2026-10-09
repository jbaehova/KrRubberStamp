# Batch 2 A001~A050와 B001~B050 독립 편집 감사

이 보고서는 완료 인계된 직접 집필100문항을 Batch 1 같은 분야600문항과 대조한 편집 결과다.100개 비교 행을 작성했고 100개 원고의 업무 요청과 사실 및 문서 배치를 읽었다. A027은 root의 원천 계약 명의 조인 재집필 인계 후 별도로 독립 확인했고 해당 중앙결론 노출 finding만 닫았다. 계산 검사를 의미 다양성 승인으로 바꾸지 않는다. 이 묶음은 **미해결 findings가 있어 accepted가 아니다**.

검토 원고는 연말정산 파일 최종 SHA `09c244c0eea326bb9d3029d5bc75dcbbb7a299b7e21ceab7d9b8dfe3b46d030b`와 급여 파일 SHA `ccc739afeab569e1f910de9802c618d20cde15ef14dcd5abb1c5bee115eece88`로 최종 확인했다. 연말 파일은 최초 SHA `7f77695b64ef95666434b1a8c00728b0a222cdffd069199d677d2b755a8d6ca7`에서 A027 한 객체만 바뀌었으며 나머지49개 객체의 개별 SHA는 인계와 같았다. 각 원고/가까운 기존 원고의 개별 SHA와 문서 선택 경로는 [비교 기록](audit_evidence/batch_2/AB001050/case_comparisons.json)에 있다.

## 핵심 findings

1. **High: 의미상 반복.** 아래 표의 `near_duplicate_high` 문항은 이름 또는 수치 및 표제만 바꾸거나 기존 완결 관계에 독립 정상 계산을 더했다. 예를 들어 B001과 Batch 1 B258은 gross/공제합계/net의 요청 필드까지 같고 B024와 B271은 높은3월 계획보다2월 실행을 먼저 선택하는 자료 관계가 같다. A005와 A116은 동일 학생 두 학부 증명을 연간900만원 한도로 합산하며 A010과 A204는 저축 자체 한도 이후 IRP 실제 납입을 합산한다. 직접 literal 집필 여부와 별개로 이 완결 관계를 재집필해야 한다. 원본 원고를 생성기로 만들었다고 단정하는 finding은 아니다.
2. **High: medium 문서 최소치 padding.** B016~B021과 B023~B024 및 B033~B038의 별도 보험 통지는 요청답에 전혀 관여하지 않는다.14문항 모두 보험 통지 그룹을 바꿔도 요청 답이 동일했다. 이 probe는 출력 의존성 확인이며 법적으로 완결된 보험 반사실이라는 주장은 아니다. 현재 보험 문서를 빼면 최소4개 업무 문서 조건이 흔들린다. 요청 필드에 보험 하나를 기계적으로 추가해 문항을 유지하지 말고 중심 업무에 실제 필요한 원자료 대조를 다시 직접 작성한다. [의존성 검사](audit_evidence/batch_2/AB001050/insurance_document_dependency.json)
3. **Medium: 형제 생계 요건 누락.** A038 및 A041은 형제의 실제 부양만 쓰고 주민등록상 동거 또는 적격 일시퇴거를 명시하지 않았다. 세법상 형제 생계 요건의 확인된 전제는 원자료에 추가해야 한다. A022 본문에는 함께 산다는 말이 있으나 사실 scope에는 없어 물리 자료에도 명시하는 것이 좋다. 이는 새 공제를 발명하라는 요청이 아니다.
4. **High: B009 저자 반사실의 계약시간 불일치.** 주18시간 약정과 세 실제6시간 카드, 합계18시간을 유지하면서 의무4일 중3일 출근으로 바꾸었다. 실제 일한 세 날만으로 소정18시간을 모두 채웠으므로 결근한 네 번째 날의 양의 소정시간을 설명하지 못한다. 주시간과 실제 카드를 함께 일관되게 다시 작성한 정상 CF 또는 카드별/의무별 새 대조가 필요하다. 계산기의 주휴0원 산출만으로 정상 CF라고 승인할 수 없다.
5. **Medium: 제목의 업무 판단이 자료에 없는 사례.** A035의 이전 표준 철회는 최종 itemized scalar와 scope 서술로만 주어진다. B037의 구형 달력 위험은 실제 구형 달력 증빙 없이 holiday_dates/public_holiday로 이미 지정된 제헌절 계산이다. 그 이력/달력 대조를 새 업무 차이라고 주장하려면 실제 원천 자료와 선택 계약을 갖추어야 한다.
6. **Closed: A027 중앙결론 노출.** 입력의 eligible_contract_holder:false를 제거하고 계약서의 계약자번호를 인적관계 명부와 조인하도록 root가 재집필했다. 새 case SHA `8d65af945234c0698341a3487e9c4d2794b36e85253620775ada60655ef998e6`에서 원자료와 self 변경 반사실을 독립 복원하고 재계산했다. unknown 계약자도 거절됐다. [수정 후 감사](audit_evidence/batch_2/AB001050/A027_post_rewrite.json). 이 finding만 닫으며 묶음의 의미 반복 및 문서 padding은 미해결이다.

기본 규칙 재사용은 허용한다. `distinct_relationship_identified`는 실제 원자료 또는 적용 단계의 차이를 설명할 수 있다는 기록이며 자동 통과나 전문가 승인이라는 뜻이 아니다. `borderline_relationship_review`의 A022와 B042는 기존 완결 구조의 축소 또는 다른 충족 근거라는 위험이 남아 root가 나란히 재검토해야 한다.

## 재계산과 법적 확인 범위

- 99개 기준안의 check_case와 원자료 field coverage 및 정답 재계산이 통과했다. 기존 저자가 저장한 정상/거절/의도 불변 반사실112건을 재현했고 재집필A027의 self 개입은 별도1건으로 재현했다. [기준안](audit_evidence/batch_2/AB001050/baseline_recalculation.json), [저자 CF 재계산](audit_evidence/batch_2/AB001050/counterfactual_recalculation.json)
- 추가15개의 직접 고른 개입으로 hard의 별도 예외 영향을 확인했다. B039 휴게 위치와 식사 제공은 각각 night 또는 taxable/net을 바꾼다. B043 보험 부과월은 유효 계획 지급일과 별도로 pension/net을 바꾼다. B050 밤 초안 승인과 완료금 제거는 각각 야간/휴일 및 총지급에 작용한다. B049 포함 flag만 바꾼 항목은 계산 의존성 probe로 기록했고 기본 집계 보정을 하지 않았으므로 정상 CF로 주장하지 않는다. [추가 검사](audit_evidence/batch_2/AB001050/additional_exception_checks.json)
- 저자 A 독립 산식9건의 정밀 문턱 및 지출별 소한도 내용을 원자료에 대조했다. 직접 구한 유리수/원단위 기대값44개를28문항에서 각각 확인했다. [직접 산식](audit_evidence/batch_2/AB001050/independent_worked_arithmetic.json). A027의17%/12% 산식은 수정 후 evidence에 별도로 있다. 물리 문서 변경 및 시각 QA는 인계 증거를 읽었고 root의 독립 물리 검수가 따로 진행 중이다. 이 감사가100문항 물리 문서 셀을 각각 직접 변조했다고 주장하지 않는다.
- 2025 귀속의 형제 생계 및 교육 한도는 국세청 [2025년 연말정산 신고안내](https://webtv.nts.go.kr/comm/nttFileDownload.do?fileKey=88c482e8d69eb1653515871654a4ab42)의 인적공제 생계 요건과 교육비 항목을 로컬 PDF에서 확인했다. web fetch는 파일 크기 한도로 실패하여 저자 인계 PDF를 읽었다. 다른 블로그나 세무 요약을 법적 근거로 사용하지 않았다.
- 2026년5월11일 시행 시점은 [국가법령정보센터 개정문](https://www.law.go.kr/lsInfoP.do?lsiSeq=285779&viewCls=lsRvsDocInfoR)에서 확인했다. 단시간 노동절 유급과 일반공휴일 요건의 차이는 [고용노동부 노동절 상담](https://1350.moel.go.kr/rtmview.do?id=1000323870) 및 [단시간 공휴일 산식 상담](https://1350.moel.go.kr/rtmview.do?id=1000323476)을 대조했다. 실제 개인 사건 전체의 적법성을 이 검사로 보증하지 않는다.

## 문항별 가까운 기존 사례와 수정 방향

| 문항 | 가까운 Batch 1 | 상태 | 실제 차이 또는 반복 이유 | 조치 |
| --- | --- | --- | --- | --- |
| A001 | [A109](../authored/batch_1/A_yearend/cases_104_153.json) | near_duplicate_high | 신용→직불 문턱 차감과 총급여/카드공제/과세표준이 같다. 3원 잔액과 절사 강조만 추가했다. | 같은 문턱을 또 계산하는 목적을 버리고 서로 다른 실제 거래 귀속을 확인하는 원자료 관계를 직접 새로 정한다. |
| A002 | [A018](../authored/batch_1/A_yearend/cases_004_053.json) | distinct_relationship_identified | 낮은 과세소득의 영 결정세액과 달리 지급 전액이 확인된 비과세라 과세 총급여 자체가 영이다. 실제 지방 기납부 누계는 국세 비율과 분리한다. | 비과세 종류는 확인된 범위라는 전제를 유지한다. |
| A003 | [A107](../authored/batch_1/A_yearend/cases_104_153.json) | near_duplicate_high | 같은 두 본인 전용기부와 독립 소액 구간이다. 80000원을100011원으로 바꾸어 절사를 강조했지만 영수증 연결 관계는 같다. | 한 기부의 두 독립 납부와 다른 기부의 납부자 귀속 등 합산 단위가 실제로 다른 원자료를 새로 작성한다. |
| A004 | [A016](../authored/batch_1/A_yearend/cases_004_053.json) | distinct_relationship_identified | 두 안경의 동일인 한도에 두 번째 영수증만의 보전금을 먼저 연결하여 총액 초과/순부담 미달을 구분한다. 기존은 안경 합산과 치료의 연결이다. | 보전 순서와 연간 사람별 제한을 유지한다. |
| A005 | [A116](../authored/batch_1/A_yearend/cases_104_153.json) | near_duplicate_high | 동일인 두 학부 증명→연간900만원 상한은 그대로다. 전과한 자녀를 동시재학 배우자로 바꾸었고 실제 학교 식별자도 없다. | 학교 수라는 서술 대신 학생/지급자/서류의 실제 귀속 조인이 달라지는 업무로 새로 작성한다. |
| A006 | [A117](../authored/batch_1/A_yearend/cases_104_153.json) | distinct_relationship_identified | 고액 정치의 구간 계산에 다른 본인 전용기부가 이어진다. 다만 기준안의 고향200000원은 잔여 소득에 제한되지 않아서 소득 잔여 조인 주장을 과장하면 안 된다. | 고향사랑에 남는 소득금액을 중심 판단이라고 주장하려면 실제 잔여 한도가 요청답에 작용하게 한다. |
| A007 | [A014](../authored/batch_1/A_yearend/cases_004_053.json) | distinct_relationship_identified | 기존 시장/교통 사례는 원시 공제 초과액이 제한하고 새 사례는 시장 자체의율환산108000원이 추가한도를 제한한다. 같은 법규칙 재사용이며 한도 단계의 제한 요소가 다르다. | 반사실과 산식에서 추가 대상 환산액이 제한하는 것을 명시한다. |
| A008 | [A063](../authored/batch_1/A_yearend/cases_054_103.json) | distinct_relationship_identified | 같은65세 이상 부모의 한도 없는 치료에 별도50만원 안경 제한이 함께 남는다. 경로우대70세와 의료65세를 같은 부모에 대조한다. | 각 제한은 요청 medical_credit에 작용한다. |
| A009 | [A103](../authored/batch_1/A_yearend/cases_054_103.json) | distinct_relationship_identified | 세액 영점은 공유하지만 과세표준도 영이며 공적연금 소득공제와 개인계좌 세액공제의 단계 차이를 직접 요청한다. | 계좌 공제 원액 증가/결정세액 불변을 보인다. |
| A010 | [A204](../authored/batch_1/A_yearend/cases_204_253.json) | near_duplicate_high | 기존도 저축 자체 한도를 넘고 IRP 납입 일부가 합산 한도에 남는다.11000000원/1원은 같은 관계의 수치 치환이다. | 계좌 납부의 실제 귀속이나 반납/이체를 지원하는 원자료 계약이 준비된 뒤 그 관계로 다시 집필한다. 현 계약 밖 반납을 임의 지원하지 않는다. |
| A011 | [A246](../authored/batch_1/A_yearend/cases_204_253.json) | distinct_relationship_identified | 기존의 종교 혼합 한도와 달리 적격 종교기부가 없어 선순위 특례 후 공익30%를 사용한다. 제한 공식 선택은 실제 다르다. | 종교 없음이 원자료 범위라는 전제를 유지한다. |
| A012 | [A055](../authored/batch_1/A_yearend/cases_054_103.json) | near_duplicate_high | 가족/지출 없는 급여에서 공제→산출세액→근로세액공제 한도를 요구한다.70000002원 정밀도 외 자료 연결과 업무는 같다. | 원단위 경계값만 바꾸지 말고 급여 원자료의 다른 귀속/정정 관계를 직접 설계한다. |
| A013 | [A105](../authored/batch_1/A_yearend/cases_104_153.json) | distinct_relationship_identified | 기존은 직원 한 사람에게 고령/장애 중첩이다. 새 원고는 직원 장애와 두 부모의 나이별 경로우대를 서로 다른 인적기록에 연결한다. | 부모70/69와 직원 장애의 적용 대상을 분리한다. |
| A014 | [A007](../authored/batch_1/A_yearend/cases_004_053.json) | near_duplicate_high | 직원 본인 대학원 무한도에 정상 학부 영수증 하나를 더했다. 모든 서류가 같은 무한도 자기 교육이라 새 선택 관계가 없다. | 동일인의 기관 문구보다 실제 부담자나 적격 기관 관계가 결론을 바꾸는 증빙을 직접 설계한다. |
| A015 | [A093](../authored/batch_1/A_yearend/cases_054_103.json) | distinct_relationship_identified | 고액 정상순서와 달리 정치가 근로소득 거의 전부를 먼저 소비해 고향 소액 구간 자체를5원 잔여 소득으로 제한한다. 이 제한은4원 요청답과 의도 불변 정치 절사에 보인다. | 작은 잔여소득/전용 공제 영점/실제 결정세액을 구분한다. |
| A016 | [A095](../authored/batch_1/A_yearend/cases_054_103.json) | distinct_relationship_identified | 기존 보전은 일반 진료다. 새 원고는 고율 난임 영수증에만 보전금을 연결하고 일반 진료부터 문턱을 차감한다. | 난임의 보전과 고율을 같은 영수증에 유지한다. |
| A017 | [A028](../authored/batch_1/A_yearend/cases_004_053.json) | distinct_relationship_identified | 두 조리원은 한 출산으로 묶고 쌍둥이는 두 사람으로 등록한다. 별도 미용 제외가 의료비에 작용한다. 출산 사건 수와 신생아 수의 조인이 다르다. | 쌍둥이 수가 조리원 제한을 두 번 만들지 않는 근거를 유지한다. |
| A018 | [A181](../authored/batch_1/A_yearend/cases_154_203.json) | distinct_relationship_identified | 전용보험 상품/피보험자 자격과 유사하나 적격 재활기관과 비장애 학생을 교육비 경로로 조인하고 정상 학교비는 남긴다. | 적격 기관과 학생 자격을 구분한 현재 관계를 유지한다. |
| A019 | [A152](../authored/batch_1/A_yearend/cases_104_153.json) | distinct_relationship_identified | 넓은 주택의 대체 가격 요건을 먼저 충족시킨 후 동일 계약 두 납부의 퇴직일 포함 여부를 가른다. 기존 기간 경계는 다른 주택/배우자 자료 조합이다. | 면적은 부적격 예외가 아니라 충족된 대체 요건이라고 명시한다. |
| A020 | [A141](../authored/batch_1/A_yearend/cases_104_153.json) | distinct_relationship_identified | 혼합소득 자녀의 카드 제외는 공유하지만 기존의 본인 학교비 대신 같은 자녀의 의료비가 소득요건 예외로 남는다. 동일인의 두 경로가 반대다. | 급여420만원/확정 혼합소득141만원의 정합성을 유지한다. |
| A021 | [A234](../authored/batch_1/A_yearend/cases_204_253.json) | distinct_relationship_identified | 나이 미달 부모 한 명의 보험/진료와 달리 두 부모의 같은 보험 유형을59/60세로 나눠 한 명만 합산한다. 사람별 피보험자 귀속을 유지한다. | 두 보험이 실제 서로 다른 피보험자임을 유지한다. |
| A022 | [A294](../authored/batch_1/A_yearend/cases_254_300.json) | borderline_relationship_review | 형제 보험 인정/카드 제외는 기존 장애인 동생에게도 있었다. 현재는19세 비장애 동생이고 교육/회사부담을 제거했다. 가족 자격의 충족 근거만 바뀐 축소형이라는 위험이 남는다. | 동거 사실을 사실문서에도 명시하고 기존과 다른 실제 원자료 연결의 필요성을 root가 재검토한다. |
| A023 | [A270](../authored/batch_1/A_yearend/cases_254_300.json) | near_duplicate_high | 같은 세대 배우자 두 번째 주택→대출 이자 제외가 같다. 정상 공적연금을 정상 본인 학부비로 바꾸었지만 중심 주택 조인은 변하지 않았다. | 소유자 변경만으로 새 문제라 주장하지 말고 주택 자료와 이자 지급의 실제 다른 연결을 직접 작성한다. |
| A024 | [A029](../authored/batch_1/A_yearend/cases_004_053.json) | near_duplicate_high | 10년 거치 변동 대출의 불인정이 같고 별도 정상 의무보험만 더했다. 급여/대출 계약/보험의 독립 산술을 새 관계로 인정하기 어렵다. | 계약 기간이나 금리 금액 치환을 중단하고 실제 날짜/상환 증빙 관계를 직접 설계한다. |
| A025 | [A284](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 재직 후 의료 제외는 공유하지만 고율 미숙아 비용의 기간 제외와7세 아이의 일반 진료 및 출생 공제를 같은 가족 등록에 연결한다. | 고율이 기간 제외를 이기지 않는 점이 요청답에 남는다. |
| A026 | [A258](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 같은 대학생 두 학기와 달리 동일 학생의 고교/대학 학교급 전환을300만원 소한도 후 연간900만원으로 처리한다.870만원 인정액에 실제 학교급 조인이 작용한다. | 학교급 소한도와 연간 상한 순서를 유지한다. |
| A027 | [A019](../authored/batch_1/A_yearend/cases_004_053.json) | distinct_relationship_identified | root 재집필 후 계약서의 계약자번호와 인적명부 ID/관계를 조인한다. 기존 주소 대조와 다른 원자료 연결이며 입력의 명의 적격bool을 제거했다. | 명의 누출 finding만 닫았다. self 변경은 월세1428000원/보험112800원 불변을 보이며 다른 findings는 열려 있다. |
| A028 | [A273](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 관리비 제외는 공유하지만 신용 관리비 때문에25% 문턱 소비가 직불로 넘어가는 원자료 위치를 특정한다. 단순 공제율 차감으로 해결되지 않는다. | 청구 항목과 결제 수단의 두 경로를 유지한다. |
| A029 | [A179](../authored/batch_1/A_yearend/cases_154_203.json) | distinct_relationship_identified | 미용의 의료 제외/카드 유지에 치료와 같은 금액의 다른 결제수단을 대응한다. 금액 동일성이 거래 동일성을 대신하지 않는다. | 두 진료와 세 카드의 대응을 날짜/수단으로 독자가 확인할 수 있게 유지한다. |
| A030 | [A187](../authored/batch_1/A_yearend/cases_154_203.json) | distinct_relationship_identified | 학교/학원 구분은 공유하지만 학원 결제가 카드 소비에도 실제 남아 교육비 제외를 카드에 복제하면 틀린다. | 학교 송금과 직불 학원 소비의 대응을 유지한다. |
| A031 | [A271](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 같은 법인 ID가 공익 지정 종료와 종교 지정 시작을 가지며 공백 하루만 제외된다. 기존은 같은 종류의 지정 재개다. | 유효 기간과 종류를 함께 조인해야 한다. |
| A032 | [A239](../authored/batch_1/A_yearend/cases_204_253.json) | near_duplicate_high | 다른 형제 배정 부모의 공익기부 제외는 같다. 요청을 본인 정치 정상공제와 묶었지만 부모 배정/지출 조인은 그대로다. | 정상 정치기부를 장식처럼 덧붙이지 말고 원자료 귀속을 확인해야 하는 새로운 관계를 작성한다. |
| A033 | [A177](../authored/batch_1/A_yearend/cases_154_203.json) | near_duplicate_high | 퇴직일/다음날 주택이자 기간 선택이 같고 별도 정상 사회보험은 독립 계산이다. 보험 종류와 납부액을 바꿔도 중심 기간 조인은 같다. | 퇴직 경계의 금액/날짜 치환 외에 지급별 다른 출처 연결 관계를 직접 작성한다. |
| A034 | [A074](../authored/batch_1/A_yearend/cases_054_103.json) | near_duplicate_high | 같은 적격자의 회사 부담 보험 제외와 직원 부담 보험 인정이 같다. 피보험자를 자녀로 바꾸고 정상 IRP를 더했다. | 납부자의 원천 지급 자료가 실제 선택을 바꾸는 구조를 지원한 뒤 그 문제를 작성한다. |
| A035 | [A260](../authored/batch_1/A_yearend/cases_254_300.json) | near_duplicate_high | 최종 특별 신청의 소액 보험 공제를 임의 표준으로 바꾸지 않는 문제는 이미 있다. 이전 표준 철회는 scope 서술뿐이고 이력 자료가 없다. 정상 고향기부가 더해졌다. | 선택 변경을 업무로 삼으려면 실제 신청 이력/확정 상태를 조인하도록 원자료 계약을 준비하고 재집필한다. |
| A036 | [A293](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 기존 고소득 장애 부모와 달리 무소득 장애 부모가 인적공제는 인정되지만 관계 때문에 일반 학부만 불인정되고 특수교육은 남는다. 제외 사유의 적용 단계가 다르다. | 소득으로 학부를 제외했다고 설명하지 않는다. |
| A037 | [A289](../authored/batch_1/A_yearend/cases_254_300.json) | near_duplicate_high | 두 자녀의 근로소득만 있는500만원 경계와 각각의 보험 귀속은 같다. 장학금/의료를 빼고 경계를1원으로 옮긴 축소형이다. | 1원 경계 대신 두 소득자료의 실제 귀속/확정 관계가 필요한 문제를 새로 작성한다. |
| A038 | [A072](../authored/batch_1/A_yearend/cases_054_103.json) | distinct_relationship_identified | 고령 형의 가족 대학원 제외에 같은 사람의65세 이상 의료 한도 예외를 결합하고70세 경로우대는 아직 없다. | 주민등록상 동거 또는 적격 일시퇴거라는 생계 요건을 원자료에 명시한다. |
| A039 | [A095](../authored/batch_1/A_yearend/cases_054_103.json) | distinct_relationship_identified | 보전은 배우자 일반진료에 대응하며 한도보다 작게 낮아지고 본인 일반/난임으로 이어진다. 별도 미용 제외도 요청 medical_credit를 바꾼다. | 배우자 한도와 고율 진료의 연속 문턱을 구분한다. |
| A040 | [A276](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 기존 두 장애 학생의 학부/특수교육과 달리 한 학생의 고교→대학 전환 및 특수교육이고 장학금/회사부담이 서로 다른 납부다. | 회사부담 확인 한 필드 문서를 실제 원천 지급확인과 연결할 수 있는지도 검토한다. |
| A041 | [A277](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 독립 아버지 제외와 인정 어머니 및 미성년 동생을 합쳐 동생 보험은 인정/카드는 제외한다. 부양 및 관계가 서로 다른 경로로 작용한다. | 동생의 동거/적격 일시퇴거 전제를 원자료에 명시한다. |
| A042 | [A251](../authored/batch_1/A_yearend/cases_204_253.json) | distinct_relationship_identified | 종합 한도는 공유하지만 기준안은 합산 한도 직전이다. 관리비 복원과 퇴직 후 교통 복원이 서로 다른 추가 한도/초과액 관계를 만든다. 중간답을 모두 요청했다. | 최종 과세표준 불변과 중간 공제/한도 초과액 변화를 혼동하지 않는다. |
| A043 | [A292](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 세대주 신청 월세 제외를 두 아이별 최종 부부 배정과 연결하여 자녀/학교 공제의 다른 사람별 귀속을 묻는다. 기존 회사부담 본인 학비와 다른 연결이다. | 월세와 아이 배정은 독립된 operative 예외다. |
| A044 | [A291](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 종료한 큰 종교기부를 제거하면 종교 혼합 한도식 자체가 사라진다. 다른 배정 부모 기부는 별도 제외라 한도식 선택과 가족 귀속의 두 단계다. | 지정종료 CF에서 실제 한도식 변경을 기록한다. |
| A045 | [A145](../authored/batch_1/A_yearend/cases_104_153.json) | distinct_relationship_identified | 무소득 장애 손녀 인적공제와 첫 자녀 출생을 다른 세대층으로 연결한다. 손녀 대학원과 회사 치료비를 각각 제외하고 보험/미숙아는 남긴다. | 성인 손녀와 직원 첫 자녀의 출생 순위를 구분한다. |
| A046 | [A293](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 장애 부모의 소득 예외는 공유하지만 다른 무소득 자녀의 회사부담 학교비가 두 번째 제외다. 부모 소득 변경은 특수교육/의료를 유지한다. | 두 사람의 비용 귀속을 유지한다. |
| A047 | [A194](../authored/batch_1/A_yearend/cases_154_203.json) | distinct_relationship_identified | 기존 단일 다른배정 부모의 의료/기부와 달리 두 부모별 카드/기부를 배정하고 인정 어머니의 종교기부만 지정종료로 제외한다. | 가족 배정과 기관 지정의 상이한 키를 유지한다. |
| A048 | [A295](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 같은 출산의 두 조리원이 아니라 같은 해 두 출산 사건이므로 출산별 상한이 둘이다. 본인 안경만 보전되고 배우자 안경은 별도 개인 한도다. | 두 출산 사건과 두 사람 안경을 서로 다른 합산 단위로 유지한다. |
| A049 | [A288](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 같은 쌍둥이 출산의 아이별 최종 배정이 출생순위/보험/미숙아에 동시 작용한다. 정상 배정 첫 자녀의 미용 제외는 독립이다. | 둘째/셋째 배정을 출산 한 사건으로 일괄 처리하지 않는다. |
| A050 | [A290](../authored/batch_1/A_yearend/cases_254_300.json) | distinct_relationship_identified | 관리비/미용 제외는 공유하지만 적격 월세가 실제 남고 소득공제로 낮아진 과세표준과 총급여 의료 문턱을 대조한다. 기존은 큰 주택이자 종합한도 문제다. | 의료 문턱과 월세율은 과세표준 감소에 따라 다시 계산하지 않는다. |
| B001 | [B258](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 정액 지급→공단/세무 공제→은행 실지급의 요청 세 필드까지 같다. | 실제 은행 지급 건과 급여 항목 귀속을 대조하는 원자료 관계가 필요하다. |
| B002 | [B267](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 현금 식대의 비과세/과세 계정 분리다. 계정 명칭과 금액 변경 외 새 원자료 관계가 없다. | 식사 제공 자료의 실제 직원/효력 귀속을 대조하는 계약을 준비한 뒤 직접 작성한다. |
| B003 | [B064](../authored/batch_1/B_payroll/cases_054_103.json) | near_duplicate_high | 정액 수당 합산 분자÷월 제수→표시 시급이다. 수당과 회사명만 다르다. | 계약 변경 자료의 실제 유효 시점/항목 연결을 대조하도록 새로 작성한다. |
| B004 | [B160](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 기초 급여/가족 등록을 표에 연결하고 국세→지방세를 요구한다. 정상 자녀 한 명은 기존 정상 가족공제 범위다. | 최종 가족 승인 원자료와 급여 지급건의 실제 연결이 필요한 업무를 작성한다. |
| B005 | [B266](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 별도 건강 통지→건강 부담→요양 부담이다. 건강/요양 요청도 같다. | 같은 공식의 금액을 바꾸지 말고 통지 식별자/확정 이력을 실제 대조한다. |
| B006 | [B156](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 기관별 서로 다른 통지 기준을 세 보험에 대응한다. 정상 가입/한도 미적용은 같다. | 기관 원자료의 다른 직원/부과월을 실제 선택하는 조인이 필요하다. |
| B007 | [B259](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 월급 포함 소정 저녁 카드→별도 야간 가산만 지급이다. 시각/휴게 변경 외 판단 관계가 없다. | 소정 승인과 실제 시간 기록의 원천 연결을 바꾸는 업무를 직접 작성한다. |
| B008 | [B205](../authored/batch_1/B_payroll/cases_204_253.json) | near_duplicate_high | 한 평일 추가 카드의 시간과 월 통상시급을 연결하는 한 줄 수당이다. | 날짜/시각 길이 변경 외 승인 자료의 귀속 판단을 필요하게 새로 작성한다. |
| B009 | [B157](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 세6시간 소정 카드→한 주 개근 비례 주휴다. 시급/주시간/업종만 바뀐다. | 기존 완결 관계를 다시 쓰지 말고 근태 원천과 계약 의무의 다른 연결을 설계한다. |
| B010 | [B125](../authored/batch_1/B_payroll/cases_104_153.json) | near_duplicate_high | 토요일 무급휴무와 일요일 주휴 지정→토요일 추가를 연장으로 지급한다. | 휴일 원자료의 실제 다른 귀속/중복 관계를 설계한다. |
| B011 | [B161](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 월급 포함 주휴 기본 대가와 실제 일요일 출동 별도 휴일 대가다. | 기존 단일 출동의 날짜/물품 교체를 중단하고 실제 다른 승인 연결을 작성한다. |
| B012 | [B013](../authored/batch_1/B_payroll/cases_004_053.json) | near_duplicate_high | 정액 월급 포함 주휴를 별도 주휴로 다시 지급하지 않는 관계다. | 포함 여부가 실제 원천 계약/지급항목 대조에서 결정되도록 새로 작성한다. |
| B013 | [B118](../authored/batch_1/B_payroll/cases_104_153.json) | near_duplicate_high | 식대는 지급 합계에 넣고 과세합계에서 법정금액을 제외한다. B2 B002의 동일 근거를 결과 필드만 바꾸었다. | 계정 출력 칸 추가가 아닌 원자료 대조 관계를 바꾼다. |
| B014 | [B265](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 단일 은행 실행일과 공제 후 금액을 등록한다. 요청 날짜/실지급도 같다. | 실행 건과 대상 급여 귀속을 서로 다른 ID 자료에서 확인하게 새로 작성한다. |
| B015 | [B154](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 15시간 미만 시급 계약의 실제 소정 카드를 무급휴게 제거 후 합산한다. 카드 수와 금액 외 관계가 같다. | 승인 카드와 계약 범위의 다른 원천 연결이 필요하다. |
| B016 | [B280](../authored/batch_1/B_payroll/cases_254_300.json) | distinct_relationship_identified | 같은 시각의 최종 소정 분류는 추가 대가를 없애지만 야간은 유지한다. 기존은 소정→추가로 기본 대가가 생기며 야간 불변을 요청하지 않았다. | 최종 category와 불변 야간의 두 필드를 유지한다. |
| B017 | [B282](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 같은 승인 record_id/revision/시각의 두 사본→한 번의 연장과 야간이다. | 같은 ID 복제 사례를 다시 쓰지 말고 다른 원자료 식별 관계를 직접 설계한다. |
| B018 | [B240](../authored/batch_1/B_payroll/cases_204_253.json) | near_duplicate_high | 승인 낮 출동과 미승인 밤 초안→밤 제외다. 요청 수당/야간/총지급과 상태 선택이 같다. | 단순 밤 초안 길이 교체 외 실제 귀속 판단을 새로 작성한다. |
| B019 | [B235](../authored/batch_1/B_payroll/cases_204_253.json) | near_duplicate_high | 22시 경계에 걸친 휴게를 전체 추가시간과 야간 교집합에서 각각 뺀다. | 휴게 시각 교체 외 새로운 승인/원천 연결을 직접 작성한다. |
| B020 | [B131](../authored/batch_1/B_payroll/cases_104_153.json) | near_duplicate_high | 배식+현금 식대→비과세 제거/과세/원천세다. | 배식 대상과 지급 직원의 원자료 귀속 등 다른 실제 대조가 필요하다. |
| B021 | [B255](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 변동 완료금은 gross에 넣지만 통상 분자에서 빼고 추가 카드 단가를 계산한다. | 성과금의 증빙 귀속/확정 관계를 직접 새로 작성한다. |
| B022 | [B033](../authored/batch_1/B_payroll/cases_004_053.json) | near_duplicate_high | 80%를 국세에 적용하고 다른 공제는 유지하여 실지급을 바꾼다. | 선택 신청 원자료의 최종 귀속이 필요한 관계를 준비한 뒤 다시 쓴다. |
| B023 | [B034](../authored/batch_1/B_payroll/cases_004_053.json) | near_duplicate_high | 자녀공제 후120%와 지방세를 계산한다. 수치/자녀 수외 연결이 같다. | 가족 및 신청 자료의 실제 다른 식별 관계를 직접 작성한다. |
| B024 | [B271](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 높은3월 approved보다2월 executed 우선→2월 자녀 기준이다. | 동일 실행/계획 골격의 날짜 치환을 중단하고 다른 지급 귀속 관계를 작성한다. |
| B025 | [B171](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 실행 없음→취소된 높은 revision 제외→유효approved 선택이다. 날짜를12월 안에서 옮긴 것이 차이다. | 다른 급여 건의 원자료 식별/승인 관계를 실제 구분하게 작성한다. |
| B026 | [B239](../authored/batch_1/B_payroll/cases_204_253.json) | near_duplicate_high | 7월 실행과6월 부과월 분리는 이미 있다. 하한을 상한으로 바꾸어도 원자료 키/선택/공제 경로는 같다. B129에도6월 고액 보험/7월 계획이 있다. | 부과월과 실행일 이외 다른 원자료 대조 관계를 직접 작성한다. |
| B027 | [B278](../authored/batch_1/B_payroll/cases_254_300.json) | near_duplicate_high | 취득월 연금 신청 true/건강 false→요양0원이다. 월급 계약으로 바꿔도 기관 상태 조인은 같다. | 기관 회신의 실제 대상/확정 이력을 조인하는 업무를 작성한다. |
| B028 | [B075](../authored/batch_1/B_payroll/cases_054_103.json) | near_duplicate_high | 연금 종료와 건강/고용 계속 부과의 기관별 선택이다. | 연령/금액 치환 대신 원천 통지 식별자를 실제 대조한다. |
| B029 | [B029](../authored/batch_1/B_payroll/cases_004_053.json) | near_duplicate_high | 66세 신규채용의 연금/고용 미부과와 건강/요양 유지다. 기존 동일 연령/상태 판정이다. | 같은 연령조건으로 새 사례를 만들지 말고 자격 원천과 지급건의 실제 다른 연결을 쓴다. |
| B030 | [B079](../authored/batch_1/B_payroll/cases_054_103.json) | near_duplicate_high | 하반기 낮은 연금 통지의 하한 적용이다. | 통지의 실제 직원/기간 귀속을 새로 대조하게 한다. |
| B031 | [B177](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 건강 상한을 먼저 적용하고 그 공제에서 요양을 산출한다. | 금액 이동 외 유효 보험 통지의 원자료 연결을 바꾼다. |
| B032 | [B179](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 하반기 상한 초과 연금 신고액→상한 기초와 부담액이다. | 상한금액을 넘긴 숫자 치환이 아닌 원천 통지 선택을 새로 쓴다. |
| B033 | [B238](../authored/batch_1/B_payroll/cases_204_253.json) | near_duplicate_high | 한 결근→실제 기본근로 감소와 그 주 주휴 탈락의 두 경로다. | 같은 결근 사례의 근무일 수를 줄이지 말고 계약 의무와 출근의 새로운 관계를 설계한다. |
| B034 | [B176](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 정확히15시간/세5시간 카드/개근→기본과 주휴다. B2 B009도 같은 양의 주휴 구조다. | 기존15시간 경계의 시급만 교체하지 않는다. |
| B035 | [B236](../authored/batch_1/B_payroll/cases_204_253.json) | near_duplicate_high | 14시간 계약 개근→기본만 있고 주휴0원이다. raw 카드 복원은 B154에도 있다. | 기존14시간 숫자/카드 길이 치환 대신 의무 원천 대조 관계를 새로 작성한다. |
| B036 | [B245](../authored/batch_1/B_payroll/cases_204_253.json) | near_duplicate_high | 주12시간에서 근로자의 날 유급/주휴 미적용이다. 인원4→8은 노동절 결론을 바꾸지 않는다. | 기관/근무목적 변경 아닌 실제 유급 원천 관계를 새로 작성한다. |
| B037 | [B226](../authored/batch_1/B_payroll/cases_204_253.json) | near_duplicate_high | 시급 실근로/공휴일 기본유급을 다른 층으로 계산한다. 제헌절은 새로운 날짜이나 입력에 holiday_dates와public_holiday가 이미 주어져 달력 충돌 선택 문제는 아니다. | 오래된 달력과 현행 달력을 업무로 삼으려면 실제 두 출처와 유효일 대조를 넣는다. 단순 날짜 교체라면 재집필한다. |
| B038 | [B188](../authored/batch_1/B_payroll/cases_154_203.json) | near_duplicate_high | 동일 휴일의 분할 카드 합계가8시간을 넘겨 하루 합산 가산이다. 두 카드 수/시각만 다르다. | 동일 일별 합산 골격 외 자료 귀속 관계를 직접 작성한다. |
| B039 | [B244](../authored/batch_1/B_payroll/cases_204_253.json) | distinct_relationship_identified | 동일 카드의 최종 category 변경은 추가 대가를 없애고 같은 길이 휴게 이동은 야간만 바꾼다. 배식 과세까지 실제 지급으로 연결한다. | 세 예외 각각의 변화/불변 증거를 유지한다. |
| B040 | [B287](../authored/batch_1/B_payroll/cases_254_300.json) | distinct_relationship_identified | 같은 공휴일 기본유급은 이미 기본 집계에 포함되어 추가0원이고 실제 두 소집은 하루8시간 초과를 만든다. 기존은 미포함 기본유급을 따로 지급한다. | 기본유급 포함 여부를 바꾸는 CF에는 실제 기본 집계도 함께 바꾼다. |
| B041 | [B192](../authored/batch_1/B_payroll/cases_154_203.json) | distinct_relationship_identified | 최종 소정 휴게 감소가 기본근로만 바꾸고 결근 주 주휴 판정은 그대로이며 시간 밖 실적금이 gross/net에 더해진다. | 휴게/결근/실적의 각 요청답을 보인다. |
| B042 | [B294](../authored/batch_1/B_payroll/cases_254_300.json) | borderline_relationship_review | 공휴일 소정 입력을 추가로 정정하고 야간 휴게를 대조하는 관계는 기존에 있다. 새 원고는 월급/8시간 이하이며 같은 길이 휴게 이동과 제헌절을 사용한다. | 날짜/휴게/월급 기반 차이만으로 새 관계라 승인하지 말고 기존 전체 원자료와 나란히 재검토한다. |
| B043 | [B295](../authored/batch_1/B_payroll/cases_254_300.json) | distinct_relationship_identified | 실행 전 최고 취소 계획을 버린 유효 지급일과 다른6월 보험 상한을 분리하고 두 자녀의 해당 지급일 기준으로 실제 자금 소요를 정한다. 기존 고액경계 중심과 다르다. | 날짜 변경은 date 요청에 나타나며 보험 부과 CF도 따로 기록한다. |
| B044 | [B076](../authored/batch_1/B_payroll/cases_054_103.json) | distinct_relationship_identified | 취득월 기관별 부과에 높은7월 계획보다6월 실행 우선의 다른 자료 관계를 함께 둔다. 실행 상태 CF는 날짜만 바꾸고 동일 보험 월은 유지한다. | 지급일과 기관 회신은 독립이며 일괄 취득월 미부과라고 하지 않는다. |
| B045 | [B286](../authored/batch_1/B_payroll/cases_254_300.json) | distinct_relationship_identified | 식대 초과/완료금이 과세 표행을 정하고 지급일 자녀→80%→부징수0원이 이어진다. taxable_pay가 요청돼 상한에 가려진 금액 차이도 보인다. | 변경 과세액에 해당하는 공식 표 행도 CF 증빙에 맞춘다. |
| B046 | [B292](../authored/batch_1/B_payroll/cases_254_300.json) | distinct_relationship_identified | 4인 사업장 동일 사실이 노동절 기본유급 유지/일반공휴일 유급 제외/실제 밤 법정가산 제외에 서로 다르게 작용한다. 실제 노동절 밤 작업이 있다. | 5인 CF에서 원래근로의무일과 공휴일 약정도 함께 일관되게 유지한다. |
| B047 | [B185](../authored/batch_1/B_payroll/cases_154_203.json) | distinct_relationship_identified | 실적금 지급/통상단가 분리에 건강 통지 하한→요양→net가 붙는다. 같은 완료금 증액이 보험 통지 자체를 자동 올리지 않는다. | 건강 하한 CF를 실적금 CF와 분리한다. |
| B048 | [B247](../authored/batch_1/B_payroll/cases_204_253.json) | distinct_relationship_identified | 배식 현금식대 과세 및 완료금 제외 통상분자와 정확히1000만원 과세를 함께 요청하고13가족/4자녀/80%가 이어진다. 기존 큰 완료금/가족 확장과 제한 지점이 다르다. | 통상분자와 과세액을 각각 요청해 급식/완료금 차이를 보인다. |
| B049 | [B224](../authored/batch_1/B_payroll/cases_204_253.json) | distinct_relationship_identified | 소정/추가 야간 분리 자체는 공유하지만 선거일 기본유급을 세 번째 층으로 두고 실제 공휴일 추가는 holiday로, 정규는 base로 보낸다. | 유급 포함 CF는 기본근로 집계도 함께 보정해야 유효하다. |
| B050 | [B049](../authored/batch_1/B_payroll/cases_004_053.json) | distinct_relationship_identified | 첫날은 최종 휴게가8시간 경계를 바꾸고 둘째날은 다른ID 미승인 밤 초안이 야간0원 여부를 바꾼다. 완료금은 시간 단가와 분리되어 실제 지급에만 더한다. | revision 선택과 draft 제외를 각각 다른 개입으로 보인다. |

## 종료 인계

원고 및 엔진은 수정하지 않았다. 감사 소유 파일의 write lock은 root에 반환한다. 미해결 findings 해결 전에는 이 보고서를 Batch 2 accepted 승인으로 쓰지 않는다. 집필된 항목을 저장하고 비교 기록을 만드는 script의 반복은 원고 생성 반복이 아니다.
