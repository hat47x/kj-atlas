# Issue: DOMAIN-KJ-CAUSAL-DIRECTION-01 `getDerivedIslandEdges()` が `causal` のペアも正規化し、島間の因果方向を約半数で反転させる

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Open
- Source Issue: `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`（Stage 4 の事後検証で付随的に発見。本issueはその是正対象ではなく、別単位の作業として切り出したもの）
- Priority: P2
- Owner: Unassigned
- Scope: `03_Implement/frontend/src/domain/island_edge_aggregate.ts`, `03_Implement/frontend/src/domain/island_edge_aggregate.test.ts`, `03_Implement/frontend/src/domain/island_edge_aggregate.python_equivalence.test.ts`, `03_Implement/backend/tests/fixtures/derived_island_edges_expected.json`（TS側期待値の退役）
- Related ADR/Spec: `02_Architecture/schemas.md` §3.3.1（DOMAIN-KJ-01 方向規約）, `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D2 round 5: 島↔残存カードの表札昇格）, `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`（AC-7 の関数対）
- Expected verification level: unit

## 課題

- 現在の問題:

`02_Architecture/schemas.md` §3.3.1（`schemas.md:373-377`）は方向規約を3行で定めている。

> - **`causal` のみ有向**とし、`fromId`（原因）→ `toId`（結果）を意味方向とする。
> - `related` / `negate` / `mutual` / `equivalence` および未知種別は**無方向**であり、描画・集約・エクスポートで端点順序に意味を持たせない。
> - 集約（島間派生エッジ・abstract map の関係行）では、無方向種別はペアを正規化してよいが、**`causal` はペア正規化を行わず方向を保存**する。

`03_Implement/frontend/src/domain/island_edge_aggregate.ts` の `getDerivedIslandEdges()` は、この3行目に**正面から違反している**。島↔島の昇格分岐で、種別による例外を一切設けずにペアを辞書順へ正規化する（`island_edge_aggregate.ts:143-145`）:

```ts
const [normalizedFromId, normalizedToId] = normalizeUndirectedIslands(fromIslandId, toIslandId);
const key = `derived-island:${normalizedFromId}|${normalizedToId}|${edge.type}`;
addContribution(key, normalizedFromId, normalizedToId, "island", edge, fromKind, toKind);
```

`normalizeUndirectedIslands()`（`island_edge_aggregate.ts:19-21`）は `a <= b ? [a, b] : [b, a]` であり、`edge.type` を見ない。結果として2つの不具合が同時に起きる。

1. **方向の反転**: 原因側の島IDが結果側の島IDより辞書順で後ろにある `causal` 辺は、`fromId`/`toId` が入れ替わって出力される。島IDは実文書では `crypto.randomUUID()` の値であり、辞書順は因果の向きと無関係なので、**該当する島ペアの約50%が反転する**。
2. **逆向き同士の畳み込み**: 正規化されたペアが**集約キー**にも使われているため、島A→島Bの `causal` と 島B→島Aの `causal` が同一キーになり、**1行へ合流して片方が消える**（`aggregateCount` が増えるだけで、逆向きの主張が存在したことは出力から復元できない）。KJ法において「AがBを生む」と「BがAを生む」は別の主張であり、同じ関係を2回見たものではない。

同じリポジトリ内に**正しい実装が既にある**。`03_Implement/frontend/src/export/abstract_map_export.ts:216-223` は、永続化された島↔島辺に対して `causal` を `normalizePair()` から明示的に除外し、根拠として §3.3.1 を引用したコメントまで置いている。

```ts
// DOMAIN-KJ-01 (schemas.md §3.3.1): "causal" is directed (fromId=cause →
// toId=effect), so its pair order must NOT be normalized away in the
// export — swapping would reverse the stated causal direction.
const [islandAId, islandBId] =
  resolveKnownEdgeType(edge.type) === "causal" ? [edge.fromId, edge.toId] : normalizePair(edge.fromId, edge.toId);
