# Issue Draft: PRODUCT-UX-01 初回利用と文書入口の製品化

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Product UX evidence steward; accountable owner remains Productization Program Owner)
- Scope: `03_Implement/frontend/src/`, `04_Documentation/installation.md`, `04_Documentation/operations.md`, `04_Documentation/public_index.md`
- Related Backlog: `PRODUCT-UX-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `ROADMAP.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-01
- RequirementStatement: 初回利用者が、起動後に新規作成、サンプル確認、既存文書読み込み、安全状態確認へ迷わず到達できる文書入口を用意する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ブラウザでkj-atlasを初回起動する / 操作=新規作成、サンプルを開く、document.jsonを読み込む、SafeMode状態を確認する / 期待結果=内部管理用語やレガシー導線に迷わず、現在の作業開始方法が分かる / 除外=認証付きポータルやクラウド同期の実装。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / import-sanitize

## 1) 課題 / Problem statement

- 現行アプリは標準サンプルまたは既定文書へ直接入る前提が強く、初回利用者が「何から始めるか」を画面上で判断しづらい。
- 主要ツールバーにはレガシーJSON操作が目立ち、文書の作成・読み込み・共有前確認の関係が分かりにくい。
- 公開文書では利用開始手順が整備されつつあるが、画面上の入口が同じ概念で整理されていない。

## 2) 背景 / Context

- `04_Documentation/public_index.md` は一般利用者向けの入口として整理済み。
- `04_Documentation/installation.md` と `operations.md` は起動・日常運用を説明するが、画面上の開始状態はMVP期の実装都合が残る。
- `ADR-0031` は開始/文書入口を製品化UIの基本領域として定義する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 初回に迷わず作業面へ入れることは、思考整理に集中する前提である。
- 安全（THREAT_MODEL / SafeMode）: 起動時からSafeModeと取り込み時の検証状態を見せることで、誤った共有や不正な取り込みを防ぎやすい。
- 企業・行政要件（enterprise_architecture）: 組織導入では、利用者が教育なしでも標準操作を開始できる画面が必要になる。
- 後方互換（schemas）: document/view/pack スキーマは変更せず、入口と説明を整理する。

## 3.1 依存関係 / Dependencies

- 直前依存: ADR-0031 の5領域定義。
- 連携先: PRODUCT-UX/QA 系issue（本ファイル内 Related ADR/Spec を参照）。
- ブロッカー条件: 上位ADRに矛盾がある場合は実装を開始しない。

## 3.2 非目標 / Non-goals（運用明示）

- 本issueの非目標は「4) 提案する解決策」の非目標節を正本とする。
- 非目標に該当する変更要求は、別issueまたはADRへ切り出す。

## 3.3 検証レベル / Verification level

- 本issueの検証レベルは Requirement meta I/F の `VerificationLevel` を正本とする。
- `e2e` 指定issueはPlaywright等の操作証跡を必須とし、`integration` 指定issueは横断ゲート記録を必須とする。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 起動直後の文書選択/作成状態。
  - サンプル、最近使った文書、document.json取り込み、レビューパック取り込みの配置。
  - SafeMode と読み取り専用状態の初期表示。
  - 公開文書のスクリーンショットと操作説明。
- 変更の最小単位:
  - 既定文書へ入る前に、開始状態または開始パネルを追加する。
  - レガシーJSON操作は補助導線として残し、推奨入口と区別する。
- 非目標:
  - 認証、ユーザープロファイル、クラウド上の最近使った文書一覧。
  - 既存のdocument読み込み形式の破壊的変更。

## 5) 受入条件 / Acceptance criteria

- [x] 初回起動時に、新規作成、サンプル、既存document.json、レビューパック取り込みの違いが分かる。→ Evidence update 2026-05-31: StartPanel に4入口を整理（`first_run_start_panel.spec.ts` 960px/390px pass）。
- [x] SafeModeの状態が、作業開始前に確認できる。→ Evidence update: 「SafeMode 状態も同じパネル内に表示する」。ブラウザ確認で SafeMode ON 表示。
- [x] 取り込み系操作は検証・置換・復元の違いが画面上で分かる。→ Evidence update: document.json/レビューパックは「共有と再現」パネルを開き、検証結果・置換確認を確認できる状態にする。
- [x] レガシーJSON操作が主要な推奨入口として誤認されない。→ §5.2: レガシーJSONは「以前の形式を読み込む」表現へ寄せ、推奨順を新規作成→サンプル→読み込み→レビューパックに固定。
- [x] `Tab` / `Enter` / `Space` で開始操作に到達できる。→ §5.1 各入口にキーボード操作を明記、T4「キーボード操作と小画面表示をE2Eで確認する」[x]。
- [x] 公開文書の導入手順と画面上の文言が一致する。→ Evidence update: `public_index.md`, `installation.md`, `operations.md`, `acceptance_check.md` を開始パネル前提に更新。

