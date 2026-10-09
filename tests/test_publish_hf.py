"""Public publishing is fail-closed and never mutates the Hub during dry-run."""

from dataclasses import replace
import hashlib
import json
from types import SimpleNamespace

import pytest

from scripts import publish_hf as publishing


@pytest.fixture
def minimum_export(tmp_path):
    manifest = {
        "rows": 4800,
        "dataset_name": "KrRubberStamp-4.8K",
        "batches": [1, 2, 3, 4],
        "preview": False,
        "authorship": "individually_written",
        "jsonl_sha256": hashlib.sha256(b"\n").hexdigest(),
    }
    for filename in publishing.ROOT_FILES | {"data/train.jsonl", "rules/sources.yaml"}:
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")
    (tmp_path / "data/train.jsonl").write_bytes(b"\n")
    (tmp_path / "README.md").write_text("KrRubberStamp-4.8K data/train.jsonl\n")
    (tmp_path / "export_manifest.json").write_text(json.dumps(manifest))
    return tmp_path, manifest


@pytest.mark.parametrize("override", [{"rows": 1200}, {"preview": True}, {"batches": [1, 2, 3]}])
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


def test_revision_pinned_download_detects_remote_corruption(tmp_path):
    names = (
        "README.md",
        "export_manifest.json",
        "data/train.jsonl",
        *(f"data/batch_{batch}/manifest.json" for batch in publishing.BATCHES),
        "data/batch_4/sample.pdf",
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

    result = publishing.verify_remote(Hub(), plan, "fixture/KrRubberStamp-4.8K")
    assert result["revision"] == revision and result["downloaded_files_checked"] == len(names)
    bad = tmp_path / "bad"
    bad.write_bytes(b"corrupt")
    hub = Hub()
    original = hub.hf_hub_download
    hub.hf_hub_download = lambda **kw: bad if kw["filename"] == names[-1] else original(**kw)
    with pytest.raises(ValueError, match="Downloaded release artifact differs"):
        publishing.verify_remote(hub, plan, "fixture/KrRubberStamp-4.8K")
    with pytest.raises(ValueError, match="Remote files differ"):
        publishing.verify_remote(
            Hub(), replace(plan, files=names[:-1]), "fixture/KrRubberStamp-4.8K"
        )
