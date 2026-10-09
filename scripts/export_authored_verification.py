"""Load an authored JSONL through Datasets entirely offline and check its artifacts."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

from KrRubberStamp.io import read_json
from KrRubberStamp.release_scope import AUTHORIZED_BATCHES, batch_rows, check_completed_cases
from KrRubberStamp.tasks import scenario_hash


def verify_export(output):
    output = Path(output).resolve()
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    from datasets import load_dataset

    manifest = read_json(output / "export_manifest.json")
    if (
        hashlib.sha256((output / "data/train.jsonl").read_bytes()).hexdigest()
        != manifest["jsonl_sha256"]
    ):
        raise ValueError("JSONL bytes differ from the recorded export fingerprint")
    if manifest["authorship"] != "individually_written":
        raise ValueError("Verification requires an individually written export")
    batches = manifest.get("batches")
    if (
        not isinstance(batches, list)
        or not batches
        or len(set(batches)) != len(batches)
        or any(type(batch) is not int or batch not in AUTHORIZED_BATCHES for batch in batches)
    ):
        raise ValueError("Verification requires unique authorized batch numbers: 1 and 2")
    if not manifest["preview"] and manifest["rows"] != sum(batch_rows(batch) for batch in batches):
        raise ValueError("Export row count differs from the final authorized batch scope")
    with tempfile.TemporaryDirectory(prefix="krt-datasets-offline-") as cache:
        dataset = load_dataset(
            "json",
            data_files=str(output / "data/train.jsonl"),
            split="train",
            cache_dir=cache,
        )
        if len(dataset) != manifest["rows"]:
            raise ValueError("JSONL row count differs from export manifest")
        identifiers, canaries = set(), set()
        artifacts = 0
        batch_cases = {batch: [] for batch in batches}
        for row in dataset:
            if row["task_id"] in identifiers or row["canary"] in canaries:
                raise ValueError("Duplicate task identity or canary")
            identifiers.add(row["task_id"])
            canaries.add(row["canary"])
            for key in ("answer_schema", "gold", "trace"):
                if not isinstance(row[key], str):
                    raise ValueError(f"{key} must remain a JSON string across domain schemas")
                json.loads(row[key])
            for relative in [
                row[key]
                for key in (
                    "task_path",
                    "gold_path",
                    "trace_path",
                    "extraction_map_path",
                    "authored_source_path",
                )
            ] + [item["path"] for item in row["input_files"]]:
                path = output / relative
                if (
                    Path(relative).is_absolute()
                    or ".." in Path(relative).parts
                    or not path.is_file()
                ):
                    raise ValueError(f"Export artifact is absent or unsafe: {relative}")
                artifacts += 1
            source = read_json(output / row["authored_source_path"])
            cases = [case for case in source if case["case_id"] == row["authorship"]["case_id"]]
            if len(cases) != 1 or scenario_hash(cases[0]) != row["authorship"]["case_sha256"]:
                raise ValueError("Exported authored source does not match its recorded case hash")
            source_parts = Path(row["authored_source_path"]).parts
            batch_directory = source_parts[1] if len(source_parts) > 2 else ""
            matched_batches = [batch for batch in batches if batch_directory == f"batch_{batch}"]
            if len(matched_batches) != 1:
                raise ValueError("Exported case belongs to an unauthorized batch")
            batch_cases[matched_batches[0]].append(cases[0])
            if read_json(output / row["gold_path"]) != json.loads(row["gold"]):
                raise ValueError("Public gold file and JSONL gold differ")
            if read_json(output / row["trace_path"]) != json.loads(row["trace"]):
                raise ValueError("Public trace file and JSONL trace differ")
        if not manifest["preview"]:
            for batch, cases in batch_cases.items():
                check_completed_cases(batch, cases)
    return {
        "rows": len(identifiers),
        "referenced_artifacts_checked": artifacts,
        "offline_datasets_load": True,
        "preview": manifest["preview"],
        "uploaded": False,
        "model_api_called": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(verify_export(args.output), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