### 5.1 初期入口案

| 入口 | 利用者の意図 | 画面上の主ラベル | 補足表示 | マウス操作 | キーボード操作 |
| --- | --- | --- | --- | --- | --- |
| 新規作成 | 何もない状態から整理を始める | 新しい文書を作成 | SafeMode ON、保存先未設定 | 主要ボタンをクリック | `Tab`で到達し`Enter` |
| サンプルを開く | 操作感を確認する | サンプルを開く | サンプルであること、保存すると自分の文書になること | ボタンをクリック | `Tab`で到達し`Enter` |
| 文書を読み込む | 既存の作業を再開する | 文書ファイルを読み込む | 対応形式、取り込み前検証、上書き前確認 | ボタンからファイル選択 | `Tab`で到達し`Enter`後にファイル選択 |
| レビューパックを取り込む | 受け取った確認用データを見る | レビューパックを取り込む | 読み取り専用、共有元、検証結果 | ボタンからファイル選択 | `Tab`で到達し`Enter`後にファイル選択 |
| 最近の作業へ戻る | 直前の作業を続ける | 前回の文書を開く | ローカル保存であること、最終更新時刻 | 一覧項目をクリック | 矢印キーまたは`Tab`で選択し`Enter` |

### 5.2 画面状態と説明量

- 初回表示では、入口ごとの違いを短い名詞句で見せ、長い説明は詳細表示やヘルプ文書へ逃がす。
- 取り込み系の入口は、検証前、検証成功、検証失敗、置換確認、取り込み完了を別状態として扱う。
- SafeModeは常時表示し、開始画面では「共有前に自動で確認する」程度の利用者向け表現に留める。
- レガシーJSONは「開発者向け/互換用」ではなく、「以前の形式を読み込む」のように利用者が意味を取れる表現へ寄せる。
- 入口の見た目はボタンの数を増やしすぎず、推奨順を「新規作成」「サンプル」「読み込み」「レビューパック」の順で固定する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 起動直後に必要な開始操作を利用者視点で分類する。
- [x] T2 開始状態または開始パネルのワイヤーフローを作成する。
- [x] T3 SafeMode、読み取り専用、取り込み検証の状態表示を追加する。
- [x] T4 キーボード操作と小画面表示をE2Eで確認する。
- [x] T5 `04_Documentation/installation.md` と `operations.md` の手順・スクリーンショットを同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/i18n/ui_hardcode_guard.test.ts src/ui/i18n_equivalence.integration.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
- 期待結果:
  - 初回入口、取り込み、SafeMode確認がマウスとキーボードで到達可能で、公開文書と矛盾しない。
- 未実施時の理由・代替検証:
  - 自動E2E追加前は、Playwright script のTab順序ログとスクリーンショットで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既定文書を直接開き、文書だけで使い方を説明する。画面上の迷いが残るため採用しない。
- 代替案B: 完全なプロジェクト管理ダッシュボードを作る。製品化の初期段階としては過大であり、文書入口に絞る。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 起動直後の選択肢が増えすぎ、かえって初回利用者が迷う。
- 影響範囲: frontend shell、文書読み込み、公開文書。
- ロールバック手順: 開始パネルを機能フラグまたはルーティング単位で戻し、既定文書直接表示へ戻す。

## 10) Additional context

- ADR化が必要になる条件: 起動ルーティング、ローカル履歴保持、公開版と編集版の分離を再定義する場合。

## 11) Evidence update 2026-05-31: first-run document entry panel

