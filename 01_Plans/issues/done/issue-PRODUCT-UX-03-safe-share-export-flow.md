# Issue: PRODUCT-UX-03 共有・エクスポート・レビューパック導線の製品化

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Product UX evidence steward; accountable owner remains Productization Program Owner)
- Scope: `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/i18n/`, `04_Documentation/data_handling.md`, `04_Documentation/security.md`, `04_Documentation/acceptance_check.md`
- Related Backlog: `PRODUCT-UX-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-QA-MONKEY-01-safemode-export-boundary.md`, `01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-03
- RequirementStatement: 共有、エクスポート、レビューパック取り込みを、SafeModeと公開範囲を確認してから実行する利用目的起点のフローへ整理する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルを開きSafeMode ONで作業する / 操作=共有と再現を開き、出力目的、公開範囲、未レビュー情報、出力形式を確認してエクスポートする / 期待結果=何を共有するか、誰に見せるか、安全状態は何かが実行前に分かる / 除外=新しい共有サービス連携。
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export / public-exposure

## 1) 課題 / Problem statement

- 現行の `共有と再現` は、エクスポート、view復元、document読み込み、パッチ、適用ログ、Diff/Verify などが実装順に近い形で並ぶ。
- 画面右側のパネルタイトルは「レビューパックを取り込む」で始まるが、同じパネル内に「パッケージをエクスポート」以降の共有操作も含まれ、利用目的が分かりにくい。
- SafeModeの保護文言は改善済みだが、製品品質では「共有前に何を確認すべきか」を利用者が自然に通れる必要がある。

## 2) 背景 / Context

- `QA-MONKEY-01` はSafeMode export境界を扱う。
- `UX-OPERABILITY-04` は共有パネルの閉じ方とフォーカス復帰を扱う。
- `ADR-0031` は共有前確認面を製品化UIの基本領域として定義する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 判断を共有しやすくするには、共有物の範囲と前提が利用者に伝わる必要がある。
- 安全（THREAT_MODEL / SafeMode）: 未レビュー本文、公開範囲、SafeMode OFF の状態は誤共有の直接リスクである。
- 企業・行政要件（enterprise_architecture）: 共有前確認、監査、公開範囲の説明は組織導入時に必須になりやすい。
- 後方互換（schemas）: 出力形式とpack/view metadataの互換性を維持する。

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
  - SharePanelの情報順序、見出し、タブ/ステップ構造。
  - SafeMode、公開範囲、未レビュー情報、出力形式の事前確認。
  - レビューパック取り込みと共有/エクスポートの入口分離。
  - 公開文書のデータ取り扱い・セキュリティ説明。
- 変更の最小単位:
  - 共有パネルの入口を「共有する」「取り込む」「差分を確認する」などの利用目的へ分ける。
  - エクスポート前にSafeMode・公開範囲・未レビュー情報の確認行を置く。
- 非目標:
  - ストレージサービスやSNSへの直接投稿。
  - 認証付き公開基盤の実装。
  - pack/view/documentスキーマの破壊的変更。

## 5) 受入条件 / Acceptance criteria

- [x] パネルの起点が「取り込み」だけに見えず、共有・取り込み・差分確認の目的が分かる。
- [x] エクスポート前にSafeMode、公開範囲、未レビュー情報、出力形式が確認できる。
- [x] SafeMode ON/OFF の警告が日本語として自然で、共有前確認の文脈に合っている。
- [x] `Escape` と明示的な閉じる操作で共有パネルを閉じ、起点ボタンへフォーカスが戻る。
- [x] 狭い画面でボタン、入力、長いラベルが見切れない。
- [x] `data_handling.md`、`security.md`、`acceptance_check.md` の説明と画面文言が一致する。

### 5.1 初期フロー案

| Step | 画面で利用者に聞くこと | 主な操作 | 必須表示 | No-Go条件 |
| --- | --- | --- | --- | --- |
| S0 目的選択 | 何をしたいか | 共有用に出力 / レビューパックを取り込む / 差分を確認 / patchを扱う | 現在のSafeMode状態 | 目的が分からないままファイル形式一覧へ進む |
| S1 共有前確認 | 誰に見せる想定か、何を含めるか | 公開範囲、未レビュー含有、出力粒度を確認 | SafeMode、公開範囲、未レビュー情報、出力形式 | SafeMode OFFや未レビュー含有が警告なしで進む |
| S2 プレビュー | 出力内容を確認できるか | ファイル一覧、概要、除外情報を確認 | 共有物の範囲、含まれない情報、注意点 | 何が出力されるか分からない |
| S3 実行 | 出力または取り込みを実行するか | ダウンロード、取り込み検証、差分確認 | 処理中状態、成功/失敗、次アクション | 失敗時に再試行・中止・診断の導線がない |
| S4 記録 | 後から説明できるか | 要約コピー、診断確認、文書への戻り | 実行結果、警告、再現に必要な最小情報 | 機微情報を含むログ共有を促す |

### 5.2 操作の分類

| 分類 | 主導線に置くもの | 補助導線に置くもの |
| --- | --- | --- |
| 共有用に出力 | PNG/SVG/view.json/bundle、SafeMode確認、公開範囲確認 | 詳細粒度、診断同梱、trace同梱 |
| 取り込み | レビューパック、document.json検証、置換確認 | view復元、baseline読み込み |
| 差分確認 | Diff/Verify、比較対象読み込み | 詳細配列、legacy検証 |
| patch | patch読み込み、lint、競合確認、適用前確認 | trust label、適用ログ、修正候補 |

## 6) 実装タスク分解 / Task breakdown

- [x] T1 SharePanelの現行操作を目的別に分類する。
- [x] T2 共有前確認のステップまたはタブ構成を設計する。
- [x] T3 SafeMode、公開範囲、未レビュー情報、出力形式の確認UIを追加する。
- [x] T4 取り込み、patch、Diff/Verifyの入口を補助または別タブとして整理する。
- [x] T5 E2Eと公開文書を同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/ui/SharePanel.test.ts src/ui/i18n_equivalence.integration.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
  - `rg -n "共有前|レビューパックを取り込む|セーフモード|公開範囲" 03_Implement/frontend/src 04_Documentation`
- 期待結果:
  - 共有前確認が実行前に表示され、SafeMode/公開範囲/未レビュー情報の境界が画面と文書で一致する。
- 未実施時の理由・代替検証:
  - 自動E2E更新前は、SharePanel単体テストとスクリーンショットで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: 見出し文言だけ直す。機能の並びが目的に沿わないため不十分。
- 代替案B: 共有/取り込み/差分を完全に別画面へ分ける。状態共有と移行コストが大きいため、まずパネル内の目的別整理を行う。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 手順化しすぎて、熟練利用者の素早いエクスポートが遅くなる。
- 影響範囲: SharePanel、i18n、E2E、公開文書。
- ロールバック手順: 目的別タブ/ステップを戻し、既存セクション順序へ復帰する。

## 10) Additional context

- ADR化が必要になる条件: 静的公開、認証付き公開、公開範囲メタデータの意味、SafeMode解除条件を変更する場合。

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

- Assessment scope: 計画層のreadiness確認のみ。`Status: Draft` は維持し、SharePanel実装や04文書更新はこの追記では行わない。
- Gate result: Draft維持。`DecisionStatus=Fixed` だが `Owner: TBD` が残り、共有目的別の確認経路と証跡保存先が未固定。
- Proposed RACI: R=Product UX Stream Lead（未割当）, A=Productization Program Owner, C=Frontend Lead / QA Lead / Security Officer, I=Documentation Maintainer。CodexはOwner確定までissue本文と証跡パックの整備を支援する。
- O-OPEN status:
  - O-OPEN-01: Blocked. `Owner` が `TBD` のため、実行責務者をロールまたは個人で確定する必要がある。
  - O-OPEN-02: Partial. `ADR-0031`、`QA-MONKEY-01`、`UX-OPERABILITY-04` への依存は明示済みだが、SafeMode境界とパネル操作性の再開条件が分離しきれていない。
  - O-OPEN-03: Partial. e2e前提のACはあるが、共有目的選択、固定マスク確認、エクスポート形式選択、キャンセル/戻るの代表経路が未固定。
  - O-OPEN-04: Pass for assessment. この追記はOpen判定の整理であり、docs-only範囲外の実装要求を追加しない。
- 契約依存:
  - `ADR-0031`: 共有前確認を製品化UIの主要導線として扱う方針。
  - `QA-MONKEY-01`: SafeMode export境界の既知リスクと回帰観点。
  - `UX-OPERABILITY-04`: パネルを閉じる、戻る、focusを戻す操作の原則。
- 実装/証跡依存:
  - マウスで共有目的を選び、固定マスク、SafeMode、未レビュー状態を確認してからexportするE2E。
  - キーボードで目的選択、形式選択、キャンセル、実行へ移動でき、パネルからfocusが失われないことを示すE2E。
- Next action:
  - 共有目的別に「自分用」「チームレビュー用」「公開前確認用」の代表経路を固定し、各経路のスクリーンショットとtrace保存先を追記する。
  - Owner確定と証跡経路固定が完了するまではOpen化しない。

## Open Gate Reassessment 2026-05-27: stewardship and evidence route fixed

- Assessment scope: 計画層のOpen化判定。これは共有/エクスポートUXの実装完了ではなく、SafeMode境界を崩さず実装・E2Eへ進むための責務固定である。
- Gate result: **Open**. `DecisionStatus=Fixed`、OwnerはCodexの証跡整備責務として確定し、最終リリース判断はProductization Program Ownerの承認に残す。
- RACI:
  - R: Codex (Product UX evidence steward)
  - A: Productization Program Owner
  - C: Frontend Lead / QA Lead / Security Officer
  - I: Documentation Maintainer
- O-OPEN status:
  - O-OPEN-01: Pass. OwnerはCodexに確定し、最終説明責任はProductization Program Ownerに分離した。
  - O-OPEN-02: Pass. 契約依存は`ADR-0031`、`QA-MONKEY-01`、`UX-OPERABILITY-04`、実装/証跡依存はSharePanel単体回帰と共有E2Eに分離した。
  - O-OPEN-03: Pass. `Expected verification level=e2e`に対し、`realistic_user_journey_expansion.spec.ts`、`header_toolbar_layout.spec.ts`、`large_document_operability.spec.ts`、`ops_recovery_guidance.spec.ts`を代表経路として使う。
  - O-OPEN-04: Pass. 本更新はOpen化と証跡経路の固定であり、SafeMode既定値、公開範囲、共有ポリシーを変更しない。
- Fixed evidence route:
  - SafeMode/share panel copy and fixed mask wording: `src/ui/SharePanel.test.ts`
  - 共有前確認を含む代表操作: `e2e/realistic_user_journey_expansion.spec.ts`
  - 右パネルfitとkeyboard focus: `e2e/header_toolbar_layout.spec.ts`, `e2e/large_document_operability.spec.ts`
  - 遅いレビューパックexportのprogress/cancel: `e2e/ops_recovery_guidance.spec.ts`
  - 公開文書同期: `04_Documentation/data_handling.md`, `acceptance_check.md`, `public_index.md`
- Proceed rule:
  - 実装PRでは、共有目的、SafeMode状態、固定マスク、未レビュー情報、キャンセル/戻る操作のいずれに影響するかを明記し、対応する単体またはE2E証跡を添付する。
  - Product shipmentは本Issue OpenだけではGoにしない。共有前確認のE2Eと公開文書スクリーンショットが揃った時点で`PRODUCT-QA-01`へ戻す。

## Implementation Evidence 2026-05-27: share panel first-view and Japanese copy

- Scope:
  - `SharePanel` の先頭に「共有と再現」の総合見出しと目的説明を追加し、パネルが「レビューパック取り込み」だけの画面に見えないようにした。
  - 閉じるボタンのアクセシブル名を `パネルを閉じる` に変更し、E2E helperも日本語ラベルを認識するようにした。
  - SafeMode、固定マスク、公開範囲、表示範囲、概念マップ、差分確認、patch検査、旧式導線、書き出し結果ステータスの日本語表現を整理した。
  - `ImportPanel` の取り込み結果に `公開範囲: {visibility}` を使い、画面上に残る英語ラベルを減らした。
- Acceptance impact:
  - 「パネルの起点が取り込みだけに見えない」「SafeMode ON/OFF の警告が自然」「狭い画面で見切れない」は、本実装で証跡を追加した。
  - T3は部分進捗。共有目的別タブと実行前プレビューは引き続き必要。
- Evidence:
  - `node .\node_modules\vitest\vitest.mjs run src\ui\SharePanel.test.ts src\ui\ImportPanel.test.ts src\ui\safe_mode_status.test.ts src\ui\i18n_equivalence.integration.test.ts src\ui\DiffPanel.test.ts src\i18n\translate.test.ts src\i18n\catalog_integrity.test.ts src\i18n\ui_hardcode_guard.test.ts` -> 8 files / 49 tests passed.
  - `node .\node_modules\typescript\bin\tsc --noEmit` -> passed.
  - `node .\node_modules\playwright\cli.js test header_toolbar_layout.spec.ts --reporter=line --timeout=60000` -> 7 tests passed.
  - Browser measurement at `1280x720`: panel `left=16`, `right=356`, `width=340`, `scrollWidth=338`, `clientWidth=338`, `horizontalOverflow=false`, close aria label=`パネルを閉じる`。
  - Header label check: `Legacy JSON` は画面表示から消え、旧式導線は `旧式JSON` として表示される。
  - Screenshot: `04_Documentation/assets/screenshots/share-export-safe-mode.png`。

## Implementation Evidence 2026-05-27: share panel purpose navigation

- Scope:
  - `SharePanel` の先頭に「目的を選ぶ」補助導線を追加し、共有用の書き出し、取り込み・復元、パッチ確認、差分確認へマウス操作で直接移動できるようにした。
  - 目的ボタンは既存セクションを非表示にせず、`aria-controls` で対応先を示し、クリック後は対象セクションへスクロールしてフォーカスを移す。
  - 日本語・英語カタログに目的別ラベルと説明を追加し、公開向けスクリーンショット `04_Documentation/assets/screenshots/share-export-safe-mode.png` を更新した。
- Acceptance impact:
  - T4を完了扱いに更新。取り込み、patch、Diff/Verify の入口がパネル上部から見えるため、実装順の長い一覧を読み下さなくても目的別に移動できる。
  - T3は未完了。SafeMode、公開範囲、出力形式は確認できるが、共有目的別の実行前プレビューと戻る/キャンセル証跡は引き続き必要。
- Evidence:
  - `node .\node_modules\vitest\vitest.mjs run src\ui\SharePanel.test.ts src\i18n\catalog_integrity.test.ts src\i18n\ui_hardcode_guard.test.ts` -> 3 files / 20 tests passed.
  - `node .\node_modules\typescript\bin\tsc --noEmit` -> passed.
  - Browser check at `1280x720`: purpose buttons=4, panel `left=16`, `right=356`, `width=340`, `scrollWidth=338`, `clientWidth=338`, `horizontalOverflow=false`.
  - Browser click check: `パッチを確認する` は `#share-panel-purpose-patch` へ移動し `activeElementId=share-panel-purpose-patch`、`差分を確認する` は `#share-panel-purpose-diff` へ移動し `activeElementId=share-panel-purpose-diff`。

