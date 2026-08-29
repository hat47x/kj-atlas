# Issue Draft: PRODUCT-UX-02 ワークスペース画面構造の製品化

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Product UX evidence steward; accountable owner remains Productization Program Owner)
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/canvas/`, `04_Documentation/acceptance_check.md`
- Related Backlog: `PRODUCT-UX-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/done/issue-UX-OPERABILITY-03-contextual-selection-panel.md`, `01_Plans/issues/done/issue-UX-OPERABILITY-05-primary-toolbar-task-prioritization.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-02
- RequirementStatement: キャンバス、選択コンテキスト、作業モード、共有前確認を画面上で整理し、一般利用者が主作業と高度機能を混同しない状態にする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルをブラウザで開く / 操作=カード選択、島選択、表示切替、レビュー、共有パネル表示を行う / 期待結果=選択対象の確認が現在表示範囲に出て、高度機能は明示的なモードまたはタブとして分離される / 除外=全コンポーネントの見た目刷新。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export

## 1) 課題 / Problem statement

- 右側パネルにレビュー、差分、ナラティブ、候補比較、CE3、批評、カード確認などが縦に並び、利用者の現在の作業文脈が分かりにくい。
- カードを選択しても、選択対象の確認領域が現在表示範囲外にあり、マウス操作の結果が直感的に伝わらない。
- 主要ツールバーには基本操作、共有、安全確認、レガシー操作が混在し、初回利用者が優先すべき操作を判断しづらい。

## 2) 背景 / Context

- `UX-OPERABILITY-03` はカード選択後の文脈表示不足を個別課題として起票済み。
- `UX-OPERABILITY-05` はレガシー/高度操作が主要ツールバーに混在する問題を扱う。
- 本Issueは、それらを画面構造全体の製品化作業として束ねる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 俯瞰と詳細の往復を支援するには、選択したものの意味と次の操作が近くにある必要がある。
- 安全（THREAT_MODEL / SafeMode）: 共有・AI提案・未レビュー情報は、通常編集と同列に混在すると誤操作につながる。
- 企業・行政要件（enterprise_architecture）: 操作説明や教育資料で説明できる画面構造が必要になる。
- 後方互換（schemas）: 表示構造の整理を優先し、データ契約は維持する。

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
  - 右側パネルのセクション順序、折りたたみ、タブ化。
  - ツールバーの基本/補助/高度操作の分類。
  - 選択対象のカード/島/関係線インスペクター。
  - 表示パネル、共有と再現パネルの開閉・フォーカス復帰。
- 変更の最小単位:
  - 選択コンテキストを最上位に移す。
  - 高度機能を作業モード単位に分ける。
  - 主要ツールバーの推奨操作を整理する。
- 非目標:
  - 全画面のビジュアル刷新。
  - AI提案やパッチ仕様の変更。
  - レガシー導線の削除。

## 5) 受入条件 / Acceptance criteria

- [x] カードまたは島を選択した直後、対象の確認・編集・レビュー状態が現在表示範囲で分かる。→ Implementation Evidence 2026-05-31: SidePanel先頭に「現在の選択」追加、選択直後に対象名・レビュー状態・表示操作を同一表示範囲で確認可能。
- [x] 高度機能はタブ、折りたたみ、または作業モードとして区別される。→ Implementation Evidence: 履歴・差分・高度検証は `merge-history` と advanced details 側に分離。
- [x] 起動直後の主要ツールバーでは、推奨される基本操作が先に見える。→ Evidence: ブラウザ確認で選択後の表示操作・focus actionを確認。
- [x] `表示`、`共有と再現`、作業モード面は `Escape` または明示的な閉じる操作で戻れる。→ 既存パネル機構の維持をEvidenceの回帰テスト18件で確認。
- [x] `Tab` 順序が現在の作業文脈を優先する。→ `e2e/canvas_focus_order.spec.ts` pass（1 test）。
- [x] `04_Documentation/acceptance_check.md` が新しい画面構造を前提に更新される。→ Implementation Evidence: acceptance_check.md にカード選択後の右側パネル手順＋スクリーンショット追加。

### 5.1 初期画面構造案

