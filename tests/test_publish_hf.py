"""Public publishing is fail-closed and never mutates the Hub during dry-run."""

from dataclasses import replace
import hashlib
import json
from types import SimpleNamespace

import pytest

from scripts import publish_hf as publishing


def test_reviewed_card_preserves_metadata_and_binds_to_current_export(tmp_path):
    manifest = {
        "dataset_name": "KrRubberStamp-1.65K",
        "canary": "current-canary",
        "jsonl_sha256": "current-jsonl-hash",
    }
    card = tmp_path / "card.md"
    content = "---\nlanguage: [ko]\n---\n# KrRubberStamp-1.65K\ndata/train.jsonl\ncurrent-canary\ncurrent-jsonl-hash\n"
    card.write_text(content)
    assert publishing.publication_card(manifest, card_path=card) == content


@pytest.mark.parametrize("stale", ["current-canary", "current-jsonl-hash", "data/train.jsonl"])
def test_stale_custom_card_is_rejected_before_publication(tmp_path, stale):
    manifest = {
        "dataset_name": "KrRubberStamp-1.65K",
        "canary": "current-canary",
        "jsonl_sha256": "current-jsonl-hash",
    }
    card = tmp_path / "card.md"
    content = "KrRubberStamp-1.65K data/train.jsonl current-canary current-jsonl-hash"
    card.write_text(content.replace(stale, "obsolete"))
    with pytest.raises(ValueError, match="this exact export"):
        publishing.publication_card(manifest, card_path=card)


@pytest.fixture
def minimum_export(tmp_path):
    manifest = {
        "rows": 1650,
        "dataset_name": "KrRubberStamp-1.65K",
        "batches": [1, 2],
        "preview": False,
        "authorship": "individually_written",
        "jsonl_sha256": hashlib.sha256(b"\n").hexdigest(),
    }
    for filename in publishing.ROOT_FILES | {"data/train.jsonl", "rules/sources.yaml"}:
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")
    (tmp_path / "data/train.jsonl").write_bytes(b"\n")
    (tmp_path / "README.md").write_text("KrRubberStamp-1.65K data/train.jsonl\n")
    (tmp_path / "export_manifest.json").write_text(json.dumps(manifest))
    return tmp_path, manifest