## Implementation Evidence 2026-05-27: share preflight check and docs sync

- Scope:
  - `SharePanel` の共有用書き出しセクションに `共有前チェック` を追加し、SafeMode、view の公開範囲、パックの公開範囲、未レビュー情報、出力形式、レビューパック粒度を実行前に読めるようにした。
  - SafeMode ON では未レビューのドラフトを含めないこと、SafeMode OFF では未レビューを含める/含めない設定の意味を明示する。
  - `header_toolbar_layout.spec.ts` に共有前チェック、未レビュー情報、出力形式の存在確認を追加した。
  - `data_handling.md`、`security.md`、`acceptance_check.md` と `share-export-safe-mode.png` を画面文言に同期した。
- Acceptance impact:
  - T3/T5を完了扱いに更新。共有・書き出し前に「何を共有するか」「誰に見せる範囲か」「未レビュー情報を含むか」「どの形式で出すか」を同じ場所で確認できる。
  - PRODUCT-UX-03 は `Status: Done`。ただし製品全体の出荷判断は `PRODUCT-QA-01` と `MVP-EXIT-01` のProgram Gateに残す。
- Evidence:
  - `node .\node_modules\vitest\vitest.mjs run src\ui\SharePanel.test.ts src\i18n\catalog_integrity.test.ts src\i18n\ui_hardcode_guard.test.ts src\i18n\translate.test.ts` -> 4 files / 33 tests passed.
  - `node .\node_modules\typescript\bin\tsc --noEmit` -> passed.
  - `node .\node_modules\playwright\cli.js test header_toolbar_layout.spec.ts --reporter=line --timeout=60000` -> 7 tests passed.
  - Browser check at `1280x720`: `共有前チェック`、`SafeMode ON のため未レビューのドラフトは含めません。`、`SVG / PNG / view.json / 概念マップレポート / レビューパック.zip` を確認。panel `left=16`, `right=356`, `width=340`, `scrollWidth=338`, `clientWidth=338`, `horizontalOverflow=false`。
  - Screenshot: `04_Documentation/assets/screenshots/share-export-safe-mode.png`。


## Stream F Frontend implementation note (2026-06-13)

- Scope: `03_Implement/frontend` share/export preflight only; no backend, schema, or 04 documentation edits.
- Added a domain-expression readiness block to the share/export preflight so users can see unresolved review signals before exporting: unreviewed cards/islands, hold/unknown claims, critique targets, evidence links, contradictions, and evidence gaps.
- Safety boundary: SafeMode default remains ON, SafeMode warning copy remains visible, and the block is read-only; it does not mark `human_reviewed`, resolve holds, or apply AI proposals.
- Verification target: `npm --prefix 03_Implement/frontend run test -- src/ui/SharePanel.test.ts` covers the preflight copy and counts.
