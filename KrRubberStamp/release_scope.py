"""The fixed boundary of the individually written 1,650-case release."""

from collections import Counter

AUTHORIZED_BATCHES = (1, 2)
FINAL_ROWS = 1650
FINAL_DATASET_NAME = "KrRubberStamp-1.65K"
DIFFICULTY_NAMES = ("easy", "medium", "hard")
DOMAINS = ("A_yearend", "B_payroll", "C_vat", "D_extract")


def batch_counts(batch):
    """Return fresh per-domain difficulty counts without shared mutable state."""
    if type(batch) is not int or batch not in AUTHORIZED_BATCHES:
        raise ValueError("Select one of the two authorized batches: 1 and 2")
    return {
        domain: dict(
            zip(
                DIFFICULTY_NAMES,
                (90, 135, 75)
                if batch == 1
                else (45, 68, 37)
                if domain == "D_extract"
                else (30, 45, 25),
                strict=True,
            )
        )
        for domain in DOMAINS
    }


def batch_rows(batch):
    return sum(sum(counts.values()) for counts in batch_counts(batch).values())


def batch_case_ids(batch):
    return {
        f"{domain[0]}{number:03d}"
        for domain, counts in batch_counts(batch).items()
        for number in range(1, sum(counts.values()) + 1)
    }


def check_completed_cases(batch, cases):
    """Require the exact quota AND contiguous authored IDs before publication."""
    expected = batch_counts(batch)
    cases = list(cases)
    counts = Counter((case["domain"], case["difficulty"]) for case in cases)
    expected_counts = {
        (domain, difficulty): number
        for domain, values in expected.items()
        for difficulty, number in values.items()
    }
    if len(cases) != batch_rows(batch) or counts != expected_counts:
        quota = (
            "300 individually authored cases per domain with 90/135/75 difficulty counts"
            if batch == 1
            else "450 individually authored cases: A/B/C 100 each with 30/45/25 and D 150 with 45/68/37 difficulty counts"
        )
        raise ValueError(f"Release requires {quota}; use --preview for an incomplete editorial set")
    ids = [case["case_id"] for case in cases]
    if len(set(ids)) != len(ids) or set(ids) != batch_case_ids(batch):
        raise ValueError("Release requires the exact authorized case IDs for this batch")
    if any(case["case_id"][0] != case["domain"][0] for case in cases):
        raise ValueError("Case ID and authorized domain disagree")
