#!/usr/bin/env python3
"""代表規模のAIルートで、プロバイダーが報告する入力トークン数を測定する。

`AI-IR-SCALE-01` では、JSONのバイト数などから正確なトークン数を推定しない。
このスクリプトは、既存の代表規模の被覆状況計測と同じ、決定論的な300カード・30島の
入力から3種類の代表プロンプトを生成する。必要な場合だけ、明示的に指定した
プロバイダーとモデルへ送信する。正確な入力トークン数として採用するのは、
プロバイダー自身が返した `usage` の値だけである。

既定ではドライランとして動作し、プロバイダーの生成もネットワークへの接続も行わない。
外部へ実際に送信するには、`--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の
両方を指定する必要がある。送信対象は `representative_document()` が生成する
合成データだけであり、利用者の実データは使用しない。

比較対象には、意図的に性質の異なる3つのルートを選ぶ。

- `suggest-layout`: 移行済みルートのうち最も入力が大きい。正規化座標、関係、島構造をIRの文脈に含む。
- `generate-narrative`: 座標を使わない代表ルート。読み順はDocument由来のまま、論理関係をIRから受け取る。
- `check-narrative`: Stage 5で最後に残る全体照合ルート。現行実装どおりIRを介さず、Narrative・読み順・全島・全カードをpromptへ載せる。

`check-narrative` の合成Narrativeは、30島を各1行で言及する決定論的な短文とする。
Narrative本文だけを不必要に膨らませず、図解全量をA/B双方向で照合するときの入力規模を
比較できるようにするためである。

プロバイダーが入力トークン数を返さない場合も、別の方法で推定して補わない。出力には
`provider-did-not-report-usage` と `measurement_complete=false` を記録する。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from typing import Any, Protocol

from kj_atlas_api.llm.provider import (
    LLMRequest,
    LLMResponse,
    ProviderError,
    _openai_chat_messages,
    get_provider,
)
from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import (
    CheckNarrativeRequest,
    GenerateNarrativeRequest,
    SuggestCardGroupsRequest,
)
from kj_atlas_api.routes.ai import (
    _build_generate_narrative_prompt,
    _build_narrative_check_prompt,
    _build_prompt,
    _build_suggest_card_groups_prompt,
    _card_group_candidates,
    _generate_narrative_ir,
    _suggest_card_groups_ir,
    _suggest_layout_ir,
)
from kj_atlas_api.settings import settings

# `python -m scripts.measure_ai_route_provider_tokens` と、Issue本文で案内している
# `python scripts/measure_ai_route_provider_tokens.py` の両方を正式に動かす。
# 後者では `scripts/` 自身が sys.path の先頭になるため sibling import が必要になる。
try:
    from scripts.measure_ai_layout_hierarchical_candidate import (
        build_hierarchical_layout_candidate,
    )
    from scripts.measure_ai_route_a2_candidate import (
        _temporary_representative_fit_budget,
    )
    from scripts.measure_ai_route_prompt_coverage import representative_document
    from scripts.measure_ai_route_projection_candidates import (
        _groups_candidate_context,
        _late_layout_document,
        _layout_candidate_context,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from measure_ai_layout_hierarchical_candidate import (
        build_hierarchical_layout_candidate,
    )
    from measure_ai_route_a2_candidate import (
        _temporary_representative_fit_budget,
    )
    from measure_ai_route_prompt_coverage import representative_document
    from measure_ai_route_projection_candidates import (
        _groups_candidate_context,
        _late_layout_document,
        _layout_candidate_context,
    )

OPT_IN_ENV = "KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN"
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_DEEPSEEK_THINKING_MODES = frozenset({"disabled", "enabled"})
PROVIDER_GENERATION_PROVENANCE = {
    "version": 1,
    "deepseek_field": "thinking.type",
}


class _Provider(Protocol):
    provider_name: str
    provider_kind: str

    def generate(self, req: LLMRequest) -> LLMResponse:
        ...


def _representative_check_narrative_text(doc: dict[str, Any]) -> str:
    """30島を各1行で言及する、token計測専用の決定論的Narrativeを作る。"""
    cards_by_id = {card["id"]: card for card in doc["cards"]}
    lines: list[str] = []
    for island in doc["islands"]:
        first_card_id = island["cardIds"][0]
        first_card_text = cards_by_id[first_card_id]["text"]
        lines.append(f'{island["title"]}: {first_card_text}')
    return "\n".join(lines)


def build_representative_requests(
    model: str,
    *,
    include_layout_c: bool = False,
    include_groups_a2: bool = False,
) -> dict[str, LLMRequest]:
    """同じ代表規模でcurrent投影・route-B候補・全量routeを比較する。

    R23のmeasurement-only B候補をここでも同じbuilderから生成し、認証情報が
    利用可能になった時点でcurrent/Bを同じnamed provider/modelへ送れるようにする。
    production routeやshared IR上限は変更しない。
    """
    base_doc = representative_document(include_evidence=False)

    groups_doc = representative_document(include_evidence=False)
    next(card for card in groups_doc["cards"] if card["id"] == "c298")["holdState"] = "held"
    groups_payload = SuggestCardGroupsRequest.model_validate(
        {
            "doc": groups_doc,
            "cards": [
                {
                    "id": card["id"],
                    "text": card["text"],
                    "textReviewed": True,
                }
                for card in groups_doc["cards"]
            ],
        }
    )
    groups_ir = _suggest_card_groups_ir(groups_payload)
    groups_candidate_ids, _ = _card_group_candidates(groups_payload, groups_ir)
    groups_prompt = _build_suggest_card_groups_prompt(
        groups_payload, groups_ir, groups_candidate_ids
    )
    groups_b_context = _groups_candidate_context(groups_payload)
    groups_b_candidate_ids, _ = _card_group_candidates(groups_payload, groups_b_context)
    groups_b_prompt = _build_suggest_card_groups_prompt(
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
    layout_payload = SuggestLayoutRequest.model_validate({"doc": layout_doc})
    layout_ir = _suggest_layout_ir(layout_payload)
    layout_prompt = _build_prompt(layout_payload, layout_ir)
    layout_b_context = _layout_candidate_context(layout_payload)
    layout_b_prompt = _build_prompt(layout_payload, layout_b_context)

    narrative_payload = GenerateNarrativeRequest.model_validate({"doc": base_doc})
    narrative_ir = _generate_narrative_ir(narrative_payload)
    narrative_prompt = _build_generate_narrative_prompt(narrative_payload, narrative_ir)

    check_payload = CheckNarrativeRequest.model_validate(
        {
            "doc": base_doc,
            "narrativeText": _representative_check_narrative_text(base_doc),
        }
    )
    check_prompt = _build_narrative_check_prompt(check_payload)

    requests = {
        "suggest-card-groups": LLMRequest(
            task="suggest_card_groups",
            prompt=groups_prompt,
            inputs=groups_ir,
            temperature=0.0,
            max_tokens=1,
            model=model,
        ),
        "suggest-card-groups-route-b": LLMRequest(
            task="suggest_card_groups",
            prompt=groups_b_prompt,
            # Measurement-only R23 candidate context. Provider transports ignore
            # inputs and send prompt only; carrying it here keeps diagnostics paired.
            inputs=groups_b_context,
            temperature=0.0,
            max_tokens=1,
            model=model,
        ),
        "suggest-layout": LLMRequest(
            task="re_layout",
            prompt=layout_prompt,
            inputs=layout_ir,
            temperature=0.0,
            max_tokens=1,
            model=model,
        ),
        "suggest-layout-route-b": LLMRequest(
            task="re_layout",
            prompt=layout_b_prompt,
            # Measurement-only R23 candidate context; not a production IR contract.
            inputs=layout_b_context,
            temperature=0.0,
            max_tokens=1,
            model=model,
        ),
        "generate-narrative": LLMRequest(
            task="generate_narrative",
            prompt=narrative_prompt,
            inputs=narrative_ir,
            temperature=0.0,
            max_tokens=1,
            model=model,
        ),
        "check-narrative": LLMRequest(
            task="check_narrative",
            prompt=check_prompt,
            inputs=None,
            temperature=0.0,
            max_tokens=1,
            model=model,
        ),
    }

    if include_groups_a2:
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
        for index, item in enumerate(layout_c["local_prompts"], start=1):
            requests[f"suggest-layout-c-local-{index:02d}"] = LLMRequest(
                task="re_layout",
                prompt=item["prompt"],
                # R25 measurement-only prompt. Provider transports send only the
                # prompt; this is not a production IR contract.
                inputs=None,
                temperature=0.0,
                max_tokens=1,
                model=model,
            )
        requests["suggest-layout-c-global"] = LLMRequest(
            task="re_layout",
            prompt=layout_c["global_prompt"],
            inputs=None,
            temperature=0.0,
            max_tokens=1,
            model=model,
        )

    return requests


def _prompt_sha256(prompt: str) -> str:
    """Return an identity fingerprint for the exact UTF-8 provider prompt."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _openai_chat_messages_sha256(req: LLMRequest) -> str:
    """Fingerprint the exact system+user message content for DeepSeek chat input."""
    serialized = json.dumps(
        _openai_chat_messages(req),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _route_row(req: LLMRequest) -> dict[str, Any]:
    return {
        "task": req.task,
        "prompt": {
            "unicode_chars": len(req.prompt),
            "utf8_bytes": len(req.prompt.encode("utf-8")),
            "sha256": _prompt_sha256(req.prompt),
        },
        "ir": {
            "cards": len((req.inputs or {}).get("cards", [])),
            "relations": len((req.inputs or {}).get("relations", [])),
            "islands": len((req.inputs or {}).get("islands", [])),
            "coordinates": len((req.inputs or {}).get("coordinates", [])),
            "truncation": (req.inputs or {}).get("truncation"),
        },
        "provider_call": None,
        "provider_input": None,
        "provider_generation": None,
        "provider_reported": {
            "input_tokens": None,
            "output_tokens": None,
        },
        "status": "dry-run",
    }


def _layout_c_summary(
    routes: dict[str, dict[str, Any]], *, included: bool
) -> dict[str, Any]:
    if not included:
        return {
            "included": False,
            "requests": 0,
            "prompt": {
                "max_single_utf8_bytes": None,
                "aggregate_utf8_bytes": None,
            },
            "provider_reported": {
                "input_tokens_complete": False,
                "aggregate_input_tokens": None,
                "max_single_input_tokens": None,
            },
        }

    names = sorted(
        name for name in routes if name.startswith("suggest-layout-c-")
    )
    prompt_bytes = [routes[name]["prompt"]["utf8_bytes"] for name in names]
    token_values = [
        routes[name]["provider_reported"]["input_tokens"] for name in names
    ]
    tokens_complete = bool(token_values) and all(
        isinstance(value, int) for value in token_values
    )
    measured_tokens = [
        int(value) for value in token_values if isinstance(value, int)
    ]
    return {
        "included": True,
        "requests": len(names),
        "prompt": {
            "max_single_utf8_bytes": max(prompt_bytes) if prompt_bytes else None,
            "aggregate_utf8_bytes": sum(prompt_bytes) if prompt_bytes else None,
        },
        "provider_reported": {
            "input_tokens_complete": tokens_complete,
            "aggregate_input_tokens": (
                sum(measured_tokens) if tokens_complete else None
            ),
            "max_single_input_tokens": (
                max(measured_tokens) if tokens_complete else None
            ),
        },
    }


def measure(
    *,
    model: str,
    expected_provider: str,
    execute: bool = False,
    provider: _Provider | None = None,
    include_layout_c: bool = False,
    include_groups_a2: bool = False,
    expected_deepseek_thinking_mode: str | None = None,
) -> dict[str, Any]:
    """計測レポートを作成し、明示的に許可された場合だけプロバイダーを呼び出す。

    `expected_provider` と `model` は必須である。環境に偶然設定されていた別の
    プロバイダーやモデルへ、意図せず送信することを防ぐためである。CLIでは、
    二重の実行許可を確認した後にだけプロバイダーを解決する。
    """
    if not model.strip():
        raise ValueError("`model` には空でないモデルIDを指定してください")
    if not expected_provider.strip():
        raise ValueError("`expected_provider` にはプロバイダー名を指定してください")
    if (
        expected_deepseek_thinking_mode is not None
        and expected_deepseek_thinking_mode not in _DEEPSEEK_THINKING_MODES
    ):
        raise ValueError("DeepSeek thinking mode must be disabled or enabled")

    requests = build_representative_requests(
        model,
        include_layout_c=include_layout_c,
        include_groups_a2=include_groups_a2,
    )
    routes = {name: _route_row(req) for name, req in requests.items()}
    report: dict[str, Any] = {
        "measurement": "ai-route-provider-reported-input-tokens",
        "scenario": "300-cards-30-islands-ring",
        "expected_provider": expected_provider,
        "expected_model": model,
        "prompt_fingerprint": {"algorithm": "sha256", "encoding": "utf-8"},
        "provider_call_provenance": {"version": 1},
        "provider_input_provenance": {
            "version": 1,
            "deepseek_kind": "openai-chat-messages-v1",
            "algorithm": "sha256",
            "encoding": "utf-8",
        },
        "provider_generation_provenance": PROVIDER_GENERATION_PROVENANCE,
        "expected_deepseek_thinking_mode": expected_deepseek_thinking_mode,
        "executed": execute,
        "measurement_complete": False,
        "routes": routes,
        "layout_c_summary": _layout_c_summary(
            routes, included=include_layout_c
        ),
        "interpretation_boundary": (
            "正確なトークン数として採用するのは、プロバイダーが報告した `usage` だけとする。"
            "プロンプトのバイト数と文字数は診断情報であり、トークン数の推定には使わない。"
        ),
    }

    if not execute:
        return report
    if provider is None:
        raise ValueError("`execute=True` の場合はプロバイダーが必要です")
    if provider.provider_name != expected_provider:
        raise ValueError(
            "現在設定されているプロバイダーが、計測対象として指定したプロバイダー名と一致しません"
        )
    if provider.provider_kind == "deepseek":
        if expected_deepseek_thinking_mode not in _DEEPSEEK_THINKING_MODES:
            raise ValueError(
                "DeepSeek measurement requires an explicit expected thinking mode"
            )
        if settings.deepseek_thinking_mode != expected_deepseek_thinking_mode:
            raise ValueError(
                "configured DeepSeek thinking mode does not match the measurement expectation"
            )
    elif expected_deepseek_thinking_mode is not None:
        raise ValueError(
            "DeepSeek thinking mode expectation is only valid for a DeepSeek provider"
        )

    all_measured = True
    for route_name, req in requests.items():
        row = routes[route_name]
        try:
            response = provider.generate(req)
        except ProviderError as exc:
            row["status"] = "provider-error"
            row["provider_error"] = exc.to_contract()
            all_measured = False
            continue

        row["actual_provider"] = response.metadata.provider_name
        row["actual_provider_kind"] = response.metadata.provider_kind
        row["actual_model"] = response.metadata.model_id
        row["provider_call"] = response.metadata.as_audit_fields()
        if response.metadata.provider_kind == "deepseek":
            row["provider_input"] = {
                "kind": "openai-chat-messages-v1",
                "sha256": _openai_chat_messages_sha256(req),
            }
            row["provider_generation"] = {
                "thinking_mode": response.metadata.thinking_mode,
            }
        row["provider_reported"] = {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }

        if response.metadata.provider_name != expected_provider:
            row["status"] = "provider-mismatch"
            all_measured = False
        elif response.metadata.model_id != model:
            row["status"] = "model-mismatch"
            all_measured = False
        elif (
            response.metadata.provider_kind == "deepseek"
            and response.metadata.thinking_mode != expected_deepseek_thinking_mode
        ):
            row["status"] = "generation-mode-mismatch"
            all_measured = False
        elif response.input_tokens is None:
            row["status"] = "provider-did-not-report-usage"
            all_measured = False
        else:
            row["status"] = "measured"

    report["layout_c_summary"] = _layout_c_summary(
        routes, included=include_layout_c
    )
    report["measurement_complete"] = all_measured
    return report


def _opted_in() -> bool:
    return os.environ.get(OPT_IN_ENV, "").strip().lower() in _TRUE_VALUES


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        required=True,
        help="現在設定されているプロバイダーに期待する正確な `provider_name`（例: deepseek）。",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="すべての比較対象で共通して使用する正確なモデルID。",
    )
    parser.add_argument(
        "--deepseek-thinking-mode",
        choices=("disabled", "enabled"),
        default=None,
        help=(
            "Expected DeepSeek V4 thinking.type for this measurement. "
            "Required before executing a DeepSeek provider so an environment override "
            "cannot silently change the measured request mode."
        ),
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "合成した代表プロンプトを実際に送信する。"
            f"{OPT_IN_ENV}=1 も必要であり、指定しなければネットワークを使わないドライランとなる。"
        ),
    )
    parser.add_argument(
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


def main() -> int:
    args = _parser().parse_args()

    if not args.execute:
        print(
            json.dumps(
                measure(
                    model=args.model,
                    expected_provider=args.provider,
                    execute=False,
                    include_layout_c=args.include_layout_c,
                    include_groups_a2=args.include_groups_a2,
                    expected_deepseek_thinking_mode=args.deepseek_thinking_mode,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not _opted_in():
        print(
            json.dumps(
                {
                    "measurement": "ai-route-provider-reported-input-tokens",
                    "measurement_complete": False,
                    "status": "external-execution-not-opted-in",
                    "required_env": OPT_IN_ENV,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    provider = get_provider()
    try:
        report = measure(
            model=args.model,
            expected_provider=args.provider,
            execute=True,
            provider=provider,
            include_layout_c=args.include_layout_c,
            include_groups_a2=args.include_groups_a2,
            expected_deepseek_thinking_mode=args.deepseek_thinking_mode,
        )
    except ValueError as exc:
        print(
            json.dumps(
                {
                    "measurement": "ai-route-provider-reported-input-tokens",
                    "measurement_complete": False,
                    "status": "configuration-mismatch",
                    "message": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["measurement_complete"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
