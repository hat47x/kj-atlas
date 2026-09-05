# Issue: DOGFOOD-35 島要約の壁打ち履歴を文書へ永続化する（違和感・再提案の記録）

- Type: Feature（W型探求・R6手順計画 Phase 2b の残タスク。DOGFOOD-34 の後続）
- Status: Done
- Source Issue: DOGFOOD-34（壁打ち）の「実施しないこと」に挙げていた「対話履歴の永続化」の解消。凝縮ロードマップ Phase 2b の最終ピース。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`（`handleAdoptIslandSummaryProposal`）, `SidePanel.tsx`（critiqueText の受け渡し）, `03_Implement/frontend/src/domain/types.ts`（`CritiqueInput`/`ReproposalDiff` 既存型）
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`（DOMAIN-EXPR-03 違和感→再提案）, `02_Architecture/schemas.md`（`critiqueInputs`/`reproposalDiffs`）, `03_Implement/frontend/src/domain/hil_rs_payload.ts`（既存 HIL-RS 基盤）, `inquiry_bundle_safe_mode.ts`（critiqueInputs=rebuild / reproposalDiffs=omit）
- Expected verification level: `unit` + `typecheck`

## 課題

壁打ちループ（候補提示→違和感→再生成→採用）は DOGFOOD-34 で完成したが、**違和感（critique）と再提案（reproposal）が文書に永続化されない**。現状は違和感がリクエスト内の一時入力（`critiqueText`）に留まり、採用後は `summaryHistory` に要約だけが残る。そのため「なぜこの要約を採用したか」の説明可能性（可逆・監査）が欠ける。

DOMAIN-EXPR-03（ADR-0040 Phase 3）は「違和感→再提案の日常ループ」を第一級化する方針であり、島要約の壁打ちはその典型。既存の `CritiqueInput`/`ReproposalDiff` 型・SafeMode ポリシー（`critiqueInputs`=rebuild・`reproposalDiffs`=omit）は既にあるが、島要約の壁打ちからこれらを記録する導線が無い。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は壁打ちで違和感を言語化し、AIの再提案を採用する。違和感・再提案を文書へ記録することで、採用理由が可逆・説明可能になる。AI は違和感を解消せず保持対象として扱う（CVI-7） | 機能: 採用時に `critiqueInputs`/`reproposalDiffs` を append する。データ: 違和感は人間の発話（未レビュー本文送出の対象外） |
| **データ設計** | `critiqueInputs`（違和感・人間発話）は SafeMode で **rebuild（sanitize して AI へ送る）**、`reproposalDiffs`（再提案差分）は **omit（AI へ送らない・人間監査用）**。両フィールドとも DocumentV1 に既存（schemas.md §9 / models.py / types.ts） | 業務: 違和感の記録は自動採否でなく人間の明示操作（adopt）に伴う。機能: 新規フィールド追加なし（既存型へ append するだけ） |
| **機能設計** | `handleAdoptIslandSummaryProposal` が採用時に、`CritiqueInput`（targetRef=`island:<id>`・critiqueType=`feels_off`・comment=違和感）と `ReproposalDiff`（relabel 前後差分）を生成し、`document.critiqueInputs`/`reproposalDiffs` へ append する。既存 `updateIslandSummaryWithHistory` の延長 | 業務: proposal-only・human_reviewed 緩和禁止を維持（記録は adopt に伴い、AI は自動適用しない）。データ: 接地・SafeMode ポリシーは既存のまま |

## 対応方針

- 実施すること:
  1. `SidePanel.tsx` が adopt 時に違和感テキスト（`islandSummaryCritique`）を `onAdoptIslandSummaryProposal(candidateIndex, critiqueText)` で渡す。
  2. `App.tsx` の `handleAdoptIslandSummaryProposal` が、critiqueText がある場合に `CritiqueInput` を、`before`（旧要約）→`after`（採用要約）の `ReproposalDiff` を生成して append する。
  3. 既存 HIL-RS 基盤（`buildHilRsCritiqueInputs`/`ReproposalDiff` 型）を参考に、島要約専用の生成ロジックを実装（新規スキーマ・新規バックエンド不要）。
- 実施しないこと:
  - 対話履歴の専用UI表示（`critiqueInputs`/`reproposalDiffs` の閲覧画面）。記録の永続化のみ。
  - バックエンド変更・スキーマ変更（既存フィールドへ append するだけ）。
  - AI による違和感の自動解消（CVI-7 維持）。

## 受入条件

- [x] 壁打ちで違和感を入力して採用すると、`document.critiqueInputs` に `CritiqueInput`（targetRef=島・comment=違和感）が記録される。
- [x] 採用時に `document.reproposalDiffs` に旧要約→採用要約の relabel 差分が記録される。
- [x] 違和感なしの採用では従来挙動（critiqueInputs/reproposalDiffs を増やさない or 最小限）。
- [x] SafeMode ポリシー（critiqueInputs=rebuild / reproposalDiffs=omit）を緩和しない。
- [x] tsc typecheck と関連 frontend テストが通過する。

## 実装（2026-08-21）

- `SidePanel.tsx` — adopt 時に `islandSummaryCritique`（trim）を `onAdoptIslandSummaryProposal(candidateIndex, critiqueText)` で渡す。
- `App.tsx` — `handleAdoptIslandSummaryProposal(candidateIndex, critiqueText)` が、違和感がある場合に `CritiqueInput`（critiqueType=`feels_off`・targetRef=`island:<id>`）と `ReproposalDiff`（relabel・旧要約→採用要約）を生成し `nextDocument.critiqueInputs`/`reproposalDiffs` へ append する。
- 検証: tsc typecheck 通過、`src/domain/validate.test.ts` 20件通過（CritiqueInput/ReproposalDiff 型の往復は既存 validate で担保）。

## 補足

- DOGFOOD-34 の Phase 2b「対話履歴の永続化」を本issueへ切り出した。壁打ちの中核（候補・違和感再生成・採用）は DOGFOOD-34 で完了済み。
- `iteration` は既存の `critiqueInputs` 件数から導出（初回=1）。より厳密な iteration 管理は後続で検討。


## 配置の整理（2026-09-05）

- 本Issue群は、島要約の凝縮支援を単一候補から複数候補へ拡張し、違和感を踏まえた再生成、さらに採用時の critique / reproposal 履歴永続化まで段階的に完成させた機能契約成熟系列として `Done` となっていた。
- `DOGFOOD-33` が複数候補と候補単位の接地検証、`DOGFOOD-34` が違和感入力を受けた再生成と代替候補採用、`DOGFOOD-35` が採用理由・再提案差分の文書永続化を完成させたため、3件を同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は17から14へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