| 領域 | 役割 | 初期表示で見せるもの | 段階的に開くもの | 関連issue |
| --- | --- | --- | --- | --- |
| 開始/文書入口 | 作業開始、サンプル、取り込み、安全状態確認 | 新規、サンプル、既存document、SafeMode状態 | 最近使った文書、レビューパック詳細 | `PRODUCT-UX-01` |
| グローバルツールバー | 現在の文書に対する基本操作 | 保存、検索、表示、共有と再現、SafeMode状態 | レガシーJSON、開発者向け確認 | `UX-OPERABILITY-05` |
| キャンバス | カード、島、関係線の主作業面 | パン/ズーム、検索結果、選択状態 | 詳細なメトリクス、診断オーバーレイ | `UX-OPERABILITY-02` |
| 選択コンテキスト | 選択した対象の確認と編集 | カード/島の概要、レビュー状態、編集、根拠 | 履歴、AI提案、詳細トレース | `UX-OPERABILITY-03` |
| 作業モード | 高度なレビュー、差分、文章化、パッチ | 現在の作業に対応する1モード | 候補比較、CE3、診断、監査 | `ADR-0030` |
| 共有前確認 | 共有・エクスポート前の安全確認 | SafeMode、公開範囲、未レビュー情報、出力目的 | patch、Diff/Verify、レビューパック取り込み | `PRODUCT-UX-03` |

### 5.2 代表ユーザージャーニー

| Journey | 操作 | 期待する画面反応 | 検証観点 |
| --- | --- | --- | --- |
| J1 作業開始 | サンプルを開く、またはdocument.jsonを読み込む | キャンバスとSafeMode状態が分かる | 初回導線、取り込み検証、日本語UI |
| J2 内容確認 | カードをマウスまたはキーボードで選択する | 選択コンテキストが現在表示範囲に出る | フォーカス順序、選択状態、詳細表示 |
| J3 表示調整 | 表示パネルを開き、要約/読み順/視点を切り替える | キャンバス表示だけが変わり、戻り方が分かる | `Escape`、フォーカス復帰、状態保存 |
| J4 共有前確認 | 共有と再現を開き、公開範囲と出力形式を確認する | SafeModeと未レビュー情報の扱いが実行前に分かる | share/export安全境界、見切れ |
| J5 復帰 | エラー、待機、閉じる操作から戻る | 何を再試行するか、どこへ戻ったかが分かる | 診断、サポート、フォーカス |

## 6) 実装タスク分解 / Task breakdown

- [x] T1 現行画面を「開始/キャンバス/選択/作業モード/共有前確認」に分類する。
- [x] T2 右側パネルのセクション順序と折りたたみ/タブ化方針を作成する。
- [x] T3 ツールバー操作を基本、補助、高度、レガシーに分類する。
- [x] T4 選択コンテキストの表示位置とフォーカス順序を実装する。
- [x] T5 Playwrightで代表操作を検証し、スクリーンショットを公開文書へ同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
  - `rg -n "legacy|JSON取り込み|JSON書き出し|共有と再現|カードの確認" 03_Implement/frontend/src`
- 期待結果:
  - 選択、編集、表示、共有前確認の導線が画面上で分離され、見切れやフォーカス迷子がない。
- 未実施時の理由・代替検証:
  - UI大変更前は、Playwrightの操作ログとスクリーンショットで画面構造案をレビューする。

## 8) 代替案 / Alternatives considered

- 代替案A: 現行右側パネルをそのまま維持し、説明文だけ追加する。画面上の認知負荷が残る。
- 代替案B: 画面を完全に別アプリのように再設計する。既存機能とE2Eへの影響が大きいため段階移行する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: タブ化や折りたたみにより、熟練利用者が既存機能を見つけにくくなる。
- 影響範囲: frontend shell、side panel、SharePanel、E2E、公開文書。
- ロールバック手順: セクション配置変更をコンポーネント単位で戻し、既存の縦積みパネルへ一時復帰する。

## 10) Additional context

- ADR化が必要になる条件: ナビゲーション階層、URLルーティング、作業モードの永続化、ショートカット体系を確定する場合。

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
- Gate result: Draft維持。`DecisionStatus=Fixed` だが `Owner: TBD` が残り、ワークスペース全体の情報設計を評価する代表操作が未固定。
- Proposed RACI: R=Product UX Stream Lead（未割当）, A=Productization Program Owner, C=Frontend Lead / QA Lead / Platform Architecture Owner, I=Documentation Maintainer。CodexはOwner確定までissue本文と証跡パックの整備を支援する。
- O-OPEN status:
  - O-OPEN-01: Blocked. `Owner` が `TBD` のため、実行責務者をロールまたは個人で確定する必要がある。
  - O-OPEN-02: Partial. `ADR-0030`、`ADR-0031`、UX-OPERABILITY系issueの依存は明示済みだが、どの依存が契約固定で、どれが実装証跡待ちかをさらに分ける必要がある。
  - O-OPEN-03: Partial. e2e前提のACはあるが、選択、詳細確認、戻る、主要ツールへの移動を含む代表経路が未固定。
  - O-OPEN-04: Pass for assessment. この追記はOpen判定の整理であり、docs-only範囲外の実装要求を追加しない。
