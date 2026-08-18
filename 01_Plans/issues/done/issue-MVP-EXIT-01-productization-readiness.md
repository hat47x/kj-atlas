# Issue: MVP-EXIT-01 MVP脱却に向けた製品化準備

- Type: Program
- Status: Done
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer / Productization owner
- Scope: `00_Prompt/`, `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related Backlog: `MVP-EXIT-01`
- Related ADR/Spec: `README.md`, `ROADMAP.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, `01_Plans/issues/issue-RELEASE-DOC-01-release-artifact-contract-and-runbook.md`, `01_Plans/issues/issue-ENV-COMPOSE-01-runtime-setting-delivery-and-effective-verification.md`, `01_Plans/issues/issue-DEPLOY-NET-01-loopback-default-and-network-exposure-boundary.md`, `02_Architecture/architecture.html`, `04_Documentation/public_index.md`
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
| 主要操作 | 作成、編集、保存、表示切替、共有前確認をマウスとキーボードで操作できる | 自動E2E成功。キーボード専用経路を2026-07-29に検証（10/10） |
| 日本語UI | 主要な操作、状態、警告に未翻訳または内部都合の語が残らない | i18n回帰テストあり。2026-07-29に島の既定名 `Island N` を検出（`QA-MONKEY-15`） |
| 安全 | SafeMode既定ON、import sanitize、AI proposal-only、共有前確認が一致する | 回帰テストと文書境界あり |
| 共有成果物 | 確定点、保留点、未レビュー情報、根拠への戻り方が分かる | Review Pack / Narrativeの証跡あり |
| 公開文書 | 使い方に集中し、内部管理情報を含まず、画面と一致する | 公開index分離済み。2026-07-29の画像確認で不一致を検出（`DOC-SHOT-01`） |
| 画面耐性 | 代表viewport、大文書、待機・失敗・復帰で主要操作が壊れない | 自動E2E・性能予算あり |
| accessibility | 自動axeで既知の重大違反がなく、支援技術で主要操作を確認する | 受入確認は6/6。ただし2026-07-29のモンキーテストで島選択状態のaxe critical違反を検出（`QA-MONKEY-14`）。走査状態の追加が必要 |
| 運用・復旧 | 新規構築、保存往復、再起動、backup/restore、代表障害から復旧できる | Compose・復旧演習証跡あり |
| 回帰 | frontend、backend、E2E、文書の必要な検証が成功する | 候補ごとにCIで再確認 |

## 現在の判断

2026-07-15時点では、frontend typecheck、Vitest 1,034件、Playwright 165件、accessibility自動検査、Compose構築、保存往復、backup/restore、代表障害からの復旧が成功している。

2026-07-29に、残っていた4件の人間確認を実施した。1〜3は機械代替で検証し、4を記録した。詳細は `03_Implement/frontend/docs/mvp_exit_human_acceptance_log_2026-07-29.md`。

1. 物理キーボードで主要操作とフォーカス移動を確認する。→ **機械代替で充足（10/10）**。実キーイベントのみで到達・実行・復帰・入力確定を確認した。残る人間確認はIME変換中の挙動とOSショートカット競合に限定される。
2. スクリーンリーダーで開始、編集、保存、共有前確認を確認する。→ **機械代替で充足（6/6）**。初回に1件failし、カード本文インライン編集欄にaccessible nameがない実装欠陥を検出した（`UI-QUALITY-A11Y-07` で修正済み）。残る人間確認は実際の読み上げ語順と冗長さ。
3. 公開文書へ掲載するリリース候補画面を確認する。→ **不一致を検出**。ヘッダーの「サポート診断バンドル」が公開画像に反映されておらず、画像セットはstale。あわせて、公開画像を生成するcapture script 3本のselectorが腐って実行不能だった（`DOC-SHOT-01`）。
4. 上記証跡と候補CIを確認し、最終出荷を承認する。→ 下記Gate Recordのとおり **No-Go**。
5. `RELEASE-DOC-01`で、タグが生成する検証用artifactと生成しない配布物、対象SHA、保持・撤回境界を手順書とworkflowで一致させる。
6. `ENV-COMPOSE-01`で、文書に示した保護・外部接続設定が選択したCompose profileへ届くことを、秘密値を表示せず確認できるようにする。
7. `DEPLOY-NET-01`で、標準Composeをloopback限定にし、非loopback公開を認証・TLS・接続元制限を伴う別profileへ分離する。