@pytest.mark.parametrize(
    "override",
    [
        {"rows": 1200},
        {"rows": 1800},
        {"rows": 2400},
        {"rows": 1650.0},
        {"batches": [True, 2]},
        {"rows": 3600},
        {"rows": 4800},
        {"preview": True},
        {"batches": [1, 2, 3]},
        {"batches": [1, 2, 3, 4]},
        {"dataset_name": "KrRubberStamp-4.8K"},
    ],
)
def test_incomplete_release_never_reaches_upstream_or_network(
    minimum_export, monkeypatch, override
):
    folder, manifest = minimum_export
    manifest.update(override)
    (folder / "export_manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(publishing, "collect_authored_tasks", lambda *_: pytest.fail("unsafe gate"))
    assert publishing.main([str(folder), "--publish"]) == 1


def test_missing_required_artifact_blocks_even_complete_manifest(minimum_export, monkeypatch):
    folder, _ = minimum_export
    (folder / "DATA_LICENSE").unlink()
    monkeypatch.setattr(publishing, "collect_authored_tasks", lambda *_: pytest.fail("unsafe gate"))
    assert publishing.main([str(folder), "--publish"]) == 1


def test_upstream_identity_rejection_precedes_publishing(minimum_export, monkeypatch):
    folder, _ = minimum_export

    def stale_source(*_):
        raise ValueError("Authored source has changed since this task was built")

    monkeypatch.setattr(publishing, "collect_authored_tasks", stale_source)
    monkeypatch.setattr(
        publishing, "publish", lambda *_: pytest.fail("must not publish stale export")
    )
    assert publishing.main([str(folder), "--publish"]) == 1


def test_dry_run_does_not_authenticate_or_publish(minimum_export, monkeypatch, capsys):
    folder, manifest = minimum_export
    manifest["task_set_sha256"] = "fixture-hash"
    plan = publishing.PublishPlan(folder, ("README.md",), (), manifest)
    monkeypatch.setattr(publishing, "preflight", lambda *_: plan)
    monkeypatch.setattr(publishing, "publish", lambda *_: pytest.fail("dry-run mutated Hub"))
    assert publishing.main([str(folder)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["dry_run"] is True and result["uploaded"] is False
    assert result["rows"] == 1650 and result["dataset_name"] == "KrRubberStamp-1.65K"


def test_private_files_and_symlink_inputs_cannot_enter_export(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/.env").write_text("private fixture")
    with pytest.raises(ValueError, match="private or hidden"):
        publishing.inventory(tmp_path)
    (tmp_path / "data/.env").unlink()
    outside = tmp_path / "outside.pdf"
    outside.write_text("fixture")
    (tmp_path / "data/linked.pdf").symlink_to(outside)
    with pytest.raises(ValueError, match="Symlink"):
        publishing.artifact(tmp_path, "data/linked.pdf")


@pytest.mark.parametrize("directory", ["data/batch_3", "authored/batch_4"])
def test_unrequested_batch_artifacts_cannot_enter_export(tmp_path, directory):
    path = tmp_path / directory / "extra.json"
    path.parent.mkdir(parents=True)
    path.write_text("[]\n")
    with pytest.raises(ValueError, match="Only Batch 1 and Batch 2"):
        publishing.inventory(tmp_path)


@pytest.mark.parametrize(
    "relative",
    ["authored/batch_2/D_extract/cases_151_200.json", "data/batch_2/D_extract/B2_D151/extra.pdf"],
)
def test_unreferenced_case_artifact_cannot_hide_beside_1650_rows(tmp_path, relative):
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text("fixture\n")
    with pytest.raises(ValueError, match="Unreferenced case artifact"):
        publishing.inventory(tmp_path, declared_case_files={"data/train.jsonl"})


def test_default_publish_folder_is_final_two_batch_export(monkeypatch):
    def inspect_folder(folder):
        assert folder == publishing.Path("exports/upto_2")
        raise ValueError("fixture gate")

    monkeypatch.setattr(publishing, "preflight", inspect_folder)
    assert publishing.main([]) == 1


def test_revision_pinned_download_detects_remote_corruption(tmp_path):
    names = (
        "README.md",
        "export_manifest.json",
        "data/train.jsonl",
        *(f"data/batch_{batch}/manifest.json" for batch in publishing.BATCHES),
        "data/batch_2/sample.pdf",
    )
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(name.encode())
    plan = publishing.PublishPlan(tmp_path, names, (names[-1],), {})
    revision = "a" * 40

    class Hub:
        def repo_info(self, **_):
            return SimpleNamespace(sha=revision)

        def list_repo_files(self, **kwargs):
            assert kwargs["revision"] == revision
            return [*names, ".gitattributes"]

        def hf_hub_download(self, **kwargs):
            assert kwargs["revision"] == revision
            return tmp_path / kwargs["filename"]

    result = publishing.verify_remote(Hub(), plan, "fixture/KrRubberStamp-1.65K")
    assert result["revision"] == revision and result["downloaded_files_checked"] == len(names)
    assert result["rows"] == 1650
    bad = tmp_path / "bad"
    bad.write_bytes(b"corrupt")
    hub = Hub()
    original = hub.hf_hub_download
    hub.hf_hub_download = lambda **kw: bad if kw["filename"] == names[-1] else original(**kw)
    with pytest.raises(ValueError, match="Downloaded release artifact differs"):
        publishing.verify_remote(hub, plan, "fixture/KrRubberStamp-1.65K")
    with pytest.raises(ValueError, match="Remote files differ"):
        publishing.verify_remote(
            Hub(), replace(plan, files=names[:-1]), "fixture/KrRubberStamp-1.65K"
        )


@pytest.fixture
def reviewed_manuscript(tmp_path):
    source = "authored/batch_2/D_extract/cases_001_050.json"
    path = tmp_path / source
    path.parent.mkdir(parents=True)
    path.write_text('[{"case_id":"D001"}]\n')
    ledger = {
        "batch": 2,
        "accepted_chunks": [
            {
                "source_file": source,
                "ids": ["D001"],
                "accepted_cases": 1,
                "source_sha256": publishing.sha256(path),
            }
        ],
    }
    acceptance = tmp_path / "reports/authoring_acceptance_batch_2.json"
    acceptance.parent.mkdir()
    acceptance.write_text(json.dumps(ledger))
    records = [
        {
            "batch": 2,
            "case": {"case_id": "D001"},
            "task": {"authorship": {"source_file": source.removeprefix("authored/")}},
        }
    ]
    return tmp_path, path, acceptance, ledger, records


def test_reviewed_manuscript_hash_and_ids_pass(reviewed_manuscript):
    folder, _, _, _, records = reviewed_manuscript
    publishing.check_editorial_acceptances(folder, records)


def test_changed_manuscript_cannot_reuse_review(reviewed_manuscript):
    folder, path, _, _, records = reviewed_manuscript
    path.write_text('[{"case_id":"D001","unreviewed":"change"}]\n')
    with pytest.raises(ValueError, match="changed after"):
        publishing.check_editorial_acceptances(folder, records)


def test_review_hash_cannot_cover_an_extra_unpublished_case(reviewed_manuscript):
    folder, path, acceptance, ledger, records = reviewed_manuscript
    path.write_text('[{"case_id":"D001"},{"case_id":"D151"}]\n')
    ledger["accepted_chunks"][0]["source_sha256"] = publishing.sha256(path)
    acceptance.write_text(json.dumps(ledger))
    with pytest.raises(ValueError, match="outside its accepted identities"):
        publishing.check_editorial_acceptances(folder, records)


@pytest.mark.parametrize("change", ["missing", "duplicate", "wrong_ids", "wrong_count"])
def test_unreviewed_or_ambiguous_expansion_is_rejected(reviewed_manuscript, change):
    folder, _, acceptance, ledger, records = reviewed_manuscript
    chunks = ledger["accepted_chunks"]
    if change == "missing":
        chunks.clear()
    elif change == "duplicate":
        chunks.append(dict(chunks[0]))
    elif change == "wrong_ids":
        chunks[0]["ids"] = ["D999"]
    else:
        chunks[0]["accepted_cases"] = True
    acceptance.write_text(json.dumps(ledger))
    with pytest.raises(ValueError):
        publishing.check_editorial_acceptances(folder, records)
