# 입력 문서 렌더링과 복원 검증

## 구현

`render.render_task(scenario, task_dir, domain, difficulty, seed)`는 `input_files` 목록을 반환한다. `render.restore_scenario(task_dir)`는 실제 입력 문서의 표시 셀과 PDF 텍스트를 읽어 시나리오를 복원한다.

이 문서는 기반 렌더러와 보조 시드 생성기의 초기 검증을 기록한다. 개별 집필 렌더러는 동일한 파일 작성기를 사용하되 원고에 직접 지정한 자료 구성과 필드 및 양식을 따른다. 초기 용량과 시드 표본 검사는 최종 집필본의 분포를 뜻하지 않는다. 최종 사용 양식과 용량은 배치 보고서에서 별도로 집계한다.

PDF는 ReportLab으로 생성하며 Noto Sans KR의 OFL 글꼴을 부분 임베딩한다. XLSX는 openpyxl로 작성한다. 금액과 수량은 실제 숫자 셀이며, 문자열은 수식으로 실행되지 않는 텍스트 셀이다. HWPX는 Hancom 네임스페이스를 사용하는 ZIP 문서다. 본문은 실제 2열 표로 구성된다.

양식은 5종이다. 표준 상단 선과 교대 행 배경이 있는 청색 양식, 왼쪽 세로 띠와 넓은 여백을 사용하는 녹색 양식, 이중 상단 선과 행 배경을 사용하지 않는 흑백 양식, 첫 열이 넓은 갈색 양식, 채운 제목 영역과 테두리를 줄인 자주색 양식을 제공한다. XLSX는 행 배경과 테두리, 열 너비가 달라진다. HWPX는 열 너비와 글자 크기가 양식마다 달라진다.

목록 안의 거래와 가족 기록은 번호를 붙여 같은 문서에 유지한다. 문서 묶음에는 원자료가 분산되어 있으며 하나의 거래를 여러 문서에서 잘라 읽도록 만들지 않는다. 분야별 `scenarios.<domain>.LABELS`의 한글 항목명을 적용한다. 자료가 적은 단위 테스트에서는 같은 사실을 담은 보완 증빙을 허용한다.

| 난이도 | A, B, C 분야 | D 분야 | 문서 수 |
|---|---|---|---|
| easy | PDF 1, XLSX 1 | PDF 1, PNG 1 | 2 |
| medium | PDF 2, XLSX 2, HWPX 1 | PDF 2, XLSX 1, HWPX 1, PNG 1 | 5 |
| hard | PDF 4, XLSX 3, HWPX 1, PNG 2 | 동일 | 10 |

## 복원 맵과 격리

`extraction_map.json`은 문항 디렉터리에 저장하며 `inputs/`에는 넣지 않는다. 맵에는 JSON 경로, 컨테이너 종류와 값의 자료형이 있다. PDF 페이지와 표시 셀의 사각형, XLSX 시트와 셀 위치, HWPX 표와 셀 위치를 저장한다. 원래 시나리오 값과 정답, 계산 과정은 저장하지 않는다.

PDF에는 본문 표에 보이는 개별 기재값만 있다. 첨부파일과 숨긴 JSON, 바코드, QR 데이터는 넣지 않는다. HWPX의 본문 XML은 화면에 표시되는 문단과 표 셀을 표현한다. XLSX에는 숨긴 워크시트나 정답 시트가 없다.

복원은 PDF의 표시 셀을 PyMuPDF로 읽고, 워크북의 실제 셀을 읽고, HWPX의 표 셀 문단을 읽는다. 셀 숫자를 변경하면 복원된 값도 변경된다. 문서가 사라지거나 자료형에 맞지 않는 셀 값이 있으면 실패한다.

## 스캔 자료

PNG는 PDF의 모든 페이지를 약 130dpi 회색 이미지로 래스터화한 뒤 작은 회전과 블러를 적용한다. 종이 영역에는 희소 노이즈를 넣고 가장자리에는 얼룩을 추가한다. 글자 영역을 가리는 큰 얼룩은 만들지 않는다. 같은 원본 증빙이라는 안내를 이미지 상단에 표시하고 `input_files.duplicate_of`로 원본을 연결한다. 다중 페이지 PDF는 세로로 이어진 PNG 한 파일로 만든다.

