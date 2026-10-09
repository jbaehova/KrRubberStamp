"""Authored facts remain literal; factories cannot enter the curated build."""

import json
import yaml
import pytest

from KrRubberStamp import authoring
from harness import run_fake
from validate import validate_task


@pytest.fixture
def editorial_source(tmp_path, monkeypatch):
    root = tmp_path / "authored"
    path = root / "batch_1/D_extract/editorial.json"
    path.parent.mkdir(parents=True)
    case = {
        "case_id": "D999",
        "domain": "D_extract",
        "difficulty": "easy",
        "title": "가상 대피소 물품 결제 확인",
        "instruction": "가상 대피소에서 구매한 구급함과 보관상자의 업체별 합계 vendor_totals와 총 결제액 grand_total을 answer.json에 정리해 주세요. 업체명은 공백 제거와 NFKC 및 대소문자 정규화 후 오름차순으로 적어 주세요.",
        "work_goal": "대피소 구매 영수증과 발주 금액을 대조하기 위한 합계",
        "design_rationale": "서로 다른 두 업체의 보완 물품을 합쳐 결제 예정액을 확인한다.",
        "exceptions": [],
        "facts": {
            "documents": [
                {
                    "document_id": "AID-01",
                    "vendor": "가상돌봄상사",
                    "price_includes_vat": False,
                    "items": [{"name": "구급함", "quantity": 3, "unit_price": 47000}],
                },
                {
                    "document_id": "BOX-07",
                    "vendor": "가상보관상점",
                    "price_includes_vat": False,
                    "items": [{"name": "방수보관상자", "quantity": 4, "unit_price": 26000}],
                },
            ]
        },
        "answer_fields": ["vendor_totals", "grand_total"],
        "documents": [
            {
                "filename": "01_구급함.pdf",
                "format": "pdf",
                "title": "임시 대피소 구급함 발주 확인",
                "note": "응급함은 세트 단위로 공급합니다. 세액은 별도 청구됩니다.",
                "fields": ["documents.0"],
            },
            {
                "filename": "02_보관상자.xlsx",
                "format": "xlsx",
                "title": "방수 보관상자 거래 내역",
                "note": "현장 배부용 보관상자입니다. 결제 담당자는 두 업체의 청구를 함께 확인합니다.",
                "fields": ["documents.1"],
            },
        ],
    }
    path.write_text(json.dumps([case], ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(authoring, "authored_root", lambda: root)
    return path, case


def test_curated_builder_never_generates_case_facts(editorial_source, tmp_path, monkeypatch):
    import validate.quality

    def forbid_factory(*args):
        raise AssertionError("A random scenario factory was used for an authored task")

    monkeypatch.setattr(validate.quality, "generate_scenario", forbid_factory)
    output = tmp_path / "preview"
    summary = authoring.build_authored(output, preview=True)
    assert summary["accepted"] == 1
    task_dir = next(output.glob("*/*/task.yaml")).parent
    assert validate_task(task_dir)["passed"]
    answer = json.loads((task_dir / "gold.json").read_text(encoding="utf-8"))
    assert set(answer) == {"vendor_totals", "grand_total"}
    assert run_fake(output, tmp_path / "oracle", "oracle")["exact_match"] == 1
    assert run_fake(output, tmp_path / "null", "null")["exact_match"] == 0


def test_changed_case_or_answer_request_fails_closed(editorial_source, tmp_path):
    source, case = editorial_source
    output = tmp_path / "preview"
    authoring.build_authored(output, preview=True)
    task_dir = next(output.glob("*/*/task.yaml")).parent
    metadata_path = task_dir / "task.yaml"
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    metadata["answer_fields"] = ["grand_total"]
    metadata_path.write_text(yaml.safe_dump(metadata, allow_unicode=True), encoding="utf-8")
    result = validate_task(task_dir)
    assert not result["passed"] and "Answer request differs" in result["errors"][0]
    case["facts"]["documents"][0]["items"][0]["quantity"] = 5
    source.write_text(json.dumps([case], ensure_ascii=False), encoding="utf-8")
    result = validate_task(task_dir)
    assert not result["passed"] and "source has changed" in result["errors"][0]


def test_preview_cannot_be_mistaken_for_completed_batch(editorial_source, tmp_path):
    with pytest.raises(ValueError, match="300 individually authored"):
        authoring.build_authored(tmp_path / "release")
    assert not (tmp_path / "release").exists()


@pytest.mark.parametrize("batch", [2, 4])
def test_new_batch_recovers_its_own_manuscript(editorial_source, tmp_path, batch):
    source, _ = editorial_source
    target = source.parents[2] / f"batch_{batch}" / "D_extract/editorial.json"
    target.parent.mkdir(parents=True)
    source.rename(target)
    output = tmp_path / "preview"
    summary = authoring.build_authored(output, batch=batch, preview=True)
    assert summary["batch"] == batch and summary["accepted"] == 1
    task_path = next(output.glob("*/*/task.yaml"))
    task = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    assert task["task_id"].startswith(f"B{batch}_D999_")
    assert task["authorship"]["source_file"] == f"batch_{batch}/D_extract/editorial.json"
    assert validate_task(task_path.parent)["passed"]


@pytest.mark.parametrize("batch", [0, 5])
def test_unrequested_batch_is_not_published(editorial_source, tmp_path, batch):
    output = tmp_path / "unrequested"
    with pytest.raises(ValueError, match="four authorized"):
        authoring.build_authored(output, batch=batch, preview=True)
    assert not output.exists()


def test_duplicate_literals_are_rejected(editorial_source, tmp_path):
    source, case = editorial_source
    duplicate = json.loads(json.dumps(case))
    duplicate["case_id"] = "D998"
    duplicate["instruction"] += " 구급함 발주 담당자도 확인할 예정입니다."
    source.write_text(json.dumps([case, duplicate], ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="Repeated authored facts"):
        authoring.build_authored(tmp_path / "preview", preview=True)


def test_failed_render_does_not_publish_partial_dataset(editorial_source, tmp_path, monkeypatch):
    import render.authored

    def fail(*args, **kwargs):
        raise ValueError("Unreadable authored document")

    monkeypatch.setattr(render.authored, "render_authored", fail)
    output = tmp_path / "review"
    with pytest.raises(ValueError, match="Unreadable authored"):
        authoring.build_authored(output, preview=True)
    assert not output.exists()
    assert not list(tmp_path.glob(".review-*"))


def test_domain_preview_does_not_read_an_unfinished_other_manuscript(editorial_source, tmp_path):
    path, _ = editorial_source
    other = path.parents[1] / "C_vat/editorial.json"
    other.parent.mkdir()
    other.write_text('[{"case_id": "C998",', encoding="utf-8")
    summary = authoring.build_authored(
        tmp_path / "preview", preview=True, file_name="editorial.json", domain="D_extract"
    )
    assert summary["accepted"] == 1
    with pytest.raises(ValueError, match="subset"):
        authoring.build_authored(tmp_path / "release", domain="D_extract")
