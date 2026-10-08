"""Deterministic domestic retail VAT facts for 2026 first-half."""

from copy import deepcopy
from datetime import date, timedelta
import hashlib
import random

LABELS = {
    "domain": "분야",
    "reference_period": "기준 기간",
    "synthetic_id": "가상 자료 묶음 번호",
    "difficulty": "난이도",
    "period_start": "과세기간 시작일",
    "period_end": "과세기간 종료일",
    "taxpayer_type": "부가가치세 과세유형",
    "business_type": "사업자 형태",
    "consumer_facing_business": "소매업으로 소비자 상대 사업에 해당",
    "prior_year_site_supply_base": "2025년 사업장별 공급가액 합계",
    "receipt_credit_previously_claimed": "2026년 이미 공제받은 발행세액공제",
    "prepaid_assessed_vat": "2026년 제1기 예정고지 납부세액",
    "business_name": "상호",
    "transactions": "거래 증빙",
    "transaction_id": "실제 거래 고유번호",
    "document_id": "증빙 문서번호",
    "direction": "매출 또는 매입",
    "date": "공급일",
    "amount": "증빙 금액",
    "includes_vat": "증빙 금액에 부가세 포함",
    "taxable": "10% 부가세 과세 거래",
    "evidence": "증빙 종류",
    "description": "거래 내용",
    "invoice_issued": "동일 거래 세금계산서 발급 여부",
    "counterparty_consumer": "매출 상대방은 소비자",
    "purpose": "사용 목적",
    "business_related": "사업과 직접 관련",
    "supplier_general": "공급자는 일반과세자",
    "vat_separately_stated": "세액 별도 표시",
    "vehicle_subject_excise": "개별소비세 과세대상 승용자동차",
    "vehicle_direct_business": "운수업 또는 자동차판매업 등의 직접 영업용 자동차",
    "exceptions": "확인할 예외사항",
    "scope_note": "추가 신고 항목 안내",
    "source_contract": "자료 연결 규약 번호",
    "operations": "실제 사업 운영 기록",
    "operation_id": "사업 활동 번호",
    "output_taxable": "해당 사업 매출의 과세 여부",
    "activities": "실제 수령과 사용 활동 기록",
    "activity_id": "수령 및 사용 활동 번호",
    "document_ids": "연결 증빙 번호",
    "action": "실제 활동 종류",
    "location": "수령 또는 사용 장소",
    "kind": "장소 종류",
    "organization": "소속 또는 장소 운영자",
    "participants": "실제 참석 및 수령인",
    "role": "해당 활동에서의 역할",
}

INSTRUCTIONS = [
    "상반기 부가세 자료 보냈어요. 거래별로 확인하고 매출세액부터 최종 납부액까지 answer.json으로 정리해 주세요.",
    "2026년 제1기 확정신고 준비 중이에요. 첨부 증빙으로 계산해서 공제 가능 매입세액과 차감 납부세액을 알려주세요.",
    "이번 부가세 마감 계산 부탁해요. 포함 금액인지 확인하고 발행세액공제와 예정고지도 반영해 주세요.",
    "상반기 매출과 매입 자료 모아뒀어요. 신고용 합계를 구해서 지정된 답안 형식으로 저장해 주세요.",
    "제1기 부가세 정산 한번 봐주세요. 불공제 항목을 구분하고 납부 또는 환급 금액까지 계산해 주시면 돼요.",
    "부가세 신고 전에 숫자를 맞추려고 해요. 증빙 기준으로 세액과 공제 내역을 정리해 주세요.",
    "상반기 세무 자료 첨부했어요. 필요한 항목을 빠짐없이 계산해서 answer.json에 담아주세요.",
    "이번 확정신고 초안용 계산 부탁드립니다. 매출세액과 매입세액을 구분해서 차감 세액까지 확인해 주세요.",
    "2026년 1월부터 6월까지 자료예요. 일반과세자 기준으로 부가세 답안을 만들어주세요.",
    "신고 자료 집계가 필요해요. 공급가액과 세액을 분리한 뒤 최종 납부세액을 구해 주세요.",
    "이번 부가세 얼마인지 확인 부탁해요. 매입 불공제와 영수증 발행 공제도 함께 검토해 주세요.",
    "상반기 증빙 정리해서 드려요. 거래 단위로 집계하고 정해진 항목의 값을 제출해 주세요.",
    "제1기 확정신고 계산 맡아주세요. 예정고지 납부분을 차감해서 실제 납부하거나 환급받을 금액을 알려주세요.",
    "부가세 마감 전에 검산이 필요해요. 자료에 나온 사실을 기준으로 신고 항목별 금액을 계산해 주세요.",
    "매출 자료와 매입 증빙을 같이 보냅니다. 세액공제까지 반영한 부가세 정산 결과를 저장해 주세요.",
    "이번 상반기 부가세 계산 부탁드려요. 같은 거래는 한 번씩 집계하고 원 단위로 답안을 적어주세요.",
    "1기 신고 준비 자료예요. 첨부 내용을 확인해서 과세표준과 공제 가능한 세액을 계산해 주세요.",
    "부가세 정산표를 만들고 있어요. 증빙별 금액을 확인한 뒤 납부액 또는 환급액을 답안으로 제출해 주세요.",
]


