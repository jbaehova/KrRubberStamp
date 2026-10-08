"""Reconcile authored activity records without exposing tax-purpose outcomes.

This is a bounded factual contract, not a natural-language legal classifier.
The VAT engine retains responsibility for the deduction and settlement rules.
"""

from copy import deepcopy
from datetime import date

CONTRACT = "vat_activity_evidence_v1"
RULE_ID = "VAT_ACTIVITY_EVIDENCE"
DERIVED = {"purpose", "business_related"}
ACTIONS = {
    "delivery",
    "service",
    "meal",
    "vehicle_delivery",
    "vehicle_lease",
    "vehicle_service",
    "ground_work",
}
LOCATION_KINDS = {"worksite", "restaurant", "home", "land_parcel", "road"}
ROLES = {"employee", "proprietor", "customer", "household_member"}
ACTIVITY_FIELDS = {
    "activity_id",
    "transaction_id",
    "document_ids",
    "date",
    "action",
    "location",
    "participants",
    "operation_id",
    "description",
}


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Raw VAT evidence requires nonempty {field}")
    return value


def _date(value, field):
    _text(value, field)
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError(f"Raw VAT evidence requires ISO calendar {field}")


def _no_outcomes(value):
    if isinstance(value, dict):
        if DERIVED & value.keys():
            raise ValueError("Raw VAT source exposes compiled purchase purpose or business link")
        for child in value.values():
            _no_outcomes(child)
    elif isinstance(value, list):
        for child in value:
            _no_outcomes(child)


def _operations(source):
    rows = source.get("operations")
    if not isinstance(rows, list):
        raise ValueError("Raw VAT operations must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "operation_id",
            "description",
            "output_taxable",
        }:
            raise ValueError("Raw VAT operation has unknown or missing factual fields")
        identity = _text(row["operation_id"], "operation_id")
        _text(row["description"], "operation description")
        if type(row["output_taxable"]) is not bool:
            raise ValueError("Operation output_taxable must be an official boolean fact")
        if identity in result:
            raise ValueError("Duplicate raw VAT operation identity")
        result[identity] = row
    return result


def _activity(row, operations, taxpayer_name):
    if not isinstance(row, dict) or set(row) != ACTIVITY_FIELDS:
        raise ValueError("Raw VAT activity has unknown or missing factual fields")
    for field in ("activity_id", "transaction_id", "description"):
        _text(row[field], field)
    _date(row["date"], "activity date")
    documents = row["document_ids"]
    if not isinstance(documents, list) or not documents:
        raise ValueError("Activity must identify its source documents")
    if any(not isinstance(item, str) or not item.strip() for item in documents):
        raise ValueError("Invalid raw VAT document reference")
    if len(set(documents)) != len(documents):
        raise ValueError("Duplicate activity document reference")
    if _text(row["action"], "activity action") not in ACTIONS:
        raise ValueError("Unsupported raw VAT action")
    location = row["location"]
    if (
        not isinstance(location, dict)
        or not {"name", "kind"} <= location.keys()
        or set(location) - {"name", "kind", "organization"}
    ):
        raise ValueError("Activity location must name the actual place and its kind")
    _text(location["name"], "location name")
    if _text(location["kind"], "location kind") not in LOCATION_KINDS:
        raise ValueError("Unsupported raw VAT location")
    if "organization" in location:
        _text(location["organization"], "location organization")
    participants = row["participants"]
    if not isinstance(participants, list) or not participants:
        raise ValueError("Activity must identify its actual participants")
    identities = set()
    roles = set()
    for person in participants:
        if not isinstance(person, dict) or set(person) != {"name", "role", "organization"}:
            raise ValueError("Participant must have name, role and organization")
        identity = (
            _text(person["name"], "participant name"),
            _text(person["organization"], "participant organization"),
        )
        if identity in identities:
            raise ValueError("Duplicate or conflicting activity participant")
        identities.add(identity)
        if _text(person["role"], "participant role") not in ROLES:
            raise ValueError("Unsupported raw VAT participant role")
        if person["role"] in {"employee", "proprietor"} and person["organization"] != taxpayer_name:
            raise ValueError("Enterprise participant organization conflicts with the taxpayer")
        if person["role"] == "customer" and person["organization"] == taxpayer_name:
            raise ValueError("A customer cannot simultaneously belong to the taxpayer organization")
        roles.add(person["role"])

    action, place, operation_id = row["action"], location["kind"], row["operation_id"]
    if operation_id is not None:
        _text(operation_id, "activity operation_id")
        if operation_id not in operations:
            raise ValueError("Unknown activity operation reference")
    family_use = operation_id is None and "household_member" in roles
    if place == "home" or family_use:
        if not family_use or roles - {"household_member", "proprietor"}:
            raise ValueError("Ambiguous household and enterprise use")
        if action not in {"delivery", "service", "meal"}:
            raise ValueError("Household vehicle and land use is outside the bounded contract")
        if place == "worksite":
            organization = location.get("organization")
            family_organizations = {
                person["organization"]
                for person in participants
                if person["role"] == "household_member"
            }
            proprietor_organizations = {
                person["organization"] for person in participants if person["role"] == "proprietor"
            }
            if (
                action != "delivery"
                or organization not in family_organizations
                or not proprietor_organizations
                or organization in proprietor_organizations
            ):
                raise ValueError("Family worksite delivery lacks a distinct recipient organization")
        elif place != "home":
            raise ValueError("Personal use location is outside the bounded contract")
        return "private", False
    if "household_member" in roles:
        raise ValueError("Mixed household and enterprise participants are ambiguous")
    if operation_id is None or not roles & {"employee", "proprietor"}:
        raise ValueError("Activity lacks a stated operation and its enterprise participants")
    if action == "meal":
        if place not in {"restaurant", "worksite"}:
            raise ValueError("Meal location is outside the bounded contract")
        if "customer" in roles:
            return "hospitality", True
        if "employee" not in roles:
            raise ValueError("A proprietor-only meal lacks sufficient staff-use evidence")
        return (
            "business" if operations[operation_id]["output_taxable"] else "exempt_business"
        ), True
    if "customer" in roles:
        raise ValueError("Customer-directed gifts and mixed acquisition use are unsupported")
    if action == "ground_work":
        if place != "land_parcel":
            raise ValueError("Ground work must identify the actual land parcel")
        return "land", True
    if action.startswith("vehicle_"):
        if place not in {"worksite", "road"}:
            raise ValueError("Vehicle activity location is outside the bounded contract")
        if not operations[operation_id]["output_taxable"]:
            return "exempt_business", True
        return {
            "vehicle_delivery": "passenger_car_purchase",
            "vehicle_lease": "passenger_car_rental",
            "vehicle_service": "passenger_car_maintenance",
        }[action], True
    if place != "worksite":
        raise ValueError("Ordinary acquisitions must identify the actual worksite use")
    return ("business" if operations[operation_id]["output_taxable"] else "exempt_business"), True


