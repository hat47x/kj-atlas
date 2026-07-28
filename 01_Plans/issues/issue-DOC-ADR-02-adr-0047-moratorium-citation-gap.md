# Issue Draft: DOC-ADR-02 ADR-0047モラトリアムの再起票条件を引用していないADRが9件

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`, `01_Plans/adr/ADR-0051-bulk-critique-reason-recording.md`, `01_Plans/adr/ADR-0052-canvas-and-menu-aria-semantics.md`, `01_Plans/adr/ADR-0053-support-diagnostics-bundle-boundary.md`, `01_Plans/adr/ADR-0055-work-mode-navigation-semantics.md`, `01_Plans/adr/ADR-0056-card-provenance-metadata-boundary.md`, `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`, `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0060-representative-visual-cue-source-boundary.md`, `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`
- Related ADR/Spec: `ADR-0047`
- Expected verification level: `docs-check`

## 課題

`ADR-0047`（2026-06-10、Accepted）は新規の設計判断ADRにモラトリアムを宣言し、再起票基準 R-1（実使用の摩擦）/ R-2（段階遷移）/ R-3（非機能境界の超過）/ R-4（破壊的契約変更）のいずれかに該当する場合のみ新規ADRを認めている（`:37-40,48`）。

ADR-0047以降に起票された13件のADR（ADR-0048〜ADR-0061）のうち、`ADR-0047` またはR-1..R-4のいずれかを本文中で明示的に引用しているのは5件（ADR-0048, 0049, 0050, 0054, 0057）のみで、残り9件（ADR-0051, 0052, 0053, 0055, 0056, 0058, 0059, 0060, 0061）は本文中に `ADR-0047` への言及もR-トリガーへの言及も一切ない（grep確認、マッチ無し）。`ADR-0047` 自身にも、モラトリアムが実務上どう運用されているか（縮小・解除されたか）を示す改訂・"Superseded by"・注記は無い。

## 論点（人的判断が必要な理由）

以下のいずれであるかは、プロジェクトの文脈を持つ人にしか判断できない。

(a) これら9件が暗黙にR-トリガー（例: R-1実使用の摩擦）を満たしているが、単に明記していないだけ。
(b) モラトリアムは実務上すでに緩和・失効しているが、`ADR-0047` 自体の更新が追いついていない。

判断次第で対応が変わる: (a)なら該当ADRへトリガー根拠を遡及的に追記する。(b)なら `ADR-0047` を改訂し、モラトリアムがもはや厳格運用されていないことを明記する。

## 影響

ドキュメントの整合性の問題であり、実行時の挙動には影響しない。ただし、`ADR-0047` のモラトリアムを字面通り信頼すると、実際のADR起票実績（9/13件が根拠不記載）と矛盾するため、プロセス文書としての信頼性を損なう。
