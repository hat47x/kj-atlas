# Issue: DX-DOC-09 バッククォート表記のパス引用がリンク切れ検査の対象外で、244件の不整合が蓄積している

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Unassigned
- Scope: `01_Plans/docs_contract_checks.py`, `01_Plans/adr/*.md`, `01_Plans/issues/*.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0078-integrity-consistency-budget-and-inspection-plan.md`（IC-11）, `AGENTS.md` §3「文書の形式」
- Expected verification level: `docs-check`

## 課題

`01_Plans/adr/`・`01_Plans/issues/` の Traceability/Scope/Related 欄は、慣例として他ファイルを

```
`01_Plans/issues/done/issue-X.md`
```

のようなバッククォート囲みのコードスパンで引用する（Markdown の `[text](path)` リンク構文ではない）。

既存のリンク切れ検査 `DC-LNK-001`（`docs_contract_checks.py:428` `check_relative_links`）は、`MARKDOWN_LINK_RE`（`!?\[[^\]\r\n]*\]\((?P<target>...)\)`）だけを走査対象としており、**バッククォートのコードスパン引用は検査対象外**である。実際、`docs_check.py` は現在 exit 0（合格）だが、これはバッククォート引用の不整合を検査していないためであり、不整合が存在しないためではない。

### 実測（`ADR-0078` IC-11 の初回監査パスとして実施）

`01_Plans/`・`02_Architecture/` 配下の全 `.md`/`.html` からバッククォート引用パス（`01_Plans|02_Architecture|03_Implement|00_Prompt|04_Documentation/...`形式）を抽出し、実在確認した。

- 検出した引用パス総数: 720件（重複除く）
- 参照先が別ディレクトリに実在する（basenameは一致・パスのみ不一致）: **159件**
- 参照先がリポジトリのどこにも実在しない: **85件**

3種の再現可能なパターンに分類できる（いずれも個別確認済み）。

**(a) issue の `done/` 移動に追随していない引用（159件の大半）**

```
01_Plans/issues/issue-CE0-contract-freeze.md
  -> 実際は 01_Plans/issues/done/issue-CE0-contract-freeze.md
```

issueがDone化して`done/`へ移動した後も、他ファイルの引用が旧パスのまま残る。個々の実害は小さいが、件数が多い。

**(b) ADRのファイル名スラグ不一致（サンプル8件中8件が不一致）**

```
`01_Plans/adr/ADR-0043-ui-complexity-budget.md`             -> 実際は ADR-0043-complexity-budget-for-cognitive-load.md
`01_Plans/adr/ADR-0046-performance-budget-and-responsive-interaction.md` -> 実際は ADR-0046-responsiveness-performance-budget.md
`01_Plans/adr/ADR-0048-ui-visual-language-and-canvas-navigation.md`      -> 実際は ADR-0048-visual-language-command-reach-and-kj-vocabulary.md
`01_Plans/adr/ADR-0050-llm-provider-and-user-freedom-boundary.md`       -> 実際は ADR-0050-llm-provider-observability-and-contract-fidelity.md
`01_Plans/adr/ADR-0053-support-diagnostics-bundle.md`                    -> 実際は ADR-0053-support-diagnostics-bundle-boundary.md
`01_Plans/adr/ADR-0054-external-connection-service-scope.md`           -> 実際は ADR-0054-external-connection-layer-staged-introduction.md
`01_Plans/adr/ADR-0068-ai-safe-mode-input-boundary.md`                  -> 実際は ADR-0068-safemode-enforcement-at-api-boundary.md
`01_Plans/adr/ADR-0070-content-addressed-revision-dag.md`               -> 実際は ADR-0070-content-addressed-generation-dag-and-git-adapter.md
```

ADR番号は正しいが、スラグ（タイトル部分）が引用時点の作業タイトルのまま固定化され、後にADR本体が改題されている。本セッション中に発見・修正した `ADR-0041-core-value-invariants.md`（誤）→`ADR-0041-core-value-invariants-single-guard.md`（正）と同種のバグであり、単発ではなく**再発するパターン**であることが今回の監査で確認できた。

**(c) `.md`→`.html` 変換（`AGENTS.md` §3）後、引用側が旧`.md`拡張子のまま**

```
`02_Architecture/architecture.md`                     -> 実際は architecture.html（現在.mdは存在しない）
`02_Architecture/enterprise_architecture.md`          -> 実際は enterprise_architecture.html
`02_Architecture/strict_mode_exception_approval_flow.md` -> 実際は strict_mode_exception_approval_flow.html
`02_Architecture/external_agent_collaboration_spec.md`   -> 実際は external_agent_collaboration_spec.html
```

`AGENTS.md` §3 は変換時に「参照元リンクをすべて新パスへ置き換える（`git grep -l 'ファイル名\.md'`で洗い出す）」ことを明記しているが、この`git grep`手順はおそらく `[text](path)` 形式のリンクのみを対象に行われており、バッククォート引用は洗い出されなかったとみられる。**`issue-DX-DOC-08`自身のScope欄が、まさにこの4ファイルを`.md`のまま引用しており、実例として現存する。**

