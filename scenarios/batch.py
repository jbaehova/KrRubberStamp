"""Generate answers first, render second, publish only after all quality gates pass."""

from collections import Counter
import hashlib
from pathlib import Path
import shutil
import yaml
from KrRubberStamp.io import write_json
from KrRubberStamp.registry import DOMAINS, PERIODS, calculate, generate_scenario
from KrRubberStamp.tasks import canary_for, instruction_for, make_schema, scenario_hash


def difficulty_counts(n):
    weights = {"easy": 30, "medium": 45, "hard": 25}
    counts = {difficulty: n * ratio // 100 for difficulty, ratio in weights.items()}
    remainder = n - sum(counts.values())
    ranking = sorted(weights, key=lambda key: (-(n * weights[key] % 100), list(weights).index(key)))
    for key in ranking[:remainder]:
        counts[key] += 1
    return counts


def derive_seed(seed, batch, domain, index, retry):
    data = f"KrRubberStamp|{seed}|{batch}|{domain}|{index}|{retry}".encode()
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


def generate_batch(seed: int, n: int, output: Path, batch: int = 1, progress=None):
    from render import render_task
    from validate import validate_task

    output = Path(output)
    if n < 1:
        raise ValueError("n must be positive")
    if batch != 1:
        raise ValueError("Only Batch 1 is authorized in this release")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to replace existing task set: {output}")
    output.mkdir(parents=True, exist_ok=True)
    prior_hashes = set()
    # Only published batch siblings are prior datasets, not temporary retry artifacts.
    for sibling in output.parent.glob("batch_*"):
        if sibling.resolve() == output.resolve():
            continue
        for task in sibling.glob("*/*/task.yaml"):
            prior_hashes.add(yaml.safe_load(task.read_text(encoding="utf-8"))["scenario_hash"])
    seen = set(prior_hashes)
    manifest = []
    rejection_reasons = Counter()
    rejections = []
    for domain_index, domain in enumerate(DOMAINS):
        domain_n = n // 4 + (domain_index < n % 4)
        counts = difficulty_counts(domain_n)
        difficulties = [level for level, count in counts.items() for _ in range(count)]
        for index, difficulty in enumerate(difficulties, 1):
            for retry in range(25):
                scenario_seed = derive_seed(seed, batch, domain, index, retry)
                scenario = generate_scenario(domain, scenario_seed, difficulty)
                digest = scenario_hash(scenario)
                if digest in seen:
                    rejection_reasons["duplicate scenario"] += 1
                    continue
                gold, trace = calculate(domain, scenario)
                task_id = f"B{batch}_{domain[0]}_{digest[:16]}"
                task_dir = output / domain / task_id
                task_dir.mkdir(parents=True, exist_ok=True)
                write_json(task_dir / "gold.json", gold)
                write_json(task_dir / "trace.json", trace)
                input_files = render_task(scenario, task_dir, domain, difficulty, scenario_seed)
                answer_schema = {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    **make_schema(gold),
                }
                task = {
                    "task_id": task_id,
                    "domain": domain,
                    "difficulty": difficulty,
                    "reference_period": PERIODS[domain],
                    "instruction": instruction_for(domain, difficulty, scenario_seed),
                    "input_files": input_files,
                    "answer_schema": answer_schema,
                    "canary": canary_for(f"{batch}/{domain}/{scenario_seed}/{digest}"),
                    "generation_seed": seed,
                    "scenario_seed": scenario_seed,
                    "scenario_hash": digest,
                    "generator_version": "0.1.0",
                }
                (task_dir / "task.yaml").write_text(
                    yaml.safe_dump(task, allow_unicode=True, sort_keys=False), encoding="utf-8"
                )
                result = validate_task(task_dir)
                if result["passed"]:
                    seen.add(digest)
                    manifest.append(
                        {
                            "task_id": task_id,
                            "domain": domain,
                            "difficulty": difficulty,
                            "scenario_hash": digest,
                            "path": str(task_dir.relative_to(output)),
                        }
                    )
                    if progress:
                        progress(len(manifest), n, task_id)
                    break
                reasons = result["errors"]
                rejections.append(
                    {
                        "task_id": task_id,
                        "scenario_seed": scenario_seed,
                        "retry": retry,
                        "errors": reasons,
                    }
                )
                rejection_reasons.update(reasons)
                shutil.rmtree(task_dir)
            else:
                write_json(output / "generation_failures.json", rejections)
                raise RuntimeError(
                    f"Could not produce valid task {domain}/{index}; reasons: {dict(rejection_reasons)}"
                )
    summary = {
        "batch": batch,
        "seed": seed,
        "requested": n,
        "accepted": len(manifest),
        "rejected_attempts": sum(rejection_reasons.values()),
        "failure_reasons": dict(rejection_reasons),
        "rejections": rejections,
        "tasks": manifest,
    }
    write_json(output / "manifest.json", summary)
    return summary
