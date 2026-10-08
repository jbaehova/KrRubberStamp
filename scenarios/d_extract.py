from copy import deepcopy
import hashlib
import random

LABELS = {
    "documents": "거래 자료",
    "document_id": "문서 번호",
    "vendor": "업체명",
    "business_number": "사업자등록번호",
    "date": "작성일",
    "price_includes_vat": "단가 부가세 포함 여부",
    "items": "품목 내역",
    "name": "품목명",
    "quantity": "수량",
    "unit_price": "단가",
    "exceptions": "확인할 사항",
    "synthetic_notice": "자료 성격",
    "comparison_basis": "비교 기준",
    "source_contract": "자료 연결 규약 번호",
    "processing_policy": "인수 집계와 문서 연결 기준",
    "headers": "원본 문서 표지",
    "record_id": "표지 기록 번호",
    "kind": "문서 종류",
    "line_sheets": "품목 부속표",
    "sheet_id": "부속표 번호",
    "header_record_id": "연결할 표지 기록 번호",
    "events": "실제 인수와 취소 기록",
    "event_id": "현장 접수 기록 번호",
    "event": "실제 접수 상태",
    "location": "인수 또는 접수 장소",
    "closing_date": "인수 대장 마감일",
}
INSTRUCTIONS = [
    "자료에 있는 업체별 공급가액과 부가세, 총액을 모아 주세요. 품목별 최저 단가 업체도 비교해서 answer.json으로 보내 주세요.",
    "견적 자료와 거래 내역 정리가 필요해요. 업체별 합계와 품목별 최저 단가를 정해진 형식으로 정리해 줄래요?",
    "첨부된 서류를 확인해서 업체별 금액을 합산해 주세요. 부가세를 나누고 품목별 단가도 비교해 주세요.",
    "구매 검토용 집계가 필요해요. 업체별 합계와 같은 품목의 최저 단가를 answer.json에 적어 주세요.",
    "이 자료 묶음에서 업체별 공급가액, 세액, 총액을 정리해 주세요. 품목별로 가장 저렴한 업체도 표시해 주세요.",
    "거래 자료 정리 좀 부탁해요. 업체별 금액 합계와 품목별 최저 단가 비교 결과를 지정한 형식으로 주시면 돼요.",
    "첨부 서류를 집계해서 업체별 금액과 품목별 단가 비교표를 만들어 주세요. JSON 답안이 필요해요.",
    "자료 검토 후 업체별 합계와 부가세를 계산해 주세요. 품목별로 단가가 가장 낮은 업체도 골라 주세요.",
    "업체별 거래 금액을 모아야 해요. 세액과 총액을 분리하고 품목별 최저 단가도 함께 정리해 주세요.",
    "이 서류들을 기준으로 구매 금액 집계해 주세요. 업체별 합계와 품목별 단가 비교 결과를 부탁해요.",
    "발주 검토를 위해 첨부 자료를 집계해 주세요. 업체별 금액과 품목별 최저 단가를 답안에 담아 주세요.",
    "자료를 대조해서 업체별 공급가액, 세액, 총액을 정리해 주세요. 같은 품목의 최저 단가도 확인해 주세요.",
    "거래 내역 집계를 부탁드려요. 업체별 합계와 품목별 최저 단가 업체를 JSON으로 정리해 주세요.",
    "첨부 자료에서 업체별 금액을 합쳐 주세요. 품목 단가를 비교한 결과도 지정 형식으로 넣어 주세요.",
    "이 자료로 구매 집계표가 필요해요. 업체별 합계와 세액을 정리하고 품목별 최저 단가를 찾아 주세요.",
]


def invalid_business_number(rng):
    digits = [rng.randrange(10) for _ in range(9)]
    weights = [1, 3, 7, 1, 3, 7, 1, 3, 5]
    checksum = (10 - (sum(a * b for a, b in zip(digits, weights)) + digits[8] * 5 // 10) % 10) % 10
    digits.append((checksum + 1) % 10)
    text = "".join(map(str, digits))
    return f"{text[:3]}-{text[3:5]}-{text[5:]}"


def generate(seed: int, difficulty: str) -> dict:
    rng = random.Random(seed)
    n = {"easy": 2, "medium": 5, "hard": 8}[difficulty]
    vendor_count = {"easy": 2, "medium": 3, "hard": 4}[difficulty]
    tag = hashlib.sha256(str(seed).encode()).hexdigest()[:12]
    vendors = [f"가상종이상사{tag}{i}" for i in range(vendor_count)]
    business_ids = [invalid_business_number(rng) for _ in vendors]
    catalog = ["복사용지", "문서보관함", "사무용펜", "파일철", "포장봉투"]
    docs = []
    for i in range(n):
        vendor_idx = i % vendor_count
        name = vendors[vendor_idx]
        if difficulty == "hard" and i >= vendor_count:
            name = f"주식회사 {name}" if i % 2 else f"(주) {name} "
        includes_vat = difficulty != "easy" and i % 2 == 1
        items = []
        for item in rng.sample(catalog, rng.randint(2, 4)):
            net_unit = rng.randint(12, 450) * 100
            items.append(
                {
                    "name": item,
                    "quantity": rng.randint(1, 30),
                    "unit_price": net_unit * 11 // 10 if includes_vat else net_unit,
                }
            )
        docs.append(
            {
                "document_id": f"SYN-{tag}-{i:02d}",
                "vendor": name,
                "business_number": business_ids[vendor_idx],
                "date": f"2026-04-{i + 1:02d}",
                "price_includes_vat": includes_vat,
                "items": items,
            }
        )
    exceptions = []
    if difficulty != "easy":
        exceptions.append("단가의 부가세 포함 여부가 문서마다 다름")
    if difficulty == "hard":
        docs.append(deepcopy(docs[0]))
        exceptions.extend(
            [
                "같은 문서 번호의 자료가 중복되므로 한 번만 합산",
                "주식회사와 (주) 표기는 동일 업체로 통합",
            ]
        )
    return {
        "documents": docs,
        "exceptions": exceptions,
        "comparison_basis": "공급가액 기준 개당 단가를 비교하고 동률이면 정규화 업체명 오름차순의 첫 업체 선택. 견적과 거래명세서는 모두 집계 대상이며 동일 문서 번호만 중복 제거.",
        "synthetic_notice": "합성 업무 자료. 업체명과 사업자등록번호는 실제 식별 정보가 아니며 번호 체크섬은 무효.",
    }
