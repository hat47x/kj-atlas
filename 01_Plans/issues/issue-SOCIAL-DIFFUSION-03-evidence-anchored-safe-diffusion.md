# Issue Draft: SOCIAL-DIFFUSION-03 証拠定着型の安全配布

- Type: Feature request
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD（A=Productization Program Owner / R=Security Officer）
- Scope: `01_Plans/`, `02_Architecture/enterprise_architecture.md`, `03_Implement/frontend/src/export/`, `04_Documentation/security.md`
- Related Backlog: `SOCIAL-DIFFUSION-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0038-social-diffusion-of-explainable-consensus.md`, `01_Plans/adr/ADR-0036-value-to-social-goal-realization-roadmap.md`, `ROADMAP.md`, `THREAT_MODEL.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: SOCIAL-DIFFUSION-03
- RequirementStatement: 広域配布（Static Publish / Review Pack配布）でも保留・反対・未レビュー・根拠参照が欠落せず、SafeMode配布既定ON・解除不可の公開モードを社会配布の標準とする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=公開候補の成果物がある / 操作=Static Publishまたはレビューパック配布を生成し、公開モードで確認する / 期待結果=保留/反対/未レビュー/根拠が残り、SafeModeが解除不可で適用される / 除外=匿名化要件の組織別最終確定、認証付き配信の実装、SNS型公開。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0038`

## 1) 課題 / Problem statement

- 社会へ広がる過程で、保留・反対・根拠が落ちて「確定済みの結論」だけが流通すると、早すぎる収束を社会規模で再生産する。
- 公開配布の安全境界（SafeMode解除可否）が社会配布向けに固定されていない。

## 2) 背景 / Context

- `ADR-0038` 柱3が証拠定着型の安全配布を要件化した。
- `ROADMAP.md` 方式A/C（Static Publish + SafeMode強制）、`FB-RM-PUB-03` が `publish:static`（safeMode強制・read-only）を提供済み。
- `THREAT_MODEL.md` が share/export/公開時の漏洩を主要脅威に位置づける。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 反対・保留・根拠が残る配布が、説明可能な合意の社会的伝播条件になる。
- 安全（THREAT_MODEL / SafeMode）: 公開配布はSafeMode解除不可を標準とし、未レビュー本文・機微情報を出さない。
- 企業・行政要件（enterprise_architecture）: 広域公開（方式A）と限定公開（方式B）の境界を安全側で明示する。
- 後方互換（schemas）: 既存pack/view metadata（visibility）とexport形式を壊さない。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs first（社会配布の安全要件、公開モード既定、欠落禁止要素の定義）。実装は既存 `publish:static` の確認に限定。
- 変更の最小単位: 配布物に「保留/反対/未レビュー/根拠参照/SafeMode結果」の非欠落を必須化する。
- 非目標: 組織別匿名化ルールの最終確定、認証付き配信(方式B)実装、SNS型公開プラットフォーム化。

## 5) 受入条件 / Acceptance criteria

- [ ] Static Publish / レビューパック配布で、保留・反対・未レビュー・根拠参照が欠落しない。
- [ ] 公開配布モードで SafeMode が既定ONかつ解除不可である。
- [ ] 配布物に未レビュー本文・機微情報が既定で含まれない。
- [ ] 広域公開(方式A)と限定公開(方式B)の境界が安全側で文書化される。
- [ ] docs-check（validator/triage/rg）で配布安全要件の整合が確認される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 社会配布物の非欠落必須要素（保留/反対/未レビュー/根拠/SafeMode結果）を定義する。
- [ ] T2 公開モードのSafeMode解除不可を標準として明記する。
- [ ] T3 既存 `publish:static` 出力との整合を確認する。
- [ ] T4 方式A/B境界の安全指針を `security.md` / `enterprise_architecture.md` と同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `rg -n "Static Publish|SafeMode|公開モード|未レビュー|根拠参照" 01_Plans 02_Architecture 03_Implement/frontend 04_Documentation`
- 期待結果:
  - validator成功、triage stopper=none、配布安全要件が検索可能。
- 未実施時の理由・代替検証:
  - 実配布前は、`publish:static` 出力レビューと公開モード設定確認で代替し理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 確定点のみを公開し保留・根拠を省く。説明可能性と反早すぎる収束に反するため不採用。
- 代替案B: 公開モードでもSafeMode解除を許可する。社会配布の漏洩リスクが上がるため不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 配布物が情報過多になり、確定点と保留点が読み分けにくい。
- 影響範囲: export、static publish、公開文書。
- ロールバック手順: 配布既定を概要+安全状態のみへ縮退し、詳細は限定公開導線へ寄せる。

## 10) Additional context

- 関連: 経時的見直しは `SOCIAL-DIFFUSION-02`、非監視観測は `SOCIAL-DIFFUSION-04`。
- ADR化が必要になる条件: 公開配布形式や匿名化方式を新しい互換契約として固定する場合。


## 11) Stream H deferred activation lock（2026-06-13）

| Item | Planning decision |
| --- | --- |
| Classification | Hold / deferred-open-ready（VR5 direction retained, activation postponed） |
| Direction retained | 広域配布時も保留・反対・未レビュー・根拠参照が欠落しない安全配布方向を保持する。 |
| Activation condition | SafeMode/share-export境界を保つ公開またはレビューパック配布候補が存在する。 |
| Open condition | Real-user/cooperator milestone exists, SafeMode/share-export impact is explicitly reviewed, and this issue can remain docs/planning-first. |
| Explicit non-goal | 根拠や未レビュー状態を削った公開、SafeMode解除を前提にした配布。 |
| Deferral reason | `ADR-0039` keeps social-diffusion work out of mandatory implementation until social participants or a safe pilot exist. |

### Safe-diffusion guardrails

- Do not require real external participants while none exist.
- Do not add surveillance telemetry, user-level adoption scoring, or administrator-centered monitoring.
- Preserve evidence, hold, review, and SafeMode/share-export states in any future handoff.
