from pathlib import Path

analyzer = Path("03_Implement/backend/scripts/analyze_ai_route_provider_measurement.py")
a = analyzer.read_text(encoding="utf-8")

needle = "from pathlib import Path\nfrom typing import Any\n\ntry:\n"
replacement = "from pathlib import Path\nfrom typing import Any\n\nfrom kj_atlas_api.llm.provider import LLMRequest\n\ntry:\n"
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

needle = "LAYOUT_C_REQUESTS = len(LAYOUT_C_ROUTES)\n\n\ndef _int_token"
replacement = '''LAYOUT_C_REQUESTS = len(LAYOUT_C_ROUTES)\nMEASUREMENT_REQUEST_MAX_TOKENS = 1\n# The four measured production tasks currently rely on LLMRequest's default\n# output cap. Keep the comparison reserve derived from that source instead of\n# copying the literal 2000 into token-budget arithmetic. Measurement requests\n# deliberately use max_tokens=1 only to minimize external measurement cost.\nCURRENT_PRODUCTION_OUTPUT_RESERVE_TOKENS = LLMRequest(\n    task="context_budget_probe", prompt="probe"\n).max_tokens\n\n\ndef _int_token'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

needle = "\n\ndef analyze(report: Any) -> dict[str, Any]:\n"
helper = r'''


def _context_budget_summary(
    tokens: dict[str, int],
    *,
    context_window_tokens: int | None,
) -> dict[str, Any]:
    """Separate measured input usage from the current production output reserve.

    This is a hard context-fit calculation only. It intentionally does not invent
    an architectural headroom percentage or choose A2/B/C.
    """
    if context_window_tokens is not None and (
        isinstance(context_window_tokens, bool)
        or not isinstance(context_window_tokens, int)
        or context_window_tokens <= 0
    ):
        raise ValueError("context_window_tokens must be a positive integer")

    route_requirements: dict[str, dict[str, Any]] = {}
    for name in sorted(tokens):
        input_tokens = tokens[name]
        minimum = input_tokens + CURRENT_PRODUCTION_OUTPUT_RESERVE_TOKENS
        remaining = (
            None
            if context_window_tokens is None
            else context_window_tokens - minimum
        )
        route_requirements[name] = {
            "provider_reported_input_tokens": input_tokens,
            "output_reserve_tokens": CURRENT_PRODUCTION_OUTPUT_RESERVE_TOKENS,
            "minimum_context_tokens": minimum,
            "remaining_context_tokens": remaining,
            "hard_context_fit": None if remaining is None else remaining >= 0,
        }

    core_requirements = [
        route_requirements[name]
        for name in CORE_ROUTES
        if name in route_requirements
    ]
    layout_c_requirements = [
        route_requirements[name]
        for name in LAYOUT_C_ROUTES
        if name in route_requirements
    ]
    groups_a2_requirement = route_requirements.get(GROUPS_A2_ROUTE)

    def _all_fit(rows: list[dict[str, Any]], *, complete: bool) -> bool | None:
        if context_window_tokens is None or not complete:
            return None
        return all(row["hard_context_fit"] is True for row in rows)

    return {
        "measurement_request_max_tokens": MEASUREMENT_REQUEST_MAX_TOKENS,
        "current_production_output_reserve_tokens": (
            CURRENT_PRODUCTION_OUTPUT_RESERVE_TOKENS
        ),
        "output_reserve_source": "LLMRequest.default.max_tokens",
        "context_window_tokens": context_window_tokens,
        "context_window_source": (
            "operator-supplied" if context_window_tokens is not None else None
        ),
        "route_requirements": route_requirements,
        "core_hard_context_fit": _all_fit(
            core_requirements, complete=len(core_requirements) == len(CORE_ROUTES)
        ),
        "groups_a2_hard_context_fit": (
            None
            if context_window_tokens is None or groups_a2_requirement is None
            else groups_a2_requirement["hard_context_fit"]
        ),
        "layout_c_hard_context_fit": _all_fit(
            layout_c_requirements,
            complete=len(layout_c_requirements) == LAYOUT_C_REQUESTS,
        ),
        "layout_c_max_single_minimum_context_tokens": (
            max(row["minimum_context_tokens"] for row in layout_c_requirements)
            if len(layout_c_requirements) == LAYOUT_C_REQUESTS
            else None
        ),
        "sufficient_headroom_policy": None,
        "interpretation": (
            "minimum_context_tokens = provider-reported input_tokens + the current "
            "production LLMRequest output reserve. A supplied context window only "
            "answers hard fit; this analyzer does not define a safety-margin percentage."
        ),
    }


