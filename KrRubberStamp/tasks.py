"""Task contracts shared by generation and independent quality gates."""

import hashlib
import uuid
from .io import json_bytes
from .registry import PERIODS, instructions

TASK_NAMESPACE = uuid.UUID("c0152180-4caa-57db-86df-8c497d5f0eab")


def scenario_hash(scenario):
    return hashlib.sha256(json_bytes(scenario)).hexdigest()


def make_schema(value):
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, dict):
        return {
            "type": "object",
            "properties": {k: make_schema(v) for k, v in value.items()},
            "required": list(value),
            "additionalProperties": False,
        }
    if isinstance(value, list):
        distinct = {str(make_schema(item)): make_schema(item) for item in value}
        schemas = list(distinct.values())
        return {
            "type": "array",
            "items": schemas[0] if len(schemas) == 1 else {"anyOf": schemas} if schemas else {},
        }
    if value is None:
        return {"type": "null"}
    raise TypeError(f"Non-exact gold type: {type(value).__name__}")


def instruction_for(domain, difficulty, scenario_seed):
    choices = instructions(domain)
    wording = choices[scenario_seed % len(choices)]
    period = PERIODS[domain]
    if domain != "D_extract":
        wording += f" 기준 기간은 {period}입니다."
    else:
        wording += (
            " 업체명에는 NFKC와 공백 제거 및 대소문자 통일을 적용하고 주식회사, (주), ㈜ 표기는 제거해 주세요."
            " 품목명에도 NFKC와 공백 제거 및 대소문자 통일을 적용해 주세요."
            " vendor_totals는 정규화 업체명 오름차순, cheapest_by_item은 정규화 품목명 오름차순으로 작성해 주세요."
            " 단가는 부가세 제외 공급가액 기준이며 최저 단가 동률이면 정규화 업체명 오름차순 첫 업체를 선택해 주세요."
        )
    wording += " 입력 자료의 적용 조건과 중복 자료 안내를 확인해 주세요. 금액은 원 단위 정수로 적고 answer.json의 필드 이름과 배열 순서는 제공한 스키마와 안내를 따라 주세요."
    return wording


def canary_for(identity):
    return f"KrRubberStamp-canary-{uuid.uuid5(TASK_NAMESPACE, identity)}"
