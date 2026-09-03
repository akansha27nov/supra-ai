from agent.graph import route_after_validation


def test_route_to_resolve_sku_when_fields_are_complete(base_state):
    result = route_after_validation(base_state)
    assert result == "resolve_sku"


def test_absent_expected_field_does_not_block_resolution(base_state):
    # A missing covered_part_numbers/tested_lead_ppm is NOT treated as blocking —
    # resolve_sku_node and rule_engine_node already have dedicated downstream
    # handling for it (unmatched SKU, NO_MEASURED_LEAD_VALUE flag, etc.). Forcing
    # this into the reconcile loop broke real-world benchmark accuracy (see
    # agent/benchmark.py results) by escalating legitimately-scoreable documents
    # straight to REQUIRES_HUMAN_REVIEW instead of letting the rule engine run.
    base_state["field_status"]["tested_lead_ppm"] = "absent_expected"
    base_state["reconciliation_attempts"] = 0

    assert route_after_validation(base_state) == "resolve_sku"


def test_route_to_reconcile_on_second_attempt(base_state):
    base_state["field_status"]["tested_lead_ppm"] = "ambiguous"
    base_state["reconciliation_attempts"] = 1

    assert route_after_validation(base_state) == "reconcile"


def test_absent_expected_field_does_not_force_human_review_even_after_attempts(base_state):
    # Unlike "ambiguous", "absent_expected" is never escalated to human review by
    # route_after_validation, regardless of reconciliation_attempts — it isn't
    # something reconciliation ever runs for in the first place (see above).
    base_state["field_status"]["tested_lead_ppm"] = "absent_expected"
    base_state["reconciliation_attempts"] = 2

    assert route_after_validation(base_state) == "resolve_sku"


def test_ambiguous_field_also_triggers_reconciliation(base_state):
    base_state["field_status"]["expiration_date"] = "ambiguous"

    assert route_after_validation(base_state) == "reconcile"
