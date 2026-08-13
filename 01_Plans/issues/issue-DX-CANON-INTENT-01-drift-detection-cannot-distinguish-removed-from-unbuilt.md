# Issue: DX-CANON-INTENT-01 ドリフト検出は差分を見つけるが意図を見分けないため、意図的に廃止した機能が「未実装（計画）」として設計正本へ復活した

- Type: Process / Product Invariant
- Status: Open
- Source Issue: `DX-CONTRACT-DRIFT-01`, `AI-IMPORTANCE-SCORING-01`
- Priority: P1
- Owner: Maintainer
- Scope: `02_Architecture/api.md`, `02_Architecture/runtime_parameter_registry.md`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, `03_Implement/backend/tests/test_ai_anti_scoring_contract.py`, `03_Implement/backend/scripts/check_contract_drift.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`, `00_Prompt/domain.md`, `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`
- Expected verification level: `unit`

## 課題

### 起きたこと

2026-08-11、`AI-IMPORTANCE-SCORING-01` が方向 D-a（廃止）を採択し、カード本文を `high` / `medium` / `low` へ序列化する route・型・prompt/parser・mock応答・デモ工程を削除した。理由は `00_Prompt/domain.md` の**条件節を伴わない不変条件**「AIは内容を採点せず」との抵触である。再発防止に `test_ai_anti_scoring_contract.py` を追加した。

2026-08-12、`DX-CONTRACT-DRIFT-01`（本セッションで起票）が逆方向ドリフト——「api.md に記載があるのに実装が無い」——として同エンドポイントを検出した。これを受けた並行セッションが `api.md` へ次の注記を追記した。

> 未実装（計画）。本 route は `AI-ROUTE-01` の設計として文書化されているが、`models_ai.py` の型も `routes/ai.py` の `@router` デコレータも現時点では存在しない。**実装前にこの契約を正本として使用すること。**

**この注記は誤りである。** 未実装ではなく廃止済みであり、しかも「実装せよ」と指示している。指示に従えば、`test_ai_anti_scoring_contract.py` が存在する理由そのものを再現することになる。

### なぜ起きたか（根本原因）

ドリフト検出器は「文書にあって実装に無い」という**差分**を見つけるが、その差分が

- まだ作っていないから生じたのか（未着手）
- 作ったが原則違反として捨てたから生じたのか（廃止）

を**見分ける情報を持たない**。両者は検出器から見て完全に同じ形をしている。したがって検出結果を修正する側は、git履歴か廃止を決めたissueを自分で辿らない限り、差分の向きを「未着手」と解釈する。既定の解釈が「これから作る」に倒れるのは自然であり、注記を書いた判断は検出器の出力に対して合理的だった。**欠陥は個々の判断ではなく、意図を運ばない検出結果を意図の必要な修正へ流している経路にある。**

これは `DOGFOOD-METRIC-01` / `dogfood-analysis-synthesis-2026-08-12.md` §2 が扱う「測定器と測定対象が同一主体」とは別の失敗である。あちらは測定器を弱めると指標が改善して見える問題。こちらは**測定器が正しく差分を検出しているのに、その差分の意味が復元できない**問題である。検出力の問題ではなく、検出結果の情報量の問題として扱う必要がある。

### 二次的に判明したこと: 保護テストの守備範囲が、守ると称する不変条件より狭い

`test_ai_anti_scoring_contract.py`（修正前）が走査していたのは3ファイル——`models_ai.py` / `routes/ai.py` / `kj_canvas_demo.py`——のみだった。その結果、`AI-IMPORTANCE-SCORING-01` の削除は**完了していなかった**。

| 残存箇所 | 内容 | 保護テストの対象 |
|---|---|---|
| `llm/provider.py` `_FINAL_JUDGEMENT_TASKS` | `assess_card_importance` が MMR-04 ルーティング表に残存。存在しないタスクに対し `routing_stage_for_task()` が `final_judgement` を返し続けていた | 対象外 |
| `02_Architecture/api.md` | request/response スキーマを含む実装可能な契約が丸ごと残存 | 対象外 |
| `02_Architecture/runtime_parameter_registry.md` | `KJ_ATLAS_LLM_HIGH_REASONING_MODEL` の説明が final_judgement 系タスクとして列挙 | 対象外 |

