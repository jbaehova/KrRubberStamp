from KrRubberStamp.tasks import make_schema, canary_for
from jsonschema import Draft202012Validator
from scenarios.batch import difficulty_counts, derive_seed


def test_strict_recursive_schema():
    schema = make_schema({"amount": 3, "rows": [{"vendor": "가상", "total": 2}]})
    validator = Draft202012Validator(schema)
    assert validator.is_valid({"amount": 8, "rows": [{"vendor": "예시", "total": 100}]})
    assert not validator.is_valid({"amount": True, "rows": []})
    assert not validator.is_valid({"amount": 3, "rows": [], "extra": 1})


def test_difficulty_distribution_and_seed_separation():
    assert difficulty_counts(300) == {"easy": 90, "medium": 135, "hard": 75}
    for n in range(60):
        assert sum(difficulty_counts(n).values()) == n
    assert derive_seed(10, 1, "A_yearend", 1, 0) != derive_seed(10, 2, "A_yearend", 1, 0)
    assert canary_for("one") == canary_for("one") != canary_for("two")
