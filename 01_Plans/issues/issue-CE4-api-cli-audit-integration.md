# Issue Draft: CE4 API/CLI/監査統合（Stream E / CE4専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream E（CE4専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0016`, `ADR-0017`, `02_Architecture/api.md`
- Dependencies: `CE-4`
- Verification: `docs-check`

## Objective（固定化する責務境界）
- API/CLI/監査の責務境界を **contract-only** で固定する（実装確定を行わない）。
- `proposal-only` を強制し、auto-apply / auto-confirm / auto-publish を禁止する。
- `fail-closed` を既定とし、監査必須項目の欠損は成功扱いしない。
- 監査イベント4点セット（`query` / `bundle` / `proposal` / `apply`）を必須契約として固定する。

## Phase 1 Read & Sync（差分抽出）

### 既存前提（抽出）
- API契約側（`02_Architecture/api.md`）では CE4 同値判定を `equivalenceKey AND bundleHash` で固定済み。
- 監査必須イベントは `query -> bundle -> proposal -> apply` の順序固定。
- CLI契約側（`ADR-0016`）には共通exit code契約はあるが、CE4監査違反コードの明示は未整備。
- セキュリティ運用側（`ADR-0017`）には監査帰属性Gateはあるが、CE4最小監査キー集合への参照は未整備。

### 不一致 / 欠落（一覧）
1. CE4監査イベントの最小スキーマ（必須キー）が issue/ADR横断で単一記述化されていない。
2. API→CLI の同値性要件（AND条件）と CLI exit code 契約の対応表が不足。
3. セキュリティ運用チェック（S2）と CE4監査4点セットのトレーサビリティ接続が弱い。

## Phase 2 ADR/契約明文化ゲート（Context / Decision / Consequences）

### Context
- CE4 は API/CLI/監査統合を実装分離で進めるため、契約を先に固定する必要がある。
- 既存文書間で監査キー・同値要件・運用チェックの粒度が部分的に分散している。

### Decision
1. **監査イベント最小スキーマ**
   - 全イベント共通必須キーを `eventType`, `timestamp`, `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `actor`, `result`, `channel`, `command`, `schemaVersion` に固定。
   - 4イベント（`query/bundle/proposal/apply`）の欠損は常に No-Go（fail-closed）。
2. **API→CLI同値性要件**
   - 成功条件は `equivalenceKey AND bundleHash` のみ。
   - CLIは同値判定失敗を契約違反として扱い、監査イベントと整合する終了コードを返す。
3. **セキュリティ運用チェックポイント**
   - `ADR-0017 Gate-S2` の判定条件へ CE4監査キー追跡（`eventType + equivalenceKey + queryCanonicalHash`）を接続する。

### Consequences
- 実装隊は mock監査fixtureだけで API/CLI監査整合を検証できる。
- 監査欠損・同値不成立時の失敗条件が先に固定され、後工程の裁量差分を縮小できる。
- ADR-0016/0017 は最小補正で CE4参照整合を維持できる。

## Phase 3 Plan（AC/DoD + mock-first）

### Acceptance Criteria（AC）
- [ ] CE4監査イベント最小スキーマ（必須キー + 4イベント順序）が issue と `api.md` で一致する。
- [ ] API/CLI成功判定が `equivalenceKey AND bundleHash` の AND 条件で固定される。
- [ ] CLI終了コードと監査失敗種別（入力違反 / 監査違反 / 同値不成立）が契約として読める。
- [ ] `ADR-0017 Gate-S2` から CE4監査キー追跡要件へ参照できる。
- [ ] 実装依存は mock監査fixture（`sourceBundleHash=mock:<hash>`）で切断する方針が明記される。

### Definition of Done（DoD）
- [ ] issue / `api.md` / `ADR-0016` / `ADR-0017` の4文書で語彙衝突がない。
- [ ] `proposal-only`, `fail-closed`, `safeMode既定ON` を後退させる記述がない。
- [ ] 監査トレーサビリティ（API/CLI相互追跡）が Yes/No 判定可能である。

## Phase 4 Execute（docs patch only）
- issue更新（本ファイル）
- `02_Architecture/api.md` の CE4監査統合節を更新（契約記述のみ）
- `ADR-0016` / `ADR-0017` は参照整合の最小補正のみ

## Phase 5 Verify（Self-check）
- AC/DoD を自己点検し、監査項目のトレーサビリティ（`eventType`, `equivalenceKey`, `queryCanonicalHash`）を確認する。
- エラー時は最大3回まで Self-Correction を許可し、4回目は停止（fail-safe）。

## Phase 6 Proceed（契約固定の記録）

### 固定した監査I/F仕様（下流参照用）
- 監査イベント最小スキーマ: 共通10キー + 4イベント順序固定。
- API/CLI同値性: `equivalenceKey AND bundleHash` 成立のみ成功。
- セキュリティ運用接続: Gate-S2 は CE4監査キー追跡を必須確認。
- 依存切断: `sourceBundleHash` は `sha256:<64hex>` / `mock:<64hex>` を同一fail-closedで扱う。

### 未解決論点（明示保留）
- principal識別子のマスキング方式（可逆/不可逆）は `ADR-0017` 保留事項に従い未決。
- 監査転送基盤の実装方式は CE4 スコープ外（契約のみ固定）。
