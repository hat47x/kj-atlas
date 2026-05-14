# Issue Draft: DOC-PUBLIC-BOUNDARY-01 開発者向け文書の公開文書境界見直し

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `04_Documentation/`, `03_Implement/frontend/docs/`, `00_Prompt/`, `01_Plans/documentation_quality.md`
- Related Backlog: `DOC-PUBLIC-BOUNDARY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0022-doc-ops-04-documentation-information-interface.md`, `01_Plans/documentation_quality.md`, `04_Documentation/README.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DOC-PUBLIC-BOUNDARY-01
- RequirementStatement: `04_Documentation/` の一般公開向け本文と、開発者・AIエージェント・内部検証向け文書の管理場所を分離し、Gist公開本文に管理情報が混ざらない状態を維持する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation/` を公開候補として読む / 操作=公開対象一覧と各文書の対象読者を確認 / 期待結果=一般利用者向け本文、開発者向け手順、内部管理文書が別管理になっている / 除外=履歴上の古いissue本文の全文置換。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- E2Eテスト方針は開発者向けであり、一般利用者向けの公開文書と同じ本文に置くと、公開読者に不要な前提知識を要求する。
- 今回 `04_Documentation/e2e_testing.md` は `03_Implement/frontend/docs/e2e_testing.md` へ移管し、`04_Documentation/acceptance_check.md` を公開向け確認手順として追加した。
- ただし `04_Documentation/e2e_verification_log_2026-03-03.md` や `04_Documentation/codex_skill_operations.md` など、公開利用者向けではない文書がまだ残っている。

## 2) 背景 / Context

- `04_Documentation/README.md` は公開Gistに含めない文書を明示している。
- `codex_skill_operations.md` はAIエージェント運用手順、`e2e_verification_log_2026-03-03.md` は検証記録テンプレートであり、一般利用者の使い方説明ではない。
- 参照元が多いため、配置変更は一括移動よりも対象文書ごとの移管先、リンク、公開対象一覧を確認してから行う必要がある。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 初読者が使い方に集中できる公開文書体系は、導入摩擦を下げる。
- 安全（THREAT_MODEL / SafeMode）: 内部ログや管理手順の公開混入を避ける。
- 企業・行政要件（enterprise_architecture）: 公開範囲と内部管理範囲を分けることで監査しやすくする。
- 後方互換（schemas）: 文書配置のみでデータ契約には影響しない。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - `04_Documentation/e2e_verification_log_2026-03-03.md`
  - `04_Documentation/codex_skill_operations.md`
  - 関連する `AGENTS.md`、`01_Plans/documentation_quality.md`、公開インデックス
- 最小単位:
  - 開発者向けは `03_Implement/frontend/docs/` または該当実装領域へ移す。
  - AIエージェント向けは `00_Prompt/` または `01_Plans/` へ移す。
  - `04_Documentation/` には一般利用者向け本文と保守者向け README のみを残す。
- 非目標:
  - 歴史的なissue本文や完了済みログの全置換。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/README.md` の公開対象一覧と実ファイル配置が一致する。
- [ ] `public_index.md` から内部管理文書へ誘導していない。
- [ ] 開発者向けE2E正本が `03_Implement/frontend/docs/e2e_testing.md` に固定される。
- [ ] `codex_skill_operations.md` と検証ログテンプレートの移管先が決まり、リンク切れがない。
- [ ] Gist公開前検索で `AGENTS.md`、`01_Plans`、`ADR-`、内部管理ログが公開本文へ混ざらない。
- [ ] 歴史的なissue本文を除き、現行ADRと設計文書の `04_Documentation/e2e_testing.md` 参照が解消されている。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 `04_Documentation/` の全mdを対象読者で分類する。
- [ ] T2 開発者向け、AIエージェント向け、内部検証向けの移管先を決める。
- [ ] T3 移管対象ごとにリンク、README、関連正本を更新する。
- [ ] T4 公開用Gist生成前の禁止語検索を更新する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "04_Documentation/e2e_testing.md|\\(e2e_testing.md\\)" AGENTS.md CONTRIBUTING.md 01_Plans 02_Architecture 04_Documentation`
  - `rg -n "04_Documentation/e2e_testing.md" 01_Plans/adr 02_Architecture AGENTS.md CONTRIBUTING.md`
  - `rg -n "AGENTS.md|01_Plans|ADR-|内部管理|作業ログ" 04_Documentation/public_index.md 04_Documentation/*.md`
  - `git diff --check -- 04_Documentation 03_Implement/frontend/docs 00_Prompt 01_Plans`
- 期待結果:
  - 公開本文に内部管理の導線が混入していない。
  - 開発者向け文書の正本リンクがGitHub上の配置へ向いている。

## 8) 代替案 / Alternatives considered

- 代替案A: `04_Documentation/README.md` で除外だけ明記し、物理配置は維持する。公開時の事故防止としては弱いため、移管先を決める。
- 代替案B: すべてを即時移動する。参照更新範囲が大きく、履歴文書の破壊的変更になりやすいため段階移行する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 移管後に古いリンクが残り、開発者が正本へ到達できなくなる。
- 影響範囲: 文書リンク、公開Gist生成手順、AIエージェント作業導線。
- ロールバック手順: 移管コミットを戻し、`04_Documentation/README.md` の除外管理へ一時的に戻す。

## 10) Additional context

- ADR化が必要になる条件: `04_Documentation/` の役割そのもの、公開Gist生成方式、またはAIエージェント向け文書の正本階層を再定義する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