def interpret(source):
    """Derive the engine's purpose fields from linked observable activity facts.

    Every purchase belongs to exactly one raw activity. Its transaction identity,
    evidence document set and supplied date must agree with that activity.
    Sales receive engine placeholders because these two fields have no effect on
    sales calculations. No activity is required or permitted for a sale.
    """
    if not isinstance(source, dict) or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown raw VAT activity evidence contract")
    _no_outcomes(source)
    taxpayer_name = _text(source.get("business_name"), "taxpayer business_name")
    operations = _operations(source)
    activities = source.get("activities")
    if not isinstance(activities, list):
        raise ValueError("Raw VAT activities must be a list")
    indexed = {}
    by_transaction = {}
    derived = {}
    for activity in activities:
        purpose = _activity(activity, operations, taxpayer_name)
        identity, transaction = activity["activity_id"], activity["transaction_id"]
        if identity in indexed or transaction in by_transaction:
            raise ValueError("Duplicate or conflicting activity identity and transaction link")
        indexed[identity] = activity
        by_transaction[transaction] = identity
        derived[identity] = purpose
    rows = source.get("transactions")
    if not isinstance(rows, list):
        raise ValueError("Raw VAT transactions must be a list")
    result = deepcopy(source)
    linked_documents = {identity: set() for identity in indexed}
    for original, row in zip(rows, result["transactions"], strict=True):
        if not isinstance(original, dict):
            raise ValueError("Raw VAT transaction must be an object")
        for field in ("transaction_id", "document_id"):
            _text(original.get(field), field)
        _date(original.get("date"), "transaction date")
        if original.get("direction") == "sale":
            if "activity_id" in original:
                raise ValueError("A sale may not refer to a purchase activity")
            row.update(purpose="business", business_related=True)
            continue
        if original.get("direction") != "purchase":
            raise ValueError("Unsupported raw VAT transaction direction")
        identity = original.get("activity_id")
        if not isinstance(identity, str) or identity not in indexed:
            raise ValueError("Missing or unknown purchase activity link")
        activity = indexed[identity]
        if (
            activity["transaction_id"] != original["transaction_id"]
            or original["document_id"] not in activity["document_ids"]
            or original["date"] != activity["date"]
        ):
            raise ValueError("Conflicting transaction, document or date activity link")
        for field in ("vehicle_subject_excise", "vehicle_direct_business"):
            if type(original.get(field)) is not bool:
                raise ValueError("Official vehicle classification must be a boolean fact")
        if not activity["action"].startswith("vehicle_") and (
            original["vehicle_subject_excise"] or original["vehicle_direct_business"]
        ):
            raise ValueError("Vehicle facts conflict with the documented acquisition activity")
        purpose, related = derived[identity]
        row.update(purpose=purpose, business_related=related)
        linked_documents[identity].add(original["document_id"])
    for identity, activity in indexed.items():
        if linked_documents[identity] != set(activity["document_ids"]):
            raise ValueError("Activity document set does not match the linked purchase evidence")
    return result


def derivation_trace(source, normalized):
    """Record factual joins separately from the unchanged VAT engine's law trace."""
    return {
        "rule_id": RULE_ID,
        "inputs": {
            "source_contract": CONTRACT,
            "operations": source["operations"],
            "activities": source["activities"],
            "purchase_links": [
                {key: row[key] for key in ("transaction_id", "document_id", "date", "activity_id")}
                for row in source["transactions"]
                if row["direction"] == "purchase"
            ],
        },
        "output": [
            {
                key: row[key]
                for key in ("transaction_id", "document_id", "purpose", "business_related")
            }
            for row in normalized["transactions"]
            if row["direction"] == "purchase"
        ],
    }
