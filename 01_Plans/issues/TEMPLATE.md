# Issue Draft: <BacklogID or Theme> <短いタイトル>

- Type: <Feature request / Bug / Process / Security / Documentation quality>
- Status: Draft (起票用)
- Source Issue: <N/A (未運用時) or GitHub Issue URL (運用時)>
- Priority: <P0/P1/P2/P3>
- Owner: <TBD or team/user>
- Scope: `<directory_or_docs>`
- Related Backlog: `<FB-...>` (なければ `N/A`)
- Related ADR/Spec: `<ADR-xxxx ...>`
- Expected verification level: `<docs-check / unit / integration / e2e>`

## Requirement meta I/F（共通キー）

> REQ-DEF系Issueで編集分離するため、先頭でこのキーセットを固定してから本文へ進む。

- RequirementID
- RequirementStatement
- PriorityClass（Must / Should / Could）
- RACI（A/R/C/I）
- ContractImpact（schema / api / policy / ops : あり / なし）
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）
- VerificationLevel（docs-check / unit / integration / e2e）
- DecisionStatus（Fixed / Pending）
- DecisionQueueRef（未確定時の参照先）


## Expected verification level values

- `docs-check`: ドキュメント整合性のみを確認（リンク/参照/必須メタ/体裁）。
- `unit`: docs-checkに加えて、対象ロジックの単体テストを実施。
- `integration`: unitに加えて、境界I/Fを含む結合テストを実施。
- `e2e`: integrationに加えて、ユーザーフロー（UI/API連動）を検証。

### Verification granularity mapping（要求粒度↔検証粒度）

| 要求粒度 | 想定変更 | Expected verification level（最小） |
| --- | --- | --- |
| R0 | 記述規約/運用手順/Issueテンプレ整備 | `docs-check` |
| R1 | ロジック単位の仕様差分 | `unit` |
| R2 | 境界I/Fを跨ぐ仕様差分 | `integration` |
| R3 | 利用者フロー完遂性を問う仕様差分 | `e2e` |

### Plan → Execute → Verify / 自己修復3回 / フェイルセーフ停止

- Plan: Issue作成時に要求粒度（R0〜R3）と `Expected verification level` を同時宣言する。
- Execute: 1Issue 1検証責務（主責務）を原則化し、例外時は理由を明記する。
- Verify: 宣言したレベル未満の検証で完了扱いにしない。未実施時は理由と代替検証を `Validation plan` に明記する。
- 自己修復: 検証不一致が出た場合、原因切り分け→最小修正→再検証を最大3回まで実施する。
- フェイルセーフ停止: 3回で収束しない場合はスコープを広げず停止し、未達条件と次アクションを記録する。

## 1) 課題 / Problem statement

- 何が困っているか（症状）
- どこで困っているか（対象レイヤ）
- 何が判断不能になっているか（影響）

## 2) 背景 / Context

- 現状仕様・既存実装・既存運用の要点
- 参照すべき正本ドキュメント（ADR / Architecture / Ops）

## 3) 判断基準による優先度評価

`AGENTS.md` の判断軸に沿って 4観点で記述する。

- 価値・判断軸（ADR-0001）:
- 安全（THREAT_MODEL / SafeMode）:
- 企業・行政要件（enterprise_architecture）:
- 後方互換（schemas）:

## 4) 提案する解決策 / Proposed solution

- 変更対象（Docs / Frontend / Backend / Schema）
- 変更の最小単位（再開可能な粒度）
- 非目標（何をこのIssueでやらないか）

## 5) 受入条件 / Acceptance criteria

- [ ] 利用者視点の完了条件
- [ ] 実装/ドキュメント整合条件
- [ ] 安全性/互換性条件
- [ ] 必要な検証（unit/integration/e2e/docs-check）が `Expected verification level` と一致する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 ...
- [ ] T2 ...
- [ ] T3 ...

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `...`
- 期待結果:
  - `...`
- 未実施時の理由・代替検証:
  - `...`

## 8) 代替案 / Alternatives considered

- 代替案A:
- 代替案B:

## 9) リスクとロールバック / Risks & rollback

- 失敗モード:
- 影響範囲:
- ロールバック手順:

## 10) Additional context

- 関連Issue/PR/議論ログ
- ADR化が必要になる条件（トレードオフ閾値）

---

## Authoring Checklist（人間/生成AI 共通）

- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。
