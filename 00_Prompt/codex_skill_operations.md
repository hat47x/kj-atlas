# Codex Skill Operations

- Status: Informative

対象読者: kj-atlas に Codex や AI エージェントで貢献する開発者、レビュー担当者。

目的: 公開文書として、AI エージェント作業時に守る最小ルールと正本への導線を示します。

範囲外: 内部 skill 実装、非公開の運用プロンプト、組織固有の自動化設定。

公開区分: 開発者/AIエージェント運用向け。一般利用者向け Gist には含めず、Codex skill の導入・検証・ロールバックを行う保守文脈で参照します。

読後にできること: AI エージェントで文書やコードを変更するとき、最初に読む文書、触ってよい範囲、公開文書に残してよい情報を判断できます。

この文書でいう AI エージェント作業とは、Codex などの支援ツールを使って、調査、文書編集、実装、検証を進める作業です。人間の判断を置き換えるものではなく、正本を読み、差分を作り、検証結果を残すための補助として扱います。

## まず読むもの

AI エージェント作業では、最初にリポジトリルートの [AGENTS.md](https://github.com/hat47x/kj-atlas/blob/main/AGENTS.md) を読みます。AGENTS.md が、読み順、対象階層、設計正本、docs-only 作業の境界を示します。

## 公開文書で決めること

この文書では次だけを決めます。

- AI エージェントが最初に読む文書。
- docs-only 作業でコードを変えないこと。
- SafeMode、share/export、外部サービスとの共有の安全境界を後退させないこと。
- 内部手順や秘密情報を公開文書に混ぜないこと。

## 公開文書で決めないこと

- skill の内部実装。
- Codex 実行環境の秘密設定。
- 組織固有の承認経路。
- 設計正本の変更。

これらが必要になった場合は、公開文書だけで結論を出さず、`01_Plans` の issue memo または ADR、`02_Architecture` の設計文書へ分けて扱います。

## 作業ルール

1. 変更対象の階層を確認する。
2. `00_Prompt`、`01_Plans`、`02_Architecture` に正本がある場合は先に読む。
3. docs-only 作業では `03_Implement` を変更しない。
4. 実装変更が必要になった場合は、文書作業とは分けて扱う。
5. 公開文書には、読者が使う手順、判断基準、確認方法だけを書く。

迷った場合は、利用者がその文書だけを読んで安全に再現できるかを基準にします。内部事情を知らないと判断できない説明は、公開文書ではなく内部文書へ移します。

## 文書更新時の確認

```bash
git diff --check
rg -n "internal execution log|private approval|secret|token" 04_Documentation
```

上の検索は、内部ログや秘密情報が公開文書に混ざっていないかを確認するための簡易チェックです。

## 関連文書

- [AGENTS.md](https://github.com/hat47x/kj-atlas/blob/main/AGENTS.md)
- [documentation_quality.md](https://github.com/hat47x/kj-atlas/blob/main/01_Plans/documentation_quality.md)
- [security.md](https://github.com/hat47x/kj-atlas/blob/main/04_Documentation/security.md)

## 運用手順（DOC-OPS-05）
1. 対象読者（Audience）と目的（Goal）を先に確認する。
2. 公開境界（Public boundary）を確認し、内部手順は公開文書へ直接書かない。
3. 実行後は関連文書の導線（Related links）と矛盾がないか確認する。

## 判断基準（DOC-OPS-05 品質ゲート）
- 可読性: 用語が定義済み語彙と一致し、読者の次アクションが明確であること。
- 検証可能性: 手順・確認コマンド・期待結果が対応していること。
- 保守性: 上流（00〜02）と矛盾せず、関連文書へ責務を分離していること。

## 失敗時対応
- 参照不整合、用語不一致、公開境界の曖昧化を検出した場合は更新を停止する。
- 自己修復は最大3回までとし、4回目相当は Hold として論点化する。
- Architecture/ADR 本体の変更が必要な場合は、この文書では確定せず提案に留める。
