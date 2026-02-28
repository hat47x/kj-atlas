# Issue Draft: DOC-REL-01 仕様・実装・ドキュメント整合性監査（cross-layer consistency audit）

- Type: Process / Documentation quality
- Status: Draft (起票用)
- Lifecycle: Draft -> Open (GitHub) -> In Progress -> Done -> GC(削除)
- Source Issue: TBD (GitHub Issue URLを記載)
- Priority: P1
- Owner: TBD
- Scope: `00_Prompt/`, `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related ADR/Spec: `01_Plans/adr/ADR-0000-adr-governance.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`

## 1) 課題 / Problem statement

仕様（00〜02）・実装（03）・運用文書（04）の間で、参照先・責務・検証条件のズレが混在すると、
次の問題が発生する。

- 何を正本として判断すべきかが曖昧になる。
- 実装済み/未実装の判定に余計なレビューコストがかかる。
- AIエージェントが誤った参照先を追って変更範囲を誤る。

## 2) 現時点で確認された主要ギャップ（2026-02-27）

### A. 参照整合性ギャップ（Doc -> Doc）

1. `ROADMAP.md` が roadmap分解の正本を `01_Plans/future_backlog.md` と参照しているが、
   実際の正本は `01_Plans/adr/ADR-0007-future-backlog.md`。
2. issue補助メモ運用は `ADR-0000` と `01_Plans/README.md` と `01_Plans/issues/README.md` に分散し、
   どの情報を最初に見るべきかが明確でない。

### B. 仕様と運用の接続ギャップ（Spec -> Ops）

3. `ADR-0019` では E2E を品質ゲートとして定義している一方、Docs-only変更時にどこまで実行必須かが
   CONTRIBUTING/運用文書側で読み取りづらい場合がある。
4. backlog項目ごとに「実装確認テスト種別（unit/integration/e2e）」の期待が表形式で固定されておらず、
   PRごとの運用判断がぶれやすい。

### C. 仕様と実装の接続ギャップ（Spec -> Source）

5. 一部バックログ項目は「新規Issue化」のまま残り、実装入口（Issue URL / memo / owner）が不足しやすい。
6. 設計ドキュメントに対する実装対応状況（Implemented / Planned / Deferred）が横断的に一覧化されていない。

## 3) 判断基準に基づく優先度評価

- 価値・判断軸（ADR-0001）: 判断基準の再現性確保に直結（高）。
- 安全（THREAT_MODEL / SafeMode）: 仕様誤読による安全要件逸脱を予防（高）。
- 企業・行政要件（enterprise_architecture）: 監査時の説明可能性を向上（中〜高）。
- 後方互換（schemas）: 互換破壊の早期検知に有効（高）。

## 4) 提案する解決策 / Proposed solution

1. **参照正規化**
   - stale参照を修正し、正本リンクを単一化する。
2. **運用導線の明確化**
   - issue運用は `01_Plans/issues/README.md` を起点に統一し、他文書は導線のみ保持。
3. **検証期待の見える化**
   - backlog/issueテンプレに「期待テスト種別」を必須項目として追加する。
4. **追跡性の強化**
   - Active issue memo に Backlog ID / ADR参照 / Source Issue URL を必須化する。

## 5) 受入条件 / Acceptance criteria

- [ ] `ROADMAP.md` の正本参照が `ADR-0007` へ一致している。
- [ ] issue運用導線（ADR-0000 / 01_Plans/README / issues/README）の役割分担が重複なく説明される。
- [ ] Active issue memo すべてに `Lifecycle` と `Source Issue` が存在する。
- [ ] 新規 issue memo テンプレ（命名・必須メタ情報）が文書化される。

## 6) 実装タスク分解（Issue化後にチェック運用）

- [ ] stale参照検査（docsリンク監査）
- [ ] issue memoテンプレート（最小雛形）追加
- [ ] backlog -> issue memo -> GitHub Issue の追跡確認手順を定義
- [ ] 四半期棚卸しチェックリストを運用文書へ反映

## 7) Additional context

- 本Issueは「実装機能追加」ではなく、設計・運用・実装の関係性を維持するための品質管理Issue。
- トレードオフが大きい運用変更（例: 例外保存ポリシー変更）は、必要に応じて別ADR化する。
