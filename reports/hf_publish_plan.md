# KrRubberStamp 4.8K Hugging Face 게시 준비

2026-10-09 기준. 공개 게시 권한은 사용자가 승인했으며 실제 게시 실행은 전체 원고와 검증을 통합하는 root가 담당한다. 이 준비 단계에서는 Hub 저장소를 만들거나 데이터를 업로드하지 않았다.

## 인증 상태

현재 프로젝트 환경에는 Hugging Face 라이브러리와 `hf` CLI가 기본 설치되어 있지 않았다. `uv run --with huggingface-hub`의 분리 환경에서 `huggingface_hub 2.2.0`을 확인했다. 기존 인증으로 `HfApi().whoami()`를 호출한 결과는 `LocalTokenNotFoundError`였다. 로그인된 사용자 namespace와 쓰기 권한은 확인할 수 없었다. 토큰이나 환경변수 값을 출력하지 않았고 비밀 파일을 읽어 옮기거나 신규 로그인을 실행하지 않았다.

따라서 최종 업로드에는 사용자가 해당 실행 환경에서 Hugging Face 계정에 로그인해야 한다. 토큰은 채팅이나 게시 명령 인자로 받지 않는다. 기존 로그인 저장소를 라이브러리가 직접 사용한다. 로그인 후 `whoami()`에서 반환한 개인 계정 이름을 사용하며 대상 저장소는 `<검증된 계정>/KrRubberStamp-4.8K`다. 계정명은 임의로 추측하지 않는다.

## 실행 경로

게시 스크립트는 [scripts/publish_hf.py](../scripts/publish_hf.py)다. root가 `exports/upto_4`를 완성한 후 실행한다. 게시 옵션 없는 명령은 인증 요청이나 원격 쓰기 없이 로컬 검사 결과만 출력한다.

```sh
uv run python scripts/publish_hf.py exports/upto_4
uv run --with 'huggingface-hub>=2.2.0' python scripts/publish_hf.py exports/upto_4 --publish
```

첫 명령이 통과해야 두 번째 명령이 게시를 시작할 수 있다. 실제 게시 명령도 모든 로컬 검사를 다시 실행한다. 성공 결과의 `repo_id`와 `revision` 및 URL을 최종 게시 기록에 남긴다. 업로드 중 중단되면 같은 변경 없는 내보내기와 명령으로 재개한다. 기존 원격 manifest가 다른 릴리스를 나타내면 덮어쓰기를 거부한다. 원격 파일 삭제와 다른 계정 또는 조직으로의 게시는 지원하지 않는다.

## 게시 전 차단 조건

공개 대상은 Batch 1부터 4까지 총 4,800문항이다. `individually_written` 원고만 허용하고 미리보기나 1,200문항 내보내기는 차단한다. 각 배치의 네 분야는 300문항이며 난이도는 easy 90, medium 135, hard 75여야 한다.

전체 task.yaml을 현재 checkout의 원고로 복원해 지시문과 사실 및 정답 재현성을 확인한다. case SHA와 task-set SHA가 일치해야 하며 JSONL의 모든 행과 문서 경로가 해당 task.yaml에 대응해야 한다. JSONL 정답과 trace 및 answer_schema를 실제 공개 파일과 대조한다. 내보낸 원고도 현재 원고와 대조한다. 배치별 검증과 oracle 및 null 측정은 정확히 같은 문항 ID를 가리켜야 한다. 배치 보고서와 검수 큐의 task-set SHA 표지도 확인한다.

필수 라이선스와 데이터카드 및 원고와 입력 문서가 하나라도 없으면 게시를 시작하지 않는다. 공개 디렉터리 이외의 파일과 숨김 파일 및 비밀 파일과 symlink를 거부한다. `.git`과 캐시 및 Python 바이트코드와 `.DS_Store`는 업로드에서 제외한다. 원본의 하위 상대 경로는 보존한다. 내보내기 파일은 검사부터 업로드 완료까지 변경하지 않는다.

## 업로드와 다운로드 검증

공식 최신 문서와 실제 2.2.0 API에서 `upload_large_folder`는 제거되어 있었다. [공식 업로드 안내](https://huggingface.co/docs/huggingface_hub/guides/upload)에 따라 `HfApi.upload_folder()`를 사용한다. 기본 Xet 경로는 파일 수에 맞춰 여러 commit으로 나누며 중단 후 동일 명령을 재실행하면 이미 commit된 파일과 전송된 chunk를 재사용한다. 저장소 생성은 `create_repo(repo_type="dataset", private=False, exist_ok=True)`를 사용한다. 기존 비공개 저장소의 공개 전환은 자동 실행하지 않는다.

업로드 후 Hub에서 불변 commit SHA를 받아 모든 후속 다운로드에 동일한 revision을 지정한다. 원격 전체 파일 목록을 로컬 공개 inventory와 대조한다. JSONL과 export manifest 및 데이터카드와 네 배치 manifest를 내려받아 로컬 파일의 SHA-256과 비교한다. 추가로 각 배치와 분야에서 존재하는 각 문서 형식별 대표 입력을 내려받아 bytes를 확인한다. JSONL 전체를 내려받아 같은 해시인지 비교하므로 원격 행 수도 로컬 검증의 4,800행과 동일하다. 모든 문서의 다운로드 검사가 아니라 전체 inventory와 대표 문서의 다운로드 검사라는 범위를 최종 기록에 유지한다. API의 revision 및 저장소 타입 동작은 [공식 HfApi 문서](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api)를 따른다.

## 준비 단계 검사 결과

- Ruff 검사와 format 검사 통과.
- `tests/test_publish_hf.py` 경계 테스트 8개 통과. 불완전 문항 수와 미리보기를 차단한다. 필수 artifact 누락과 현재 원고 identity 변경을 차단한다. dry-run에서 원격 쓰기를 하지 않으며 숨김 파일과 symlink를 거부한다. revision 고정 다운로드의 원격 손상과 전체 inventory 불일치를 탐지한다.
- 기존 `exports/upto_1`을 실행 입력으로 주었을 때 4,800문항 요건으로 차단됨을 확인했다.
- 실제 Hub 생성 및 업로드는 실행하지 않았으며 실제 인증은 현재 불가능하다. 네트워크 업로드 mock 테스트도 원격 부작용을 일으키지 않는다.

Batch 2부터 Batch 4까지는 `authoring_acceptance_batch_N.json`에 의미 검토를 마친 원고별 SHA256과 문항 ID를 기록한다. 게시 preflight가 내보낸 원고의 실제 바이트 및 현재 문항 ID를 대조하므로, 검토 뒤 변경된 원고나 검토가 아직 끝나지 않은 원고는 게시할 수 없다. 이 기록은 root의 개별 집필 및 중복 검토 인계이며 사람 전문가 검수 완료를 뜻하지 않는다.
