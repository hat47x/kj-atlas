from pathlib import Path

analyzer = Path("03_Implement/backend/scripts/analyze_ai_route_provider_measurement.py")
a = analyzer.read_text(encoding="utf-8")

old = '''def _context_budget_summary(\n    tokens: dict[str, int],\n    *,\n    layout_c_tokens: list[int],\n    context_window_tokens: int | None,\n) -> dict[str, Any]:\n'''
new = '''def _context_budget_summary(\n    tokens: dict[str, int],\n    *,\n    layout_c_tokens: list[int],\n    context_window_tokens: int | None,\n    context_window_source: str | None,\n) -> dict[str, Any]:\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

old = '''    if context_window_tokens is not None and (\n        isinstance(context_window_tokens, bool)\n        or not isinstance(context_window_tokens, int)\n        or context_window_tokens <= 0\n    ):\n        raise ValueError("context_window_tokens must be a positive integer")\n\n    route_requirements: dict[str, dict[str, Any]] = {}\n'''
new = '''    if context_window_tokens is not None and (\n        isinstance(context_window_tokens, bool)\n        or not isinstance(context_window_tokens, int)\n        or context_window_tokens <= 0\n    ):\n        raise ValueError("context_window_tokens must be a positive integer")\n    if context_window_tokens is None:\n        if context_window_source is not None:\n            raise ValueError(\n                "context_window_source requires context_window_tokens"\n            )\n        normalized_context_window_source = None\n    else:\n        if not isinstance(context_window_source, str) or not context_window_source.strip():\n            raise ValueError(\n                "context_window_source is required when context_window_tokens is supplied"\n            )\n        normalized_context_window_source = context_window_source.strip()\n\n    route_requirements: dict[str, dict[str, Any]] = {}\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

old = '''        "context_window_tokens": context_window_tokens,\n        "context_window_source": (\n            "operator-supplied" if context_window_tokens is not None else None\n        ),\n        "route_requirements": route_requirements,\n'''
new = '''        "context_window_tokens": context_window_tokens,\n        "context_window_source": normalized_context_window_source,\n        "context_window_source_kind": (\n            "operator-supplied-document-reference"\n            if normalized_context_window_source is not None\n            else None\n        ),\n        "route_requirements": route_requirements,\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

old = '''            "production LLMRequest output reserve. A supplied context window only "\n            "answers hard fit; this analyzer does not define a safety-margin percentage."\n'''
new = '''            "production LLMRequest output reserve. A supplied context window only "\n            "answers hard fit and must carry an operator-supplied documentation reference; "\n            "the analyzer records but does not verify that reference. It does not define a "\n            "safety-margin percentage."\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

old = '''def analyze(\n    report: Any,\n    *,\n    context_window_tokens: int | None = None,\n) -> dict[str, Any]:\n'''
new = '''def analyze(\n    report: Any,\n    *,\n    context_window_tokens: int | None = None,\n    context_window_source: str | None = None,\n) -> dict[str, Any]:\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

old = '''    context_budget = _context_budget_summary(\n        tokens,\n        layout_c_tokens=layout_c_tokens,\n        context_window_tokens=context_window_tokens,\n    )\n'''
new = '''    context_budget = _context_budget_summary(\n        tokens,\n        layout_c_tokens=layout_c_tokens,\n        context_window_tokens=context_window_tokens,\n        context_window_source=context_window_source,\n    )\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

old = '''            "current production LLMRequest output reserve to provider-reported input usage; an "\n            "operator-supplied context window can establish hard fit only. No safety-margin "\n            "percentage is invented and this analyzer does not choose A2/B/C."\n'''
new = '''            "current production LLMRequest output reserve to provider-reported input usage; an "\n            "operator-supplied context window can establish hard fit only when its documentation "\n            "reference is recorded. The reference is provenance, not independently verified by "\n            "this analyzer. No safety-margin percentage is invented and this analyzer does not "\n            "choose A2/B/C."\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

old = '''    parser.add_argument(\n        "--context-window-tokens",\n        type=_positive_token_count,\n        default=None,\n        help=(\n            "Optional documented context-window size for the named model. "\n            "Used only for hard-fit arithmetic; it does not change measurement readiness "\n            "or define an architectural safety-margin percentage."\n        ),\n    )\n    return parser\n'''
new = '''    parser.add_argument(\n        "--context-window-tokens",\n        type=_positive_token_count,\n        default=None,\n        help=(\n            "Optional documented context-window size for the named model. "\n            "Used only for hard-fit arithmetic; it does not change measurement readiness "\n            "or define an architectural safety-margin percentage."\n        ),\n    )\n    parser.add_argument(\n        "--context-window-source",\n        default=None,\n        help=(\n            "Required with --context-window-tokens: provider/model documentation URL, "\n            "document identifier, or equivalent audit reference for that context-window value."\n        ),\n    )\n    return parser\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