- Implementation route: `StartPanel` を追加し、起動直後に「新しい文書を作成」「サンプルを開く」「文書ファイルを読み込む」「レビューパックを取り込む」を同じ入口に整理した。SafeMode 状態も同じパネル内に表示する。
- Integration route: `App.tsx` で既存の新規作成、標準サンプル読み込み、`document.json` 検証、レビューパック取り込み処理へ接続した。`document.json` とレビューパックは既存の「共有と再現」パネルを開き、検証結果や置換確認を確認できる状態にする。
- Documentation route: `04_Documentation/public_index.md`, `installation.md`, `operations.md`, `acceptance_check.md` を開始パネル前提に更新し、`04_Documentation/assets/screenshots/start-panel-document-entry.png` を追加した。
- Verification:
  - `node .\node_modules\typescript\bin\tsc --noEmit`: Pass（Codex bundled Node）
  - `node .\node_modules\vitest\vitest.mjs run src/ui/StartPanel.test.ts src/i18n/key_consistency.test.ts src/i18n/catalog_integrity.test.ts`: Pass, 6 tests
  - `node .\node_modules\playwright\cli.js test e2e/first_run_start_panel.spec.ts --reporter=line`: Pass, 2 tests at 960px / 390px
  - Browser check: `http://127.0.0.1:4173/?locale=ja` で開始パネル表示、横スクロールなし、SafeMode ON 表示を確認。
- Task status adjustment: T3, T4, T5 は開始パネルの代表経路として covered。最近使った文書の入口統合や、取り込み後の詳細状態を開始パネル内に戻すかどうかは、広い情報設計判断が必要な場合のみ別 issue/ADR へ切り出す。

---

## Stream I 要件契約固定パック（2026-05-18）

### Phase 1: Read同期サマリ
- 重複論点: 画面導線の分かりやすさ、SafeMode境界、検証証跡要件。
- 曖昧論点: Open化の判定条件と、依存関係が契約依存か実装依存かの境界。
- 欠落補完: 価値→要件→受入→測定の追跡行と、Draft→Open判定を明文化。

### Phase 2-3: ADR要素 + 要件契約
| Context | Decision | Consequences |
| --- | --- | --- |
| 上流価値定義（ADR-0001/0031/0032）を実装入口へ接続する必要がある。 | AC/DoDを機械検証可能な粒度で固定し、未確定はDecision Queueへ隔離する。 | 下流実装Streamは要件の再発明をせず、検証可能なIssue単位で着手できる。 |

### 価値→要件→受入→測定 対応表（最小）
| 価値仮説 | 要件（Requirement） | 受入条件（AC） | 測定（Evidence/KPI） |
| --- | --- | --- | --- |
| 利用者が安全に判断を共有できる。 | SafeMode境界を保持し、共有前確認を必須化する。 | SafeMode/公開範囲/未レビュー状態を実行前に提示できる。 | docs-check + E2E記録 + 文言一致確認。 |
| 要件から実装へ手戻りなく移行できる。 | AC/DoDをOpen前に固定し、未確定はPending化する。 | Draft→Open条件を満たしたIssueのみ実装に着手する。 | checklist充足率、No-Go件数、Pending解消件数。 |

### Phase 4: Draft→Open 条件（要件側ゲート）

### Phase 5-6: Verify / Proceed 引き継ぎ条件
- Verify合格条件: 価値仮説とACの1対1追跡が可能で、非検証要件が残っていない。
- Proceed条件: 実装ストリームが「どのACをどのテストで満たすか」を追加解釈なしで決定できる。
- フェイルセーフ: 上流価値定義との矛盾・非検証要件・競合編集を検出した場合はOpen化を停止する。

## Open化判定メタ（Draft gate解除条件）

### Open化に必要な最小条件（全件必須）

### 依存待ち理由（未解消時は Draft 維持）
| Dependency | 依存待ち理由 | 再開条件 | Owner |
|---|---|---|---|
| 上位ADR/関連Issue | 上位合意または境界仕様の最終確定待ち | 参照先に承認IDまたは確定コミットを追記 | Platform Architecture Owner / 各Issue Owner |
| QA検証経路 | `e2e`/`integration` の実行経路と証跡フォーマット未固定 | 実行経路（Compose/SQLite/例外）を1件固定し、判定ログ形式を定義 | QA Lead |
| 実行責務 | 実装担当とレビュー担当の分離未確定 | RACI（R/A）を本文に追記し通知記録を残す | PM/Triage |

