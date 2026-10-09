"""Offline export of individually written cases. Never uploads or calls a model."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import yaml

from . import authoring
from .io import json_bytes, read_json, write_json
from .registry import DOMAINS, PERIODS, calculate
from .tasks import canary_for, make_schema, scenario_hash

DIFFICULTIES = (("easy", 90), ("medium", 135), ("hard", 75))
SUPPORT_REPORTS = (
    "EXPANSION_DIVERSITY_GUIDE.md",
    "extract_fulfillment_contract.md",
    "extract_fulfillment_legacy_integrity.json",
    "extract_procurement_contract.md",
    "extract_cart_procurement_contract.md",
    "yearend_holder_contract.md",
    "expansion_contracts_legacy_integrity.json",
    "expansion_contracts_integration.md",
    "yearend_pay_statement_contract.md",
    "payroll_bank_reconciliation_contract.md",
    "vat_document_reconciliation_contract.md",
    "vat_document_lifecycle_contract.md",
    "authored_vat_204300_editorial.md",
    "audit_evidence/vat_204300/C243_baseline_page_1.png",
    "audit_evidence/vat_204300/C272_post_tire_page_1.png",
    "audit_evidence/vat_204300/C290_baseline_page_1.png",
    "audit_evidence/vat_204300/C290_source_edit_page_1.png",
    "audit_evidence/vat_204300/C291_baseline_page_1.png",
    "audit_evidence/vat_204300/C300_baseline_page_1.png",
    "audit_evidence/vat_204300/original_cases.json",
    "audit_evidence/vat_204300/physical/C243/extraction_map.json",
    "audit_evidence/vat_204300/physical/C243/inputs/대여신고.hwpx",
    "audit_evidence/vat_204300/physical/C243/inputs/등록전정비.hwpx",
    "audit_evidence/vat_204300/physical/C243/inputs/등록후정비.hwpx",
    "audit_evidence/vat_204300/physical/C243/inputs/전정비카드.pdf",
    "audit_evidence/vat_204300/physical/C243/inputs/차량기간.xlsx",
    "audit_evidence/vat_204300/physical/C243/inputs/칠월정비.xlsx",
    "audit_evidence/vat_204300/physical/C243/inputs/칠월카드.pdf",
    "audit_evidence/vat_204300/physical/C243/inputs/허가업무.pdf",
    "audit_evidence/vat_204300/physical/C243/inputs/후정비카드.pdf",
    "audit_evidence/vat_204300/physical/C290/extraction_map.json",
    "audit_evidence/vat_204300/physical/C290/inputs/7월인도.xlsx",
    "audit_evidence/vat_204300/physical/C290/inputs/반기범위.xlsx",
    "audit_evidence/vat_204300/physical/C290/inputs/소액갑.pdf",
    "audit_evidence/vat_204300/physical/C290/inputs/소액을.hwpx",
    "audit_evidence/vat_204300/physical/C290/inputs/실사용.hwpx",
    "audit_evidence/vat_204300/physical/C290/inputs/실스캔.png",
    "audit_evidence/vat_204300/physical/C290/inputs/실원본.pdf",
    "audit_evidence/vat_204300/physical/C290/inputs/이전금액.hwpx",
    "audit_evidence/vat_204300/physical/C290/inputs/판매업종.pdf",
    "audit_evidence/vat_204300/physical/C291/extraction_map.json",
    "audit_evidence/vat_204300/physical/C291/inputs/갑영수.pdf",
    "audit_evidence/vat_204300/physical/C291/inputs/갑인수.xlsx",
    "audit_evidence/vat_204300/physical/C291/inputs/강의설치.pdf",
    "audit_evidence/vat_204300/physical/C291/inputs/공급자명칭.hwpx",
    "audit_evidence/vat_204300/physical/C291/inputs/사업신고.pdf",
    "audit_evidence/vat_204300/physical/C291/inputs/설치전자.hwpx",
    "audit_evidence/vat_204300/physical/C291/inputs/을영수.xlsx",
    "audit_evidence/vat_204300/physical/C291/inputs/을인수.hwpx",
    "audit_evidence/vat_204300/physical/C291/inputs/키트부서.pdf",
    "audit_evidence/vat_204300/physical/C300/extraction_map.json",
    "audit_evidence/vat_204300/physical/C300/inputs/결산인계.pdf",
    "audit_evidence/vat_204300/physical/C300/inputs/교실사용.hwpx",
    "audit_evidence/vat_204300/physical/C300/inputs/납품마감.pdf",
    "audit_evidence/vat_204300/physical/C300/inputs/반입인수.hwpx",
    "audit_evidence/vat_204300/physical/C300/inputs/유효고지.xlsx",
    "audit_evidence/vat_204300/physical/C300/inputs/음료원본.pdf",
    "audit_evidence/vat_204300/physical/C300/inputs/재료전자.hwpx",
    "audit_evidence/vat_204300/physical/C300/inputs/재료카드.xlsx",
    "audit_evidence/vat_204300/physical/C300/inputs/차량업무.xlsx",
    "audit_evidence/vat_204300/physical/C300/inputs/차량청구.pdf",
    "audit_evidence/vat_204300/physical_cf/C243/extraction_map.json",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/대여신고.hwpx",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/등록전정비.hwpx",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/등록후정비.hwpx",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/전정비카드.pdf",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/차량기간.xlsx",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/칠월정비.xlsx",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/칠월카드.pdf",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/허가업무.pdf",
    "audit_evidence/vat_204300/physical_cf/C243/inputs/후정비카드.pdf",
    "audit_evidence/vat_204300/physical_cf/C290/extraction_map.json",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/7월인도.xlsx",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/반기범위.xlsx",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/소액갑.pdf",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/소액을.hwpx",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/실사용.hwpx",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/실스캔.png",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/실원본.pdf",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/이전금액.hwpx",
    "audit_evidence/vat_204300/physical_cf/C290/inputs/판매업종.pdf",
    "audit_evidence/vat_204300/physical_cf/C291/extraction_map.json",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/갑영수.pdf",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/갑인수.xlsx",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/강의설치.pdf",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/공급자명칭.hwpx",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/사업신고.pdf",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/설치전자.hwpx",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/을영수.xlsx",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/을인수.hwpx",
    "audit_evidence/vat_204300/physical_cf/C291/inputs/키트부서.pdf",
    "audit_evidence/vat_204300/physical_cf/C300/extraction_map.json",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/결산인계.pdf",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/교실사용.hwpx",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/납품마감.pdf",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/반입인수.hwpx",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/유효고지.xlsx",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/음료원본.pdf",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/재료전자.hwpx",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/재료카드.xlsx",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/차량업무.xlsx",
    "audit_evidence/vat_204300/physical_cf/C300/inputs/차량청구.pdf",
    "audit_evidence/vat_204300/physical_post/C272/extraction_map.json",
    "audit_evidence/vat_204300/physical_post/C272/inputs/기간별허가.xlsx",
    "audit_evidence/vat_204300/physical_post/C272/inputs/매입검토.pdf",
    "audit_evidence/vat_204300/physical_post/C272/inputs/상품화발급.pdf",
    "audit_evidence/vat_204300/physical_post/C272/inputs/정비실적.hwpx",
    "audit_evidence/vat_204300/physical_post/C272/inputs/차량전환.hwpx",
    "audit_evidence/vat_204300/physical_post/C272/inputs/타이어카드.pdf",
    "audit_evidence/vat_204300/physical_post_cf/C272/extraction_map.json",
    "audit_evidence/vat_204300/physical_post_cf/C272/inputs/기간별허가.xlsx",
    "audit_evidence/vat_204300/physical_post_cf/C272/inputs/매입검토.pdf",
    "audit_evidence/vat_204300/physical_post_cf/C272/inputs/상품화발급.pdf",
    "audit_evidence/vat_204300/physical_post_cf/C272/inputs/정비실적.hwpx",
    "audit_evidence/vat_204300/physical_post_cf/C272/inputs/차량전환.hwpx",
    "audit_evidence/vat_204300/physical_post_cf/C272/inputs/타이어카드.pdf",
    "audit_evidence/vat_204300/post_cases.json",
    "audit_evidence/vat_204300/post_counterfactuals.json",
    "audit_evidence/vat_204300/post_legal_checks.json",
    "audit_evidence/vat_204300/post_physical_checks.json",
    "audit_evidence/vat_204300/post_scope.json",
    "audit_evidence/vat_204300/post_sources.json",
    "audit_evidence/vat_204300/proof_manifest.json",
    "audit_evidence/vat_204300/replay_proof.py",
    "authored_payroll_254300_editorial.md",
    "audit_evidence/payroll_254300/calendar_checks.json",
    "audit_evidence/payroll_254300/checks.json",
    "audit_evidence/payroll_254300/counterfactuals.json",
    "audit_evidence/payroll_254300/manifest.json",
    "audit_evidence/payroll_254300/physical_roundtrip.json",
    "audit_evidence/payroll_254300/post_calendar_checks.json",
    "audit_evidence/payroll_254300/post_checks.json",
    "audit_evidence/payroll_254300/post_counterfactuals.json",
    "audit_evidence/payroll_254300/post_physical.json",
    "audit_evidence/payroll_254300/post_reference_checks.json",
    "audit_evidence/payroll_254300/post_review.json",
    "audit_evidence/payroll_254300/post_scope.json",
    "audit_evidence/payroll_254300/post_sources.json",
    "audit_evidence/payroll_254300/reference_checks.json",
    "audit_evidence/payroll_254300/scope.json",
    "audit_evidence/payroll_254300/sources.json",
    "authored_yearend_204300_editorial.md",
    "audit_evidence/yearend_204300/post_checks.json",
    "audit_evidence/yearend_204300/post_counterfactuals.json",
    "audit_evidence/yearend_204300/post_earned_only_coherence.json",
    "audit_evidence/yearend_204300/post_editorial_findings.json",
    "audit_evidence/yearend_204300/post_guard_checks.json",
    "audit_evidence/yearend_204300/post_physical_checks.json",
    "audit_evidence/yearend_204300/post_primary_sources.json",
    "audit_evidence/yearend_204300/post_sources.json",
    "authored_payroll_154253_editorial.md",
    "audit_evidence/payroll_154253/checks.json",
    "audit_evidence/payroll_154253/counterfactuals.json",
    "audit_evidence/payroll_154253/current_calendar_checks.json",
    "audit_evidence/payroll_154253/current_cf_checks.json",
    "audit_evidence/payroll_154253/current_cf_reference_checks.json",
    "audit_evidence/payroll_154253/current_cf_sources.json",
    "audit_evidence/payroll_154253/current_counterfactuals.json",
    "audit_evidence/payroll_154253/current_physical_roundtrip.json",
    "audit_evidence/payroll_154253/current_relationships.json",
    "audit_evidence/payroll_154253/current_scope.json",
    "audit_evidence/payroll_154253/owned_paths.json",
    "audit_evidence/payroll_154253/physical_roundtrip.json",
    "audit_evidence/payroll_154253/post_checks.json",
    "audit_evidence/payroll_154253/post_differences.json",
    "audit_evidence/payroll_154253/post_reference_checks.json",
    "audit_evidence/payroll_154253/post_sources.json",
    "audit_evidence/payroll_154253/reference_checks.json",
    "audit_evidence/payroll_154253/scope.json",
    "audit_evidence/payroll_154253/sources.json",
    "research_yearend.md",
    "research_payroll.md",
    "research_vat.md",
    "unverified_rules.md",
    "render_design.md",
    "harness_design.md",
    "payroll_effective_date_audit.md",
    "vat_evidence_contract.md",
    "extract_evidence_contract.md",
    "yearend_evidence_contract.md",
    "authored_yearend_first103_editorial.md",
    "authored_yearend_104203_editorial.md",
    "audit_evidence/yearend_104203/post_snapshot.json",
    "audit_evidence/yearend_104203/post_counterfactuals.json",
    "audit_evidence/yearend_104203/post_physical_checks.json",
    "audit_evidence/yearend_104203/physical_checks.json",
    "audit_evidence/yearend_104203/earned_only_coherence.json",
    "audit_evidence/yearend_104203/post_mortgage_guards.json",
    "audit_evidence/yearend_104203/guard_checks.json",
    "authored_extract_first50_editorial.md",
    "authored_extract_254300_editorial.md",
    "audit_evidence/extract_254300/scope.json",
    "audit_evidence/extract_254300/counterfactuals.json",
    "audit_evidence/extract_254300/post_scope.json",
    "audit_evidence/extract_254300/post_checks.json",
    "audit_evidence/extract_254300/post_counterfactuals.json",
    "audit_evidence/extract_254300/physical.json",
    "audit_evidence/extract_254300/post_physical.json",
    "audit_evidence/extract_254300/independent_arithmetic.json",
    "authored_vat_first103_editorial.md",
    "authored_payroll_first153_editorial.md",
    "audit_evidence/payroll_first153/scope.json",
    "audit_evidence/payroll_first153/sources.json",
    "audit_evidence/payroll_first153/counterfactuals.json",
    "audit_evidence/payroll_first153/post_sources.json",
    "audit_evidence/payroll_first153/post_checks.json",
    "audit_evidence/payroll_first153/post_reference_checks.json",
    "audit_evidence/vat_first103/post_counterfactuals.json",
    "audit_evidence/vat_first103/post_engine_plan_checks.json",
    "audit_evidence/vat_first103/post_visible_source_cf.json",
    "audit_evidence/vat_first103/post_snapshot.json",
)


def _relative(raw):
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"Invalid artifact path: {raw}")
    return path


def collect_authored_tasks(data_root, batches, *, allow_preview=False, batch_directories=None):
    """Check release identity and current literal sources before creating output.

    A preview is a deliberately incomplete editorial set. Generated cases cannot
    be reclassified as authored by passing the preview flag.
    """
    data_root = Path(data_root)
    if (
        not batches
        or len(set(batches)) != len(batches)
        or any(
            type(batch) is not int or batch not in authoring.AUTHORIZED_BATCHES for batch in batches
        )
    ):
        raise ValueError("Select unique authorized batch numbers: 1 and 2")
    tasks, manifests, seen = [], {}, set()
    for batch in sorted(batches):
        directory = (
            Path(batch_directories[batch])
            if batch_directories and batch in batch_directories
            else data_root / f"batch_{batch}"
        )
        if not directory.is_dir():
            raise FileNotFoundError(f"Batch {batch} is absent: {directory}")
        manifest = read_json(directory / "manifest.json")
        if manifest.get("authorship") != "individually_written":
            raise ValueError("Only individually written task sets may be exported or reported")
        if manifest.get("batch") != batch or (manifest.get("preview") and not allow_preview):
            raise ValueError("A preview cannot be published as a completed batch")
        records = []
        for path in sorted(directory.glob("*/*/task.yaml")):
            task = yaml.safe_load(path.read_text(encoding="utf-8"))
            if task.get("authorship", {}).get("method") != "individually_written":
                raise ValueError(f"Task is not individually written: {path}")
            if task["task_id"] in seen or path.parent.name != task["task_id"]:
                raise ValueError("Task identities must be unique and match their directories")
            if path.parent.parent.name != task["domain"] or task["domain"] not in DOMAINS:
                raise ValueError("Task domain and directory disagree")
            seen.add(task["task_id"])
            case = authoring.recover_case(task)
            if (
                task["task_id"] != f"B{batch}_{case['case_id']}_{scenario_hash(case)[:8]}"
                or task.get("scenario_hash") != scenario_hash(case["facts"])
                or task.get("reference_period") != PERIODS[task["domain"]]
            ):
                raise ValueError(f"Task identity or fact provenance differs: {path}")
            answer, trace = calculate(task["domain"], case["facts"])
            if (
                task.get("instruction") != case["instruction"]
                or task.get("answer_fields") != case["answer_fields"]
            ):
                raise ValueError(f"Authored instruction or answer request changed: {path}")
            gold = authoring.project_answer(answer, case["answer_fields"])
            if task.get("answer_schema") != make_schema(gold):
                raise ValueError(f"Answer schema differs from the current authored gold: {path}")
            if (path.parent / "gold.json").read_bytes() != json_bytes(gold) or (
                path.parent / "trace.json"
            ).read_bytes() != json_bytes(trace):
                raise ValueError(f"Current source does not reproduce gold and trace: {path}")
            for item in task["input_files"]:
                relative = _relative(item["path"])
                if relative.parts[0] != "inputs":
                    raise ValueError("Input documents must remain inside inputs/")
                if not (path.parent / relative).is_file():
                    raise FileNotFoundError(path.parent / relative)
            if not (path.parent / "extraction_map.json").is_file():
                raise FileNotFoundError(path.parent / "extraction_map.json")
            records.append({"batch": batch, "task": task, "path": path, "case": case})
        if not records:
            raise ValueError("No individually written tasks found")
        ids = {record["task"]["task_id"] for record in records}
        listed = manifest.get("tasks", [])
        if (
            len(listed) != len(records)
            or {item["task_id"] for item in listed} != ids
            or manifest.get("requested") != len(records)
            or manifest.get("accepted") != len(records)
        ):
            raise ValueError("Manifest does not describe the selected task set")
        counts = Counter(
            (record["task"]["domain"], record["task"]["difficulty"]) for record in records
        )
        if not allow_preview and (
            len(records) != 1200
            or any(
                counts[domain, difficulty] != n
                for domain in DOMAINS
                for difficulty, n in DIFFICULTIES
            )
        ):
            raise ValueError("Release requires 300 authored cases per domain with 90/135/75 counts")
        manifests[batch] = manifest
        tasks.extend(records)
    instructions = [record["case"]["instruction"] for record in tasks]
    fact_hashes = [record["task"]["scenario_hash"] for record in tasks]
    if len(set(instructions)) != len(tasks) or len(set(fact_hashes)) != len(tasks):
        raise ValueError("Authored instruction and fact hashes must be unique")
    canaries = [record["task"]["canary"] for record in tasks]
    if len(set(canaries)) != len(canaries):
        raise ValueError("Task canaries must be unique")
    return tasks, manifests


def task_set_sha256(tasks):
    records = [
        {
            "batch": record["batch"],
            "task_id": record["task"]["task_id"],
            "case_sha256": record["task"]["authorship"]["case_sha256"],
        }
        for record in sorted(tasks, key=lambda record: record["task"]["task_id"])
    ]
    return hashlib.sha256(json_bytes(records)).hexdigest()


def checked_measurements(report_root, tasks, batch, *, preview=False):
    """Accept only current validation and fake-solver results for exactly these IDs."""
    report_root = Path(report_root)
    suffix = "authored_preview" if preview else f"batch_{batch}"
    ids = {record["task"]["task_id"] for record in tasks if record["batch"] == batch}
    evidence = {}
    for label in ("validation", "oracle", "null"):
        path = report_root / f"{label}_{suffix}.json"
        if not path.is_file():
            if preview:
                continue
            raise FileNotFoundError(f"Current {label} measurements are required: {path}")
        value = read_json(path)
        key = "results" if label == "validation" else "tasks"
        records = value.get(key, [])
        measured_ids = [item.get("task_id") for item in records]
        if len(measured_ids) != len(ids) or set(measured_ids) != ids:
            raise ValueError(f"{label} measurements describe another task set: {path}")
        if label == "validation":
            if (
                value.get("total") != len(ids)
                or value.get("passed") != len(ids)
                or value.get("failed") != 0
                or value.get("pass_rate") != 1
                or not value.get("all_passed")
                or value.get("failure_reasons")
                or not all(item.get("passed") and not item.get("errors") for item in records)
            ):
                raise ValueError("All current authored tasks must pass validation")
        else:
            expected = 1 if label == "oracle" else 0
            fields = sum(item["total_fields"] for item in records)
            correct = sum(item["correct_fields"] for item in records)
            exact = sum(item["exact_match"] for item in records) / len(ids)
            accuracy = correct / fields if fields else 0
            if (
                value.get("solver") != label
                or value.get("task_count") != len(ids)
                or value.get("total_fields") != fields
                or value.get("correct_fields") != correct
                or value.get("exact_match") != exact
                or value.get("field_accuracy") != accuracy
                or exact != expected
                or accuracy != expected
            ):
                raise ValueError(f"Current {label} measurements fail the fake-solver contract")
        evidence[label] = {"path": path, "value": value}
    return evidence


def _document_root():
    checkout = Path(__file__).resolve().parents[1]
    return (
        checkout if (checkout / "DATA_LICENSE").is_file() else Path(__file__).parent / "resources"
    )


def _rule_path():
    import rules

    return Path(rules.__file__).parent / "sources.yaml"


def export_hf(
    data_root: Path,
    batches: list[int],
    output: Path,
    *,
    allow_preview=False,
    batch_directories=None,
):
    """Write the Hub-compatible JSONL and a self-contained offline snapshot.

    The unchanged CLI calls the release path. ``allow_preview`` is for explicit
    editorial verification through Python and never gives a completed-release name.
    """
    data_root, output = Path(data_root), Path(output)
    if batch_directories and not allow_preview:
        raise ValueError("Batch path overrides are only permitted for an editorial preview")
    tasks, manifests = collect_authored_tasks(
        data_root,
        batches,
        allow_preview=allow_preview,
        batch_directories=batch_directories,
    )
    document_root = _document_root()
    evidence = {
        batch: checked_measurements(document_root / "reports", tasks, batch, preview=allow_preview)
        for batch in batches
    }
    rules = yaml.safe_load(_rule_path().read_text(encoding="utf-8"))["rules"]
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise FileExistsError(f"Refusing to overwrite export: {output}")
    if any(
        output.resolve() == path or path in output.resolve().parents
        for path in (data_root.resolve(),)
    ):
        raise ValueError("Export must be outside the source task tree")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    try:
        result = _write_export(
            tasks,
            manifests,
            evidence,
            rules,
            document_root,
            batches,
            temporary,
            preview=allow_preview,
        )
        if output.exists():
            output.rmdir()
        temporary.rename(output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    result["output"] = str(output)
    return result


def _write_export(tasks, manifests, evidence, rules, document_root, batches, output, *, preview):
    (output / "data").mkdir()
    n = len(tasks)
    size = f"{n / 1000:.1f}K" if n >= 1000 else str(n)
    name = f"KrRubberStamp-{'preview-' if preview else ''}{size}"
    source_records = defaultdict(dict)
    counts = Counter()
    formats = Counter()
    contracts = Counter()
    layouts = Counter()
    digest = hashlib.sha256()
    with (output / "data/train.jsonl").open("w", encoding="utf-8") as stream:
        for record in tasks:
            task, task_dir, batch, case = (
                record["task"],
                record["path"].parent,
                record["batch"],
                record["case"],
            )
            relative = Path("data") / f"batch_{batch}" / task["domain"] / task["task_id"]
            target = output / relative
            target.mkdir(parents=True)
            # Only declared documents and public benchmark artifacts are included.
            for filename in ("task.yaml", "gold.json", "trace.json", "extraction_map.json"):
                shutil.copy2(task_dir / filename, target / filename)
            for item in task["input_files"]:
                destination = target / _relative(item["path"])
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(task_dir / item["path"], destination)
            provenance = task["authorship"]
            source = _relative(provenance["source_file"]).as_posix()
            source_records[source][provenance["case_id"]] = case
            row = {
                "task_id": task["task_id"],
                "domain": task["domain"],
                "difficulty": task["difficulty"],
                "reference_period": task["reference_period"],
                "instruction": task["instruction"],
                "canary": task["canary"],
                "scenario_hash": task["scenario_hash"],
                "authorship": provenance,
                "answer_fields": task["answer_fields"],
                "input_files": [
                    {"path": f"{relative.as_posix()}/{item['path']}", "format": item["format"]}
                    for item in task["input_files"]
                ],
                "answer_schema": json.dumps(
                    task["answer_schema"], ensure_ascii=False, sort_keys=True
                ),
                "gold": json.dumps(
                    read_json(task_dir / "gold.json"), ensure_ascii=False, sort_keys=True
                ),
                "trace": json.dumps(
                    read_json(task_dir / "trace.json"), ensure_ascii=False, sort_keys=True
                ),
                "task_path": (relative / "task.yaml").as_posix(),
                "gold_path": (relative / "gold.json").as_posix(),
                "trace_path": (relative / "trace.json").as_posix(),
                "extraction_map_path": (relative / "extraction_map.json").as_posix(),
                "authored_source_path": f"authored/{source}",
            }
            content = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            stream.write(content)
            digest.update(content.encode("utf-8"))
            counts[f"{task['domain']}/{task['difficulty']}"] += 1
            formats.update(item["format"] for item in task["input_files"])
            contracts[case["facts"].get("source_contract", "literal_engine_facts")] += 1
            layouts.update(
                str(document.get("template_variant", 0))
                for document in case["documents"]
                if document["format"] != "png"
            )
    for source, cases in source_records.items():
        write_json(output / "authored" / source, [cases[key] for key in sorted(cases)])
    for batch, manifest in manifests.items():
        write_json(output / "data" / f"batch_{batch}" / "manifest.json", manifest)
    fingerprint = digest.hexdigest()
    card_canary = canary_for(f"dataset-card/{name}/{fingerprint}")
    summary = {
        "dataset_name": name,
        "rows": n,
        "batches": sorted(batches),
        "preview": preview,
        "authorship": "individually_written",
        "counts": dict(sorted(counts.items())),
        "document_formats": dict(sorted(formats.items())),
        "source_contracts": dict(sorted(contracts.items())),
        "layout_variants_used": dict(sorted(layouts.items())),
        "task_set_sha256": task_set_sha256(tasks),
        "rule_sources": {
            "total": len(rules),
            "verified": sum(rule["verified"] is True for rule in rules),
            "unverified": sum(rule["verified"] is not True for rule in rules),
        },
        "measurements": {
            str(batch): {
                label: {
                    key: item["value"][key]
                    for key in (
                        ("total", "passed", "failed", "pass_rate")
                        if label == "validation"
                        else (
                            "task_count",
                            "exact_match",
                            "field_accuracy",
                            "total_fields",
                            "correct_fields",
                        )
                    )
                }
                for label, item in values.items()
            }
            for batch, values in evidence.items()
        },
        "jsonl_sha256": fingerprint,
        "canary": card_canary,
        "uploaded": False,
        "actual_model_evaluated": False,
    }
    write_json(output / "export_manifest.json", summary)
    (output / "README.md").write_text(_dataset_card(summary), encoding="utf-8")
    for filename in ("DATA_LICENSE", "LICENSE", "DECISIONS.md", "DATA_SPEC.md"):
        shutil.copy2(document_root / filename, output / filename)
    (output / "reports").mkdir()
    for filename in SUPPORT_REPORTS:
        path = document_root / "reports" / filename
        if path.is_file():
            (output / "reports" / filename).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, output / "reports" / filename)
    for batch, values in evidence.items():
        for item in values.values():
            shutil.copy2(item["path"], output / "reports" / item["path"].name)
        for path in sorted((document_root / "reports").glob(f"authored_batch_{batch}_*.md")):
            shutil.copy2(path, output / "reports" / path.name)
        acceptance = document_root / "reports" / f"authoring_acceptance_batch_{batch}.json"
        if acceptance.is_file():
            shutil.copy2(acceptance, output / "reports" / acceptance.name)
        audit_path = document_root / "reports" / "audit_evidence" / f"batch_{batch}"
        if audit_path.is_dir():
            shutil.copytree(audit_path, output / "reports" / "audit_evidence" / f"batch_{batch}")
        if not preview:
            for filename in (f"BATCH_{batch}_REPORT.md", f"REVIEW_QUEUE_BATCH_{batch}.md"):
                path = document_root / "reports" / filename
                if not path.is_file():
                    raise FileNotFoundError(f"Completed release reports are required: {path}")
                marker = f"<!-- authored-task-set-sha256: {task_set_sha256([record for record in tasks if record['batch'] == batch])} -->"
                if marker not in path.read_text(encoding="utf-8"):
                    raise ValueError(f"Release report belongs to another authored task set: {path}")
                shutil.copy2(path, output / "reports" / filename)
    (output / "rules").mkdir()
    shutil.copy2(_rule_path(), output / "rules/sources.yaml")
    shutil.copy2(_rule_path(), output / "sources.yaml")
    return summary


def _dataset_card(summary, *, repo_id=None):
    name = summary["dataset_name"]
    status = (
        "편집 검토용 미완성 미리보기입니다. 완성된 Batch 1 배포본이 아닙니다."
        if summary["preview"]
        else f"{len(summary['batches'])}개 배치의 개별 집필 문항입니다. 각 배치는 분야별 300문항이며 누적 분야별 문항 수는 {summary['rows'] // 4:,}개입니다."
    )
    lines = [
        "---",
        "license: cc-by-4.0",
        "language:",
        "  - ko",
        "task_categories:",
        "  - question-answering",
        "  - tabular-to-text",
        "tags:",
        "  - synthetic",
        "  - benchmark",
        "  - korean",
        "configs:",
        "  - config_name: default",
        "    data_files:",
        "      - split: train",
        "        path: data/train.jsonl",
        "---",
        f"# {name}",
        "",
        "Korean office rubber stamp, as an AI benchmark dataset: auto-graded tasks on year-end tax, payroll, VAT, and document extraction.",
        "",
        status,
        "",
        f"공개 합성 문항 {summary['rows']:,}개. Batch {', '.join(map(str, summary['batches']))}. 모든 정답을 공개하며 비공개 분할은 없습니다.",
        "",
        "각 문항의 업무 요청과 사실관계 및 문서 배치는 코딩 에이전트가 별도로 집필했습니다. 반복 템플릿에 숫자와 이름만 바꾸는 생성본은 이 평가본에 포함하지 않습니다. 집필 원고에서 규칙 엔진이 정답과 계산 trace를 먼저 산출하고 이후 입력 문서를 렌더링합니다. 원고는 authored/에 있으며 문항별 authorship에 원고 경로와 전체 문항 SHA-256을 기록합니다.",
        "",
        "원고를 수정하면 집필 의도와 증빙 관계를 다시 검토해야 합니다. 보조용 krt generate의 새 시드 출력은 개별 집필 평가본을 대체하지 않으며 같은 문항 다양성을 보장하지 않습니다. 집필본 재현에는 krt build-authored를 사용합니다. 메타데이터의 scenario_seed는 문서 배치에만 사용합니다.",
        "",
        "주 지표는 문항 전체 정답률입니다. 숫자는 원 단위 정수의 정확 일치로 채점합니다. 문자열은 NFKC와 공백 제거 및 대소문자 정규화 후 일치로 채점합니다. 필드 점수는 정답의 leaf 항목을 기준으로 집계합니다. LLM 심사위원을 사용하지 않습니다.",
        "",
        "연말정산은 2025년 귀속, 급여는 2026년, 부가세는 2026년 제1기 일반과세자 기준입니다. 각 문항이 요청한 answer_fields만 답안에 포함합니다.",
        "",
        "| 분야 | easy | medium | hard | 합계 |",
        "|---|---:|---:|---:|---:|",
    ]
    for domain in DOMAINS:
        values = [
            summary["counts"].get(f"{domain}/{difficulty}", 0) for difficulty, _ in DIFFICULTIES
        ]
        lines.append(f"| {domain} | {values[0]} | {values[1]} | {values[2]} | {sum(values)} |")
    lines += ["", "| 문서 형식 | 파일 수 |", "|---|---:|"]
    lines += [f"| {key} | {value} |" for key, value in summary["document_formats"].items()]
    lines += [
        "",
        f"이 내보내기에 실제 사용한 문서 양식은 {len(summary['layout_variants_used'])}종입니다. 양식 ID별 파일 수는 export_manifest.json의 layout_variants_used에 기록합니다.",
    ]
    rules = summary["rule_sources"]
    lines += [
        "",
        f"규칙 출처 {rules['total']}개 중 공식 수치 회귀 검증이 있는 규칙은 {rules['verified']}개이며 verified: false는 {rules['unverified']}개입니다. 법령의 공식 확인과 독립적인 공식 숫자 예시의 회귀 검증을 구분합니다. 원문 출처는 [sources.yaml](rules/sources.yaml)을 확인해 주세요.",
        "",
        "| 배치 | 검증 통과 | 솔버 | 문항 수 | 전체 정답률 | 필드 정답률 |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for batch, values in sorted(summary["measurements"].items()):
        validation = values.get("validation")
        passed = f"{validation['passed']}/{validation['total']}" if validation else "측정 없음"
        for label in ("oracle", "null"):
            metric = values.get(label)
            if metric:
                lines.append(
                    f"| {batch} | {passed} | {label} | {metric['task_count']} | {metric['exact_match']:.0%} | {metric['field_accuracy']:.0%} |"
                )
        if not any(label in values for label in ("oracle", "null")):
            lines.append(f"| {batch} | {passed} | 측정 없음 | 0 | 해당 없음 | 해당 없음 |")
    lines += [
        "",
        "위 측정은 현재 문항 ID와 일치하는 검증 및 가짜 솔버 결과만 포함합니다. oracle은 실제 문서를 추출 맵의 위치로 읽고 규칙 엔진으로 정답을 재계산합니다. null은 빈 객체를 제출합니다. 모델 API와 실제 모델 평가는 실행하지 않았습니다. 이 결과는 모델 성능 점수가 아닙니다.",
        "",
        "```python",
        "import json",
        "from datasets import load_dataset",
        "from huggingface_hub import hf_hub_download",
        (
            f'repo_id = "{repo_id}"'
            if repo_id
            else f'repo_id = "YOUR_NAMESPACE/{name}"  # Hub 게시 후 실제 주소로 바꿉니다.'
        ),
        (
            'ds = load_dataset(repo_id, data_files="data/train.jsonl", split="train")'
            if repo_id
            else 'ds = load_dataset("json", data_files="data/train.jsonl", split="train")'
        ),
        'gold = json.loads(ds[0]["gold"])',
        "# Hub의 입력 문서는 문항별 상대 경로로 별도 내려받습니다.",
        'first_document = hf_hub_download(repo_id, filename=ds[0]["input_files"][0]["path"], repo_type="dataset")',
        "```",
        "",
        'input_files.path와 각 *_path 필드는 이 내보내기 디렉터리를 기준으로 한 상대 경로입니다. 로컬에서는 해당 파일을 직접 읽습니다. Hub 사용자는 hf_hub_download(repo_id, filename=path, repo_type="dataset")로 받을 수 있습니다. 분야마다 구조가 다른 answer_schema와 gold 및 trace는 Arrow 스키마 충돌을 피하기 위해 JSON 문자열로 저장합니다.',
        "",
        "task.yaml과 gold.json 및 trace.json과 extraction_map.json, 개별 집필 원고를 공개합니다. 하네스가 모델에 제공하는 작업 디렉터리에는 input_files 문서와 instruction.txt 및 answer_schema.json만 복사해야 합니다. 공개 정답과 원고 및 추출 맵과 카나리아 메타데이터는 평가 입력에 포함하지 않습니다.",
        "",
        "알려진 한계: 자동 게이트는 입력 보존성과 계산 재현성을 확인합니다. instruction_consistency는 원고와 task.yaml의 지시문 동일성과 예외 수를 확인하며 자유문장의 사실이나 법률 모순을 독립적으로 분석하지 않습니다. 모든 문항의 법률 해석이나 집필 다양성을 독립적인 전문가가 확인했다는 뜻은 아닙니다. PNG는 원본 PDF의 중복 자료이므로 스캔만 있는 OCR 평가 성능을 주장하지 않습니다. HWPX는 ZIP과 XML 구조 및 독립 파싱을 확인했으며 한컴 앱 호환성 검수는 남아 있습니다. 렌더러는 공통 표 기반 양식 5종을 지원합니다. Docker의 실환경 격리는 구축 호스트의 엔진 부재로 실행하지 못했으며 가짜 솔버 결과가 운영 보안을 인증하지 않습니다. 각 문항의 적용 범위를 따라야 하며 면세 겸업 안분과 가산세 등은 지원하지 않습니다.",
        "",
        f"Dataset card canary: `{summary['canary']}`",
        "",
        "문항과 데이터카드의 카나리아 GUID는 오염을 조사할 때 참고할 수 있습니다. 공개 파일에서 접했을 가능성도 있으므로 문자열 인지만으로 학습 포함을 확정할 수 없습니다. 카나리아는 모델 평가 작업 디렉터리에 전달하지 않습니다.",
        "",
        "코드 Apache-2.0, 합성 데이터 CC-BY-4.0. 공식 원문은 별도 저작권을 따르며 합성 데이터 라이선스로 재허가하지 않습니다. 폰트는 SIL OFL-1.1입니다. 내보내기 명령은 로컬 파일을 만들며 Hugging Face 게시는 별도의 배포 단계입니다.",
        "",
        f"JSONL SHA-256: `{summary['jsonl_sha256']}`",
        "",
    ]
    return "\n".join(lines)
