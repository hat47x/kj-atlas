# Issue: DOMAIN-SCORING-SURFACE-01 利用者の図解に「健全性 N%」が表示されており、孤立カードが欠陥として扱われている

- Type: Product Invariant
- Status: Done
- Source Issue: `AI-IMPORTANCE-SCORING-01`, `DX-CANON-INTENT-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/view/outline_quality.ts`, `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/src/i18n/locales/ja.json`, `03_Implement/frontend/src/domain/view/recommendations.ts`, `03_Implement/frontend/src/domain/view/structural_metrics.ts`
- Related ADR/Spec: `02_Architecture/design/ui_design_handoff.md`, `00_Prompt/kj_technique.md`, `00_Prompt/domain.md`, `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`
- Norms: `DOM-CORE-04`, `DOM-AI-07`, `KJT-SIGN-03`
- Expected verification level: `unit`

## 課題

### 事実1: 利用者の統合結果に0〜100の点数が表示されている

```ts
// 03_Implement/frontend/src/domain/view/outline_quality.ts:225
health: Math.max(0, 100 - severityPenalty),
```

```json
// 03_Implement/frontend/src/i18n/locales/ja.json:263
"side_panel.outline.health": " · 健全性 {health}% (推定)",
```

`SidePanel.tsx` から描画される。すなわち**利用者が自分の図解に対して「健全性 72%」のような点数を提示される**。

これは宣言済みの不変条件と正面から抵触する。

> `02_Architecture/design/ui_design_handoff.md:32`
> 単一正解、ランキング、**採点**、準備度スコアで結論を誘導しない。

条件節を伴わない禁止である。三要素牽制チェックリストの **B2** そのものであり、この画面はゲートを通っていない。

### 事実2: 孤立カードが「欠陥」として提示されている

```ts
// outline_quality.ts:182-187
code: "Q007",
title: "Lone cards are present",
detail: `${loneCards.length} card(s) are not assigned to any island.`,
suggestedAction: "Group lone cards into islands when they should be part of the explainable structure.",
```

方法論の正本は逆を述べている。

> `00_Prompt/kj_technique.md` §2 束ねる（グループ編成）。孤立カードをゼロにすることは `KJT-SIGN-03` が失敗の徴候として挙げている
> 孤立した1枚が最も重要なことがある。

さらに `kj_technique.md:195` は**孤立カードがゼロであること自体を失敗の徴候**として挙げている。つまり Q007 は、方法論が「探索が足りない証拠」と呼ぶ状態へ利用者を誘導している。`suggestedAction` には "when they should be" という留保が付いているが、**所見（finding）として提示されている時点で「解消すべきもの」という枠組みを与えている**。

同様の傾向が `Q005 "Many islands are disconnected"` にもある。`kj_technique.md` §4 は島の真の独立性を価値として扱う。

### 事実3: 同じクラスの surface が他にもある

- `domain/view/recommendations.ts:9-18` — `priority: number`、`impactLevel: high|medium|low`、impact rank でソート
- `domain/view/structural_metrics.ts:13` — `connectivityScore`

### なぜこれが今の優先事項か

`AI-IMPORTANCE-SCORING-01`（Done, 2026-08-11）は、**まったく同じ不変条件**（`00_Prompt/domain.md`「AIは内容を採点せず」）を根拠に `POST /ai/assess-card-importance` を削除し、`test_ai_anti_scoring_contract.py` で復活を禁じた。その判断は正しい。

**しかしその防御はバックエンドのAI経路にしか及んでいない。** 利用者に見える画面上の採点は、AI経由ではなくクライアント側の決定論的計算であるため、当時の判断の射程外に落ちた。結果として:

| 経路 | 採点 | 状態 |
|---|---|---|
| AI（サーバ） | カード重要度 high/medium/low | **削除済み・テストで固定** |
| 画面（クライアント決定論） | 健全性 N% | **出荷中・誰も検査していない** |
| 書き出し/取り込み境界 | score/rank/confidence/priority | **検査済み**（`agent_task_export.test.ts:106`、`agent_response_import.ts:177-184`、`verify_mcp.ts:104-110`） |