def analyze(
    report: Any,
    *,
    context_window_tokens: int | None = None,
) -> dict[str, Any]:
'''
assert a.count(needle) == 1
a = a.replace(needle, helper, 1)

needle = '''    canonical_prompt_hashes = {
        name: _prompt_sha256(req.prompt) for name, req in canonical_requests.items()
    }
'''
replacement = '''    canonical_prompt_hashes = {
        name: _prompt_sha256(req.prompt) for name, req in canonical_requests.items()
    }
    for name, req in canonical_requests.items():
        if req.max_tokens != MEASUREMENT_REQUEST_MAX_TOKENS:
            errors.append(
                f"measurement-max-tokens-drift:{name}:{req.max_tokens}"
            )
'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

needle = '''    return {
        "analysis": "ai-route-provider-measurement-readiness",
'''
replacement = '''    context_budget = _context_budget_summary(
        tokens,
        context_window_tokens=context_window_tokens,
    )

    return {
        "analysis": "ai-route-provider-measurement-readiness",
'''
# There are two return dictionaries with this start; replace the last/main one only.
assert a.count(needle) == 2
index = a.rfind(needle)
a = a[:index] + a[index:].replace(needle, replacement, 1)

needle = '''        "observations": {
            "groups": groups,
            "layout": layout,
            "whole_document": whole_document,
        },
        "interpretation_boundary": (
'''
replacement = '''        "observations": {
            "groups": groups,
            "layout": layout,
            "whole_document": whole_document,
        },
        "context_budget": context_budget,
        "interpretation_boundary": (
'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

needle = '''            "and hashes are never converted into tokens. DeepSeek measurements additionally bind "
            "the exact current OpenAI-chat system+user message content. This report does not know the "
            "model context limit or choose A2/B/C; optional A2/C readiness only records whether "
            "those explicit measurements are present and internally complete."
'''
replacement = '''            "and hashes are never converted into tokens. DeepSeek measurements additionally bind "
            "the exact current OpenAI-chat system+user message content. Context minimums add the "
            "current production LLMRequest output reserve to provider-reported input usage; an "
            "operator-supplied context window can establish hard fit only. No safety-margin "
            "percentage is invented and this analyzer does not choose A2/B/C."
'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

needle = '''def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="measurement JSON path, or '-' to read stdin")
    return parser
'''
replacement = '''def _positive_token_count(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="measurement JSON path, or '-' to read stdin")
    parser.add_argument(
        "--context-window-tokens",
        type=_positive_token_count,
        default=None,
        help=(
            "Optional documented context-window size for the named model. "
            "Used only for hard-fit arithmetic; it does not change measurement readiness "
            "or define an architectural safety-margin percentage."
        ),
    )
    return parser
'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

needle = '''    try:
        result = analyze(_load(args.report))
    except (OSError, json.JSONDecodeError) as exc:
'''
replacement = '''    try:
        result = analyze(
            _load(args.report),
            context_window_tokens=args.context_window_tokens,
        )
    except (OSError, json.JSONDecodeError) as exc:
'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

analyzer.write_text(a, encoding="utf-8")


test_path = Path("03_Implement/backend/tests/test_ai_route_provider_measurement_analysis.py")
t = test_path.read_text(encoding="utf-8")

