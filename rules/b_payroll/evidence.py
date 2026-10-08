"""Interpret authored clock records without printing their computed totals."""

from copy import deepcopy
from datetime import datetime, timedelta

CONTRACT = "payroll_evidence_v1"
DERIVED = {
    "regular_minutes",
    "qualifying_weeks",
    "overtime_minutes",
    "night_minutes",
    "holiday_shifts",
    "payment_date",
    "employer_provides_meals",
}


def _integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f"Invalid raw evidence {name}")
    return value


def _clock(value):
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def _segments(record):
    start, end = _clock(record["start"]), _clock(record["end"])
    if not start < end <= start + timedelta(days=1):
        raise ValueError("Work interval must be positive and no longer than 24 hours")
    breaks = sorted((_clock(row["start"]), _clock(row["end"])) for row in record["breaks"])
    segments, cursor = [], start
    for low, high in breaks:
        if not cursor <= low < high <= end:
            raise ValueError("Breaks overlap or fall outside the work interval")
        if cursor < low:
            segments.append((cursor, low))
        cursor = high
    if cursor < end:
        segments.append((cursor, end))
    return segments


def _minutes(segments):
    return sum(int((end - start).total_seconds()) // 60 for start, end in segments)


def _night(segments):
    result = 0
    for start, end in segments:
        day = start.date() - timedelta(days=1)
        while day <= end.date():
            low = datetime.combine(day, datetime.min.time()) + timedelta(hours=22)
            high = low + timedelta(hours=8)
            a, b = max(start, low), min(end, high)
            if a < b:
                result += int((b - a).total_seconds()) // 60
            day += timedelta(days=1)
    return result


def _approved_records(records):
    versions = {}
    for record in records:
        if record["status"] not in {"approved", "superseded", "draft"}:
            raise ValueError("Unknown work record approval status")
        revision = _integer(record["revision"], "revision")
        identity = record["record_id"]
        if not isinstance(identity, str) or not identity or revision == 0:
            raise ValueError("Work record identity and positive revision are required")
        if record["status"] != "approved":
            continue
        prior = versions.get(identity)
        if prior and prior["revision"] == revision and prior != record:
            raise ValueError("Conflicting approved work record revision")
        if prior is None or revision > prior["revision"]:
            versions[identity] = record
    return [versions[key] for key in sorted(versions)]


def interpret(source):
    """Return the engine contract derived solely from declared raw evidence."""
    if source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown raw payroll evidence contract")
    if DERIVED & source.keys():
        raise ValueError("Raw payroll source exposes precomputed derived fields")
    result = deepcopy(source)
    regular = overtime = night = 0
    holidays = {}
    schedule = source.get("regular_schedule")
    if schedule is not None:
        days = _integer(schedule["working_days"], "working_days")
        daily = _integer(schedule["minutes_per_day"], "minutes_per_day")
        seen = set()
        absence_minutes = 0
        for absence in schedule["unpaid_absences"]:
            identity = absence["record_id"]
            if identity in seen:
                raise ValueError("Duplicate unpaid absence source record")
            seen.add(identity)
            datetime.strptime(absence["date"], "%Y-%m-%d")
            absence_minutes += _integer(absence["minutes"], "absence minutes")
        regular = days * daily - absence_minutes
        if regular < 0:
            raise ValueError("Absences exceed scheduled work")
    holiday_dates = set(source["holiday_dates"])
    for value in holiday_dates:
        datetime.strptime(value, "%Y-%m-%d")
    approved = _approved_records(source["work_records"])
    occupied = []
    for record in approved:
        pieces = _segments(record)
        for low, high in pieces:
            if any(low < prior_high and prior_low < high for prior_low, prior_high in occupied):
                raise ValueError("Different approved work records overlap")
            occupied.append((low, high))
        minutes, night_minutes = _minutes(pieces), _night(pieces)
        work_date = _clock(record["start"]).date().isoformat()
        if record["category"] == "regular":
            if schedule is not None:
                raise ValueError(
                    "Regular schedule and individual regular records would double count"
                )
            regular += minutes
        elif record["category"] == "additional":
            if work_date in holiday_dates:
                day = holidays.setdefault(work_date, {"minutes": 0, "holiday_night_minutes": 0})
                day["minutes"] += minutes
                day["holiday_night_minutes"] += night_minutes
            else:
                overtime += minutes
        else:
            raise ValueError("Unknown raw work category")
        night += night_minutes
    qualifying = 0
    weeks = set()
    for row in source["week_attendance"]:
        if row["week_id"] in weeks:
            raise ValueError("Duplicate weekly attendance source record")
        weeks.add(row["week_id"])
        scheduled = _integer(row["scheduled_days"], "scheduled_days")
        attended = _integer(row["attended_days"], "attended_days")
        if attended > scheduled or scheduled > 7:
            raise ValueError("Invalid weekly attendance counts")
        qualifying += int(scheduled > 0 and attended == scheduled)
    payments = source["payment_records"]
    for row in payments:
        if row["status"] not in {"executed", "approved", "cancelled"}:
            raise ValueError("Unknown payment record status")
        _integer(row["revision"], "payment revision")
        datetime.strptime(row["date"], "%Y-%m-%d")
    executed = [row for row in payments if row["status"] == "executed"]
    candidates = executed or [row for row in payments if row["status"] == "approved"]
    if not candidates:
        raise ValueError("No executed or approved payment date")
    latest_revision = max(row["revision"] for row in candidates)
    latest = [row for row in candidates if row["revision"] == latest_revision]
    if len({row["date"] for row in latest}) != 1:
        raise ValueError("Conflicting authoritative payment dates")
    service = source["meal_service"]
    if service not in {"none", "employer_catering"}:
        raise ValueError("Unknown factual meal service")
    result.update(
        {
            "regular_minutes": regular,
            "qualifying_weeks": qualifying,
            "overtime_minutes": overtime,
            "night_minutes": night,
            "holiday_shifts": [holidays[day] for day in sorted(holidays)],
            "payment_date": latest[0]["date"],
            "employer_provides_meals": service == "employer_catering",
        }
    )
    return result


def derivation_trace(source, normalized):
    return {
        "rule_id": "B.EVIDENCE_RECONCILIATION",
        "inputs": {
            "source_contract": CONTRACT,
            "regular_schedule": source.get("regular_schedule"),
            "work_records": source["work_records"],
            "holiday_dates": source["holiday_dates"],
            "week_attendance": source["week_attendance"],
            "payment_records": source["payment_records"],
            "meal_service": source["meal_service"],
        },
        "output": {key: normalized[key] for key in sorted(DERIVED)},
    }
