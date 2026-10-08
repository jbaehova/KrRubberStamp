from copy import deepcopy
from hypothesis import given, strategies as st
from rules.d_extract.engine import calculate, normalize_vendor, split_vat
from scenarios.d_extract import generate


def test_vendor_aliases():
    assert normalize_vendor("㈜ 가상 Ａ") == normalize_vendor("주식회사 가상 A")


@given(st.integers(min_value=0, max_value=10**10))
def test_split_conserves_money(amount):
    supply, vat = split_vat(amount)
    assert supply + vat == amount
    assert supply >= 0 and vat >= 0


@given(st.integers(min_value=0, max_value=10**9))
def test_duplicate_invariance(seed):
    scenario = generate(seed, "hard")
    original, _ = calculate(scenario)
    scenario["documents"].append(deepcopy(scenario["documents"][0]))
    duplicated, _ = calculate(scenario)
    assert original == duplicated


def test_trace_and_generation():
    for difficulty in ("easy", "medium", "hard"):
        scenario = generate(14, difficulty)
        assert scenario == generate(14, difficulty)
        gold, trace = calculate(scenario)
        assert gold["grand_total"] == gold["supply_total"] + gold["vat_total"]
        assert all("rule_id" in step and "output" in step for step in trace)
