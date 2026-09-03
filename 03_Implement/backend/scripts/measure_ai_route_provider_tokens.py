#!/usr/bin/env python3
"""代表規模のAIルートについて、providerが報告した入力token数を測定する。

`AI-IR-SCALE-01` では、JSONのbyte数などから正確なtoken数を推定してはならない。
このスクリプトは、既存のscale coverage計測と同じ決定論的な300カード・30島の
入力を使って2種類の代表promptを生成し、明示的に指定したprovider/modelへ必要に
応じて送信する。正確な入力token数として採用するのはprovider自身が返したusage
だけである。

既定動作はdry-runであり、providerの生成も呼び出しも行わない。外部実行には
`--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の両方を必要とする。
送信するのは `representative_document()` が作る合成データだけであり、利用者の
実データは使わない。

比較対象は意図的に性質の異なる2ルートとする。

- `suggest-layout`: 移行済みルートのうち最重量。正規化座標、関係、島構造をIR文脈に含む。
- `generate-narrative`: 座標を使わない代表ルート。reading orderはDocument由来のまま、
  論理関係をIRから受け取る。

providerが入力token数を返さない場合は推定で補わない。出力には
`provider-did-not-report-usage` と `measurement_complete=false` を記録する。
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Protocol

from kj_atlas_api.llm.provider import LLMRequest, LLMResponse, ProviderError, get_provider
from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import GenerateNarrativeRequest
from kj_atlas_api.routes.ai import (
    _build_generate_narrative_prompt,
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


def build_representative_requests(model: str) -> dict[str, LLMRequest]:
    """同じ決定論的な代表入力から、比較対象となる2つのpromptを生成する。"""
    doc = representative_document(include_evidence=False)

    layout_payload = SuggestLayoutRequest.model_validate({"doc": doc})
    layout_ir = _suggest_layout_ir(layout_payload)
    layout_prompt = _build_prompt(layout_payload, layout_ir)

    narrative_payload = GenerateNarrativeRequest.model_validate({"doc": doc})
    narrative_ir = _generate_narrative_ir(narrative_payload)
    narrative_prompt = _build_generate_narrative_prompt(narrative_payload, narrative_ir)

    return {
        "suggest-layout": LLMRequest(
            task="re_layout",
            prompt=layout_prompt,
            inputs=layout_ir,
            temperature=0.0,
            # 入力token数の測定には実質的な回答本文は不要である。
            # provider層が受理する最小値まで出力上限を下げ、費用と待ち時間を抑える。
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
    """計測レポートを作り、明示的に許可された場合だけproviderを呼び出す。

    `expected_provider` と `model` は必須とする。環境に偶然設定されていた別の
    provider/modelへ黙って送信することを防ぐためである。CLIでは、二重の実行許可を
    確認した後にだけproviderを解決する。
    """
    if not model.strip():
        raise ValueError("modelには空でないmodel idを明示してください")
    if not expected_provider.strip():
        raise ValueError("expected_providerにはprovider名を明示してください")

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
            "正確なtoken数として採用するのはproviderが報告したusageだけとする。"
            "promptのbyte数・文字数は診断情報であり、token数の推定には使わない。"
        ),
    }

    if not execute:
        return report
    if provider is None:
        raise ValueError("execute=Trueの場合はproviderが必要です")
    if provider.provider_name != expected_provider:
        raise ValueError(
            "現在設定されているproviderが、計測対象として明示したprovider名と一致しません"
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
        help="現在設定されているproviderに期待する正確なprovider_name（例: deepseek）。",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="2つの代表ルートで共通して使用する正確なmodel id。",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "合成された代表promptを実際に送信する。"
            f"{OPT_IN_ENV}=1 も必要。指定しなければネットワークを使わないdry-runとなる。"
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
