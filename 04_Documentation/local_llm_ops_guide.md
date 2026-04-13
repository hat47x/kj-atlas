# Local LLM Operations Guide

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部運用者（閉域/企業）
> Goal: provider切替と安全運用の最小runbookを提供する。
> Non-goal: 組織固有の承認フロー、秘密情報、内部検討ログの公開。
> Public boundary: 公開可能な設定・確認手順のみを記載し、内部監査詳細は除外する。
> Outcome: provider切替、safeMode境界、最小監査確認を再現できる。
> Related: `02_Architecture/llm_provider_spec.md`, `02_Architecture/runtime_parameter_registry.md`, `01_Plans/documentation_quality.md`, `01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。

## 0. Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されている。
2. SafeMode既定ON・share/export漏えい防止を後退させる記述がない。
3. 内部監査詳細や組織固有の承認ログを本文に含めていない。

いずれか未充足なら「No-Go」として公開更新を停止し、`01_Plans/issues/` へ論点を分離する。

## 1. 運用モード

- Offline: `KJ_ATLAS_LLM_PROVIDER=none`（既定、外部送信なし）
- Intranet: `KJ_ATLAS_LLM_PROVIDER=local`（社内LLMのみ）
- Enterprise: local中心 + 必要時のみ人手承認で外部経路

## 2. 最小設定

```bash
export KJ_ATLAS_LLM_PROVIDER='none'   # default
# local利用時のみ
export KJ_ATLAS_LLM_PROVIDER='local'
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
```

確認:

```bash
curl -fsS http://localhost:8000/healthz
```

## 3. safeModeと漏えい防止

- `safeMode` は export/share で既定ON。
- safeMode時、analytics/exportに生カードテキストを含めない。
- LLM出力を保存する場合も、禁止領域では原文を残さず要約/マスク化を行う。
- MVPではPII項目（author/timeなど）は保存対象外。将来拡張時に再評価する。

---

## 4. CE4 API/CLI 監査統合手順（query/bundle/proposal/apply）

Phase 1〜6 を通じて、API/CLI/GUI 同値性と監査4点セット（`query/bundle/proposal/apply`）を固定契約として扱う。

CE4実行フェーズは `Read → ADR CDC → Plan → Execute → Verify → Proceed` の固定順序で運用し、各フェーズで `equivalenceKey + bundleHash` のAND条件を再確認する。


### 4.0 CE Contract gate（Stream B固定契約の運用反映）

- Query Preview gate: `previewConfirmed=true` が無い `context-query` は運用上も失敗（`422 preview_required`）として扱う。
- Proposal gate: AI出力は常に `proposalId/diff/sourceBundleHash/status/reviewState` を満たす patch 提案のみ許可する。
- Review gate: AIによる `unreviewed -> reviewed` 自動遷移は禁止し、検知時は `status=held` で停止する。
- Safety gate: safeMode 既定ON時は未レビュー本文の投入・外部送信を禁止する。

### 4.1 運用前提（依存切離し）

- CE3完了待ちはしない。
- `sourceBundleHash` は `mock:<hash>` を許容し、監査導線と同値性導線の検証を継続する。
- 同値性判定は常に `equivalenceKey + bundleHash` の AND 条件で行う（値種別による例外なし）。

### 4.2 API/CLI/GUIの共通監査項目

`POST /docs/{docId}/context-audit` は次の4操作を `eventType` として記録する。

- `query`
- `bundle`
- `proposal`
- `apply`

API/CLI/GUI いずれの経路でも、以下の監査項目を同一キーで残す。

- `equivalenceKey`
- `bundleHash`
- `dryRun`
- `sideEffect`
- `sourceBundleHash`
- `rejectReasonCode`
- `command`
- `channel`（`api` / `cli` / `gui`）
- `schemaVersion`（CE4契約期間は固定値）

必須バリデーション（CE4固定）:
- `equivalenceKey` と `bundleHash` はともに 64桁hex を必須とする。
- `queryHash` を送る場合は `equivalenceKey` と同値でなければならない。
- `sourceBundleHash` は `mock:<64桁hex>` または本番 `64桁hex` のみ許容する。
- `operation` と `command` は固定マッピング（`query↔context-query`, `bundle↔context-bundle`, `proposal↔proposal-diff`, `apply↔apply|apply --dry-run`）に一致しなければならない。
- `operation=apply` は常に `dryRun=true` を必須とし、`dryRun=false` は契約違反として失敗扱いにする。
- `dryRun=true` の場合、`sideEffect=none` 以外は契約違反として失敗扱いにする。
- `dryRun=true` の場合、DB永続化・外部送信・`reviewState` 昇格（`unreviewed -> reviewed`）は全て禁止する。

CE4運用期間の固定値:
- `schemaVersion="ce4.audit.v1"`
- `eventType` は `query | bundle | proposal | apply` 以外を許容しない。

### 4.3 実施手順（最小runbook）

1. APIで `context-query` と `context-bundle` を実行し、`equivalenceKey` と `bundleHash` を取得する。
2. CLIで同一入力の `context-query` と `context-bundle` を実行し、`equivalenceKey` と `bundleHash` が一致することを確認する。
3. GUIで同一入力を実行し、API/CLIと `equivalenceKey` と `bundleHash` が一致することを確認する。
4. API/CLI/GUIで `proposal-diff` を実行し、`sourceBundleHash`（本番値または `mock:<hash>`）を記録する。
5. API/CLI/GUIで `apply --dry-run` を実行し、`dryRun=true` かつ `sideEffect=none` を確認する。
6. 監査ログで `query/bundle/proposal/apply` の4イベントが揃っていることを確認する。

### 4.4 契約整合チェック（`mock:<hash>` / 本番hash）

1. `sourceBundleHash=mock:<hash>` で 4.3 を実施し、同値性判定と監査4点セットが成立することを確認する。
2. `sourceBundleHash=<prod_sha256>`（64桁hex）で 4.3 を実施し、同一の判定条件で成立することを確認する。
3. 1 と 2 で監査キー集合（`equivalenceKey`, `bundleHash`, `dryRun`, `sideEffect`, `sourceBundleHash`, `channel`, `schemaVersion`）に差がないことを確認する。
4. 差がある場合は契約ドリフトとして CE4 作業を停止し、共通契約へ修正を戻す。

### 4.5 監査欠落の検知・通知

欠落判定は「同一 `equivalenceKey` で `query/bundle/proposal/apply` が揃っているか」で行う。

- 検知条件: 上記4イベントのいずれかが欠落。
- 一次対応: 欠落した操作を再実行し、`equivalenceKey` を維持したまま再送する。
- 通知: Platform Operator が当日中に運用チャネルへ「欠落操作・equivalenceKey・再実行結果」を報告する。
- 是正: 2回連続で同一欠落が発生した場合、CLI/APIの片系実装差分を停止し、共通実行ライブラリへ集約する。
- 判定原則: ログ欠損を成功扱いしない（fail-closed）。
- 判定原則: `dryRun=true` で `sideEffect=none` を満たさない場合も成功扱いしない（fail-closed）。

`rejectReasonCode` の最小分類（固定）:
- `missing_event`（4点セット欠損）
- `equivalence_mismatch`（`equivalenceKey + bundleHash` 不一致）
- `dry_run_side_effect`（`dryRun=true` かつ `sideEffect!=none`）
- `safemode_regression`（safeMode後退語彙/設定検知）

### 4.6 Verify → Proceed（3回自己修復上限）

- Verify で不整合を検出した場合、自己修復（再実行/設定補正/キー補完）は最大3回まで。
- 3回で解消しない場合は Proceed を停止し、論点を保留化する。
- 契約ドリフト（operation語彙差、監査キー差、`mock:<hash>` と本番hashでの判定差）を検知した場合は、回数に関わらず即停止する。
- 契約衝突（同一キーの複数定義）または未定義競合（必要キーの定義欠落）を検知した場合も、回数に関わらず即停止する。
- 監査4点セット（`query/bundle/proposal/apply`）の欠損は No-Go とし、補完完了まで成功扱いしない。

### 4.7 フェイルセーフ停止条件

以下を検知した場合、CE4運用を停止する。

1. 同値性定義の多義化
2. ログ欠損成功扱い
3. safeMode後退要求
4. Consensus 直書き要求（proposal/apply を迂回する直接更新）
5. Verify の自己修復が3回失敗した場合（4回目試行は禁止）
6. 前提崩れ（固定 operation または `equivalenceKey + bundleHash` 判定が成立しない）
7. 未定義競合（必須キー未定義、または同一キーの契約衝突）

### 4.8 Proceed引継ぎ記録（運用導線）

- 引継ぎ時は `equivalenceKey + bundleHash` 判定結果、`sourceBundleHash` の値種別（`mock:<hash>` / 本番hash）、`dryRun=true` と `sideEffect=none` の確認結果を同時に記録する。
- 運用日報には `channel`（`api|cli|gui`）別の実行結果と共通キー集合（`equivalenceKey`, `bundleHash`, `sourceBundleHash`, `dryRun`, `sideEffect`, `schemaVersion`）の差分有無を残す。
- 差分あり/自己修復3回超過/停止条件該当のいずれかを満たした場合、Proceedは実施せず、Issueへ保留論点として即時エスカレーションする。

### 4.9 docs-check（CE4契約整合）

```bash
rg -n "equivalenceKey|bundleHash|dryRun|sideEffect|sourceBundleHash|schemaVersion|rejectReasonCode|query|bundle|proposal|apply|fail-closed|前提崩れ|未定義競合|3回" \
  01_Plans/issues/issue-CE4-api-cli-audit-integration.md \
  02_Architecture/api.md \
  04_Documentation/local_llm_ops_guide.md
