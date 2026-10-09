"""Public routes recompute from edited original documents with a frozen map."""

import pytest

from KrRubberStamp.io import write_json
from KrRubberStamp.registry import calculate
from physical_source import edit_numeric_source
from render.authored import render_authored
from render.documents import restore_scenario
from test_payroll_statement_revisions import source as payroll_source
from test_vat_itemized_activity import source as vat_source


@pytest.mark.parametrize("fmt", ["pdf", "xlsx", "hwpx"])
@pytest.mark.parametrize("domain", ["B_payroll", "C_vat"])
def test_final_source_selection_and_price_units_survive_actual_file_edit(tmp_path, fmt, domain):
    facts = payroll_source() if domain == "B_payroll" else vat_source()
    render_authored(
        facts,
        tmp_path,
        domain,
        [
            {
                "filename": "확정원천." + fmt,
                "format": fmt,
                "title": "확정 원본 대조",
                "note": "원본의 적용 단위와 승인 상태를 확인한다.",
                "fields": list(facts),
            }
        ],
    )
    assert restore_scenario(tmp_path) == facts
    before, trace = calculate(domain, restore_scenario(tmp_path))
    write_json(tmp_path / "gold.json", before)
    write_json(tmp_path / "trace.json", trace)
    frozen = {
        name: (tmp_path / name).read_bytes()
        for name in ["extraction_map.json", "gold.json", "trace.json"]
    }
    if domain == "B_payroll":
        assert trace[0]["rule_id"] == "B_PAYROLL_STATEMENT_REVISION"
        edit_numeric_source(tmp_path, ["statement_records", 1, "facts", "hourly_rate"], 12600)
        after, _ = calculate(domain, restore_scenario(tmp_path))
        # Twenty actual hours and four weekly holiday hours use the selected rate.
        assert after["gross_total"] == 302400
        assert after["deductions_total"] == 2700
        assert after["net_total"] == 299700
        assert after["paid_total"] == 290000
        assert after["balance_total"] == 9700
        assert after["net_total"] - before["net_total"] == 2400
    else:
        assert trace[0]["rule_id"] == "C_VAT_ITEMIZED_ACTIVITY"
        edit_numeric_source(
            tmp_path, ["transactions", 0, "invoice_lines", 0, "unit_discount"], 9000
        )
        after, _ = calculate(domain, restore_scenario(tmp_path))
        # The discount is per unit, so three actual units add 3,000 supply.
        assert after["tax_base"] == 353000
        assert after["output_vat"] == 35300
        assert after["receipt_credit"] == 5047
        assert after["net_vat"] == 30253
        assert after["tax_base"] - before["tax_base"] == 3000
    for name, contents in frozen.items():
        assert (tmp_path / name).read_bytes() == contents
