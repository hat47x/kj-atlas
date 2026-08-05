# Issue Draft: DOC-PUBLIC-BOUNDARY-01 開発者向け文書の公開文書境界見直し

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `04_Documentation/public_index.md`, Gist公開候補の `04_Documentation/*.md`, `04_Documentation/README.md`, `README.md`（必要最小限の導線整合）, `01_Plans/issues/issue-DOC-PUBLIC-BOUNDARY-01-developer-doc-relocation.md`
- Related Backlog: `DOC-PUBLIC-BOUNDARY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0022-doc-ops-04-documentation-information-interface.md`, `01_Plans/documentation_quality.md`, `04_Documentation/README.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Expected verification level: `docs-check`

## Draft→Open 2026-06-20
DOC-PUBLIC-BOUNDARY-01 Open化。DecisionStatus=Fixed、scope定義済み。ADR-0039により重量RACI不要。docs-check levelで着手可能。

## Done 2026-06-20
文書公開境界確定。DoD 5/5達成:
- 利用者入口(public_index.md) / 管理者入口(04_Documentation/README.md) / 開発者入口(README.md) 3系統固定
- 相互リンク規約固定（public→利用者限定、README(04)→管理、README(root)→二系統分離）
- e2e_testing.md → 03_Implement/frontend/docs/ 移管済み
- 公開対象文書から内部管理語除去確認済み（rg scan: 0 matches）
- codex_skill_operations.md / e2e_verification_log 物理移管は後続タスク（明示的にdeferred）

## Requirement meta I/F（共通キー）

- RequirementID: DOC-PUBLIC-BOUNDARY-01
- RequirementStatement: `04_Documentation/` の一般公開向け本文と、開発者・AIエージェント・内部検証向け文書の管理場所を分離し、Gist公開本文に管理情報が混ざらない状態を維持する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation/` を公開候補として読む / 操作=公開対象一覧と各文書の対象読者を確認 / 期待結果=一般利用者向け本文、開発者向け手順、内部管理文書が別管理になっている / 除外=履歴上の古いissue本文の全文置換。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure

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

### Context / Decision / Consequences（情報公開境界）

- Context:
  - 利用者向け公開入口（Gist/公開配布）と、保守者・開発者向け管理入口が同一導線上に見えると、公開本文に内部管理情報が混入しやすい。
  - `04_Documentation/public_index.md` は利用者向け入口、`04_Documentation/README.md` は保守者向け入口という役割が既に定義されている。
- Decision:
  - 入口を3系統に固定する。
    1. 利用者入口: `04_Documentation/public_index.md`
    2. 管理者入口: `04_Documentation/README.md`
    3. 開発者入口: `README.md`（実装・貢献導線は `03_Implement/README.md` と `CONTRIBUTING.md`）
  - 相互リンク規約を固定する。
    - `public_index.md` は利用者向け文書のみを参照し、管理情報や開発運用文書へ直接誘導しない。
    - `04_Documentation/README.md` は `public_index.md` を公開入口として指し示しつつ、管理手順・除外方針を担当する。
    - ルート `README.md` は「利用者向け公開入口（public_index）」と「開発者向け入口（03_Implement/README, CONTRIBUTING）」を明示分離する。
- Consequences:
  - 公開配布時に「含めるべき文書」と「含めない管理情報」の判定が単純化される。
  - 利用者は手順探索に集中でき、開発者は管理・実装導線へ最短で到達できる。
  - 文書更新時は3入口のリンク整合確認が必須になる。

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

- [x] `04_Documentation/README.md` の公開対象一覧と実ファイル配置が一致する。
- [x] `public_index.md` から内部管理文書へ誘導していない。
- [x] 利用者入口・管理者入口・開発者入口の3系統が明文化されている。
- [x] 相互リンク規約（public→利用者限定、README(04)→管理、README(root)→二系統分離）が明文化されている。
- [ ] 開発者向けE2E正本が `03_Implement/frontend/docs/e2e_testing.md` に固定される。（本Issueでは導線明示まで）
- [ ] `codex_skill_operations.md` と検証ログテンプレートの移管先が決まり、リンク切れがない。（後続タスク）
- [x] Gist公開前検索で `AGENTS.md`、`01_Plans`、`ADR-`、内部管理ログが公開本文へ混ざらない方針が明文化されている。
- [ ] 歴史的なissue本文を除き、現行ADRと設計文書の `04_Documentation/e2e_testing.md` 参照が解消されている。（後続タスク）

## 6) 実装タスク分解 / Task breakdown

- [x] T1 `public_index.md` / `04_Documentation/README.md` / `README.md` の対象読者導線を確認する。
- [x] T2 情報公開境界における Context / Decision / Consequences をIssue本文へ明文化する。
- [x] T3 利用者入口・管理者入口・開発者入口の3系統と相互リンク規約を固定する。
- [x] T4 公開向け本文に管理情報を混入させない方針と確認観点を更新する。
- [x] T5 Gist公開候補文書から、内部issue/ADR/Gate/Stream/DOC-OPS などの管理語を除去する。

## 6.1 Definition of Done（DoD）

- [x] 公開入口（`public_index.md`）が利用者向け説明に限定されている。
- [x] 管理入口（`04_Documentation/README.md`）が公開境界管理の責務を持つことが明示されている。
- [x] 開発者入口（`README.md`）に利用者導線と開発者導線の分離が明記されている。
- [x] 3入口間のリンク到達性が `rg` により検証済み。
- [x] Gist公開候補の利用者向け文書に、内部管理語が混ざらないことを `rg` で確認済み。

## 6.2 Update 2026-05-21: Public-target boundary cleanup

### 実施内容

- `acceptance_check.md` から、開発者向けE2E、内部Gate Record、Program判定、ADR/issue参照を外し、画面操作と確認記録の説明へ寄せた。
- `operations.md`、`diagnostics.md`、`security.md`、`security_operational_guidelines.md` から、内部Stream、DOC-OPS、AUTH運用の進捗管理節を外し、利用者・運用担当者が読める復旧手順と判断支援に整理した。
- `configuration.md`、`operations.md`、`security.md`、`security_operational_guidelines.md` では、04以外の設計詳細を GitHub 上の設計文書リンクとして扱う方針に合わせた。
- 「外部に送る」「データを渡す」に近い表現を、外部サービスとの「共有」として伝わる文に置き換えた。ただし `環境変数` の説明における「アプリへ渡す設定値」は外部共有を意味しないため維持した。

### 検証結果

- Public-target forbidden term scan:
  - `rg -n "04_Documentation|AGENTS.md|01_Plans|ADR-|PUBLICATION_MANIFEST|内部管理|作業ログ|issue-|Issue|PRODUCT-|MVP|Stream [A-Z]|Draft Proposal|DOC-OPS|AUTH-OPS|Gate Record|Productization" <public target 04 docs>`
  - Result: no matches.
- External-sharing wording scan:
  - `rg -n "外部に送る|外部送信|送る|渡す|渡さない|投げる" <public target 04 docs>`
  - Result: only `configuration.md` の `環境変数` 定義における `渡す` が残る。外部サービス共有の説明ではないため許容。

### 残課題

- `codex_skill_operations.md` と `e2e_verification_log_2026-03-03.md` は引き続き公開Gist対象外として扱う。物理移管は後続タスク。
- Gist生成物そのものの連結後スキャンと公開更新は、公開作業時に改めて実施する。

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

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `public boundary`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-PUBLIC-BOUNDARY-01` の公開境界を再確認。
- Decision: 入口を public_index / 04 README / README に再固定し、公開・保守・開発者・内部計画の4分類を明記した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
