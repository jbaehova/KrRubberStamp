"""Receiving facts determine selection before the unchanged document arithmetic."""

from copy import deepcopy

import pytest

from KrRubberStamp.registry import calculate
from rules.d_extract.evidence import CONTRACT, interpret


def source():
    return {
        "source_contract": CONTRACT,
        "processing_policy": "실제 인수한 주문과 계산서만 연결해 집계한다. 견적과 출고 전 취소는 제외한다.",
        "headers": [
            {
                "record_id": "h1",
                "document_id": "INV1",
                "kind": "invoice",
                "vendor": "가상도구",
                "date": "2026-04-01",
                "price_includes_vat": False,
            },
            {
                "record_id": "h2",
                "document_id": "Q2",
                "kind": "quote",
                "vendor": "가상예산",
                "date": "2026-04-01",
                "price_includes_vat": False,
            },
            {
                "record_id": "h3",
                "document_id": "ORD3",
                "kind": "order",
                "vendor": "가상주문",
                "date": "2026-04-01",
                "price_includes_vat": False,
            },
        ],
        "line_sheets": [
            {
                "sheet_id": "s1",
                "header_record_id": "h1",
                "items": [{"name": "망치", "quantity": 2, "unit_price": 10000}],
            },
            {
                "sheet_id": "s2",
                "header_record_id": "h1",
                "items": [{"name": "고정판", "quantity": 3, "unit_price": 10000}],
            },
            {
                "sheet_id": "s3",
                "header_record_id": "h2",
                "items": [{"name": "예산공구", "quantity": 10, "unit_price": 80000}],
            },
            {
                "sheet_id": "s4",
                "header_record_id": "h3",
                "items": [{"name": "취소공구", "quantity": 7, "unit_price": 10000}],
            },
        ],
        "events": [
            {
                "event_id": "e1",
                "document_id": "INV1",
                "event": "received",
                "date": "2026-04-03",
                "location": "가상작업장",
            },
            {
                "event_id": "e2",
                "document_id": "ORD3",
                "event": "cancelled_before_dispatch",
                "date": "2026-04-02",
                "location": "가상주문접수실",
            },
        ],
    }


def test_original_attachments_join_by_header_and_actual_receipt_excludes_other_records():
    raw = source()
    before = deepcopy(raw)
    normalized = interpret(raw)
    assert len(normalized["documents"]) == 1
    assert len(normalized["documents"][0]["items"]) == 2
    answer, trace = calculate("D_extract", raw)
    assert answer["grand_total"] == 55000
    assert answer["unique_document_count"] == 1
    assert trace[0]["output"]["excluded_document_ids"] == ["ORD3", "Q2"]
    assert raw == before


def test_cancellation_changed_to_actual_receipt_adds_its_amount():
    raw = source()
    raw["events"][1]["event"] = "received"
    answer, _ = calculate("D_extract", raw)
    assert answer["grand_total"] == 132000
    assert answer["unique_document_count"] == 2


def test_identical_reissued_header_and_attachment_are_counted_once():
    raw = source()
    header = deepcopy(raw["headers"][0])
    header["record_id"] = "h4"
    raw["headers"].append(header)
    for old in raw["line_sheets"][:2]:
        sheet = deepcopy(old)
        sheet.update(sheet_id=sheet["sheet_id"] + "copy", header_record_id="h4")
        raw["line_sheets"].append(sheet)
    normalized = interpret(raw)
    assert len(normalized["documents"]) == 2
    answer, trace = calculate("D_extract", raw)
    assert answer["grand_total"] == 55000
    assert answer["unique_document_count"] == 1
    assert any(step["rule_id"] == "D.deduplicate" for step in trace)


@pytest.mark.parametrize("group", ["headers", "line_sheets", "events"])
def test_duplicate_source_identities_are_rejected(group):
    raw = source()
    raw[group].append(deepcopy(raw[group][0]))
    with pytest.raises(ValueError, match="Duplicate raw"):
        interpret(raw)


