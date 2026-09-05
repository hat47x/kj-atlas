from pathlib import Path

provider_path = Path("03_Implement/backend/scripts/measure_ai_route_provider_tokens.py")
s = provider_path.read_text(encoding="utf-8")

old = '''try:
    from scripts.measure_ai_layout_hierarchical_candidate import (
        build_hierarchical_layout_candidate,
    )
    from scripts.measure_ai_route_prompt_coverage import representative_document
'''
new = '''try:
    from scripts.measure_ai_layout_hierarchical_candidate import (
        build_hierarchical_layout_candidate,
    )
    from scripts.measure_ai_route_a2_candidate import (
        _temporary_representative_fit_budget,
    )
    from scripts.measure_ai_route_prompt_coverage import representative_document
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''    from measure_ai_layout_hierarchical_candidate import (
        build_hierarchical_layout_candidate,
    )
    from measure_ai_route_prompt_coverage import representative_document
'''
new = '''    from measure_ai_layout_hierarchical_candidate import (
        build_hierarchical_layout_candidate,
    )
    from measure_ai_route_a2_candidate import (
        _temporary_representative_fit_budget,
    )
    from measure_ai_route_prompt_coverage import representative_document
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''def build_representative_requests(
    model: str, *, include_layout_c: bool = False
) -> dict[str, LLMRequest]:
'''
new = '''def build_representative_requests(
    model: str,
    *,
    include_layout_c: bool = False,
    include_groups_a2: bool = False,
) -> dict[str, LLMRequest]:
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''    groups_b_prompt = _build_suggest_card_groups_prompt(
        groups_payload, groups_b_context, groups_b_candidate_ids
    )

    layout_doc = _late_layout_document()
'''
new = '''    groups_b_prompt = _build_suggest_card_groups_prompt(
        groups_payload, groups_b_context, groups_b_candidate_ids
    )

    groups_a2_ir: dict[str, Any] | None = None
    groups_a2_prompt: str | None = None
    if include_groups_a2:
        # R29 measurement-only A2 lower bound. The context manager temporarily
        # fits this synthetic fixture and restores production caps before any
        # provider request can be sent.
        with _temporary_representative_fit_budget(groups_payload.doc):
            groups_a2_ir = _suggest_card_groups_ir(groups_payload)
        groups_a2_candidate_ids, _ = _card_group_candidates(
            groups_payload, groups_a2_ir
        )
        groups_a2_prompt = _build_suggest_card_groups_prompt(
            groups_payload, groups_a2_ir, groups_a2_candidate_ids
        )

    layout_doc = _late_layout_document()
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''    if include_layout_c:
        layout_c = build_hierarchical_layout_candidate(layout_doc)
'''
new = '''    if include_groups_a2:
        assert groups_a2_ir is not None
        assert groups_a2_prompt is not None
        requests["suggest-card-groups-a2-lower-bound"] = LLMRequest(
            task="suggest_card_groups",
            prompt=groups_a2_prompt,
            # Measurement-only R29 lower-bound shared IR, not a production cap
            # or production projection contract.
            inputs=groups_a2_ir,
            temperature=0.0,
            max_tokens=1,
            model=model,
        )

    if include_layout_c:
        layout_c = build_hierarchical_layout_candidate(layout_doc)
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''    provider: _Provider | None = None,
    include_layout_c: bool = False,
) -> dict[str, Any]:
'''
new = '''    provider: _Provider | None = None,
    include_layout_c: bool = False,
    include_groups_a2: bool = False,
) -> dict[str, Any]:
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''    requests = build_representative_requests(
        model, include_layout_c=include_layout_c
    )
'''
new = '''    requests = build_representative_requests(
        model,
        include_layout_c=include_layout_c,
        include_groups_a2=include_groups_a2,
    )
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''    parser.add_argument(
        "--include-layout-c",
        action="store_true",
        help=(
            "R25の階層layout C候補（local 30 + global 1）も比較する。"
            "--execute と併用すると31件の追加provider requestが発生するため、"
            "Cを明示的に測る場合だけ指定する。"
        ),
    )
    return parser
'''
new = '''    parser.add_argument(
        "--include-layout-c",
        action="store_true",
        help=(
            "R25の階層layout C候補（local 30 + global 1）も比較する。"
            "--execute と併用すると31件の追加provider requestが発生するため、"
            "Cを明示的に測る場合だけ指定する。"
        ),
    )
    parser.add_argument(
        "--include-groups-a2",
        action="store_true",
        help=(
            "R29のsuggest-card-groups A2下限候補も比較する。"
            "--execute と併用すると1件の追加provider requestが発生する。"
            "layout A2はR29でroute-Bとprompt完全一致のため重複送信しない。"
        ),
    )
    return parser
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''                    expected_provider=args.provider,
                    execute=False,
                    include_layout_c=args.include_layout_c,
                ),
'''
new = '''                    expected_provider=args.provider,
                    execute=False,
                    include_layout_c=args.include_layout_c,
                    include_groups_a2=args.include_groups_a2,
                ),
'''
assert s.count(old) == 1
s = s.replace(old, new)

old = '''            execute=True,
            provider=provider,
            include_layout_c=args.include_layout_c,
        )
'''
new = '''            execute=True,
            provider=provider,
            include_layout_c=args.include_layout_c,
            include_groups_a2=args.include_groups_a2,
        )
'''
assert s.count(old) == 1
s = s.replace(old, new)

provider_path.write_text(s, encoding="utf-8")

test_path = Path("03_Implement/backend/tests/test_ai_route_provider_token_measurement.py")
t = test_path.read_text(encoding="utf-8")

