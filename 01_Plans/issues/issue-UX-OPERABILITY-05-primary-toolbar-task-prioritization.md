# Issue Draft: UX-OPERABILITY-05 主要ツールバーにレガシー/高度操作が混在している

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/`, `04_Documentation/acceptance_check.md`
- Related Backlog: `UX-OPERABILITY-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-OPERABILITY-05
- RequirementStatement: 初回利用者が主要ツールバーで、現在推奨される基本操作とレガシー/高度操作を混同しない。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプル `doc_phase1_canvas` を開く / 操作=ヘッダーと主要ツールバーをマウス・キーボードで確認する / 期待結果=新規、開く、保存、表示、共有、安全確認が優先され、レガシーJSON操作は補助導線として区別される / 除外=import/export機能そのものの削除。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0030`

## 1) 課題 / Problem statement

- 起動直後の主要ツールバーに `JSON取り込み` / `JSON書き出し` が表示され、操作後には「レガシー導線です。順序化された Diff/Verify フローには『共有と再現』を使用してください。」という案内が出る。
- 利用者の視点では、画面上で目立つ主要ボタンが非推奨に近い導線であり、推奨される `共有と再現` との関係が分かりにくい。
- `Tab` 順序でもレガシーJSON操作が早い段階に入り、保存やカード操作より前後の文脈で迷いやすい。

## 2) 背景 / Context

- 共有/復元/パッチ/安全確認は `SharePanel` 側に順序化されつつある。
- 既存のlegacy import/exportは後方互換や緊急操作として必要だが、一般利用者向けの主導線としては説明負荷が高い。
- MVP脱却では、初回導線から仮実装・レガシー導線・高度操作を整理する必要がある。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 思考整理の主作業に入る前に、ファイル操作の選択肢で迷う負荷を下げる。
- 安全（THREAT_MODEL / SafeMode）: export/share はSafeMode確認と結びつくため、推奨導線へ誘導する価値がある。
- 企業・行政要件（enterprise_architecture）: 組織導入では推奨手順とlegacy手順が明確に分かれる必要がある。
- 後方互換（schemas）: legacy導線を即削除せず、配置とラベルを整理する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 主要ツールバーの情報優先順位。
  - legacy JSON import/export の配置、ラベル、補足説明。
  - `SharePanel` への推奨導線。
- 変更の最小単位:
  - legacy JSON操作を「その他」または `共有と再現` 内の補助導線へ移し、ツールバー上では推奨操作を優先する。
- 非目標:
  - legacy JSON import/export の機能削除。
  - patch/review pack の仕様変更。

## 5) 受入条件 / Acceptance criteria

- [ ] 初回表示の主要ツールバーで、現在推奨される基本操作が優先表示される。
- [ ] legacy JSON import/export は補助導線として区別される。
- [ ] `共有と再現` が推奨される理由が、操作直後の警告だけでなく事前に分かる。
- [ ] キーボードの早いTab順序で、非推奨に近いlegacy導線が主要操作より目立ちすぎない。
- [ ] 既存のlegacy import/export機能は必要時に到達可能である。
- [ ] 受け入れ確認文書が、推奨導線とlegacy導線を混同しない説明になっている。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 ツールバー上の主要/補助/legacy操作を分類する。
- [ ] T2 legacy JSON操作の配置変更案を作成する。
- [ ] T3 `SharePanel` への推奨導線と説明を更新する。
- [ ] T4 E2Eまたは操作確認でTab順序と表示優先度を検証する。
- [ ] T5 `04_Documentation/acceptance_check.md` を同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/i18n/ui_hardcode_guard.test.ts src/ui/i18n_equivalence.integration.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
- 期待結果:
  - ツールバーは見切れず、推奨導線とlegacy導線が区別される。
- 未実施時の理由・代替検証:
  - 自動E2E更新前は、Playwright script のTab順序ログとスクリーンショットで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: legacyラベルだけ詳しくする。主要ツールバーで目立つ問題は残る。
- 代替案B: legacy機能を即削除する。既存利用者とデバッグ導線への影響が大きいため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: legacy操作を見つけられず、検証やデータ復旧がしづらくなる。
- 影響範囲: ヘッダー/ツールバー、SharePanel、受け入れ確認、E2E。
- ロールバック手順: 配置変更を戻し、legacyボタンを従来のツールバー位置へ戻す。

## 10) Additional context

- 2026-05-14 検証:
  - 起動直後の主要ツールバーに `JSON取り込み` / `JSON書き出し` が表示された。
  - 画面本文には「レガシー導線です。順序化された Diff/Verify フローには『共有と再現』を使用してください。」が表示され、推奨導線との二重性が確認された。
  - 右端見切れは `390px` / `960px` / `1440px` の代表確認では再発なし。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
