# Issue: DOC-ROADMAP-01 公開ROADMAPの現在地を実装・価値検証の正本へ合わせる

- Type: Process / Documentation
- Status: Done
- Source Issue: COGNITIVE-DOGFOOD-01
- Priority: P1
- Owner: Maintainer
- Scope: `ROADMAP.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/issues/`, `01_Plans/dogfood/`
- Related ADR/Spec: `ADR-0007`, `PRODUCT-POSITION-01`, `COGNITIVE-EVAL-01`, `VALUE-REALNESS-01`
- Expected verification level: `docs-check`

## 課題

公開 `ROADMAP.md` の「近接フェーズ（Next 1–2 Releases）」には、視座プリセット、島の折りたたみ、多角形島、SafeModeのUI明示、Trace Analytics、構造メトリクス、Diagnostics安定化、ZIP hardening、Worker安定化、CI回帰防止が今後の項目として並んでいた。

一方、実装順序の正本である `ADR-0007-future-backlog.md` では、これらは2026年2〜3月にすべて `Done` と記録されている。さらに現在のP0は、新しい機能群の拡張よりも、認知比較評価と第三者価値実証を通じて一次利用仕事と切替理由を反証可能に検証することへ移っている。

この差分を残すと、公開文書だけを読んだ人には「既に実装済みの機能が次の開発対象」に見える。開発側でも、完了済みの機能一覧が未来の約束として残ることで、実証前の機能拡張を暗黙に正当化する可能性がある。

## dogfoodで観察した摩擦

継続dogfood R11では、次の文書を同じ材料として比較した。

- `ROADMAP.md`
- `01_Plans/adr/ADR-0007-future-backlog.md`
- `01_Plans/issues/issue-PRODUCT-POSITION-01-primary-job-and-switch-reason.md`
- `01_Plans/issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md`
- `01_Plans/issues/issue-VALUE-REALNESS-01-third-party-beachhead-validation.md`
- `01_Plans/dogfood/cognitive-dogfood-index.md`

そこで見えた問題は、個別機能の不足ではなく、**公開されている「次に進む方向」と、内部で実際に未完了な価値検証の間に時間差があること**だった。

これは比較実験や第三者実証の代替証拠ではない。ただし、リポジトリ内の正本同士を照合すれば再現でき、外部入力なしで修正できる文書上の不整合であるため、F2の実行可能な製品・運用課題として本Issueへ起票した。

## 対応方針

1. `ROADMAP.md` の完了済み近接項目を「実装済みの基盤」へ移す。
2. 公開ロードマップの現在の焦点を、次の三点として明示する。
   - 一次利用仕事と切替理由の検証。
   - Case 001〜003による認知比較評価。
   - 第三者による価値実証。
3. 比較実験や第三者実証が未完であることを明記し、準備済みと実証済みを混同しない。
4. 中長期の機能候補は削除せず、「実装を約束した順序」ではなく、実使用の証拠によって昇格・延期・棄却し得る候補として扱う。
5. 実装状態の詳細は `ADR-0007`、実験状態は `cognitive-dogfood-index.md`、一次利用仕事は `PRODUCT-POSITION-01` を正本として参照する。

## 非目標

- `COGNITIVE-EVAL-01` の4-arm実験をこのdogfoodで代替すること。
- `VALUE-REALNESS-01` の第三者観察を内部分析で代替すること。
- 実証前に新しい機能ロードマップを追加すること。
- 中長期候補を一括で廃止すること。
- 完了済み実装の履歴を消すこと。

## 受入条件

- [x] `ROADMAP.md` が、完了済みの近接機能を未来の実装予定として表示しない。
- [x] `ROADMAP.md` に、現在の主な未完了事項が価値・認知の実証であることを明記する。
- [x] `COGNITIVE-EVAL-01` は実行準備済みだが有効な生の実行記録が未取得であることを誤解なく示す。
- [x] `VALUE-REALNESS-01` は手順準備済みだが第三者セッション未実施であることを誤解なく示す。
- [x] 中長期候補を、実証結果によって優先順位を変えられる仮説として読める。
- [x] `ADR-0007` の実装状態と公開ROADMAPの表現に明白な矛盾がない。
- [x] 変更後の全文を、意味・参照先を変えず自然な日本語として読み直す。

## 検証結果

- `ROADMAP.md` と `ADR-0007` の近接項目を再照合した。
- `PRODUCT-POSITION-01`、`COGNITIVE-EVAL-01`、`VALUE-REALNESS-01`、`cognitive-dogfood-index.md` の現在地とROADMAPの記述を照合した。
- push CI run `11511` は成功した。
- pull_request CI run `11513` は成功した。
- `Docs contract (fail-closed repository rules)`、dogfood文書検査、設計整合検査、contract drift検査、changed-file whitespace検査はいずれも成功した。
- アプリコードは変更していないため、frontend/backend/MCPの実装テストはchange-scope判定によりskipされた。

## ロールバック

公開ROADMAPの再構成によって外部向けの理解がかえって不明瞭になった場合は、今回の変更だけを戻す。`ADR-0007`、各P0 Issue、実装コード、凍結済み認知比較実験の入力は変更しない。

## 配置の整理（2026-09-05）

- 本Issueは内容上すべての受入条件を満たして `Done` となっていた一方、R18以前からの経緯により、完了済みのまま作業中Issueと同じルートへ残るlegacy集合に含まれていた。
- 既存のライフサイクル契約は、このlegacy集合を恒久的に残すものではない。移行のたびに `LEGACY_DONE_AT_ROOT_BASELINE` を同じ変更で下げ、完了済みIssueを `01_Plans/issues/done/` へ移す単調減少のラチェットである。
- 本変更では文書系の完了済みIssue 3件をまとめて正規配置へ移し、baselineを57から54へ縮小した。R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
