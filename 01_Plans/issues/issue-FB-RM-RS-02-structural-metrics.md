# Issue Draft: FB-RM-RS-02 構造メトリクス（健全性指標）を diagnostics へ追加

- Type: Feature request (enhancement)
- Status: Draft (起票用)
- Lifecycle: Draft -> Open (GitHub) -> In Progress -> Done -> GC(削除)
- Source Issue: TBD (GitHub Issue URLを記載)
- Priority: P1
- Owner: TBD
- Related Backlog: `FB-RM-RS-02` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `04_Documentation/diagnostics.md`
- Related Principles: `P-03` (レビュー追跡), `P-06` (視点制御), `P-07` (privacy-by-default)

## 1) 課題 / Problem statement

現状の Trace Analytics では「根拠リンク数」「孤立ノード数」などの**記述統計**は得られるが、
構造の健全性（偏り・分断・過密）を判断するための**評価可能なメトリクス定義**が不足している。

このため、レビュー時に以下の問題が残る。

- どこが“危険な構造”かを一貫して判定できない。
- diagnostics の警告優先度が人依存になり、再現性が低下する。
- E2E/回帰で「壊れていない」を機械的に検証しづらい。

## 2) 判断基準に基づく優先度評価

`AGENTS.md` の判断軸（価値・安全・企業/行政要件・後方互換）で評価すると、次の通り。

- 価値・判断軸（`ADR-0001`）: Human-in-the-loop のレビュー品質を定量化する基盤として有効（高）。
- 安全（`THREAT_MODEL.md` / SafeMode）: 外部送信不要でローカル計算可能。SafeModeを破らず導入可能（高）。
- 企業・行政要件（`enterprise_architecture.md`）: 監査説明性（「なぜ警告したか」）を補強できる（中〜高）。
- 後方互換（`schemas.md`）: 既存schemaを破壊せず `diagnostics` 拡張で導入可能（高）。

## 3) 提案する解決策 / Proposed solution

`diagnostics` パイプラインに「構造メトリクス」レイヤを追加し、少なくとも次を定義・実装する。

1. **connectedComponentCount**: 構造分断の検知
2. **largestComponentRatio**: 主成分への集中度
3. **degreeP95**: 局所過密の検知
4. **bridgeEdgeCount**: ボトルネック依存の把握

実装要件:

- すべて決定論（入力同一 → 出力同一）で計算する。
- `diagnostics_protocol` の schemaVersion ポリシーに整合させる。
- Markdown report / UI 表示 / worker 経路で同一値を参照する。

## 4) 受入条件 / Acceptance criteria

- [ ] 指標定義（意味・計算式・しきい値初期値）が `04_Documentation/diagnostics.md` に記載される。
- [ ] `src/worker/*` でメトリクス計算が実装され、決定論テストで固定される。
- [ ] 既存 diagnostics 出力互換を維持し、旧クライアントで致命的失敗を起こさない。
- [ ] SidePanel/Report で追加指標が表示される。
- [ ] E2Eまたは統合テストで「偏った構造」「分断構造」の検知シナリオが1件以上追加される。

## 5) 検討した代替案 / Alternatives considered

- 代替案A: 既存 Trace Analytics のみで運用を継続
  - 欠点: 健全性評価が主観依存となり、監査説明性が弱い。
- 代替案B: LLM評価に委譲
  - 欠点: 非決定性が増し、CI回帰基準として不適。

## 6) 実装タスク分解（Issue化後にチェック運用）

- [ ] metrics contract（型/命名/閾値）確定
- [ ] worker計算実装 + unit test
- [ ] diagnostics markdown 出力反映
- [ ] SidePanel 表示反映
- [ ] regression guards への追加
- [ ] ドキュメント同期（diagnostics / operations / release）

## 7) Additional context

- 本Issueは `ADR-0000` の「Issue=Action / ADR=Decision」分離方針に従う。
- トレードオフ（しきい値や警告ポリシー）が大きい場合のみ、後続でADR起票する。
