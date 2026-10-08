"""Optional ID-based registers for authored VAT documentary decisions."""

from datetime import date


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"VAT register requires nonempty {name}")
    return value


def _money(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f"VAT register requires nonnegative integer {name}")
    return value


def _date(value):
    _text(value, "date")
    if date.fromisoformat(value).isoformat() != value:
        raise ValueError("VAT register requires ISO calendar date")
    return value


def vehicle_registry(source, operations):
    if "vehicle_registry" not in source:
        return None
    rows = source["vehicle_registry"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Vehicle registry must be a nonempty list")
    result = {}
    for row in rows:
        required = {
            "vehicle_id",
            "registration_class",
            "business_license",
            "permitted_operation_id",
        }
        if (
            not isinstance(row, dict)
            or not required <= row.keys()
            or set(row) - required - {"valid_from", "valid_to"}
        ):
            raise ValueError("Vehicle registry has unknown or missing fields")
        identity = _text(row["vehicle_id"], "vehicle_id")
        if row["registration_class"] not in {"excise_passenger", "non_excise_vehicle"}:
            raise ValueError("Unsupported official vehicle classification")
        if row["business_license"] not in {
            "none",
            "taxi_transport",
            "vehicle_rental",
            "vehicle_sales",
        }:
            raise ValueError("Unsupported vehicle business license")
        operation = row["permitted_operation_id"]
        if row["business_license"] == "none":
            if operation is not None:
                raise ValueError("Unlicensed vehicle has a permitted operation")
        elif operation not in operations:
            raise ValueError("Vehicle license refers to unknown permitted operation")
        if ("valid_from" in row) != ("valid_to" in row):
            raise ValueError("Vehicle status needs both validity dates")
        start = _date(row["valid_from"]) if "valid_from" in row else "0001-01-01"
        end = _date(row["valid_to"]) if "valid_to" in row else "9999-12-31"
        if start > end:
            raise ValueError("Vehicle status interval is reversed")
        intervals = result.setdefault(identity, [])
        if any(start <= old[1] and end >= old[0] for old in intervals):
            raise ValueError("Overlapping vehicle status intervals")
        intervals.append((start, end, row))
    return result


def vehicle_flags(original, activity, register):
    identity = _text(original.get("vehicle_id"), "transaction vehicle_id")
    if activity.get("vehicle_id") != identity or identity not in register:
        raise ValueError("Unknown or conflicting vehicle identity link")
    if {"vehicle_subject_excise", "vehicle_direct_business"} & original.keys():
        raise ValueError("Registered vehicle transaction exposes preselected classifications")
    records = [
        record for start, end, record in register[identity] if start <= original["date"] <= end
    ]
    if len(records) != 1:
        raise ValueError("Vehicle status does not cover purchase date")
    record = records[0]
    return {
        "vehicle_subject_excise": record["registration_class"] == "excise_passenger",
        "vehicle_direct_business": record["business_license"] != "none"
        and record["permitted_operation_id"] == activity["operation_id"],
    }


def supplier_registry(source):
    if "supplier_status_records" not in source:
        return None
    rows = source["supplier_status_records"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Supplier status register must be a nonempty list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "supplier_id",
            "status",
            "valid_from",
            "valid_to",
        }:
            raise ValueError("Supplier status has unknown or missing fields")
        identity = _text(row["supplier_id"], "supplier_id")
        if row["status"] not in {"general", "simplified_no_invoice_duty"}:
            raise ValueError("Unsupported supplier tax status")
        start, end = _date(row["valid_from"]), _date(row["valid_to"])
        if start > end:
            raise ValueError("Supplier status interval is reversed")
        intervals = result.setdefault(identity, [])
        if any(start <= old["valid_to"] and end >= old["valid_from"] for old in intervals):
            raise ValueError("Overlapping supplier status intervals")
        intervals.append(row)
    return result


def supplier_general(original, register):
    if "supplier_general" in original:
        raise ValueError("Registered supplier transaction exposes preselected status")
    identity = _text(original.get("supplier_id"), "transaction supplier_id")
    if identity not in register:
        raise ValueError("Unknown supplier identity link")
    selected = [
        r for r in register[identity] if r["valid_from"] <= original["date"] <= r["valid_to"]
    ]
    if len(selected) != 1:
        raise ValueError("Supplier status does not cover purchase date")
    return selected[0]["status"] == "general"


def prior_year_site_supply(source):
    if "site_year_records" not in source:
        if "filing_site_id" in source:
            raise ValueError("Filing site requires site-year records")
        return None
    if {"prior_year_site_supply_base", "other_site_supply_base"} & source.keys():
        raise ValueError("Site records expose a preselected prior-year amount")
    identity = _text(source.get("filing_site_id"), "filing_site_id")
    rows = source["site_year_records"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Site-year records must be a nonempty list")
    seen, selected = set(), []
    year = date.fromisoformat(source["period_start"]).year - 1
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"site_id", "site_name", "year", "supply_base"}:
            raise ValueError("Site-year record has unknown or missing fields")
        _text(row["site_id"], "site_id")
        _text(row["site_name"], "site_name")
        if type(row["year"]) is not int or row["year"] < 2000:
            raise ValueError("Invalid site record year")
        _money(row["supply_base"], "site supply_base")
        key = row["site_id"], row["year"]
        if key in seen:
            raise ValueError("Duplicate site-year record")
        seen.add(key)
        if key == (identity, year):
            selected.append(row)
    if len(selected) != 1 or selected[0]["site_name"] != source["business_name"]:
        raise ValueError("Unknown or conflicting filing site and prior-year record")
    return selected[0]["supply_base"]