old = '''LAYOUT_C_ROUTES = {
    *(f"suggest-layout-c-local-{index:02d}" for index in range(1, 31)),
    "suggest-layout-c-global",
}
'''
new = '''LAYOUT_C_ROUTES = {
    *(f"suggest-layout-c-local-{index:02d}" for index in range(1, 31)),
    "suggest-layout-c-global",
}
GROUPS_A2_ROUTE = "suggest-card-groups-a2-lower-bound"
'''
assert t.count(old) == 1
t = t.replace(old, new)

marker = '''def test_layout_c_requests_are_explicit_opt_in_and_match_r25_diagnostics() -> None:
'''
insert = '''def test_groups_a2_request_is_explicit_opt_in_and_matches_r29_diagnostics() -> None:
    default_requests = token_measure.build_representative_requests("named-model")
    requests = token_measure.build_representative_requests(
        "named-model", include_groups_a2=True
    )

    assert set(default_requests) == EXPECTED_ROUTES
    assert set(requests) == EXPECTED_ROUTES | {GROUPS_A2_ROUTE}
    assert len(requests) == 7

    groups_a2 = requests[GROUPS_A2_ROUTE]
    groups_b = requests["suggest-card-groups-route-b"]
    layout_b = requests["suggest-layout-route-b"]
    assert groups_a2.task == "suggest_card_groups"
    assert groups_a2.model == "named-model"
    assert groups_a2.max_tokens == 1
    assert len((groups_a2.inputs or {}).get("cards", [])) == 300
    assert len((groups_a2.inputs or {}).get("relations", [])) == 300
    assert (groups_a2.inputs or {})["truncation"] == {
        "truncated": False,
        "reason_codes": [],
    }
    assert len(groups_a2.prompt.encode("utf-8")) == 56_047
    assert len(groups_b.prompt.encode("utf-8")) == 48_791
    assert groups_a2.prompt != groups_b.prompt

    # R29 proved layout A2 and route B render the identical 128,562-byte prompt;
    # R30 therefore adds no duplicate layout-A2 provider request.
    assert "suggest-layout-a2-lower-bound" not in requests
    assert len(layout_b.prompt.encode("utf-8")) == 128_562


'''
assert t.count(marker) == 1
t = t.replace(marker, insert + marker)

marker = '''def test_dry_run_never_needs_a_provider_or_claims_exact_tokens() -> None:
'''
insert = '''def test_groups_a2_dry_run_adds_one_request_without_provider_or_token_claim() -> None:
    report = token_measure.measure(
        model="named-model",
        expected_provider="named-test-provider",
        execute=False,
        include_groups_a2=True,
    )

    assert report["executed"] is False
    assert report["measurement_complete"] is False
    assert set(report["routes"]) == EXPECTED_ROUTES | {GROUPS_A2_ROUTE}
    row = report["routes"][GROUPS_A2_ROUTE]
    assert row["status"] == "dry-run"
    assert row["prompt"]["utf8_bytes"] == 56_047
    assert row["provider_reported"]["input_tokens"] is None


'''
assert t.count(marker) == 1
t = t.replace(marker, insert + marker)

marker = '''def test_direct_cli_layout_c_dry_run_is_network_free() -> None:
'''
insert = '''def test_direct_cli_groups_a2_dry_run_is_network_free() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/measure_ai_route_provider_tokens.py",
            "--provider",
            "named-test-provider",
            "--model",
            "named-model",
            "--include-groups-a2",
        ],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)

    assert report["executed"] is False
    assert len(report["routes"]) == 7
    assert report["routes"][GROUPS_A2_ROUTE]["prompt"]["utf8_bytes"] == 56_047
    assert "suggest-layout-a2-lower-bound" not in report["routes"]


def test_direct_cli_groups_a2_and_layout_c_dry_run_is_explicitly_38_requests() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/measure_ai_route_provider_tokens.py",
            "--provider",
            "named-test-provider",
            "--model",
            "named-model",
            "--include-groups-a2",
            "--include-layout-c",
        ],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)

    assert report["executed"] is False
    assert len(report["routes"]) == 38
    assert GROUPS_A2_ROUTE in report["routes"]
    assert report["layout_c_summary"]["requests"] == 31


'''
assert t.count(marker) == 1
t = t.replace(marker, insert + marker)

marker = '''def test_layout_c_provider_usage_aggregates_only_reported_usage() -> None:
'''
insert = '''def test_groups_a2_provider_usage_is_reported_without_estimation() -> None:
    provider = _UsageProvider()
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
        include_groups_a2=True,
    )

    assert report["measurement_complete"] is True
    assert len(provider.calls) == 7
    row = report["routes"][GROUPS_A2_ROUTE]
    assert row["status"] == "measured"
    # The seventh fake provider response reports 106. This is intentionally
    # arbitrary and unrelated to the 56,047 prompt bytes.
    assert row["provider_reported"] == {
        "input_tokens": 106,
        "output_tokens": 1,
    }
    assert row["provider_reported"]["input_tokens"] != row["prompt"]["utf8_bytes"]


def test_groups_a2_missing_usage_remains_incomplete_without_estimation() -> None:
    provider = _UsageProvider(report_usage=False)
    report = token_measure.measure(
        model="named-model",
        expected_provider=provider.provider_name,
        execute=True,
        provider=provider,
        include_groups_a2=True,
    )

    assert report["measurement_complete"] is False
    assert len(provider.calls) == 7
    assert report["routes"][GROUPS_A2_ROUTE]["status"] == (
        "provider-did-not-report-usage"
    )
    assert report["routes"][GROUPS_A2_ROUTE]["provider_reported"]["input_tokens"] is None


'''
assert t.count(marker) == 1
t = t.replace(marker, insert + marker)

test_path.write_text(t, encoding="utf-8")
