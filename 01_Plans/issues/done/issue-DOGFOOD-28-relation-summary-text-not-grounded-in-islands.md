# Issue: DOGFOOD-28 島間関係要約の本文（text）が島A/Bを参照せず、E2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 192（シナリオ122・映画館 実装時の実走行観察）。`summarize-island-relation` の本文（`text`）が**常に汎用文字列**（「島間の関係に関する下書きの示唆です」）で、**どの島（islandA/islandB）の関係かを示さない**ことを再現確認した。DOGFOOD-15 で接地カード（groundingCardIds）は固定済みだが、本文が島ペアを参照しない。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ122）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §4（島間関係線）, `02_Architecture/api.md`（summarize-island-relation 契約）, `01_Plans/issues/done/issue-DOGFOOD-15-island-relation-summary-grounding-always-empty.md`（接地カードの保全）, `01_Plans/issues/done/issue-DOGFOOD-21-narrative-text-not-grounded-in-reading-order.md`（テキスト接地の同型）
- Expected verification level: `e2e`

## 課題

業務フローE2E の `summarize-island-relation`（島間関係要約）はシナリオ48/66/106/110等が固定するが、全シナリオが `"text"` キーの存在（+ DOGFOOD-15 以降の接地カード）だけを確認し、**本文がどの島（islandA/islandB）の関係かを参照しているか**は検証しない。モックの本文は常に同一の汎用文字列:

```python
"text": "（モック）島間の関係に関する下書きの示唆です。確証ではありません。"
```

したがって:

- **関係要約の本文が島ペア（どの島とどの島の関係か）に接地しているか**を E2E で一切検証できない。
- バックエンドが関係要約を無関係な/汎用的な本文に劣化させる回帰（どの島間の関係かを示さない）が起きても、業務フローE2E は全部 pass する。
- 関係要約は「島間の関係を示唆」するものであり、島ペアに接地していなければ意味を成さない。

実機再現（iteration 192）:

```text
# islandAId=cine-sched / islandBId=cine-ops で summarize-island-relation
# → text="（モック）島間の関係に関する下書きの示唆です。確証ではありません。"
#   （島ペアを一切参照しない）
```

### なぜ問題か

- **関係要約の島ペア接地が未検証**: 本文がどの島間の関係かを示さないと、人間が関係の根拠を確認できない。
- **接地カードの保全（DOGFOOD-15）と本文の接地が別**: 接地カードは固定されたが、本文の島ペア参照は未固定。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は「島Aと島Bの関係」を**島ペアに接地した要約**として得たい。汎用本文ではどの関係かを判断できない | 関係要約は **proposal 相当（read-only の下書き）** のまま。自動適用しない |
| **データ設計** | 関係要約のプロンプトは `islandAId="<id>", islandBId="<id>"` を含むため、モックは**島A/BのIDを本文へ埋め込む**ことで「島ペアへの接地」を決定的に表現できる | 既存の `"text"` キー assert（scenario 48/66/106/110等）は、本文に島IDを埋めても成立（非後退） |
| **機能設計** | `summarize_island_relation` の本文を「（モック）島<A>と島<B>の関係に関する…」へ変更し、シナリオ122の関係チェックで**本文が島A/Bを参照**することを assert する。API契約（`SummarizeIslandRelationResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオは `"text"` キー assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `summarize_island_relation` で、プロンプトの `islandAId` / `islandBId` を抽出して**本文へ埋め込む**。
  2. シナリオ122（映画館・2島 cine-sched/cine-ops）の関係チェックで、**本文が島A/Bを参照**することを assert する。
- 実施しないこと:
  - summarize-island-relation の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（48/66/106/110等）の関係アサーションの変更（`"text"` キー assert・非後退）。

## 受入条件

- [x] cine-sched/cine-ops の関係要約の本文が「島cine-schedと島cine-ops」を参照する（実走行で確認）。
- [x] 既存シナリオ（106/110・`"text"` キー assert）は非後退。
- [x] シナリオ122の関係チェックが `"text"` かつ島A/B参照を assert し、業務フローE2E が **734/734 pass**（並行編集によるMGシナリオの干渉がない場合）。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 734/734（シナリオ122の CN ⑤関係要約が島A/Bを本文で参照）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの島ID埋め込みは「関係要約が島ペアに接地する」ことを検証可能にする決定性表現であり、実LLMの関係要約品質とは独立（本issueは検証ハーネスの能力向上）。DOGFOOD-15（接地カード）の延長。
- ドッグフーディング観察起点（2026-08-16・iteration 192）: 映画館（cine-sched/cine-ops）で summarize-island-relation を実行し、本文が島ペアを一切参照しないことを再現。関係要約の島ペア接地がE2Eで検証不能であることを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、接地IDの存在だけでなく生成本文そのものが対象の島・テーマへ接地することをE2Eで決定的に検証できるようにした verification harness 改善として `Done` となっていた。
- `DOGFOOD-28` と `DOGFOOD-29` は、既存の grounding 保全を前提に、関係要約本文と島表札本文の意味接地をそれぞれ固定した同型の小さなまとまりとして同時に `01_Plans/issues/done/` へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は31から29へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
