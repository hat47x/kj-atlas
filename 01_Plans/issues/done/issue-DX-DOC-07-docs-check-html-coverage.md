# Issue Draft: DX-DOC-07 docs_check がHTML文書を走査していない

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/docs_check.py`, `01_Plans/docs_contract_checks.py`, `02_Architecture/`
- Related ADR/Spec: `AGENTS.md` §3「文書の形式」
- Expected verification level: `docs-check`

## 課題

`docs_check.py` の Markdown 横断検査は、すべて `docs_contract_checks.tracked_markdown_paths()` を経由し、これは `git ls-files -z -- *.md` を実行する。したがって**検査対象は git 管理下の `.md` のみ**であり、HTML 文書は一切走査されない。

現状 `02_Architecture/design/*.dc.html` が4件存在し、さらに設計ビューを HTML + Mermaid で持つ方針を `AGENTS.md` §3 に追加した。この状態では、HTML 側に次の欠陥が入っても fail-closed 検査が検出しない。

- 存在しないリポジトリパスへの参照（Markdown 側では `check_repository_path_commands` が検出する）
- 壊れた相対リンク（Markdown 側では `check_relative_links` が DC-LNK-001 として検出する）
- 実在しない `npm run` スクリプトや `KJ_ATLAS_*` キーの記載（Markdown 側では対応する検査がある）

この非対称は「安全がサーフェスごとの opt-in になっている」という既知の系統的パターン（`02_Architecture/architecture-coherence-synthesis-2026-07-23.md`）と同型である。HTML 側だけ検査が無いため、そちらへ書けば検査を回避できる状態になっている。

## 影響と当面の回避

被参照の多い設計文書（`schemas.md` は109ファイル、`02_Architecture/architecture.html` は98ファイル、`value_traceability.md` は42ファイルから参照）を HTML へ置換すると、リンク検証の対象外になったうえで参照側も壊れる。そのため `AGENTS.md` §3 で当面**Markdown を正本として残し、HTML は追加のビューに限る**と定めた。本Issueが解消するまでこの制約を維持する。

## 論点（人的判断が必要な理由）

検査をHTMLへ広げる際、Markdown 用の抽出規則がそのまま使えない。

- `check_relative_links` は `MARKDOWN_LINK_RE`（`[text](target)`）に依存する。HTML では `href` / `src` 属性を抽出する必要がある。
- `check_repository_path_commands` はバックティック内トークンを走査する。HTML では `<code>` 要素の内容が対応する。
- HTML の解析に標準ライブラリ（`html.parser`）で足りるか、依存を追加するかは方針判断。現在 `docs_check.py` は標準ライブラリと `git` のみで動いている。

どこまで対称にするか（全検査をHTMLへ広げるか、リンクとリポジトリパスの2件に絞るか）も判断対象である。

## 対応（2026-08-05）

### スコープ判断: リンク検査のみ拡張し、repo-path検査は拡張しない

`check_repository_path_commands` は `_is_current_public_doc()` で `CURRENT_PUBLIC_DOC_ROOTS`（`README.md` / `CONTRIBUTING.md` / `04_Documentation` / `03_Implement/frontend/docs/e2e_testing.md`）に限定されている。**`02_Architecture` は含まれない**ため、この検査はそもそも設計文書のMarkdownにも適用されていない。HTMLへ拡張しても現状の効果はゼロであり、`ADR-0039` の「予測だけで実装しない」に反する。同じ理由で npm script / `KJ_ATLAS_*` キー / CLI option / localhost の各検査も拡張しない。

一方 `check_relative_links` は全追跡Markdownに適用されるため、HTMLへの拡張に実効がある。現在の対象は5件（`business-intent-boundary-and-phases.html` と `design/*.dc.html` 4件）。

### アプリHTMLを除外する必要があった

`03_Implement/frontend/index.html` は `src="/src/main.tsx"` を持つ。これは dev server のルート基準で、リポジトリルート基準ではない。全HTMLを対象にすると本検査が**アプリ本体で誤検知**する。HTMLはMarkdownと違い実行時成果物でもあるため、文書HTMLとアプリHTMLを分ける必要がある。`DOCUMENTATION_HTML_ROOTS`（`00_Prompt` / `01_Plans` / `02_Architecture` / `04_Documentation`）で区別した。

### 実装: 検査を分岐させず、HTMLをMarkdown等価テキストへ正規化する

各検査をHTML用に複製するのではなく、正規化関数を1つ置いて既存検査へ流す方式を採った（`html_to_markdownish`）。`<a href="X">label</a>` → `[label](X)`、`<code>Y</code>` → バックティック、`<script>`/`<style>` 本体は破棄。これにより `MARKDOWN_LINK_RE` と `_without_code()` がそのまま機能し、検査ロジックのフォークが発生しない。

**行番号を保存する制約**を課した。findings は走査テキストから行番号を算出するため、正規化で行が詰まると読者が開くファイルに存在しない位置を報告してしまう。破棄・書き換えのすべてで改行数を維持している。既知の制限として終了タグが複数行に跨らないことを仮定している。

## Acceptance

- [x] HTML 文書がリンク切れの検査対象に入る（repo-path検査は上記スコープ判断により対象外）。
- [x] `02_Architecture/design/*.dc.html` を含む既存HTML5件が検査を通る（誤検知ゼロを実リポジトリで確認）。
- [x] `AGENTS.md` §3 の制約を実態へ更新した。`02_Architecture` に適用される文書契約検査はリンク検査だけであり、それがHTMLを覆ったため**検査被覆の観点での置換制約は解消**した。残る制約は被参照数（パス変更で参照側が壊れる）であり、これは docs_check とは独立した別の理由である。

## Validation

- `python3 -m unittest discover -s 01_Plans/tests -t 01_Plans/tests`: 86 tests OK（既存81＋新規5）。新規は HTML でのリンク切れ検出、実在リンクの受理、`<code>`/`<script>`/外部URL/アンカーの無視、行番号保存、アプリHTML除外。
- 実リポジトリに対する `docs_contract_checks.py --root .`: `ok: checked 471 tracked Markdown files`、走査対象HTML5件で findings ゼロ。
