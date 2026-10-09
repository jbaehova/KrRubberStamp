"""Public lifecycle route reads actual source documents before VAT calculation."""

import json

from openpyxl import load_workbook
import pytest

from KrRubberStamp.registry import calculate
from render.authored import render_authored
from render.documents import _label, restore_scenario
from test_vat_document_lifecycle import lifecycle
from test_vat_document_reconciliation import invoice, sale_source


@pytest.mark.parametrize("fmt", ["pdf", "xlsx", "hwpx"])
def test_current_original_status_is_read_from_real_documents(tmp_path, fmt):
    facts = sale_source()
    facts["evidence_documents"].append(invoice())
    facts = lifecycle(facts)
    documents = [
        {
            "filename": "원본효력." + fmt,
            "format": fmt,
            "title": "공급과 원본 효력 인계",
            "note": "공급과 실제 지급은 유지됩니다. valid는 유효, revoked는 최종 취소 확인이며 취소 적법성은 판정하지 않습니다.",
            "fields": list(facts),
        }
    ]
    render_authored(facts, tmp_path, "C_vat", documents)
    assert restore_scenario(tmp_path) == facts
    answer, trace = calculate("C_vat", restore_scenario(tmp_path))
    assert (answer["output_vat"], answer["receipt_credit"], answer["payable_vat"]) == (
        10_000,
        0,
        10_000,
    )
    assert trace[0]["rule_id"] == "C_DOCUMENT_LIFECYCLE_SELECTION"
    assert trace[1]["rule_id"] == "C_DOCUMENT_RECONCILIATION"
    assert _label(["document_status_records", 1, "confirmed_on"], "C_vat").endswith("효력 확인일")
    if fmt == "xlsx":
        mapping_file = tmp_path / "extraction_map.json"
        original_map = mapping_file.read_bytes()
        record = next(
            row
            for row in json.loads(original_map)["records"]
            if row["path"] == ["document_status_records", 1, "state"]
        )
        workbook = load_workbook(tmp_path / record["file"])
        selector = record["selector"]
        workbook[selector["sheet"]][selector["cell"]] = "revoked"
        workbook.save(tmp_path / record["file"])
        workbook.close()
        restored = restore_scenario(tmp_path)
        assert restored["supplies"] == facts["supplies"]
        assert restored["payments"] == facts["payments"]
        assert mapping_file.read_bytes() == original_map
        after, _ = calculate("C_vat", restored)
        assert (after["output_vat"], after["receipt_credit"], after["payable_vat"]) == (
            10_000,
            715,
            9_285,
        )
