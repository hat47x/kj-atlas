# Decision Pack (2026-03-05): 人間判断待ちの高優先項目

目的: Active issue memo（Draft/Open）で着手を止めている判断点を短時間で決定可能にする。

## 0. 対象と優先順位

1. **P0 / AUTH-OPS-03**: strict mode例外緩和 Runbook の承認運用境界（Q1〜Q10）
2. **P1 / ENV-ARCH-01**: `KJ_ATLAS_*` 移行実装の運用境界
3. **P1 / REQ-DEF-01〜03**: 要件定義フェーズ壁打ち結果の固定粒度（優先要求・責任分界・受入規約）

---

## 1. P0: AUTH-OPS-03（完了）

### 1-1. 決定結果（2026-03-06）

- D1〜D4 を確定: 承認順序/TTL=4h、scope=tenant/最大2h、代理承認なし、48hレビュー+15m/60mエスカレーション。
- `02_Architecture/strict_mode_exception_approval_flow.md` を正本として決裁を記録済み。

### 1-2. 確定済み決定セット

- D1: 承認順序 + 承認TTL
- D2: 適用スコープ + 例外最大継続時間
- D3: 復旧判定者 + 緊急時代理承認
- D4: 保存先 + 事後レビュー期限 + 違反時SLA

### 1-3. 完了アクション

1. `enterprise_architecture.md` / `operations.md` / `security.md` の相互リンクを同期済み。
2. dashboard と `issues/README.md` の状態を `Done` に同期済み。
3. 整合確認と docs-check 完了をもって AUTH-OPS-03 を Done 判定。

---

## 2. P1: ENV-ARCH-01（人間判断済み）

### 2-1. 決定結果

- E1: **Option B**（痕跡を残さない一括移行）
- E2: **Option C**（移行警告/監査痕跡を追加しない）
- E3: **考慮外**（期限ベース運用を採用しない）

### 2-2. 確定した実行方針

- `KJ_ATLAS_*` 以外を受理しない。
- 旧キー互換を実装しない。
- 新旧混在は不正設定として失敗させる。

### 2-3. 直近アクション

1. `settings.py` の旧キーalias削除。
2. compose / backend README / operations の旧キー記載削除。
3. 旧キー拒否をテストで固定。

---


## 3. P1: REQ-DEF-01〜03（新規）

### 3-1. 止まっている理由

- 要件定義フェーズの壁打ち結果をIssue化したが、Must/Should/Could分類と責任分界の拘束力をどこまで必須化するか未決定。
- 受入シナリオ規約を「推奨」に留めるか「必須」に引き上げるかで、後続Issue分割基準が変わる。

### 3-2. 必須決定セット（現況）

- R1: `REQ-DEF-01` の要求優先度分類（P-01〜P-07）をレビュー承認必須にするか。**→ 決定済み（Done）**
- R2: `REQ-DEF-02` のRACI/契約判定欄を全Issue必須項目にするか。**→ 未承認（Pending）**
- R3: `REQ-DEF-03` の要求粒度↔検証粒度マッピングをテンプレ必須にするか。**→ 未承認（Pending）**

### 3-3. Pending項目一覧（R2/R3系のみ）

#### 3-3-1) 「決めるべきこと」（Decision）

| Decision ID | Backlog | 論点 | 提案案 |
|---|---|---|---|
| R2-P1 | REQ-DEF-02 | `RACI` / `ContractImpact` を全Issueで必須化するか | 新規Issueは必須、既存Activeは移行期限付きで段階適用 |
| R2-P2 | REQ-DEF-02 | `Go/No-Go` 判定欄の適用開始時期 | 承認日から+1スプリントで全Openへ適用 |
| R2-P3 | REQ-DEF-02 | SafeMode/漏えい防止をレビューゲートへ接続する運用レベル | docs-check必須 + レビュー時チェックリスト必須 |
| R3-P1 | REQ-DEF-03 | 要求粒度↔検証粒度マッピングをテンプレ必須化するか | R0〜R3のマッピング記述を新規Issueで必須 |
| R3-P2 | REQ-DEF-03 | 1Issue1検証責務の例外閾値 | 例外は「統合境界が2つ以上」の場合のみ許容 |
| R3-P3 | REQ-DEF-03 | 受入シナリオ最小テンプレの必須化範囲 | Process/Docs以外は必須、Docs-onlyは任意 |

