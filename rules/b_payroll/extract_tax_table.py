"""Rebuild the vendored table from the original official PDF, without interpolation.

Run: uv run python -m rules.b_payroll.extract_tax_table
The independent 2023 NTS spreadsheet agrees with every wage/family table cell.
Only the separately applied child credit changed in the 2026 annex.
"""

import hashlib
import json
from pathlib import Path
import re

import pymupdf


ROOT = Path(__file__).parent
PDF_URL = "https://www.law.go.kr/LSW/flDownload.do?flSeq=164357181"


def extract(path: Path) -> dict:
    rows = []
    at_ten_million = None
    with pymupdf.open(path) as document:
        for page in document:
            for line in page.get_text(sort=True).splitlines():
                parts = line.split()
                if len(parts) == 13 and all(re.fullmatch(r"[0-9,]+|-", x) for x in parts):
                    values = [0 if x == "-" else int(x.replace(",", "")) for x in parts]
                    if 770 <= values[0] < values[1] <= 10000:
                        rows.append([values[0] * 1000, values[1] * 1000, *values[2:]])
                elif parts and parts[0] == "10,000천원" and len(parts) == 12:
                    at_ten_million = [int(x.replace(",", "")) for x in parts[1:]]
    assert len(rows) == 646
    assert rows[0][0] == 770000 and rows[-1][1] == 10000000
    assert all(a[1] == b[0] for a, b in zip(rows, rows[1:]))
    assert at_ten_million is not None and len(at_ten_million) == 11
    return {
        "source": PDF_URL,
        "description": "소득세법 시행령 별표 2, 개정 2026.2.27, 제6호의 원문 표",
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "columns": ["minimum_won_inclusive", "maximum_won_exclusive", *range(1, 12)],
        "rows": rows,
        "at_ten_million": at_ten_million,
    }


if __name__ == "__main__":
    table = extract(ROOT / "evidence" / "income_tax_table_2026.pdf")
    (ROOT / "income_tax_table.json").write_text(
        json.dumps(table, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
