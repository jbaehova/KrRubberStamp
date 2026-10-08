"""One public calculation/generation contract for all domains."""

from importlib import import_module

DOMAINS = ("A_yearend", "B_payroll", "C_vat", "D_extract")
PERIODS = {
    "A_yearend": "2025",
    "B_payroll": "2026",
    "C_vat": "2026-H1",
    "D_extract": "not-applicable",
}


def calculate(domain: str, scenario: dict):
    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain: {domain}")
    if domain == "A_yearend" and "source_contract" in scenario:
        from rules.a_yearend.evidence import interpret, derivation_trace

        normalized = interpret(scenario)
        answer, trace = import_module("rules.a_yearend.engine").calculate(normalized)
        return answer, [derivation_trace(scenario, normalized), *trace]
    if domain == "B_payroll" and "source_contract" in scenario:
        from rules.b_payroll.evidence import interpret, derivation_trace

        normalized = interpret(scenario)
        answer, trace = import_module("rules.b_payroll.engine").calculate(normalized)
        return answer, [derivation_trace(scenario, normalized), *trace]
    if domain == "C_vat" and "source_contract" in scenario:
        from rules.c_vat.evidence import interpret, derivation_trace

        normalized = interpret(scenario)
        answer, trace = import_module("rules.c_vat.engine").calculate(normalized)
        return answer, [derivation_trace(scenario, normalized), *trace]
    if domain == "D_extract" and "source_contract" in scenario:
        from rules.d_extract.evidence import interpret, derivation_trace

        normalized = interpret(scenario)
        answer, trace = import_module("rules.d_extract.engine").calculate(normalized)
        return answer, [derivation_trace(scenario, normalized), *trace]
    return import_module(f"rules.{domain.lower()}.engine").calculate(scenario)


def generate_scenario(domain: str, seed: int, difficulty: str):
    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain: {domain}")
    return import_module(f"scenarios.{domain.lower()}").generate(seed, difficulty)


def instructions(domain: str):
    module = import_module(f"scenarios.{domain.lower()}")
    return getattr(
        module,
        "INSTRUCTIONS",
        ["첨부 자료를 확인해서 요청한 계산 결과를 answer.json으로 정리해 주세요."],
    )
