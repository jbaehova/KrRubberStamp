"""Authored exports stay readable offline and do not certify stale measurements."""

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from KrRubberStamp import authoring, export
from KrRubberStamp.io import read_json, write_json
from harness import run_fake, stage_task
from validate import validate_batch


@pytest.mark.parametrize("batches", [[3], [4], [1, 2, 3], [1, 2, 3, 4], [True]])
def test_export_rejects_batches_outside_final_scope_before_reading_data(tmp_path, batches):
    output = tmp_path / "export"
    with pytest.raises(ValueError, match="unique authorized batch numbers"):
        export.export_hf(tmp_path / "absent", batches, output, allow_preview=True)
    assert not output.exists()


@pytest.fixture
def authored_export(tmp_path, monkeypatch):
    project = tmp_path / "project"
    source = project / "authored/batch_1/D_extract/editorial.json"
    source.parent.mkdir(parents=True)
    case = {
        "case_id": "D999",
        "domain": "D_extract",
        "difficulty": "easy",
        "title": "가상 임시 매장 진열 선반 발주",
        "instruction": "임시 매장의 진열 선반 발주서와 배달료 안내를 확인해 총 결제액 grand_total을 answer.json에 적어 주세요.",
        "work_goal": "한 곳의 부품 공급처에 지급할 예정액 확인",
        "design_rationale": "선반 수량과 단가를 읽고 운송비를 포함한 결제액을 확정한다.",
        "exceptions": [],
        "facts": {
            "documents": [
                {
                    "document_id": "SHELF-03",
                    "vendor": "가상수납공방",
                    "price_includes_vat": False,
                    "items": [{"name": "진열선반", "quantity": 2, "unit_price": 71000}],
                }
            ],
        },
        "answer_fields": ["grand_total"],
        "documents": [
            {
                "filename": "01_선반발주.pdf",
                "format": "pdf",
                "title": "임시 매장 진열 선반 발주서",
                "note": "운송비는 없으며 세액은 별도로 청구합니다.",
                "fields": ["documents"],
            }
        ],
    }
    write_json(source, [case])
    monkeypatch.setattr(authoring, "authored_root", lambda: project / "authored")
    for filename in ("DATA_LICENSE", "LICENSE", "DECISIONS.md", "DATA_SPEC.md"):
        (project / filename).write_text(f"Fixture {filename}\n", encoding="utf-8")
    report_root = project / "reports"
    report_root.mkdir()
    rules_path = project / "rules/sources.yaml"
    rules_path.parent.mkdir()
    rules_path.write_text(
        yaml.safe_dump(
            {
                "rules": [
                    {
                        "rule_id": "D.FIXTURE",
                        "description": "가상 수치 회귀 근거",
                        "verified": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(export, "_document_root", lambda: project)
    monkeypatch.setattr(export, "_rule_path", lambda: rules_path)
    batch = project / "data/batch_1"
    authoring.build_authored(batch, preview=True)
    write_json(report_root / "validation_authored_preview.json", validate_batch(batch))
    for solver in ("oracle", "null"):
        result = run_fake(batch, tmp_path / f"answers_{solver}", solver)
        write_json(report_root / f"{solver}_authored_preview.json", result)
    return project, batch, source


def _reports_module():
    path = Path(__file__).resolve().parents[1] / "scripts/build_reports.py"
    spec = importlib.util.spec_from_file_location("authored_reports", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_offline_authored_snapshot_preserves_paths_and_separates_model_inputs(
    authored_export, tmp_path
):
    project, _, _ = authored_export
    output = tmp_path / "export"
    result = export.export_hf(project / "data", [1], output, allow_preview=True)
    assert result["rows"] == 1 and result["dataset_name"] == "KrRubberStamp-preview-1"
    assert not result["uploaded"] and not result["actual_model_evaluated"]
    assert result["measurements"]["1"]["oracle"]["exact_match"] == 1
    row = json.loads((output / "data/train.jsonl").read_text(encoding="utf-8"))
    assert row["authorship"]["method"] == "individually_written"
    assert isinstance(row["gold"], str) and json.loads(row["gold"]) == {"grand_total": 156200}
    for key in (
        "task_path",
        "gold_path",
        "trace_path",
        "extraction_map_path",
        "authored_source_path",
    ):
        assert (output / row[key]).is_file()
    for item in row["input_files"]:
        assert (output / item["path"]).is_file()
    sources = read_json(output / row["authored_source_path"])
    assert len(sources) == 1 and sources[0]["case_id"] == "D999"
    workspace = stage_task((output / row["task_path"]).parent, tmp_path / "workspaces")
    files = {path.name for path in workspace.rglob("*") if path.is_file()}
    assert files == {"01_선반발주.pdf", "instruction.txt", "answer_schema.json"}
    card = (output / "README.md").read_text(encoding="utf-8")
    assert "미완성 미리보기" in card and "instruction_consistency" in card
    assert "새 시드 출력은 개별 집필 평가본을 대체하지" in card
    assert "--seed 987654" not in card


def test_preview_cannot_be_exported_or_reported_as_a_completed_release(authored_export, tmp_path):
    project, batch, _ = authored_export
    with pytest.raises(ValueError, match="preview"):
        export.export_hf(project / "data", [1], tmp_path / "release")
    assert not (tmp_path / "release").exists()
    with pytest.raises(ValueError, match="preview"):
        _reports_module().build_reports(batch, output=tmp_path / "reports", project_root=project)
    assert not (tmp_path / "reports").exists()
    # Merely changing the manifest flag cannot bypass the release quota.
    manifest = read_json(batch / "manifest.json")
    manifest["preview"] = False
    write_json(batch / "manifest.json", manifest)
    with pytest.raises(ValueError, match="90/135/75"):
        export.export_hf(project / "data", [1], tmp_path / "release")


def test_export_refuses_changed_sources_and_stale_measurements(authored_export, tmp_path):
    project, _, source = authored_export
    measurements = project / "reports/oracle_authored_preview.json"
    oracle = read_json(measurements)
    oracle["tasks"][0]["task_id"] = "an_old_generated_task"
    write_json(measurements, oracle)
    with pytest.raises(ValueError, match="another task set"):
        export.export_hf(project / "data", [1], tmp_path / "export", allow_preview=True)
    assert not (tmp_path / "export").exists()
    case = read_json(source)
    case[0]["facts"]["documents"][0]["items"][0]["quantity"] = 4
    write_json(source, case)
    with pytest.raises(ValueError, match="source has changed"):
        export.export_hf(project / "data", [1], tmp_path / "export", allow_preview=True)


def test_preview_report_uses_actual_counts_and_current_results(authored_export, tmp_path):
    project, batch, _ = authored_export
    module = _reports_module()
    output = tmp_path / "review"
    result = module.build_reports(
        batch, project / "reports", output, project_root=project, preview=True
    )
    assert result["tasks"] == 1 and result["review_tasks"] == 1
    assert not (output / "BATCH_1_REPORT.md").exists()
    report = (output / "AUTHORED_PREVIEW_REPORT.md").read_text(encoding="utf-8")
    queue = (output / "REVIEW_QUEUE_AUTHORED_PREVIEW.md").read_text(encoding="utf-8")
    assert "| D_extract | 1 | 0 | 0 | 1 |" in report
    assert "| oracle | 1 | 100% | 100% | 1 |" in report
    assert "현재 규칙 출처 1개" in report and "verified: false는 1개" in report
    assert "독립적으로 분석하는 검사는 아닙니다" in report
    assert "검수 상태: 대기" in queue
    assert "gold.json" in queue and "trace.json" in queue and "집필 원고" in queue
    before = queue
    module.build_reports(batch, project / "reports", output, project_root=project, preview=True)
    assert (output / "REVIEW_QUEUE_AUTHORED_PREVIEW.md").read_text(encoding="utf-8") == before


def test_export_never_copies_unrelated_or_superseded_report_files(authored_export, tmp_path):
    project, _, _ = authored_export
    old = project / "reports/BATCH_1_REPORT.md"
    old.write_text("Old template-generated 1200 score", encoding="utf-8")
    (project / "reports/validation_batch_1.json").write_text('{"old": true}', encoding="utf-8")
    output = tmp_path / "export"
    export.export_hf(project / "data", [1], output, allow_preview=True)
    assert not (output / "reports/BATCH_1_REPORT.md").exists()
    assert not (output / "reports/validation_batch_1.json").exists()
    assert (output / "reports/validation_authored_preview.json").is_file()
