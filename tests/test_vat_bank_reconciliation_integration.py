"""Real bank source cells change cash balances without changing VAT filings."""

import json
import zipfile
from xml.etree import ElementTree as ET

from openpyxl import load_workbook
import pymupdf
import pytest

from KrRubberStamp.io import write_json
from KrRubberStamp.registry import calculate
from render.authored import render_authored
from render.documents import FONT_PATH, HP, _display, _label, restore_scenario
from test_vat_bank_reconciliation import source


@pytest.mark.parametrize("fmt", ["pdf", "xlsx", "hwpx"])
def test_registration_cash_is_read_from_real_bank_documents(tmp_path, fmt):
    facts = source()
    render_authored(
        facts,
        tmp_path,
        "C_vat",
        [
            {
                "filename": "은행대조." + fmt,
                "format": fmt,
                "title": "독립 신고와 은행 실행 자료",
                "note": "서로 다른 등록번호를 상계하지 않는 사적 장부 대조입니다.",
                "fields": list(facts),
            }
        ],
    )
    assert restore_scenario(tmp_path) == facts
    before, trace = calculate("C_vat", restore_scenario(tmp_path))
    assert before["balance_total"] == 2_000
    assert trace[0]["rule_id"] == "C_VAT_BANK_RECONCILIATION"
    assert _label(["filings", 0, "registration_id"], "C_vat").endswith("사업자등록 식별번호")
    write_json(tmp_path / "gold.json", before)
    write_json(tmp_path / "trace.json", trace)
    fixed = {
        name: (tmp_path / name).read_bytes()
        for name in ("gold.json", "trace.json", "extraction_map.json")
    }
    record = next(
        row
        for row in json.loads(fixed["extraction_map.json"])["records"]
        if row["path"] == ["transfers", 0, "amount"]
    )
    file = tmp_path / record["file"]
    selector = record["selector"]
    if fmt == "xlsx":
        workbook = load_workbook(file)
        workbook[selector["sheet"]][selector["cell"]] = 9_000
        workbook.save(file)
        workbook.close()
    elif fmt == "pdf":
        with pymupdf.open(file) as pdf:
            page = pdf[selector["page"]]
            box = pymupdf.Rect(selector["bbox"])
            page.add_redact_annot(box, fill=(1, 1, 1))
            page.apply_redactions()
            page.insert_font(fontname="bank_cf", fontfile=str(FONT_PATH))
            page.insert_text(
                (box.x0 + 4, box.y0 + 16),
                _display({"kind": "int", "value": 9_000}),
                fontname="bank_cf",
                fontsize=9.4,
            )
            temp = file.with_suffix(".edited.pdf")
            pdf.save(temp)
        temp.replace(file)
    else:
        with zipfile.ZipFile(file) as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        xml = ET.fromstring(members[selector["section"]])
        table = xml.findall(f".//{{{HP}}}tbl")[selector["table"]]
        row = table.findall(f"{{{HP}}}tr")[selector["row"]]
        cell = row.findall(f"{{{HP}}}tc")[selector["column"]]
        texts = list(cell.iter(f"{{{HP}}}t"))
        texts[0].text = "9000"
        for text in texts[1:]:
            text.text = ""
        members[selector["section"]] = ET.tostring(xml, encoding="utf-8", xml_declaration=True)
        with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, value in members.items():
                archive.writestr(name, value)
    restored = restore_scenario(tmp_path)
    assert restored["filings"] == facts["filings"]
    assert restored["transfers"][0]["amount"] == 9_000
    after, _ = calculate("C_vat", restored)
    assert after["filing_calculations"] == before["filing_calculations"]
    assert after["balance_total"] == 1_000
    for name, value in fixed.items():
        assert (tmp_path / name).read_bytes() == value
