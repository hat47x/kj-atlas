# Local LLM Operations Guide

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部運用者（閉域/企業）
> Goal: ローカルLLM運用時の最小runbookを提供する。
> Outcome: 分類結果を **Improve external** に固定し、外部公開runbookとして再利用できる検証導線を提供する。
> Public boundary: 公開可能な運用条件と検証手順のみを記載し、秘密情報・内部承認ログ・組織固有手順は含めない。
> This document decides: provider切替手順、safeMode境界、最小監査確認。
> This document does not decide: 組織固有の承認フロー、秘密情報管理、内部監査ログの保管方式。
> Related: `02_Architecture/llm_provider_spec.md`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/strict_mode_exception_approval_flow.md`, `04_Documentation/operations.md`

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。

## 1. Go/No-Go gate（公開運用判定）

公開運用を開始してよいのは、次の条件をすべて満たす場合のみです。

1. SafeMode既定ONと share/export 漏えい防止を後退させない。
2. 役割語彙を `Security Officer / System Owner / Platform Operator` に統一する。
3. strict mode例外を扱う場合、D1〜D4（承認TTL=4h、最大2h、代理承認なし、48hレビュー+15m/60m）を満たす。
4. 本文に内部承認ログや秘密情報を含めない。

未充足の場合は `StoppedForClarification` として停止し、設定変更を実施しないでください。

## 2. 運用モード

- Offline: `KJ_ATLAS_LLM_PROVIDER=none`（既定、外部送信なし）
- Intranet: `KJ_ATLAS_LLM_PROVIDER=local`（社内LLMのみ）
- Enterprise: local中心 + 必要時のみ人手承認で外部経路

## 3. 最小設定（前提条件つき）

前提条件:

- APIサーバーが `http://localhost:8000` で起動している。
- ローカルLLMを使う場合、LLMエンドポイントが到達可能である。

```bash
export KJ_ATLAS_LLM_PROVIDER='none'   # default

# local利用時のみ
export KJ_ATLAS_LLM_PROVIDER='local'
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
```

疎通確認:

```bash
curl -fsS http://localhost:8000/healthz
```

失敗時対応:

- `curl` が失敗する場合は、API起動状態とポート競合を先に確認する。
- local provider だけ失敗する場合は、`KJ_ATLAS_LOCAL_LLM_BASE_URL` 到達性を確認する。

## 4. SafeMode と漏えい防止

- `safeMode` は export/share で既定ON。
- safeMode時は未レビュー本文のAI入力混入を許可しない。
- analytics/export に生カード本文を含めない。
- AI出力は提案として扱い、確定は人手レビューで行う。

## 5. 最小監査runbook（query/bundle/proposal/apply）

監査4点セット（`query/bundle/proposal/apply`）は、成功判定の必須条件です。

1. APIで `context-query` と `context-bundle` を実行し、`equivalenceKey` と `bundleHash` を取得する。
2. CLI/GUIで同一入力を実行し、`equivalenceKey + bundleHash` が一致することを確認する。
3. `proposal-diff` 実行時に `sourceBundleHash` を記録する（`mock:<hash>` 許容）。
4. `apply --dry-run` で `dryRun=true` かつ `sideEffect=none` を確認する。
5. 監査ログで `query/bundle/proposal/apply` が揃っていることを確認する。

必須バリデーション:

- `equivalenceKey` と `bundleHash` は 64桁hex。
- `operation=apply` は `dryRun=true` を必須とし、`dryRun=false` は失敗扱い。
- `dryRun=true` で `sideEffect!=none` は失敗扱い。

## 6. エスカレーション運用

- 既定は無効（disabled by default）。
- 有効化時は明示opt-in + allowlist-only outbound + 送信前フィルタを必須とする。
- 次の条件ではローカル再試行より先に人手確認へエスカレーションする。
  - schema不一致
  - 必須セクション欠落
  - 反証・留保の欠落

## 7. Verify / 停止条件

推奨チェック:

