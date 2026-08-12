# Issue: DOGFOOD-05 MCP経路が未レビューカードを一切露出せず、Org-D「AI委譲による初期探索」を支援できない

- Type: Design decision / Product
- Status: Draft
- Source Issue: DOGFOOD-01（ドッグフーディングのパターン多様化で発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/mcp/src/context_projection_tool.ts`, `03_Implement/frontend/src/export/context_bundle_projection.ts`, `04_Documentation/`
- Related ADR/Spec: `01_Plans/adr/ADR-0054`（context projection）相当, `03_Implement/frontend/src/export/context_bundle_projection.ts`（SEC-CONTEXT-PROJECTION-01）, `01_Plans/dogfood/adopting-org-patterns.md` §3.5
- Expected verification level: `docs-check`

## 課題

2026-08-12 のパターン多様化実走行（`adopting-org-patterns.md` §3.5）で、MCP経路の価値ギャップを実測した。

50カードの実題材文書（`dogfood_orga_batch_20260812`）に対し、`get_context_projection` を
`safeMode: false` で呼んでも、**未レビューカード50枚は全constraint（reviewed-only/evidence/contradiction/summary）で `cards=0`** になる。
レビュー済み3枚にすると `cards=3` で実テキストが返る（`safeMode: true` では `[REDACTED]`）。

これは SEC-CONTEXT-PROJECTION-01 の意図通りの fail-closed 設計（未レビューカードの id/ref すら MCP 出力に含めない）。

### 三要素分析

- **業務設計**: README は「LLMを伴走者として、人間の違和感・保留・未分化な意味を起点に、カード配置と対話的修正を通じて思考を深めていく」と謳う。Org-D（新規事業企画・個人の思考外部化）は **未レビューの初期探索段階こそ AI 委譲を望む**。
- **データ設計**: SEC-CONTEXT-PROJECTION-01 は未レビューカードの id/ref すら projection に含めない。したがって AI は「カードが存在すること」すら知覚できない。
- **機能設計**: MCP経路は実質 `reviewed-only` 制約しか使えず、初期探索（未レビュー）では AI に何も見えない。**「AI伴走者による初期探索」という業務価値と、fail-closed データ境界が衝突**する。

→ 結論: MCP経路は Org-D の「AI委譲による初期探索」を**現状の設計では支援できない**。

## 扱い方の判断

- 本 issue は「安全境界の緩和」を求めない。fail-closed（未レビュー内容は AI へ開示しない）は維持する。
- 選択肢を整理して維持者の判断を仰ぐ:
  - **案A（適用範囲の明示）**: MCP経路が「未レビュー段階では AI に何も見せない」ことを `04_Documentation` と MCP ツール description に明記し、AI委譲の対象を「レビュー済み以降の整理・俯瞰」に限定する。実装は軽い。
  - **案B（探索専用経路の別設計）**: 未レビュー内容を別の安全境界（例: 同じ安全・反スコアリング原則を守った「探索用プロジェクション」）で扱う専用経路を設計する。安全設計の再考が必要で重い。
  - **案C（現状維持＋ドキュメントのみ）**: 変更せず、知見を分析文書に残す。

## 受入条件

- [ ] 案A〜C のいずれかが維持者によって採択される。
- [ ] MCP経路の適用範囲がドキュメント化され、Org-D 相当の利用者が誤った期待を持たない。
- [ ] fail-closed（未レビュー内容のAI開示禁止）が維持される。

## 検証計画

- 実行コマンド（再現）:
  - backend 起動後、50カード未レビュー文書を投入 → `cd 03_Implement/mcp && KJ_ATLAS_MCP_API_BASE_URL=http://127.0.0.1:8000 npm run verify -- <doc_id> reviewed-only`
  - もしくは `context_bundle_projection.test.ts` で「未レビュー文書の全constraintで cards=0」を固定
- 期待結果: 再現が確認でき、採択された案に沿った文書・設計変更が行われる。

## 補足

- 実測データ: `reviewed-only`/`evidence`/`contradiction`/`summary` 全constraintで `cards=0`, `counts={"reviewed":0,"unreviewed":50,"redacted":50}`。レビュー済み3枚化後は `cards=3`（実テキスト）、`safeMode:true` で `[REDACTED]`。
- このギャップは「バグ」ではなく「業務価値と安全境界の設計上の衝突」であり、方針判断を要する点で設計 issue とした。
