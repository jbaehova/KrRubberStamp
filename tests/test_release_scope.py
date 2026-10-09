"""Public authored commands stop at the final two-batch project boundary."""

import pytest

from KrRubberStamp import cli
from KrRubberStamp.release_scope import (
    batch_case_ids,
    batch_counts,
    batch_rows,
    check_completed_cases,
)
from scripts import build_authored_catalog


@pytest.mark.parametrize("batch", [3, 4])
@pytest.mark.parametrize(
    "arguments", [["build-authored", "--batch"], ["export-hf", "--batch"], ["export-hf", "--upto"]]
)
def test_public_cli_rejects_unrequested_batches(arguments, batch):
    with pytest.raises(SystemExit) as error:
        cli.main([*arguments, str(batch)])
    assert error.value.code == 2


@pytest.mark.parametrize("option", ["--batch", "--upto"])
@pytest.mark.parametrize("batch", [3, 4])
def test_catalog_rejects_unrequested_batches_without_writing(option, batch):
    with pytest.raises(SystemExit) as error:
        build_authored_catalog.main([option, str(batch)])
    assert error.value.code == 2


def _scope_records(spec):
    # Only quota metadata, not benchmark content or document factories.
    return [
        {"case_id": f"{domain[0]}{number:03d}", "domain": domain, "difficulty": difficulty}
        for domain, values in spec.items()
        for difficulty, begin, end in values
        for number in range(begin, end + 1)
    ]


@pytest.fixture
def final_batch_two():
    return _scope_records(
        {
            "A_yearend": [("easy", 1, 30), ("medium", 31, 75), ("hard", 76, 100)],
            "B_payroll": [("easy", 1, 30), ("medium", 31, 75), ("hard", 76, 100)],
            "C_vat": [("easy", 1, 30), ("medium", 31, 75), ("hard", 76, 100)],
            "D_extract": [("easy", 1, 45), ("medium", 46, 113), ("hard", 114, 150)],
        }
    )


def test_final_scope_keeps_original_batch_and_adds_450(final_batch_two):
    assert batch_rows(1) == 1200 and batch_rows(2) == 450
    assert batch_counts(1)["D_extract"] == {"easy": 90, "medium": 135, "hard": 75}
    assert batch_counts(2)["D_extract"] == {"easy": 45, "medium": 68, "hard": 37}
    assert "D150" in batch_case_ids(2) and "D151" not in batch_case_ids(2)
    assert "A100" in batch_case_ids(2) and "A101" not in batch_case_ids(2)
    check_completed_cases(2, final_batch_two)


def test_original_batch_scope_remains_1200():
    cases = _scope_records(
        {
            domain: [("easy", 1, 90), ("medium", 91, 225), ("hard", 226, 300)]
            for domain in ("A_yearend", "B_payroll", "C_vat", "D_extract")
        }
    )
    check_completed_cases(1, cases)
    with pytest.raises(ValueError, match="450 individually authored"):
        check_completed_cases(2, cases)


@pytest.mark.parametrize(
    "change", ["extra", "missing", "wrong_id", "wrong_difficulty", "duplicate"]
)
def test_release_quota_and_identity_cannot_be_bypassed(final_batch_two, change):
    if change == "extra":
        final_batch_two.append({"case_id": "D151", "domain": "D_extract", "difficulty": "hard"})
    elif change == "missing":
        final_batch_two.pop()
    elif change == "wrong_id":
        final_batch_two[-1]["case_id"] = "D151"
    elif change == "wrong_difficulty":
        final_batch_two[-1]["difficulty"] = "medium"
    else:
        final_batch_two[-1]["case_id"] = "D149"
    with pytest.raises(ValueError):
        check_completed_cases(2, final_batch_two)


def test_same_total_cannot_move_extract_quota_into_yearend(final_batch_two):
    row = final_batch_two[-1]
    row.update({"case_id": "A101", "domain": "A_yearend"})
    with pytest.raises(ValueError, match="450 individually authored"):
        check_completed_cases(2, final_batch_two)
