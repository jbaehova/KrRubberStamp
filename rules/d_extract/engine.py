from collections import defaultdict
import re
import unicodedata


def normalize_vendor(name: str) -> str:
    name = unicodedata.normalize("NFKC", name).casefold()
    name = name.replace("주식회사", "").replace("(주)", "").replace("㈜", "")
    return re.sub(r"\s+", "", name)


def split_vat(total: int) -> tuple[int, int]:
    supply = total * 10 // 11
    return supply, total - supply


def calculate(scenario: dict) -> tuple[dict, list[dict]]:
    totals = defaultdict(lambda: {"supply": 0, "vat": 0, "total": 0})
    prices = defaultdict(list)
    seen = {}
    trace = []
    for doc in scenario["documents"]:
        key = doc["document_id"]
        if key in seen:
            if seen[key] != doc:
                raise ValueError(f"Conflicting duplicate document: {key}")
            trace.append(
                {"rule_id": "D.deduplicate", "inputs": {"document_id": key}, "output": "skipped"}
            )
            continue
        seen[key] = doc
        vendor = normalize_vendor(doc["vendor"])
        supply_sum = vat_sum = total_sum = 0
        for item in doc["items"]:
            amount = item["quantity"] * item["unit_price"]
            if doc["price_includes_vat"]:
                supply, vat = split_vat(amount)
                net_unit = item["unit_price"] * 10 // 11
            else:
                supply, vat = amount, amount // 10
                net_unit = item["unit_price"]
            total = supply + vat
            supply_sum += supply
            vat_sum += vat
            total_sum += total
            item_key = re.sub(r"\s+", "", unicodedata.normalize("NFKC", item["name"])).casefold()
            prices[item_key].append((net_unit, vendor))
            trace.append(
                {
                    "rule_id": "D.vat_split",
                    "inputs": {
                        "document_id": key,
                        "quantity": item["quantity"],
                        "unit_price": item["unit_price"],
                        "includes_vat": doc["price_includes_vat"],
                    },
                    "output": {"supply": supply, "vat": vat, "total": total},
                }
            )
        for field, value in (("supply", supply_sum), ("vat", vat_sum), ("total", total_sum)):
            totals[vendor][field] += value
        trace.append(
            {"rule_id": "D.vendor_normalize", "inputs": {"vendor": doc["vendor"]}, "output": vendor}
        )
    vendors = [{"vendor": vendor, **amounts} for vendor, amounts in sorted(totals.items())]
    cheapest = [
        {"item": item, "unit_price": min(values)[0], "vendor": min(values)[1]}
        for item, values in sorted(prices.items())
    ]
    gold = {
        "vendor_totals": vendors,
        "cheapest_by_item": cheapest,
        "supply_total": sum(v["supply"] for v in vendors),
        "vat_total": sum(v["vat"] for v in vendors),
        "grand_total": sum(v["total"] for v in vendors),
        "unique_document_count": len(seen),
    }
    trace.append(
        {"rule_id": "D.aggregate", "inputs": {"unique_documents": len(seen)}, "output": gold}
    )
    return gold, trace
