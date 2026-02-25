# ADR-0000: 01_Plans を ADR で管理する方針

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`

## Context

従来の `01_Plans` は `roadmap.md` / `phase*.md` / `phaseX*.md` / `value_to_requirements.md` に分散し、
意思決定（なぜそうするか）と実行計画（いつ・何をするか）が混在していた。
この状態では、判断根拠の追跡と差分レビューが困難になる。

## Decision

`01_Plans` 配下の計画文書を **ADR（Architecture Decision Record）形式へ全面移行**する。
今後の要件・計画・運用方針は `01_Plans/adr/ADR-xxxx-*.md` で管理する。

### ADR 管理方式

1. 採番: `ADR-0000` からの連番（4桁ゼロ埋め）。
2. 1 ADR = 1 意思決定境界（必要なら旧文書1つを1 ADRとして移管）。
3. 必須ヘッダ: `Status` / `Date` / `Deciders` / `Scope`。
4. 必須章: `Context` / `Decision` / `Consequences` / `Traceability`。
5. 変更時は「追記優先」。破壊的改変ではなく、
   `Supersedes` / `Superseded by` を使って履歴を残す。
6. 計画の実行項目は ADR 内でチェックリストまたは Gate 条件として表現する。
7. 旧 `phase*.md` などのタスク管理文書は廃止し、ADRへ一本化する。

### ADR粒度ポリシー（2026-02-24 追記）

8. 1 ADR の目安は **50〜180行**。200行を継続的に超える場合は分割候補とする。
9. 分割軸は「意思決定境界」（例: 価値原則 / 要求マッピング / 受入基準 / 運用手順）。
10. 親ADRは要約と索引に縮約し、詳細は子ADRへ委譲して可読性を維持する。
11. 情報欠落を避けるため、分割時は `Traceability` に `Derived-from` を必須記載する。

## Consequences

- どの判断が、どの要件・設計・実装に影響するかを追跡しやすくなる。
- 既存参照（AGENTS.md 等）は ADR パスへ更新が必要。
- 既存文書の情報は ADR 側へ欠落なく移管し、旧文書は削除する。

## Traceability

- Replaces: `01_Plans/roadmap.md`, `01_Plans/value_to_requirements.md`,
  `01_Plans/phase0_bootstrap.md`, `01_Plans/phase1_canvas_mvp.md`,
  `01_Plans/phase2_qualitative_integration.md`, `01_Plans/phase3_review_governance.md`,
  `01_Plans/phaseX_future_backlog.md`, `01_Plans/phaseX_cli_tool.md`,
  `01_Plans/phaseX_local_llm_integration.md`
