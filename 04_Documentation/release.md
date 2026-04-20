# リリース手順（最小）

> DOC-OPS-05 Classification: **Improve external**
> Audience: メンテナ・リリース担当者
> Goal: 最小リリース手順を公開し再現可能性を担保する。
> Non-goal: 組織内部の承認会議ログ・秘密鍵運用手順・未公開インシデント情報は扱わない。
> Public boundary: 内部承認履歴は除外し、公開可能な手順とチェックのみを残す。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Outcome: 外部読者が最小リリース手順と公開チェックを単独で追従できる。
> Related: `01_Plans/documentation_quality.md`, `.github/workflows/release.yml`, `01_Plans/issues/issue-doc-ops-05-12-04doc-release.md`

このドキュメントは、kj-atlas の最小リリース運用（バージョニング、タグ作成、リリースノート）を定義します。

## 1. バージョニング方針（SemVer）

バージョンは `MAJOR.MINOR.PATCH` 形式（例: `0.2.3`）を使います。

- `MAJOR`:
  - 互換性を壊す変更を含むとき
- `MINOR`:
  - 後方互換を保った機能追加
- `PATCH`:
  - 後方互換を保ったバグ修正・文言修正

## 1.5 公開ドキュメントの位置づけ（04_Documentation / Gist）

`04_Documentation/` は、対外的なユーザ/開発者向けの公開技術文書として Gist にリリースできる前提で扱います。

- 内部計画メモや未承認方針は `04_Documentation/` の既定読者に含めません。
- Gistへ公開する文書は、内部基準 `01_Plans/documentation_quality.md` の Mandatory（QG-1〜QG-6）を満たしてから出します。
- 04の文書は「公開運用文書」であり、設計の正本を書き換える場所ではありません。必要な設計根拠は `01_Plans/` / `02_Architecture/` を参照します。

## 2. リリース前チェック

タグ作成前に、最低限次のチェックを通してください。

- Backend テストが成功すること
- Frontend テストが成功すること
- Frontend ビルドが成功すること
- Gist公開対象の `04_Documentation/*.md` が `01_Plans/documentation_quality.md` の Mandatory（QG-1〜QG-6）を満たすこと
- strict mode例外運用を含む場合、`02_Architecture/strict_mode_exception_approval_flow.md` の D1〜D4（4h / 2h / 代理承認なし / 48h+15m/60m）と役割語彙（Security Officer / System Owner / Platform Operator）が `04_Documentation/operations.md` / `04_Documentation/local_llm_ops_guide.md` と一致すること

実行例:

```bash
# backend
cd 03_Implement/backend
python -m pytest

# frontend
cd ../frontend
npm test
npm run build
```

> CI を利用している場合は、上記に相当するチェックが green であることを確認してください。
> 本リポジトリではタグ push 後に `.github/workflows/release.yml` が実行され、backend Docker build（no push）と frontend dist artifact 作成が走ります。

## 3. バージョン更新（手動）

1. `CHANGELOG.md` の `## [Unreleased]` に変更点を追記する
2. リリース時に `Unreleased` の内容を新しいバージョン見出しへ移動する
   - 例: `## [0.1.1] - 2026-02-13`
3. 必要に応じて、比較リンクを使う運用ならリンク定義も更新する

## 4. タグ作成手順（vX.Y.Z）

例として `0.1.1` をリリースする場合:

```bash
git checkout main
git pull

# 必要ならリリース準備コミットを作成
git add CHANGELOG.md 04_Documentation/release.md
git commit -m "docs: prepare release v0.1.1"

git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main
git push origin v0.1.1
```

## 5. リリースノートの作り方

- GitHub Release の本文は `CHANGELOG.md` の対象バージョン節をそのまま転記します。
- 基本は次の3区分で十分です。
  - `Added`
  - `Changed`
  - `Fixed`

## 6. 運用ルール（最小）

- 自動 publish（レジストリへの配布）は行わない
- まずは「タグを切れること」「変更履歴を追えること」を優先する
- 運用が固まるまで手順はシンプルに保つ


## 7. タグ後の確認（GitHub Actions）

`vX.Y.Z` タグを push したら、GitHub Actions の **Release Build** を確認します。

