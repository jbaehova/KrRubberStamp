"""Join original headers, item attachments and physical receiving records."""

from copy import deepcopy
from datetime import date

CONTRACT = "extract_evidence_v1"
RULE_ID = "D.evidence_reconciliation"


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Raw procurement evidence requires {name}")
    return value


def _date(value):
    _text(value, "date")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Raw procurement date must use ISO calendar format")
    return parsed


def _records(source, name, fields, identity):
    rows = source.get(name)
    if not isinstance(rows, list):
        raise ValueError(f"Raw procurement {name} must be a list")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError(f"Raw procurement {name} has unknown or missing fields")
        key = _text(row[identity], identity)
        if key in seen:
            raise ValueError(f"Duplicate raw procurement {identity}")
        seen.add(key)
    return rows


def interpret(source):
    if source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown raw procurement evidence contract")
    if "documents" in source:
        raise ValueError("Raw procurement source exposes preselected joined documents")
    _text(source.get("processing_policy"), "visible processing policy")
    headers = _records(
        source,
        "headers",
        {"record_id", "document_id", "kind", "vendor", "date", "price_includes_vat"},
        "record_id",
    )
    sheets = _records(source, "line_sheets", {"sheet_id", "header_record_id", "items"}, "sheet_id")
    events = _records(
        source, "events", {"event_id", "document_id", "event", "date", "location"}, "event_id"
    )
    by_record = {}
    by_document = {}
    for header in headers:
        _text(header["document_id"], "document_id")
        _text(header["vendor"], "vendor")
        _date(header["date"])
        if header["kind"] not in {"invoice", "quote", "order"}:
            raise ValueError("Unsupported raw procurement document kind")
        if type(header["price_includes_vat"]) is not bool:
            raise ValueError("Raw procurement VAT inclusion must be a boolean")
        by_record[header["record_id"]] = header
        by_document.setdefault(header["document_id"], []).append(header)
    joined = {identity: [] for identity in by_record}
    for sheet in sheets:
        if sheet["header_record_id"] not in by_record:
            raise ValueError("Unknown item attachment header reference")
        if not isinstance(sheet["items"], list) or not sheet["items"]:
            raise ValueError("Item attachment must contain original item lines")
        for item in sheet["items"]:
            if not isinstance(item, dict) or set(item) != {"name", "quantity", "unit_price"}:
                raise ValueError("Unknown or missing original item fields")
            _text(item["name"], "item name")
            if (
                type(item["quantity"]) is not int
                or item["quantity"] <= 0
                or type(item["unit_price"]) is not int
                or item["unit_price"] < 0
            ):
                raise ValueError("Item quantity and unit price require bounded integer facts")
        joined[sheet["header_record_id"]].extend(deepcopy(sheet["items"]))
    if any(not items for items in joined.values()):
        raise ValueError("Every original header requires an item attachment")
    states = {}
    for event in events:
        identity = event["document_id"]
        if identity not in by_document:
            raise ValueError("Unknown receiving event document reference")
        _text(event["location"], "event location")
        day = _date(event["date"])
        if event["event"] not in {"received", "cancelled_before_dispatch"}:
            raise ValueError("Unsupported physical procurement event")
        if any(day < _date(header["date"]) for header in by_document[identity]):
            raise ValueError("Physical event predates its original document")
        if any(header["kind"] == "quote" for header in by_document[identity]):
            raise ValueError("Quote cannot have an actual dispatch or receiving event")
        state = (event["event"], event["date"], event["location"])
        if identity in states and states[identity] != state:
            raise ValueError("Conflicting procurement event state or receiving occurrence")
        states[identity] = state
    originals = {}
    documents = []
    for header in headers:
        document = {
            "document_id": header["document_id"],
            "vendor": header["vendor"],
            "date": header["date"],
            "price_includes_vat": header["price_includes_vat"],
            "items": joined[header["record_id"]],
        }
        identity = document["document_id"]
        if identity in originals and originals[identity] != document:
            raise ValueError("Conflicting duplicate procurement document")
        originals[identity] = document
        if header["kind"] != "quote" and states.get(identity, (None,))[0] == "received":
            documents.append(document)
    if not documents:
        raise ValueError("Raw receiving contract requires at least one actual received document")
    result = deepcopy(source)
    result["documents"] = documents
    return result


def derivation_trace(source, normalized):
    accepted = {row["document_id"] for row in normalized["documents"]}
    return {
        "rule_id": RULE_ID,
        "inputs": {
            "source_contract": CONTRACT,
            "headers": source["headers"],
            "line_sheets": source["line_sheets"],
            "events": source["events"],
            "processing_policy": source["processing_policy"],
        },
        "output": {
            "received_document_ids": sorted(accepted),
            "excluded_document_ids": sorted(
                {row["document_id"] for row in source["headers"]} - accepted
            ),
            "joined_document_records_before_deduplication": len(normalized["documents"]),
        },
    }
