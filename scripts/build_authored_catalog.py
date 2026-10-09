"""List completed individual manuscripts for editorial inspection."""

import argparse
import json
from pathlib import Path

from KrRubberStamp.authoring import load_cases

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-file", action="append")
    parser.add_argument("--completed-from", type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--batch", type=int)
    selection.add_argument("--upto", type=int)
    args = parser.parse_args(argv)
    batches = list(range(1, args.upto + 1)) if args.upto is not None else [args.batch or 1]
    cases = (
        (
            [
                entry
                for batch in batches
                for name in args.case_file
                for entry in load_cases(batch, file_name=name)
            ]
            if args.case_file
            else [entry for batch in batches for entry in load_cases(batch)]
        )
        if not args.completed_from
        else [
            entry
            for source in json.loads(args.completed_from.read_text())["completed_source_files"]
            for entry in load_cases(
                int(Path(source).parts[0].removeprefix("batch_")),
                file_name=Path(source).name,
                domain=Path(source).parent.name,
            )
        ]
    )
    cases.sort(key=lambda entry: (entry[1].split("/")[0], entry[0]["case_id"]))
    lines = [
        "# 개별 문항 집필 목록",
        "",
        f"완료 원고 {len(cases)}개를 수록했다. 배치당 1,200개를 구성하며 현재 승인된 누적 목표는 4,800개다. 이 목록은 집필 내용을 검토할 수 있도록 보여 주며 독립 전문가의 승인이나 문항 다양성 점수를 뜻하지 않는다.",
        "",
    ]
    for case, source in cases:
        lines.extend(
            [
                f"## B{Path(source).parts[0].removeprefix('batch_')}_{case['case_id']}: {case['title']}",
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
