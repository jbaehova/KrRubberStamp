"""List completed individual manuscripts for editorial inspection."""

import argparse
from pathlib import Path

from KrRubberStamp.authoring import load_cases

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-file", action="append")
    args = parser.parse_args(argv)
    cases = (
        [entry for name in args.case_file for entry in load_cases(file_name=name)]
        if args.case_file
        else load_cases()
    )
    cases.sort(key=lambda entry: entry[0]["case_id"])
    lines = [
        "# 개별 문항 집필 목록",
        "",
        f"완료 원고 {len(cases)}개를 수록했다. 전체 Batch 1은 1,200개가 필요하다. 이 목록은 집필 내용을 검토할 수 있도록 보여 주며 독립 전문가의 승인이나 문항 다양성 점수를 뜻하지 않는다.",
        "",
    ]
    for case, source in cases:
        lines.extend(
            [
                f"## {case['case_id']}: {case['title']}",
                "",
                f"난이도: {case['difficulty']}. 입력 자료 {len(case['documents'])}개.",
                "",
                case["instruction"],
                "",
                f"업무 목적: {case['work_goal']}",
                "",
                f"판단 관계: {case['design_rationale']}",
                "",
                "요청 답안: " + ", ".join(f"`{key}`" for key in case["answer_fields"]),
                "",
                f"[집필 원고](../authored/{source})",
                "",
            ]
        )
    target = ROOT / "reports/AUTHORED_CASE_CATALOG.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    print({"authored_cases": len(cases), "catalog": str(target)})


if __name__ == "__main__":
    main()
