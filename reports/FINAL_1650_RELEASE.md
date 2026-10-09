# KrRubberStamp 최종 1,650문항 공개

[Hugging Face 데이터셋](https://huggingface.co/datasets/jbaehova/KrRubberStamp-1.65K)과 [GitHub 프로젝트](https://github.com/jbaehova/KrRubberStamp)를 공개했다. Batch1의1,200문항에 Batch2의 A100 및 B100과 C100 및 D150을 추가하여 정확히1,650문항으로 마감했다. 최종 분야 수는 연말정산400 및 급여400과 부가세400 및 문서 추출450이다. 난이도는 easy495 및 medium743과 hard412다. 추가 배치는 없다.

## 검증

- 두 배치 모두 실제 입력 문서 복원과 정답 및 전체 계산 trace 검증을 통과했다.
- 요청 답안18,001필드에서 oracle100% 및 null0%다. 실제 모델 성능 점수가 아니며 모델 API 호출은0회다.
- 로컬 테스트1,532개와 Ruff를 통과했다. [최종 데이터 커밋의 GitHub 검사](https://github.com/jbaehova/KrRubberStamp/actions/runs/37901331218)도 성공했다.
- Hugging Face Datasets로 오프라인1,650행과 참조 경로16,343건을 확인했다. 게시한 기본 config도 실제 Hub에서1,650행을 읽었다.
- Hugging Face 공개 파일15,167개 전체 목록을 대조했다. 고정 revision에서 데이터카드와 JSONL 및 양 배치 manifest, 배치와 분야 및 형식별 문서29개와 설치 패키지 보고서를 내려받아35개 파일의 바이트를 확인했다. 모든 공개 파일의 바이트를 원격에서 각각 내려받았다고 주장하지 않는다.
- 분리 설치한 wheel도 전체1,650원고 및 답안과 trace 및18,001필드가 일치했다. 실제 PDF 및 XLSX와 HWPX 원본 변경6개 및 설치 CLI 검증을 통과했다.

사람 전문가 검수120문항은 별도 대기다. 규칙 출처78개 중 공식 수치 검증30개와 미검증48개를 구분한다. 계산 적용 범위와 실제 국고 현금의 끝수 처리는 DATA_SPEC을 따른다.

## 공개 자료 식별자

- Hugging Face revision: `f00e4e9e652499296f4283203e53b329f671b969`
- 전체 task-set SHA256: `e38c9b60cf4eef4990f04d4ee1431811cb0221ec6a90ab04f1ebad109375af29`
- JSONL SHA256: `cbbefeab092ee0ba1484a1afbfe11bcc9ddd7ba83bd8de3d224b1754aed90a62`
- 설치 wheel SHA256: `d00e4995a7841943ef56599733769fcb9fec998a5c0f3949a7be3bdad01137e5`

원고 원본의 JSON 키 순서까지 보존하여 승인 당시의 파일 SHA256을 유지한다. 공개 원고는37파일이며 Batch2 승인 기록은9구간450문항이다. 범위 밖 원고는 최종 공개본에 포함하지 않았다.

## 찾기와 사용하기

GitHub 소개에 한국어 문서 이해와 연말정산 및 급여와 부가세 평가 용도를 적고 홈페이지를 Hugging Face로 연결했다. 검색용 주제15개를 적용했다. Hugging Face 카드에는 한국어 및 영어 소개와 문서 질의응답 및 정보 추출 태그를 담았다. 언어 ko와 문서 이해 태그로 필터한 검색에서 실제 데이터셋을 확인했다. 양쪽 README는 이미지 없이 텍스트로 구성했다.

[게시 검증 기록](HUGGING_FACE_PUBLICATION.json)과 [검색 메타데이터 기록](DISCOVERY_METADATA.json)을 함께 보관한다. 카드 원본은 [docs/HUGGING_FACE_DATASET_CARD.md](../docs/HUGGING_FACE_DATASET_CARD.md)다.
