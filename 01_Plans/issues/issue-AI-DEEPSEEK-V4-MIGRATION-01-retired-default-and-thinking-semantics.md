# Issue: AI-DEEPSEEK-V4-MIGRATION-01 退役DeepSeek既定modelとV4 thinking semanticsを移行する

- Type: Bug / Compatibility / Contract
- Status: Open
- Lifecycle: Draft -> Open
- Source Issue: `AI-IR-SCALE-01` R44（2026-09-05の公式DeepSeek資料再確認）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, model registry seed/docs/tests
- Related Backlog: `AI-DEEPSEEK-V4-MIGRATION-01`
- Related ADR/Spec: `02_Architecture/llm_provider_spec.md`, `02_Architecture/runtime_parameter_registry.md`, `ADR-0065`
- Expected verification level: integration（外部API実行は別途明示opt-in）

## 課題

KJ Atlasの `KJ_ATLAS_DEEPSEEK_MODEL` 既定値は現在も `deepseek-chat` である。DeepSeek公式Change Logは2026-04-24に `deepseek-chat` / `deepseek-reasoner` を2026-07-24で廃止すると告知し、2026-09-05時点のQuick Start / Chat CompletionsはV4 model IDを現行値として扱っている。このため、DeepSeek providerを既定設定で使う運用はvendor側model lifecycleと不整合になっている。

ただし旧 `deepseek-chat` はV4移行期間中に `deepseek-v4-flash` の**non-thinking**相当へ対応づけられていた一方、現行V4はthinking/non-thinkingを明示的に持つ。model文字列だけを `deepseek-v4-flash` へ置換すると、transportが `thinking` を送っていない現状ではvendor既定modeへ挙動が変わり、費用・latency・structured output特性まで暗黙に変える可能性がある。したがってmodel ID更新とthinking semanticsの決定を一体で行う。

## 対応方針

- 現行公式model IDへ既定値を移す。候補は一般用途の `deepseek-v4-flash` を第一候補とするが、単純文字列置換だけでは完了としない。
- 旧 `deepseek-chat` のnon-thinking性をproduction既定で維持するか、V4のthinking既定へ移行するかを明示し、transport payload・task routing・cost/latencyへの影響を回帰で固定する。
- `KJ_ATLAS_LLM_TASK_MODEL_MAP` / `KJ_ATLAS_LLM_HIGH_REASONING_MODEL` / request overrideの優先順位を変えない。
- env seed / registry例 / runtime parameter registry / configuration / active operational scriptsを現行model IDへ同期する。
- 過去のDone issue、dated dogfood実API結果、当時のmodel IDを示す履歴資料は書き換えない。
- 実DeepSeek API確認を行う場合は、credentialと外部費用を伴うため明示opt-inで別途実施する。

## 受入条件

- [ ] DeepSeek providerの既定model IDが2026-09-05時点の公式supported modelに一致する。
- [ ] thinking/non-thinkingのproduction既定が仕様として明示され、transport payloadの回帰で固定される。
- [ ] task model map / high-reasoning model / request overrideの既存優先順位を維持する。
- [ ] env model registry seedとoperator向け登録例が新しい既定model IDに整合する。
- [ ] active configuration/spec/evaluation scriptsに退役aliasを既定値・推奨値として残さない。
- [ ] dated historical evidenceに記録された旧model IDは改変しない。
- [ ] SafeMode、proposal-only、防PII、provider allowlist/audit境界を弱めない。

## 検証計画

- DeepSeek provider/settings/model-governance近接testを実行する。
- request payload testでmodel IDとthinking modeの明示契約を確認する。
- repo内 `deepseek-chat` / `deepseek-reasoner` inventoryを再取得し、残存が歴史資料または意図的互換testだけであることを分類する。
- 外部APIを呼ばない回帰を先行し、実API確認は明示opt-in時のみ行う。

## 公式資料provenance（2026-09-05確認）

- `https://api-docs.deepseek.com/updates` — 2026-04-24 entryでlegacy aliasの2026-07-24廃止を告知。
- `https://api-docs.deepseek.com/` — 現行Quick StartでV4 model IDsを列挙。
- `https://api-docs.deepseek.com/quick_start/pricing` — V4 Flash/Proとcontext `1M` を掲載。

