# Issue: DOGFOOD-08 MCP/外部プロジェクションが Hold/Critique 作業状態を落とす

- Type: Design decision / Product
- Status: Done
- Source Issue: DOGFOOD-01（Org-Bパターンの実走行で発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/export/context_bundle_projection.ts`（`ProjectedCard`）, `03_Implement/mcp/src/context_projection_tool.ts`
- Related ADR/Spec: `00_Prompt/domain.md`（保留・違和感）, `issue-DOGFOOD-05`（MCP未レビュー不可視）, `01_Plans/dogfood/adopting-org-patterns.md` §3.5
- Norms: `DOM-SHARE-02`（`ProjectedCard` に `holdState` を含めるか否かが、この共有隣接プロジェクションの決定そのもの）
- Expected verification level: `unit`

## 課題

Org-Bパターン（プロダクトUXリサーチ: 保留・違和感を残したまま週跨ぎで開き直す）の実走行で、
MCPの `get_context_projection` が **Hold/Critique 作業状態を一切出力しない**ことを確認した。

実測（`dogfood_orgb_hold_20260812`、`safeMode:false`・`reviewed-only`）:
- レビュー済みカードは実テキストとともに `cards=3` で返る。
- しかし `holdState`（held/pending/shelved）も `critique` も出力されない（全カード `hold=-`）。
- 元文書では c1=held+critique有, c4=pending と作業状態を持っていたにもかかわらず。

### 三要素分析

- **機能設計**: `ProjectedCard` のスキーマ（`context_bundle_projection.ts`）は `id/claimType/text/reviewed/redacted` のみで、
  `holdState`・`critique`・`critiqueTags` を含まない。テストfixture（`context_bundle_projection.test.ts`）も
  これらのフィールドを投入しておらず、欠落が検証から隠れている。
- **データ設計**: `DocumentV1` のカードは `holdState`（held/pending/shelved）と `critique`（違和感メモ）を持つが、
  外部プロジェクションIR（transport非依存の共有面）に写像されない。内部モデルと外部面で扱うデータが非対称。
- **業務設計**: domain.md は「保留」「違和感」を本ツールの**根幹価値**と定義する。AI伴走者（Org-D相当）が
  カードの作業状態を読めなければ、「何を確定させず残すか」という協働の基本情報が欠ける。
  Org-B の「確定させない状態を週跨ぎで維持する」協働支援に直接関わる。

→ DOGFOOD-05（未レビュー不可視）とは別の欠落。DOGFOOD-05 は「何も見せない」fail-closed、
  本issue は「見せるカードに作業状態が含まれない」スキーマの欠落。

## 扱い方の判断

- fail-closed の緩和ではないため、DOGFOOD-05 の案A/B/C とは独立に判断できる。
- 追加する場合の安全上の論点: `critique` は主観的メモであり、SafeMode ON では「share」境界の一部として
  開示可否を決めるべき。holdState 自体は構造値（テキストなし）なので開示リスクは低い。
  → 論点: ①holdState のみ追加（低リスク）／②critique も含める場合は SafeMode との整合を設計。

## 受入条件

- [x] `ProjectedCard` に `holdState`（および必要なら `critique`）が追加されるか、意図的に除外する判断が記録される。— ①（holdState のみ追加）を採択（69c122dc）。critique は SafeMode の「share」境界の一部とみなし、DOGFOOD-05 の案と合わせて別判断（除外判断を記録）。
- [x] 追加する場合、SafeMode ON での `critique` 開示可否が `context_bundle_projection.test.ts` で固定される。— critique は追加しない①を採択したため該当なし。holdState は構造値（テキスト非含有）として `safeMode:true/false` 双方で出力されることを test で固定。
- [x] MCP 経路で Org-B 相当の AI 協働（保留状態を読んで提案）が可能になる、または非対応であることが明示される。— `ProjectedCard.holdState` 出力により、AI 伴走者が「何を確定させず残すか」を読める。

## 検証計画

- 実行コマンド:
  - `npx vitest run`（frontend, `context_bundle_projection.test.ts`）
  - backend起動後、Hold/Critique付き文書を投入し MCP プロジェクションで holdState の有無を確認
- 期待結果: スキーマ追加後は holdState が出力される（または明示的な除外理由が残る）。

## 補足

- 発見経路: Org-Bパターン（Hold/Critique週跨ぎ）のAPI保存→再読込は成功（5カード・held2/shelved1/critiqued2・テキスト無傷）。
  その直後に MCP 面を確認したところ本欠落を発見。API（永続化）は価値経路を満たすが、MCP（AI協働）は満たさない。

## 修正案（proposal-only・L2: 最終判断は人間）

**対象: `03_Implement/frontend/src/export/context_bundle_projection.ts` の `ProjectedCard` と builder**

現状の型（`ProjectedCard`）と builder の `map` は `id/claimType/text/reviewed/redacted` のみ。

提案の最小変更（holdState のみ追加、critique は別判断）:

```ts
export type ProjectedCard = {
  id: string;
  claimType: string | null;
  text: string;
  reviewed: boolean;
  redacted: boolean;
  /** held/pending/shelved を構造値として出力。SafeMode に関わらず開示（テキスト非含有） */
  holdState: HoldState | null;
};
```

builder の `map` に追加:
```ts
return {
  id: card.id,
  claimType: card.claimType ?? null,
  text: projected.text,
  reviewed,
  redacted: projected.redacted,
  holdState: card.holdState ?? null,
};
```

**理由（三要素）**:
- holdState は列挙型（held/pending/shelved）の**構造値**で、テキスト・主観メモを含まない。SafeMode が保護する対象
  （カード本文）とは性質が異なるため、`safeMode:true` でも開示してよい（安全境界の緩和ではなく、非秘密構造値の追加）。
- critique（主観メモ）は SafeMode の「share」境界の一部とみなすべき。追加する場合は `text` と同じ
  `projectCardText` の分岐（reviewed AND safeMode OFF のときのみ実値）を適用し、`redacted` 相当の扱いを別途設計する。
  本提案では critique は含めない（DOGFOOD-05 の案A/B/C と合わせて判断）。

**テスト追加（`context_bundle_projection.test.ts`）**:
- fixture のカードに `holdState` を付与し、`safeMode:true` / `false` 双方で `holdState` が保持されること。
- 未レビューカードは現状どおり全constraintで出力されないこと（回帰なし）。
- holdState 追加で bundleHash が変わるが、既存の「determinism」テストは同一入力での一致を検証しているため影響しない。
- 反スコアリング語彙（score/rank/confidence/priority）が出力に含まれないことは引き続き満たされる（holdState は該当語彙ではない）。

## 対応記録（2026-08-12）

- **実装（69c122dc）**: `ProjectedCard` に `holdState: "held" | "pending" | "shelved" | null` を追加し、builder の `map` で `card.holdState ?? null` を出力。critique は①採択により含めない（SafeMode との整合設計は DOGFOOD-05 の判断と合わせる）。
- **テスト**: `context_bundle_projection.test.ts` に「holdState が SafeMode でも出力される」「未レビューカードは従来どおり全constraintで出力されない」を追加。
- **検証**: frontend 17 tests pass（`context_bundle_projection.test.ts` 含む）＋ MCP suite pass。反スコアリング語彙なしを維持。
