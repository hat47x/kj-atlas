# Issue: MVP-EXIT-01 MVP脱却に向けた製品化準備

- Type: Program
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer / Productization owner
- Scope: `00_Prompt/`, `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related Backlog: `MVP-EXIT-01`
- Related ADR/Spec: `README.md`, `ROADMAP.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, `01_Plans/issues/issue-RELEASE-DOC-01-release-artifact-contract-and-runbook.md`, `01_Plans/issues/issue-ENV-COMPOSE-01-runtime-setting-delivery-and-effective-verification.md`, `01_Plans/issues/issue-DEPLOY-NET-01-loopback-default-and-network-exposure-boundary.md`, `02_Architecture/architecture.md`, `04_Documentation/public_index.md`
- Expected verification level: `integration`

## 目的

kj-atlasを、機能デモとして動くMVPから、一般利用者が継続利用でき、安全に共有でき、公開文書から導入できる製品へ移行する。本Issueは個別実装を抱える場所ではなく、製品化の出口条件と未完了領域を示す親issueである。

## 方針

- 実装作業は `UX-*`、`DOC-*`、`QA-*`、`SEC-*`、`PRODUCT-VALUE-*` 等の所有issueで進める。
- 品質判定にはDoneの `PRODUCT-QA-01` に定義したG0〜G7と価値ゲートを使う。
- 候補ごとの検証結果はCI、PR、releaseへ記録し、本Issueへ反復転記しない。
- 長期的・横断的・破壊的・安全境界の変更だけをADRへ送る。
- 組織向け機能は、現時点の一般公開に必要なものと、導入組織が要求した場合に追加するものを区別する。

非目標:

- 認証、SSO、外部PDP、共同編集などの将来機能を一括実装すること。
- すべてのDraft issueを製品化前に完了すること。
- 自動テストを人間による最終出荷判断の代替にすること。

## 出口条件

| 領域 | Done条件 | 現在 |
| --- | --- | --- |
| 初回価値 | 開始から最初の意味あるカード配置まで迷わず到達できる | 自動E2Eと日本語UI証跡あり |
| 主要操作 | 作成、編集、保存、表示切替、共有前確認をマウスとキーボードで操作できる | 自動E2E成功。物理キーボード受入は未完了 |
| 日本語UI | 主要な操作、状態、警告に未翻訳または内部都合の語が残らない | i18n回帰テストあり。最終目視は出荷候補で実施 |
| 安全 | SafeMode既定ON、import sanitize、AI proposal-only、共有前確認が一致する | 回帰テストと文書境界あり |
| 共有成果物 | 確定点、保留点、未レビュー情報、根拠への戻り方が分かる | Review Pack / Narrativeの証跡あり |
| 公開文書 | 使い方に集中し、内部管理情報を含まず、画面と一致する | 公開index分離済み。最終画像確認は未完了 |
| 画面耐性 | 代表viewport、大文書、待機・失敗・復帰で主要操作が壊れない | 自動E2E・性能予算あり |
| accessibility | 自動axeで既知の重大違反がなく、支援技術で主要操作を確認する | 自動検査成功。スクリーンリーダー受入は未完了 |
| 運用・復旧 | 新規構築、保存往復、再起動、backup/restore、代表障害から復旧できる | Compose・復旧演習証跡あり |
| 回帰 | frontend、backend、E2E、文書の必要な検証が成功する | 候補ごとにCIで再確認 |

## 現在の判断

2026-07-15時点では、frontend typecheck、Vitest 1,034件、Playwright 165件、accessibility自動検査、Compose構築、保存往復、backup/restore、代表障害からの復旧が成功している。

**製品機能と自動検証はConditional Go、正式な出荷はNo-Go** とする。残る項目は、4件の人間確認、リリース成果物契約、Compose実効設定契約、標準Composeのネットワーク公開境界の整合である。

