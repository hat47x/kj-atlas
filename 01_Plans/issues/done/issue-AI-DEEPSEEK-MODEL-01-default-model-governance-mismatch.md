# Issue: AI-DEEPSEEK-MODEL-01 DeepSeekの既定モデルが統制層で拒否される

- Type: Bug / Contract
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のDeepSeek実APIモンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, `03_Implement/backend/tests/test_ai_eval_pipeline.py`
- Related Backlog: `AI-DEEPSEEK-MODEL-01`
- Related ADR/Spec: `02_Architecture/llm_provider_spec.md`, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`
- Expected verification level: `e2e`

## 課題

`KJ_ATLAS_LLM_PROVIDER=deepseek`かつ操作別model未指定の場合、routeのモデル統制は`default`を検査する一方、DeepSeek送信層だけが後から`deepseek-chat`へ置換していた。registryには`deepseek-chat`が正しく登録されていても、実API送信前に403 `model_not_registered`となり、既定設定の全AI操作が利用不能だった。既存の評価testは操作別model mapを明示していたため、この既定経路を覆えていなかった。

## 対応方針

- model解決の正本で、DeepSeek選択時の既定値を`KJ_ATLAS_DEEPSEEK_MODEL`へ確定する。
- model mapやrequest overrideの優先順位は変えない。
- 実API評価testは操作別mapなしの既定経路を固定する。

三要素牽制: 業務上は運用者が選択したDeepSeek既定モデルを追加指定なしで利用できる必要がある。データ上は既存registry IDの解決順だけを整合させ、prompt・応答・秘密情報の保存範囲を変えない。機能上は統制層と送信層が同じmodel IDを用いるようにし、allowlist、proposal-only、SafeModeを緩和しない。安全境界の変更ではないためADRは追加しない。

## 受入条件

- [x] DeepSeek設定かつmodel未指定で`deepseek-chat`が統制前に解決される。
- [x] request override、task map、高推論modelの既存優先順位が回帰しない。
- [x] 実DeepSeek APIでカード改善と島要約が200になる。
- [x] provider statusがDeepSeekのcall countとtoken usageを記録する。

## 対応結果（2026-08-16）

- `resolve_model_for_task`でDeepSeek provider既定値を統制前に解決するよう修正した。
- 操作別model mapで欠陥を覆っていた評価testを、mapなしの既定経路へ変更した。
- 隔離SQLite環境の実APIでカード改善1件と島要約1件を検証し、提案応答、島内grounding、利用量記録を確認した。

## 検証計画

- backendのprovider、AI評価、model governance近接testを実行する。
- 隔離SQLite + DeepSeek実APIでカード改善1件・島要約1件・provider statusを確認する。
- 実ブラウザでprovider表示とproposal-only導線を確認する。


## 配置の整理（2026-09-05）

- 本Issueは受入条件を満たし、実装・回帰確認・実API確認まで完了して `Done` となっていた一方、R18以前からの経緯により、完了済みのまま作業中Issueと同じルートへ残るlegacy集合に含まれていた。
- 既存のライフサイクル契約は、このlegacy集合を恒久的に残すための例外ではない。完了済みIssueを `01_Plans/issues/done/` へ移すたびに `LEGACY_DONE_AT_ROOT_BASELINE` も同じ変更で下げる、単調減少のラチェットである。
- 本変更ではDeepSeek対応の完了済みIssue 2件を正規配置へ移し、baselineを54から52へ縮小した。R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
