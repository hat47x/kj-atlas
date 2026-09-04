# Issue: DOC-VOCAB-01 廃止した語彙 `Core Graph` が下位層で契約語彙として使われ続けており、ドリフト検知器もその語に依存している

- Type: Documentation / Process
- Status: Done
- Source Issue: `DOC-NORM-01`
- Priority: P2
- Owner: Maintainer
- Scope: `02_Architecture/llm_input_ir_spec.md`, `02_Architecture/llm_quality_strategy.md`, `02_Architecture/review_attribution.md`, `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`, `01_Plans/docs_contract_checks.py`
- Related ADR/Spec: `00_Prompt/domain.md` §5, `02_Architecture/architecture.html`
- Norms: `DOM-AI-04`
- Expected verification level: `unit`

## 課題

- 現在の問題: `domain.md` は用語表で `Consensus Graph` を正とし、**「`Core Graph` は旧称です。履歴説明以外では契約語彙として再導入しません」** と定めている。`architecture.html` も「契約語彙へ再導入してはならない（履歴注記用途のみ許可）」と重ねて述べている。

  しかし実際には、**規範を実装する側が契約文として使い続けている。**

  | 箇所 | 使い方 | 履歴注記か |
  |---|---|---|
  | `llm_input_ir_spec.md` | 見出し「Core Graph write boundary（`CE0-CG-WRITE-IF`）」 | **いいえ。契約の名前そのもの** |
  | `llm_input_ir_spec.md` | 「safeMode 既定ON・unreviewed 保護・Core Graph direct write 禁止の3点は同時成立が必須」 | **いいえ。契約条文** |
  | `llm_quality_strategy.md` | 「`Core Graph direct write prohibition` の後退は契約違反とみなす」 | **いいえ。契約条文** |
  | `review_attribution.md` | 契約表の `CE0-CG-WRITE-IF` 行「Core Graph direct write 禁止」 | **いいえ。契約表の本文** |
  | `ADR-0028` D2 Fixed Contracts | 「Core Graph 直接更新禁止（patch提案経由のみ）」 | **いいえ。固定契約の列挙** |
  | `ADR-0028` D11「Core Graph再考」 | 改名を決めた記録 | はい（許容される用法） |

  **起票時の上表は数え落としていた。** 是正作業で `ADR-0028` をもう一度読み、
  「Perspective切替がCore Graphを変更しない」（CE1検証）、「AI-aware Perspective を表示レイヤに限定
  （Core Graph非破壊）」（CE3実装）、「Core Graph / Consensus Graph / `human_reviewed` を直接更新する
  権限を持たない」（HIL-RS）の3件を追加で見つけた。**最後の1件は旧称と新称を別物として並べており、
  読み手が2つのグラフがあると誤解する形になっていた。** 契約文としての違反は合計9箇所である。

  つまり **`domain.md` が禁じた形式が、`domain.md` を実装する層で9箇所生きている。** `DOC-NORM-01` で扱った「主張した保護範囲 > 実際の保護範囲」と同じ構造である。規範は書かれ、下位層はそれを守っていない。

- **さらに悪いこと**: `ADR-0028` D6 のドリフト検知コマンドは、検知対象の文字列として `Core Graph` を挙げている（`safeMode|unreviewed|Core Graph|projection` を検索する）。**したがって正しく改名すると、この検知器は何も見つけなくなり、黙って通る。** 語彙を是正する作業が検知器を無効化する経路になっている。改名と検知器の更新は同時に行わなければならない。

- 利用者または開発への影響: 契約名が2つある状態では、どちらが有効か読んで判断できない。新規参加者とAIエージェントは両方を見て、どちらかを再生産する。実際に本件は `ai_cognitive_externalization_requirements.md` の改名作業（`1811bddbc`）が憲法層だけを書き換えて下位層へ伝搬しなかった結果として生じている。

## 対応方針

- 実施すること:
  - **契約文の `Core Graph` を `Consensus Graph` へ改める。** 対象は上表で「履歴注記か = いいえ」の5箇所。
  - **契約ID `CE0-CG-WRITE-IF` は変更しない。** IDは識別子であり、指し先が変わらない以上、改名する理由がない（`DOC-NORM-01` で確立した「識別子は追記のみ・再利用しない」と同じ理由）。
  - **`ADR-0028` D6 のドリフト検知コマンドを同時に更新する。** 新語で検知できるようにし、旧語も残して「旧語の再出現」自体を検知対象にする。
  - **`docs_contract_checks.py` に廃止語彙の検査を加える。** `domain.md` 用語表の「旧称」欄を機械可読な形にし、旧称が契約文脈で現れたら落とす。`domain.md` が自分で宣言した禁止事項を、`domain.md` を正本として検証できる状態にする。