```bash
rg -n "Audience|This document decides|This document does not decide|safeMode|equivalenceKey|bundleHash|dryRun|sideEffect|query|bundle|proposal|apply" 04_Documentation/local_llm_ops_guide.md
git diff --check
```

停止条件:

- 上流正本（`02_Architecture/*`）との矛盾を検知。
- SafeMode後退要求を検知。
- Verify自己修復が3回を超過。

## 8. 実行フェーズ固定（Read → Plan → Execute → Verify → Proceed）

Local LLM 運用変更時は、次の順序を固定する。

1. **Read**: `llm_provider_spec.md` / `runtime_parameter_registry.md` / `operations.md` を再確認する。
2. **Plan**: 対象モード（Offline/Intranet/Enterprise）、変更対象の環境変数、監査4点セット確認方法を先に固定する。
3. **Execute**: 設定反映と疎通確認を実施し、コマンド結果を記録する。
4. **Verify**: `rg` と `git diff --check` で文書整合を確認する。
5. **Proceed**: Go/No-Go を明示し、未解決事項があれば次サイクルへ引き継ぐ。

フェイルセーフ:

- Verify失敗時の自己修復は **最大3回**。
- 3回で収束しない、または未定義競合を検知した場合は `StoppedForClarification` で停止する。


## 9. DOC-OPS Track 4 serial cycle（2026-04-22 / DOC-OPS-05-09）

### Phase 1 Read
- `AGENTS.md` Read Order、`02_Architecture/llm_provider_spec.md`、`02_Architecture/runtime_parameter_registry.md`、対応Issue（`issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`）を再読。
- Classification **Improve external** と公開境界（秘密情報・内部承認ログ非掲載）を確認。

### Phase 2 Plan
- 運用境界を `provider切替/safeMode境界/監査4点セット` の3点で固定。
- フェイルセーフは自己修復3回上限、超過時 `StoppedForClarification`。

### Phase 3 Execute
- 本Trackの実行記録を docs-only で追記。
- `safeMode` 既定ONと提案-only運用の記述は維持し、後退させない。

### Phase 4 Verify
- `rg -n "DOC-OPS Track 4 serial cycle|Improve external|safeMode|query|bundle|proposal|apply|StoppedForClarification" 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**
- 次アクション: 変数名追加/改名が必要な場合は `runtime_parameter_registry.md` を先に更新してから本書へ反映。

## Stream H serial execution（2026-04-26 / DOC-OPS-05-09）

### Phase 1 Read
- 対象Issue（`issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`）と本書を再読。

### Phase 2 ADR/CDC
- Context: 本書は外部向けrunbookとして有効だが、公開境界を超える内部情報の混在は不可。
- Decision: 分類は **Improve external** を維持し、LLM運用境界の説明に限定する。
- Consequences: 実装仕様や内部承認実務の新規追加は行わない。

### Phase 3 Plan
- docs-only / 最小差分で直列フェーズ記録のみ追加。

### Phase 4 Execute
- 本セクションを追加し、Issueとの整合ログを明示。

### Phase 5 Verify
- `rg -n "Stream H serial execution|Improve external|LLM運用境界|Phase 5 Verify" 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`
- 自己修復回数: 0/3。

### Phase 6 Proceed
- 状態: **Ready**（直列2Issue完了）。


## Stream G mini-Phase serial run（2026-04-27）

### Phase 1 Read
- 対応Issue（`DOC-OPS-05-09`）と本書の分類ヘッダを再読し、公開境界を確認。

### Phase 2 Plan
- 変更責務を docs-only の記録同期に限定し、本文の分類（Move internal / Improve external）を維持。
- 共通ACテンプレ（Scope固定 / 境界明示 / GoNoGo / docs-check / 3回上限）を適用。

### Phase 3 Execute
- 本節を追記し、Read→Plan→Execute→Verify→Proceed の直列実行証跡を固定。
- 指定外ファイル・実装コード・共有統合ファイルは未編集。

### Phase 4 Verify
- `rg -n "DOC-OPS|Classification|Audience|Goal|Public boundary|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`
- self-repair count: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（分類方針と公開境界を維持）。

