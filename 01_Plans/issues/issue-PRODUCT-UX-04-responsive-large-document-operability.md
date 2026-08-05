# Issue Draft: PRODUCT-UX-04 小画面・大規模文書・低速環境での操作性確認

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Product UX evidence steward; accountable owner remains Productization Program Owner)
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `04_Documentation/acceptance_check.md`, `04_Documentation/diagnostics.md`
- Related Backlog: `PRODUCT-UX-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-QA-MONKEY-06-header-toolbar-responsive-overlap.md`, `01_Plans/issues/issue-UX-OPERABILITY-01-pointer-keyboard-flow-review.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-04
- RequirementStatement: 製品化対象として、狭い画面、大きな文書、低速環境でも主要操作が見切れず、待機状態と復帰方法が理解できる状態にする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルと大きめの文書を複数viewportで開く / 操作=検索、選択、表示切替、共有前確認、診断を実行する / 期待結果=見切れ、重なり、反応なしに見える状態、フォーカス迷子がない / 除外=モバイル専用ネイティブUI。
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export

## 1) 課題 / Problem statement

- MVP期の画面はデスクトップ広幅での利用を中心に増築されており、狭い画面や右側パネルの長いラベルで見切れが起きやすい。
- 大きな文書や低速環境では、検索、表示切替、診断、エクスポートの待機状態が分かりにくい可能性がある。
- 製品化では、代表的な画面幅とデータ規模での操作感を品質ゲートに入れる必要がある。

## 2) 背景 / Context

- `QA-MONKEY-06` でヘッダーツールバーのレスポンシブ崩れは修正済み。
- `UX-OPERABILITY-01` の代表確認では、390px / 960px / 1440pxで共有パネル右端見切れは再発していないが、画面構造変更後も継続検証が必要である。
- `ADR-0031` は小画面・大規模文書・低速環境を製品化UIの必須条件とした。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 思考整理の作業中に画面崩れや反応不明が起きると、利用者は内容ではなく操作に注意を奪われる。
- 安全（THREAT_MODEL / SafeMode）: 共有前確認やSafeMode状態が見切れると誤共有のリスクになる。
- 企業・行政要件（enterprise_architecture）: 支給端末、リモート環境、VDIなど画面幅や性能が揺れる環境での利用が想定される。
- 後方互換（schemas）: 表示・パフォーマンス・E2Eの課題であり、データ契約は維持する。

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
  - ヘッダー、主要ツールバー、右側パネル、SharePanel、ViewControlsPanel。
  - 大きな文書の検索、表示切替、診断、エクスポートの待機表示。
  - E2E viewport matrix と手動受け入れ確認。
- 変更の最小単位:
  - 390px / 768px / 960px / 1440px の代表幅で主要操作を確認する。
  - 大きめfixtureを用意し、検索・選択・共有前確認の操作時間と待機表示を確認する。
- 非目標:
  - スマートフォン専用アプリ化。
  - リアルタイム共同編集や差分同期の導入。

## 5) 受入条件 / Acceptance criteria

- [ ] 390px、768px、960px、1440pxの代表幅で、主要ボタンとSafeMode状態が見切れない。
- [ ] 右側パネルと共有パネルの長い日本語ラベルが、横スクロール前提にならず読める。
- [ ] 大きな文書で検索、選択、表示切替、共有前確認を行っても、処理中状態や次の操作が分かる。
- [ ] 低速またはbackend待機時に、利用者が保存・再読み込み・診断のどれを行うべきか判断できる。
- [ ] E2EまたはPlaywright scriptで代表viewportと主要操作が記録される。
- [ ] `acceptance_check.md` と `diagnostics.md` が製品化後の確認観点を説明する。

### 5.1 代表確認マトリクス

| 条件 | 代表値 | 確認する操作 | 合格の目安 | 記録方法 |
| --- | --- | --- | --- | --- |
| 狭い画面 | 390px幅 | 開始、選択、共有前確認、診断 | 主要ボタンとSafeModeが見切れず、横スクロールなしで読める | Playwright screenshot / 操作ログ |
| タブレット相当 | 768px幅 | パネル開閉、表示切替、検索 | パネルが本文を不自然に隠さず、戻り方が分かる | Playwright screenshot |
| 小さめデスクトップ | 960px幅 | 右側パネル、共有、エクスポート | 長い日本語ラベルが折り返され、ボタンが押せる | E2E / screenshot |
| 標準デスクトップ | 1440px幅 | 複数パネル、キャンバス操作 | 情報量が過密にならず、主要導線が一貫する | E2E |
| 大きめ文書 | 標準サンプルの複製または専用fixture | 検索、選択、表示切替、共有前確認 | 処理中表示があり、操作不能に見えない | E2E / 手動記録 |
| 低速環境 | worker/API遅延またはbackend未接続 | 保存、診断、再試行 | 待機中、失敗、復帰の違いが分かる | 失敗注入ログ / screenshot |

### 5.2 不自然な操作として扱う基準

- クリック対象が見えていても、周囲の説明や状態が隠れている場合は不合格とする。
- `Tab`移動でパネル内へ入った後、閉じる・戻る・主要操作へ復帰する経路が分からない場合は不合格とする。
- 処理中に同じボタンを連打できる、または連打してよいか分からない表示は不自然な操作として扱う。
- 共有前確認、SafeMode、取り込み検証は、画面幅が狭くても省略してよい情報にしない。
- モバイル専用UIや別ルートが必要になるほど差分が大きい場合は、このissueで実装せずADR化する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 代表viewportと代表データ規模を定義する。
- [x] T2 大きめfixtureまたは既存サンプル拡張を用意する。
- [x] T3 主要パネルのレイアウト崩れ、長いラベル、フォーカス順序を検証する。
- [x] T4 待機表示、エラー表示、診断導線を確認する。
- [x] T5 E2Eと公開文書の受け入れ確認を更新する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `rg -n "390|768|960|1440|viewport|大きな文書|低速" 04_Documentation 03_Implement/frontend/e2e`
- 期待結果:
  - 代表viewportと大きめ文書で主要操作が見切れず、待機・エラー・復帰導線が分かる。
- 未実施時の理由・代替検証:
  - 大きめfixture未整備時は、既存fixtureを複製した検証用データで暫定確認する。

## 8) 代替案 / Alternatives considered

- 代替案A: デスクトップ広幅のみを公式サポートにする。公開配布や組織導入の期待と合わない。
- 代替案B: 小画面では機能を大幅に削る。SafeModeや共有前確認など削れない操作があるため、表示優先順位で整理する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 小画面最適化でデスクトップの作業効率が下がる。
- 影響範囲: frontend layout、E2E、公開文書。
- ロールバック手順: レスポンシブ変更をコンポーネント単位で戻し、代表viewportテストだけを残して再設計する。

## 10) Additional context

- ADR化が必要になる条件: モバイル専用UI、別ルート、キャンバスレンダリング方式の変更を決める場合。

## 11) Evidence update 2026-05-22: canvas pointer operability fixed, broader matrix remains

### Closed in implementation

- Resolved defect: the primary canvas flow had no effective height, so polygon handles could be visible while mouse hit-testing targeted surrounding layout instead of the handle buttons.
- Implementation route: `App.tsx` gives `data-ui-region="primary-flow"` a real `height: 100%`; `CanvasShell.tsx` renders polygon edit controls above card layers; `PolygonEditLayer.tsx` uses a bounded hit-test area around the edited polygon.
- Verification: `e2e/polygon_vertex_edit.spec.ts` and `e2e/polygon_autofit_qa_boundary.spec.ts` pass, including vertex drag and self-intersection guard behavior.
- ADR impact: no ADR required because this restores the agreed mouse-operation contract instead of changing screen architecture or product policy.

### Partial evidence now available

| Area | Evidence | Result | Remaining gap |
| --- | --- | --- | --- |
| Header/share responsive fit | `e2e/header_toolbar_layout.spec.ts` | Pass at 1440px / 1280px / 920px / 768px / 390px | large-document and slow/backend-recovery scenarios remain outside this fit check. |
| Header panel keyboard flow | `e2e/header_toolbar_layout.spec.ts` | Pass at 1440px / 768px: focus Share/View trigger, Enter opens dialog, Escape closes, focus returns to trigger. | advanced panel-specific focus paths remain sampled rather than exhaustive. |
| Canvas mouse and keyboard operability | `e2e/polygon_vertex_edit.spec.ts`, `e2e/polygon_autofit_qa_boundary.spec.ts`, `e2e/canvas_focus_order.spec.ts` | Pass: mouse drag, arrow-key nudge, Shift+arrow large nudge, Delete removal, self-intersection guard, card selection, island selection, and side-panel focus reachability. | broader slow worker/API delay states remain under this issue. |
| Full frontend E2E | bundled Playwright full suite | Pass: 32 tests | synthetic large-document fixture and canvas focus-order fixture are now covered; broader slow/backend-recovery scenarios remain outside the current suite. |
| Frontend regression | full Vitest | Pass: 160 files / 734 tests | does not replace browser viewport evidence. |

### Task status adjustment

- T3 remains open but narrowed: layout collapse, mouse hit-testing, polygon keyboard nudge/removal, 768px/1440px header-panel fit, Share/View keyboard open-close focus return, card/island/side-panel focus reachability, and synthetic large-document interaction evidence are fixed for covered flows; advanced panel-specific focus paths and broader slow/backend-recovery UX remain.
- T5 remains open: public acceptance documentation should be updated after the full viewport/large-document/slow-environment matrix is recorded.

## 12) Evidence update 2026-05-22: header panel keyboard and viewport matrix

- Implementation route: `App.tsx` now moves focus into the View dialog when it opens and restores focus to the View trigger when Escape closes it. This aligns View with the existing Share dialog focus-return behavior.
- E2E route: `e2e/header_toolbar_layout.spec.ts` now checks 1440px, 1280px, 920px, 768px, and 390px layout fit, plus keyboard Enter/Escape focus return at 1440px and 768px.
- Verification:
  - bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit`: Pass.
  - bundled `node.exe .\node_modules\playwright\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`: Pass, 7 tests.
