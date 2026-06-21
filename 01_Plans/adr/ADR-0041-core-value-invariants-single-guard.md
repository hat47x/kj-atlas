# ADR-0041: 根幹価値の不変条件を単一の砦で守る

- Status: Accepted
- Date: 2026-06-10
- Deciders: Maintainer（委譲された意思決定権限）
- Scope: `01_Plans/`, `02_Architecture/value_traceability.md`, `03_Implement/`

## Context

機能実装が急速に出揃った（CE0–CE4 Done、DOMAIN-EXPR 進行、undo/redo・safe_mode・LLM provider 実装済み）。
この段階で根幹価値（`domain.md`：保留・違和感・可逆性／`ai_cognitive_externalization_requirements.md`：proposal-only・安全な外在化）を**最大化**する上での最大のボトルネックは、機能の不在ではなく「実装が根幹価値を裏切らないこと」の保証構造の欠落である。

事実として、根幹価値の禁止事項（非後退の不変条件）は実装側に**散在**している。

- SafeMode 既定ON: `03_Implement/frontend/src/domain/policy/safe_mode.test.ts`
- proposal-only（auto-apply 禁止）: `03_Implement/frontend/src/domain/ce2_proposal_only.test.ts`
- `human_reviewed` 自動昇格禁止: `03_Implement/frontend/src/domain/ce2_suggestion_candidates.test.ts`
- dryRun 副作用なし・監査4点: `03_Implement/backend/tests/test_ce2_proposal_api.py`, `test_audit.py`
- Consensus Graph 直接更新禁止: CE0 契約テスト群

不変条件の「正本」は `02_Architecture/value_traceability.md`（検証観点列）にあるが、それらを **1つの実行可能な砦** として束ねた横断テストも、正本ADRも存在しない（`core_value*` / `invariant*` テストは grep 0件）。

この状態の危険性は段階とともに増す。Codex を含む並行実装が高速で進むほど、ある PR が1つの不変条件を静かに後退させても、関連する個別テストが**たまたま変更対象でなければ**気づけない。根幹価値は「1箇所の違反で全体が崩れる」性質を持つのに、それを守る単一の砦がない。

## Decision

根幹価値の非後退不変条件を、**単一の正本（本ADR）＋単一の横断テスト**で守る。

### 不変条件セット（Core Value Invariants, CVI）

`value_traceability.md` から導出し、次を非後退の不変条件として固定する。実装都合での緩和を禁止する。

- **CVI-1 SafeMode 既定ON**: 共有・export 既定で未レビュー本文・生テキストを漏らさない。
- **CVI-2 proposal-only**: AI 出力は候補のみ。auto-apply / auto-confirm / auto-publish を全経路で禁止。
- **CVI-3 人手レビュー昇格のみ**: `unreviewed → human_reviewed` は人手のみ。AI/worker/API 自動昇格禁止。
- **CVI-4 Consensus 直接更新禁止**: `patch + approval` 以外で Consensus Graph を更新しない。
- **CVI-5 dryRun 無副作用**: `dryRun=true` は DB 永続化・外部共有・review 昇格を起こさない。
- **CVI-6 provider=none 既定で価値成立**: `KJ_ATLAS_LLM_PROVIDER=none` でも保留・違和感・構造化・共有前確認の主要価値が成立。
- **CVI-7 保留・違和感の非破壊**: AI は保留（Hold）を勝手に解消せず、違和感（Critique）を無視・正当化しない。表示制御（hidden/collapse）は内容削除と分離。

### 単一の砦

- 上記 CVI-1..7 を **1ファイルの横断テスト**（実装担当が新設）に集約し、各 CVI が「どの既存テスト／コード契約で担保されるか」を参照リンクとして列挙する。新規ロジックの再実装ではなく、**既存の散在テストを CVI へ索引づけ、欠落 CVI のみ新規カバー**する。
- 砦テストは CI の回帰ゲートに含める（個人OSS段階では既存 vitest/pytest 実行に同梱でよく、専用ジョブ新設は必須としない）。
- 非目標: 不変条件の新規追加・厳格化（本ADRは既存価値の保護であり拡張ではない）。形式手法・実行時アサーションの全面導入。

## Consequences

- 期待される効果:
  - 並行実装下でも、根幹価値の後退が単一テストの赤で即検知できる。
  - `value_traceability.md`（正本）と実装テスト（砦）が CVI-ID で 1:1 に追跡可能になる。
  - レビュー時「この PR は CVI に触れるか」を CVI-ID で機械的に問える。
- 想定される副作用/制約:
  - 砦テストの新設・維持コスト（ただし大半は既存テストへの索引づけで賄える）。
  - CVI の表現が `value_traceability.md` とずれると二重管理になる → 正本は value_traceability、砦はその参照とする。
- 移行時に必要な対応:
  - `02_Architecture/value_traceability.md` に CVI-1..7 の ID と参照先テストの対応表を追記する。
  - 実装 issue（`CORE-VALUE-GUARD-01`）で砦テストの新設と既存テスト索引づけを行う。

## Traceability

- Related: `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`
- Related: `02_Architecture/value_traceability.md`（不変条件の正本）
- Related: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `ADR-0040-domain-expression-first-class-strategy.md`
- Related: `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`（緩和禁止＝プロダクト不変条件の維持方針）
- Derived-from: 2026-06-10 価値最大化の不足分析（機能は出揃い、保護構造が最大の欠落）
