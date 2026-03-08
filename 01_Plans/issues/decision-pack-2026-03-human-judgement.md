# Decision Pack (2026-03-05): 人間判断待ちの高優先項目

目的: Active issue memo（Draft/Open）で着手を止めている判断点を短時間で決定可能にする。

## 0. 対象と優先順位

1. **P0 / AUTH-OPS-03**: strict mode例外緩和 Runbook の承認運用境界（Q1〜Q10）
2. **P1 / ENV-ARCH-01**: `KJ_ATLAS_*` 移行実装の運用境界
3. **P1 / REQ-DEF-01〜03**: 要件定義フェーズ壁打ち結果の固定粒度（優先要求・責任分界・受入規約）

---

## 1. P0: AUTH-OPS-03（決定固定済み / 反映フェーズ）

### 1-1. 決定結果（2026-03-06）

- D1〜D4 を確定: 承認順序/TTL=4h、scope=tenant/最大2h、代理承認なし、48hレビュー+15m/60mエスカレーション。
- `02_Architecture/strict_mode_exception_approval_flow.md` を正本として決裁を記録済み。

### 1-2. 確定済み決定セット

- D1: 承認順序 + 承認TTL
- D2: 適用スコープ + 例外最大継続時間
- D3: 復旧判定者 + 緊急時代理承認
- D4: 保存先 + 事後レビュー期限 + 違反時SLA

### 1-3. 残アクション

1. `enterprise_architecture.md` / `operations.md` / `security.md` の相互リンクを固定。
2. dashboard と `issues/README.md` の状態を `In Progress` に同期。
3. 整合確認後に AUTH-OPS-03 を Done 判定する。

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

### 3-2. 必須決定セット

- R1: `REQ-DEF-01` の要求優先度分類（P-01〜P-07）をレビュー承認必須にするか。
- R2: `REQ-DEF-02` のRACI/契約判定欄を全Issue必須項目にするか。
- R3: `REQ-DEF-03` の要求粒度↔検証粒度マッピングをテンプレ必須にするか。

### 3-3. 決定後アクション

1. REQ-DEF-01〜03 の `Status: Draft -> Open` へ更新。
2. `01_Plans/issues/TEMPLATE.md` への反映要否を確定。
3. `project-progress-dashboard.md` の Decision Queue を決定済みに更新。

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

- `project-progress-dashboard.md`: AUTH-OPS-03=In Progress、REQ-DEF-01〜03=Open を反映。
- `issues/README.md`: Active memo の AUTH-OPS-03 状態を In Progress へ同期。
- decision-pack 本書: AUTH-OPS-03 を「決定固定済み/反映フェーズ」へ更新。

### 残課題（次スプリント持越し）

1. AUTH-OPS-03 の Done 判定エビデンス（3文書同期確認ログ）を最終添付する。
2. REQ-DEF共通キーを `01_Plans/issues/TEMPLATE.md` へ必須反映するかを人間判断する。
3. DOC-OPS-02 ドリフト検知を定期運用（レビュー時チェック項目）へ組み込む。

### 判定

- P0ボトルネック（AUTH-OPS-03 D1〜D4未確定）は解消。
- P1（DOC-OPS-02 / REQ-DEF-01〜03）は Open/In Progress に移行し、後続更新の競合源を縮減。
