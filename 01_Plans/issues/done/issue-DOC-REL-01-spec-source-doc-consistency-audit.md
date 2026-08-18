# Issue Memo: DOC-REL-01 仕様・実装・ドキュメント整合性監査（cross-layer consistency audit）

- Type: Process / Documentation quality
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Owner: TBD
- Scope: `00_Prompt/`, `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related ADR/Spec: `01_Plans/adr/ADR-0000-adr-governance.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: N/A
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

仕様（00〜02）・実装（03）・運用文書（04）の間で、参照先・責務・検証条件のズレが混在すると、
次の問題が発生する。

- 何を正本として判断すべきかが曖昧になる。
- 実装済み/未実装の判定に余計なレビューコストがかかる。
- AIエージェントが誤った参照先を追って変更範囲を誤る。

## 2) 現時点で確認された主要ギャップ（2026-02-27, 監査時点の記録）

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

- [x] `ROADMAP.md` の正本参照が `ADR-0007` へ一致している。
- [x] issue運用導線（ADR-0000 / 01_Plans/README / issues/README）の役割分担が重複なく説明される。
- [x] Active issue memo すべてに `Lifecycle` と `Source Issue` が存在する。
- [x] 新規 issue memo テンプレ（命名・必須メタ情報）が文書化される。

## 6) 実装タスク分解（Issue化後にチェック運用）

- [x] stale参照検査（docsリンク監査）
- [x] issue memoテンプレート（最小雛形）追加
- [x] backlog -> issue memo -> GitHub Issue の追跡確認手順を定義
- [x] 四半期棚卸しチェックリストを運用文書へ反映

## 7) Additional context

- 本Issueは「実装機能追加」ではなく、設計・運用・実装の関係性を維持するための品質管理Issue。
- トレードオフが大きい運用変更（例: 例外保存ポリシー変更）は、必要に応じて別ADR化する。


## 8) 実行TODO（詳細）

- [x] T0: DOC-REL-01 の終了条件を「Done移管」に明確化する。
- [x] T1: stale参照を棚卸しし、`ROADMAP.md` の正本リンク一致を再確認する。
- [x] T2: issue運用の起点を `01_Plans/issues/README.md` に明文化し、`01_Plans/README.md` とADR-0000の導線重複を解消する。
- [x] T3: `01_Plans/issues/TEMPLATE.md` に検証レベル（docs-check/unit/integration/e2e）を必須メタとして追加する。
- [x] T4: Active issue memo のメタ情報（Lifecycle/Source Issue）を機械検証する。
- [x] T5: 監査結果を本メモへ反映し、完了条件チェックを更新する。
- [x] T6: `validate_active_issue_memos.py` を関数分割し、検証レベルの妥当値チェックを追加する。
- [x] T7: validator のユニットテストを追加し、status/source 整合と validation level 異常系を固定する。
- [x] T8: validator に index と memo の `Status` / `Source Issue` 一致検証を追加し、差分ドリフトを防止する。
- [x] T9: Source Issue 未確定のため、運用ルールに従って本メモを `Done` に移管し Active 一覧から除外する。

## 9) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "01_Plans/future_backlog\.md|ADR-0007-future-backlog" ROADMAP.md 01_Plans/README.md 01_Plans/issues/README.md 01_Plans/issues/TEMPLATE.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
- 期待結果:
  - stale参照が運用正本（ROADMAP/01_Plans README群）で検出されない。
  - Active issue memo が required fields を満たす。
  - Markdown差分に whitespace error がない。

## 10) Progress log

- 2026-02-28: 参照整合性の監査を実施。ROADMAPの正本参照は `ADR-0007` で整合済みであることを確認。
- 2026-02-28: issue運用導線の重複を整理し、`Expected verification level` をテンプレート/READMEへ反映。
- 2026-02-28: Active issue memo 必須メタ項目の機械検証手順を追加。
- 2026-02-28: `Source Issue` が `TBD` のため、運用規約に合わせて本メモの `Status` は Draft を維持。進行中扱いは Source Issue URL 記載後に更新する。
- 2026-02-28: validator の仕様を強化（allowed verification level 判定）し、ユニットテストを追加して回帰防止を導入。
- 2026-02-28: Source Issue 未確定でも完了済みタスクを滞留させないため、本メモを `Done` へ移管し、`01_Plans/issues/README.md` の Active 一覧から除外。
- 2026-02-28: validator に index/memo 間の `Status` と `Source Issue` 一致検証を追加し、ユニットテストで mismatch 検知を固定。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。
