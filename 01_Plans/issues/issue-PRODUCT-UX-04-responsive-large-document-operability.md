# Issue Draft: PRODUCT-UX-04 小画面・大規模文書・低速環境での操作性確認

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `04_Documentation/acceptance_check.md`, `04_Documentation/diagnostics.md`
- Related Backlog: `PRODUCT-UX-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-QA-MONKEY-06-header-toolbar-responsive-overlap.md`, `01_Plans/issues/issue-UX-OPERABILITY-01-pointer-keyboard-flow-review.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-04
- RequirementStatement: 製品化対象として、狭い画面、大きな文書、低速環境でも主要操作が見切れず、待機状態と復帰方法が理解できる状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルと大きめの文書を複数viewportで開く / 操作=検索、選択、表示切替、共有前確認、診断を実行する / 期待結果=見切れ、重なり、反応なしに見える状態、フォーカス迷子がない / 除外=モバイル専用ネイティブUI。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: `ADR-0031`

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
- [ ] T2 大きめfixtureまたは既存サンプル拡張を用意する。
- [ ] T3 主要パネルのレイアウト崩れ、長いラベル、フォーカス順序を検証する。
- [ ] T4 待機表示、エラー表示、診断導線を確認する。
- [ ] T5 E2Eと公開文書の受け入れ確認を更新する。

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
| Header panel keyboard flow | `e2e/header_toolbar_layout.spec.ts` | Pass at 1440px / 768px: focus Share/View trigger, Enter opens dialog, Escape closes, focus returns to trigger. | canvas edit-mode focus-order breadth remains under this issue. |
| Canvas mouse and keyboard operability | `e2e/polygon_vertex_edit.spec.ts`, `e2e/polygon_autofit_qa_boundary.spec.ts` | Pass: mouse drag, arrow-key nudge, Shift+arrow large nudge, Delete removal, self-intersection guard. | broader canvas edit-mode focus order remains under this issue. |
| Full frontend E2E | bundled Playwright full suite | Pass: 21 tests | large-document fixture and slow/backend-recovery scenarios remain outside the current suite. |
| Frontend regression | full Vitest | Pass: 160 files / 732 tests | does not replace browser viewport evidence. |

### Task status adjustment

- T3 remains open but narrowed: layout collapse, mouse hit-testing, polygon keyboard nudge/removal, 768px/1440px header-panel fit, and Share/View keyboard open-close focus return are fixed for covered flows; broader canvas edit-mode focus order and large-document interaction evidence remain.
- T5 remains open: public acceptance documentation should be updated after the full viewport/large-document/slow-environment matrix is recorded.

## 12) Evidence update 2026-05-22: header panel keyboard and viewport matrix

- Implementation route: `App.tsx` now moves focus into the View dialog when it opens and restores focus to the View trigger when Escape closes it. This aligns View with the existing Share dialog focus-return behavior.
- E2E route: `e2e/header_toolbar_layout.spec.ts` now checks 1440px, 1280px, 920px, 768px, and 390px layout fit, plus keyboard Enter/Escape focus return at 1440px and 768px.
- Verification:
  - bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit`: Pass.
  - bundled `node.exe .\node_modules\playwright\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`: Pass, 7 tests.
- Remaining gap: this closes the header/share/view panel portion of the viewport matrix. Large-document fixtures, slow/backend-recovery UX, and canvas edit-mode keyboard semantics remain open.

## 13) Evidence update 2026-05-22: polygon edit keyboard operation

- Implementation route: `PolygonEditLayer.tsx` now makes vertex handles keyboard focusable and supports Arrow-key nudging, Shift+Arrow larger nudging, and Delete/Backspace removal. `CanvasShell.tsx` converts screen-step keyboard deltas into world coordinates using the current zoom before committing the vertex move.
- E2E route: `e2e/polygon_vertex_edit.spec.ts` now verifies focus on a vertex handle, ArrowRight + Shift+ArrowDown movement, Delete removal of another vertex, and persistence through legacy document JSON export.
- Verification:
  - bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit`: Pass.
  - bundled `node.exe .\node_modules\playwright\cli.js test e2e/polygon_vertex_edit.spec.ts --reporter=line`: Pass, 2 tests.
- Remaining gap: the polygon edit primitive is now keyboard-operable; full canvas focus-order coverage across card selection, island selection, panels, and edit handles remains open.

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

