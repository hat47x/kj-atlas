# Issue Memo: DOMAIN-ALIGN-01 00/02 vocabulary synchronization

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `00_Prompt/`, `02_Architecture/`
- Related Backlog: `N/A`
- Related ADR/Spec: `00_Prompt/domain.md`, `00_Prompt/handoff.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`, `02_Architecture/review_attribution.md`
- Dependencies: N/A
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-ALIGN-01
- RequirementStatement: 00層の正規語彙を、02層で実際に使われる Island / Consensus Graph / WorkingGraph / ContextProjectionGraph へ同期する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=domain.mdが概念上位正本である; 操作=00/02の中核語彙を確認する; 期待結果=用語の意味とコード/設計上の対応が一致する; 除外=新概念の追加。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode

## 1) 課題 / Problem statement

`domain.md` は「概念の憲法」とされるが、現在の02層で重要になっている `Island`、`Consensus Graph`、`WorkingGraph`、`ContextProjectionGraph` が、中核オブジェクト定義として十分に整理されていない。

このままだと、AIエージェントや新規開発者が `Cluster` / `Island` / `Consensus Graph` / `Core Graph` の関係を誤読し、設計正本で禁止されている direct write や自動昇格の境界を弱める可能性がある。

## 2) 背景 / Context

- `domain.md` は保留、違和感、可逆性を最上位概念として定義している。
- `ai_cognitive_externalization_requirements.md` は Consensus Graph / WorkingGraph / ContextProjectionGraph を中核に置いている。
- `architecture.md` と `schemas.md` は Contract Freeze で同語彙を固定している。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 保留・可逆性・人間レビューを設計語彙として守りやすくする。
- 安全（THREAT_MODEL / SafeMode）: `human_reviewed` の自動昇格や Consensus Graph direct write を誤って許容しない。
- 企業・行政要件（enterprise_architecture）: 監査説明で用語の揺れを減らす。
- 後方互換（schemas）: `Core Graph` を履歴用語に限定し、契約語彙の再導入を防ぐ。

## 4) 提案する解決策 / Proposed solution

- `domain.md` の中核オブジェクト表に `Island` と三層Graph語彙を追加する。
- `Core Graph` は旧称として扱い、正規語彙は `Consensus Graph` に統一する。
- 外向け/共有向け表現の注意にも、未レビューAI文章を正式版として共有しない旨を明示する。

Non-goals:

- データスキーマを変更しない。
- AI機能の責務を拡張しない。
- `reviewed` / `human_reviewed` の契約値を変更しない。

## 5) 受入条件 / Acceptance criteria

- [x] `domain.md` で `Island` と `Cluster` の関係が説明される。
- [x] `Consensus Graph` / `WorkingGraph` / `ContextProjectionGraph` が `domain.md` から参照できる。
- [x] `Core Graph` は旧称であり、契約語彙として再導入しないことが明記される。
- [x] 00/02 の主要文書で不自然な「外部送信」系の利用者向け表現が残らない。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: `domain.md` の中核オブジェクト定義を更新する。
- [x] T2: `domain.md` のAI役割定義に proposal-only / 人手レビュー境界を補足する。
- [x] T3: 00/02 の硬い共有表現をスキャンし、設計用語として必要な箇所以外を自然な表現へ直す。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check`
  - `rg -n "Consensus Graph|WorkingGraph|ContextProjectionGraph|Core Graph|外部送信|送信先" 00_Prompt 02_Architecture`
- 期待結果:
  - 新規語彙が `domain.md` で説明される。
  - `Core Graph` は旧称または履歴文脈に限定される。

## 8) 代替案 / Alternatives considered

- 02層だけで語彙を維持する:
  - 却下。00層が上位正本であるため、AIエージェントが先に読む `domain.md` に反映する必要がある。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: domain.md が設計詳細を持ちすぎる。
- 影響範囲: 00/02 の概念導線。
- ロールバック手順: `domain.md` の追加語彙と関連導線を revert する。

## 10) Additional context

- 本件は用語同期であり、思想変更ではない。新しい判断軸が必要になった場合は ADR 化する。

## 11) Closeout

- Completed by: PR #2131 `[codex] Align 00 and 02 value documentation`
- Result: `domain.md` に `Island` / `Consensus Graph` / `WorkingGraph` / `ContextProjectionGraph` を同期し、AIの proposal-only / 人手レビュー境界を補足した。
- Validation: `git diff --check`, active issue memo validator, validator unit tests, `rg` による語彙・表現確認。