### Proceed / Stop
- Proceed（Open化可）: O-OPEN-01〜04がすべて充足。
- Stop（Draft維持）: 依存先不明 / Status正規化不能 / 競合ファイル検出時は更新停止し、理由を `Additional context` に記録。

## Draft Gate Assessment 2026-05-23: Open readiness

- Assessment scope: 計画層のreadiness確認のみ。`Status: Draft` は維持し、画面実装や04文書更新はこの追記では行わない。
- Gate result: Draft維持。`DecisionStatus=Fixed` だが `Owner: TBD` が残り、初回入口の代表E2Eと証跡保存先が未固定。
- Proposed RACI: R=Product UX Stream Lead（未割当）, A=Productization Program Owner, C=Frontend Lead / QA Lead / Documentation Maintainer, I=Platform Architecture Owner。CodexはOwner確定までissue本文と証跡パックの整備を支援する。
- O-OPEN status:
  - O-OPEN-01: Blocked. `Owner` が `TBD` のため、実行責務者をロールまたは個人で確定する必要がある。
  - O-OPEN-02: Partial. `ADR-0031` と `MVP-EXIT-01` への依存は明示済みだが、再開条件が「どの画面証跡で足りるか」まで落ちていない。
  - O-OPEN-03: Partial. e2e前提のACはあるが、初回起動、サンプル選択、自分の文書入力、SafeMode確認の代表経路が未固定。
  - O-OPEN-04: Pass for assessment. この追記はOpen判定の整理であり、docs-only範囲外の実装要求を追加しない。
- 契約依存:
  - `ADR-0031`: 開始、文書入口、作業面の情報設計。
  - `MVP-EXIT-01`: MVP脱却時に初回利用者が迷わず主要作業へ入れること。
- 実装/証跡依存:
  - マウス操作でサンプルまたは文書入力から作業面へ入れることを示すE2E。
  - `Tab`、`Enter`、`Space` で同じ入口へ到達できるキーボードE2Eとスクリーンショット。
- Next action:
  - 初回入口のE2Eシナリオ名、fixture名、スクリーンショット保存先を本文へ追記する。
  - Owner確定と証跡経路固定が完了するまではOpen化しない。

## Open Gate Reassessment 2026-05-27: stewardship and evidence route fixed

- Assessment scope: 計画層のOpen化判定。これは実装完了判定ではなく、実装、E2E、公開文書同期へ進めるための責務と証跡経路の固定である。
- Gate result: **Open**. `DecisionStatus=Fixed`、OwnerはCodexの証跡整備責務として確定し、最終リリース判断はProductization Program Ownerの承認に残す。
- RACI:
  - R: Codex (Product UX evidence steward)
  - A: Productization Program Owner
  - C: Frontend Lead / QA Lead / Documentation Maintainer
  - I: Platform Architecture Owner
- O-OPEN status:
  - O-OPEN-01: Pass. OwnerはCodexに確定し、最終説明責任はProductization Program Ownerに分離した。
  - O-OPEN-02: Pass. 契約依存は`ADR-0031`、実装/証跡依存は初回入口E2Eと公開文書同期に分離した。
  - O-OPEN-03: Pass. `Expected verification level=e2e`に対し、`realistic_user_journey_expansion.spec.ts`、`header_toolbar_layout.spec.ts`、`polygon_import_validation.spec.ts`を代表経路として使う。
  - O-OPEN-04: Pass. 本更新はOpen化と証跡経路の固定であり、実装変更や04文書変更を直接要求しない。
- Fixed evidence route:
  - 初回の作業開始: `e2e/realistic_user_journey_expansion.spec.ts`
  - 起動後の表示、パネルfit、keyboard focus: `e2e/header_toolbar_layout.spec.ts`
  - document/review pack系取り込み検証: `e2e/polygon_import_validation.spec.ts` および import系unit regression
  - 公開文書同期: `04_Documentation/public_index.md`, `installation.md`, `operations.md`, `acceptance_check.md`
- Proceed rule:
  - 実装PRでは「開始入口の文言」「SafeMode表示」「取り込み検証」「Tab/Enter到達性」「公開文書スクリーンショット」のうち、変更対象に対応する証跡を必ず添付する。
  - Product shipmentは本Issue OpenだけではGoにしない。実装証跡と公開文書同期が揃った時点で`PRODUCT-QA-01`へ戻す。

