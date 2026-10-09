"""Real transfer source cells change local reservations without changing total stock."""

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
from test_inventory_snapshots import source


@pytest.mark.parametrize("fmt", ["pdf", "xlsx", "hwpx"])
def test_inventory_transfer_is_read_from_real_documents(tmp_path, fmt):
    facts = source()
    render_authored(
        facts,
        tmp_path,
        "D_extract",
        [
            {
                "filename": "창고이동." + fmt,
                "format": fmt,
                "title": "지정 창고 주문과 실제 이동 자료",
                "note": "타 창고의 잉여로 지정 창고 부족을 상계하지 않는 사적 수량 원장입니다.",
                "fields": list(facts),
            }
        ],
    )
    assert restore_scenario(tmp_path) == facts
    before, trace = calculate("D_extract", restore_scenario(tmp_path))
    first = before["organization_item_snapshots"][0]["items"][0]
    assert first == {
        "item_id": "A",
        "on_hand": 18,
        "reserved_quantity": 15,
        "available_quantity": 4,
        "reservation_shortfall": 1,
    }
    assert trace[0]["rule_id"] == "D_INVENTORY_SNAPSHOTS"
    assert _label(["movements", 1, "from_warehouse_id"], "D_extract").endswith("출고 창고 번호")
    write_json(tmp_path / "gold.json", before)
    write_json(tmp_path / "trace.json", trace)
    fixed = {
        name: (tmp_path / name).read_bytes()
        for name in ("gold.json", "trace.json", "extraction_map.json")
    }
    record = next(
        row
        for row in json.loads(fixed["extraction_map.json"])["records"]
        if row["path"] == ["movements", 1, "quantity"]
    )
    file = tmp_path / record["file"]
    selector = record["selector"]
    if fmt == "xlsx":
        workbook = load_workbook(file)
        workbook[selector["sheet"]][selector["cell"]] = 8
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
                _display({"kind": "int", "value": 8}),
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
        texts[0].text = "8"
        for text in texts[1:]:
            text.text = ""
        members[selector["section"]] = ET.tostring(xml, encoding="utf-8", xml_declaration=True)
        with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, value in members.items():
                archive.writestr(name, value)
    restored = restore_scenario(tmp_path)
    assert restored["orders"] == facts["orders"]
    assert restored["movements"][1]["quantity"] == 8
    after, _ = calculate("D_extract", restored)
    assert after["order_snapshots"] == before["order_snapshots"]
    first_after = after["organization_item_snapshots"][0]["items"][0]
    assert first_after == {
        "item_id": "A",
        "on_hand": 18,
        "reserved_quantity": 15,
        "available_quantity": 3,
        "reservation_shortfall": 0,
    }
    assert after["stock_snapshots"][0]["stocks"][0]["on_hand"] == 8
    assert after["stock_snapshots"][0]["stocks"][1]["on_hand"] == 10
    for name, value in fixed.items():
        assert (tmp_path / name).read_bytes() == value