def test_conflicting_actual_receipt_and_cancellation_cannot_be_cherry_picked():
    raw = source()
    event = deepcopy(raw["events"][0])
    event.update(event_id="e3", event="cancelled_before_dispatch")
    raw["events"].append(event)
    with pytest.raises(ValueError, match="Conflicting procurement event"):
        interpret(raw)


def test_quote_is_not_an_actual_physical_receiving_record():
    raw = source()
    raw["events"].append(
        {
            "event_id": "e3",
            "document_id": "Q2",
            "event": "received",
            "date": "2026-04-03",
            "location": "가상작업장",
        }
    )
    with pytest.raises(ValueError, match="Quote cannot"):
        interpret(raw)


@pytest.mark.parametrize(
    "mutation,message",
    [
        (lambda raw: raw["line_sheets"][0].update(header_record_id="missing"), "Unknown item"),
        (lambda raw: raw["events"][0].update(document_id="missing"), "Unknown receiving"),
        (lambda raw: raw["events"][0].update(date="2026-03-01"), "predates"),
        (lambda raw: raw["line_sheets"][0]["items"][0].update(quantity=0), "bounded integer"),
        (lambda raw: raw.update(documents=[]), "preselected"),
        (lambda raw: raw["line_sheets"].pop(2), "requires an item"),
    ],
)
def test_incomplete_or_preselected_evidence_is_rejected(mutation, message):
    raw = source()
    mutation(raw)
    with pytest.raises(ValueError, match=message):
        interpret(raw)


def test_raw_join_contract_survives_real_pdf_xlsx_hwpx_and_oracle(tmp_path, monkeypatch):
    from KrRubberStamp import authoring
    from KrRubberStamp.io import write_json
    from harness import run_fake
    from validate import validate_batch

    root = tmp_path / "authored"
    case = {
        "case_id": "D998",
        "domain": "D_extract",
        "difficulty": "medium",
        "title": "가상 작업장 인수 자료 마감",
        "instruction": "표지 번호와 품목 부속표를 연결하고 실제 인수 기록을 확인해 지급 총액과 실제 거래 수를 answer.json의 grand_total 및 unique_document_count에 적어 주세요.",
        "work_goal": "견적과 출고 전 취소 주문을 인수 마감에서 구별",
        "design_rationale": "품목 표와 표지는 별개 파일이고 실제 인수한 자료만 결제 대상이다.",
        "exceptions": ["physical_receiving_reconciliation"],
        "facts": source(),
        "answer_fields": ["grand_total", "unique_document_count"],
        "documents": [
            {
                "filename": "01_집계방침.pdf",
                "format": "pdf",
                "title": "가상 작업장 마감 방침",
                "note": "품목별 공급가액은 수량 곱하기 단가이고 세액은 공급가액의 10%에서 원 미만을 버린 값이다. 자료 연결과 실제 인수 기준을 따른다.",
                "fields": ["source_contract", "processing_policy"],
                "template_variant": 3,
            },
            {
                "filename": "02_거래표지.pdf",
                "format": "pdf",
                "title": "거래 원본 표지",
                "note": "문서 종류와 표지 기록 번호를 기재했다.",
                "fields": ["headers"],
                "template_variant": 2,
            },
            {
                "filename": "03_품목부속표.xlsx",
                "format": "xlsx",
                "title": "원본 품목 내역",
                "note": "표지 기록 번호에 연결된 부속표다.",
                "fields": ["line_sheets"],
                "template_variant": 1,
            },
            {
                "filename": "04_현장접수.hwpx",
                "format": "hwpx",
                "title": "현장 인수와 취소 기록",
                "note": "실제 접수 상태를 기록했다.",
                "fields": ["events"],
                "template_variant": 4,
            },
        ],
    }
    write_json(root / "batch_1/D_extract/fixture.json", [case])
    monkeypatch.setattr(authoring, "authored_root", lambda: root)
    output = tmp_path / "tasks"
    authoring.build_authored(output, preview=True)
    assert validate_batch(output)["all_passed"]
    assert run_fake(output, tmp_path / "answers", "oracle")["exact_match"] == 1