つまり `AI-IMPORTANCE-SCORING-01` の AC-5a「関連する型が削除されていることを確認する」は、**確認範囲がテストの走査範囲に暗黙に限定されていた**。これは `DX-DESIGN-CHECK-01` / `DX-CONTRACT-DRIFT-01` と同型の「保護の主張と保護の実効範囲の乖離」である。3件目。

なお設計正本に契約が残っていたことは、上記の誤った注記の**直接の原因**でもある。スキーマが実装可能な形で残っていれば、それは仕様として読まれる。

## 対応方針

- 実施したこと（本issueと同PR）:
  1. `api.md` の当該節を、実装可能な契約から**廃止記録**へ置換した。旧 route 名は残すが request/response スキーマは削除し、再実装禁止と代替方針（`graph_summary`、`ADR-0069` 後）を明記した。誤注記が入った経緯も記録した。
  2. `runtime_parameter_registry.md:102` の final_judgement タスク列挙から `assess_card_importance` を除去した。
  3. `llm/provider.py` の `_FINAL_JUDGEMENT_TASKS` から `assess_card_importance` を除去した。
  4. `test_ai_anti_scoring_contract.py` の走査対象へ `llm/provider.py` を追加し、さらに**設計正本（`api.md` / `runtime_parameter_registry.md`）に実装可能な契約が復活しないこと**を固定する第2のテストを追加した。正本は廃止を散文で記録してよいが、スキーマを持ってはならない。
  5. **案Aの最小実装。** 契約を api.md から削除しただけでは別の副作用が出ることが実測で判明したため（下記）、機械可読な廃止宣言を導入した。`api.md` §13 に書式（`- 廃止: <METHOD> <path> — <issue>（<日付>、<方向>）`）と規約を定め、`check_design_consistency.py` が `RETIRED_ENDPOINT_RE` でこれを読む。
- 実施しないこと:
  1. 廃止された全機能の網羅的な棚卸し（本issueは1件の是正と再発防止に限定。棚卸しはAC-3で扱う）
  2. `check_contract_drift.py` の逆方向チェック（api.md→routes）の実装。`DX-CONTRACT-DRIFT-01` で範囲外としたまま

### 契約を削除するだけでは足りなかった（実測）

当初は案B（正本から契約を消し散文の廃止記録のみ置く）で対応した。その状態で `check_design_consistency.py` を走らせると、**警告が 4 → 13 件へ増えた**。増分9件の内訳は次のとおりで、いずれも偽陽性である。

- `ADR-0069`、`AI-IMPORTANCE-SCORING-01`（×2）、`DX-CONTRACT-DRIFT-01`（×2）、`DX-DOC-08`、`SEC-AI-SAFEMODE-01`、`DOMAIN-SCORING-SURFACE-01` が、**廃止されたエンドポイントを正当に論じているだけ**で「api.md に無いエンドポイントを参照している」と警告された。**廃止を決めた issue 自身が警告対象になった。**

つまり案Bは、事故の直接原因（実装可能なスキーマの残存）は消すが、**検出器から見た「廃止」と「未文書化」の区別を作らない**ため、廃止のたびに関連文書の数だけ偽陽性を生む。ここでベースラインを 4→13 に緩めるのは、`DOGFOOD-METRIC-01` が指摘する「測定器を弱めて指標を満たす」そのものになる。

機械可読な廃止宣言（案A最小形）を入れた結果、警告は **4件（ベースラインどおり）** へ戻った。検出器の識別力を一切下げずに偽陽性8件が解消されており、**案Aが検出器の情報量を増やす方向の対策であることの実証**になっている。

## 論点（保守者判断が必要な理由）