#### 3-3-2) 「決めないと止まる後続作業」（Blocked work）

1. `01_Plans/issues/TEMPLATE.md` の必須項目固定（RACI/ContractImpact/検証粒度/受入シナリオ）。
2. `01_Plans/issues/README.md` の Active issue 起票手順（必須メタ定義）更新。
3. REQ-DEF-02/03 を参照する新規Issueのレビュー判定（Go/No-Go）自動化条件定義。

### 3-4. Decision Record（確定案 / 承認待ち）

#### DR-REQ-DEF-02 (R2系)

- Context: REQ-DEF-02では責任分界と契約影響の記載は固定済みだが、テンプレ全体への必須化範囲が未承認。
- Decision (Proposal): `RACI` / `ContractImpact` / `Go-No-Go` を「新規Issue必須」「既存Activeは次スプリント末までに追補」とする。
- Consequences:
  - 採用時: 起票品質のばらつきが減り、契約判断の漏れを抑制できる。
  - 非採用時: Issueごとの責任境界解釈差が残り、レビュー再作業が発生する。
- Approval status: **Pending Human Approval**
- Approval request (for human decider):
  - `Approve` または `Reject` を R2-P1/R2-P2/R2-P3 ごとに明示してください。
  - 期限提案: 2026-03-12 JST（未回答時は「未承認」のまま Phase 2 へ進まない）。
  - 記録先: 本ファイルの Decision Record と `project-progress-dashboard.md` の Decision Queue を同時更新。

#### DR-REQ-DEF-03 (R3系)

- Context: REQ-DEF-03では検証粒度の考え方は固定済みだが、テンプレ必須化/例外閾値が未承認。
- Decision (Proposal): `要求粒度↔検証粒度` と `AcceptanceScenario最小テンプレ` を新規Issue必須化し、例外は統合境界2つ以上のみ許容する。
- Consequences:
  - 採用時: 分割粒度と検証責務が明確になり、後続Issueの衝突を抑制できる。
  - 非採用時: docs-check対象の粒度判断が人依存で残り、分割ルールの再議論が継続する。
- Approval status: **Pending Human Approval**
- Approval request (for human decider):
  - `Approve` または `Reject` を R3-P1/R3-P2/R3-P3 ごとに明示してください。
  - 期限提案: 2026-03-12 JST（未回答時は「未承認」のまま Phase 2 へ進まない）。
  - 記録先: 本ファイルの Decision Record と `project-progress-dashboard.md` の Decision Queue を同時更新。

### 3-5. 決定後アクション（承認後のみ実施）

1. REQ-DEF-01 は Done、REQ-DEF-02/03 は Open のまま共通I/F参照を維持する。
2. `01_Plans/issues/TEMPLATE.md` への必須反映範囲を人間判断で確定する。
3. `project-progress-dashboard.md` の Decision Queue を未確定テーマ（REQ-DEF-02/03）中心に維持する。

## 4. 意思決定記録テンプレート

```md
[Decision Record]
- Date (UTC):
- Decider(s):
- Backlog ID:
- Selected options:
- Rationale:
- Effective from:
- Follow-up tasks:
```


## 5. 統合確認サマリ（1ページ）

### 整合点検結果

- `project-progress-dashboard.md`: AUTH-OPS-03/DOC-OPS-02/DOC-OPS-03/REQ-DEF-01 を Done に同期。
- `issues/README.md`: 上記4件を Completed issue memos へ移送し、Active一覧と実態を一致。
- decision-pack 本書: AUTH-OPS-03 を「完了」へ更新。

### 残課題（次スプリント持越し）

1. REQ-DEF共通キーを `01_Plans/issues/TEMPLATE.md` へ必須反映するかを人間判断する。
2. DOC-OPS-02 ドリフト検知を定期運用（レビュー時チェック項目）へ組み込む。
3. REQ-DEF-02/03 の未確定項目を Decision Queue で決裁する。

### 判定

- P0ボトルネック（AUTH-OPS-03 D1〜D4未確定）は解消。
- DOC-OPS-02 / DOC-OPS-03 / REQ-DEF-01 は Done へ遷移し、残る P1 は REQ-DEF-02/03 に集約。