old = '''        result = analyze(\n            _load(args.report),\n            context_window_tokens=args.context_window_tokens,\n        )\n    except (OSError, json.JSONDecodeError) as exc:\n        result = {\n            "analysis": "ai-route-provider-measurement-readiness",\n            "decision_ready": False,\n            "errors": [f"measurement-report-read-error:{type(exc).__name__}"],\n        }\n'''
new = '''        result = analyze(\n            _load(args.report),\n            context_window_tokens=args.context_window_tokens,\n            context_window_source=args.context_window_source,\n        )\n    except (OSError, json.JSONDecodeError) as exc:\n        result = {\n            "analysis": "ai-route-provider-measurement-readiness",\n            "decision_ready": False,\n            "errors": [f"measurement-report-read-error:{type(exc).__name__}"],\n        }\n    except ValueError as exc:\n        result = {\n            "analysis": "ai-route-provider-measurement-readiness",\n            "decision_ready": False,\n            "errors": [f"context-window-argument-error:{exc}"],\n        }\n'''
assert a.count(old) == 1
a = a.replace(old, new, 1)

analyzer.write_text(a, encoding="utf-8")


test_path = Path("03_Implement/backend/tests/test_ai_route_provider_measurement_analysis.py")
t = test_path.read_text(encoding="utf-8")

old = '''import subprocess\nimport sys\nfrom pathlib import Path\n\nfrom scripts import analyze_ai_route_provider_measurement as analysis\n'''
new = '''import subprocess\nimport sys\nfrom pathlib import Path\n\nimport pytest\n\nfrom scripts import analyze_ai_route_provider_measurement as analysis\n'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

old = '''def test_context_window_option_reports_hard_fit_without_inventing_margin() -> None:\n    result = analysis.analyze(_core_report(), context_window_tokens=10_000)\n\n    budget = result["context_budget"]\n    assert result["decision_ready"] is True\n    assert budget["context_window_tokens"] == 10_000\n    assert budget["context_window_source"] == "operator-supplied"\n'''
new = '''def test_context_window_option_reports_hard_fit_without_inventing_margin() -> None:\n    result = analysis.analyze(\n        _core_report(),\n        context_window_tokens=10_000,\n        context_window_source=" https://provider.example/models/named-model ",\n    )\n\n    budget = result["context_budget"]\n    assert result["decision_ready"] is True\n    assert budget["context_window_tokens"] == 10_000\n    assert budget["context_window_source"] == "https://provider.example/models/named-model"\n    assert budget["context_window_source_kind"] == "operator-supplied-document-reference"\n'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

old = '''    result = analysis.analyze(report, context_window_tokens=3_000)\n'''
new = '''    result = analysis.analyze(\n        report,\n        context_window_tokens=3_000,\n        context_window_source="provider-doc: named-model context window",\n    )\n'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

needle = '''def test_groups_a2_adds_only_provider_reported_comparison() -> None:\n'''
new_tests = '''def test_context_window_tokens_require_documentation_source() -> None:\n    with pytest.raises(\n        ValueError,\n        match="context_window_source is required",\n    ):\n        analysis.analyze(_core_report(), context_window_tokens=10_000)\n\n\ndef test_context_window_source_cannot_exist_without_token_value() -> None:\n    with pytest.raises(\n        ValueError,\n        match="context_window_source requires context_window_tokens",\n    ):\n        analysis.analyze(\n            _core_report(),\n            context_window_source="https://provider.example/models/named-model",\n        )\n\n\n'''
assert t.count(needle) == 1
t = t.replace(needle, new_tests + needle, 1)

old = '''            "--context-window-tokens",\n            "10000",\n        ],\n'''
new = '''            "--context-window-tokens",\n            "10000",\n            "--context-window-source",\n            "https://provider.example/models/named-model",\n        ],\n'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

old = '''    assert result["context_budget"]["context_window_tokens"] == 10_000\n    assert result["context_budget"]["core_hard_context_fit"] is False\n'''
new = '''    assert result["context_budget"]["context_window_tokens"] == 10_000\n    assert result["context_budget"]["context_window_source"] == (\n        "https://provider.example/models/named-model"\n    )\n    assert result["context_budget"]["core_hard_context_fit"] is False\n'''
# Replace only CLI occurrence; the earlier function has an intervening source assertion.
assert t.count(old) == 1
t = t.replace(old, new, 1)

needle = '''def test_cli_returns_nonzero_for_incomplete_report(tmp_path: Path) -> None:\n'''
cli_missing_source = '''def test_cli_rejects_context_window_without_source(tmp_path: Path) -> None:\n    backend_dir = Path(__file__).resolve().parents[1]\n    report_path = tmp_path / "measurement.json"\n    report_path.write_text(json.dumps(_core_report()), encoding="utf-8")\n\n    completed = subprocess.run(\n        [\n            sys.executable,\n            "scripts/analyze_ai_route_provider_measurement.py",\n            str(report_path),\n            "--context-window-tokens",\n            "10000",\n        ],\n        cwd=backend_dir,\n        check=False,\n        capture_output=True,\n        text=True,\n    )\n    result = json.loads(completed.stdout)\n\n    assert completed.returncode == 2\n    assert result["decision_ready"] is False\n    assert result["errors"] == [\n        "context-window-argument-error:context_window_source is required when "\n        "context_window_tokens is supplied"\n    ]\n\n\n'''
assert t.count(needle) == 1
t = t.replace(needle, cli_missing_source + needle, 1)

test_path.write_text(t, encoding="utf-8")