needle = '''def test_groups_a2_adds_only_provider_reported_comparison() -> None:
'''
new_tests = r'''
def test_context_budget_separates_measurement_cap_from_production_output_reserve() -> None:
    result = analysis.analyze(_core_report())

    budget = result["context_budget"]
    assert budget["measurement_request_max_tokens"] == 1
    assert budget["current_production_output_reserve_tokens"] == 2_000
    assert budget["output_reserve_source"] == "LLMRequest.default.max_tokens"
    assert budget["context_window_tokens"] is None
    assert budget["core_hard_context_fit"] is None
    assert budget["sufficient_headroom_policy"] is None
    check = budget["route_requirements"]["check-narrative"]
    assert check == {
        "provider_reported_input_tokens": 11_000,
        "output_reserve_tokens": 2_000,
        "minimum_context_tokens": 13_000,
        "remaining_context_tokens": None,
        "hard_context_fit": None,
    }


def test_context_window_option_reports_hard_fit_without_inventing_margin() -> None:
    result = analysis.analyze(_core_report(), context_window_tokens=10_000)

    budget = result["context_budget"]
    assert result["decision_ready"] is True
    assert budget["context_window_tokens"] == 10_000
    assert budget["context_window_source"] == "operator-supplied"
    assert budget["core_hard_context_fit"] is False
    assert budget["route_requirements"]["suggest-layout-route-b"]["minimum_context_tokens"] == 10_000
    assert budget["route_requirements"]["suggest-layout-route-b"]["remaining_context_tokens"] == 0
    assert budget["route_requirements"]["suggest-layout-route-b"]["hard_context_fit"] is True
    assert budget["route_requirements"]["check-narrative"]["remaining_context_tokens"] == -3_000
    assert budget["route_requirements"]["check-narrative"]["hard_context_fit"] is False
    assert budget["sufficient_headroom_policy"] is None


def test_layout_c_context_budget_uses_max_single_request_not_aggregate() -> None:
    report = _core_report()
    _add_complete_layout_c(report)

    result = analysis.analyze(report, context_window_tokens=3_000)

    budget = result["context_budget"]
    assert result["layout_c_ready"] is True
    assert budget["layout_c_max_single_minimum_context_tokens"] == 2_900
    assert budget["layout_c_hard_context_fit"] is True
    # Aggregate C input usage is a cost/throughput observation, not one context window.
    assert result["observations"]["layout"]["layout_c_aggregate_input_tokens"] > 3_000


'''
assert t.count(needle) == 1
t = t.replace(needle, new_tests + needle, 1)

needle = '''    assert result["decision_ready"] is True
    assert result["provider"] == "named-provider"
    assert result["model"] == "named-model"
'''
replacement = '''    assert result["decision_ready"] is True
    assert result["provider"] == "named-provider"
    assert result["model"] == "named-model"
    assert result["context_budget"]["context_window_tokens"] is None
'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)

# Add a CLI context-window probe before the incomplete-report case.
needle = '''\ndef test_cli_returns_nonzero_for_incomplete_report(tmp_path: Path) -> None:\n'''
cli_test = r'''
def test_cli_accepts_explicit_context_window_for_hard_fit_only(tmp_path: Path) -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    report_path = tmp_path / "measurement.json"
    report_path.write_text(json.dumps(_core_report()), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/analyze_ai_route_provider_measurement.py",
            str(report_path),
            "--context-window-tokens",
            "10000",
        ],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)

    assert result["decision_ready"] is True
    assert result["context_budget"]["context_window_tokens"] == 10_000
    assert result["context_budget"]["core_hard_context_fit"] is False
    assert result["context_budget"]["sufficient_headroom_policy"] is None


'''
assert t.count(needle) == 1
t = t.replace(needle, "\n" + cli_test + needle.lstrip("\\n"), 1)

test_path.write_text(t, encoding="utf-8")