- Remaining gap: this closes the header/share/view panel portion of the viewport matrix. Synthetic large-document coverage is recorded in section 14; slow/backend-recovery UX and broader canvas edit-mode keyboard semantics remain open.

## 13) Evidence update 2026-05-22: polygon edit keyboard operation

- Implementation route: `PolygonEditLayer.tsx` now makes vertex handles keyboard focusable and supports Arrow-key nudging, Shift+Arrow larger nudging, and Delete/Backspace removal. `CanvasShell.tsx` converts screen-step keyboard deltas into world coordinates using the current zoom before committing the vertex move.
- E2E route: `e2e/polygon_vertex_edit.spec.ts` now verifies focus on a vertex handle, ArrowRight + Shift+ArrowDown movement, Delete removal of another vertex, and persistence through legacy document JSON export.
- Verification:
  - bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit`: Pass.
  - bundled `node.exe .\node_modules\playwright\cli.js test e2e/polygon_vertex_edit.spec.ts --reporter=line`: Pass, 2 tests.
- Remaining gap: the polygon edit primitive is now keyboard-operable. Card selection, island selection, and side-panel focus reachability are recorded in section 16; advanced panel-specific focus paths remain sampled rather than exhaustive.

## 14) Evidence update 2026-05-22: synthetic large-document operability

- E2E route: `e2e/large_document_operability.spec.ts` loads a deterministic 120-card / 12-island / 119-edge document at 768px width.
- Verification scope: search for a rare card, hide non-matches, confirm the rare card remains visible, open View and Share panels without fixed-panel viewport overflow, and export a review bundle whose `diagnostics.md` contains `connectivityScore`.
- Command evidence:
  - bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit`: Pass.
  - bundled `node.exe .\node_modules\playwright\cli.js test e2e/large_document_operability.spec.ts --reporter=line`: Pass, 1 test.
  - bundled `node.exe .\node_modules\playwright\cli.js test --reporter=line`: Pass, 32 tests.
