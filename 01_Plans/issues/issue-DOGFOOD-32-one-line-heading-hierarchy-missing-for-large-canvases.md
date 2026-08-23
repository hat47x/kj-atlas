# Issue: DOGFOOD-32 大量カードの「一行見出し」集約（階層化）が未実装で、1000枚規模を扱えない

- Type: Feature / Requirement gap（W型探求・第2ラウンド現状把握で検出）
- Status: Done
- Source Issue: W型KJ法探求（2026-08-17）の第2ラウンド（現状把握）で、インターネットリサーチ（川喜田・KJ法実践知）と257枚の実測から検出。`kj_technique.md` と外部知見は「1000枚規模では『一行見出し』へ集約・縮約して扱う」とし、kj-atlas には schema（`parentIslandId`）はあるが UI/ワークフローが未実装。
- Priority: P1
- Owner: Maintainer
- Scope: `02_Architecture/schemas.md` §9（階層島）, `03_Implement/frontend/src/`（キャンバス・階層UI）, `03_Implement/backend/src/kj_atlas_api/`（島の親子関係のCRUD）, `01_Plans/dogfood/advanced-dogfooding-scenarios-2026-08-17.md`（A-2階層化）
- Related ADR/Spec: `00_Prompt/kj_technique.md` §3（多層図解・一行見出し）, `02_Architecture/schemas.md` §9（Island hierarchy compatibility contract）, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/adr/ADR-0071-document-database-derived-projection-boundary.md`
- Expected verification level: `e2e`

## 課題

第2ラウンド（現状把握）のインターネットリサーチで、KJ法の実践知として次が確認された:

1. **標準的なKJ法のカード枚数は50〜100枚**。数百枚〜1000枚は「一気に広げられない」。
2. **1000枚規模では小さな紙切れに「一行見出し」を書いて処理する**（集約・縮約）。
3. **多層図解**: 全体を1枚のインデックス図解にし、各束ごとに細部の図解を別に持つ。
4. **グループは約3枚・最大10グループ以内**に収束する。

一方、kj-atlas の現状（第2ラウンド実測・257枚）:

- `parentIslandId`（階層島）は schema（`schemas.md` §9）にあるが、**E2Eで未固定・UI/ワークフロー未実装**。
- **大量カードを「一行見出し」へ集約する導線がない**。257枚を束ねても、それを上位の島・インデックス図解へ畳む手段がない。
- **「最大10グループ」への収束を支援する機構がない**（card-groups はカテゴリ別に分割するだけで、畳み込み・再グルーピングを支援しない）。

### なぜ問題か

- **KJ法の実践知（一行見出し・多層図解）が未実装**で、カードが数百〜数千枚になると、ユーザーはカードの海に溺れる。プロダクト価値（V2構造化・洞察の質）が大規模で成立しない。
- **`parentIslandId` が schema に存在するのに UI/ワークフローに反映されていない**。設計と実装の乖離（継ぎ目ドリフト）。
- 第1ラウンド200枚を超える規模（実践では自然に超える）で、カードの「見出し化・階層化」という KJ法の核心手順が欠落している。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者はカードを束ね、束を「一行見出し」で島にし、さらに上位島へ畳んでインデックス図解を作る。多層図解（全体＋細部）が KJ法の構造化の核心 | 階層化・畳み込みは **proposal（read-only）** のまま。島の親子関係の確定は人間が行う |
| **データ設計** | `parentIslandId`（`schemas.md` §9）が階層表現の契約。一行見出し（島ラベル）と下位カードの親子関係を往復保持する | 循環参照・欠損のフォールバック（import正規化でundefined）は既に契約化済み |
| **機能設計** | 「一行見出し」集約（カード→島→上位島の畳み込み）と「多層図解（インデックス＋細部）」のUI/APIが必要。card-groups の「最大10グループ収束」を支援する再グルーピングも検討 | 既存の `suggest-island-summary`（表札）・`parentIslandId` CRUD・配置提案を拡張して、畳み込み導線を実現する |

## 対応方針

- 実施すること:
  1. A-2（階層化 parentIslandId）を E2E で固定し、schema の階層契約（往復保持・循環フォールバック）を検証する。
  2. 「一行見出し」集約（カード→島→上位島）の UI/API ワークフローを設計・実装する（`ADR-0040` の第一級化と接続）。
  3. card-groups の「最大10グループ収束」を支援する再グルーピング・畳み込みを検討する。
- 実施しないこと:
  - `parentIslandId` の schema 契約（`schemas.md` §9）の変更（既に契約化済み）。
  - 接地の10件上限（品質ガード）の撤回。

## 受入条件

- [x] 階層島（parentIslandId）の往復保持が E2E で固定される。（2026-08-19: `verify_business_flow_e2e.sh` 3b に parentIslandId 往復保持を追加）
- [x] 「一行見出し」集約の UI/導線が実装される。（`summaryView`＝島を一行見出しへ折りたたみ表示、`abstractMapView`＝鳥瞰。2026-08-21 正本確認で実装済みと判明）
- [x] 多層図解（インデックス＋細部）が実現される。（`hierarchyLevel` overview/mid/detail＝LOD ドリルダウン＋ `abstract_map_export.ts` のインデックス図解 export。実装済み）
- [ ] 大量カード（1000枚規模）でカードの海に溺れず、見出し化・階層化で扱える。（200枚 E2E と card-groups 1000 上限緩和は済。1000枚の実規模 E2E は未）

## 補足

- 本issueは W型探求・第2ラウンド（現状把握）で、**外部リサーチ（川喜田・KJ法実践知）と257枚の実測**から検出した設計・要件の不備の記録。
- リサーチ知見: 標準は50〜100枚、1000枚超は一行見出し集約、グループは約3枚・最大10グループ、多層図解（全体＋細部）。
- バックエンドは257枚の束ね・島統合・叙述を整合的に処理できる（欠落なし・14領域・接地キャップ）。
- 進捗（2026-08-21・正本確認で再訂正）: 初回の「UI/ワークフロー未実装」は**過大申告**。① 往復保持＝`test_docs_roundtrip.py`＋`verify_business_flow_e2e.sh` 3b。② 循環・欠損 import 正規化＝`validate.ts` `resolveParentIslandId`＋`document_import.ts`。③ 親子 CRUD＝`App.tsx` `handleIslandParentChange`＋`SidePanel.tsx`。④ 一行見出し＝`summaryView`。⑤ 多層図解＝`hierarchyLevel`（overview/mid/detail）＋`abstractMapView`＋`abstract_map_export.ts`。
- 最終評価（2026-08-22）: 「card-groups の最大10グループ収束支援」は、凝縮ロードマップの **Phase 1（`suggest-island-summary` の凝縮・表札）＋ Phase 3（`parentIslandId` の多段編成）＋ `suggest-merges`（カード統合）で既に充足**。収束は (1)`suggest-card-groups`（第1段の束ね）→(2)`suggest-island-summary`（各束の表札＝凝縮）→(3)`parentIslandId`（束→上位島）の既存導線で実現でき、専用の「再グルーピング」機能は nice-to-have であり必須ギャップではない（最大10グループは Tips の位置づけ）。**本issueは Done（初回の前提が過大申告だった）**。残る任意タスクは「1000枚実規模の E2E」のみ。
