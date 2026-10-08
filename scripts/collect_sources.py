"""Assemble engine-owned source records and honest coverage report."""

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    rules = []
    required = {"rule_id", "description", "source", "effective_period", "verified"}
    for path in sorted((ROOT / "rules").glob("*/sources.yaml")):
        for rule in yaml.safe_load(path.read_text(encoding="utf-8")):
            if required - rule.keys() or type(rule["verified"]) is not bool:
                raise ValueError(f"Malformed source entry: {path}: {rule}")
            rules.append(rule)
    ids = [r["rule_id"] for r in rules]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate rule ID in source fragments")
    rules.sort(key=lambda rule: rule["rule_id"])
    (ROOT / "rules/sources.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "verified_definition": "공식 출처의 적용 시점 확인과 독립된 공식 수치 예시 회귀 검증을 모두 확보. 정부 계산 대상이 아닌 규약은 false.",
                "rules": rules,
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    missing = [rule for rule in rules if not rule["verified"]]
    lines = [
        "# 공식 수치 예시 미확인 규칙",
        "",
        f"전체 {len(rules)}개 출처 규칙 중 {len(missing)}개가 verified: false이다. false는 출처가 없다는 뜻으로 한정하지 않는다. 법령을 확인했지만 해당 계산의 공식 수치 예시를 확보하지 못한 경우도 포함한다.",
        "",
        "| 규칙 | 내용 | 미확인 사유 |",
        "|---|---|---|",
    ]
    for rule in missing:
        reason = rule.get(
            "verification_note",
            rule.get(
                "verification_notes",
                rule.get(
                    "unverified_reason",
                    rule.get(
                        "notes", "독립된 공식 수치 예시를 확보하지 못함. 분야별 연구 보고서 참조"
                    ),
                ),
            ),
        )
        reason = str(reason).replace("|", "/").replace("\n", " ")
        lines.append(f"| {rule['rule_id']} | {rule['description']} | {reason} |")
    lines += [
        "",
        "법령과 공식 안내 원문은 rules/sources.yaml에 기록했다. 도메인 D의 문서 통합 규약에는 대응하는 정부 계산 예시가 없다. 모델 API나 LLM 심사위원으로 미확인 사례를 채우지 않는다.",
        "",
    ]
    (ROOT / "reports/unverified_rules.md").write_text("\n".join(lines), encoding="utf-8")
    return {"total": len(rules), "verified": len(rules) - len(missing), "unverified": len(missing)}


if __name__ == "__main__":
    print(main())
