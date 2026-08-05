# Issue Draft: SOCIAL-DIFFUSION-01 複数レビュアー間の理解再現性

- Type: Feature request
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD（A=Productization Program Owner / R=QA Lead）
- Scope: `01_Plans/`, `02_Architecture/value_traceability.md`, `03_Implement/frontend/e2e/`, `04_Documentation/narratives.md`
- Related Backlog: `SOCIAL-DIFFUSION-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0038-social-diffusion-of-explainable-consensus.md`, `01_Plans/adr/ADR-0036-value-to-social-goal-realization-roadmap.md`, `01_Plans/issues/issue-PRODUCT-VALUE-03-reviewable-outcome-package.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: SOCIAL-DIFFUSION-01
- RequirementStatement: 同一レビューパックを独立した複数レビュアーが読んだとき、確定点・保留点・根拠・未レビュー情報の読み取り結果が再現的に一致することを、観測可能な形で扱う。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=PRODUCT-VALUE-03の成果物パッケージが生成できる / 操作=同一パックを複数レビュアーが独立に読み、確定/保留/根拠/未レビューを抽出する / 期待結果=読み取り結果の一致率が観測でき、不一致箇所が成果物の改善点として残る / 除外=結論の正誤判定、合意の強制、レビュアー個人の評価。
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0038`

## 1) 課題 / Problem statement

- V4は「1人が安全に共有できる」状態までで、複数レビュアー間で同じ理解が再現するかは未定義。
- 再現性が低い成果物は、社会的に広がるほど誤解と早すぎる収束を増幅する。

## 2) 背景 / Context

- `ADR-0038` 柱1が複数レビュアー再現性を社会的普及の前提に位置づけた。
- `PRODUCT-VALUE-03` が成果物最小6要素（要約/確定/保留/未レビュー/根拠導線/SafeMode結果）を定義済み。
- 観測するのは理解の再現性であり、正誤や合意強制ではない（P-02反スコアリング維持）。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 説明可能性は「複数人が同じ確定/保留/根拠を読み取れる」ことで初めて社会的価値になる。
- 安全（THREAT_MODEL / SafeMode）: 再現性観測でも未レビュー本文・機微情報を新たに露出しない。
- 企業・行政要件（enterprise_architecture）: 判断資料の説明責任は、レビュアー間で読み取りが揃うことに支えられる。
- 後方互換（schemas）: 既存review pack形式を壊さず、再現性観測手順を追加する。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs first（再現性観測手順、不一致の記録方法）。実装はE2E名の割当のみ。
- 変更の最小単位: 1パックにつき「確定/保留/根拠/未レビュー」の読み取り項目チェックリストと一致率の観測手順。
- 非目標: 正解判定、合意強制、レビュアーのスコアリング、複数人同時編集基盤。

## 5) 受入条件 / Acceptance criteria

- [ ] 同一パックに対する複数レビュアーの読み取り項目（確定/保留/根拠/未レビュー）が定義される。
- [ ] 読み取り一致率の観測手順と、不一致箇所を成果物改善点として残す方法が定義される。
- [ ] 観測がレビュアー個人の評価・序列化に転用されない非目標が明記される。
- [ ] SafeMode境界を越えず、未レビュー本文・機微情報を露出しない。
- [ ] docs-check（validator/triage/rg）で手順の整合が確認される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 読み取り項目チェックリスト（確定/保留/根拠/未レビュー）を定義する。
- [ ] T2 一致率観測手順と不一致の記録方法を定義する。
- [ ] T3 非評価・非序列化の制約を明記する。
- [ ] T4 `narratives.md` / `value_traceability.md` と同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `rg -n "再現性|複数レビュア|読み取り一致" 01_Plans 02_Architecture 04_Documentation`
- 期待結果:
  - validator成功、triage stopper=none、再現性観測手順が検索可能。
- 未実施時の理由・代替検証:
  - 多人数検証前は、代表パックの机上レビューで代替し理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 単一作成者の自己点検のみとする。社会的普及時の誤解増幅を防げないため不採用。
- 代替案B: 合意一致を強制する。反スコアリング・意味保留の価値に反するため不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 一致率を品質スコア化し、レビュアー評価へ転用される。
- 影響範囲: review pack、narratives、value_traceability。
- ロールバック手順: 一致率観測を成果物改善メモのみへ縮退し、数値運用を停止する。

## 10) Additional context

- 関連: 経時的見直しは `SOCIAL-DIFFUSION-02`、非監視観測は `SOCIAL-DIFFUSION-04`。
- ADR化が必要になる条件: 再現性を公開配布の合否ゲートとして契約化する場合。


## 11) Stream H deferred activation lock（2026-06-13）

| Item | Planning decision |
| --- | --- |
| Classification | Hold / deferred-open-ready（VR5 direction retained, activation postponed） |
| Direction retained | 同一レビュー成果物を複数レビュアーが読んだとき、確定点・保留点・根拠・未レビュー情報の理解が再現的に揃うかを観測する。 |
| Activation condition | 二名以上の独立レビュアー、またはMaintainer承認のサロゲート読解プロトコルが存在する。 |
| Open condition | Real-user/cooperator milestone exists, SafeMode/share-export impact is explicitly reviewed, and this issue can remain docs/planning-first. |
| Explicit non-goal | 結論の正誤判定、レビュアー採点、強制合意。 |
| Deferral reason | `ADR-0039` keeps social-diffusion work out of mandatory implementation until social participants or a safe pilot exist. |

### Safe-diffusion guardrails

- Do not require real external participants while none exist.
- Do not add surveillance telemetry, user-level adoption scoring, or administrator-centered monitoring.
- Preserve evidence, hold, review, and SafeMode/share-export states in any future handoff.