- Task status adjustment: T2 is covered for a synthetic browser fixture. T3 remains open for broader focus-order breadth. T4 remains open for slow/backend-recovery states. T5 remains open until public acceptance documentation is updated after the remaining slow-environment evidence is available.

## 15) Evidence update 2026-05-22: backend-recovery guidance on small screens

- Implementation route: API load/create/save failures now produce recovery-oriented status messages and the status region is fixed to the viewport with wrapping, preventing long diagnostic guidance from being pushed off-screen by the right panel.
- Documentation route: `04_Documentation/acceptance_check.md` now asks users to verify progress, disabled in-flight controls, cancellation, cancelled status messages, and narrow-screen fit for diagnostics and review-pack export.
- E2E route: `e2e/ops_recovery_guidance.spec.ts` covers API load failure, save failure, slow diagnostics cancellation, and slow review-pack export cancellation at 390px width, including viewport-fit checks for the status message.
- Verification:
  - bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit`: Pass.
  - bundled `node.exe .\node_modules\playwright\cli.js test e2e/ops_recovery_guidance.spec.ts --reporter=line`: Pass, 4 tests.
- Task status adjustment: the backend-recovery messaging portion of T4 is covered for API unavailable/save failure. Progress/cancel behavior is covered for slow diagnostics and slow review-pack export. T4 remains open for broader worker/API delay states outside those covered flows.

## 16) Evidence update 2026-05-22: canvas focus order and residual English labels

- Implementation route: `IslandView.tsx` and `CanvasShell.tsx` now use the i18n catalog for island select/focus/collapse/peek labels, default island titles, representative labels, card-count tooltips, collapsed/stale badges, and critique indicators. `SidePanel.tsx` now localizes the island editor labels for parent island, collapse state, title, placard card, and placard-card text.
- Regression route: `src/i18n/ui_hardcode_guard.test.ts` now guards the affected SidePanel and IslandView literals so these user-facing English strings do not return in source. `IslandView.accessibility.test.ts` and `IslandView.bounds.test.ts` verify Japanese default labels and English fallback when the active locale is switched.
- E2E route: `e2e/canvas_focus_order.spec.ts` loads a deterministic card/island document at 960px width, selects a card with keyboard Enter, tabs to the selected-card side-panel action, focuses an island with keyboard activation, verifies the Japanese island-editor labels, and tabs to the selected-island action.
- Verification:
  - bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit`: Pass.
  - bundled `node.exe .\node_modules\vitest\vitest.mjs run`: Pass, 160 files / 734 tests.
  - bundled `node.exe .\node_modules\playwright\cli.js test e2e/canvas_focus_order.spec.ts e2e/polygon_vertex_edit.spec.ts e2e/polygon_autofit_qa_boundary.spec.ts --reporter=line`: Pass, 6 tests.
  - bundled `node.exe .\node_modules\playwright\cli.js test --reporter=line`: Pass, 32 tests.
