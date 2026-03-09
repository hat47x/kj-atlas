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

加えて、以下の AC/DoD 不足がある。

- AC不足: 可読性タスクごとに「適用対象（どの文書へ適用するか）」と「非目標（今回触らない文書）」の境界が曖昧になりやすい。
- DoD不足: docs-check 未自動化項目の手動確認結果が、再現可能な形で残らないケースがある。

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

## Plan（AC/DoD不足の補完提案）

- 受入条件の不足（適用境界の曖昧さ）を AC-4 として明文化し、レビュー時に「今回触る文書」と「触らない文書」を判別可能にする。
- 完了条件の不足（未自動化確認ログの再現性欠如）を DoD-2 / DoD-3 として補完し、手動確認の実行コマンドと判定理由を追跡可能にする。
- 適用は段階導入（差分発生文書のみ）とし、一括改修は行わない。

## Execute（本ADRで実施した具体化）

- Readability Baseline（RBL-1〜RBL-5）を定義し、最低限の記述要件を固定した。
- DOC-OPS-04 A-I/F の固定語彙（Audience / Goal / Non-goal / Outcome / Upstream Reference / Downstream Apply / Verification）との整合を明示した。
- docs-check 連携時の検証観点と、未自動化領域の運用要件（コマンド・判定理由の記録）を明記した。

## Decision

**採用方針**: Documentation Readability Baseline として、全レイヤ文書に共通する「最小必須記述」と「用語整合ルール」を固定し、本文構成は文書目的に応じて柔軟に運用する。

採用理由（トレードオフ）は以下。

1. 可読性を上げる目的は「統一フォーマットの強制」ではなく「初読者の迷子防止」である。
2. 必須メタの最小集合を固定することで、可読性と保守負荷のバランスを取れる。
3. docs-check との接続点を明確化し、運用で回る最小規約として継続可能性を高める。

### 1) Interface Vocabulary（A系I/F語彙準拠）

本ADRで扱う可読性I/F語彙は、`ADR-0022-doc-ops-04-documentation-information-interface.md` の固定語彙
（正本 / 暫定メモ / 決裁入力 / 例外承認）と整合する形で、文書種別を横断して次を標準語彙として扱う。

- **Audience**: 想定読者（Maintainer / Operator / Contributor / AI Agent）
- **Goal**: 文書が決めること・達成させること
- **Non-goal**: 本文書で決めないこと
- **Outcome**: 読了後に判断・実行可能になる到達状態
- **Upstream Reference**: 判断根拠となる上流文書（Prompt / ADR / Architecture）
- **Downstream Apply**: 適用先となる下流文書（Implementation / Operations / Runbook）
- **Verification**: docs-check 相当での検証観点

### 2) Readability Baseline（最低要件）

文書新規作成・大幅改訂時は、少なくとも次を満たす。

- **RBL-1: Audience（読者前提）**
  - 想定読者を冒頭または導入で明示する。
- **RBL-2: Goal / Non-goal（目的と非目標）**
  - 「この文書が決めること」と「この文書で決めないこと」を区別して記載する。
- **RBL-3: Outcome（到達目標）**
  - 読了後に何を判断・実行できるべきかを1〜3項目で示す。
- **RBL-4: Upstream / Downstream（参照導線）**
  - 上流根拠（ADR/Architecture/Prompt）と下流適用先（実装/運用文書）を最低1件ずつ示す。
- **RBL-5: Terminology Consistency（用語整合）**
  - 役割名・状態名・判定語彙を既存正本（`00_Prompt/domain.md` など）と矛盾させない。

### 3) 適用境界

- 本ベースラインは **記述品質の最低線** を定義する。
- 文書種別（ADR、運用手順、Issue補助メモ、Architecture Spec）の章構成そのものは、各テンプレ規約を優先する。
- 既存文書を一括改修する義務は課さず、**差分が発生した文書から段階適用**する。

### 4) 検証接続（docs-check相当）