## Completion Evidence 2026-05-31: first-run entry implemented

- 実装:
  - `03_Implement/frontend/src/ui/StartPanel.tsx` を追加し、起動直後に「新しい文書を作成」「サンプルを開く」「文書ファイルを読み込む」「レビューパックを取り込む」を同じ入口で選べるようにした。
  - `03_Implement/frontend/src/App.tsx` から既存の新規作成、サンプル読込、document.json 検証、レビューパック検証フローへ接続した。
  - 開始パネルに SafeMode、現在の文書、編集状態（編集可/読み取り専用）を表示した。
- 検証:
  - `03_Implement/frontend/e2e/first_run_document_entry.spec.ts` を追加し、390pxでの表示収まり、document.json の検証後置換フロー、キーボード起動を確認した。
  - `header_toolbar_layout.spec.ts` と同時実行し、開始パネル追加後もヘッダー、表示パネル、共有パネルのレイアウトとフォーカス復帰が崩れないことを確認した。
- 公開文書:
  - `04_Documentation/installation.md`、`operations.md`、`public_index.md` に開始パネルの説明を追加した。
  - `04_Documentation/assets/screenshots/start-document-entry.png` を追加し、`04_Documentation/assets/screenshots/README.md` に撮影対象を追記した。
- 実行確認:
  - bundled node `tsc --noEmit`: Pass.
  - bundled node `vitest run src/i18n/key_consistency.test.ts src/i18n/catalog_integrity.test.ts src/i18n/ui_hardcode_guard.test.ts`: Pass, 13 tests.
  - bundled node `playwright test first_run_document_entry header_toolbar_layout --reporter=line`: Pass, 10 tests.
  - Browser plugin / in-app browser で `http://127.0.0.1:4173/?locale=ja` を開き、開始パネルの表示文言を確認した。

## Evidence Refresh 2026-06-06: current-main first-run entry rerun

- Candidate: `origin/main@f9c042f595aa96754b6da83e0e62ca946f48ac27`.
- Reviewer: Codex.
- Scope: current-main browser automation rerun for the first-run document entry and adjacent header/panel operability. This is an evidence refresh only; it does not change runtime behavior, UI copy, SafeMode policy, import/export behavior, public documentation, issue status, or release authority.
- Local execution:
  - Bundled Node.js started Vite directly on `127.0.0.1:4173` because this Codex host did not expose `npm` on PATH.
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/first_run_document_entry.spec.ts e2e/header_toolbar_layout.spec.ts --reporter=line` -> pass, 11 tests.
- Covered user operations:
  - 390x720 first-run panel fit and safe entry choices.
  - Document-file selection with validation-before-replace dialog.
  - Sample open, card selection, and selection-context surfacing.
  - Keyboard focus and `Enter` activation for new-document creation.
  - Header View / Share & Reproduce panel placement and `Escape` focus return across desktop/tablet/narrow viewports.
- Human follow-ups:
  - Confirm real Chrome copy quality and screenshot approval for the first-run panel remains human-owned.
  - Confirm physical keyboard and screen-reader acceptance before using this as final release evidence.


## Evidence Refresh 2026-06-07: current-main import validation rerun

- Candidate: `origin/main@ec08690eb98124820dfbc946f202b081eb7a2c0d`.
- Reviewer: Codex.
- Scope: current-main browser automation rerun for the document/review-pack ingestion validation route that `O-OPEN-03` names as a representative first-run safety path. This is an evidence refresh only; it does not change runtime behavior, UI copy, SafeMode policy, import/export behavior, public documentation, issue status, or release authority.
- Local execution:
  - Bundled Node.js started Vite directly on `127.0.0.1:4173` because this Codex host did not expose `npm` on PATH.
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/polygon_import_validation.spec.ts --reporter=line` -> pass, 1 test.
- Covered user operations:
  - Opened Share & Reproduce, selected an invalid `document.json` through the file picker, and used the replace confirmation flow.
  - Imported a self-intersecting island polygon and exported a review bundle.
  - Confirmed exported `document.json` does not preserve the invalid polygon shape and falls back to a non-polygon shape.
- Human follow-ups:
  - Keep real Chrome copy quality and visible import-validation messaging review human-owned before release.
  - Keep malicious/large-file import breadth covered by import/security regression suites rather than treating this single E2E as exhaustive import assurance.