- `Backend Docker build (no push)` が成功していること
- `Frontend dist build + artifact` が成功していること
- Artifacts に `frontend-dist-vX.Y.Z` が生成されていること

## 8. main ブランチの Required checks 設定（回帰防止）

`FB-RM-SEC-03` の運用として、GitHub の Branch protection rules で以下を **Required** に設定します。

- `Frontend regression guards (import/serialization/shape)`
- `Frontend lint + test`
- `Backend lint + test`

設定手順（GitHub UI）:

1. `Settings` → `Branches` → `Branch protection rules`
2. `main` 向けルールを作成/編集
3. `Require status checks to pass before merging` を有効化
4. 上記3ジョブ名を Required checks に追加して保存

> ジョブ名を変更した場合、Required checks の設定も更新が必要です。

## 9. Publishing metadata リリース注意（FB-RM-PUB-01）

- `view.json` / `packs/index.json` の `visibility` は `Public | Unlisted | Org | Restricted` のみを許容します。
- 互換読込では欠損値を次の既定値で補完します。
  - `view.json`: `Restricted`
  - `packs/index.json` の各 pack entry: `Public`
- enum 外値（例: `FriendsOnly`）は互換対象にせず、validator が拒否することをリリース前テストで確認してください。
- `visibility` は公開範囲のメタデータであり、権限制御の切替スイッチではありません。SafeMode 既定ON / read-only 公開 / share-export 制御は従来通り優先されます。
- 運用責務の境界:
  - 製品側: metadata 正規化・検証（import/export/validate）と既定値補完。
  - 運用側: `visibility` の意味づけ（公開ポリシー）を組織ルールへマッピングし、配布先アクセス制御（CDN/SSO/ネットワーク境界）を別途担保。

## 10. 04_Documentation の Gist 公開チェック

`04_Documentation/` を Gist へ切り出して公開する場合、タグリリースとは別に次を確認します。

1. 公開対象ファイルを確定する。
2. `01_Plans/documentation_quality.md` の Mandatory（QG-1〜QG-6）を確認する。
3. Markdown preview で表示崩れを確認する。
4. 外部読者が読んでも成立するよう、Audience / Goal / Non-goal / Outcome が読めることを確認する。
5. コマンド例がある場合は、前提条件・実行場所・期待結果が記載されていることを確認する。
6. 公開判定の記録を PR本文、release note、または同等の監査可能な場所に残す。

> QG未充足の文書は、Gist公開を見送り、修正後に再判定してください。



## Stream E 専属実行サイクル（operations / release / local_llm_ops_guide）

### Scope（編集許可）

- `04_Documentation/operations.md`
- `04_Documentation/release.md`
- `04_Documentation/local_llm_ops_guide.md`

### 編集禁止

- 上記以外のファイル

### 固定フェーズ

- `Read → Plan → Execute → Verify → Proceed`
- 各フェーズ開始時に対象3文書を再Readし、差分観点（用語 / 役割分離 / D1〜D4 / 参照導線）を確認する。

### 自己修復上限

- Verifyの自己修復（追記・体裁修正・語彙統一）は最大3回。
- 3回で解消しない場合は **Hold** として停止し、論点を `01_Plans/issues/` へ分離する。

### 停止条件

- 前提不整合（上流正本 `02_Architecture/*` と矛盾）。
- 他ストリーム領域への越境要求（編集許可外ファイルの変更要求）。

## DOC-OPS-05 セット1 実行記録（Phase 1〜5）

### AC（Acceptance Criteria）

- AC-1: 対外公開可能なリリース手順として Classification（Improve external）が明示される。
- AC-2: SemVer・事前チェック・タグ作成・タグ後確認の流れが維持される。
- AC-3: 内部基準参照（documentation_quality）と公開手順の境界が明確である。
- AC-4: 変更は Docs only とし、CI設定や実装フローを変更しない。

### DoD（Definition of Done）

- DoD-1: Phase 1〜5 が文書内に記録され、再実行可能な状態。
- DoD-2: docs-check コマンドが定義され、差分検証可能。
- DoD-3: Proceed判定（Ready/Hold/Needs-decision）が明記される。

### Phase 1 Read

- リリース前後チェック、CI導線、公開境界を確認。

### Phase 2 Plan

- 方針: 最小再現可能手順を維持し、内部承認フロー詳細は持ち込まない。