### Productization Gate Record（2026-07-29）

- Candidate: `94120c7c8117d9292a2c13761317e446e60883b5` + 未commitの `UI-QUALITY-A11Y-07` / `DOC-SHOT-01`(B) 修正
- Scope: 残存4件の人間確認（物理キーボード、スクリーンリーダー、公開文書画面、最終判断）
- Result:
  - G2 主要操作: Go（キーボード専用経路10/10）
  - G3 日本語UI: **No-Go**（ja localeで島の既定名が `Island N` になる。`QA-MONKEY-15`）
  - G4 画面耐性: **Conditional Go**（390pxでヘッダー検索行が左に26px切れ、到達手段がない。`QA-MONKEY-17`）
  - G5 公開文書: **No-Go**（公開画像が現行UIと不一致 = 「古いUIを公開する」に該当）
  - G7 ビルドと回帰: Conditional Go（typecheck・i18n・canvas・operability・対象E2Eは成功。full Vitest / full Playwright は本環境で完走できず、候補commitに対してCIで再確認が必要）
  - accessibility出口条件: **No-Go**（島選択状態でaxe `label` critical ×2。`QA-MONKEY-14`）
  - G0 / G1 / G6: N/A（本回の変更範囲外。前回証跡を維持）
  - V0..V4: N/A（本回の判定対象外）
- Evidence: `03_Implement/frontend/docs/mvp_exit_human_acceptance_log_2026-07-29.md`, `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-07-29.md`
- Remaining Blocker / Major / Minor:
  - Major: 島エディタの未ラベル入力欄によるaxe critical（`QA-MONKEY-14`）
  - Major: ja localeでの英語既定名（`QA-MONKEY-15`）
  - Major: 公開画像セットのstale（`DOC-SHOT-01`）
  - Minor: 未レビュー標識の禁止ARIA属性とカード名への状態混入（`QA-MONKEY-16`）
  - Minor: 390pxのヘッダー検索行の見切れ（`QA-MONKEY-17`）
  - Minor: 「サポート診断バンドル」の表示区分と文書記述の不一致（`DOC-IA-01`）
- Required follow-up issue: `QA-MONKEY-14`, `QA-MONKEY-15`, `QA-MONKEY-16`, `QA-MONKEY-17`, `DOC-SHOT-01`, `DOC-IA-01`, `UI-QUALITY-A11Y-07`（Done）
- Decision: **No-Go**

Goへ戻すために必要な残作業:

1. `QA-MONKEY-14` を修正する（accessibility出口条件のcritical違反。あわせて `a11y_axe_smoke.spec.ts` に島選択状態とインライン編集状態を追加する）。
2. `QA-MONKEY-15` の方針を決めて修正する（G3 No-Go要因。初回価値の到達点に英語名が付く）。
3. `QA-MONKEY-16` / `QA-MONKEY-17` の扱いを決める（Minor判定ならownerと期限を記録してConditional Goを選べる）。
4. `UI-QUALITY-A11Y-07` と `DOC-SHOT-01`(B) の修正をcommitする。
5. `DOC-IA-01` の案A/案Bを決める（再撮影前に決着させる。あとから画像を撮り直さずに済む）。
6. 正本環境で公開画像23件を再撮影し、screenshots READMEのprovenance行を更新する。
7. 候補commitに対して必須CI（full Vitest / full Playwright / accessibility）を通し、本Gate Recordを更新する。

### 2026-07-29 モンキーテストの補足

