# Issue Draft: SOCIAL-DIFFUSION-02 合意の経時的見直し可能性

- Type: Feature request
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD（A=Productization Program Owner / R=Platform Architecture Owner）
- Scope: `01_Plans/`, `02_Architecture/schemas.md`, `02_Architecture/review_attribution.md`, `03_Implement/frontend/`, `04_Documentation/data_handling.md`
- Related Backlog: `SOCIAL-DIFFUSION-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0038-social-diffusion-of-explainable-consensus.md`, `01_Plans/adr/ADR-0036-value-to-social-goal-realization-roadmap.md`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: SOCIAL-DIFFUSION-02
- RequirementStatement: 共有済みの合意成果物を、版を越えて再オープンし、差分と根拠付きで見直せるようにし、過去合意を不可逆に固定しない。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=共有済みレビューパック（Consensus Graph由来）がある / 操作=後の版で再オープンし、差分・根拠・レビュー履歴を辿る / 期待結果=過去合意が見直し可能で、再評価導線と source trace が残る / 除外=合意の自動上書き、履歴の破壊的削除、署名必須化。
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0038`

## 1) 課題 / Problem statement

- 共有した合意が時間とともに固定化（lock-in）すると、可逆性という中核価値が社会規模で失われる。
- 後から「やはり違った」を扱えないと、early collapse を社会的に追認してしまう。

## 2) 背景 / Context

- `ADR-0038` 柱2が合意の経時的見直し可能性を要件化した。
- `domain.md` は可逆性（履歴・差分・巻き戻し）を設計前提に置く。
- `review_attribution.md` がレビュー帰属、`patch + approval` 履歴が再評価の基盤。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 可逆性（P-01関連）は共有後も維持されて初めて社会的価値になる。
- 安全（THREAT_MODEL / SafeMode）: 再オープン時も SafeMode と未レビュー保護を維持する。
- 企業・行政要件（enterprise_architecture）: 過去判断の見直し導線は監査・説明責任に直結する。
- 後方互換（schemas）: 既存の版・差分・履歴構造を壊さず、再オープン導線を追加する。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs first（再オープン手順、見直し導線、source trace保持方針）。スキーマ拡張が必要なら別途分離する。
- 変更の最小単位: 共有パックに「どの版か / 元データへの戻り方 / 再評価開始点」を保持する。
- 非目標: 合意の自動上書き、履歴の破壊的削除、電子署名・改ざん不能監査の既定必須化。

## 5) 受入条件 / Acceptance criteria

- [ ] 共有済み成果物を後の版で再オープンし、差分・根拠・レビュー履歴を辿れる。
- [ ] 過去合意が不可逆に固定されず、再評価開始点が残る。
- [ ] 再オープン時も SafeMode・未レビュー保護・`human_reviewed`人手昇格が維持される。
- [ ] source trace（元カード/島/関係/レビュー状態）への復帰導線が欠落しない。
- [ ] docs-check（validator/triage/rg）で再オープン手順の整合が確認される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 共有パックの版・元データ参照・再評価開始点の保持方針を定義する。
- [ ] T2 再オープン導線（差分/根拠/履歴の辿り方）を定義する。
- [ ] T3 SafeMode非後退と履歴非破壊の制約を明記する。
- [ ] T4 現行スキーマで足りる範囲と拡張が要る範囲を分離する。
- [ ] T5 `data_handling.md` / `review_attribution.md` と同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `rg -n "再オープン|見直し|可逆|source trace" 01_Plans 02_Architecture 04_Documentation`
- 期待結果:
  - validator成功、triage stopper=none、再オープン手順が検索可能。
- 未実施時の理由・代替検証:
  - 実装前は、版間再オープンの操作計画と履歴保持レビューで代替し理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 共有後は読み取り専用で固定する。可逆性価値を失うため不採用。
- 代替案B: 履歴を都度上書きする。再評価追跡性を失うため不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 版が増え、どの合意が最新か分かりにくくなる。
- 影響範囲: review pack、版/差分構造、data_handling。
- ロールバック手順: 再オープンを最新版からの差分参照のみへ縮退し、版分岐運用を停止する。

## 10) Additional context

- 関連: 複数レビュア再現性は `SOCIAL-DIFFUSION-01`、安全配布は `SOCIAL-DIFFUSION-03`。
- ADR化が必要になる条件: 版・再オープンのためにスキーマへ新しい永続構造を追加する場合。


## 11) Stream H deferred activation lock（2026-06-13）

| Item | Planning decision |
| --- | --- |
| Classification | Hold / deferred-open-ready（VR5 direction retained, activation postponed） |
| Direction retained | 共有済み成果物を版越しに再オープンし、差分・根拠・保留理由を失わず見直せることを保持する。 |
| Activation condition | 版管理されたレビュー成果物と再オープン候補フローが存在する。 |
| Open condition | Real-user/cooperator milestone exists, SafeMode/share-export impact is explicitly reviewed, and this issue can remain docs/planning-first. |
| Explicit non-goal | 過去合意の不可逆固定、自動再承認、合意ロックイン。 |
| Deferral reason | `ADR-0039` keeps social-diffusion work out of mandatory implementation until social participants or a safe pilot exist. |

### Safe-diffusion guardrails

- Do not require real external participants while none exist.
- Do not add surveillance telemetry, user-level adoption scoring, or administrator-centered monitoring.
- Preserve evidence, hold, review, and SafeMode/share-export states in any future handoff.
