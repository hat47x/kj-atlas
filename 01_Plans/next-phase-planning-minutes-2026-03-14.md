# 次フェーズ計画会議 議事録（2026-03-14）

- 日時: 2026-03-14 21:00-22:10 JST
- 形式: 仮想ステークホルダー・エージェント会議
- 参加ロール:
  - Product/Value
  - Architecture
  - Security/Governance
  - Operations/Delivery
  - QA/Verification
- 議題:
  1. 現フェーズ（HIL-RS-01）の完了状態と未解決事項の固定
  2. 次フェーズ（HIL-RS-02）での実行境界（安全/責務分離/検証）
  3. ADR化・Issue分解・ダッシュボード同期

## 1. 前提固定（Step 1）

### 1-1. 現フェーズ完了状態

- `ADR-0026` により HIL-RS-01 の目的/非目標/停止条件は Accepted で固定済み。
- A1（最小I/F契約固定）は Open だが、A2/A3着手の契約前提（schemaVersion固定、SSOT固定、契約変更差し戻し）は文書化済み。

### 1-2. 未解決事項

- 未解決事項は「A2/A3の実装順序をどこまで並列化できるか」「Decision Queueの更新タイミング」。
- いずれも上位方針変更を必要としないが、運用手順が分散しやすい。

### 1-3. 次フェーズ制約（非機能）

- SafeMode既定ONを維持し、share/export漏洩防止を弱めない。
- human_dual_control_only（責務分離）を維持し、単独権限確定を禁止する。
- 未確定事項は「未確定」のまま Decision Queue へ記録し、決め打ちしない。

## 2. 論点別ディスカッション（Step 2）

## 論点A: 価値整合（Product/Value）

- 提案: HIL-RS-02は「候補比較 + 人間確定 + 可逆差分記録」を最小スコープで実装する。
- 懸念: 実装先行で「単一正解UI」に寄るリスク。
- 反証: A1契約とADRで非目標を固定し、ランキング/自動確定UIを禁止。
- 結論: 採用。Issue分解で「非スコープ」を明示する。

## 論点B: 設計整合（Architecture）

- 提案: 02_Architectureの既存契約を変更せず、03_Implementで参照実装に限定する。
- 懸念: 実装中に契約変更要求が発生する可能性。
- 反証: 変更要求はA1へ差し戻し、HIL-RS-02内では凍結。
- 結論: 採用。A1を依存クリティカルパスとして固定。

## 論点C: 安全・統治（Security/Governance）

- 提案: 安全境界チェック（SafeMode, leakage prevention, SoD）を各Issueの受入条件へ必須記載。
- 懸念: docs-only変更でもチェック漏れが起きる。
- 反証: docs-checkに `rg` 検証を含め、違反語（disable safe mode等）を監査する。
- 結論: 採用。検証コマンドを固定。

## 論点D: 運用・デリバリ（Operations/Delivery）

- 提案: 次フェーズは 1 umbrella + 3最小Issue（A1/A2/A3）で運用する。
- 懸念: Active件数増加で dashboard 保守コストが上がる。
- 反証: 依存順（A1→A2→A3）を明記し、着手順を固定すれば再開性は向上。
- 結論: 採用。Active件数増加は許容。

## 論点E: 検証・回帰（QA/Verification）

- 提案: 各Issueに docs-check の最低コマンド + Done時の unit/e2e追加条件を定義する。
- 懸念: 現時点で実装未着手のため unit/e2e を強制すると空振りになる。
- 反証: 本計画フェーズは docs-check を必須、実装Issueで unit/e2e を昇格設定する。
- 結論: 採用。検証レベルは段階昇格。

## 3. 採否理由・代替案（Step 3）

- 代替案1（不採用）: HIL-RS-02を単一Issueで管理。
  - 不採用理由: 依存と責務境界が曖昧になり、停止/再開判断が困難。
- 代替案2（不採用）: A2/A3を先行Openにして並列着手。
  - 不採用理由: A1契約差分の再作業リスクが高い。
- 採用案: umbrella + A1/A2/A3 の直列依存を固定。

## 4. Decision Queue（未決事項）

1. DQ-HIL-RS-02-01: A2開始時点で必要な最小fixtureセット確定（Owner: Architecture/QA, Due: 2026-03-17）
2. DQ-HIL-RS-02-02: A3開始前の運用手順差分テンプレート固定（Owner: Ops, Due: 2026-03-18）

## 5. 次アクション（担当・期限・依存）

1. Plan Owner: ADR-0027起票と受入条件固定（期限: 2026-03-15, 依存: 本議事録）
2. Architecture Owner: HIL-RS-02-A1 issueをOpen化（期限: 2026-03-16, 依存: ADR-0027 Accepted）
3. Delivery Owner: HIL-RS-02-A2/A3 issueのDraft詳細化（期限: 2026-03-16, 依存: A1 Open）
4. Plan Owner: dashboard/README同期（期限: 2026-03-15, 依存: issue作成完了）
