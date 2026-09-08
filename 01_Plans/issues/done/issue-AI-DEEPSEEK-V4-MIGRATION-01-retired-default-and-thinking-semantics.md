# Issue: AI-DEEPSEEK-V4-MIGRATION-01 退役DeepSeek既定modelとV4 thinking semanticsを移行する

- Type: Bug / Compatibility / Contract
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `AI-IR-SCALE-01` R44（2026-09-05の公式DeepSeek資料再確認）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, model registry seed/docs/tests
- Related Backlog: `AI-DEEPSEEK-V4-MIGRATION-01`
- Related ADR/Spec: `02_Architecture/llm_provider_spec.md`, `02_Architecture/runtime_parameter_registry.md`, `ADR-0065`
- Expected verification level: integration（外部API実行は別途明示opt-in）

## 課題

R44確認時点で、KJ Atlasの `KJ_ATLAS_DEEPSEEK_MODEL` 既定値は `deepseek-chat` だった。DeepSeek公式Change Logは2026-04-24に `deepseek-chat` / `deepseek-reasoner` を2026-07-24で廃止すると告知し、2026-09-05時点のQuick Start / Chat CompletionsはV4 model IDを現行値として扱っていた。このため、DeepSeek providerを既定設定で使う運用はvendor側model lifecycleと不整合になっていた。

ただし旧 `deepseek-chat` はV4移行期間中に `deepseek-v4-flash` の**non-thinking**相当へ対応づけられていた一方、現行V4はthinking/non-thinkingを明示的に持つ。model文字列だけを `deepseek-v4-flash` へ置換すると、vendor既定modeへ挙動が変わり、費用・latency・structured output特性まで暗黙に変える可能性がある。したがってmodel ID更新とthinking semanticsの決定を一体で行った。

## 対応方針

- 現行公式model IDへ既定値を移す。一般用途の `deepseek-v4-flash` を採用する。
- 旧 `deepseek-chat` のnon-thinking性をproduction既定で維持し、`KJ_ATLAS_DEEPSEEK_THINKING_MODE=disabled|enabled` として明示する。既定は `disabled` とする。
- `KJ_ATLAS_LLM_TASK_MODEL_MAP` / `KJ_ATLAS_LLM_HIGH_REASONING_MODEL` / request overrideの優先順位を変えない。
- env seed / registry例 / runtime parameter registry / configuration / active operational scriptsを現行model IDへ同期する。
- 過去のDone issue、dated dogfood実API結果、当時のmodel IDを示す履歴資料は書き換えない。
- 実DeepSeek API確認を行う場合は、credentialと外部費用を伴うため明示opt-inで別途実施する。

## 受入条件

- [x] DeepSeek providerの既定model IDが2026-09-05時点の公式supported modelに一致する。
- [x] thinking/non-thinkingのproduction既定が仕様として明示され、transport payloadの回帰で固定される。
- [x] task model map / high-reasoning model / request overrideの既存優先順位を維持する。
- [x] env model registry seedとoperator向け登録例が新しい既定model IDに整合する。
- [x] active configuration/spec/evaluation scriptsに退役aliasを既定値・推奨値として残さない。
- [x] dated historical evidenceに記録された旧model IDは改変しない。
- [x] SafeMode、proposal-only、防PII、provider allowlist/audit境界を弱めない。

## 対応結果（R45-R46、2026-09-05）

- R45 / PR #2979（merge `9862e0013fd27cfef091bd739d84dfe3282303b0`）で `KJ_ATLAS_DEEPSEEK_MODEL` 既定を `deepseek-v4-flash` へ移行した。
- `KJ_ATLAS_DEEPSEEK_THINKING_MODE=disabled|enabled` を追加し、旧既定のnon-thinking semanticsを維持するため `disabled` を既定とした。direct / registered DeepSeek Chat Completionsの双方で `thinking.type` を明示送信する。
- R45検証run `33964712805` でprovider/settings/model-governance/Lane B近接回帰 **139 passed / 4 deselected**、対象ruff、`git diff --check` を通過した。
- R46 inventory run `33970106106` で、active default/configとしての `deepseek-chat` / `deepseek-reasoner` 残存が0件であることを確認した。残存はmigration説明、dated Done/dogfood/monkey-test履歴、退役事実を説明するコメント、および当初は非本質的なtest fixtureだけだった。
- 非本質的なlegacy-alias test fixtureはR46でgeneric/current V4 IDへ整理した。run `33970198588` はbackend **66 passed**、frontend ModelSelector **6 passed**、ruff、active test-source alias grep、`git diff --check` を通過した。
- dated Done issue、2026-08-12 dogfood実API結果、2026-08-16 monkey-test log等の旧model IDは当時の証拠なので維持した。
- R45/R46は実DeepSeek APIを呼んでいない。外部API実行は本Issueの完了条件ではなく、credential・費用を伴うため明示opt-in境界を維持した。
- production cap、`AI-IR-SCALE-01` のA2/B/C選択、SafeMode、proposal-only、防PII、provider allowlist/audit契約は変更していない。

## 検証計画

- DeepSeek provider/settings/model-governance近接testを実行する。
- request payload testでmodel IDとthinking modeの明示契約を確認する。
- repo内 `deepseek-chat` / `deepseek-reasoner` inventoryを再取得し、残存が歴史資料またはmigration説明だけであることを分類する。
- active test fixtureから非本質的なlegacy aliasを除去し、backend/frontend近接回帰を実行する。
- issue memoを `Status: Done` と同時に `01_Plans/issues/done/` へmoveし、Done-at-root 0件契約を検証する。
- 外部APIを呼ばない回帰を先行し、実API確認は明示opt-in時のみ行う。

## 公式資料provenance（2026-09-05確認）

- `https://api-docs.deepseek.com/updates` — 2026-04-24 entryでlegacy aliasの2026-07-24廃止を告知。
- `https://api-docs.deepseek.com/` — 現行Quick StartでV4 model IDsを列挙。
- `https://api-docs.deepseek.com/quick_start/pricing` — V4 Flash/Proとcontext `1M` を掲載。