- Task status adjustment: T3 is covered for representative card selection, island selection, side-panel focus reachability, header panel focus return, and polygon edit handles. It remains open only for advanced panel-specific focus paths and slow-environment breadth outside the currently instrumented API, diagnostics, and review-pack export flows.

## 17) Evidence update 2026-05-31: public acceptance and diagnostics sync

- Documentation route:
  - `04_Documentation/acceptance_check.md` now names the representative viewport set as `390px / 768px / 960px / 1440px` and adds a large-document confirmation flow for search, selection, display switching, share preflight, diagnostics, and review-pack export.
  - `04_Documentation/diagnostics.md` now explains how to record large-document and slow-environment symptoms for search, view switching, share preflight, diagnostics, review-pack export, and diff calculation.
- Completion decision:
  - T2 is covered by `e2e/large_document_operability.spec.ts` with a deterministic 120-card / 12-island / 119-edge fixture.
  - T3 is covered by the viewport matrix, Share/View panel fit checks, canvas selection focus checks, and polygon keyboard/mouse checks.
  - T4 is covered by `e2e/ops_recovery_guidance.spec.ts` for API load failure, save failure, slow diagnostics cancellation, slow review-pack export cancellation, and slow review diff cancellation.
  - T5 is covered by the public acceptance and diagnostics documentation updates above.
