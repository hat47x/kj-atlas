# Decision Pack (2026-03-05): 人間判断待ちの高優先項目

目的: Active issue memo（Draft/Open）で着手を止めている判断点を短時間で決定可能にする。

## 0. 対象と優先順位

1. **P0 / AUTH-OPS-03**: strict mode例外緩和 Runbook の承認運用境界（Q1〜Q10）
2. **P1 / ENV-ARCH-01**: `KJ_ATLAS_*` 移行実装の運用境界

---

## 1. P0: AUTH-OPS-03（継続して判断待ち）

### 1-1. 止まっている理由

- 2者承認責務は確定済みだが、承認順序/TTL/代理承認/違反時SLA などの最終決裁が未完了。
- `02_Architecture/strict_mode_exception_approval_flow.md` を正本として決裁を記録する必要がある。

### 1-2. 必須決定セット

- D1: 承認順序 + 承認TTL
- D2: 適用スコープ + 例外最大継続時間
- D3: 復旧判定者 + 緊急時代理承認
- D4: 保存先 + 事後レビュー期限 + 違反時SLA

### 1-3. 決定後アクション

1. AUTH-OPS-03へ採択結果を追記。
2. `operations.md` / `security.md` へ同期。
3. `Status: Draft -> Open/In Progress` へ移行。

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

## 3. 意思決定記録テンプレート

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
