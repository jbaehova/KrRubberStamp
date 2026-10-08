"""Bounded receipt and register evidence before the 2025 arithmetic engine.

Only supplied factual branches are reconciled. This does not infer arbitrary
legal eligibility from prose or certify all mortgage acquisition conditions.
"""

from copy import deepcopy
from datetime import date
import unicodedata

CONTRACT = "yearend_evidence_v1"
RULE_ID = "A_EVIDENCE_RECONCILIATION"


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Year-end evidence requires nonempty {field}")
    return value


def _date(value, field):
    _text(value, field)
    if date.fromisoformat(value).isoformat() != value:
        raise ValueError(f"Year-end evidence requires ISO {field}")
    return value


def _address(value):
    return "".join(unicodedata.normalize("NFKC", _text(value, "address")).split())


def _receipts(source, normalized, group, field, mapping):
    for original, row in zip(source.get(group, []), normalized.get(group, []), strict=True):
        if field not in original:
            continue
        if "excluded" in original or "exclusion_reason" in original:
            raise ValueError(f"Raw {group} receipt exposes a compiled exclusion")
        value = _text(original[field], field)
        if value not in mapping:
            raise ValueError(f"Unsupported raw {group} {field}")
        row["excluded"] = mapping[value]


def _household_homes(homes, source):
    if not isinstance(homes, list):
        raise ValueError("Year-end household homes must be a list")
    identities = set()
    for home in homes:
        if not isinstance(home, dict) or set(home) != {"home_id", "address", "owner_person_id"}:
            raise ValueError("Household home requires identity, address and household owner")
        identity = _text(home["home_id"], "home_id")
        _text(home["address"], "home address")
        owner = _text(home["owner_person_id"], "home owner")
        if owner not in {"self", *(p["person_id"] for p in source.get("dependents", []))}:
            raise ValueError("Home owner is outside the attested household")
        if identity in identities:
            raise ValueError("Duplicate household home identity")
        identities.add(identity)
    return len(identities)