스캔은 원본 PDF와 중복된 자료이다. 복원 검증기는 PNG의 정상 여부를 확인하며 계산에 필요한 값은 원본 문서에서 읽는다. 검증기가 OCR로 원본 값을 복원했다고 주장하지 않는다. 따라서 이 배치는 스캔에서만 제공되는 필수 사실을 포함하지 않으며 독립적인 OCR 성능 검증용으로는 부족하다.

실제 OCR 확인은 `tesseract render/qa_scan.png render/qa_scan_ocr -l kor+eng --psm 6`으로 수행했다. 합성 업체명과 날짜, 문서 번호를 읽었고 수량 26 및 21, 단가 34,100 및 6,300을 읽었다. 일부 행 번호를 오인식했다. 출력은 `render/qa_scan_ocr.txt`에 있다.

## HWPX 확인 범위

Hancom의 [HWPX 포맷 설명](https://tech.hancom.com/hwpxformat/)과 [공개 OWPML 모델](https://github.com/hancom-io/hwpx-owpml-model)을 참고했다. ZIP의 첫 항목은 비압축 `mimetype`이며 `application/hwp+zip`을 담는다. 컨테이너와 매니페스트를 포함한다. `Contents/content.hpf`의 spine은 header와 section을 참조한다. 본문은 section, paragraph, run, text와 table 요소를 사용하고 헤더의 글꼴 및 서식 ID를 참조한다.

독립적인 `python-hwpx` 파서로 생성한 hard 자료를 열었다. 경고 없이 한 구역과 15행 2열 표를 읽었고 표시 셀의 문서 번호 `SYN-00000271-04`를 읽었다. 테스트는 ZIP CRC와 XML 문법, spine 참조, 표의 행과 열 개수, 페이지 및 서식 ID 구조를 검사한다.

이 확인은 전체 KS X 6101 XSD 검증이나 Hancom 화면 검증을 대체하지 않는다. 로컬에 Hancom 뷰어가 없고 설치된 LibreOffice는 HWPX 가져오기를 지원하지 않아 화면 호환성은 미확인이다. 구조 작성 및 독립 파싱이 성공하여 DOCX 대체는 사용하지 않았다. 사람이 검수할 때 HWPX를 Hancom에서 확인해야 한다.

## 수행한 검증

`uv run pytest tests/test_render.py`: 19개 통과. 네 분야와 세 난이도에서 원본 시나리오와 입력 문서 복원 결과가 완전히 같았다. 추가로 8개 시드의 모든 분야 및 난이도 조합 96개를 복원하여 불일치가 없었다.

테스트는 실제 숫자 셀을 확인하며 PDF의 첨부와 정답 메타데이터가 없는지 검사한다. 문서 삭제와 셀 변조를 검증한다. 한글과 빈 문자열, 중첩 목록, 불리언, 빈 컨테이너를 검증한다. PDF와 PNG는 같은 시드로 생성할 때 바이트가 같다. `uv run ruff check render tests/test_render.py`도 통과했다.

PDF와 PNG를 직접 열어 한글이 잘 보이고 표가 겹치거나 잘리지 않는지 확인했다. `render/korean_sample.pdf`와 `render/korean_sample.png`는 M0 한글 확인용이다. `render/qa_templates.png`는 다섯 양식을 비교한 화면이며 `render/qa_scan.png`는 실제 스캔 효과를 확인한 자료다.

## 용량과 의존성

한글 정적 글꼴 원본은 약 6.2MB이며 `assets/fonts/OFL.txt`를 함께 제공한다. 문서에는 필요한 글자만 부분 임베딩된다. 초기 실측의 문항당 입력 크기는 A부터 C의 easy가 약 30~45KB이고 medium이 약 64~71KB이다. hard는 약 240~560KB이다. D easy는 다중 페이지 스캔 때문에 약 250KB이다. 최종 배치 용량은 생성 보고서에서 집계해야 한다.

필수 Python 의존성은 reportlab과 openpyxl, Pillow, pymupdf 및 fonttools이다. Tesseract는 OCR 확인에만 사용했고 런타임 복원에는 필요하지 않다. PDF는 번들 글꼴을 사용한다. XLSX와 HWPX의 표시 글꼴은 뷰어 환경에 따라 대체될 수 있다.
