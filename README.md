# KrRubberStamp

Korean office rubber stamp, as an AI benchmark dataset: auto-graded tasks on year-end tax, payroll, VAT, and document extraction.

한국 실무 서류 업무의 문제를 한 문항씩 직접 설계하는 공개 벤치마크입니다. 각 사례의 업무 목적과 사실을 작성하고, 증빙 사이의 관계와 문서 배치 및 요청하는 답을 개별적으로 정합니다. 계산 엔진은 작성된 사례의 정답을 계산하고 검증합니다.

현재 개별 집필 중입니다. 기존 1,200개 자동생성 문항은 공개 후보에서 제외했습니다. 목표는 Batch 1의 분야별 300문항이며, 완성된 개별 사례만 최종 배치에 포함합니다.

[직접 작성한 첫 12문항](reports/AUTHORED_PREVIEW.md)에서 지시문과 증빙 및 설계 이유를 확인할 수 있습니다.

```sh
uv sync --frozen
uv run krt build-authored --preview --case-file preview.json --output data/preview_copy
uv run krt validate --data data/preview_copy
```

전체 집필이 완료되면 다음 명령이 개별 사례 원본에서 정답과 문서를 빌드합니다. 1,200개 집필본과 분야별 난이도 비율이 맞지 않으면 최종 배치를 만들지 않습니다.

```sh
uv run krt build-authored --batch 1 --output data/batch_1
```

## 집필과 검증

`authored/batch_1/`에는 직접 작성한 사례 원본이 있습니다. 각 원본은 업무 요청, 사실값, 질문별 답안 필드와 자료 배치를 담습니다. 빌더는 문항의 내용이나 숫자를 만들어 넣지 않습니다. 누락된 자료를 자동으로 채우거나 문서 개수를 맞추기 위해 내용을 나누지도 않습니다.

정답은 분야별 규칙 엔진에서 계산합니다. 작성된 원본의 해시와 정답 JSON 바이트 재현을 검사하고, 실제 입력 파일의 값으로 시나리오를 복원한 결과도 대조합니다. 숫자는 원 단위 정확 일치이며 문자열은 정규화 후 정확 일치로 채점합니다. LLM 심사위원은 사용하지 않습니다.

```sh
uv run krt harness --data data/authored_preview --solver oracle --answers answers/preview_oracle
uv run krt harness --data data/authored_preview --solver null --answers answers/preview_null
uv run krt grade --data data/authored_preview --answers answers/my_answers
```

하네스는 에이전트에게 선언된 입력 문서와 지시문 및 답안 스키마만 제공합니다. 개별 집필 원본과 정답 및 계산 trace는 작업 디렉터리에 넣지 않습니다. 현재 작업에서는 모델 API를 호출하지 않습니다. 사용자 모델 연결용 OpenAI 호환 어댑터는 별도 인터페이스로 제공합니다.

## 보조 생성기

```sh
uv run krt generate --seed 987654 --n 1200 --output data/generated_seed_987654
```

시드 생성기는 별도의 자동 변형 자료를 만들 때만 사용합니다. 그 출력은 직접 집필한 공개 평가본에 포함되지 않으며 같은 수준의 사례 다양성을 보장하지 않습니다. 개별 집필 문항의 제작을 이 명령으로 대신하지 않습니다.

## 배포와 범위

완성된 배치는 `uv run krt export-hf --batch 1`로 Hugging Face용 JSONL과 원본 문서 및 데이터셋 카드를 내보냅니다. 업로드는 하지 않습니다. 모든 문항과 정답은 공개하며 비공개 분할은 없습니다.

연말정산은 2025년 귀속, 급여는 2026년, 부가세는 2026년 제1기 일반과세자 기준입니다. [규칙 출처](rules/sources.yaml)와 [미검증 규칙](reports/unverified_rules.md)에 근거와 검증 공백을 기록합니다. 세법 계산의 적용 범위는 [DATA_SPEC.md](DATA_SPEC.md)에 있습니다.

PDF와 XLSX 및 HWPX와 PNG를 지원합니다. PNG는 PDF 원본의 보관 사본이며 스캔만 읽는 OCR 평가를 보장하지 않습니다. HWPX는 네이티브 구조와 XML 추출을 확인하며 한컴 실제 앱 호환성은 별도 검수 항목입니다.

```sh
uv run python scripts/check.py
uv run pre-commit run --all-files
```

코드는 [Apache-2.0](LICENSE), 합성 데이터는 [CC-BY-4.0](DATA_LICENSE)이며 Noto Sans KR은 [SIL OFL-1.1](assets/fonts/OFL.txt)입니다. 공식 원문 자료의 권리는 해당 기관에 있습니다. 모든 개인과 업체 정보는 합성이며 식별번호를 기재할 때 체크섬은 고의로 무효화합니다.
