# Issue: OPS-LLM-COST-01 LLMコスト統制とレート制限が文書のみで未実装

- Type: Operations / Process
- Status: Open
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `02_Architecture/llm_escalation_policy.html`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `04_Documentation/operations.md`
- Related ADR/Spec: `02_Architecture/llm_escalation_policy.html`, `01_Plans/adr/ADR-0009-local-llm-integration.md`, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`（Proposed）
- Expected verification level: `unit`

## 課題

`02_Architecture/llm_escalation_policy.html` §03（コスト制御）はこう定めている。

> 月次または環境別の外部呼び出し上限（回数/トークン）を定義する。上限到達時は**自動でローカル専用モードに降格**する。運用ダッシュボードで、ローカル成功率・エスカレーション率・失敗率を監視する。

**この契約は一切実装されていない。**

- 呼び出し回数カウンタ: 無し
- トークン計上: 無し（`grep -n "token_count\|usage\|quota\|budget" llm/provider.py` → 該当なし）
- 上限到達時の自動降格: 無し
- 監視用メトリクス: 無し

全backend APIにrate limitがない問題も同時に発見されたが、これはLLM費用の計測・予算と責務、key、対象routeが異なる。`SEC-RATE-LIMIT-01`を正本とし、本issueでは扱わない。

## 影響

- **予算統制**: 外部LLM（`KJ_ATLAS_LLM_PROVIDER=large-scale`）は従量課金である。上限が無いため、暴走クライアント・ループ・意図的濫用のいずれでもコストが青天井になる。企業・行政の調達では、コスト上限が技術的に担保されていることが要件になる場合がある。
- **文書の信頼性**: 「上限到達時は自動でローカル専用モードに降格する」と読んだ運用担当者は、そのガードが働くと期待して外部LLMを有効化する。実際には働かない。

## 対応方針（実装者向け）

本issueは範囲が広いため、**分割して段階実施**することを推奨する。文書の記述が過大である点だけでも先に解消できる。

### 段階1（低コスト・先行可能）: 文書と実態の整合

`llm_escalation_policy.html` §03 を、実装済みの内容と未実装の計画に区別して書き分ける。「自動降格する」という断定を、未実装であれば計画として明示する。**これだけでも運用者の誤解は防げる。**

### 段階2: 計測

- LLM 呼び出し回数・トークン数（provider が返す場合）を計上する。
- `ADR-0050` D1 が導入した provider 可視化と接続する余地がある。

### 段階3: 上限と降格

- 上限値の設定キー（`KJ_ATLAS_*` 命名規約に従う）を定義し、`02_Architecture/runtime_parameter_registry.md` へ登録する。
- 上限到達時の挙動を決める。「ローカル専用へ降格」は `llm_fallback_to_none` / provider 切替との関係整理が要る。降格が SafeMode や proposal-only の境界を弱めないこと。

段階2は`ADR-0050` D3が未配線としているprovider `usage`契約の採択を待つ。段階3は集計scope、共有store、hard/soft limit、fallback semanticsという別の設計判断を含むため、段階2の実測を得てから補足ADRの要否を判断する。

## 受入条件

- [x] AC-1（段階1）: `llm_escalation_policy.html` §03 の記述が、実装済み機能と未実装の計画を区別している。未実装の断定表現が残っていない。
- [~] AC-2（段階2・部分→拡充）: **呼び出し回数**は計測・参照可能になった（OPS-LLM-COST-01 段階2・iteration 54）— `llm/provider.py` にプロセス内カウンタ（provider種別別＋total）を追加し `generate_with_fallback` で計上。`GET /ai/provider-status` の `callCounts` から参照可能（単一プロセス前提。共有ストアは段階3）。**トークン数**も計上開始（2026-08-16）— `LLMResponse` に `input_tokens`/`output_tokens` を追加し、OpenAI互換 `usage`（DeepSeek等）を解析してプロセス内で蓄積、`GET /ai/provider-status` の `tokenUsage`（provider種別別＋total）から参照可能。usage未報告providerは0計上。欠損時の区別（AC-4）と共有store（AC-6）は段階3。
- [ ] AC-3（段階3以降）: 上限設定と到達時挙動が実装され、テストで固定されている。降格時も SafeMode / proposal-only 境界が維持される。
- [ ] AC-4: 計測値がprovider自己申告値かlocal tokenizer推定値かを区別し、provider／model／task／tenant等の集計scopeと欠損時挙動が一意である。prompt／response本文、生token、個人識別子をmetricへ保存しない。
- [ ] AC-5: 上限設定と到達時挙動に新規設定キーを使う場合、`02_Architecture/runtime_parameter_registry.md`、設定model、起動時validation、運用文書を同期する。
- [ ] AC-6: 複数workerで同じ予算を共有し、同時requestのreserve／settleが上限を超えて外部providerを呼ばない。共有store不達時は外部呼出しを許可する側へfallbackしない。
- [ ] AC-7: 全backend APIのrate limitは`SEC-RATE-LIMIT-01`で扱い、本issueへ重複実装・重複ACを作らない。

## 依存関係

- `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`（D3 `usage`契約の採択が前提）

### 連携（依存ではない）

- `01_Plans/issues/issue-SEC-RATE-LIMIT-01-backend-api-has-no-rate-limiting.md`（全API rate limit。費用台帳とは独立に判断する）

## 検証

- `python -m pytest tests/ -k "llm or provider" -q`
- `python 01_Plans/docs_check.py`

## 進捗（2026-08-11）

- 段階1を完了。現行保証をprovider既定無効、外部opt-in、要求／応答bytes、要求単位max output tokensに限定し、回数・実使用token計測、予算上限、自動降格、dashboardは未実装計画と明記した。
- 段階2以降は共有計数store、集計scope、provider usageの信頼境界を決める必要があるためOpenを維持する。全API rate limitは`SEC-RATE-LIMIT-01`へ分離した。

## 進捗（2026-08-16）: 段階2の計測を完了し、政策文書へ反映

- **段階2（計測）を実装**: 呼出回数（`callCounts`・既存）に加え、**入力/出力token計測（`tokenUsage`）**を実装（`LLMResponse.input/output_tokens`・`_record_llm_usage`・DeepSeek等のOpenAI互換`usage`解析・`/ai/provider-status`で参照可能）。単一プロセス前提（共有storeは段階3）。
- **政策文書の整合（段階1の継続）**: `llm_escalation_policy.html` §03 を更新し、現行実装に「プロセス内の呼出回数・token計測」を追記。未実装計画は予算上限・local-only降格・dashboard・共有計数storeへ限定し、運用者が計測済みと未実装を誤解しないようにした。
- 段階3（上限・降格・共有store・AC-3/AC-4/AC-6）は設定値と共有storeの設計判断が必要なため、引き続きOpen。
