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
import json
import os
from typing import Any, Protocol

from kj_atlas_api.llm.provider import (
    LLMRequest,
    LLMResponse,
    ProviderError,
    get_provider,
)
from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import CheckNarrativeRequest, GenerateNarrativeRequest
from kj_atlas_api.routes.ai import (
    _build_generate_narrative_prompt,
    _build_narrative_check_prompt,
    _build_prompt,
    _generate_narrative_ir,
    _suggest_layout_ir,
)
from scripts.measure_ai_route_prompt_coverage import representative_document

OPT_IN_ENV = "KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN"
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


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


def build_representative_requests(model: str) -> dict[str, LLMRequest]:
    """同じ決定論的な代表入力から、比較対象となる3つのプロンプトを生成する。"""
    doc = representative_document(include_evidence=False)

    layout_payload = SuggestLayoutRequest.model_validate({"doc": doc})
    layout_ir = _suggest_layout_ir(layout_payload)
    layout_prompt = _build_prompt(layout_payload, layout_ir)

    narrative_payload = GenerateNarrativeRequest.model_validate({"doc": doc})
    narrative_ir = _generate_narrative_ir(narrative_payload)
    narrative_prompt = _build_generate_narrative_prompt(narrative_payload, narrative_ir)

    check_payload = CheckNarrativeRequest.model_validate(
        {
            "doc": doc,
            "narrativeText": _representative_check_narrative_text(doc),
        }
    )
    check_prompt = _build_narrative_check_prompt(check_payload)

    return {
        "suggest-layout": LLMRequest(
            task="re_layout",
            prompt=layout_prompt,
            inputs=layout_ir,
            temperature=0.0,
            # 入力トークン数の測定には、実質的な回答本文は不要である。
            # プロバイダー層が受理する最小値まで出力上限を下げ、費用と待ち時間を抑える。
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
            # 現行production routeを忠実に再現する。check-narrativeはまだ
            # generic Document IR / route固有structured inputへ移行していない。
            prompt=check_prompt,
            inputs=None,
            temperature=0.0,
            max_tokens=1,
            model=model,
        ),
    }


def _route_row(req: LLMRequest) -> dict[str, Any]:
    return {
        "task": req.task,
        "prompt": {
            "unicode_chars": len(req.prompt),
            "utf8_bytes": len(req.prompt.encode("utf-8")),
        },
        "ir": {
            "cards": len((req.inputs or {}).get("cards", [])),
            "relations": len((req.inputs or {}).get("relations", [])),
            "islands": len((req.inputs or {}).get("islands", [])),
            "coordinates": len((req.inputs or {}).get("coordinates", [])),
            "truncation": (req.inputs or {}).get("truncation"),
        },
        "provider_reported": {
            "input_tokens": None,
            "output_tokens": None,
        },
        "status": "dry-run",
    }


def measure(
    *,
    model: str,
    expected_provider: str,
    execute: bool = False,
    provider: _Provider | None = None,
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

    requests = build_representative_requests(model)
    routes = {name: _route_row(req) for name, req in requests.items()}
    report: dict[str, Any] = {
        "measurement": "ai-route-provider-reported-input-tokens",
        "scenario": "300-cards-30-islands-ring",
        "expected_provider": expected_provider,
        "expected_model": model,
        "executed": execute,
        "measurement_complete": False,
        "routes": routes,
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
        elif response.input_tokens is None:
            row["status"] = "provider-did-not-report-usage"
            all_measured = False
        else:
            row["status"] = "measured"

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
        help="3つの代表ルートで共通して使用する正確なモデルID。",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "合成した代表プロンプトを実際に送信する。"
            f"{OPT_IN_ENV}=1 も必要であり、指定しなければネットワークを使わないドライランとなる。"
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