## Stream E共通: Draft課題のOpen化条件（DOC-OPS-05）

- 本文書で扱う Draft 課題は、次の **5条件をすべて満たした場合のみ Open 化** する。
  1. **Read**: 対象本文書と上位根拠（00〜02、必要なADR）を再読し、参照差分を列挙済み。
  2. **Plan**: Scope / Non-Goals / Acceptance / Validation / Stop Conditions を明文化済み。
  3. **Execute**: docs-only 境界（実装コード非変更）を維持し、allowlist 外の差分が 0。
  4. **Verify**: 再現可能な docs-check コマンドと結果（成功/未実施理由）を記録済み。
  5. **Proceed**: Go/No-Go/Conditional を明示し、未確定事項を「決定」扱いせず次アクションに分離済み。
- 未確定事項は `TBD` / `Assumption` / `Decision Needed` で明示し、**承認前に仕様確定文へ昇格しない**。
- 自己修復（同一原因への再試行）は最大3回まで。4回目相当は Stop とし、Open 化を保留する。

### Stream E serial execution（2026-05-10 / CE4 API/CLI/Audit, proposal-only）

#### Phase 1 Read
- `ADR-0028` CE-4要件、`02_Architecture/api.md`、`04_Documentation/operations.md`、`04_Documentation/local_llm_ops_guide.md` を再読し、監査導線の共通語彙を確認。
- CE1契約は read-only 参照とし、`ContextQuery/ContextBundle` の contract freeze を変更しないことを確認。

#### Phase 2 ADR（Context / Decision / Consequences）
- **Context**: `query/bundle/proposal/apply` の監査4点セットは存在するが、API/CLI同値性判定と routing 監査キーの統一記述が分散している。
- **Decision**: CE4同値判定を `equivalenceKey AND bundleHash` に固定し、routing監査キー（`routingStage/provider/model/sourceBundleHash/proposalId`）を API/CLI共通必須観点として固定する。
- **Consequences**: 実装前でも docs-only で検証計画を統一でき、監査欠損時は fail-closed で停止判断可能になる。

#### Phase 3 Plan
- 受入条件:
  - [x] API/CLI双方で同値性判定キーと失敗分類が同一語彙で読める。
  - [x] 監査ログの必須イベント/必須キー/順序要件が operations / local LLM guide と整合する。
  - [x] routingStage 追跡不能時の Stop 条件を明文化する。
- 非目標:
  - 実装コード変更、契約型定義（CE0/CE1）変更、frontend変更。

#### Phase 4 Execute
- 本Issueに CE4統合方針（同値条件・監査キー・停止条件）を追記。
- API設計文書へ監査I/Fの統一節を追加。
- Operations / Local LLM guide へ API/CLI同値性検証計画の実行手順を追加。

#### Phase 5 Verify（API/CLI同値性検証計画）
- 検証計画（docs-contract）:
  1. 同一 canonical query で API/CLI それぞれ `query -> bundle -> proposal -> apply` を dry-run 実行。
  2. `equivalenceKey` と `bundleHash` の一致（AND条件）を確認。
  3. routing監査キー（`routingStage/provider/model/sourceBundleHash/proposalId`）が4イベントすべてで追跡可能か確認。
  4. 欠損・順序逆転・競合（同一キーで矛盾値）時は fail-closed で No-Go。
- 自己修復カウンタ: `0/3`。

#### Phase 6 Proceed / Stop
- **Proceed条件**: 4文書（Issue/API/operations/local_llm_ops）で同値判定・監査キー・停止条件が矛盾なく読解できること。
- **Stop条件**:
  1. 監査ログ欠落（4イベント欠損または必須キー欠損）。
  2. `routingStage` 追跡不能。
  3. 未定義競合（同一 `equivalenceKey` / `bundleHash` で矛盾結果）。
  4. 自己修復4回目相当（>3）。