- Residual breadth:
  - Exhaustive advanced-panel focus traversal remains outside this issue and should stay in the broader E2E expansion backlog (`QA-E2E-USE-01`) rather than blocking the representative productization gate.

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。


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
- [ ] `DecisionStatus=Fixed` の要求のみでACが評価可能（PendingはDecision Queueへ退避済み）。
- [ ] 依存が `契約依存`（schema/api/policy/ops）と `実装依存`（UI/Backend/E2E）に分離されている。
- [ ] Validation plan のコマンドがこのIssue本文だけで再実行可能。

### Phase 5-6: Verify / Proceed 引き継ぎ条件
- Verify合格条件: 価値仮説とACの1対1追跡が可能で、非検証要件が残っていない。
- Proceed条件: 実装ストリームが「どのACをどのテストで満たすか」を追加解釈なしで決定できる。
- フェイルセーフ: 上流価値定義との矛盾・非検証要件・競合編集を検出した場合はOpen化を停止する。

## Open化判定メタ（Draft gate解除条件）

### Open化に必要な最小条件（全件必須）
- [ ] O-OPEN-01: `Owner` が `TBD` ではなく、実行責務者（個人またはロール）に確定している。
- [ ] O-OPEN-02: 依存Issue/ADRごとに `依存待ち理由` と `再開条件` が1:1で明示されている。
- [ ] O-OPEN-03: `Acceptance criteria` と `Validation plan` が `Expected verification level` と一致している。
- [ ] O-OPEN-04: docs-only範囲外の要求が本文に混入していない（本memoの範囲と矛盾しない）。

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

- Assessment scope: 計画層のreadiness確認のみ。`Status: Draft` は維持し、追加実装や04文書更新はこの追記では行わない。
- Gate result: Draft維持。`DecisionStatus=Fixed` だが `Owner: TBD` が残る。2026-05-22の証跡で大きく前進した一方、advanced panel固有のfocus経路と遅延環境の幅は未完了。
- Proposed RACI: R=Product UX Stream Lead（未割当）, A=Productization Program Owner, C=Frontend Lead / QA Lead / Platform Architecture Owner, I=Documentation Maintainer。CodexはOwner確定までissue本文と証跡パックの整備を支援する。
- O-OPEN status:
  - O-OPEN-01: Blocked. `Owner` が `TBD` のため、実行責務者をロールまたは個人で確定する必要がある。
  - O-OPEN-02: Partial. `ADR-0031`、responsive overlap、pointer/keyboard flowの依存は明示済みで、既存証跡もあるが、残タスクの再開条件を「advanced panel focus」「slow worker/API breadth」「docs sync」に分ける必要がある。
  - O-OPEN-03: Partial. 既存E2Eは narrow viewport、canvas focus、recovery guidance を確認済みだが、Expected verification level=e2eに対して残る操作範囲が明示されている。
  - O-OPEN-04: Pass for assessment. この追記はOpen判定の整理であり、docs-only範囲外の実装要求を追加しない。
- 契約依存:
  - `ADR-0031`: 製品化画面での主要領域、情報優先度、レスポンシブ境界。
  - `QA-MONKEY-06`: ヘッダー、ツールバー、右パネルの狭幅重なり回帰。
  - `UX-OPERABILITY-01`: マウス操作とキーボード操作の代表フロー評価。
- 実装/証跡依存:
  - advanced panelを開く、編集する、閉じる、元の作業面へ戻るfocus経路のE2E。
  - slow worker/API、遅いexport、キャンセル後再実行を含む遅延環境の代表E2E。
  - `04_Documentation/acceptance_check.md` との同期確認。
- Next action:
  - 既存の2026-05-22証跡を残しつつ、残タスクを3区分に分けて証跡名と完了条件を追記する。
  - Owner確定と残証跡の保存先固定が完了するまではOpen化しない。

## Open Gate Reassessment 2026-05-27: stewardship and evidence route fixed