1. 物理キーボードで主要操作とフォーカス移動を確認する。
2. スクリーンリーダーで開始、編集、保存、共有前確認を確認する。
3. 公開文書へ掲載するリリース候補画面を確認する。
4. 上記証跡と候補CIを確認し、最終出荷を承認する。
5. `RELEASE-DOC-01`で、タグが生成する検証用artifactと生成しない配布物、対象SHA、保持・撤回境界を手順書とworkflowで一致させる。
6. `ENV-COMPOSE-01`で、文書に示した保護・外部接続設定が選択したCompose profileへ届くことを、秘密値を表示せず確認できるようにする。
7. `DEPLOY-NET-01`で、標準Composeをloopback限定にし、非loopback公開を認証・TLS・接続元制限を伴う別profileへ分離する。

組織内の正式承認は、導入組織が存在し、その組織が要求する場合だけ追加する。`DATA-MAINT-04` のmetadata-only監査表示や外部接続の将来レーンは独立した製品候補であり、一般公開の必須出口にはしない。削除、アーカイブ、所有者移管を標準機能外とする境界は `ADR-0035` で確定している。

## 受入条件

- [x] UI上の主要操作に日本語の表示と回帰検査がある。
- [ ] 物理キーボードとスクリーンリーダーで主要操作を受入確認する。
- [x] MVP期の内部管理情報を一般公開の主要導線から分離する。
- [x] 一般利用者向け文書と開発者向け文書を分離する。
- [x] share/export、SafeMode、AI提案、import sanitizeの説明が画面・文書・実装で一致する。
- [x] 製品化の残作業を所有issueへ分解し、必要な長期判断だけをADRへ分離する。
- [ ] 公開文書のリリース候補画像を確認する。
- [ ] 候補commitの必須CIと人間確認を根拠に最終出荷判断を記録する。
- [x] タグ・候補commit・品質証跡・実際の成果物が一意に対応し、検証用artifactを正式配布物と誤認しない。（`RELEASE-DOC-01` Phase AがDone済みのため充足を確認。2026-07-20更新）
- [x] Compose向けに案内する安全設定が実際の`api`へ配送され、未対応設定を有効と誤認しない。（`ENV-COMPOSE-01` Done済みのため充足を確認。LLM stub・外部接続test doubleのDocker integration確認はscope-excludedのfollow-upとして引き続き対象外。2026-07-20更新）
- [x] fresh cloneの標準Composeが認証なしでLANへ暗黙公開されず、非loopback公開の安全要件が文書化される。（`DEPLOY-NET-01` Done済みのため充足を確認。非loopback公開自体の別profile化はPhase Bとして引き続き対象外。2026-07-20更新）

## 実施済み

- [x] 画面上の未翻訳ラベル、仮実装ラベル、MVP期の主要な表示を棚卸しした。
- [x] 代表的なマウス・キーボード操作をE2E化し、不具合を個別issueで修正した。
- [x] 公開文書から内部管理情報を除外し、開発者向けE2E文書を03へ移した。
- [x] share/export、SafeMode、import sanitizeを画面、文書、テストで照合した。
- [x] 狭い画面、大文書、代表的な失敗と復帰を検証した。
- [x] release readinessの品質ゲートを `PRODUCT-QA-01` に定義した。
- [x] Compose新規構築、保存、再起動、backup/restore、障害復旧を演習した。

## 検証入口

- 品質ゲート: `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- E2E実務手順: `03_Implement/frontend/docs/e2e_testing.md`
- 一般利用者の受入確認: `04_Documentation/acceptance_check.md`
- 公開文書入口: `04_Documentation/public_index.md`
- CI: `.github/workflows/ci.yml`

候補ごとに実行するコマンドは変更範囲と品質ゲートから選ぶ。未実施項目は、理由、代替証跡、再開条件を記録し、成功扱いしない。

## 完了条件

残る4つの人間確認が候補commitに対して完了し、`RELEASE-DOC-01`のPhase A、`ENV-COMPOSE-01`、`DEPLOY-NET-01`が完了し、重大なBlockerまたは未解消Majorがなく、最終出荷判断が記録された時点でDoneとする。新しい製品欠陥が見つかった場合は、本Issueへ詳細ログを積まず、再現条件と受入条件を持つ個別issueへ戻す。

詳細な過去Program Gate DecisionはGit履歴で参照する。新ADRは不要であり、本整理は `ADR-0039` の運用軽量化を実行するもので、安全・互換・出荷権限を変更しない。
