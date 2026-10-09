"""Edit the original input cell selected by a frozen map, without editing that map."""

import json
import zipfile
from xml.etree import ElementTree as ET
import pymupdf
from openpyxl import load_workbook
from render.documents import FONT_PATH, HP, _display


def edit_numeric_source(folder, path, value):
    record = next(
        r
        for r in json.loads((folder / "extraction_map.json").read_text())["records"]
        if r["path"] == path
    )
    file = folder / record["file"]
    selector = record["selector"]
    if file.suffix == ".xlsx":
        workbook = load_workbook(file)
        workbook[selector["sheet"]][selector["cell"]] = value
        workbook.save(file)
        workbook.close()
    elif file.suffix == ".pdf":
        with pymupdf.open(file) as pdf:
            page = pdf[selector["page"]]
            box = pymupdf.Rect(selector["bbox"])
            page.add_redact_annot(box, fill=(1, 1, 1))
            page.apply_redactions()
            page.insert_font(fontname="source_cf", fontfile=str(FONT_PATH))
            page.insert_text(
                (box.x0 + 4, box.y0 + 16),
                _display({"kind": "int", "value": value}),
                fontname="source_cf",
                fontsize=9.4,
            )
            temp = file.with_suffix(".edited.pdf")
            pdf.save(temp)
        temp.replace(file)
    else:
        assert file.suffix == ".hwpx"
        with zipfile.ZipFile(file) as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        xml = ET.fromstring(members[selector["section"]])
        table = xml.findall(f".//{{{HP}}}tbl")[selector["table"]]
        row = table.findall(f"{{{HP}}}tr")[selector["row"]]
        cell = row.findall(f"{{{HP}}}tc")[selector["column"]]
        texts = list(cell.iter(f"{{{HP}}}t"))
        texts[0].text = str(value)
        for text in texts[1:]:
            text.text = ""
        members[selector["section"]] = ET.tostring(xml, encoding="utf-8", xml_declaration=True)
        with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, content in members.items():
                archive.writestr(name, content)
