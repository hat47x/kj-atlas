# Codex Skill Operations

対象読者: kj-atlas に Codex や AI エージェントで貢献する開発者、レビュー担当者。

目的: 公開文書として、AI エージェント作業時に守る最小ルールと正本への導線を示します。

範囲外: 内部 skill 実装、非公開の運用プロンプト、組織固有の自動化設定。

## まず読むもの

AI エージェント作業では、最初にリポジトリルートの [AGENTS.md](../AGENTS.md) を読みます。AGENTS.md が、読み順、対象階層、設計正本、docs-only 作業の境界を示します。

## 公開文書で決めること

この文書では次だけを決めます。

- AI エージェントが最初に読む文書。
- docs-only 作業でコードを変えないこと。
- SafeMode、share/export、外部送信の安全境界を後退させないこと。
- 内部手順や秘密情報を公開文書に混ぜないこと。

## 公開文書で決めないこと

- skill の内部実装。
- Codex 実行環境の秘密設定。
- 組織固有の承認経路。
- 設計正本の変更。

## 作業ルール

1. 変更対象の階層を確認する。
2. `00_Prompt`、`01_Plans`、`02_Architecture` に正本がある場合は先に読む。
3. docs-only 作業では `03_Implement` を変更しない。
4. 実装変更が必要になった場合は、文書作業とは分けて扱う。
5. 公開文書には、読者が使う手順、判断基準、確認方法だけを書く。

## 文書更新時の確認

```bash
git diff --check
rg -n "internal execution log|private approval|secret|token" 04_Documentation
```

上の検索は、内部ログや秘密情報が公開文書に混ざっていないかを確認するための簡易チェックです。

## 関連文書

- [AGENTS.md](../AGENTS.md)
- [documentation_quality.md](../01_Plans/documentation_quality.md)
- [security.md](security.md)
