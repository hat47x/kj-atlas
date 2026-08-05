# Issue Draft: DX-DOC-07 docs_check がHTML文書を走査していない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
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

被参照の多い設計文書（`schemas.md` は109ファイル、`architecture.md` は98ファイル、`value_traceability.md` は42ファイルから参照）を HTML へ置換すると、リンク検証の対象外になったうえで参照側も壊れる。そのため `AGENTS.md` §3 で当面**Markdown を正本として残し、HTML は追加のビューに限る**と定めた。本Issueが解消するまでこの制約を維持する。

## 論点（人的判断が必要な理由）

検査をHTMLへ広げる際、Markdown 用の抽出規則がそのまま使えない。

- `check_relative_links` は `MARKDOWN_LINK_RE`（`[text](target)`）に依存する。HTML では `href` / `src` 属性を抽出する必要がある。
- `check_repository_path_commands` はバックティック内トークンを走査する。HTML では `<code>` 要素の内容が対応する。
- HTML の解析に標準ライブラリ（`html.parser`）で足りるか、依存を追加するかは方針判断。現在 `docs_check.py` は標準ライブラリと `git` のみで動いている。

どこまで対称にするか（全検査をHTMLへ広げるか、リンクとリポジトリパスの2件に絞るか）も判断対象である。

## Acceptance

- [ ] HTML 文書がリンク切れ・存在しないリポジトリパスの検査対象に入る。
- [ ] `02_Architecture/design/*.dc.html` を含む既存HTMLが検査を通る、または違反が起票される。
- [ ] `AGENTS.md` §3 の「Markdown を正本として残す」制約を、解除できるかどうか判断して記録する。

## Validation

- `python 01_Plans/docs_check.py --root .`
- HTML 側に意図的な壊れたリンクを入れた fixture で、検査が検出することを確認する。
