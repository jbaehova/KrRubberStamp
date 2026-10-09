# KrRubberStamp

Korean office rubber stamp, as an AI benchmark dataset: auto-graded tasks on year-end tax, payroll, VAT, and document extraction.

한국 사무 실무의 서류 업무를 한 문항씩 직접 설계한 공개 벤치마크입니다. Batch 1은 연말정산과 급여, 부가세 및 문서 추출 분야의 총 1,200문항입니다. 각 사례의 업무 목적을 정하고 사실과 증빙의 연결 관계를 작성한 뒤, 규칙 엔진으로 정답과 계산 과정을 확정했습니다. 이름과 금액만 바꾼 자동 생성 자료는 공개 평가본에서 제외했습니다.

사용자의 확대 지시에 따라 누적 목표를 4,800문항으로 늘렸습니다. Batch 2부터 Batch 4까지 각 1,200문항을 추가 집필하고 있습니다. 현재 완료된 공개본은 아래 Batch 1의 1,200문항입니다. 최종 검증 후 Hugging Face에 `KrRubberStamp-4.8K`로 게시하며 GitHub에서는 규칙 엔진과 채점기 및 재현 코드를 관리합니다.

공개 문항 전체와 정답을 내려받아 평가하거나 학습에 사용할 수 있습니다. 새로운 시드의 자동 변형 자료가 필요하면 아래 보조 생성기를 실행하세요. 그 출력은 직접 집필한 Batch 1과 별도의 자료입니다.

```sh
uv sync --frozen
uv run krt generate --seed 987654 --n 1200 --output data/generated_seed_987654
```

## Batch 1

| 분야 | 기준 시점 | easy | medium | hard | 합계 |
|---|---|---:|---:|---:|---:|
| `A_yearend` 근로소득 연말정산 | 2025년 귀속 | 90 | 135 | 75 | 300 |
| `B_payroll` 급여와 4대보험 | 2026년 | 90 | 135 | 75 | 300 |
| `C_vat` 일반과세자 부가세 | 2026년 제1기 | 90 | 135 | 75 | 300 |
| `D_extract` 문서 추출과 집계 | 문항별 자료 기준 | 90 | 135 | 75 | 300 |
| 합계 | | 360 | 540 | 300 | 1,200 |

완성된 입력 문서와 답안 스키마는 [`data/batch_1/`](data/batch_1/)에 있습니다. [배치 보고서](reports/BATCH_1_REPORT.md)는 전체 검증 결과와 적용 범위를 기록합니다. [문항 집필 목록](reports/AUTHORED_CASE_CATALOG.md)에서 각 문항의 요청과 설계 이유를 읽을 수 있으며, [사람 검수 목록](reports/REVIEW_QUEUE_BATCH_1.md)은 분야별 15개씩 총 60문항의 입력과 정답 및 계산 과정을 모았습니다.

현재 공개본 1,200문항 모두 검증을 통과했습니다. 같은 문항 ID 전체를 평가한 가짜 솔버의 문항 정답률은 `oracle` 100%, `null` 0%이며 답안 필드는 총 5,524개입니다. 60문항의 사람 검수는 대기 중입니다.

개별 문항은 서로 다른 자료 관계를 판단하도록 작성했습니다.

| 사례 | 판단해야 하는 자료 관계 |
|---|---|
| [A275: 입사 후 추가 납부한 등록금](data/batch_1/A_yearend/B1_A275_23032501/task.yaml) | 같은 봄학기 등록금의 선납과 추가 납부를 실제 지급일로 나누고 재직 기간에 맞춘다. |
| [B204: 일요일이 소정근로일인 창구](data/batch_1/B_payroll/B1_B204_6486778d/task.yaml) | 일요일 근태를 정규 근로로 읽고 토요일 주휴일과 완료된 지급 주를 연결한다. |
| [C002: 공방의 판매와 대표 카드 지출](data/batch_1/C_vat/B1_C002_c185935c/task.yaml) | 결제 전표를 실제 식사 참석자의 활동기록과 연결해 매입세액의 공제 여부를 판정한다. |
| [D276: 가격 조건이 다른 두 표지와 별첨](data/batch_1/D_extract/B1_D276_953771be/task.yaml) | 뒤섞인 품목표의 표지 참조를 읽어 각 가격에 부가세 포함 또는 별도 조건을 적용한다. |

## 평가하기

숫자는 원 단위 정수의 정확 일치로 채점합니다. 문자열은 유니코드와 공백 및 대소문자를 정규화한 뒤 정확 일치로 채점합니다. 주 지표는 문항 전체 정답률이며 필드별 정답률도 제공합니다. LLM 심사위원은 사용하지 않습니다.

사용자 답안은 `answers/my_answers/<task_id>/answer.json`에 저장합니다.

