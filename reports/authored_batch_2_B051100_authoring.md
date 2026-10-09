# Batch2 B051–B100 개별 집필 인계

최종 source SHA-256: `283884fb2b96695e7074f30f28fd188ebf8d6d477908e45cc8f4ab390bb3122f`

최종 목표는 Batch1과 Batch2 합계2,400문항이다. 이 원고는 Batch2 급여50문항만 담당하며 Batch3과 Batch4를 만들지 않았다.

50문항은 easy15, medium22, hard13이다. 원자료는 235개이며 PDF 99개, XLSX 70개, HWPX 66개다.

모든 원문은 literal JSON으로 한 문제씩 직접 작성했다. 이전 원고를 복제하거나 이름 및 금액을 바꿔 사례를 생성한 factory를 사용하지 않았다. 검증 스크립트는 source 생성 없이 이미 작성된 원고의 계산과 반사실 시험만 수행한다.

계약 계산, 문서 원자료 전체 coverage 및 실제50문항 렌더가 통과했다. 독립 check_chunk가 현재 source의 provenance, gold, schema, trace 및 실제 문서복원을 확인했고50/50을 통과했다. 최종 물리 자료는 `tmp/batch2_payroll_051100/rendered_closed/`다. 앞선 `rendered/`와 `rendered_final/`은 자체 교정 이전 자료라 최종 근거로 사용하지 않는다.

문항별 반사실50건 중 47건은 실제 요청 답안을 바꾸고3건은 정당한 제외 또는 중복 제거의 불변량을 확인한다. 제외 불변량은 B072 휴일 목록 중복, B091 미승인 밤 초안, B094 동일 은행 실행 사본이다. 수기로 계산한 15문항의 기대 필드를 실제 산출과 별도로 대조했다.

PDF B051의 고정수당, HWPX B052의 실행액 및 XLSX B094의 동일 실행 사본 두 셀을 실제 원문에서 수정했다. 세 형식 모두 원문복원 및 요청 답안이 바뀌었고 extraction_map, gold, trace, task.yaml은 바이트 그대로 유지됐다. PDF 첫 페이지 표본 B065, B088, B096에서 제목 및 원자료 행이 잘리지 않고 읽히는 것도 확인했다.

비교는 frozen 이전350문항의 메타데이터를 색인하고 각 새 문항의 가까운 업무 관계를 직접 선택하여75개 이전 whole object와 대조했다. 단순 텍스트 유사도 결과는 탐색용이며 의미 승인으로 사용하지 않았다. 각 문항의 이전 관계 두 개 및 chunk 안 최근접 관계와 최종 SHA를 comparisons.json에 기록했다. 같은 은행 wrapper를 썼다는 사실만으로 다양성을 승인하지 않는다.

자체 검토에서 B065의 기존 평일 카드 합산안, B069의 단일 고액 완료금안, B079의 경계 효과 없는 선지급안 및 B088의 B077 유사 노동절안을 폐기하고 각각 완전히 새 literal 원고로 다시 작성했다. B065는 같은 표시 시급과 다른 정확 단가, B069는 동일 과세액과 다른 통상임금의 불변량, B079는 반기 양쪽 지급일과 동일 보험월의 불변량, B088은 부분 부재 및 개근 유지와4인 밤 추가 대가의 관계다.

인사 확정 개근에서 부분 부재를 하루 전체 결근으로 확대하지 않는다. 마지막 지정 주휴일까지 재직 조건을 시급 종료 계약에 명시했다. 정규 지급집계에 이미 포함된 기본유급은 별도 지급하지 않는다. 같은 직원 및 보험월의 명세를 분할하지 않았고 은행 executed 날짜는 해당 명세의 유효 지급일과 정확히 일치한다. 사내 합성 처리 약정은 정부 규정으로 주장하지 않았다.

독립 의미 검토와 최종 승인 권한은 root에 있다. B070/B089의 승인 선택 및 날짜 합류, B072/B091의 달력 중복과 현재 실제근로, B086/B098의 휴무 기본유급 포함 위치는 특히 서로 가까운 관계로 표시했으며 독립 검토에서 부가 단계가 충분히 다른 업무 관계인지 판단해야 한다. 기술 검증 통과를 편집 승인이나 전문가 세무 검토 완료로 바꾸지 않았다.

근거 파일:

- `tmp/batch2_payroll_051100/technical_closed_check.json`
- `tmp/batch2_payroll_051100/counterfactuals.json`
- `tmp/batch2_payroll_051100/hand_arithmetic.json`
- `tmp/batch2_payroll_051100/physical_checks.json`
- `tmp/batch2_payroll_051100/comparisons.json`
- `tmp/batch2_payroll_051100/comparison_readset.json`

모델 API 호출 및 commit은0회다. 규칙 엔진, global report, acceptance ledger 및 다른 작업자의 파일은 변경하지 않았다.