- Assessment scope: 計画層のOpen化判定。これはレスポンシブ/大規模文書/低速環境の完了判定ではなく、残タスクの証跡名と完了条件を固定して実装・E2Eへ進めるための更新である。
- Gate result: **Open**. `DecisionStatus=Fixed`、OwnerはCodexの証跡整備責務として確定し、最終リリース判断はProductization Program Ownerの承認に残す。
- RACI:
  - R: Codex (Product UX evidence steward)
  - A: Productization Program Owner
  - C: Frontend Lead / QA Lead / Platform Architecture Owner
  - I: Documentation Maintainer
- O-OPEN status:
  - O-OPEN-01: Pass. OwnerはCodexに確定し、最終説明責任はProductization Program Ownerに分離した。
  - O-OPEN-02: Pass. 契約依存は`ADR-0031`、`QA-MONKEY-06`、`UX-OPERABILITY-01`、実装/証跡依存はadvanced panel focus、slow worker/API breadth、docs syncに分離した。
  - O-OPEN-03: Pass. `Expected verification level=e2e`に対し、`header_toolbar_layout.spec.ts`、`large_document_operability.spec.ts`、`canvas_focus_order.spec.ts`、`ops_recovery_guidance.spec.ts`を代表経路として使う。
  - O-OPEN-04: Pass. 本更新はOpen化と証跡経路の固定であり、実装変更や04文書変更を直接要求しない。
- Fixed evidence route:
  - viewport matrix and panel focus return: `e2e/header_toolbar_layout.spec.ts`
  - synthetic large document search/panel/export: `e2e/large_document_operability.spec.ts`
  - card/island/selection-panel focus order: `e2e/canvas_focus_order.spec.ts`
  - API/save/diagnostics/review-pack/review-diff slow or failure recovery: `e2e/ops_recovery_guidance.spec.ts`
  - 公開文書同期: `04_Documentation/acceptance_check.md`, `operations.md`, `diagnostics.md`
- Remaining completion buckets:
  - Advanced panel focus breadth: panel固有の開く、編集する、閉じる、元へ戻る経路を追加または既存E2Eへ統合する。
  - Slow worker/API breadth: diagnostics/review-pack/review-diff以外の長時間処理が追加された場合、progress/cancel/retryを同じ証跡形式で追加する。
  - Docs sync: 代表viewport、キーボード操作、キャンセル後復帰の説明とスクリーンショットを公開文書へ同期する。
- Proceed rule:
  - 実装PRでは、変更がviewport、focus、large document、slow/failure recoveryのどれに影響するかを分類し、対応E2Eまたは明示的な未実施理由を添付する。
  - Product shipmentは本Issue OpenだけではGoにしない。残Completion bucketが閉じた時点で`PRODUCT-QA-01`へ戻す。

## Evidence Refresh 2026-06-06: current-main large-document and recovery rerun

- Candidate: `origin/main@6a4aef91558800da26232c953634da11a60c8535`.
- Reviewer: Codex.
- Scope: current-main browser automation rerun for large-document operability and adjacent slow/failure recovery coverage. This is an evidence refresh only; it does not change runtime behavior, UI copy, SafeMode/share-export policy, diagnostics policy, public documentation, issue status, or release authority.
- Local execution:
  - Bundled Node.js started Vite directly on `127.0.0.1:4173` because this Codex host did not expose `npm` on PATH.
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/large_document_operability.spec.ts e2e/ops_recovery_guidance.spec.ts --reporter=line` -> pass, 6 tests.
- Covered user operations:
  - Load a deterministic 120-card / 12-island / 119-edge document at 768px width.
  - Search for `rare-signal-87`, hide non-matches, and confirm the matching card remains visible.
  - Open View and Share & Reproduce panels without fixed-panel viewport overflow.
  - Export a review bundle and confirm `diagnostics.md` includes `connectivityScore`.
  - Exercise API load failure, save failure, slow diagnostics cancellation, slow review-pack export cancellation, and slow review-diff cancellation at 390px width.
- Human follow-ups:
  - Keep real Chrome visual acceptance, physical keyboard review, and screen-reader acceptance human-owned.
  - Keep automated support bundle generation outside this issue; it remains split to `PRODUCT-OPS-02` and requires policy review/ADR if the product scope changes.

