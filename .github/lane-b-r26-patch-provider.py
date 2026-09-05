from pathlib import Path

path = Path("03_Implement/backend/scripts/measure_ai_route_provider_tokens.py")
s = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)


replace_once(
    '''try:\n    from scripts.measure_ai_route_prompt_coverage import representative_document\n    from scripts.measure_ai_route_projection_candidates import (\n        _groups_candidate_context,\n        _late_layout_document,\n        _layout_candidate_context,\n    )\nexcept ModuleNotFoundError as exc:\n    if exc.name != "scripts":\n        raise\n    from measure_ai_route_prompt_coverage import representative_document\n    from measure_ai_route_projection_candidates import (\n        _groups_candidate_context,\n        _late_layout_document,\n        _layout_candidate_context,\n    )\n''',
    '''try:\n    from scripts.measure_ai_layout_hierarchical_candidate import (\n        build_hierarchical_layout_candidate,\n    )\n    from scripts.measure_ai_route_prompt_coverage import representative_document\n    from scripts.measure_ai_route_projection_candidates import (\n        _groups_candidate_context,\n        _late_layout_document,\n        _layout_candidate_context,\n    )\nexcept ModuleNotFoundError as exc:\n    if exc.name != "scripts":\n        raise\n    from measure_ai_layout_hierarchical_candidate import (\n        build_hierarchical_layout_candidate,\n    )\n    from measure_ai_route_prompt_coverage import representative_document\n    from measure_ai_route_projection_candidates import (\n        _groups_candidate_context,\n        _late_layout_document,\n        _layout_candidate_context,\n    )\n''',
)

replace_once(
    'def build_representative_requests(model: str) -> dict[str, LLMRequest]:\n',
    '''def build_representative_requests(\n    model: str, *, include_layout_c: bool = False\n) -> dict[str, LLMRequest]:\n''',
)
replace_once(
    '''    return {\n        "suggest-card-groups": LLMRequest(\n''',
    '''    requests = {\n        "suggest-card-groups": LLMRequest(\n''',
)
replace_once(
    '''        "check-narrative": LLMRequest(\n            task="check_narrative",\n            prompt=check_prompt,\n            inputs=None,\n            temperature=0.0,\n            max_tokens=1,\n            model=model,\n        ),\n    }\n\n\ndef _route_row(req: LLMRequest) -> dict[str, Any]:\n''',
    '''        "check-narrative": LLMRequest(\n            task="check_narrative",\n            prompt=check_prompt,\n            inputs=None,\n            temperature=0.0,\n            max_tokens=1,\n            model=model,\n        ),\n    }\n\n    if include_layout_c:\n        layout_c = build_hierarchical_layout_candidate(layout_doc)\n        for index, item in enumerate(layout_c["local_prompts"], start=1):\n            requests[f"suggest-layout-c-local-{index:02d}"] = LLMRequest(\n                task="re_layout",\n                prompt=item["prompt"],\n                # R25 measurement-only prompt. Provider transports send only the\n                # prompt; this is not a production IR contract.\n                inputs=None,\n                temperature=0.0,\n                max_tokens=1,\n                model=model,\n            )\n        requests["suggest-layout-c-global"] = LLMRequest(\n            task="re_layout",\n            prompt=layout_c["global_prompt"],\n            inputs=None,\n            temperature=0.0,\n            max_tokens=1,\n            model=model,\n        )\n\n    return requests\n\n\ndef _route_row(req: LLMRequest) -> dict[str, Any]:\n''',
)