**(d) その他（個別確認が必要、優先度は低い）**

- `01_Plans/phase0_bootstrap.md` 等（`ADR-0000-adr-governance.md`他、初期フェーズADRからの引用）: `ADR-0000`はAccepted・現行だが、引用先の初期計画文書は現存しない。プロジェクト黎明期に退役した可能性があり、意図的な歴史的引用の可能性がある。削除ではなく状態確認が先。
- `03_Implement/frontend/src/ui/*.ts`（`App.ts`・`SidePanel.ts`・`CardView.ts`等、件数最多。`App.ts`だけで50件超）: 実ファイルは`.tsx`（`App.tsx`・`SidePanel.tsx`確認済み）。Reactコンポーネントを`.ts`として引用する誤記が定着している。

### なぜ「本物の穴」と判断したか

`DC-LNK-001`は「リンク切れが無い」ことをCIで固定しているが、対象がMarkdownリンク構文のみのため、**この検査は「バッククォート引用のリンク切れが無い」ことを一切保証していない**。`01_Plans/`のTraceability欄は実質的にすべてバッククォート引用であり、この慣習の下では現行の`DC-LNK-001`は当該慣習の主要な使用箇所をほぼカバーしていない。`ADR-0078`のIC-11（ADR/issue間相互参照の正確性）は「薄い」と記録したが、本監査で「薄い」ではなく**「自動検査が存在しない」**であり、かつ機械的に検査可能（構造的ドリフトであり、IC-8/IC-9/IC-10のような意味的ドリフトではない）ことが判明した。`ADR-0078`のIC-11記述はこの点で補正が必要。

## 対応方針

2段階に分ける。

### Phase 1: 検査の拡張（`docs_contract_checks.py`）

- `DC-LNK-001`（またはコードスパン専用の新ルールID、例 `DC-LNK-002`）を追加し、`` `<パス>` `` 形式のコードスパンのうち、`01_Plans|02_Architecture|03_Implement|00_Prompt|04_Documentation/` で始まり既知の拡張子（`.md`/`.html`/`.py`/`.ts`/`.tsx`）で終わるものを対象に、実在確認する。
- 誤検出回避のため、以下を除外する: フェンスコードブロック内（`_without_code`と同等の除外）、`03_Implement`配下の生成物やビルド成果物、環境変数名や設定キー（拡張子で判定するため誤爆は少ない見込みだが、実装時に既存の`_without_code`ヘルパーを再利用して確認する）。
- **既存の244件を一括で解禁条件にしない。** `test_ts_python_contract_drift.py`の`KNOWN_TS_ONLY_GAPS`と同様のベースライン許可リスト方式を検討する。ただし、Phase 2（後述）で大半を先に修正できるなら、許可リストは不要になる可能性が高い。

### Phase 2: 既存バックログの解消

- パターン(a)（`done/`移動）: 移動先が一意に特定できるため機械的に一括置換できる。`os.path.relpath`ベースの解決（本セッション中に`check_history_metadata`で実装した手法と同型）を流用できる。
- パターン(b)（ADRスラグ不一致）: ADR番号は正しいため、番号→現在のファイル名を機械的に引いて置換できる。
- パターン(c)（`.md`→`.html`）: 該当4ファイル（他にもある可能性があるため実装時に再走査）を機械的に置換できる。`issue-DX-DOC-08`自身のScope欄も同じPRで修正する。
- パターン(d)（`phase*.md`等、`.ts`/`.tsx`）: 個別確認のうえ、`.ts`→`.tsx`は機械的一括置換が可能。`phase*.md`系は削除済み文書への意図的な歴史的引用である可能性を先に確認する。

**この issue 自身が対象とする `01_Plans/adr/`・`01_Plans/issues/` は、実装者が変更する際に他セッションとの同時編集衝突に注意すること。** 本リポジトリは複数の生成AIセッションが同一ワークツリーを共有する運用がある（`01_Plans/agent_failure_lessons.md`参照）。大量置換の前に`git status`で作業中ファイルの有無を確認する。

## 受入条件

- [x] AC-1: バッククォート引用のパス整合性を検査する仕組みが `docs_check.py` パイプラインに追加され、`docs-check passed`の判定に含まれる。→ `DC-LNK-002`（`check_code_span_citations`）を新設。
- [x] AC-2: パターン(a)〜(c)が修正され、修正後は当該パターンの再発をCIが検知する。→ 446件を修正（内訳は下記「実施結果」）。
- [x] AC-3: パターン(d)の`.ts`/`.tsx`引用が修正される。→ 本着手時点で残存ゼロ。`.ts`引用のうち同名`.tsx`が実在するものは1件も検出されず、issue記載の`App.ts`・`SidePanel.ts`は既に修正済みだった（再走査で確認）。
- [x] AC-4: `phase*.md`系の引用について、意図的な歴史的引用か単純な失効かを判定した記録が残る（削除は伴わなくてよい）。→ **歴史的引用と判定**。下記「`phase*.md`系の判定」を参照。削除していない。
- [x] AC-5: `issue-DX-DOC-08`のScope欄が現行の`.html`パスへ更新される。→ 本着手時点で既に更新済み（Scope欄は `02_Architecture/api.md` と `03_Implement/backend/src/kj_atlas_api/routes/` のみを引用し、`.md`のまま残った4文書は含まれていなかった）。再確認のみで変更なし。
- [x] AC-6: 新検査導入後、`docs_check.py`がバッククォート引用のリンク切れをゼロ件で通過する。→ `docs-check passed`（`RETIRED_CITATION_TARGETS`の25件を除く）。
- [x] AC-7: `ADR-0078`のIC-11行の記述を実態へ整合させる。→ 「未（自動検査なし）」は本issueの完了により事実に反するため、`DC-LNK-002`で充足（自動）へ更新した。

