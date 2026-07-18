# Issue: DOC-EXTERNAL-WIKI-01 DeepWikiの生成文書と設計正本の意味境界を明確にする

- Type: Documentation / Architecture / Quality
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `README.md`, `AGENTS.md`, `02_Architecture/architecture.md`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/schemas.md`, `02_Architecture/runtime_parameter_registry.md`, `04_Documentation/public_index.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0039-lean-governance-for-small-oss.md`, `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DOC-EXTERNAL-WIKI-01
- RequirementStatement: DeepWiki等の自動生成文書を補助索引として利用できる一方、索引時点、正本ではないこと、DocumentV1・互換性・環境変数・実装構成の境界を誤解せず正本へ戻れるようにする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=利用者または開発者がDeepWikiからkj-atlasを理解する / 操作=概要、データモデル、設定、UI構成を読み、リポジトリの正本へ移動する / 期待結果=索引commitと非正本性を識別でき、DocumentV1をセッション全状態の正本と誤解せず、往復保証と環境変数名を正しく確認できる / 除外=DeepWiki生成ロジックの修正、生成ページの手作業による全文保守、DeepWikiを公開マニュアルの正本にすること
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure / import-sanitize
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

2026-07-18に`https://deepwiki.com/hat47x/kj-atlas`（索引commit `68d4b720`）を確認したところ、リポジトリの横断理解には有用だが、次の説明が現行設計・実装より強い、または誤っていた。

1. 「strict five-layer hierarchy」と説明するが、現行`AGENTS.md`は小規模OSS向けに必要文書だけを読む軽量運用へ削減済みである。
2. `DocumentV1`をKJセッションの空間・意味状態すべてのsingle source of truthと説明するが、view/perspective状態は`view.json`、反復探究は独立`InquiryJourneyV1`であり、DocumentV1は文書内容スナップショットの正本である。
3. 将来・外来データを含むround-trip preservationを包括保証するように読めるが、未知edge typeだけは保持し、未知`Card.meta`キーやclosed-world契約の未知キーは安全側で破棄または拒否する。保証はフィールド単位で異なる。
4. データフロー図に`CardPanel.tsx`、`IslandCritiquePanel.tsx`という実在しないコンポーネント名が表示される。
5. 設定ページのprofile要約で`DATABASE_URL`、`LLM_PROVIDER`等の接頭辞が脱落する。正本は全公開環境変数を例外なく`KJ_ATLAS_*`とする。
6. `L2.5`の例として`EvidenceLinks`を挙げるが、現行CRUD表では`EvidenceLink`は`L2`である。

索引が古いことだけでは説明できない推論もある。一方、生成ページの文面をリポジトリから直接修正することはできないため、正本側に短く明確な境界を置き、再索引後に改善有無を確認する必要がある。

## 2) 提案する解決策 / Proposed solution

- READMEにDeepWikiを「特定commitから生成された補助索引」として案内し、設計判断・設定値・利用手順の正本ではないことを明記する。
- `architecture.md`と`data_model_operations_overview.md`に、DocumentV1、view状態、InquiryJourneyの正本範囲を一つの表で示す。
- `schemas.md`に、未知値・未知キーの保持、正規化、破棄、拒否をフィールド/契約別にまとめた互換性表を置く。
- 環境変数の例やprofile表は省略名を使わず、常に完全な`KJ_ATLAS_*`名で記載する現行規則を維持する。
- 実装コンポーネント名を設計概念図へ載せる場合は実在パスを使い、概念上の仮名には「概念」と明記する。
- DeepWiki再索引後、同じ6観点を確認する。生成誤りが残っても正本への導線が明確なら、生成ページの完全一致を完了条件にしない。

## 3) 受入条件 / Acceptance criteria

- [ ] AC-1: READMEからDeepWikiへ移動でき、索引commit依存・非正本・正本入口が同じ文脈で分かる。
- [ ] AC-2: DocumentV1、view状態、InquiryJourneyの正本範囲が重複なく説明される。
- [ ] AC-3: 未知edge type、未知`Card.meta`、Document未知top-level key、CE closed-world keyの処理差が表で確認できる。
- [ ] AC-4: 現行文書の公開環境変数例に接頭辞なしキーが残らない。
- [ ] AC-5: 正本の実装構成図に実在しないコンポーネント名を実装名として載せない。
- [ ] AC-6: 再索引したDeepWikiを同じ観点で確認し、残る生成誤りと正本側で解消した誤読余地を記録する。
- [ ] AC-7: `docs_check.py`とリンク検証が通る。

## 4) タスク / Tasks

- [x] T1 DeepWikiのOverview、Data Model、Configuration Referenceを索引commitとともに確認する。
- [x] T2 生成説明を現行`AGENTS.md`、データモデル正本、validator、環境変数registryと照合する。
- [ ] T3 READMEへ補助索引としての案内と正本への戻り先を追加する。
- [ ] T4 データ正本範囲と未知値処理表を設計文書へ追加する。
- [ ] T5 現行文書の接頭辞・実装名を機械検査する。
- [ ] T6 DeepWiki再索引後の差分を確認する。

## 5) 検証計画 / Validation plan

- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans.issues.tests.test_validate_active_issue_memos`
- `python 01_Plans/docs_check.py`
- `rg`で接頭辞なし設定キーと、実在しないコンポーネント名を確認する。
- DeepWikiの索引commitを記録し、Overview / Data Model / Configuration Referenceを再確認する。

## 6) 依存関係 / Dependencies

- DeepWikiの再索引可能時期
- `ADR-0058`
- `runtime_parameter_registry.md`

## 7) ADR判定

新規ADRは不要。設計正本、互換性契約、環境変数命名、軽量運用の決定自体は既存ADRで確定している。本issueは自動生成文書によって顕在化した説明境界と導線を修正する。