書き出し境界とMCP経路では `score` / `rank` / `confidence` / `priority` の混入を明示的に検査しているのに、**利用者が最も長く見る画面には検査が無い**。防御の周縁が中心より厚いという逆転が起きている。

これは `DX-DESIGN-CHECK-01` / `DX-CONTRACT-DRIFT-01` / `DX-CANON-INTENT-01` / `QA-TENANT-ISOLATION-01` と同じ「**保護の主張と保護の実効範囲の乖離**」であり、5件目にあたる。

## 対応方針

- 実施すること:
  1. **判断を仰いだうえで**、`health` の提示形式を決める（下記論点）。
  2. Q007 / Q005 の扱いを方法論と整合させる。孤立カードは「所見」ではなく**中立な事実の提示**（例: 「島に属さないカード: 3枚」）とし、`suggestedAction` の解消誘導を外す。ゼロのときにこそ注意を促すのが方法論に忠実（`kj_technique.md:195`）。
  3. `recommendations.ts` / `structural_metrics.ts` の数値提示を棚卸しする。
  4. 画面表示に対する反スコアリング検査を追加する。書き出し境界と同じ形式（禁止語彙 + 数値提示の形式検査）をUI層へ適用する。
- 実施しないこと:
  1. 品質検査ロジック自体の削除。**検査は方法論が要求している**（`kj_technique.md` §6 の失敗の徴候12項目）。問題は検査の存在ではなく、その結果を**点数へ畳んで提示している**ことにある。

## 論点（保守者判断が必要な理由）

`health` をどうするかは3案ある。方法論の解釈が絡むため保守者判断とする。

- **案A: 点数を廃し、件数と種別で提示する。** 「未検討の指摘: 4件（うち重大 1件）」。`kj_technique.md:185` が A/B照合について「報告は件数で」と明示しており、**方法論はすでに件数を正しい提示形式として指定している**。最も整合する。
- **案B: 点数を残し、上昇を良しとしない文脈へ置く。** 「健全性」という語を捨て、100%を目標としない旨を併記する。ただし数値である限り最大化圧力は残り、`ui_design_handoff.md:32` の「準備度スコア」に該当し続ける懸念がある。
- **案C: `ui_design_handoff.md:32` を改める。** 採点を許容する範囲を明文化する。`ADR-0041` の CVI 群および KJ法の方法論的根拠との整合を示す必要がある（`AI-IMPORTANCE-SCORING-01` の D-c と同じ構造）。

**案Aを推奨する。** 方法論が件数という提示形式を既に指定しており、検査ロジックを一切失わずに不変条件と整合できる。

## 受入条件

- [x] AC-1: 上記案から方針を決定する。— **案A（点数を廃し、件数と種別で提示）を採択**。方向性レビュー優先2と方法論（`kj_technique.md:185`「報告は件数で」）が同一の指針を指定しており、検査ロジックを失わずに不変条件と整合できるため。仮承認に基づき採択。
- [x] AC-2: `outline_quality.ts` の提示が採択案に従っている。案Aの場合、0〜100の数値が画面に現れない。— `health` フィールドを `OutlineQualityReport` から削除し、`SidePanel` の描画と i18n キーを撤去。
- [x] AC-3: Q007 が孤立カードを欠陥として提示していない。孤立カードがゼロの場合の注意喚起が方法論（`kj_technique.md:195`）に従って存在する。— Q007 を `info` の中立事実へ変更（`suggestedAction` 撤去・`kj_technique.md:109`「孤立した1枚が最も重要なことがある」を明記）。ゼロ枚時は新コード **Q009**（`warn`・forced-grouping の失敗徴候）を発行。
- [x] AC-4: `recommendations.ts` / `structural_metrics.ts` の数値提示が棚卸しされ、採択案に従っている。— 棚卸し結果: `connectivityScore` は表示（SidePanel metrics・`diagnostics.md`）から撤去（内部計算は維持・`structural_metrics.test.ts` は継続）。`recommendations.impactLevel` / `priority` は内部ソート用に維持し、表示（バッジ・エクスポートタグ・高影響フィルタ）を撤去。Q005 は `info` の中立観察へ変更（島の独立性を価値とする方法論 §4 と整合）。
- [x] AC-5: UI層への反スコアリング検査がテストで固定されている（書き出し境界の既存検査と同形式）。— `worker_golden.test.ts` に `diagnosticsMd`（SidePanel表示・診断追記・bundle export の表面）が `/score|rank|confidence|priority|readiness|優先度の数値|点数|順位/i` に一致しないことを固定。`outlineReport` に `health` が存在しないことも固定。
- [x] AC-6: `AI-IMPORTANCE-SCORING-01` へ、同一不変条件の防御がクライアント側に及んでいなかった事実を追記する（判断の取り消しではなく記録の正確化として）。— `01_Plans/issues/done/issue-AI-IMPORTANCE-SCORING-01-importance-rating-conflicts-with-no-scoring.md`「記録の正確化（2026-08-13、DOMAIN-SCORING-SURFACE-01 AC-6）」節として追記済みであることを確認した。

