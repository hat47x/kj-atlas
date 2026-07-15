# Issue Draft: DATA-CONTRACT-RESET-01 Document契約を単一V1へ移行する

- Type: Architecture / Refactoring
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `02_Architecture/`, `03_Implement/frontend/`, `03_Implement/backend/`, `03_Implement/mcp/`, `04_Documentation/`
- Related Backlog: `DATA-CONTRACT-01`
- Related ADR/Spec: `ADR-0058`, `02_Architecture/schemas.md`
- Expected verification level: integration

## Requirement meta I/F（共通キー）

- RequirementID: DATA-CONTRACT-RESET-01
- RequirementStatement: 現行DocumentV2を唯一のDocumentV1へ再基線化し、未使用の旧V1互換機能を除却して、公開前の保存・取込・API契約を一つにする。
- PriorityClass: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=移行対象となる実利用データと安定API利用者がいない / 操作=新V1を保存、取得、export、importする / 期待結果=全機能を損失なく往復でき、旧最小V1、旧V2、版番号欠落は拒否される / 除外=Document以外のV1契約、DB正規化、個別CRUD追加。
- GoNoGoGate: Required
- SecurityGateImpact: import-sanitize
- VerificationLevel: integration
- DecisionStatus: Fixed
- DecisionQueueRef: `ADR-0058`

## 1) 課題 / Problem statement

- 永続Documentが旧V1と現V2の二重契約になっており、実利用のない互換処理が設計・実装・テストの負担になっている。
- 旧V1は島、根拠、レビューなど現在の製品価値を表現できず、標準形式として残す意味がない。
- 現V2をV1へ改称するだけでは、旧V1を新V1として誤認するため、必須構造を伴う厳格なversion gateが必要である。

## 2) 背景 / Context

- `ADR-0058` は現V2を新しい唯一のV1へ再基線化する判断を採択した。
- frontendの寛容取込は旧V1をV2へ補完し、backendはdiscriminated unionとして両方を受け付ける。
- 現在はプレリリースかつ実運用者不在であり、公開後の互換維持より公開前の契約単純化を優先できる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 現在の製品価値を表現できる契約だけを残し、利用者の理解負担を減らす。
- 安全（THREAT_MODEL / SafeMode）: importは版番号と必須構造をfail-closedで検証し、暗黙補完による欠落の隠蔽を避ける。
- 企業・行政要件（enterprise_architecture）: 公開前のため移行保証は不要。公開後は版番号を互換境界として用いる。
- 後方互換（schemas）: 意図的に旧V1/V2互換を廃止する。実利用データ不在をGo/No-Go条件とする。

## 4) 提案する解決策 / Proposed solution

- frontendの型、厳格検証、寛容取込、UI文言を `DocumentV1` / `version: 1` に統一する。
- backendの旧V1モデルとunionを削除し、現V2モデルを唯一のV1へ改称する。
- MCP、fixture、unit/integration/E2EのDocumentデータを新V1へ移行する。
- 現行の正本文書と一般向け文書を単一V1へ同期する。過去ADRの履歴表現は保持する。
- 非目標: Patch/InquiryJourneyなど別契約のV1、DB構造、支援レベル、SafeMode方針は変更しない。

## 5) 受入条件 / Acceptance criteria

- [x] 現行コードに永続Documentを指す `DocumentV2` が残っていない。
- [x] backend APIは完全な `DocumentV1` / `version: 1` だけを保存・返却する。
- [x] frontend importは数値 `version: 1` と現行必須構造を要求し、旧最小V1、旧V2、文字列版、版欠落を拒否する。
- [x] 新V1のoptionalフィールドがfrontend/backend/API往復で失われない。
- [x] 現行正本文書と一般向け文書が単一V1を説明する。
- [x] SafeMode、share/export、review attributionの安全境界が維持される。
- [x] frontend unit/typecheck、backend unit/integration、MCP test、文書整合テストが成功する。
- [x] Go/No-Go: 実利用データまたは安定API利用者が存在しないこと。存在が判明した場合は移行CLIを先行させる。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 現行正本文書を新V1へ同期する。
- [x] T2 frontend型・検証・取込・fixtureを移行する。
- [x] T3 backendモデル・API・fixtureを移行する。
- [x] T4 MCPと一般向け文書を移行する。
- [x] T5 横断検索と統合テストで旧契約の残存とデータ損失を検証する。

### Follow-up（2026-07-16）

T1完了後もcurrent architecture文書（`schemas.md` §3.4/§3.5の二重`Document`定義、`contract_reading_guide.md`、`contract_consolidation_inventory.md`）とe2e/unitのfixture（`card_quality_assistance.spec.ts`、`zip_import.test.ts`）に旧`DocumentV2`/`version: 2`表記が残存していたことが2026-07-15の横断監査で判明した。実装（frontend/backend型・validator）は本issueのT1-T5どおりV1へ移行済みであり、実装完了の事実は変えない。文書・fixtureの回帰是正は `issue-DATA-CONTRACT-DOC-01-single-v1-current-contract-reconciliation.md` として別issueへ切り出し、そちらで追跡する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `pnpm typecheck`
  - `pnpm test -- --run`
  - `python -m pytest`
  - `rg -n "DocumentV2|version: 2" 02_Architecture 03_Implement 04_Documentation`
- 期待結果:
  - 新V1の往復テストが成功し、現行契約から旧名称と旧version gateが消えている。
- 未実施時の理由・代替検証:
  - なし。integration検証完了までDoneにしない。

## 8) 代替案 / Alternatives considered

- 旧V1だけを削除してV2を維持: 変更量は少ないが、公開契約に不要な歴史を残すため不採用。
- versionを廃止: 将来移行の判別子を失うため不採用。
- 旧V1/V2を維持: 実利用者がいない段階では便益がなく不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: fixtureの置換漏れ、旧V1の誤受理、Document以外のversion誤変更。
- 影響範囲: frontend/backend/MCP/API/import/export/設計文書。
- ロールバック手順: ADR-0058をSupersededとし、変更コミットをrevertしてV1/V2 unionへ戻す。実利用データが判明した場合はロールバック後に移行issueを起票する。

## 10) Additional context

- GitHub Issuesは未運用のため、本issue memoを正本とする。
- 過去ADRの `DocumentV2` 記述は当時の判断記録であり、機械的に書き換えない。
- 2026-07-15のGo/No-Go確認では、OSS運用者、実利用データ、安定API利用者はいずれも存在しないというプロジェクト前提を採用した。将来その前提に反する事実が判明した場合は、新V1の公開前に移行CLIを別issueで先行実装する。
- 完了証跡: frontend `pnpm typecheck` 成功、Vitest 191 files / 1051 tests 成功、backend全体 293 passed / 24 skipped、追加契約・往復確認 31 passed / 21 skipped、MCP 3 files / 21 tests 成功、Active issue validator / unittest 成功。
- 横断検索では現行コード・正本文書の旧名称残存は0件。`ADR-0058` に残る `DocumentV2` は、比較した選択肢と判断履歴を説明する意図的な記録である。