def generate(seed: int, difficulty: str) -> dict:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("difficulty must be easy, medium or hard")
    rng = random.Random(seed)
    tag = hashlib.sha256(str(seed).encode()).hexdigest()[:16]
    count = {"easy": 5, "medium": 9, "hard": 15}[difficulty]
    scenario = {
        "domain": "C_vat",
        "reference_period": "2026년 제1기 (일반과세자)",
        "synthetic_id": f"가상VAT-{tag}",
        "difficulty": difficulty,
        "taxpayer_type": "general",
        "period_start": "2026-01-01",
        "period_end": "2026-06-30",
        "business_name": f"가상별빛상점{tag}",
        "business_type": "individual",
        "consumer_facing_business": True,
        "prior_year_site_supply_base": rng.randrange(100, 850) * 1_000_000,
        "receipt_credit_previously_claimed": 0,
        "prepaid_assessed_vat": 0,
        "scope_note": "소매업의 국내 10% 과세 거래만 있습니다. 세금계산서는 종이 발급입니다. 전자신고세액공제, 가산세, 그 밖의 공제는 적용하지 않습니다. 모든 증빙은 적법하게 보관하고 수령명세서를 제출합니다.",
        "transactions": [],
        "exceptions": [],
    }
    for index in range(count):
        sale = index < (count + 1) // 2
        base = rng.randrange(20, 400) * 100_000 if sale else rng.randrange(8, 160) * 100_000
        includes = rng.choice([True, False])
        evidence = (
            "card_receipt"
            if index == 0
            else rng.choice(["tax_invoice", "card_receipt", "cash_receipt"])
        )
        scenario["transactions"].append(
            {
                "transaction_id": f"V{tag}-{index:03d}",
                "document_id": f"DOC-{index:03d}",
                "direction": "sale" if sale else "purchase",
                "date": (date(2026, 1, 1) + timedelta(days=rng.randrange(181))).isoformat(),
                "description": "생활용품 판매"
                if sale
                else rng.choice(["판매용 상품 매입", "매장 소모품 구입", "매장 광고 제작"]),
                "amount": base * 11 // 10 if includes else base,
                "includes_vat": includes,
                "taxable": True,
                "evidence": evidence,
                "invoice_issued": evidence == "tax_invoice",
                "counterparty_consumer": evidence != "tax_invoice" if sale else False,
                "purpose": "business",
                "business_related": True,
                "supplier_general": True,
                "vat_separately_stated": True,
                "vehicle_subject_excise": False,
                "vehicle_direct_business": False,
            }
        )
    purchases = [r for r in scenario["transactions"] if r["direction"] == "purchase"]
    if difficulty != "easy":
        kind = rng.choice(["hospitality", "passenger_car_maintenance", "private"])
        row = purchases[0]
        row["purpose"] = kind
        row["description"] = {
            "hospitality": "거래처 접대 식사",
            "passenger_car_maintenance": "소매업 대표의 5인승 2000cc 승용차 정비",
            "private": "대표 개인 가사용품 구입",
        }[kind]
        row["business_related"] = kind != "private"
        row["vehicle_subject_excise"] = kind == "passenger_car_maintenance"
        scenario["exceptions"].append(kind)
    if difficulty == "hard":
        duplicate = deepcopy(rng.choice(scenario["transactions"]))
        duplicate["document_id"] += "-COPY"
        scenario["transactions"].append(duplicate)
        scenario["exceptions"].append("duplicate_document")
        extra = seed % 5
        if extra == 0:
            scenario["business_type"] = "corporation"
            scenario["exceptions"].append("corporation_receipt_credit_exclusion")
        elif extra == 1:
            scenario["prior_year_site_supply_base"] = rng.randrange(1001, 1400) * 1_000_000
            scenario["exceptions"].append("prior_year_sales_over_one_billion")
        elif extra == 2:
            scenario["prepaid_assessed_vat"] = rng.randrange(50, 151) * 10_000
            scenario["exceptions"].append("prepaid_assessment")
        elif extra == 3:
            row = next(
                r
                for r in scenario["transactions"]
                if r["direction"] == "sale" and r["evidence"] != "tax_invoice"
            )
            row["invoice_issued"] = True
            row["counterparty_consumer"] = False
            for other in scenario["transactions"]:
                if other["transaction_id"] == row["transaction_id"]:
                    other.update(invoice_issued=True, counterparty_consumer=False)
            scenario["exceptions"].append("invoice_and_receipt_same_transaction")
        else:
            sales_base = sum(
                r["amount"] * 10 // 11 if r["includes_vat"] else r["amount"]
                for r in scenario["transactions"]
                if r["direction"] == "sale"
            )
            row = purchases[-1]
            row["amount"] = (
                (sales_base + 60_000_000) * 11 // 10
                if row["includes_vat"]
                else sales_base + 60_000_000
            )
            row["description"] = "매장 판매용 재고 대량 매입"
            for other in scenario["transactions"]:
                if other["transaction_id"] == row["transaction_id"]:
                    other.update(amount=row["amount"], description=row["description"])
            scenario["exceptions"].append("input_vat_refund")
    return scenario
