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


## 0.1 AUTH-OPS-03 整合ゲート（運用責務）

- 承認フロー仕様の正本は `02_Architecture/strict_mode_exception_approval_flow.md`。
- 本書での実行責務は、役割語彙を `Security Officer / System Owner / Platform Operator` に統一し、承認（2者）と実行（Platform Operator）を分離して運用すること。
- strict mode 例外が関与する運用は D1〜D4 固定値（承認TTL=4h、最大2h、代理承認なし、48hレビュー+15m/60m）を必須チェックとする。
- 上記を満たせない場合は `StoppedForClarification` として停止し、設定変更を実施しない。

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

CE4実行フェーズは `Read → ADR CDC → Plan → Execute(同値性契約) → Verify(max3) → Proceed` の固定順序で運用し、各フェーズで `equivalenceKey + bundleHash` のAND条件を再確認する。


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
- 実行順序は `Plan -> Execute(同値性契約) -> Verify(max3) -> Proceed` を固定し、順序逆転（Verify前Proceed）を禁止する。
- CE3完了待ちは禁止し、`sourceBundleHash=mock:<hash>` の契約検証結果を Proceed 記録へ含める。

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

### 4.10 Stream E 実行ガード（2026-04-16 追補）

- フェーズは直列で運用し、各フェーズ冒頭で Read を実施する（`Read -> ADR CDC -> Plan -> Execute(同値性契約) -> Verify(max3) -> Proceed`）。
- CE3 完了待ちは禁止し、`sourceBundleHash=mock:<hash>` を許容して契約検証を継続する。
- 監査4点セット（`query/bundle/proposal/apply`）欠損は成功扱い禁止（fail-closed）。
- Verify の自己修復は最大3回まで。3回失敗時は即停止し、Proceedへ進まない。


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

## DOC-OPS-05 実行記録（Phase 1〜6）

### Phase 1 Read

- Audience / Goal / Public boundary / Related を確認し、公開境界と安全前提を再確認。

### Phase 2 ADR CDC

- Context: 本書は provider切替と監査4点セットの公開runbookであり、承認フロー仕様の正本ではない。
- Decision: `Read → ADR CDC → Plan → Execute(同値性契約) → Verify(max3) → Proceed` を固定順序として明文化する。
- Consequences: API/CLI/GUI 同値性と監査4点セットの運用確認が、公開文書のみで追跡可能になる。

### Phase 3 Plan

- 本文は docs-only の範囲で更新し、仕様正本（00〜02）を上書きしない方針を固定。

### Phase 4 Execute

- Go/No-Go gate を追加し、公開判定を文書内で自己完結化。

### Phase 5 Verify

- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`

### Phase 6 Proceed

- 状態: **Ready**
- 次アクション: provider切替runbookと監査4点セットの公開境界を維持し、内部承認ログは 01_Plans 側で管理する。



## Stream E 専属実行サイクル（Read → Plan → Execute → Verify → Proceed）

1. **Read**: `operations.md` / `release.md` / `local_llm_ops_guide.md` を再読し、D1〜D4・役割語彙・導線整合を確認する。
2. **Plan**: docs-only で3文書内の差分方針を固定する（越境編集を禁止）。
3. **Execute**: 役割分離（2者承認/実行責務分離）と fixed values の記述を同期する。
4. **Verify**: `rg` と `git diff --check` で語彙・固定値・体裁を検査し、自己修復は最大3回まで。
5. **Proceed**: Ready/Hold を判定し、停止条件（前提不整合・他ストリーム越境要求）に該当した場合は即停止する。

## Stream G docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **CDC**: Context / Decision / Consequences を明文化し、分類結果（Move internal / Improve external）を固定する。
3. **Plan**: AC/DoD を先に定義し、docs-only スコープ（`03_Implement/**` 非変更）を明示する。
4. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
5. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
6. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## Phase 1-5 execution record (2026-04-16, DOC-OPS-05-06/07/08/09/10 scope)

### Phase 1: Read
- 再Read: 本文冒頭メタ（Audience / Goal / Non-goal / Public boundary / Outcome / Related）と Requirement meta I/F を再確認。
- スコープ確認: 本タスクは「当該Issue本文 + 当該Scope文書」のみを編集対象とする。

### Phase 2: Plan
- 再Read: 関連ADR（特に ADR-0019）と `01_Plans/documentation_quality.md` の参照導線を再確認。
- 計画: Read → Plan → Execute → Verify → Proceed を単一サイクルで実施し、記録を追記する。
- フェイルセーフ: Verify 失敗時の自己修復は最大3回まで、4回目相当は停止。

### Phase 3: Execute
- 再Read: 直前差分と本文の禁止事項（SafeMode後退、公開境界逸脱）を再確認してから編集。
- 実施内容: 本セクションを追記し、Phase運用・再Read・修復上限ルールを明文化。

### Phase 4: Verify
- 再Read: 追記後の本文を再読し、語彙ドリフト・参照不整合・体裁崩れの有無を確認。
- 実施: `git diff --check` と対象ファイルの目視確認を実施。
- 修復回数: 0回（3回超過なし）。

### Phase 5: Proceed
- 再Read: Verify結果とスコープ逸脱の有無を再確認。
- 判定: **Ready**（docs-only、許可範囲内、停止条件なし）。
- 継続条件: 後続差分でも同じ5Phase + 再Read + 修復上限3回を維持する。

## Stream H 専任: DOC-OPS-05後半 実行記録（2026-04-16）

### Phase 1 Read

- 対象本文と関連正本（`00_Prompt/*` / `01_Plans/adr/ADR-0001` / `02_Architecture/*`）を再読し、公開境界を確認した。
- 用語・責務の整合（特に security 系は `Security Officer / System Owner / Platform Operator`）を事前確認した。

### Phase 2 Plan（AC/DoD補完）

- AC補完:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の冒頭メタを維持する。
  - 本文は docs-only で更新し、実装仕様・設定値の新規決定を持ち込まない。
  - 参照導線（関連文書・issue memo）を切断しない。
- DoD補完:
  - Read → Plan → Execute → Verify → Proceed の記録を残す。
  - Verify で `docs-check` とリンク整合を確認する。

### Phase 3 Execute

- 本文の方針を維持したまま、Stream H後半の実行責務（Phase運用・停止条件）を追記した。
- 編集範囲外（backend/frontendコード、shared統合3ファイル）は変更しない。

### Phase 4 Verify（docs-check + リンク整合）

- `rg` で必須メタ語彙・Phase見出し・停止条件語彙を確認した。
- `git diff --check` で体裁崩れがないことを確認した。
- security 系は D1〜D4 と役割語彙の整合を追加確認した。

### Phase 5 Proceed

- 判定: **Ready**
- 継続条件: 次回更新でも同一フェーズ順序と docs-only 制約を維持する。

### 停止条件（固定）

- 責務用語不整合（`Security Officer / System Owner / Platform Operator` の混在・崩れ）を検知した場合は停止。
- D1〜D4 固定値矛盾（`4h / 2h / 代理承認なし / 48h+15m/60m`）を検知した場合は停止。
- Verify の自己修復が3回を超える場合は `StoppedForClarification` として停止。

## Stream H docs群1 serial cycle (2026-04-18)

### Phase 1 Read
- 対象ファイルを再読し、`Audience / Goal / Non-goal / Public boundary / Outcome / Related` の整合を確認した。
- Scopeを docs-only に固定し、編集禁止対象（`security.md` / `security_operational_guidelines.md` / shared files）へ非接触であることを確認した。

### Phase 2 Plan
- 1Phase1責務で進行し、変更は「実行記録の同期」と「公開境界の維持」に限定する。
- AC/DoD不足があれば先に補完提案し、未合意の新規仕様決定は持ち込まない。

### Phase 3 Execute（1ファイル直列）
- Classification: **Improve external**
- 04_Documentation/local_llm_ops_guide.md は公開運用runbookと非公開境界を分離したまま維持する。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。

## DOC-OPS-05 Stream J2 execution record (2026-04-18)

### Phase 1: Read
- Target issue scope and this document were re-read to confirm Audience / Goal / Public boundary.
- Classification remains **Improve external** and no Stream H-owned file edits are required.

### Phase 2: ADR CDC
- CDC update is **not required** because the existing placement policy is within current DOC-OPS-05 decisions.

### Phase 3: Plan
- AC/DoD補足: 分類根拠（Audience/Goal/公開境界）・次アクション・検証一致（docs-check）を1セットで記録する。
- 次アクション固定: 公開可能なprovider切替手順のみを対象に改善を継続する。

### Phase 4: Execute
- docs-onlyで本ファイルのみを更新し、実装仕様変更は行わない。

### Phase 5: Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|DOC-OPS-05 Stream J2" 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`
- Self-correction policy: max 3 attempts, then stop and reassign if unresolved.

### Phase 6: Proceed
- 判定: **Ready**
- 根拠: 分類根拠・次アクション・検証一致を同一文書内で追跡可能。

## Stream J（DOC-OPS-05 中盤2）実行記録（2026-04-19）

### Phase 1 Read
- 開始時に対応Issueと本ドキュメントを再読し、Classification=**Improve external** と公開境界メタの有効性を確認。
- 変更範囲を `01_Plans/issues/issue-doc-ops-05-*`（担当4件）と本ドキュメントに限定。

### Phase 2 ADR CDC（必要時のみ）
- 判定: **不要**（既存の分類・公開境界・Go/No-Go方針は上流文書と整合）。

### Phase 3 Plan
- AC/DoD不足の補完方針:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の再確認結果を記録。
  - Verify は docs-check（`rg` / issue memo validator / `git diff --check`）で実施。
  - Verify失敗時は自己修復を最大3回まで許容し、4回目相当は停止して判断依頼。

### Phase 4 Execute
- docs-only 追記を実施。既存手順・分類方針は維持し、実装仕様やコード変更は行わない。

### Phase 5 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream J（DOC-OPS-05 中盤2）" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**。
- 引き継ぎ: 次担当は各Phase開始時に issue/doc の再読を継続し、競合・前提崩壊・3回超過時は即停止する。


## Stream H serial cycle（2026-04-19 / DOC-OPS-05-09）

### Phase 1 Read（参照整合）
- 対象Issueと本文を照合し、Classification=Improve external と公開境界（Audience / Goal / Non-goal / Outcome / Related）の整合を確認。
- 重複・矛盾は既存本文へ統合し、新規仕様追加は行わない。

### Phase 2 Plan（AC/DoDドラフト）
- AC: 公開境界メタの維持、Issue分類との一致、docs-onlyスコープ維持。
- DoD: Read→Plan→Execute→Verify→Proceed を記録し、検証コマンドを再現可能に残す。

### Phase 3 Execute（本文更新）
- 本節を追記し、Stream H の担当範囲であることを明示。
- 編集範囲は本ファイルのみとし、他ストリーム対象ファイルは非変更。

### Phase 4 Verify（docs-check + 参照リンク）
- `rg -n "Audience|Goal|Non-goal|Outcome|Related|Go/No-Go|Stream H serial cycle" 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`
- 参照リンクは `Related` に記載された正本/Issue導線が有効であることを目視確認。

### Phase 5 Proceed/Stop
- 判定: **Ready**
- 停止条件: Verify自己修復が3回を超過、または未定義競合（要件キー未定義/契約衝突）を検知した場合は **Stop** とし、`01_Plans/issues/` に保留論点を記録する。