## 対応記録（2026-08-13）

案Aを採択し、出荷中の採点面を件数・種別へ転換した。

- `outline_quality.ts`: `health`（0〜100点数）を削除。Q007 を中立事実化。Q009（ゼロ孤立カードの注意喚起）を追加。Q005 を中立観察（`info`）化。
- `SidePanel.tsx`: health / `connectivity_score` / 推奨の impact バッジ / 高インパクトフィルタを撤去。
- `diagnostics_compute.ts` / `bundle_export.ts`: `connectivityScore` 行・推奨の impact タグを撤去。
- `recommendations.ts`: rec-q007 を「孤立カードの意図を確認する」へ再構成（方法論に整合・解消誘導を外す）。
- i18n: 未使用キー（`health`・`connectivity_score`・`impact.*`・`high_impact_only`）を ja/en から削除。
- テスト: `worker_golden.test.ts` に UI 反スコアリング検査を追加。ゴールデンフィクスチャ `diagnostics.md` を更新。`outline_quality.test.ts` / `translate.test.ts` を更新。フロントエンド全 1439 tests pass、typecheck・build 成功。

検証: `cd 03_Implement/frontend && npm run test && npm run typecheck && npm run build`、`python 01_Plans/docs_check.py`（pass）。

## 対応記録2（2026-08-25・再検証・Close out）

AC-1〜5は2026-08-13の対応記録で完了済み、AC-6は`AI-IMPORTANCE-SCORING-01`側への追記として既に実施済み（本issue起票時の記述漏れ）だったが、Statusが`In Progress`のまま残っていた。`outline_quality.ts`に`health`フィールドが存在しないこと・`Q009`が存在することをコード上で再確認し、`01_Plans/docs_check.py`が通過することを確認した。Statusを`Done`へ更新し、`done/`へ移動する。

## 検証

```bash
cd 03_Implement/frontend && npm run test -- outline_quality
cd 03_Implement/frontend && npm run typecheck
python 01_Plans/docs_check.py
```

## 補足

- 発見経緯: ドッグフーディングの方向性レビューで、KJ法の実装忠実度を三要素の観点から調査した際に検出した。
- 三要素牽制の観点: 業務設計（「採点で結論を誘導しない」）は明文で存在し、**機能設計（AI経路）とデータ設計（書き出しスキーマ）には反映されている**が、**画面という第3の機能面には反映されていない**。同じ不変条件が経路ごとに個別実装されており、横断的に効かせる機構が無い。`ADR-0041`（core value invariants single guard）が「single guard」を掲げているにもかかわらず、実際には経路ごとに別々の守り方をしている。この観測は `ADR-0041` の再検討材料となりうる。
- 本件は**ドッグフーディングでは見つからなかった**。自己言及題材（設計判断・issue・ADR）では図解の「健全性」を気にする場面が起動しないためである。`01_Plans/dogfood/adopting-org-patterns.md:9-15` が「未分化な違和感・保留・曖昧な意味を扱う操作は、自己言及題材では起動しにくい」と既に記録しており、本件はその予測が的中した実例にあたる。