### Phase 3 Execute

- AC/DoD とPhase記録を追加し、運用判定を固定。

### Phase 4 Verify

- 推奨コマンド:
  - `rg -n "DOC-OPS-05 セット1|AC（Acceptance Criteria）|DoD（Definition of Done）" 04_Documentation/release.md`
  - `git diff --check`

### Phase 5 Proceed（判定と引き継ぎ）

- 状態: **Ready**（公開リリースガイドとして継続改善可能）。
- 次アクション: リリース自動化範囲を拡張する場合は `.github/workflows/release.yml` と同時整合で更新。


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

## 11. Phase 1-5 実行記録（2026-04-16 / DOC-OPS-05-12）

- Phase 1 Read: 開始時に `release.md` / `operations.md` / `security.md` / `strict_mode_exception_approval_flow.md` を再Readし、公開境界と語彙整合を確認。
- Phase 2 Plan: docs-only 変更に限定し、分類（Improve external）と公開チェック手順を維持する計画を固定。
- Phase 3 Execute: 本書の公開リリース手順と参照導線を整理し、内部専用情報は持ち込まない。
- Phase 4 Verify: `rg` と `git diff --check` を実施。修復は最大3回、超過時は停止。
- Phase 5 Proceed: 判定は **Ready**。後続は公開品質改善PRのみを対象とする。

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
- 04_Documentation/release.md は公開リリース手順の責務境界を維持し、運用常時監視との重複を増やさない。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/release.md`
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
- 次アクション固定: 公開リリース手順の改善対象として維持する。

### Phase 4: Execute
- docs-onlyで本ファイルのみを更新し、実装仕様変更は行わない。

### Phase 5: Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|DOC-OPS-05 Stream J2" 04_Documentation/release.md`
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
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-12-04doc-release.md`
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream J（DOC-OPS-05 中盤2）" 01_Plans/issues/issue-doc-ops-05-12-04doc-release.md 04_Documentation/release.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**。
- 引き継ぎ: 次担当は各Phase開始時に issue/doc の再読を継続し、競合・前提崩壊・3回超過時は即停止する。


## Stream H serial cycle（2026-04-19 / DOC-OPS-05-12）

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
- `rg -n "Audience|Goal|Non-goal|Outcome|Related|Go/No-Go|Stream H serial cycle" 04_Documentation/release.md`
- `git diff --check`
- 参照リンクは `Related` に記載された正本/Issue導線が有効であることを目視確認。

### Phase 5 Proceed/Stop
- 判定: **Ready**
- 停止条件: Verify自己修復が3回を超過、または未定義競合（要件キー未定義/契約衝突）を検知した場合は **Stop** とし、`01_Plans/issues/` に保留論点を記録する。

## Stream I phase execution record（2026-04-19 / DOC-OPS-05-12）

### Phase 1) Read
- release 手順と `e2e_testing.md` / `operations.md` / `security.md` の依存関係を再読。

### Phase 2) セキュリティ境界優先
- リリースゲートで SafeMode / share-export 境界後退を許容しないことを再確認。

### Phase 3) e2e/testing/release整合
- release判定とE2E判定（Compose/代替経路/Blocked記録）が整合することを確認。

### Phase 4) installation/config/narratives/local-llm整合
- install/local-llm/narratives 更新時のリリース判定導線（docs-check対象）を維持。

### Phase 5) Verify
- docs-check + `git diff --check`。

### Phase 6) Proceed
- 判定: **Ready**。

## Stream E serial cycle（2026-04-20 / DOC-OPS-05後半 docs-only）

### Phase 1 Read
- 本文先頭メタ（Classification / Audience / Goal / Non-goal / Public boundary / Outcome / Related）を再確認。

### Phase 2 Plan
- 変更は docs-only に限定し、Plan→Execute→Verify→Proceed の固定順序で進める。
- Verify失敗時の自己修復は最大3回、4回目相当は停止する。

### Phase 3 Execute
- 本文の公開境界・導線を維持し、safeMode既定ON／漏えい防止後退禁止を再確認。

### Phase 4 Verify
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Outcome|Related" 04_Documentation/release.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**。
- 次担当へ: 致命的矛盾（上位文書不整合・安全境界後退・自己修復3回超過）を検知した場合は停止してIssueへ記録する。