git diff --check
```

---

## 5. エスカレーション運用

### 5.1 既定

- 無効（disabled by default）。
- 無効時はローカル再試行または人手確認へ遷移。

### 5.2 有効化条件

- 設定で明示opt-inする。
- allowlist-only outbound を満たす。
- 送信前フィルタ（safeMode・最小化・不要メタ除去）を有効化する。

### 5.3 代表トリガ

- schema不一致
- 重要セクション欠落/短すぎ
- 否定関係があるのに反証記述欠落
- 入力規模閾値超過
- ルーブリックスコア閾値未達

---

## 6. テストと評価運用

- 毎回実行: unit + regression（fixture中心）
- 定期実行: curated integration（強モデル、小規模セット）
- 目的: 正解一致ではなく、有用性ゲート（構造・安全・根拠性）維持

- SafeMode既定ONを維持する。
- 未レビュー本文の自動確定を許可しない。
- AI出力は提案として扱い、確定は人手レビューで実施する。

## DOC-OPS-05 実行記録（Phase 1〜5）

### Phase 1 Read

- Audience / Goal / Public boundary / Related を確認し、公開境界と安全前提を再確認。

### Phase 2 Plan

- 本文は docs-only の範囲で更新し、仕様正本（00〜02）を上書きしない方針を固定。

### Phase 3 Execute

- Go/No-Go gate を追加し、公開判定を文書内で自己完結化。

### Phase 4 Verify

- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`

### Phase 5 Proceed

- 状態: **Ready**
- 次アクション: provider切替runbookと監査4点セットの公開境界を維持し、内部承認ログは 01_Plans 側で管理する。