- 実施しないこと:
  - **一括置換はしない。** `ADR-0028` D11 は改名を決めた記録であり、そこでは旧称が正しい。文脈を見ずに置き換えると決定の記録が読めなくなる。
  - **検査を先に入れて赤にすることはしない。** 既存違反を分類せずにゲートを置くと、`DX-DESIGN-CHECK-02` で問題にした「件数ベースラインを上げて黙らせる」経路に入る。是正と検査は同一変更で入れる。

## 対応結果（2026-08-16）

**契約文9箇所を `Consensus Graph` へ是正した。** `02_Architecture` 4件（`llm_input_ir_spec.md` の
見出しと条文、`llm_quality_strategy.md`、`review_attribution.md` の契約表）、`ADR-0028` 5件
（D2 Fixed Contracts、CE1検証、CE0-B、CE3-B、HIL-RS Context）。

**`DC-VOCAB-001` を追加した。** 廃止語彙の一覧は**ハードコードせず `domain.md` §5 から読む。**
規範を持つ文書が規範を供給し、検査はそれに従う。一覧を検査側に書くと、規範と検査が別々に動く。

**意図は推測せず、明示させる設計にした。** 当初はキーワード（`旧称`・`履歴`・`再定義`）で
履歴文脈を判別しようとしたが、`ADR-0028` D11（改名を決定した記録）と `architecture.html` の
禁止条文は**どちらも旧称を正しく名指ししており、語句からは契約文と区別できなかった。**
そこでブロックを明示マーカーで囲む形にした。

```
<!-- retired-vocabulary: historical -->
（旧称を用いてよい記録・禁止条文）
<!-- /retired-vocabulary -->
```

`DX-CANON-INTENT-01` が記録した「差分は見えるが意図が見えない」への対処であり、
**意図を検出器に推測させず、文書に書かせる。** 括弧内で旧称であると明示する形
（`Consensus Graph（旧称: Core Graph）`）は行内例外として許す。

## 検出力の確認

`01_Plans/tests/test_norm_identifier_checks.py` の `RetiredVocabularyCheckTests` 5件。

- ベースラインが緑
- 契約文に旧称を1件戻すと**落ちる**
- 明示マーカーで囲んだ履歴記録は落ちない
- **マーカーが閉じた後まで免除が漏れない**（免除がファイル残り全体を覆うと、検査は静かに無効化される）
- 行内で旧称と明示した参照は落ちない

## この検査が守らない範囲（重要）

**`DC-VOCAB-001` の適用範囲は `02_Architecture` に限る。** `domain.md` §5 は
「履歴説明以外では契約語彙として再導入しません」と層を限定せずに述べているので、
**検査の範囲は規範の主張より狭い。**

理由は実測である。旧称はリポジトリ全体に約110箇所あり、その大半は
`issue-CE0-core-graph-repositioning.md`（単独で80箇所超）と `issue-CE0-contract-freeze.md` の
**改名作業そのものの実行記録**である。そこでは旧称が正しい。issue層まで検査対象にすると、
80箇所以上にマーカーを貼る作業が発生し、しかもその作業に価値はない。

**したがって「主張した保護範囲 > 実際の保護範囲」がここでも残っている。** 本issueが
問題にしたのと同じ構造であり、隠さずに記録する。契約語彙が置かれる層は `02_Architecture` であり、
再導入が実害を生むのもそこなので、狭めた範囲は最も効く範囲ではある。

- **未検査**: `01_Plans/adr/` の Decision 節（今回 `ADR-0028` は手で是正したが、次に誰かが
  旧称で契約を書いても検出されない）
- **未検査**: `03_Implement/` のコード・コメント・スキーマ

## 受入条件

- [x] 契約文の旧称が `Consensus Graph` になっている（9箇所。起票時の見立ては5箇所だった）
- [x] `ADR-0028` D11 の改名記録は旧称のまま残っている（明示マーカーで囲んだ）
- [x] `CE0-CG-WRITE-IF` の契約IDが変わっていない
- [x] `ADR-0028` D6 のドリフト検知コマンドが新語で検知でき、かつ旧語の再出現も検知する
- [x] `docs_contract_checks.py` が廃止語彙の契約文脈での使用を検出する（`DC-VOCAB-001`）
- [x] **検出力の確認**: 契約文へ旧称を1件戻す probe で検査が落ちることを確かめた
- [x] 検査が守らない範囲を本書に明記した


## 配置の整理（2026-09-05）

- 本Issueは内容上すべての受入条件を満たして `Done` となっていた一方、R18以前からの経緯により、完了済みのまま作業中Issueと同じルートへ残るlegacy集合に含まれていた。
- 既存のライフサイクル契約は、このlegacy集合を恒久的に残すものではない。移行のたびに `LEGACY_DONE_AT_ROOT_BASELINE` を同じ変更で下げ、完了済みIssueを `01_Plans/issues/done/` へ移す単調減少のラチェットである。
- 本変更では文書系の完了済みIssue 3件をまとめて正規配置へ移し、baselineを57から54へ縮小した。R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
