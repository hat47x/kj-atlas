# Narrative Generation and Review Semantics

> Audience: 外部利用者・レビュー担当者
> Purpose: narrative生成とレビュー運用の意味論を公開する。
> Outcome: 分類結果を **Improve external** に固定し、公開利用時のレビュー責務と安全境界を再現可能にする。
> Public boundary: 公開文書は意味論・レビュー条件・停止条件のみを扱い、内部監査実装や組織固有承認フローは扱わない。
> This document decides: review stateの既定、人間レビュー責務、公開利用条件。
> This document does not decide: 真偽の自動確定、内部監査ログ形式、組織固有の承認フロー。
> Related: `00_Prompt/domain.md`, `02_Architecture/schemas.md`, `01_Plans/documentation_quality.md`

## 1. Go/No-Go gate（公開利用前チェック）

Go 条件（全て必須）:

1. `reviewState=unreviewed`（互換表記: `reviewed=false`）が既定である。
2. `reviewed` 昇格は人間の明示操作のみである。
3. AI生成結果を確定情報として扱わないことが明示されている。
4. SafeMode既定ONと share/export 境界の後退記述がない。

未充足時は No-Go とし、公開前に修正します。

## 2. A型図解とB型文章の関係

- A型図解（カード/配置）が一次表現。
- B型文章（narrative）は図解を言語化した二次表現。
- B型文章は「正解」ではなく、レビュー対象のドラフト。
- 矛盾時は narrative よりカード内容を優先して確認する。

## 3. Review State semantics

### 3.1 既定値

- AI生成直後は `reviewState=unreviewed` を必須とする。
- 未レビュー文章は意思決定・外部共有の根拠にしない。

### 3.2 昇格条件

- `reviewState=human_reviewed` は、人間がカードと照合して妥当と判断した記録。
- AI単独で `human_reviewed` へ昇格してはならない。

### 3.3 proposal-only 原則

- narrative支援出力は提案（proposal）として扱う。
- auto-apply は禁止。
- SafeMode ON時は未レビュー本文の混入を禁止する。

## 4. 推奨ワークフロー

1. readingOrder を定義する。
2. AIで draft narrative を生成する（`unreviewed` 固定）。
3. consistency check で欠落・矛盾候補を抽出する。
4. 人間が修正し、妥当な場合のみ `human_reviewed` に変更する。

## 5. Caveats / Non-goals

- AIは hallucination を起こしうるため、カード照合を必須とする。
- consistency check は助言（advisory）であり、自動確定機構ではない。
- 本書は **automatic truth validation**（真偽の自動保証）を提供しない。

## 6. Verify / 停止条件

```bash
rg -n "Audience|This document decides|This document does not decide|reviewState|unreviewed|reviewed|proposal|auto-apply|SafeMode" 04_Documentation/narratives.md
git diff --check
```

停止条件:

- 上流正本との矛盾を検知。
- AI生成結果を確定情報として扱う記述が混入。
- Verify自己修復が3回を超過。
