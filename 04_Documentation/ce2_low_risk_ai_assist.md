# CE2 Low-Risk AI Assist

対象読者: AI 提案機能を使う利用者、レビュー担当者、QA。

目的: AI 出力を「提案」として扱い、人間が採用・保留・破棄を判断する運用を説明します。

範囲外: AI 出力の自動採用、自動公開、レビュー済み状態への自動昇格。

## 基本方針

CE2 の AI assist は proposal-only です。AI は候補や下書きを出せますが、ドキュメントを自動で確定変更しません。

提案には、少なくとも次の情報が必要です。

- `proposalId`
- `diff`
- `sourceBundleHash`
- `rationale`
- `status`
- `reviewState`

## 状態

| 状態 | 意味 |
| --- | --- |
| `proposed` | AI または補助機能が提案した状態 |
| `accepted` | 人間が採用した状態 |
| `rejected` | 人間が破棄した状態 |
| `held` | 根拠不足、hash 不一致、追加確認待ち |

`human_reviewed` への変更は、人間の明示操作だけで行います。

## 利用フロー

1. AI 提案を生成する。
2. `sourceBundleHash` と対象データが対応していることを確認する。
3. 差分を読む。
4. 必要なら手で修正する。
5. `accept`、`hold`、`reject` を選ぶ。
6. 判断理由を記録する。

## 採用してはいけない例

- hash が一致しない。
- 提案が元データにない断定を追加している。
- 未レビュー情報を確定情報として扱っている。
- 秘密情報や個人情報が出力に混ざっている。
- SafeMode の境界を緩める内容になっている。

## 関連 API

- `POST /ai/proposals/island-summary`
- `POST /ai/proposals/audit`

API の詳細は実装と設計正本を参照してください。この文書では、利用者向けの安全な扱いだけを説明します。

## 関連文書

- [narratives.md](narratives.md)
- [local_llm_ops_guide.md](local_llm_ops_guide.md)
- [security.md](security.md)
- [canonicalization.md](canonicalization.md)
