from agent.graph import (
    _normalize_std,
    _standard_is_covered,
    match_sku,
)


def test_normalize_standard_extracts_directive_code():
    assert _normalize_std(
        "RoHS Directive 2011/65/EU (restricted substances)"
    ) == "2011/65/EU"


def test_normalize_standard_extracts_hyphenated_standard():
    assert _normalize_std("EN 62368-1:2020") == "62368-1"


def test_normalize_standard_handles_empty_input():
    assert _normalize_std("") == ""
    assert _normalize_std(None) == ""


def test_normalize_standard_falls_back_to_alphanumeric_text():
    assert _normalize_std("ABC-123 / test") == "ABC123TEST"


def test_standard_is_covered_by_directive_code():
    assert _standard_is_covered(
        "RoHS Directive 2011/65/EU",
        ["2011/65/EU"],
    )


def test_standard_is_covered_ignores_parenthetical_details():
    assert _standard_is_covered(
        "RED Directive 2014/53/EU",
        ["RED Directive 2014/53/EU (Radio Equipment)"],
    )


def test_standard_is_not_covered_when_codes_differ():
    assert not _standard_is_covered(
        "RED Directive 2014/53/EU",
        ["EMC Directive 2014/30/EU"],
    )


def test_match_sku_matches_case_insensitively():
    catalog = {
        "SKU-001": {
            "covered_part_numbers": ["MODEL-ABC"],
        }
    }

    assert match_sku(["model-abc"], catalog) == "SKU-001"


def test_match_sku_supports_mpn_cross_reference():
    catalog = {
        "SKU-001": {
            "mpn_cross_reference": ["MPN-123"],
        }
    }

    assert match_sku(["MPN-123"], catalog) == "SKU-001"


def test_match_sku_returns_none_for_no_match():
    catalog = {
        "SKU-001": {
            "covered_part_numbers": ["MODEL-ABC"],
        }
    }

    assert match_sku(["MODEL-XYZ"], catalog) is None


def test_match_sku_returns_none_for_empty_inputs():
    assert match_sku([], {}) is None
    assert match_sku(["MODEL-001"], {}) is None
    assert match_sku([], {"SKU-001": {}}) is None