再発防止の本体は「**廃止した契約をどこに、どう記録するか**」の規約であり、これは文書体系の設計判断である。

- **案A: 廃止レジストリを設ける（本PRで最小実装済み）。** 廃止宣言を機械可読にし、検出器が「廃止済み」と「未着手」を区別する。ドリフト検出結果に意図が乗る。コストは廃止のたびの1行追記。本PRでは api.md 内の宣言行として実装したが、**独立したレジストリファイル**（`02_Architecture/retired_endpoints.json` 等）へ寄せる形もあり、`check_contract_drift.py` の逆方向チェックを将来入れる場合はそちらの方が扱いやすい。**どの形を正とするかは保守者判断とする。**
- **案B: 正本から契約を消し、履歴側へ寄せるだけ。** 追加機構が不要な代わり、上記のとおり**廃止のたびに関連文書の数だけ偽陽性が出る**。実測で9件。単独では成立しない。
- **案C: 不変条件違反による廃止に限り、テストで固定する。** 本PRで追加した「正本にスキーマが復活しないこと」のテストを、廃止のたびに書く規約にする。`ADR-0041` CVI に関わるものだけに絞る。コストは廃止1件につきテスト1本。
- **案D: 現状維持。** 個別に気づいたら直す。

**案A（実装済み・形式は要確定）＋案C（CVI関連に限り規約化）を推奨する。** 案Bは単独では成立しないことが実測で判明した。

## 受入条件

- [x] AC-1: `assess_card_importance` / `AssessCardImportance*` が実装・設計正本の双方から消えている。
- [x] AC-2: 保護テストが `llm/provider.py` と設計正本を走査対象に含み、契約の復活でfailする。
- [x] AC-6: 廃止宣言が機械可読であり、廃止されたエンドポイントを論じる設計文書が偽陽性を生まない（警告数がベースライン4件のまま）。
- [ ] AC-3: 過去に廃止された他の機能について、同種の残存が無いか棚卸しする（`ADR-0041` CVI に関わるものを優先）。
- [ ] AC-4: 上記案から方針を決定し、廃止レジストリの置き場所（api.md内 / 独立ファイル）を確定して `AGENTS.md` または `02_Architecture/contract_reading_guide.md` へ明記する。
- [ ] AC-5: `02_Architecture/canvas-projection-asymmetry-2026-08-09.html:168` が既に存在しない `ai.py:763` を参照している。日付入り分析文書のため履歴として許容するか注記するかを決める。

## 検証

```bash
python -m pytest 03_Implement/backend/tests/test_ai_anti_scoring_contract.py -v
python 03_Implement/backend/scripts/check_design_consistency.py --baseline 02_Architecture/design_consistency_baseline.json
python 03_Implement/backend/scripts/check_contract_drift.py --baseline 02_Architecture/contract_drift_baseline.json
python 01_Plans/docs_check.py
```

## 補足

- 発見経緯: ドッグフーディングの方向性レビューで `DX-CONTRACT-DRIFT-01` が範囲外として記録した逆方向ドリフト1件を追跡したところ、それが「未実装」ではなく「廃止済み」であり、私自身の起票を受けた並行セッションの修正が誤りだったことが判明した。
- **本件はドッグフーディングが機能した結果として見つかった**。検出器が逆方向ドリフトを可視化しなければ、誤注記も残存も表面化しなかった。仕組みの否定ではない。
- 三要素牽制の観点: 業務設計（「AIは内容を採点せず」という製品不変条件）が機能設計（route削除）へは反映されたが、データ設計・契約正本（api.md のスキーマ）へ反映されていなかった。**三要素のうち2つだけが追随した廃止**であり、`ADR-0067` の「三者が揃わない設計判断は着工しない」は着工時の条件だが、**廃止時にも同じ牽制が要る**ことを示している。この一般化は `three-element-constraint-checklist.html` への追加提案となりうる（`post-mvp-business-scope-design-program.html` §3 が「無効化時の振る舞い」を必須項目として提案しているのと同じ性質）。