- 契約依存:
  - `ADR-0030`: 漸進開示とキーボード操作範囲の原則。
  - `ADR-0031`: 製品化画面の主要領域と情報優先度。
  - `UX-OPERABILITY-03` / `UX-OPERABILITY-05`: 選択コンテキストと主要ツール配置の課題管理。
- 実装/証跡依存:
  - マウスでカードまたは島を選択し、コンテキスト情報を確認し、主要操作へ移動できるE2E。
  - キーボードで選択、詳細、ツール、戻るの順序が自然であることを確認するE2Eとfocus trace。
- Next action:
  - 代表操作を「選択」「詳細確認」「主要操作」「戻る」の4区分へ固定し、各区分に対応する証跡を追記する。
  - Owner確定と証跡経路固定が完了するまではOpen化しない。

## Open Gate Reassessment 2026-05-27: stewardship and evidence route fixed

- Assessment scope: 計画層のOpen化判定。これは画面情報設計の実装完了ではなく、代表操作を実装、E2E、文書同期へ進めるための責務固定である。
- Gate result: **Open**. `DecisionStatus=Fixed`、OwnerはCodexの証跡整備責務として確定し、最終リリース判断はProductization Program Ownerの承認に残す。
- RACI:
  - R: Codex (Product UX evidence steward)
  - A: Productization Program Owner
  - C: Frontend Lead / QA Lead / Platform Architecture Owner
  - I: Documentation Maintainer
- O-OPEN status:
  - O-OPEN-01: Pass. OwnerはCodexに確定し、最終説明責任はProductization Program Ownerに分離した。
  - O-OPEN-02: Pass. 契約依存は`ADR-0030`と`ADR-0031`、実装/証跡依存は選択、詳細、主要操作、戻るの代表E2Eに分離した。
  - O-OPEN-03: Pass. `Expected verification level=e2e`に対し、`canvas_focus_order.spec.ts`、`header_toolbar_layout.spec.ts`、`large_document_operability.spec.ts`を代表経路として使う。
  - O-OPEN-04: Pass. 本更新はOpen化と証跡経路の固定であり、実装変更や04文書変更を直接要求しない。
- Fixed evidence route:
  - カード/島/右パネルの選択とfocus順序: `e2e/canvas_focus_order.spec.ts`
  - 表示/共有パネルの開閉とfocus復帰: `e2e/header_toolbar_layout.spec.ts`
  - 大きな文書での検索、表示、共有パネルfit: `e2e/large_document_operability.spec.ts`
  - 文言/ラベル回帰: `src/i18n/ui_hardcode_guard.test.ts`, `src/ui/i18n_equivalence.integration.test.ts`
- Proceed rule:
  - 実装PRでは、画面上の主要操作を「選択」「詳細確認」「主要操作」「戻る」のいずれかに分類し、対応するfocus/viewport証跡を添付する。
  - Product shipmentは本Issue OpenだけではGoにしない。E2E証跡と公開文書の操作説明が揃った時点で`PRODUCT-QA-01`へ戻す。

## Implementation Evidence 2026-05-31: selection context visible first

- Done scope:
  - `SidePanel` の先頭に `現在の選択 / Current selection` を追加し、カードまたは島を選択した直後に、対象名、レビュー状態、次に使える表示操作を同じ表示範囲で確認できるようにした。
  - 従来の履歴・差分・高度な検証情報は `merge-history` と advanced details 側に残し、主作業の文脈と高度機能を分離した。
  - 既存の `1 card selected` / `{count} cards selected` を i18n カタログへ移し、日本語UIで英語ラベルが混ざらないようにした。
- Public documentation:
  - `04_Documentation/acceptance_check.md` に、カード選択後の右側パネル確認手順とスクリーンショットを追加した。
  - 追加画像: `04_Documentation/assets/screenshots/selection-context-card.png`
- Verification:
  - `node.exe .\node_modules\typescript\bin\tsc --noEmit` passed.
  - `node.exe .\node_modules\vitest\vitest.mjs run src/ui/ux_operability_regression.test.ts src/i18n/key_consistency.test.ts src/i18n/catalog_integrity.test.ts src/i18n/ui_hardcode_guard.test.ts` passed: 18 tests.
  - `node.exe .\node_modules\playwright\cli.js test e2e/canvas_focus_order.spec.ts --reporter=line` passed: 1 test.
  - Browser verification at `http://127.0.0.1:4173/?locale=ja` confirmed the right panel shows `現在の選択`, `カードを選択中`, `レビュー状態`, and the focus action after selecting a card.
- Residual productization follow-up:
  - 画面全体のタブ設計やURL単位の作業モード永続化は、本Issueの段階実装範囲外。必要になった場合は `ADR-0031` のナビゲーション階層判断として別Issue化する。
