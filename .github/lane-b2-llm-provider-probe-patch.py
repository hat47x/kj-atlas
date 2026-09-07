from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
TEST = ROOT / "01_Plans/tests/test_llm_provider_probe_contract.py"

old = "| `KJ_ATLAS_LLM_PROVIDER` | `none` | LLM provider 種別。`none`, `local`, `local_http`, `large-scale`, `large_scale`, `external`, `deepseek`。起動時fail-fastの対象となる**プロセス既定/フォールバック transport**であり、`model` を指定しないAI呼び出しに使う。AI-MODEL-GOVERNANCE-03以降、`model` を指定するAI呼び出しはmodel自身のregistry上の `providerKind` へ動的dispatchするため、この値と一致しないproviderへも（その `providerKind` 自身の設定が完全なら）到達し得る。`none` は無条件のkill switchであり、この場合は動的dispatchを含め一切のAI呼び出しを行わない | direct / base Compose | 通常値 | 起動ログまたは `/healthz` で provider 名（値のみ）を確認する |"
new = "| `KJ_ATLAS_LLM_PROVIDER` | `none` | LLM provider 種別。`none`, `local`, `local_http`, `large-scale`, `large_scale`, `external`, `deepseek`。起動時fail-fastの対象となる**プロセス既定/フォールバック transport**であり、`model` を指定しないAI呼び出しに使う。AI-MODEL-GOVERNANCE-03以降、`model` を指定するAI呼び出しはmodel自身のregistry上の `providerKind` へ動的dispatchするため、この値と一致しないproviderへも（その `providerKind` 自身の設定が完全なら）到達し得る。`none` は無条件のkill switchであり、この場合は動的dispatchを含め一切のAI呼び出しを行わない | direct / base Compose | 通常値 | `GET /ai/provider-status` の `providerKind` で実際に解決されたcanonical runtime kindを確認する。aliasは `local_http`→`local`、`large_scale`/`external`→`large-scale`。`/healthz` はliveness-onlyでproviderを返さない |"

raw = REGISTRY.read_bytes()
old_b = old.encode("utf-8")
new_b = new.encode("utf-8")
count = raw.count(old_b)
if count != 1:
    raise SystemExit(f"expected exactly one LLM provider backend row, got {count}")
REGISTRY.write_bytes(raw.replace(old_b, new_b, 1))

TEST.write_text(
    '''from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
AI_ROUTE = ROOT / "03_Implement/backend/src/kj_atlas_api/routes/ai.py"
PROVIDER = ROOT / "03_Implement/backend/src/kj_atlas_api/llm/provider.py"
KEY = "KJ_ATLAS_LLM_PROVIDER"


def _backend_row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows: list[str] = []
    in_backend = False
    for line in text.splitlines():
        if line == "## Backend settings":
            in_backend = True
            continue
        if in_backend and line.startswith("## "):
            break
        if in_backend and line.startswith(prefix):
            rows.append(line)
    if len(rows) != 1:
        raise AssertionError(f"expected one backend row for {key}, got {len(rows)}")
    return rows[0]


class LlmProviderProbeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.ai_route = AI_ROUTE.read_text(encoding="utf-8")
        self.provider = PROVIDER.read_text(encoding="utf-8")

    def test_registry_uses_provider_status_instead_of_healthz_or_startup_log(self) -> None:
        row = _backend_row(self.registry, KEY)
        self.assertIn("GET /ai/provider-status", row)
        self.assertIn("providerKind", row)
        self.assertIn("canonical runtime kind", row)
        self.assertNotIn("起動ログまたは `/healthz`", row)

    def test_provider_status_reports_the_resolved_runtime_kind(self) -> None:
        self.assertIn('@router.get("/provider-status", response_model=ProviderStatusResponse)', self.ai_route)
        self.assertIn("providerKind=get_provider().provider_kind", self.ai_route)

    def test_documented_aliases_match_the_runtime_registry(self) -> None:
        row = _backend_row(self.registry, KEY)
        self.assertIn("`local_http`→`local`", row)
        self.assertIn("`large_scale`/`external`→`large-scale`", row)
        self.assertIn('registry.register("local", LocalProvider, aliases=("local_http",))', self.provider)
        self.assertIn('registry.register("large-scale", LargeScaleProvider, aliases=("large_scale", "external"))', self.provider)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)
