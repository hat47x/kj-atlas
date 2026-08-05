# Issue Memo: DOC-ARCH-01 02 Architecture source/log separation and value traceability

- Type: Documentation quality / Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `00_Prompt/`, `02_Architecture/`, `AGENTS.md`
- Related Backlog: `N/A`
- Related ADR/Spec: `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `02_Architecture/design/architecture.html`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Dependencies: N/A
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DOC-ARCH-01
- RequirementStatement: 00/02 文書から、プロジェクト価値、設計正本、実行ログ、後続フェーズ契約を迷わず辿れるようにする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=00/02が上流正本である; 操作=価値トレーサビリティと正本/ログ分離方針を確認する; 期待結果=新規参加者とAIエージェントが価値から設計へ辿れる; 除外=設計契約そのものの変更。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export

## 1) 課題 / Problem statement

`02_Architecture/api.md` と `02_Architecture/schemas.md` には、現行契約、MVP説明、Stream実行ログ、freeze note が同じ本文に蓄積している。これにより、どの記述が「いま参照すべき正本」なのか、どの記述が「履歴・監査ログ」なのかが判断しづらい。

また、`00_Prompt/domain.md` が定義する価値（保留、違和感、可逆性）と、02層の設計要素（SafeMode、ContextBundle、proposal-only、visibilityなど）との対応が一覧化されていない。結果として、設計変更時に「どの価値を守るための設計か」を説明しにくい。

## 2) 背景 / Context

- `domain.md` は概念の憲法として扱われる。
- `02_Architecture/design/architecture.html` / `schemas.md` / `api.md` は実装者が参照する設計正本である。
- `AGENTS.md` は新規AIエージェントの入口であり、新しい主要文書を追加した場合は Project Map 更新が必要である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 価値から設計への導線が弱いと、単なる機能追加に流れやすい。
- 安全（THREAT_MODEL / SafeMode）: SafeMode や share/export 境界の正本が埋もれると、安全後退を見落としやすい。
- 企業・行政要件（enterprise_architecture）: 監査時に「なぜその設計か」を説明しやすくする。
- 後方互換（schemas）: 契約変更と履歴ログを分離し、互換判断を明確にする。

## 4) 提案する解決策 / Proposed solution

- `02_Architecture/value_traceability.md` を追加し、価値、設計要素、受入条件、検証観点を対応付ける。
- `02_Architecture/design/architecture.html` から value traceability へ導線を追加する。
- `AGENTS.md` の Project Map に新規文書を追加する。
- `02_Architecture/contract_reading_guide.md` を追加し、現行契約と履歴ログの読み分けを明示する。
- 後続タスクとして、`api.md` / `schemas.md` の正本本文と Stream 実行ログを段階的に分離する。

Non-goals:

- API/schema 契約値を変更しない。
- Stream履歴を削除しない。
- 03実装を変更しない。

## 5) 受入条件 / Acceptance criteria

- [x] 価値から設計要素へ辿る文書が `02_Architecture` に追加される。
- [x] `02_Architecture/design/architecture.html` と `AGENTS.md` から新規文書へ辿れる。
- [x] SafeMode / share/export / proposal-only / review attribution の価値対応が説明される。
- [x] `api.md` / `schemas.md` の現行契約と Stream / freeze 履歴の読み分け導線がある。
- [x] `api.md` / `schemas.md` の正本/ログ分離は後続タスクとして明記され、今回PRでは契約値を変更しない。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: `02_Architecture/value_traceability.md` を追加する。
- [x] T2: `02_Architecture/design/architecture.html` に価値トレーサビリティ導線を追加する。
- [x] T3: `AGENTS.md` の Project Map を同期する。
- [x] T4: `api.md` / `schemas.md` のログ分離方針を本メモに残す。
- [x] T5: `02_Architecture/contract_reading_guide.md` を追加し、現行契約/履歴ログの読み分けを明示する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check`
  - `rg -n "value_traceability|contract_reading_guide|DOC-ARCH-01" AGENTS.md 01_Plans/issues 02_Architecture`
  - Markdown relative link check for changed docs
- 期待結果:
  - 新規文書への導線が存在する。
  - 契約値や実装ファイルへの差分がない。

## 8) 代替案 / Alternatives considered

- `02_Architecture/design/architecture.html` に直接長い対応表を追加する:
  - 却下。最上位設計文書がさらに肥大化する。
- すぐに `api.md` / `schemas.md` を分割する:
  - 保留。差分が大きくなるため、まず価値導線を作ってから段階的に分離する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 新規文書が正本を増やしすぎる。
- 影響範囲: 00/02の参照導線。
- ロールバック手順: 新規文書と導線追加を revert する。契約値を変更しないため実装影響はない。

## 10) Additional context

- 本件は設計判断変更ではなく、既存価値と既存設計の追跡性改善である。
- API/schema本文の大規模整理が必要になった場合は、本メモから後続 issue に分割する。

## 11) Closeout

- Completed by: PR #2131 `[codex] Align 00 and 02 value documentation`
- Result: `value_traceability.md` と `contract_reading_guide.md` を追加し、`02_Architecture/design/architecture.html` / `api.md` / `schemas.md` / `AGENTS.md` から導線を張った。
- Validation: `git diff --check`, active issue memo validator, validator unit tests, Markdown relative link check, `rg` 導線確認。
