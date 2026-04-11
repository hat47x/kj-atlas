# Narrative Generation and Review Semantics

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部利用者・レビュー担当者
> Goal: narrative生成とレビュー状態の公開セマンティクスを示す。
> Public boundary: 内部判断ログは含めず、運用意味論と非目標を公開する。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。


本ドキュメントは、A型図解（空間配置）から B型文章（narrative）を作成・レビューする際の、
**最小の運用セマンティクス**を定義する。

- 本ドキュメントで扱う narrative は、カード内容を説明可能な形に並べた文章ドラフトである。
- AI は narrative の下書き生成を補助できるが、内容の真偽を保証しない。
- 生成された文章は、**常に `reviewed=false`（未レビュー）を既定値**とする。

---

## 1. A型図解とB型文章の関係

- A型図解は、カードと配置・関係によって思考の素材を保持する一次表現である。
- B型文章は、A型図解を読み順（readingOrder）に沿って言語化した二次表現である。
- B型文章は A型図解から独立した「正解」ではなく、
  **図解に対する説明ドラフト**として扱う。
- 解釈が曖昧な場合は、B型文章より A型図解（カード内容）を優先して確認する。

---

## 2. Review State セマンティクス

### 2.1 Unreviewed by default

- AI 生成直後の narrative は、必ず `reviewed=false` とする。
- `reviewed=false` は「人間による内容確認が未完了」であることを意味する。
- UI 上では、生成文章に対して **「未レビュー（unreviewed）」ラベルを明示表示**する。
- 未レビュー表示がある文章は、意思決定や外部共有の根拠として扱わない。

### 2.2 Reviewed の意味

- `reviewed=true` は、**人間がカード内容と照合して妥当と判断した**状態を示す。
- reviewed は「絶対に正しい」ことの証明ではなく、
  利用者が現時点で確認済みであることの記録である。
- reviewed への変更は、人間の明示操作でのみ行う。

---

## 3. 推奨ワークフロー

narrative 作成は次の順序を推奨する。

1. **Build readingOrder**
   - 先にカードの読取順（readingOrder）を確定する。
   - 順序が未確定のまま文章化しない。

2. **Generate draft narrative**
   - AI で文章ドラフトを生成する。
   - 生成時点の review state は常に `reviewed=false` とする。

3. **Run consistency check**
   - narrative とカード間の整合チェックを実行する。
   - 不一致候補や欠落候補を確認し、修正対象を洗い出す。

4. **Edit narrative and mark reviewed**
   - 人間が narrative を編集し、カードと照合する。
   - 妥当と判断できたら、明示操作で `reviewed=true` に変更する。

---

## 4. Caveats

- AI は hallucination（事実にない補完・誤読）を起こしうる。
  narrative の記述は、必ずカード内容に照らして検証する。
- consistency check は **助言（advisory）** であり、
  正誤を自動確定する仕組みではない。
- したがって、最終判断責任は常に人間にある。

---

## 5. Non-goals

本セマンティクスの非目標は以下。

- **automatic truth validation**（自動的な真偽保証）
  - システムは narrative の真実性を自動確定しない。
  - AI 出力を権威的な結論として提示しない。
