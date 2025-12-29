from app.services.rules import try_match_rules


def test_rules_billing():
    r = try_match_rules("Need invoice for last month")
    assert r.matched
    assert r.category == "Billing"


def test_rules_account():
    r = try_match_rules("I can't login, password reset not working")
    assert r.matched
    assert r.category == "Account / Access"
