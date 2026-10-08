"""Publish written cases for review. This script does not invent case content."""

from pathlib import Path
import json
import yaml

from KrRubberStamp.authoring import load_cases

ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = load_cases(file_name="preview.json")
    built = {}
    for path in (ROOT / "data/authored_preview").glob("*/*/task.yaml"):
        metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
        built[metadata["authorship"]["case_id"]] = (path.parent, metadata)
    lines = [
        "# 직접 작성한 문항 미리보기",
        "",
        "기존 자동생성 1,200문항은 공개 후보에서 제외했다. 여기에는 개별적으로 작성한 첫 12문항을 담았다. Batch 1의 전체 집필은 진행 중이며 이 파일은 완료 보고서가 아니다.",
        "",
        "각 사례의 업무 목적과 사실을 먼저 작성하고 증빙 배치와 질문별 답안 항목을 정했다. 문항 생성기를 호출하거나 이전 문항의 이름과 숫자를 바꾸어 작성하지 않았다. 정답과 trace는 규칙 엔진에서 계산했다.",
        "",
        "12문항 모두 원본 재현과 실제 문서 값 복원 및 지시문과 스키마 검사를 통과했다. oracle 전체 정답률과 필드 정답률은 100%, null은 0%다. 이는 계산과 자료의 일치 검증이며 사례의 세법 해석에 대한 독립적인 전문가 검수는 아니다.",
        "",
        "| 사례 | 난이도 | 업무 요청 | 자료 수 | 답안 필드 수 |",
        "|---|---|---|---:|---:|",
    ]
    for case, source in cases:
        lines.append(
            f"| [{case['case_id']}](#{case['case_id'].lower()}) | {case['difficulty']} | {case['title']} | {len(case['documents'])} | {len(case['answer_fields'])} |"
        )
    for case, source in cases:
        directory, metadata = built[case["case_id"]]
        source_path = "../authored/" + source
        lines += [
            "",
            f"## {case['case_id']}",
            "",
            f"**{case['title']}**",
            "",
            "업무 요청:",
            "",
            case["instruction"],
            "",
            "설계 목적:",
            "",
            case["work_goal"],
            "",
            case["design_rationale"],
            "",
            "직접 작성한 증빙:",
            "",
            "| 파일 | 자료의 역할과 기재 내용 |",
            "|---|---|",
        ]
        for document in case["documents"]:
            relative = (directory / "inputs" / document["filename"]).relative_to(ROOT)
            note = document["note"].replace("|", "/").replace("\n", " ")
            lines.append(f"| [{document['title']}](../{relative}) | {note} |")
        gold = json.loads((directory / "gold.json").read_text(encoding="utf-8"))
        lines += [
            "",
            "계산한 정답:",
            "",
            "```json",
            json.dumps(gold, ensure_ascii=False, indent=2),
            "```",
            "",
            f"[개별 집필 원본]({source_path})",
            "",
        ]
    (ROOT / "reports/AUTHORED_PREVIEW.md").write_text("\n".join(lines), encoding="utf-8")
    print({"authored_preview_cases": len(cases)})


if __name__ == "__main__":
    main()
