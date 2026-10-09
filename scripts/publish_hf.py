"""Publish only the complete, verified 4,800-case export with explicit --publish.

Dry-run is entirely local. Authentication comes from huggingface_hub's existing
login, never from arguments or copied credentials. Re-run a failed publish with
the same export to resume committed files and Xet chunks.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys

from KrRubberStamp.export import (
    _dataset_card,
    checked_measurements,
    collect_authored_tasks,
    task_set_sha256,
)
from KrRubberStamp.io import read_json
from KrRubberStamp.tasks import scenario_hash

DATASET_NAME = "KrRubberStamp-4.8K"
BATCHES = [1, 2, 3, 4]
ROWS = 4800
ROOT_FILES = {
    "README.md",
    "export_manifest.json",
    "LICENSE",
    "DATA_LICENSE",
    "DATA_SPEC.md",
    "DECISIONS.md",
    "sources.yaml",
}
ROOT_DIRS = {"authored", "data", "rules", "reports"}
IGNORED_PARTS = {".git", ".cache", "cache", "__pycache__"}
SECRET_NAMES = {"token", "tokens", "credentials", "stored_tokens", ".env", "id_rsa", "id_ed25519"}


@dataclass(frozen=True)
class PublishPlan:
    folder: Path
    files: tuple[str, ...]
    samples: tuple[str, ...]
    manifest: dict


def sha256(path):
    with Path(path).open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256")
    return digest.hexdigest()


def artifact(folder, relative):
    path = Path(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"Unsafe artifact path: {relative}")
    target = folder / path
    if any(part.is_symlink() for part in [target, *target.parents] if part != folder.parent):
        raise ValueError(f"Symlink artifacts are forbidden: {relative}")
    if not target.is_file():
        raise ValueError(f"Missing required artifact: {relative}")
    return target


def inventory(folder):
    files = []
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        if (
            any(part in IGNORED_PARTS for part in relative.parts)
            or path.name == ".DS_Store"
            or path.suffix == ".pyc"
        ):
            continue
        if path.is_symlink():
            raise ValueError(f"Symlinks cannot be published: {relative}")
        if not path.is_file():
            continue
        if any(part.lower() in SECRET_NAMES or part.startswith(".") for part in relative.parts):
            raise ValueError("Unexpected private or hidden file in public export")
        if relative.as_posix() not in ROOT_FILES and relative.parts[0] not in ROOT_DIRS:
            raise ValueError(f"Unexpected file outside public export roots: {relative}")
        files.append(relative.as_posix())
    return tuple(files)


def preflight(folder):
    """Reject partial exports, stale upstream cases and mismatching public artifacts."""
    folder = Path(folder).resolve()
    manifest = read_json(artifact(folder, "export_manifest.json"))
    if (
        manifest.get("rows") != ROWS
        or manifest.get("dataset_name") != DATASET_NAME
        or manifest.get("batches") != BATCHES
        or manifest.get("preview") is not False
        or manifest.get("authorship") != "individually_written"
    ):
        raise ValueError("Publishing requires the complete individually written 4,800-case export")
    for relative in sorted(ROOT_FILES | {"data/train.jsonl", "rules/sources.yaml"}):
        artifact(folder, relative)
    if sha256(folder / "data/train.jsonl") != manifest.get("jsonl_sha256"):
        raise ValueError("JSONL fingerprint differs from the release manifest")
    card = (folder / "README.md").read_text(encoding="utf-8")
    if DATASET_NAME not in card or "data/train.jsonl" not in card:
        raise ValueError("Dataset card does not describe this release")

    # This recovers every case from the CURRENT checkout, checks per-batch counts,
    # current engine/schema/gold/trace, and unique instructions/facts/canaries.
    records, _ = collect_authored_tasks(folder / "data", BATCHES)
    if len(records) != ROWS or task_set_sha256(records) != manifest.get("task_set_sha256"):
        raise ValueError("Export task identities differ from the current authored release")
    for batch in BATCHES:
        evidence = checked_measurements(folder / "reports", records, batch)
        for label, item in evidence.items():
            expected = manifest.get("measurements", {}).get(str(batch), {}).get(label)
            if not expected or any(item["value"].get(k) != v for k, v in expected.items()):
                raise ValueError("Manifest measurements do not match their current reports")
        batch_records = [record for record in records if record["batch"] == batch]
        marker = f"<!-- authored-task-set-sha256: {task_set_sha256(batch_records)} -->"
        for name in (f"BATCH_{batch}_REPORT.md", f"REVIEW_QUEUE_BATCH_{batch}.md"):
            if marker not in artifact(folder, f"reports/{name}").read_text(encoding="utf-8"):
                raise ValueError("Editorial report belongs to another task set")

    by_id = {record["task"]["task_id"]: record for record in records}
    seen, counts, samples = set(), Counter(), {}
    source_cache = {}
    for line in (folder / "data/train.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        task_id = row["task_id"]
        if task_id in seen or task_id not in by_id:
            raise ValueError("JSONL contains a duplicate or unknown task identity")
        seen.add(task_id)
        record = by_id[task_id]
        task, case, batch = record["task"], record["case"], record["batch"]
        for key in (
            "domain",
            "difficulty",
            "reference_period",
            "instruction",
            "canary",
            "scenario_hash",
            "authorship",
            "answer_fields",
        ):
            if row.get(key) != task[key]:
                raise ValueError(f"JSONL metadata differs from task.yaml: {task_id}/{key}")
        base = f"data/batch_{batch}/{task['domain']}/{task_id}"
        for key, filename in (
            ("task_path", "task.yaml"),
            ("gold_path", "gold.json"),
            ("trace_path", "trace.json"),
            ("extraction_map_path", "extraction_map.json"),
        ):
            if row.get(key) != f"{base}/{filename}":
                raise ValueError("JSONL artifact path differs from the task identity")
            artifact(folder, row[key])
        for key in ("answer_schema", "gold", "trace"):
            if not isinstance(row.get(key), str):
                raise ValueError("Heterogeneous answer fields must remain JSON strings")
            value = json.loads(row[key])
            expected = (
                task["answer_schema"]
                if key == "answer_schema"
                else read_json(folder / row[f"{key}_path"])
            )
            if value != expected:
                raise ValueError(f"JSONL and public {key} differ")
        expected_inputs = [
            {"path": f"{base}/{item['path']}", "format": item["format"]}
            for item in task["input_files"]
        ]
        if row.get("input_files") != expected_inputs:
            raise ValueError("JSONL input document list differs from task.yaml")
        for item in row["input_files"]:
            artifact(folder, item["path"])
            samples.setdefault((batch, task["domain"], item["format"]), item["path"])
        source = f"authored/{task['authorship']['source_file']}"
        if row.get("authored_source_path") != source:
            raise ValueError("JSONL authored source path differs")
        if source not in source_cache:
            cases = read_json(artifact(folder, source))
            source_cache[source] = {item["case_id"]: item for item in cases}
            if len(source_cache[source]) != len(cases):
                raise ValueError("Ambiguous exported source identity")
        exported = source_cache[source].get(case["case_id"])
        if exported != case or scenario_hash(exported) != task["authorship"]["case_sha256"]:
            raise ValueError("Exported case differs from its current upstream source")
        counts[f"{task['domain']}/{task['difficulty']}"] += 1
    if len(seen) != ROWS or dict(counts) != manifest.get("counts"):
        raise ValueError("JSONL rows or category counts differ from the release manifest")
    return PublishPlan(folder, inventory(folder), tuple(sorted(samples.values())), manifest)


def verify_remote(api, plan, repo_id):
    """Pin all downloads to one revision; check inventory and representative bytes."""
    info = api.repo_info(repo_id=repo_id, repo_type="dataset", revision="main")
    revision = info.sha
    if not revision or not re.fullmatch(r"[0-9a-f]{40,64}", revision):
        raise ValueError("The Hub did not return an immutable release revision")
    remote = set(api.list_repo_files(repo_id=repo_id, repo_type="dataset", revision=revision))
    if remote - {".gitattributes"} != set(plan.files):
        raise ValueError("Remote files differ from the complete public export inventory")
    targets = {"README.md", "export_manifest.json", "data/train.jsonl", *plan.samples}
    targets.update(f"data/batch_{batch}/manifest.json" for batch in BATCHES)
    for relative in sorted(targets):
        downloaded = api.hf_hub_download(
            repo_id=repo_id,
            filename=relative,
            repo_type="dataset",
            revision=revision,
        )
        if sha256(downloaded) != sha256(plan.folder / relative):
            raise ValueError(f"Downloaded release artifact differs: {relative}")
    return {"revision": revision, "downloaded_files_checked": len(targets), "rows": ROWS}


def publish(plan, api):
    """Only called by --publish after full local preflight has passed."""
    identity = api.whoami()
    namespace = identity.get("name")
    if not isinstance(namespace, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", namespace):
        raise ValueError("Cannot determine the authenticated personal namespace")
    repo_id = f"{namespace}/{DATASET_NAME}"
    (plan.folder / "README.md").write_text(
        _dataset_card(plan.manifest, repo_id=repo_id), encoding="utf-8"
    )
    # Existing repositories may be resumed only for this exact export. We never
    # delete remote files or overwrite a different release under the same name.
    from huggingface_hub.errors import EntryNotFoundError, RepositoryNotFoundError

    try:
        previous = api.hf_hub_download(
            repo_id=repo_id,
            filename="export_manifest.json",
            repo_type="dataset",
        )
    except (EntryNotFoundError, RepositoryNotFoundError):
        previous = None
    if previous and read_json(previous) != plan.manifest:
        raise ValueError("Existing Hub repository describes another release; refusing overwrite")
    api.create_repo(repo_id=repo_id, repo_type="dataset", private=False, exist_ok=True)
    info = api.repo_info(repo_id=repo_id, repo_type="dataset")
    if info.private:
        raise ValueError("Existing repository is private; visibility must be resolved explicitly")
    api.upload_folder(
        repo_id=repo_id,
        repo_type="dataset",
        folder_path=str(plan.folder),
        # Use a bounded pattern set rather than tens of thousands of exact
        # patterns. Inventory has already rejected all unexpected public files.
        allow_patterns=sorted(ROOT_FILES) + [f"{directory}/*" for directory in sorted(ROOT_DIRS)],
        ignore_patterns=[
            "**/.DS_Store",
            "**/*.pyc",
            *[f"**/{part}/*" for part in sorted(IGNORED_PARTS)],
            *[f"**/{name}" for name in sorted(SECRET_NAMES)],
        ],
        commit_message="Publish individually written KrRubberStamp 4.8K benchmark",
    )
    result = verify_remote(api, plan, repo_id)
    result.update(
        {"uploaded": True, "repo_id": repo_id, "url": f"https://huggingface.co/datasets/{repo_id}"}
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, nargs="?", default=Path("exports/upto_4"))
    parser.add_argument(
        "--publish", action="store_true", help="Create/update the public HF dataset"
    )
    args = parser.parse_args(argv)
    try:
        plan = preflight(args.folder)
        if args.publish:
            from huggingface_hub import HfApi

            result = publish(plan, HfApi())
        else:
            result = {
                "uploaded": False,
                "dry_run": True,
                "rows": ROWS,
                "dataset_name": DATASET_NAME,
                "files": len(plan.files),
                "document_samples": len(plan.samples),
                "task_set_sha256": plan.manifest["task_set_sha256"],
            }
    except Exception as exc:
        # Authentication exceptions may contain request details. Do not print
        # arbitrary exception strings or tracebacks from networking libraries.
        message = (
            str(exc) if isinstance(exc, (ValueError, FileNotFoundError)) else type(exc).__name__
        )
        print(
            json.dumps({"uploaded": False, "error": message}, ensure_ascii=False), file=sys.stderr
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
