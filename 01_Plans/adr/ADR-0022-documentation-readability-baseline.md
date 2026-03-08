# ADR-0022: Documentation Readability Baseline

- Status: Proposed
- Date: 2026-03-08
- Deciders: Project Maintainers
- Scope: `01_Plans/` + `02_Architecture/` + `04_Documentation/`（文書記述規約に限定）
- Derived-from: `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`（ADR候補B）

## Context

DOC-OPS-04 の前処理監査では、ADR候補B（Documentation Readability Baseline）として次の課題が記録された。

- 読者前提、非目標、到達目標の記載粒度が文書ごとに揺れ、初読時の理解コストが高い。
- 同一概念でも表記ゆれ（役割名・運用語彙・DoD表現）があり、文書横断で判断基準がぶれやすい。
- docs-check は運用されているが、可読性の最低線（何を最低限書くべきか）が共通規約として固定されていない。

本ADRは、実装仕様を増やすためではなく、既存仕様を「読み違えにくく再開しやすい」形で維持するための可読性ベースラインを定義する。

比較した主要選択肢は以下。

1. **選択肢A: 既存運用のまま（各文書の裁量に委ねる）**
   - 長所: 移行コスト最小。
   - 短所: 可読性品質が属人化し、更新時の再学習コストが継続。
2. **選択肢B: 文書種別ごとの厳密テンプレを全面義務化**
   - 長所: 形式差が最小化される。
   - 短所: 過剰拘束となり、短い補助文書まで冗長化する。
3. **選択肢C: 最小必須メタだけ共通化し、本文構成は目的に応じて柔軟運用（採用）**
   - 長所: 可読性の最低線を揃えつつ、文書特性ごとの表現自由度を維持できる。
   - 短所: 最小必須メタの運用監査（docs-check相当）が必要。

## Decision

**採用方針**: Documentation Readability Baseline として、全レイヤ文書に共通する「最小必須記述」と「用語整合ルール」を固定し、本文構成は文書目的に応じて柔軟に運用する。

採用理由（トレードオフ）は以下。

1. 可読性を上げる目的は「統一フォーマットの強制」ではなく「初読者の迷子防止」である。
2. 必須メタの最小集合を固定することで、可読性と保守負荷のバランスを取れる。
3. docs-check との接続点を明確化し、運用で回る最小規約として継続可能性を高める。

### 1) Readability Baseline（最低要件）

文書新規作成・大幅改訂時は、少なくとも次を満たす。

- **RBL-1: 読者前提**
  - 想定読者（例: Maintainer / Operator / Contributor / AI Agent）を冒頭または導入で明示する。
- **RBL-2: 目的と非目標**
  - 「この文書が決めること」と「この文書で決めないこと」を区別して記載する。
- **RBL-3: 到達目標（完了状態）**
  - 読了後に何を判断・実行できるべきかを1〜3項目で示す。
- **RBL-4: 参照導線**
  - 上流根拠（ADR/Architecture/Prompt）と下流適用先（実装/運用文書）を最低1件ずつ示す。
- **RBL-5: 用語整合**
  - 役割名・状態名・判定語彙を既存正本（`00_Prompt/domain.md` など）と矛盾させない。

### 2) 適用境界

- 本ベースラインは **記述品質の最低線** を定義する。
- 文書種別（ADR、運用手順、Issue補助メモ、Architecture Spec）の章構成そのものは、各テンプレ規約を優先する。
- 既存文書を一括改修する義務は課さず、**差分が発生した文書から段階適用**する。

### 3) 検証接続（docs-check相当）

- 必須メタ・見出し整合・用語整合は docs-check の対象とする。
- docs-check が未自動化の観点は、PRまたは作業ログで実行コマンドと期待結果を明示する。

### 4) 非目標

- 本ADRで新しい機能要件・実装要件を追加しない。
- 本ADRで全既存文書の章構成統一を強制しない。
- 本ADRで CI 必須化範囲（fail条件）を最終確定しない。

## Consequences

- 初読時の理解コストが下がり、文書更新時の差分レビュー観点（何が目的で何が非目標か）が明確になる。
- 文書横断ドリフト（用語ゆれ・導線欠落）を早期に検知しやすくなる。
- 一方で、執筆時に最小メタ確認が増えるため、短期的には文書作成コストがわずかに上がる。
- 適用を段階導入とするため、移行期は「適用済み文書」と「未適用文書」が混在する。

## Traceability

- Related: `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- Related: `00_Prompt/domain.md`
- Related: `00_Prompt/agent_handover.md`
- Related: `01_Plans/adr/ADR-0000-adr-governance.md`
- Related: `01_Plans/adr/ADR-0018-coding-standards-and-smell-remediation.md`
- Related: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
