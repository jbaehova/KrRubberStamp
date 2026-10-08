from rules.common import floor_won, truncate_ten, mul_floor, normalize_text


def test_money_rules_are_explicit():
    assert floor_won("10.99") == 10
    assert floor_won("-10.01") == -11
    assert truncate_ten(119) == 110
    assert truncate_ten(-119) == -110
    assert mul_floor(12345, "0.045") == 555


def test_normalize():
    assert normalize_text(" Ａ B\n가 ") == "ab가"