```sh
uv run krt validate --data data/batch_1 --report reports/validation_local.json
uv run krt grade --data data/batch_1 --answers answers/my_answers --report reports/grade_local.json
```

하네스와 채점기를 확인하는 두 가짜 솔버도 제공합니다. `oracle`은 렌더링한 입력을 추출 맵으로 복원한 뒤 규칙 엔진에서 답을 다시 계산하고, `null`은 빈 답을 제출합니다. 이 점수는 실제 모델의 성능을 뜻하지 않습니다.

```sh
uv run krt harness --data data/batch_1 --solver oracle --answers answers/oracle --report reports/oracle_local.json
uv run krt harness --data data/batch_1 --solver null --answers answers/null --report reports/null_local.json
```

모델을 연결하는 Python 인터페이스와 작업 디렉터리의 경계는 [하네스 문서](reports/harness_design.md)에 있습니다. 모델이 받는 작업 디렉터리에는 선언된 입력 문서와 지시문 및 답안 스키마만 복사합니다. 개별 집필 원본과 정답 및 계산 trace는 복사하지 않습니다. 이 데이터셋 구축과 검증에서는 모델 API를 호출하지 않았습니다.

## 원본에서 다시 빌드하기

[`authored/batch_1/`](authored/batch_1/)에는 1,200개의 개별 집필 원본이 있습니다. 각 원본은 업무 요청과 사실값을 담고 있으며 답안 필드와 증빙 배치를 명시합니다. 빌더는 문항 내용이나 숫자를 새로 생성하지 않습니다. 누락된 사실을 채우거나 문서 수를 맞추기 위해 내용을 자동으로 나누지도 않습니다.

새로운 출력 경로를 지정해 정답과 입력 문서를 다시 만들 수 있습니다. 기존 파일이 들어 있는 출력 경로는 덮어쓰지 않습니다. 분야별 300문항과 난이도 비율이 맞지 않거나 검증을 통과하지 못하면 최종 배치를 게시하지 않습니다.

```sh
uv run krt build-authored --batch 1 --output data/batch_1_rebuilt
uv run krt validate --data data/batch_1_rebuilt
```

검증기는 원본 해시와 정답 JSON의 바이트 재현을 검사합니다. 렌더링한 입력 파일에서 사실값을 복원해 계산한 정답도 대조하고, 답안 스키마와 지시문 일관성을 확인합니다. 이 구조적 검증과 별도로 문항 원고를 읽고 증빙의 값이나 날짜를 바꿔 결과가 달라지는지도 점검했습니다. 검토 범위와 수정 내역은 배치 보고서의 편집 검토 문서에 기록합니다. 개별 집필과 내부 검토를 독립 전문가의 승인으로 표현하지 않습니다.

## Hugging Face용 내보내기

```sh
uv run krt export-hf --batch 1
uv run --with datasets python scripts/export_authored_verification.py exports/upto_1
```

`exports/upto_1/`에 `KrRubberStamp-1.2K`의 데이터셋 카드와 JSONL을 만들고 입력 문서 및 집필 원본을 함께 복사합니다. 두 번째 명령은 로컬 JSONL을 Hugging Face Datasets로 읽고 자료 참조와 원본 해시를 확인합니다. 업로드는 하지 않습니다. 모든 문항과 정답을 공개하며 비공개 분할은 없습니다. 각 문항과 데이터셋 카드에는 학습 데이터 오염을 확인하기 위한 카나리아 문자열이 있습니다.

## 규칙과 검증 범위

[`rules/sources.yaml`](rules/sources.yaml)은 71개 규칙의 출처를 기록합니다. 이 중 30개는 공식 수치 예시로 확인했고, 나머지 41개는 `verified: false`로 공개합니다. [미검증 규칙](reports/unverified_rules.md)과 [DATA_SPEC.md](DATA_SPEC.md)에서 근거와 계산 범위를 확인할 수 있습니다.

PDF와 XLSX 및 HWPX와 PNG를 지원합니다. PNG는 PDF 원본의 보관 사본이므로 스캔만 읽는 OCR 평가를 보장하지 않습니다. HWPX는 ZIP 구조와 XML 추출을 검사했으며 한컴 실제 앱 호환성은 별도 검수 대상입니다. 모델 코드 실행용 Docker 명령은 테스트했지만 이 구축 환경에서 실제 Docker 엔진 실행은 확인하지 못했습니다.

```sh
uv run python scripts/check.py
uv run pre-commit run --all-files
```

코드는 [Apache-2.0](LICENSE), 합성 데이터는 [CC-BY-4.0](DATA_LICENSE)이며 Noto Sans KR은 [SIL OFL-1.1](assets/fonts/OFL.txt)입니다. 공식 원문 자료의 권리는 해당 기관에 있습니다. 개인과 업체 정보는 합성이며 식별번호를 기재할 때 체크섬은 고의로 무효화합니다.
