from pathlib import Path

script_path = Path("03_Implement/backend/scripts/measure_ai_route_a2_candidate.py")
s = script_path.read_text(encoding="utf-8")
old = '''def representative_fit_budget(doc: Any) -> dict[str, int]:
    """Return the minimum shared card/text budgets needed by this fixture.

    This intentionally does not invent headroom. It only answers what the
    deterministic 300-card representative source needs to avoid those two
    current truncation reasons.
    """
    source = source_from_document(doc)
'''
new = '''def representative_fit_budget(doc: Any) -> dict[str, int]:
    """Return the minimum shared card/text budgets needed by this fixture.

    This intentionally does not invent headroom. It only answers what the
    deterministic 300-card representative source needs to avoid those two
    current truncation reasons. Raw representative-document dicts are accepted
    too, so the measurement helper cannot silently interpret them as empty
    duck-typed objects.
    """
    if isinstance(doc, dict):
        doc = SuggestLayoutRequest.model_validate({"doc": doc}).doc
    source = source_from_document(doc)
'''
assert s.count(old) == 1
s = s.replace(old, new)
script_path.write_text(s, encoding="utf-8")

test_path = Path("03_Implement/backend/tests/test_ai_route_a2_candidate.py")
t = test_path.read_text(encoding="utf-8")
old = '''    assert candidate["truncation"] == {"truncated": False, "reason_codes": []}
    assert candidate["prompt"]["utf8_bytes"] > 0


def test_a2_candidate_restores_full_layout_structure_and_tail_meaning() -> None:
'''
new = '''    assert candidate["truncation"] == {"truncated": False, "reason_codes": []}
    assert candidate["prompt"]["utf8_bytes"] == 56_047
    assert groups["route_b_candidate"]["prompt"]["utf8_bytes"] == 48_791
    assert groups["rendered_prompt_equivalent_to_b"] is False


def test_a2_candidate_restores_full_layout_structure_and_tail_meaning() -> None:
'''
assert t.count(old) == 1
t = t.replace(old, new)
old = '''    assert candidate["truncation"] == {"truncated": False, "reason_codes": []}
    assert candidate["prompt"]["utf8_bytes"] > 0


def test_temporary_budget_restores_constants_even_when_body_raises() -> None:
'''
new = '''    assert candidate["truncation"] == {"truncated": False, "reason_codes": []}
    assert candidate["prompt"]["utf8_bytes"] == 128_562
    assert layout["route_b_candidate"]["prompt"]["utf8_bytes"] == 128_562
    assert layout["rendered_prompt_equivalent_to_b"] is True


def test_temporary_budget_restores_constants_even_when_body_raises() -> None:
'''
assert t.count(old) == 1
t = t.replace(old, new)
test_path.write_text(t, encoding="utf-8")
