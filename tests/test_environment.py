from pathlib import Path
import pymupdf
from KrRubberStamp import __version__


def test_environment_and_embedded_korean_font():
    assert __version__ == "0.1.0"
    sample = Path(__file__).resolve().parents[1] / "render/korean_sample.pdf"
    with pymupdf.open(sample) as pdf:
        assert "근로계약" in pdf[0].get_text()
        assert pdf[0].get_fonts()