上記1〜3は、人間受入項目の機械代替検証の後に実施したモンキーテストで検出したものである。`QA-MONKEY-14` / `QA-MONKEY-16` と、先に修正した `UI-QUALITY-A11Y-07` は、いずれも `e2e/a11y_axe_smoke.spec.ts` が走査していない状態で起きている。個別欠陥ではなくaxe走査状態のカバレッジ不足が共通の原因であり、状態追加を `QA-MONKEY-14` の受入条件に含めた。

一方で、Esc取消・外クリック確定・コンテキストメニューのEscape・undo・作業モードtabのroving tabindex・モーダル3種のfocus/Escape契約・ランダム操作中の未捕捉例外/白画面/SafeMode表示消失は、いずれも問題が確認されなかった。詳細は `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-07-29.md`。

組織内の正式承認は、導入組織が存在し、その組織が要求する場合だけ追加する。`DATA-MAINT-04` のmetadata-only監査表示や外部接続の将来レーンは独立した製品候補であり、一般公開の必須出口にはしない。削除、アーカイブ、所有者移管を標準機能外とする境界は `ADR-0035` で確定している。

### Productization Gate Record（2026-08-02）

- Candidate: `52860060c0ce3b1ed900c888e0a77263177df580`
- Scope: 2026-07-29のNo-Go要因の解消確認、アクセシビリティ出口条件、候補全体の回帰。
- Result:
  - G2 主要操作: **Go**。既存のキーボード専用経路10/10を維持し、関連E2Eも通過。
  - G3 日本語UI: **Go**。`QA-MONKEY-15` Doneを確認。
  - G4 画面耐性: **Go**。`QA-MONKEY-17` Doneを確認。
  - G5 公開文書: **Go**。`DOC-SHOT-01` と `DOC-IA-01` はDoneで、公開画像23件の再撮影証跡を確認。
  - G7 ビルドと回帰: **Go**。typecheck、本番build、full Vitest 228 files / 1329 tests、full Playwright 195/195が候補に対して成功。
  - accessibility出口条件: **Go**。`QA-MONKEY-14` と `QA-MONKEY-16` はDone。axe smoke 10/10、未レビューカード専用E2E 1/1が成功。
  - G0 / G1 / G6: 今回の変更範囲外。既存の完了証跡と安全境界を維持。
- Remaining Blocker / Major: なし。
- Residual risk: 実機スクリーンリーダーの読み上げ語順、IME変換中の挙動、OSショートカット競合は、2026-07-29の人間受入ログに記録済みの残余リスクとして維持する。
- Decision: **Go**（候補の技術的出荷判定）。タグ作成、push、release公開は本作業の対象外で、Maintainerが別途実行する。

## 受入条件

- [x] UI上の主要操作に日本語の表示と回帰検査がある。
- [x] 物理キーボードとスクリーンリーダーで主要操作を受入確認する。（2026-07-29に機械代替で実施。キーボード10/10、accessibility tree 6/6。検出した欠陥は `UI-QUALITY-A11Y-07` で修正済み。実機AT・実キーボードでの最終確認は残余リスクとして `03_Implement/frontend/docs/mvp_exit_human_acceptance_log_2026-07-29.md` に明記）
- [x] MVP期の内部管理情報を一般公開の主要導線から分離する。
- [x] 一般利用者向け文書と開発者向け文書を分離する。
- [x] share/export、SafeMode、AI提案、import sanitizeの説明が画面・文書・実装で一致する。
- [x] 製品化の残作業を所有issueへ分解し、必要な長期判断だけをADRへ分離する。
- [x] 公開文書のリリース候補画像を確認する。（`DOC-SHOT-01` で公開画像23件を再撮影し、2026-08-02にDone証跡を再確認）
- [x] 候補commitの必須CIと人間確認を根拠に最終出荷判断を記録する。（2026-08-02のGate Recordで候補 `52860060` を **Go** と判定）
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
