"""krt offline task generation, grading, validation, harness, and export."""

import argparse
import json
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="krt", description="KrRubberStamp offline benchmark utilities"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    authored = commands.add_parser(
        "build-authored", help="Render independently written cases, without generating their facts"
    )
    authored.add_argument("--batch", type=int, default=1)
    authored.add_argument("--output", type=Path)
    authored.add_argument(
        "--case-file", help="Preview only: choose a source filename such as preview.json"
    )
    authored.add_argument(
        "--domain",
        choices=("A_yearend", "B_payroll", "C_vat", "D_extract"),
        help="Preview only: inspect one completed domain while other manuscripts are being written",
    )
    authored.add_argument(
        "--preview",
        action="store_true",
        help="Build the currently written subset without declaring a complete release",
    )
    gen = commands.add_parser(
        "generate", help="Generate a fresh seeded task set without model calls"
    )
    gen.add_argument("--seed", type=int, required=True)
    gen.add_argument("--n", type=int, default=1200)
    gen.add_argument("--output", type=Path)
    gen.add_argument("--batch", type=int, default=1)
    valid = commands.add_parser(
        "validate", help="Rebuild answers from rendered inputs and their source facts"
    )
    valid.add_argument("--batch", type=int, default=1)
    valid.add_argument("--data", type=Path)
    valid.add_argument("--report", type=Path)
    grade = commands.add_parser("grade", help="Score submitted answer.json folders")
    grade.add_argument("--batch", type=int, default=1)
    grade.add_argument("--data", type=Path)
    grade.add_argument("--answers", type=Path, required=True)
    grade.add_argument("--report", type=Path)
    harness = commands.add_parser("harness", help="Run oracle or null only; never invokes a model")
    harness.add_argument("--batch", type=int, default=1)
    harness.add_argument("--data", type=Path)
    harness.add_argument("--solver", choices=["oracle", "null"], required=True)
    harness.add_argument("--answers", type=Path, required=True)
    harness.add_argument("--report", type=Path)
    export = commands.add_parser(
        "export-hf", help="Create an upload-ready Hugging Face export, without uploading"
    )
    which = export.add_mutually_exclusive_group()
    which.add_argument("--batch", type=int)
    which.add_argument("--upto", type=int)
    export.add_argument("--data-root", type=Path, default=Path("data"))
    export.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "build-authored":
            from .authoring import build_authored

            output = args.output or (
                Path("data/authored_preview")
                if args.preview
                else Path("data") / f"batch_{args.batch}"
            )
            summary = build_authored(
                output,
                batch=args.batch,
                preview=args.preview,
                file_name=args.case_file,
                domain=args.domain,
            )
            result = {key: value for key, value in summary.items() if key != "tasks"}
            result["output"] = str(output)
        elif args.command == "generate":
            from scenarios.batch import generate_batch

            output = args.output or Path("data/generated") / f"seed_{args.seed}_n_{args.n}"

            def progress(count, total, task_id):
                if count % 25 == 0 or count == total:
                    print(f"Accepted {count}/{total}: {task_id}", file=sys.stderr, flush=True)

            summary = generate_batch(args.seed, args.n, output, args.batch, progress)
            result = {k: v for k, v in summary.items() if k not in ("tasks", "rejections")}
            result["output"] = str(output)
        elif args.command == "validate":
            from validate import validate_batch

            result = validate_batch(args.data or Path("data") / f"batch_{args.batch}")
        elif args.command == "grade":
            from grader import grade_batch

            result = grade_batch(args.data or Path("data") / f"batch_{args.batch}", args.answers)
        elif args.command == "harness":
            from harness import run_fake

            result = run_fake(
                args.data or Path("data") / f"batch_{args.batch}", args.answers, args.solver
            )
        else:
            from .export import export_hf

            batches = list(range(1, args.upto + 1)) if args.upto is not None else [args.batch or 1]
            result = export_hf(
                args.data_root, batches, args.output or Path("exports") / f"upto_{batches[-1]}"
            )
        if getattr(args, "report", None):
            from .io import write_json

            write_json(args.report, result)
        printed = {
            k: v
            for k, v in result.items()
            if k not in ("results", "tasks", "rejections", "staged_tasks")
        }
        print(json.dumps(printed, ensure_ascii=False, indent=2))
        return 1 if args.command == "validate" and not result["all_passed"] else 0
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"krt: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