def interpret(source: dict) -> dict:
    if source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown year-end evidence contract")
    normalized = deepcopy(source)
    normalized.pop("source_contract")
    branches = 0
    rent = source.get("rent", {})
    address_fields = {"contract_address", "resident_registration_address"}
    if address_fields & rent.keys():
        if not address_fields <= rent.keys() or "address_matches" in rent:
            raise ValueError("Raw rent needs both addresses without a compiled match")
        normalized["rent"]["address_matches"] = _address(rent["contract_address"]) == _address(
            rent["resident_registration_address"]
        )
        branches += 1
    if "household_homes_at_year_end" in rent:
        if "homeless_household" in rent:
            raise ValueError("Raw rent exposes a compiled household housing status")
        normalized["rent"]["homeless_household"] = (
            _household_homes(rent["household_homes_at_year_end"], source) == 0
        )
        branches += 1

    for group, field, mapping in (
        ("medical", "treatment_purpose", {"therapeutic": False, "cosmetic": True}),
        (
            "cards",
            "billed_item",
            {"ordinary_goods_services": False, "apartment_management_fee": True},
        ),
    ):
        _receipts(source, normalized, group, field, mapping)
        branches += sum(field in row for row in source.get(group, []))

    education_levels = {
        "primary_secondary_school": "school",
        "university": "university",
        "graduate_school": "graduate",
        "kindergarten_or_childcare": "preschool",
        "qualified_special_education": "special_disabled",
        "private_academy": "school",
    }
    for original, row in zip(
        source.get("education", []), normalized.get("education", []), strict=True
    ):
        if "institution_type" not in original:
            continue
        if "excluded" in original or "exclusion_reason" in original:
            raise ValueError("Raw education receipt exposes a compiled exclusion")
        institution = _text(original["institution_type"], "institution_type")
        if (
            institution not in education_levels
            or original["level"] != education_levels[institution]
        ):
            raise ValueError("Unsupported or conflicting institution and attendance level")
        # This branch covers school-age academy fees only, not preschool academy
        # attendance requirements or supplementary school expense sublimits.
        row["excluded"] = institution == "private_academy"
        branches += 1

    mortgage = source.get("housing_mortgage", {})
    if "interest_payments" in mortgage:
        if "interest_paid" in mortgage:
            raise ValueError("Raw mortgage payments expose compiled employment-period interest")
        payments = mortgage["interest_payments"]
        if not isinstance(payments, list):
            raise ValueError("Mortgage interest payments must be a list")
        start = _date(source["employment_start"], "employment start")
        end = _date(source["employment_end"], "employment end")
        if start > end:
            raise ValueError("Employment interval is reversed")
        eligible_interest = 0
        identities = set()
        for payment in payments:
            if not isinstance(payment, dict) or not {"date", "amount"} <= payment.keys():
                raise ValueError("Mortgage payment requires its actual date and amount")
            paid = _date(payment["date"], "mortgage payment date")
            amount = payment["amount"]
            if type(amount) is not int or amount < 0:
                raise ValueError("Mortgage interest amount must be a nonnegative integer")
            if "payment_id" in payment:
                identity = _text(payment["payment_id"], "mortgage payment identity")
                if identity in identities:
                    raise ValueError("Duplicate mortgage interest payment identity")
                identities.add(identity)
            if start <= paid <= end:
                eligible_interest += amount
        normalized["housing_mortgage"]["interest_paid"] = eligible_interest
        branches += 1
    homes_field = "household_homes_at_year_end"
    if homes_field in mortgage:
        if "requirements_met" in mortgage:
            raise ValueError("Raw household home list exposes compiled mortgage eligibility")
        if mortgage.get("other_common_requirements_attested") is not True:
            raise ValueError("Other mortgage conditions need a separate attestation")
        normalized["housing_mortgage"]["requirements_met"] = (
            _household_homes(mortgage[homes_field], source) <= 1
        )
        branches += 1

    if "organization_designations" in source:
        designations = source["organization_designations"]
        if not isinstance(designations, list) or not designations:
            raise ValueError("Organization designations must be a nonempty register")
        groups = {}
        for designation in designations:
            if not isinstance(designation, dict) or set(designation) != {
                "organization_id",
                "kind",
                "valid_from",
                "valid_to",
            }:
                raise ValueError("Organization designation has unknown or missing fields")
            identity = _text(designation["organization_id"], "organization_id")
            if designation["kind"] not in {"statutory", "public", "religious"}:
                raise ValueError("Unsupported organization designation kind")
            start = _date(designation["valid_from"], "designation start")
            end = _date(designation["valid_to"], "designation end")
            if start > end:
                raise ValueError("Organization designation interval is reversed")
            intervals = groups.setdefault(identity, [])
            if any(start <= old["valid_to"] and end >= old["valid_from"] for old in intervals):
                raise ValueError("Overlapping organization designations")
            intervals.append(designation)
        for original, row in zip(
            source.get("donations", []), normalized.get("donations", []), strict=True
        ):
            if "eligible_organization" in original:
                raise ValueError("Raw donation exposes compiled organization eligibility")
            identity = _text(original.get("organization_id"), "donation organization_id")
            if identity not in groups:
                raise ValueError("Unknown donation organization reference")
            paid_date = _date(original.get("date"), "donation date")
            active = [d for d in groups[identity] if d["valid_from"] <= paid_date <= d["valid_to"]]
            if active and original["kind"] != active[0]["kind"]:
                raise ValueError("Donation kind conflicts with its active designation")
            row["eligible_organization"] = bool(active)
            branches += 1
    if not branches:
        raise ValueError("Year-end contract requires at least one raw evidence branch")
    return normalized


def derivation_trace(source: dict, normalized: dict) -> dict:
    outcomes = {}
    if "contract_address" in source.get("rent", {}):
        outcomes["rent.address_matches"] = normalized["rent"]["address_matches"]
    if "household_homes_at_year_end" in source.get("rent", {}):
        outcomes["rent.homeless_household"] = normalized["rent"]["homeless_household"]
    for group, field in (
        ("medical", "treatment_purpose"),
        ("cards", "billed_item"),
        ("education", "institution_type"),
    ):
        for index, row in enumerate(source.get(group, [])):
            if field in row:
                outcomes[f"{group}.{index}.excluded"] = normalized[group][index]["excluded"]
    if "household_homes_at_year_end" in source.get("housing_mortgage", {}):
        outcomes["housing_mortgage.requirements_met"] = normalized["housing_mortgage"][
            "requirements_met"
        ]
    if "interest_payments" in source.get("housing_mortgage", {}):
        outcomes["housing_mortgage.interest_paid"] = normalized["housing_mortgage"]["interest_paid"]
    if "organization_designations" in source:
        for index, row in enumerate(normalized.get("donations", [])):
            outcomes[f"donations.{index}.eligible_organization"] = row["eligible_organization"]
    return {"rule_id": RULE_ID, "inputs": source, "output": outcomes}