## 実施結果（2026-08-29）

新検査`DC-LNK-002`の初回検出は**508件**（issue起票時の実測244件から増加。監査後も引用が追加され続けたため）。うち446件を機械的に修正し、62件を歴史的引用と判定して許可リスト化した。

| パターン | 修正件数 | 解決方法 |
|---|---|---|
| (a) issueの`done/`移動等への追随漏れ | 431 | basenameで一意解決。うち`archive/`移動1件、`research/`移動2件は個別確認 |
| (b) ADR番号は正・スラグが失効 | 14 | ADR番号→現行ファイル名を引当（`DC-ADR-001`が番号の一意性を保証済み） |
| (c) `.md`→`.html`変換への追随漏れ | 1 | issue記載の4文書のうち3件は着手時点で修正済み。残る`external_agent_collaboration_spec.md`を修正 |
| (d) `.ts`→`.tsx` | 0 | 残存なし（AC-3） |
| 歴史的引用（許可リスト） | 62 | `RETIRED_CITATION_TARGETS`（25パス） |

**実装上の注意（再発防止）**: 修正はフェンスコードブロックの外だけに適用した。本issue自身のフェンス内には不整合パスが実例として引用されており、一括置換で書き換えるとissueの記述が壊れる。またHTML文書では引用が`<code>`要素でありバッククォートではないため、Markdown向けの一括置換とは別経路が必要だった（`02_Architecture/`のHTML 6件）。

### `phase*.md`系の判定（AC-4）

**歴史的引用と判定した。失効ではない。**

`01_Plans/phase0_bootstrap.md`・`phase1_canvas_mvp.md`・`phase2_qualitative_integration.md`・`phase3_review_governance.md`・`phaseX_*.md`・`roadmap.md`・`value_to_requirements.md` の9文書は、コミット`906e8bbf`（"docs: make 01_Plans README a navigable ADR index"）でフェーズ計画形式をADR形式へ移行した際に削除されている。

これらを引用しているのは`ADR-0000`〜`ADR-0009`の **`Replaces:` / `Supersedes:` / `Source:` / `Migrated-from:` 欄のみ**であり、いずれも「このADRが何を置き換えたか」を記録する欄である。**退役した文書の名前を書くことがその欄の目的**であるから、引用先が存在しないことは不整合ではなく正しい状態である。現行文書へ付け替えると、ADRが何を置き換えたのかという記録そのものが失われる。

同型の判定を、退役モジュールを引用する完了issue群（`DX-CLEANUP-01`/`-02`/`-06`、`ENV-ARCH-02`、`UX-NAV-02`）にも適用した。これらは「そのissue自身が削除したファイル」を引用しており、付け替えは記録の改竄にあたる。

判定の記録先は`docs_contract_checks.py`の`RETIRED_CITATION_TARGETS`とし、各エントリに退役理由（コミットまたは退役させたissue）をコメントで併記した。引用箇所ごとのインラインマーカーではなくパス単位の許可リストにしたのは、「その文書はリポジトリから削除された」がリポジトリ側の事実であって引用箇所ごとの事実ではないためである。副作用として、同名の文書を新規作成する意図の引用は検知されない。

## 依存関係

なし（`ADR-0078`はACCEPTED不要で参照するのみ。本issueは`ADR-0078`のIC-11を実行に移す具体issueであり、ADR自体の決定を待たない）。

## 検証

- `python 01_Plans/docs_check.py` → `docs-check passed: active_memos=46, tracked_markdown=683`（2026-08-29）
- `python -m unittest discover -s 01_Plans/tests -p "test_*.py"` → 117 tests, OK
- 件数の推移（`DC-LNK-002`の検出件数）: 508 → 81（パターンa）→ 68（パターンb）→ 62（パターンc）→ 0（歴史的引用62件を`RETIRED_CITATION_TARGETS`へ記録）


## 配置の整理（2026-09-05）

- 本Issueは内容上すべての受入条件を満たして `Done` となっていた一方、R18以前からの経緯によりactive rootに残る58件のlegacy集合へ含まれていた。
- 既存のライフサイクル契約は、この58件を恒久的にrootへ置くことを認めるものではない。移行のたびに `LEGACY_DONE_AT_ROOT_BASELINE` を同じ変更で下げる、単調減少のラチェットとして設計されている。
- その契約に従い、本Issueを `01_Plans/issues/done/` へ移し、baselineを58から57へ縮小した。R18時点のidentity manifestは「新しいDone-at-rootを紛れ込ませない」歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