- 必須メタ・見出し整合・用語整合は docs-check の対象とする。
- docs-check が未自動化の観点は、PRまたは作業ログで実行コマンドと期待結果を明示する。

### 5) Acceptance Criteria / Definition of Done（補完）

本ADR適用タスクは、以下を満たした時点で完了とする（Plan段階で合意対象として明示する）。

- **AC-1**: 対象文書に Audience / Goal / Non-goal / Outcome が明示されている。
- **AC-2**: 対象文書に Upstream Reference と Downstream Apply が各1件以上ある。
- **AC-3**: 用語が `00_Prompt/domain.md` と矛盾しない（役割名・判定語彙を含む）。
- **AC-4**: 適用対象文書と非目標文書（今回更新しない範囲）が明示され、レビュー時に境界が判別できる。
- **DoD-1**: docs-check（または同等手順）で必須メタ欠落が検知されない。
- **DoD-2**: 手動確認項目がある場合、実行コマンドと確認結果が作業ログ/PRに記録される。
- **DoD-3**: docs-check 未自動化観点は、判定理由（pass/fail）を再実行可能な粒度で記録する。

### 6) 非目標

- 本ADRで新しい機能要件・実装要件を追加しない。
- 本ADRで全既存文書の章構成統一を強制しない。
- 本ADRで CI 必須化範囲（fail条件）を最終確定しない。

## Consequences

- 初読時の理解コストが下がり、文書更新時の差分レビュー観点（Goal / Non-goal / Outcome）が明確になる。
- 文書横断ドリフト（用語ゆれ・導線欠落）を早期に検知しやすくなる。
- docs-check 連携により、可読性規約の運用実効性が上がる。
- 一方で、執筆時に最小メタ確認が増えるため、短期的には文書作成コストがわずかに上がる。
- 適用を段階導入とするため、移行期は「適用済み文書」と「未適用文書」が混在する。

## Verify (docs-check 観点の自己検証)

- 判定: **Ready for approval / Not accepted yet**
- 検証観点:
  1. ADR必須見出しI/F（Context / Decision / Consequences / Traceability）を保持している。
  2. DOC-OPS-04 A-I/F で要求される固定語彙（Audience / Goal / Non-goal / Outcome / Upstream Reference / Downstream Apply / Verification）を Decision 配下で定義している。
  3. AC/DoD補完として、適用対象と非目標境界（AC-4）および手動確認ログ要件（DoD-2/DoD-3）を明示している。
  4. 編集対象は本ADR本文のみであり、統合ファイル（README/dashboard/issue-DOC-OPS-04）を更新していない。
- 未充足:
  - `Status: Proposed` のため、Deciders 承認待ち。

## Proceed (承認依頼)

- 承認依頼先: Project Maintainers
- 依頼内容:
  1. 本ADRを `Accepted` へ更新する可否の判断。
  2. Readability Baseline（RBL-1〜RBL-5）を DOC-OPS-04 文書整備タスクの最小判定軸として採用すること。
- 承認までの運用:
  - 本ADRの規約適用は「差分が発生した文書から段階適用」を維持し、一括改修は実施しない。
  - docs-check 未自動化観点は、作業ログ/PRへ実行コマンドと判定理由を記録する。

## Traceability

- Related (Upstream): `00_Prompt/domain.md`
- Related (Upstream): `00_Prompt/agent_handover.md`
- Related (Upstream): `01_Plans/adr/ADR-0000-adr-governance.md`
- Related (Upstream): `01_Plans/adr/ADR-0018-coding-standards-and-smell-remediation.md`
- Related (Upstream): `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Related (Upstream): `01_Plans/adr/ADR-0022-doc-ops-04-documentation-information-interface.md`
- Related (Source): `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- Related (Downstream): `02_Architecture/architecture.md`
- Related (Downstream): `04_Documentation/security.md`
- Related (Downstream): `04_Documentation/operations.md`
