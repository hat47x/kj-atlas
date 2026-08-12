# Issue: DOGFOOD-07 .gitignore の `result-*`（Nix出力用）が全階層のファイルを無視する

- Type: Bug / Process
- Status: Draft
- Source Issue: DOGFOOD-01（ドッグフーディングの結果分析・文書化で発見）
- Priority: P2
- Owner: Maintainer
- Scope: `.gitignore`
- Related ADR/Spec: なし（運用規約の修正）
- Expected verification level: `docs-check`

## 課題

2026-08-12 に作成した横断分析文書 `01_Plans/dogfood/result-analysis-synthesis-2026-08-12.md` が
`git add` で「gitignore により無視」された。

原因は `.gitignore` L218-219 の Nix ビルド出力用ルール:

```gitignore
# Nix / direnv
.direnv/
result
result-*
```

`result` と `result-*` は**先頭スラッシュでアンカーされていない**ため、Nix ビルドのルート配置物だけでなく、
**リポジトリ内の任意の階層で `result-` で始まる名前のファイルすべて**を無視する。
Nix の一般的な gitignore はルート限定の `/result` `/result-*` を用いる。

### 三要素分析

- **機能設計**: ルールの意図（ルートの Nix シンボリックリンク `result` を除外）は明確だが、パスのアンカーが欠けて意図の範囲を超えて適用される。
- **データ設計**: `result-*` は将来の文書・成果物名として自然な接頭辞（例: `result-analysis-*`, `result-*.md`）であり、リポジトリ追跡から静かに外れる。
- **業務設計**: ドッグフーディングの成果物（分析文書・計測結果）が「git 管理外」と見えてしまい、追跡・レビュー・コミットの対象から脱落する。ファイル名を変える回避は可能だが、ルール自体の誤りが残る。

## 期待される改善

- `.gitignore` の Nix ルールをルート限定にアンカーする:
  ```gitignore
  /result
  /result-*
  ```
- これにより、ルートの Nix 出力のみ無視し、文書名の `result-*` を誤って無視しなくなる。

## 受入条件

- [ ] `result-` で始まる非Nixファイル（例: `01_Plans/xxx/result-analysis.md`）が `git add` できる。
- [ ] ルートの Nix 出力（`./result`, `./result-*`）は引き続き無視される。
- [ ] `git status` に意図しない無視ファイルが現れない。

## 検証計画

- 実行コマンド:
  - `git check-ignore -v 01_Plans/.../result-analysis.md` → 修正後は ignore されないこと
  - `git check-ignore ./result-link`（ルートのNix出力想定）→ 引き続き ignore されること
- 期待結果: アンカー適用後、両方の期待どおりになる。

## 補足

- 本 issue はドッグフーディング成果物が「自分自身の成果物名」で無視された実例であり、
  横断分析（dogfood-analysis-synthesis）の「検証経路・成果物の理想状態前提」とは別の、
  「成果物の追跡可能性」の摩擦である。
