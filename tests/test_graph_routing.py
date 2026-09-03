from agent.graph import route_after_validation


def test_route_to_resolve_sku_when_fields_are_complete(base_state):
    result = route_after_validation(base_state)
    assert result == "resolve_sku"


def test_route_to_reconcile_on_second_attempt(base_state):
    base_state["field_status"]["tested_lead_ppm"] = "ambiguous"
    base_state["reconciliation_attempts"] = 1

    assert route_after_validation(base_state) == "reconcile"


def test_ambiguous_field_also_triggers_reconciliation(base_state):
    base_state["field_status"]["expiration_date"] = "ambiguous"

    assert route_after_validation(base_state) == "reconcile"
