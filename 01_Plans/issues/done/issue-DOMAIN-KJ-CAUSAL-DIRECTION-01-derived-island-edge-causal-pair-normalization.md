# Issue: DOMAIN-KJ-CAUSAL-DIRECTION-01 派生島 causal の方向保存

- Type: Bug
- Status: Done
- Source Issue: `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/island_edge_aggregate.ts`, 同テスト、TS/Python共有fixture
- Related ADR/Spec: `02_Architecture/schemas.md` §3.3.1, `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`
- Expected verification level: unit

## 完了内容

`getDerivedIslandEdges()` が島間派生辺を集約するとき、`causal` まで辞書順へ正規化していたため、原因側の島IDが結果側より後ろに並ぶケースで原因→結果が反転し、A→B/B→Aの逆向き主張も同一aggregateへ畳み込まれていた。

修正後は `resolveKnownEdgeType(edge.type) === "causal"` の場合だけ、`fromIslandId`（原因）→`toIslandId`（結果）をそのまま使う。例外は表示用端点だけでなく `derived-island:<from>|<to>|<type>` の集約keyにも適用し、逆向き2本を別aggregateとして保持する。`related` / `negate` / `mutual` / `equivalence` と未知種別の従来の無方向正規化は維持した。

回帰testとして、辞書順と因果方向が逆になる1本、および A→B と B→A が別aggregateに残るケースを追加した。TS側の既知bugを許容するため存在していた `tsCurrentDerivedIslandEdges` golden と「causalだけ差異を許す」testを退役し、TS/Python双方が単一の `derivedIslandEdges` 契約正を再び共有するようにした。

## relation summary 互換性判断

旧bug状態で生成された派生 `causal` relation summary は、修正後に `sourceSignature` の端点順が変わる場合がある。逆順signatureへのfallback照合は実装しない。

理由は、旧summary自体が原因/結果を逆に読んだ関係へ生成された可能性があり、正しい向きへ自動再接続すると誤った説明を温存しうるため。プレリリース段階では、そのsummaryを一度「未作成」として失効させ、必要なら正しい関係から再生成する方を安全側と判断した。永続DocumentV1や元のedge自体は変更しない。

## 検証結果

GitHub Actions one-shot run `34396002249`:

- targeted frontend `island_edge_aggregate.test.ts`: pass
- targeted frontend TS/Python equivalence test: pass
- backend `test_derived_island_relations_ts_equivalence.py`: pass
- frontend full test suite: pass
- TypeScript typecheck: pass
- `git diff --check` / diff scope: pass
- one-shot workflow retirement: pass

製品挙動変更は派生 island↔island の `causal` 方向保存に限定した。島↔lone-wolf-cardの方向shape問題は元issueのOut of Scopeどおり別課題とする。