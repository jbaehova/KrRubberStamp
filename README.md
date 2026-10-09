# KrRubberStamp

**서류를 읽고, 근거를 연결하고, 정확한 답을 내는 한국 사무 실무 벤치마크.**

연말정산부터 급여 정산, 부가세 신고, 견적 비교까지. 한 문항씩 직접 설계한 1,650개의 업무입니다.

[데이터셋 받기](https://huggingface.co/datasets/jbaehova/KrRubberStamp-1.65K) / [문항 둘러보기](reports/AUTHORED_CASE_CATALOG.md) / [데이터 명세](DATA_SPEC.md)

Korean office rubber stamp, as an AI benchmark dataset: auto-graded tasks on year-end tax, payroll, VAT, and document extraction.

새 시드의 보조 자료 생성: `uv run krt generate --seed 987654 --n 1200 --output data/generated_seed_987654`. 이 출력은 개별 집필 공개본과 별도의 자동 변형 자료입니다.

## 서류 뒤에 있는 판단을 평가합니다

한국어 문서 질의응답(document question answering)과 정보 추출(information extraction)을 평가합니다. 연말정산과 급여 및 부가세 자료를 연결하는 재무 추론(financial reasoning)도 포함합니다.

같은 직원의 정정 급여 명세에서 어떤 승인본을 선택할지, 할인과 배송비를 어디에 적용할지, 만료된 견적을 제외하면 어떤 구매 조합이 유리한지. 정답을 내려면 문서 속 숫자와 함께 자료의 관계를 읽어야 합니다.

모든 공개 문항은 업무 목적과 사실을 개별 집필했습니다. 증빙을 구성한 뒤 규칙 엔진으로 정답과 계산 과정을 확정했습니다. 이름과 금액만 바꾼 자동 생성 자료는 공개 평가본에서 제외했습니다.

| 분야 | 평가하는 업무 | 기준 시점 | 문항 |
|---|---|---|---:|
| `A_yearend` | 근로소득 연말정산 | 2025년 귀속 | 400 |
| `B_payroll` | 급여와 4대보험 정산 | 2026년 | 400 |
| `C_vat` | 일반과세자 부가세 | 2026년 제1기 | 400 |
| `D_extract` | 문서 추출과 집계, 견적 비교 | 문항별 자료 기준 | 450 |
| **합계** | | | **1,650** |

**easy 495 / medium 743 / hard 412.** Batch 1의 1,200문항과 Batch 2의 450문항으로 완료한 최종 공개본입니다. 추가 배치는 없습니다.

## 바로 사용하기

Hugging Face에서 문항과 정답을 읽습니다. 아래 예시는 `datasets`와 `huggingface_hub` 패키지를 사용합니다. `answer_schema`, `gold`, `trace`는 JSON 문자열이며 입력 문서는 별도 파일로 내려받습니다.

```python
import json
from datasets import load_dataset
from huggingface_hub import hf_hub_download

repo_id = "jbaehova/KrRubberStamp-1.65K"
tasks = load_dataset(repo_id, data_files="data/train.jsonl", split="train")
task = tasks[0]

print(task["instruction"])
schema = json.loads(task["answer_schema"])
document = hf_hub_download(
    repo_id, filename=task["input_files"][0]["path"], repo_type="dataset"
)
```

로컬 채점에는 Python 3.12와 [uv](https://docs.astral.sh/uv/)를 사용합니다. 답안을 `answers/my_answers/<task_id>/answer.json`에 저장한 뒤 두 배치를 각각 평가합니다.

```sh
uv sync --frozen
uv run krt grade --data data/batch_1 --answers answers/my_answers --report reports/grade_local_1.json
uv run krt grade --data data/batch_2 --answers answers/my_answers --report reports/grade_local_2.json
```

숫자는 정수의 정확 일치로 채점하며 금액은 원 단위입니다. 문자열은 유니코드와 공백 및 대소문자를 정규화한 뒤 정확 일치로 채점합니다. 주 지표는 **문항 전체 정답률**이며 필드별 정답률도 제공합니다. LLM 심사위원은 사용하지 않습니다.

<details>
<summary><strong>보조 생성기로 새로운 시드의 자료 만들기</strong></summary>

```sh
uv run krt generate --seed 987654 --n 1200 --output data/generated_seed_987654
```

이 명령은 자동 변형 자료를 만드는 보조 기능입니다. 출력은 직접 집필한 공개본 1,650문항과 별도의 자료입니다.

</details>

## 네 문항 먼저 보기

| 문항 | 읽어야 하는 근거 |
|---|---|
| [A275: 입사 후 추가 납부한 등록금](data/batch_1/A_yearend/B1_A275_23032501/task.yaml) | 같은 학기 등록금의 선납과 추가 납부를 실제 지급일로 나누고 재직 기간에 맞춥니다. |
| [B082: 보험 기초가 정정된 급여 명세](data/batch_2/B_payroll/B2_B082_104d7996/task.yaml) | 임금은 같지만 보험 기초가 다른 명세에서 최종 완전 승인본을 선택하고 실제 은행 지급과 연결합니다. |
| [C062: 할인이 겹치는 청구 행](data/batch_2/C_vat/B2_C062_5b890dbb/task.yaml) | 개당 할인과 행 할인을 구분하고 상품 전체 할인 및 배송비를 적용해 부가세와 발행세액공제를 계산합니다. |
| [D123: 함께 살까, 나눠 살까](data/batch_2/D_extract/B2_D123_9941a97b/task.yaml) | 포장 수량과 무료배송 기준을 함께 비교하고 종료된 할인을 제외해 구매 조합을 고릅니다. |

각 문항은 입력 문서와 지시문, 답안 스키마를 포함합니다. 공개 정답과 계산 trace도 함께 제공하므로 평가 및 학습에 사용할 수 있습니다. 비공개 분할은 없으며 문항별 카나리아 문자열로 학습 데이터 오염 여부를 점검할 수 있습니다.

## 검증 결과

| 공개본 | 문항 | 답안 필드 | `oracle` | `null` |
|---|---:|---:|---:|---:|
| [Batch 1](reports/BATCH_1_REPORT.md) | 1,200 | 5,524 | 100% | 0% |
| [Batch 2](reports/BATCH_2_REPORT.md) | 450 | 12,477 | 100% | 0% |
| **전체** | **1,650** | **18,001** | **100%** | **0%** |

[최종 공개 검증](reports/FINAL_1650_RELEASE.md)과 [설치 패키지 검증](reports/final_1650_portable_package.md)에서 재현 결과를 확인할 수 있습니다.

`oracle`은 렌더링된 입력을 추출 맵으로 복원하고 규칙 엔진에서 답을 다시 계산하는 가짜 솔버입니다. `null`은 빈 답을 제출합니다. 이 결과는 하네스와 계산 재현성 검증이며 실제 모델의 성능 점수가 아닙니다. 코드 검증에서는 **1,532개 테스트를 통과**했으며 구축과 검증 과정에서 모델 API 호출은 **0회**입니다.

원고를 읽는 내부 검토와 증빙의 값이나 날짜를 바꾸는 반사실 점검도 수행했습니다. 독립 전문가의 승인으로 표현하지 않습니다. 사람 검수는 배치마다 60개씩 **총 120문항이 대기 중**입니다. [Batch 1 검수 목록](reports/REVIEW_QUEUE_BATCH_1.md)과 [Batch 2 검수 목록](reports/REVIEW_QUEUE_BATCH_2.md)에 입력과 정답 및 계산 과정을 모았습니다.

<details>
<summary><strong>빌드부터 채점까지 재현하기</strong></summary>

[`authored/batch_1/`](authored/batch_1/)과 [`authored/batch_2/`](authored/batch_2/)에 개별 집필 원본이 있습니다. 빌더는 원고에 명시한 사실과 증빙 배치를 렌더링하며 새 문항이나 숫자를 생성하지 않습니다. 기존 파일이 있는 출력 경로는 덮어쓰지 않습니다.

```sh
uv run krt build-authored --batch 1 --output data/batch_1_rebuilt
uv run krt build-authored --batch 2 --output data/batch_2_rebuilt
uv run krt validate --data data/batch_1_rebuilt
uv run krt validate --data data/batch_2_rebuilt
```

검증기는 원본 해시와 정답 JSON의 바이트 재현을 확인합니다. 실제 입력 파일에서 사실을 복원해 정답과 계산 trace를 대조하고 답안 스키마 및 지시문 일관성을 검사합니다. 분야별 수량과 난이도 및 문항 ID 범위를 만족해야 배치를 게시할 수 있습니다.

| 분야 | Batch 1 | Batch 2 |
|---|---:|---:|
| A / B / C 각각 | 300 | 100 |
| D | 300 | 150 |

가짜 솔버 실행 예시입니다. Batch 2는 `--data data/batch_2`로 같은 절차를 수행합니다.

```sh
uv run krt harness --data data/batch_1 --solver oracle --answers answers/oracle --report reports/oracle_local.json
uv run krt harness --data data/batch_1 --solver null --answers answers/null --report reports/null_local.json
uv run python scripts/check.py
uv run pre-commit run --all-files
```

모델 연결 방법은 [하네스 문서](reports/harness_design.md)를 참고하세요. 모델의 작업 디렉터리에는 선언된 입력 문서와 지시문 및 답안 스키마만 복사합니다. 공개 정답과 원고 및 추출 맵은 평가 입력에 포함하지 않습니다.

</details>

<details>
<summary><strong>Hugging Face 내보내기와 게시 재현하기</strong></summary>

```sh
uv run krt export-hf --upto 2
uv run --with datasets python scripts/export_authored_verification.py exports/upto_2
uv run --with 'huggingface-hub>=2.2.0' python scripts/publish_hf.py exports/upto_2
uv run --with 'huggingface-hub>=2.2.0' python scripts/publish_hf.py exports/upto_2 --card docs/HUGGING_FACE_DATASET_CARD.md --publish
```

`exports/upto_2/`에 데이터셋 카드와 JSONL을 만들고 입력 문서 및 개별 집필 원본을 복사합니다. 오프라인 검증은 Hugging Face Datasets로 JSONL을 읽고 자료 참조와 원본 해시를 확인합니다. 게시 스크립트는 정확히 1,650문항과 배치 `[1, 2]` 및 승인 원고의 SHA256을 검사합니다.

게시 명령은 기본적으로 로컬 검증만 수행하며 `--publish`를 지정하면 기존 로컬 Hugging Face 인증으로 공개 업로드합니다.

</details>

## 적용 범위와 라이선스

[`rules/sources.yaml`](rules/sources.yaml)은 78개 규칙의 출처를 기록합니다. 30개는 공식 수치 예시로 확인했고 48개는 `verified: false`로 공개합니다. 근거와 계산 범위는 [미검증 규칙](reports/unverified_rules.md) 및 [DATA_SPEC.md](DATA_SPEC.md)를 확인하세요.

PDF와 XLSX, HWPX 및 PNG를 지원합니다. PNG는 PDF 원본의 보관 사본이므로 스캔만 읽는 OCR 평가를 보장하지 않습니다. HWPX는 ZIP 구조와 XML 추출을 검사했으며 한컴 실제 앱 호환성은 별도 검수 대상입니다. 모델 실행용 Docker 명령은 테스트했으나 구축 환경에서 실제 Docker 엔진 실행은 확인하지 못했습니다.

코드는 [Apache-2.0](LICENSE), 합성 데이터는 [CC-BY-4.0](DATA_LICENSE)입니다. Noto Sans KR은 [SIL OFL-1.1](assets/fonts/OFL.txt)을 따릅니다. 공식 원문 자료의 권리는 해당 기관에 있습니다. 개인과 업체 정보는 합성이며 식별번호를 기재할 때 체크섬은 고의로 무효화합니다.