replace_once(
    '''def measure(\n    *,\n    model: str,\n''',
    '''def _layout_c_summary(\n    routes: dict[str, dict[str, Any]], *, included: bool\n) -> dict[str, Any]:\n    if not included:\n        return {\n            "included": False,\n            "requests": 0,\n            "prompt": {\n                "max_single_utf8_bytes": None,\n                "aggregate_utf8_bytes": None,\n            },\n            "provider_reported": {\n                "input_tokens_complete": False,\n                "aggregate_input_tokens": None,\n                "max_single_input_tokens": None,\n            },\n        }\n\n    names = sorted(\n        name for name in routes if name.startswith("suggest-layout-c-")\n    )\n    prompt_bytes = [routes[name]["prompt"]["utf8_bytes"] for name in names]\n    token_values = [\n        routes[name]["provider_reported"]["input_tokens"] for name in names\n    ]\n    tokens_complete = bool(token_values) and all(\n        isinstance(value, int) for value in token_values\n    )\n    measured_tokens = [\n        int(value) for value in token_values if isinstance(value, int)\n    ]\n    return {\n        "included": True,\n        "requests": len(names),\n        "prompt": {\n            "max_single_utf8_bytes": max(prompt_bytes) if prompt_bytes else None,\n            "aggregate_utf8_bytes": sum(prompt_bytes) if prompt_bytes else None,\n        },\n        "provider_reported": {\n            "input_tokens_complete": tokens_complete,\n            "aggregate_input_tokens": (\n                sum(measured_tokens) if tokens_complete else None\n            ),\n            "max_single_input_tokens": (\n                max(measured_tokens) if tokens_complete else None\n            ),\n        },\n    }\n\n\ndef measure(\n    *,\n    model: str,\n''',
)
replace_once(
    '''    expected_provider: str,\n    execute: bool = False,\n    provider: _Provider | None = None,\n) -> dict[str, Any]:\n''',
    '''    expected_provider: str,\n    execute: bool = False,\n    provider: _Provider | None = None,\n    include_layout_c: bool = False,\n) -> dict[str, Any]:\n''',
)
replace_once(
    '''    requests = build_representative_requests(model)\n    routes = {name: _route_row(req) for name, req in requests.items()}\n''',
    '''    requests = build_representative_requests(\n        model, include_layout_c=include_layout_c\n    )\n    routes = {name: _route_row(req) for name, req in requests.items()}\n''',
)
replace_once(
    '''        "measurement_complete": False,\n        "routes": routes,\n        "interpretation_boundary": (\n''',
    '''        "measurement_complete": False,\n        "routes": routes,\n        "layout_c_summary": _layout_c_summary(\n            routes, included=include_layout_c\n        ),\n        "interpretation_boundary": (\n''',
)
replace_once(
    '''    report["measurement_complete"] = all_measured\n    return report\n''',
    '''    report["layout_c_summary"] = _layout_c_summary(\n        routes, included=include_layout_c\n    )\n    report["measurement_complete"] = all_measured\n    return report\n''',
)
replace_once(
    '''    parser.add_argument(\n        "--execute",\n        action="store_true",\n        help=(\n            "合成した代表プロンプトを実際に送信する。"\n            f"{OPT_IN_ENV}=1 も必要であり、指定しなければネットワークを使わないドライランとなる。"\n        ),\n    )\n    return parser\n''',
    '''    parser.add_argument(\n        "--execute",\n        action="store_true",\n        help=(\n            "合成した代表プロンプトを実際に送信する。"\n            f"{OPT_IN_ENV}=1 も必要であり、指定しなければネットワークを使わないドライランとなる。"\n        ),\n    )\n    parser.add_argument(\n        "--include-layout-c",\n        action="store_true",\n        help=(\n            "R25の階層layout C候補（local 30 + global 1）も比較する。"\n            "--execute と併用すると31件の追加provider requestが発生するため、"\n            "Cを明示的に測る場合だけ指定する。"\n        ),\n    )\n    return parser\n''',
)
replace_once(
    '''                    expected_provider=args.provider,\n                    execute=False,\n                ),\n''',
    '''                    expected_provider=args.provider,\n                    execute=False,\n                    include_layout_c=args.include_layout_c,\n                ),\n''',
)
replace_once(
    '''            expected_provider=args.provider,\n            execute=True,\n            provider=provider,\n        )\n''',
    '''            expected_provider=args.provider,\n            execute=True,\n            provider=provider,\n            include_layout_c=args.include_layout_c,\n        )\n''',
)

path.write_text(s, encoding="utf-8")
