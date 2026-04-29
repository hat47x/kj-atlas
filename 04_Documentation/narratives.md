# Narrative Generation and Review Semantics

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部利用者・レビュー担当者
> Goal: narrative生成とレビュー運用の意味論を公開する。
> Outcome: 分類結果を **Improve external** に固定し、公開利用時のレビュー責務と安全境界を再現可能にする。
> Public boundary: 公開文書は意味論・レビュー条件・停止条件のみを扱い、内部監査実装や組織固有承認フローは扱わない。
> This document decides: review stateの既定、人間レビュー責務、公開利用条件。
> This document does not decide: 真偽の自動確定、内部監査ログ形式、組織固有の承認フロー。
> Related: `00_Prompt/domain.md`, `02_Architecture/schemas.md`, `01_Plans/documentation_quality.md`

## 1. Go/No-Go gate（公開利用前チェック）

Go 条件（全て必須）:

1. `reviewState=unreviewed`（互換表記: `reviewed=false`）が既定である。
2. `human_reviewed` への昇格は人間の明示操作のみである。
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

## 6. Domain vocabulary compatibility（必須）

- 用語は `00_Prompt/domain.md` の定義を優先し、独自定義で上書きしない。
- `reviewState` は `unreviewed` / `human_reviewed` を正規とする。
- SafeMode, share/export の境界表記を既存仕様と矛盾させない。

## 7. Verify / 停止条件

```bash
rg -n "Audience|This document decides|This document does not decide|reviewState|unreviewed|reviewed|proposal|auto-apply|SafeMode" 04_Documentation/narratives.md
git diff --check
```

停止条件:

- 上流正本との矛盾を検知。
- AI生成結果を確定情報として扱う記述が混入。
- Verify自己修復が3回を超過。


## 8. Stream K serial completion record（2026-04-26）

### Phase 1 Read
- 本書と `00_Prompt/domain.md` を再読し、語彙矛盾がないことを確認。

### Phase 2 ADR/CDC
- Context: narrative公開は有効だが語彙衝突は運用リスク。
- Decision: Improve externalを維持し、domain語彙互換を必須化。
- Consequences: 公開利用時の誤解を抑制。

### Phase 3 Plan
- Go/No-Goへ「domain語彙矛盾なし」を組み込む。

### Phase 4 Execute
- Domain vocabulary compatibility節を追加。

### Phase 5 Verify
- `rg -n "Domain vocabulary compatibility|reviewState|human_reviewed|SafeMode|Go/No-Go" 04_Documentation/narratives.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**（自己修復0/3）。


## Stream G mini-Phase serial run（2026-04-27）

### Phase 1 Read
- 対応Issue（`DOC-OPS-05-10`）と本書の分類ヘッダを再読し、公開境界を確認。

### Phase 2 Plan
- 変更責務を docs-only の記録同期に限定し、本文の分類（Move internal / Improve external）を維持。
- 共通ACテンプレ（Scope固定 / 境界明示 / GoNoGo / docs-check / 3回上限）を適用。

### Phase 3 Execute
- 本節を追記し、Read→Plan→Execute→Verify→Proceed の直列実行証跡を固定。
- 指定外ファイル・実装コード・共有統合ファイルは未編集。

### Phase 4 Verify
- `rg -n "DOC-OPS|Classification|Audience|Goal|Public boundary|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/narratives.md`
- `git diff --check`
- self-repair count: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（分類方針と公開境界を維持）。

## Stream E共通: Draft課題のOpen化条件（DOC-OPS-05）

- 本文書で扱う Draft 課題は、次の **5条件をすべて満たした場合のみ Open 化** する。
  1. **Read**: 対象本文書と上位根拠（00〜02、必要なADR）を再読し、参照差分を列挙済み。
  2. **Plan**: Scope / Non-Goals / Acceptance / Validation / Stop Conditions を明文化済み。
  3. **Execute**: docs-only 境界（実装コード非変更）を維持し、allowlist 外の差分が 0。
  4. **Verify**: 再現可能な docs-check コマンドと結果（成功/未実施理由）を記録済み。
  5. **Proceed**: Go/No-Go/Conditional を明示し、未確定事項を「決定」扱いせず次アクションに分離済み。
- 未確定事項は `TBD` / `Assumption` / `Decision Needed` で明示し、**承認前に仕様確定文へ昇格しない**。
- 自己修復（同一原因への再試行）は最大3回まで。4回目相当は Stop とし、Open 化を保留する。