```

つまり**同一ファイルの中で、永続化された島間辺は方向を保存し、派生した島間辺（`getDerivedIslandEdges()` 経由、同ファイル242行）は方向を失う**という自己矛盾が生じている。

- 利用者または開発への影響:

`getDerivedIslandEdges()` の呼出は定義を除き**7箇所**（2026-08-31 実測）。方向を読むかどうかで分けると次のとおり。

| 呼出箇所 | 方向を使うか | 影響 |
|---|---|---|
| `canvas/CanvasShell.tsx:869` → `derivedIslandEdgeMeta` → `ui/SidePanel.tsx:3314` | **使う** | **実害あり（利用者に見える）**。辺インスペクタが `side_panel.edge_inspector.endpoint`（`i18n/locales/ja.json:1574` = `端点: {from} ({fromKind}) → {to} ({toKind})`）で**矢印つきに描画**する。派生 `causal` 島関係を選ぶと、約半数で原因と結果が逆に表示される |
| `export/abstract_map_export.ts:242` | **使う** | **実害あり（共有物に残る）**。abstract map の関係行 `islandAId`/`islandBId` の順序が派生 `causal` 行だけ正規化される。上記のとおり同ファイルの永続辺側は方向を保存しており、1つの出力の中で規約が食い違う |
| `domain/geometry/bounds.ts:152` | 使わない | 端点の座標を含めるだけ。両端を等しく扱うので影響なし |
| `domain/view/outline_quality.ts:64` | 使わない | `addEdge(a, b)` が両島の次数を +1 する。順序非依存 |
| `domain/void_detection.ts:89` | 使わない | 同上（孤立島の検出） |
| `domain/void_detection.ts:133` | 使わない | `pairKey()`（`void_detection.ts:127`）が自前で `a <= b` 正規化する。順序非依存 |
| `export/canvas_svg.ts:66` | 使わない | 線を引くだけで矢印マーカーを出力しない |

キャンバス本体の描画は影響を受けない。`canvas/EdgeLayer.tsx:263-269` が派生辺の種別記号・矢羽を意図的に抑止しており、その理由として「派生辺は端点順序が正規化されているので矢羽は誤った向きを指しうる」と明記している。**フロントエンドはこの関数の出力を方向として読めないことを既に知っており、EdgeLayer はそれを回避しているが、SidePanel と abstract map export は回避していない**、というのが現状の正確な姿である。

データ破壊は確認されていない。派生辺自体は保存されず、`RelationSummary` に保存されるのは `islandAId` / `islandBId`（`from`/`to` ではなく A/B の対で命名されており、それ自体は方向を主張しない）。ただし後述のとおり、修正時に signature の互換性を検討する必要がある。

**バックエンド側（Python）は既に §3.3.1 準拠である。** `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py` の `derived_island_relations()` は、`AI-IR-PROJECTION-01` Stage 4 の事後検証で本件と同型の不具合が見つかり、その場で `causal` を正規化から除外する形へ是正した（レンダリング対のみならず**集約キーも**除外）。したがって現在、AI入力経路は正しい方向を渡しており、UI・export だけが反転しうる。

## 対応方針

- 実施すること:
  1. `island_edge_aggregate.ts:135-148` の島↔島昇格分岐で、`causal` をペア正規化から除外する。**除外はレンダリング対（`fromId`/`toId`）だけでなく集約キー（`derived-island:<a>|<b>|<type>`）にも及ぼす** — キーを正規化したままにすると、向きは正しく出るのに逆向き同士が同一エントリへ合流するという別の壊れ方になる。`abstract_map_export.ts:216-223` の例外パターンと、`llm_input_ir.derived_island_relations()` の対応する修正（コメントごと）を雛形にする。種別解決は `resolveKnownEdgeType()` を通す（未知種別は「関連（無方向）」へ解決される §3.3.2-3 の規約に合わせるため）。
  2. `island_edge_aggregate.test.ts` に、原因側の島IDが結果側より辞書順で後ろにある `causal` 辺のケースと、逆向き2本が別行のまま残ることを固定する回帰テストを追加する。現行テストがこの不具合を捕まえられなかったのは、テストの島IDが常に「原因が辞書順で先」だったためである。
  3. AC-7 の共有 fixture から TS 側の暫定期待値を退役させる。`03_Implement/backend/tests/fixtures/derived_island_edges_expected.json` の `tsCurrentDerivedIslandEdges` 配列と `_tsCurrentComment` を削除し、`island_edge_aggregate.python_equivalence.test.ts` を `derivedIslandEdges`（契約正の配列）へ差し戻す。同ファイルの「causal 行のみ乖離する」ことを固定した3件目のテストも削除する（乖離が無くなるため）。Python 側テスト `test_derived_island_relations_ts_equivalence.py` の `_ts_current()` と `test_the_divergence_from_the_ts_implementation_is_confined_to_causal` も同時に削除し、両docstringの「5番目の差異」の記述を「解消済み」へ書き換える。
  4. `RelationSummary` の signature 互換性を判断する。`relation_summary_ops.ts:72-80` の `buildRelationSummarySourceSignature()` は派生辺に対し `derived:${fromIslandId}:${toIslandId}:${type}:${hash}` を返すため、修正で `causal` の対順序が変わる文書では**既存の relation summary が紐付かなくなる**（`abstract_map_export.ts:262` の `relationSummariesBySignature.get()` が外れ、要約が「未作成」として扱われる）。取りうる案は (a) 受け入れて既知の一度きりの失効として記録する、(b) 照合時に causal だけ逆順の signature もフォールバックで探す、(c) 移行処理を書く。**判断は本issue着手時に行い、選んだ理由を結果欄へ記録する**（現時点では未決。実文書での発生件数が不明なため、まず (a) の影響範囲を計測することを推奨する）。
- 実施しないこと:
  - 島↔残存カード（一匹狼）昇格分岐の方向問題（下記「補足」の項目2）。`DerivedIslandEdge.fromKind` が `"island"` リテラルに固定されているため、こちらの修正は**型の変更**を伴い、TS/Python 双方の行形状と全呼出箇所へ波及する。本issueは島↔島ペアの正規化に範囲を閉じる。
  - `EdgeLayer.tsx` の派生辺での種別記号・矢羽の抑止（`EdgeLayer.tsx:263-269`）。これは UX-SCALE-01 のレッドライン（派生辺は種別を主張しない）に由来する独立の判断であり、本修正で自動的に解除してよいものではない。解除の要否は別途判断する。
  - `derived_island_relations()`（Python）の再変更。既に §3.3.1 準拠であり、本修正は Python を TS に合わせるのではなく**TS を契約に合わせる**方向で行う。

## 受入条件

- [ ] AC-1: `getDerivedIslandEdges()` が `causal` 辺について `fromId`（原因）→ `toId`（結果）を保存する。原因側の島IDが結果側より辞書順で後ろにある fixture で、`fromId` が原因島であることがテストで示される。
- [ ] AC-2: 島A→島B と 島B→島A の `causal` が**別々の `DerivedIslandEdge`** として出力される（集約キーが方向を含む）。両者の `aggregateCount` が独立に数えられることがテストで示される。
- [ ] AC-3: `related` / `negate` / `mutual` / `equivalence` / 未知種別のペア正規化と集約挙動は**変わらない**ことが既存テストで示される（`island_edge_aggregate.test.ts` の既存11件が無改修で通る、または変更が必要になった件があればその理由が記録される）。
- [ ] AC-4: AC-7 の共有 fixture が単一の期待値配列（`derivedIslandEdges`）へ戻り、TS 側・Python 側の両テストが同じ配列を突き合わせる。`tsCurrentDerivedIslandEdges` が削除され、両側のdocstringから「5番目の差異」の記述が消える。
- [ ] AC-5: `RelationSummary` signature の互換性について、採った案（受容／フォールバック／移行）と理由が本issueの結果欄に記録される。

## 検証計画

- 実行する確認:
  - `npm run typecheck`
  - `npx vitest run src/domain/island_edge_aggregate.test.ts src/domain/island_edge_aggregate.python_equivalence.test.ts`
  - `npx vitest run src/domain src/export src/view`（`outline_quality` / `void_detection` / `abstract_map_export` / `canvas_svg` の回帰）
  - `wsl -e bash -lc 'cd /mnt/d/GIT/kj-atlas/03_Implement/backend && .venv/bin/python -m pytest tests/test_derived_island_relations_ts_equivalence.py -q'`（fixture を共有しているため、TS側の修正で Python 側テストも影響を受ける）
  - `python3 01_Plans/docs_check.py`
- 期待結果: 新規テストがグリーン。方向を使わない5呼出箇所（`bounds` / `outline_quality` / `void_detection` ×2 / `canvas_svg`）の既存テストに regression が無いこと。`abstract_map_export` の派生 `causal` 行の対順序が変わることによる期待値更新は、変更理由を明記した上で許容する。

## 補足

- **発見の経緯**: 本件は `getDerivedIslandEdges()` を対象とした監査で見つかったものではない。`AI-IR-PROJECTION-01` Stage 4（`suggest-layout` のIR経路化）が、この関数の Python 対応実装 `derived_island_relations()` を新規に書き、AC-7 の同値性スポットチェックを追加した。その変更に掛けた独立レビューが Python 側の同型の不具合（プロンプトへ `- island "X" --causal--> island "Y"` と描く行で方向が反転しうる）を指摘し、是正の過程で「TS 側は同じことを最初からしている＝Python は忠実に移植した結果バグまで移植していた」ことが判明した。**したがって本件は本ロールアウトが作り込んだものではなく、それ以前から存在していた。**
- **意図的に残っている同型の問題（本issueの範囲外）**: 島↔残存カード（一匹狼）昇格分岐（`island_edge_aggregate.ts:151-165`、Python 側も同じ）は、`fromKind` を常に `"island"` として島を先に置く。`causal` 辺の**原因が一匹狼カードの側**にある場合、出力は島→カードとなり向きが逆になる。これは正規化の問題ではなく `DerivedIslandEdge` の行形状（`fromKind: "island"` リテラル）の制約であり、修正には型変更と全呼出箇所の追随が要る。Python 側 `derived_island_relations()` の docstring にも同じ限界として明記してある。**別issue化するか本issueの第2ラウンドとするかは、本issueの1ラウンド目完了時に判断する。**
- **fixture の共有関係**: `03_Implement/backend/tests/fixtures/derived_island_edges_document.json` / `..._expected.json` は backend 配下にあるが TS 側テストからも読まれる（`island_edge_aggregate.python_equivalence.test.ts:56` が `../backend/tests/fixtures` を解決する）。TS 側だけを直したつもりでも Python 側テストが落ちるので、両方を1コミットで扱う。
- 本リポジトリは複数の生成AIセッションが同一ワークツリーを共有する運用がある（`01_Plans/agent_failure_lessons.md` 参照）。実装前に `git status --short` で作業中ファイルの有無を確認する。
