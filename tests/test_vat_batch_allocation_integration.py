"""One actual execution, two explicit registration amounts, no inferred allocation."""

import pytest
from KrRubberStamp.registry import calculate
from KrRubberStamp.io import write_json
from render.authored import render_authored
from render.documents import restore_scenario
from physical_source import edit_numeric_source
from test_vat_batch_allocation import source


@pytest.mark.parametrize("fmt", ["pdf", "xlsx", "hwpx"])
def test_actual_two_instruction_cells_change_registration_balances_only(tmp_path, fmt):
    facts = source()
    render_authored(
        facts,
        tmp_path,
        "C_vat",
        [
            {
                "filename": "분배지시." + fmt,
                "format": fmt,
                "title": "일괄 실행과 등록별 실제 분배 지시",
                "note": "은행 수수료를 세금 원금에 나누지 않는다.",
                "fields": list(facts),
            }
        ],
    )
    assert restore_scenario(tmp_path) == facts
    before, trace = calculate("C_vat", restore_scenario(tmp_path))
    assert before["balance_total"] == 0
    assert trace[0]["rule_id"] == "C_VAT_BANK_BATCH_ALLOCATION"
    write_json(tmp_path / "gold.json", before)
    write_json(tmp_path / "trace.json", trace)
    fixed = {
        n: (tmp_path / n).read_bytes() for n in ["extraction_map.json", "gold.json", "trace.json"]
    }
    edit_numeric_source(tmp_path, ["allocation_instructions", 0, "amount"], 95000)
    edit_numeric_source(tmp_path, ["allocation_instructions", 1, "amount"], 76400)
    restored = restore_scenario(tmp_path)
    assert restored["bank_executions"] == facts["bank_executions"]
    assert restored["filings"] == facts["filings"]
    after, _ = calculate("C_vat", restored)
    assert after["filing_calculations"] == before["filing_calculations"]
    assert after["bank_cash_totals"] == before["bank_cash_totals"]
    assert after["balance_total"] == 0
    assert sorted(r["balance"] for r in after["registration_settlements"]) == [-5000, 5000]
    for name, content in fixed.items():
        assert (tmp_path / name).read_bytes() == content
