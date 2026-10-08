"""Current authored Batch 1 report and a deterministic human review queue."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import random

import yaml

from KrRubberStamp.export import (
    DIFFICULTIES,
    checked_measurements,
    collect_authored_tasks,
    task_set_sha256,
)
from KrRubberStamp.io import read_json
from KrRubberStamp.registry import DOMAINS

ROOT = Path(__file__).resolve().parents[1]


def _link(path, output):
    return Path(os.path.relpath(path, output)).as_posix()


def _review_queue(tasks, output, *, project_root, preview, seed):
    heading = "개별 집필 미리보기 검수 대기열" if preview else "Batch 1 사람 검수 대기열"
    lines = [
        f"# {heading}",
        "",
        (
            "미완성 집필본의 편집 검토 자료입니다. 완성된 배치의 배포 보고서가 아닙니다."
            if preview
            else "분야별 무작위 15문항, 총 60문항을 검수 대기 상태로 정리했습니다."
        ),
        "",
        f"무작위 추출 시드는 {seed}입니다. 추출은 문항 선택에만 쓰이며 사실이나 지시문을 생성하지 않습니다. 자동 게이트는 전문가의 독립적인 법률 해석 및 문항 다양성 검수를 대체하지 않습니다.",
        "",
    ]
    rng = random.Random(seed)
    selected = []
    for domain in DOMAINS:
        group = [record for record in tasks if record["task"]["domain"] == domain]
        sample = sorted(
            rng.sample(group, min(15, len(group))), key=lambda record: record["task"]["task_id"]
        )
        for record in sample:
            task, case, directory = record["task"], record["case"], record["path"].parent
            selected.append(task["task_id"])
            gold, trace = read_json(directory / "gold.json"), read_json(directory / "trace.json")
            source = project_root / "authored" / task["authorship"]["source_file"]
            lines += [
                f"## {task['task_id']} ({domain}, {task['difficulty']})",
                "",
                f"집필 제목: {case['title']}",
                "",
                f"업무 목적: {case['work_goal']}",
                "",
                task["instruction"],
                "",
                f"설계 의도: {case['design_rationale']}",
                "",
                f"집필 원고 ID: `{case['case_id']}`, 전체 문항 SHA-256: `{task['authorship']['case_sha256']}`",
                "",
                f"[문항 메타데이터]({_link(directory / 'task.yaml', output)})와 [집필 원고]({_link(source, output)})",
                "",
                "입력 파일:",
                "",
            ]
            for item in task["input_files"]:
                source = directory / item["path"]
                lines.append(f"- [{source.name}]({_link(source, output)}) ({item['format']})")
            lines += [
                "",
                f"정답: [gold.json]({_link(directory / 'gold.json', output)})",
                "",
                "```json",
                json.dumps(gold, ensure_ascii=False, sort_keys=True, indent=2),
                "```",
                "",
                "계산 trace 요약:",
                "",
                "| 규칙 | 결과 |",
                "|---|---|",
            ]
            for step in trace:
                value = json.dumps(step["output"], ensure_ascii=False, sort_keys=True)
                if len(value) > 230:
                    value = value[:227] + "..."
                lines.append(f"| {step['rule_id']} | {value.replace('|', '/')} |")
            lines += [
                "",
                f"전체 계산 입력과 중간값: [trace.json]({_link(directory / 'trace.json', output)})",
                "",
                "검수 상태: 대기. 확인할 항목은 지시문과 증빙의 일치, 판단 과정의 사전 노출, 예외의 실제 계산 영향과 다른 문항에 대한 의미 중복입니다.",
                "",
            ]
    lines += [f"<!-- authored-task-set-sha256: {task_set_sha256(tasks)} -->", ""]
    return "\n".join(lines), selected


def build_reports(
    batch_dir=None,
    measurement_root=None,
    output=None,
    *,
    project_root=None,
    preview=False,
    seed=20261009,
):
    """Fail closed on incomplete release counts or stale fake-solver evidence."""
    project_root = Path(project_root) if project_root else ROOT
    batch_dir = Path(batch_dir) if batch_dir else project_root / "data/batch_1"
    measurement_root = Path(measurement_root) if measurement_root else project_root / "reports"
    output = Path(output) if output else project_root / "reports"
    tasks, manifests = collect_authored_tasks(
        batch_dir.parent,
        [1],
        allow_preview=preview,
        batch_directories={1: batch_dir},
    )
    metrics = checked_measurements(measurement_root, tasks, 1, preview=preview)
    rules_path = project_root / "rules/sources.yaml"
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))["rules"]
    unverified = [rule for rule in rules if rule["verified"] is not True]
    counts = Counter((record["task"]["domain"], record["task"]["difficulty"]) for record in tasks)
    formats = Counter(item["format"] for record in tasks for item in record["task"]["input_files"])
    contracts = Counter(
        record["case"]["facts"].get("source_contract", "literal_engine_facts") for record in tasks
    )
    layouts = Counter(
        str(document.get("template_variant", 0))
        for record in tasks
        for document in record["case"]["documents"]
        if document["format"] != "png"
    )
    file_bytes = sum(path.stat().st_size for path in batch_dir.rglob("*") if path.is_file())
    manifest = manifests[1]
    queue, selected = _review_queue(
        tasks, output, project_root=project_root, preview=preview, seed=seed
    )
    # Release names cannot be produced for an incomplete editorial preview.
    queue_name = "REVIEW_QUEUE_AUTHORED_PREVIEW.md" if preview else "REVIEW_QUEUE_BATCH_1.md"
    report_name = "AUTHORED_PREVIEW_REPORT.md" if preview else "BATCH_1_REPORT.md"
    lines = [
        f"# KrRubberStamp {'개별 집필 미리보기' if preview else 'Batch 1'} 보고서",
        "",
        (
            "미완성 원고의 편집 검토 결과입니다. Batch 1의 1,200문항 완성을 의미하지 않습니다."
            if preview
            else "이번 보고서는 개별 집필을 완료한 Batch 1만 대상으로 합니다."
        ),
        "",
        f"현재 문항 {len(tasks):,}개. 파일 용량은 {file_bytes / 1024**2:.1f} MiB입니다. 모든 문항과 정답을 공개하며 비공개 분할은 없습니다.",
        "",
        "## 집필 방법",
        "",
        "각 문항의 업무 요청과 사실관계 및 문서 배치를 따로 집필했습니다. 숫자와 이름만 변경한 시드 생성본은 이번 집필 평가본에 포함하지 않습니다. 원고에서 규칙 엔진으로 정답과 trace를 먼저 계산하고 이후 입력 문서를 렌더링합니다. 원고의 전체 문항 SHA-256과 요청한 answer_fields를 task.yaml에 기록했습니다.",
        "",
        "재현성은 고정한 개별 원고를 다시 계산하여 gold와 trace의 바이트가 일치하는 방식으로 확인합니다. scenario_seed는 문서 배치에만 사용합니다. 보조 생성기의 새 시드 출력은 이번 평가본과 같은 문항 다양성을 보장하지 않습니다.",
        "",
        "## 분야와 난이도",
        "",
        "| 분야 | easy | medium | hard | 합계 |",
        "|---|---:|---:|---:|---:|",
    ]
    totals = [0, 0, 0]
    for domain in DOMAINS:
        values = [counts[domain, difficulty] for difficulty, _ in DIFFICULTIES]
        totals = [left + right for left, right in zip(totals, values, strict=True)]
        lines.append(f"| {domain} | {values[0]} | {values[1]} | {values[2]} | {sum(values)} |")
    lines += [f"| 합계 | {totals[0]} | {totals[1]} | {totals[2]} | {sum(totals):,} |", ""]
    if not preview:
        lines += ["난이도 비율은 30%, 45%, 25%입니다.", ""]
    lines += ["## 품질 게이트", ""]
    if "validation" in metrics:
        validation = metrics["validation"]["value"]
        lines += [
            f"현재 문항 ID 전체와 일치하는 재검증 {validation['passed']}/{validation['total']} 통과 ({validation['pass_rate']:.0%}). 원고 정답의 바이트 재현과 실제 문서의 값 복원, 지시문 일관성 및 JSON Schema를 확인했습니다.",
            "",
            f"검증 결과: [validation JSON]({_link(metrics['validation']['path'], output)})",
            "",
            "최종 재검증 탈락 사유:",
            "",
            "```json",
            json.dumps(validation["failure_reasons"], ensure_ascii=False, sort_keys=True, indent=2),
            "```",
            "",
        ]
    else:
        lines += [
            "현재 문항 ID에 해당하는 자동 게이트 측정 파일이 없습니다. 통과율을 보고하지 않습니다.",
            "",
        ]
    lines += [
        f"빌드 manifest의 차단 시도 {manifest['rejected_attempts']}건. 이 숫자는 해당 빌드 스냅샷의 기록이며 집필 중 모든 수정과 재작업의 총횟수는 아닙니다.",
        "",
        "manifest 차단 사유:",
        "",
        "```json",
        json.dumps(manifest["failure_reasons"], ensure_ascii=False, sort_keys=True, indent=2),
        "```",
        "",
        "instruction_consistency는 원고와 task.yaml의 지시문 동일성과 예외 수를 확인합니다. 자유문장 안의 사실이나 법률 모순을 독립적으로 분석하는 검사는 아닙니다. 원고 해시와 지시문 및 카나리아의 중복 검사도 의미가 비슷한 문항을 모두 찾아내는 검수가 아닙니다. 집필 다양성과 실제 판단 과정은 사람 검수에서 확인해야 합니다.",
        "",
        "| 문서 형식 | 파일 수 |",
        "|---|---:|",
    ]
    lines += [f"| {fmt} | {count} |" for fmt, count in sorted(formats.items())]
    lines += ["", "| 입력 사실 계약 | 문항 수 |", "|---|---:|"]
    lines += [f"| {contract} | {count} |" for contract, count in sorted(contracts.items())]
    lines += ["", "| 실제 사용한 문서 양식 ID | 파일 수 |", "|---|---:|"]
    lines += [f"| {variant} | {count} |" for variant, count in sorted(layouts.items())]
    lines += [
        "",
        "## 가짜 솔버 결과",
        "",
        "| 솔버 | 문항 수 | 전체 정답률 | 필드 정답률 | 정답 leaf 수 |",
        "|---|---:|---:|---:|---:|",
    ]
    for label in ("oracle", "null"):
        if label in metrics:
            metric = metrics[label]["value"]
            lines.append(
                f"| {label} | {metric['task_count']} | {metric['exact_match']:.0%} | {metric['field_accuracy']:.0%} | {metric['total_fields']} |"
            )
    if not any(label in metrics for label in ("oracle", "null")):
        lines.append("| 측정 없음 | 0 | 해당 없음 | 해당 없음 | 0 |")
    lines += [
        "",
        "oracle은 실제 입력 문서를 추출 맵의 위치로 읽고 엔진을 적용합니다. 정답과 trace 및 집필 원고를 읽어서 답을 만드는 방식이 아닙니다. null은 빈 객체를 제출합니다. 수치는 현재 문항 ID 전체와 일치하는 결과만 사용했습니다. 모델 API와 실제 모델 평가는 실행하지 않았으므로 이 표는 모델 성능 점수가 아닙니다.",
        "",
        "## 공식 예시와 미검증 규칙",
        "",
        f"현재 규칙 출처 {len(rules)}개 중 verified: true는 {len(rules) - len(unverified)}개이며 verified: false는 {len(unverified)}개입니다. 공식 법령 확인과 독립 공식 수치 예시 회귀 검증을 구분합니다.",
        "",
        f"원문 출처: [sources.yaml]({_link(rules_path, output)})",
        "",
        "미검증 규칙:",
        "",
    ]
    lines += [f"- `{rule['rule_id']}`: {rule['description']}" for rule in unverified]
    editorials = [
        ("연말정산 A001부터 A103", "authored_yearend_first103_editorial.md"),
        ("연말정산 A104부터 A203", "authored_yearend_104203_editorial.md"),
        ("급여 B001부터 B153", "authored_payroll_first153_editorial.md"),
        ("부가세 C001부터 C103", "authored_vat_first103_editorial.md"),
        ("문서 추출 첫 50문항", "authored_extract_first50_editorial.md"),
        ("문서 추출 D254부터 D300", "authored_extract_254300_editorial.md"),
    ]
    available = [
        (label, project_root / "reports" / name)
        for label, name in editorials
        if (project_root / "reports" / name).is_file()
    ]
    if available:
        lines += ["", "## 개별 원고 편집 감사", ""]
        lines += [f"- [{label}]({_link(path, output)})" for label, path in available]
        lines += [
            "",
            "각 기록의 명시된 범위에서 질문과 원자료 및 문서 관계를 직접 읽고, 조건을 바꾸어 요청 답의 변화 또는 불변성을 확인했습니다. 발견한 법률 전제와 날짜 모순 및 의미 중복을 교정했습니다. 이 기록을 전체 1,200문항의 전문가 승인으로 확대하지 않습니다.",
            "",
        ]
    lines += [
        "",
        "연말정산 공식 전체 정산 예시와 간이세액표의 공식 숫자 셀, 부가세 완성 신고서 사례는 서로 다른 근거 단위입니다. 한 사례의 여러 중간값을 여러 독립 완성 사례로 세지 않습니다. 세부 범위는 각 분야 연구 보고서에서 확인해야 합니다. 분야 D는 자체 업무 집계 규약이므로 대응하는 국세청이나 공단 공식 예시가 없습니다.",
        "",
        "## 사람 검수",
        "",
        f"[검수 대기열]({queue_name})에 {len(selected)}문항을 정리했습니다. 현재 상태는 검수 대기입니다. 각 항목에는 업무 목적과 설계 의도, 한국어 지시문과 입력 파일, 정답 및 trace가 있습니다.",
        "",
        "## 알려진 한계와 다음 배치 개선",
        "",
        "- 공식 규정과 숫자 회귀 테스트를 확보했지만 모든 조건 조합의 독립적인 세무 검수를 완료한 것은 아닙니다. verified: false 규칙과 개별 증빙 판단을 우선 검수해야 합니다.",
        "- 연말정산은 국내 거주자의 근로소득 정산 범위를 따릅니다. 지원하는 공제의 구체적인 증빙 조건과 제외 항목은 개별 입력과 분야 연구 보고서에 따릅니다.",
        "- 부가세는 정확히 나누어떨어지는 국내 10% 과세 거래 범위를 따릅니다. 면세 겸업 공통매입 안분과 영세율 및 가산세 등은 지원하지 않습니다.",
        "- PNG는 원본 PDF에서도 같은 사실을 읽을 수 있는 중복 자료입니다. 스캔만 있는 한국어 OCR 평가 품질을 검증한 것으로 주장하지 않습니다.",
        "- HWPX의 ZIP 및 XML 구조와 독립 파싱을 확인했습니다. 한컴 앱에서 열기와 인쇄 호환성은 별도로 검수해야 합니다.",
        "- 렌더러는 공통 표 기반 양식 5종을 지원합니다. 실제 관공서 양식의 시각적인 복제나 각 회사의 구조를 모두 재현하지 않았습니다.",
        "- 가짜 oracle은 입력과 엔진의 일치를 확인합니다. 모든 세법 해석과 문항의 의미상 다양성을 보증하는 검사는 아닙니다.",
        "- 모델의 Python 실행은 네트워크를 차단한 Docker 컨테이너를 사용하도록 구현했습니다. 구축 호스트의 Docker 엔진을 사용할 수 없어 실제 컨테이너 실행은 검증하지 못했습니다. 신뢰된 로컬 가짜 솔버는 운영 보안 인증이 아닙니다.",
        "",
        "## 공개 준비",
        "",
        "코드는 Apache-2.0, 합성 데이터는 CC-BY-4.0이며 폰트는 OFL입니다. 공식 원문은 해당 저작권에 따르며 합성 데이터 라이선스로 재허가하지 않습니다.",
        "",
        (
            "미완성 미리보기는 완성 배포본의 파일명과 내보내기 이름으로 게시할 수 없습니다."
            if preview
            else "uv run krt export-hf --batch 1은 KrRubberStamp-1.2K JSONL과 입력 파일, 공개 정답 및 집필 원고 스냅샷과 데이터카드를 만듭니다. Hugging Face 업로드는 실행하지 않았습니다."
        ),
        "",
        "각 문항과 데이터카드에 카나리아 GUID를 제공합니다. 카나리아 인지만으로 모델의 학습 포함을 확정할 수는 없습니다. 하네스는 입력 문서와 지시문 및 답안 스키마만 제공하며 공개 원고와 정답, trace와 추출 맵 및 카나리아 메타데이터를 모델에 제공하지 않습니다.",
        "",
    ]
    lines += [f"<!-- authored-task-set-sha256: {task_set_sha256(tasks)} -->", ""]
    output.mkdir(parents=True, exist_ok=True)
    (output / queue_name).write_text(queue, encoding="utf-8")
    (output / report_name).write_text("\n".join(lines), encoding="utf-8")
    return {
        "tasks": len(tasks),
        "review_tasks": len(selected),
        "bytes": file_bytes,
        "preview": preview,
        "report": str(output / report_name),
        "review_queue": str(output / queue_name),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/batch_1")
    parser.add_argument("--measurements", type=Path, default=ROOT / "reports")
    parser.add_argument("--output", type=Path, default=ROOT / "reports")
    parser.add_argument(
        "--preview", action="store_true", help="Write explicitly incomplete editorial reports"
    )
    parser.add_argument("--seed", type=int, default=20261009, help="Human review selection only")
    args = parser.parse_args(argv)
    try:
        result = build_reports(
            args.data, args.measurements, args.output, preview=args.preview, seed=args.seed
        )
    except (OSError, ValueError) as exc:
        parser.exit(2, f"build_reports: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
