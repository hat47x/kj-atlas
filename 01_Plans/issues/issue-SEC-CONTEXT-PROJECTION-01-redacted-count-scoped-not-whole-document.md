# Issue Draft: SEC-CONTEXT-PROJECTION-01 redactedCountが全文書ではなく絞り込み後の部分集合のみを計上

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/export/context_bundle_projection.ts`, `03_Implement/frontend/src/export/context_bundle_projection.test.ts`, `03_Implement/mcp/src/context_projection_tool.ts`
- Related ADR/Spec: `ADR-0054`（EXT-CONN-01 read-only MCP）, `ADR-0041`（CVI-1 SafeMode）
- Expected verification level: `unit`

## 課題

`context_bundle_projection.ts:155-169` において、`redactedCount` は制約（`constraint`）で絞り込んだ後のカード集合を走査する際にのみインクリメントされる。

```
155  let redactedCount = 0;
156  const cards: ProjectedCard[] = allCards
157    .filter((card) => cardIdsInScope.has(card.id))
158    .map((card) => {
159      const reviewed = isReviewed(card);
160      const projected = projectCardText(card, safeMode);
161      if (projected.redacted) redactedCount += 1;
```

これは `context_bundle_projection.test.ts:55` が明文化している `counts` 全体の不変条件（「文書全体を報告し、投影後の部分集合だけではない」）に反する。`reviewedCount`/`unreviewedCount`（`:121-123`）は `allCards` 全体から正しく計算されているが、`redactedCount` はそうなっていない。

`constraint === "summary"` の場合、`cardIdsInScope` は空の `Set`（`:145`）になるため、ループ本体は一度も実行されず、`counts.redacted` は `safeMode` の値に関わらず常に `0` になる。`"summary"` 制約は「構造とカウントのみ」を提供すると明記されている経路であり、外部エージェントはこの経路から「実際にどれだけの量のコンテンツが秘匿されているか」の情報を一切得られない。

`safeMode: true` かつ `constraint: "summary"` の組み合わせで `counts` を検証する既存テストは無く、このギャップは検出されない。

## 論点（人的判断が必要な理由）

`redactedCount` の意図された意味論——(a) 文書全体に対する秘匿件数の集計、または (b) 実際に投影・表示される部分集合に対する集計——のどちらを正とするかは、このMCPツールの反スコアリング・秘匿契約を所有する側が決めるべき設計判断であり、コード修正を先行させるべきではない。`reviewedCount`/`unreviewedCount` が(a)の解釈で実装されている以上、一貫性のためには(a)に揃えるのが自然に見えるが、`"summary"` 制約が意図的に最小情報しか出さない設計である可能性も排除できない。

## 影響

外部エージェントが `constraint: "summary"` で問い合わせた場合、SafeModeによってどの程度の秘匿が行われているかのシグナルを一切得られない。反スコアリング・SafeMode境界の安全側フェイルには該当しない（情報を過小に見せるだけで、秘匿すべきでない情報を漏らすわけではない）が、この工具の安全性表面の一部として、意図した仕様なのか見落としなのかを明確にすべきである。

## 解決記録（2026-08-07）

- **決定**: 論点の(a)「文書全体に対する秘匿件数の集計」を正とした。`context_bundle_projection.test.ts:55` の不変条件（「countsは文書全体を報告し、投影後の部分集合だけではない」）が既に契約として明文化されており、`reviewedCount`/`unreviewedCount` が(a)で実装済みのため、`redactedCount` を(a)に揃えるのは契約への整合であり新規設計判断ではない。
- **修正**: `context_bundle_projection.ts` の `redactedCount` を `allCards` 全体（文書全体）に対して計算するよう変更。`summary` 制約（空のscope）でも SafeMode 秘匿量を報告する。
- **テスト**: `context_bundle_projection.test.ts` の3既存アサーションを文書全体意味論へ更新（`reviewed-only` OFF→redacted:1、ON→redacted:4、`summary` OFF→redacted:1）。`summary` + `safeMode: true` → redacted:4 の新規テストを追加。
- **検証**: frontend 234 files / 1397 tests（+1）pass、typecheck 0 errors、MCP 49 tests pass。
- Status: Done
