# Issue Draft: UX-COMPLEXITY-01 MVP主要価値の前景化と複雑性予算の継続適合

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (UX complexity steward; accountable owner remains Productization Program Owner)
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`, `04_Documentation/acceptance_check.md`
- Related Backlog: `UX-COMPLEXITY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/done/issue-PRODUCT-UX-02-workspace-information-architecture.md`, `01_Plans/issues/done/issue-UX-OPERABILITY-05-primary-toolbar-task-prioritization.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-COMPLEXITY-01
- RequirementStatement: アプリ規模の拡大に伴い機能が増えても、初期表示では MVP の主要価値（カードを書く・並べる・束ねる・つなぐ／曖昧さの保留）が前景化され、高度・企業向け機能は段階開示の背後に留まる状態を、一回限りの再編ではなく継続規律として維持する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルを既定（`KJ_ATLAS_LLM_PROVIDER=none`・詳細トグルOFF）で開く / 操作=初期表示および単一選択直後に見える主要操作を数える / 期待結果=主要操作は MVP 中核（作成・編集・整理・選択確認・保存・共有前確認）に限定され、AI・CE3パッチ・差分・SSO・公開範囲・監査・集約エッジ等は明示的な開示操作（詳細トグル／モード／メニュー）の背後にある / 除外=全画面のビジュアル刷新、機能削除。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export

## 1) 課題 / Problem statement

- 機能は急速に増えており（claimType・holdState・evidence・critique・review・diff・narrative・trace・metrics・diagnostics・AI提案・CE3パッチ・公開範囲・SSO・監査・集約エッジ 等）、個々は妥当でも総体として初期表示の認知負荷が MVP の主要価値を覆い隠す懸念がある。
- ADR-0031（5領域）と PRODUCT-UX-02（ワークスペース再編, Done）は一回限りの構造整理を完了したが、「増え続ける機能に対して前景化を保ち続ける継続規律」と「現行ビルドが ADR-0043 の複雑性予算に適合しているかの定点監査」が独立の追跡課題として未起票である。
- 直近の実装でも緊張が観測されている: 段階開示の機構（`isAdvancedUiEnabled` による SidePanel/SharePanel の高度機能ゲート）が入った一方で、ヘッダーは inline ボタン構成へ戻され（dropdown メニュー廃止）、初期表示の常設要素数（ADR-0043 CB-1/CB-3）への影響が監査されていない。

## 2) 背景 / Context

- 本Issueは新たな設計判断を起こすものではなく、確定済みの上位方針を**継続運用・定点監査の課題**として具体化する。
  - ADR-0043: 複雑性予算（CB-1 既定の静けさ / CB-2 保留の容易さ最優先 / CB-3 純増は置換・包含・モード分離で / CB-4 可逆の明示）。`ux_operability_regression.test.ts` の source-string を実質的な初期表示上限として扱う。
  - ADR-0030: 段階的開示とキーボードスコープ。
  - ADR-0031: 5領域の画面情報設計（入口 / キャンバス / 選択コンテキスト / 作業モード面 / 共有前確認面）。
- MVP の主要価値（前景化対象）: カードの作成・本文編集・削除、島の作成、関係線、選択コンテキストの確認、保存、共有前確認、SafeMode 状態。これらは LLM 非依存で完結する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001 / domain.md）: kj-atlas の価値は「少ない操作で曖昧さを保持できる軽さ」にあり、機能の多さではない。前景化の劣化は価値の核を侵す。
- 安全（THREAT_MODEL / SafeMode）: AI・共有・公開範囲・未レビュー情報が主要操作と同列に並ぶと誤操作・誤共有を招く。段階開示は安全境界でもある。
- 規模拡大（enterprise / scale）: 機能追加が続く前提で、初期表示の上限と前景化を維持する歯止めが必要。
- 後方互換: 表示構造の規律であり、document/view/pack スキーマは変更しない。

## 3.1 依存関係 / Dependencies

- 直前依存: ADR-0043 の複雑性予算、ADR-0031 の5領域、PRODUCT-UX-02 の再編結果。
- 連携先: UX-OPERABILITY-05（主要ツールバー優先度）、PRODUCT-QA-01（リリース品質ゲート：複雑性予算違反を品質ゲートで捕捉する整合先）。
- ブロッカー条件: 上位ADR（0030/0031/0043）に矛盾が生じる場合は実装を開始しない。

## 3.2 非目標 / Non-goals

- 全画面のビジュアル刷新。
- 既存機能（AI・パッチ・差分・レガシーimport/export 等）の削除。
- document/view/pack スキーマの変更。
- ADR-0030/0031/0043 の再決定（本Issueはそれらの**運用・監査**であり再決定ではない）。
- PRODUCT-UX-02 の AC の再定義（重複禁止。本Issueは継続規律と定点監査という非重複の角度を扱う）。

## 4) 提案する解決策 / Proposed solution

- 変更の最小単位:
  - 現行ビルドの「初期表示（前景）要素」と「段階開示（高度）要素」の分類インベントリを `04_Documentation` または本Issueに記録し、ADR-0031 の5領域 × ADR-0043 CB-1 に対して適合を判定する。
  - MVP 主要価値（作成・編集・整理・選択確認・保存・共有前確認）が初期表示で前景化され、AI/CE3/差分/SSO/公開範囲/監査/集約エッジ等が明示的開示の背後にあることを e2e の source-string アンカーで固定する。
  - ヘッダー inline 化の純増影響（CB-3）を UX-OPERABILITY-05 と整合のうえ判定し、初期表示の常設操作数の上限を `ux_operability_regression.test.ts` のアンカーとして明文化する。
  - UI/操作を増やす今後の変更に、ADR-0043 の複雑性予算1行自己申告を必須運用とする（軽量・ADR-0039 準拠）。
- 非目標: 上記「3.2 非目標」を正本とする。

## 5) 受け入れ条件 / Acceptance criteria

- AC-1: 現行ビルドの初期表示要素／段階開示要素の分類が文書化され、ADR-0031 5領域 × ADR-0043 CB-1 に照らした適合判定（適合／要是正）が残る。
- AC-2: 既定（詳細OFF・provider=none）で、MVP 主要価値の操作が前景化され、高度・企業向け機能は明示的開示操作の背後にあることが e2e で固定される（PRODUCT-UX-02 の再編ACとは重複しない、初期表示インベントリの観点）。
- AC-3: UI追加変更に対する複雑性予算1行自己申告の運用が `01_Plans` または PR テンプレに定義され、`ux_operability_regression.test.ts` の初期表示アンカーが実質上限として参照される。
- AC-4: 初期表示への純増（CB-3）が必要な場合、理由が当該変更のIssue/PRに記録される。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（本Issueはガバナンス/監査であり実行時UIを追加しない） / 保留操作の距離=不変 / 取り消し導線=N/A

## Traceability

- Related: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
- Related: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Related: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- Related: `01_Plans/issues/done/issue-PRODUCT-UX-02-workspace-information-architecture.md`
- Related: `01_Plans/issues/done/issue-UX-OPERABILITY-05-primary-toolbar-task-prioritization.md`
- Related: `ROADMAP.md`
- Derived-from: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`

## 完了記録（2026-06-23）

### 初期表示／段階開示インベントリ

| ADR-0031 の領域 | 初期表示で前景化する内容 | 「詳細」の背後に置く内容 | ADR-0043 判定 |
| --- | --- | --- | --- |
| 入口 | ファイル、最近の文書、開く | 旧式JSONはファイルメニュー内 | 適合 |
| キャンバス | 新規カード、島を作成、削除、保存 | AIによる配置提案 | 適合 |
| 選択コンテキスト | 選択対象、レビュー状態、保留、違和感 | トレース、メトリクス、診断、HIL-RS | 適合 |
| 作業モード面 | SafeMode、探索／レビュー／要約、表示、検索 | 高度な表示・証拠オーバーレイ等は表示パネル内 | 適合 |
| 共有前確認面 | 共有と再現、SafeMode、公開範囲、未レビュー情報、出力形式 | パッチ、差分、詳細な出力設定 | 適合 |

### 実装と検証

- `App.tsx` に `data-ui-complexity-tier` と `data-ui-core-action` を付与し、見た目を変えずに前景／段階開示の境界を機械判定可能にした。
- `ux_operability_regression.test.ts` で前景領域、開示操作、高度機能、主要4操作のアンカーを固定した。
- `complexity_budget_foregrounding.spec.ts` で既定時に高度機能が非表示であること、主要4操作が見えること、「詳細」の開閉で可逆に戻ることを実ブラウザで固定した。
- `04_Documentation/acceptance_check.md` に一般利用者が通常表示と詳細表示を確認する手順を追加した。
- `.github/pull_request_template.md` に UI 変更時の複雑性予算自己申告を追加した。

### 受け入れ条件の判定

- AC-1: Pass。5領域のインベントリと CB-1 適合判定を上表へ記録した。
- AC-2: Pass。既定表示と段階開示を Playwright で固定した。
- AC-3: Pass。PRテンプレの自己申告と source-string 回帰アンカーを追加した。
- AC-4: Pass。純増時の理由記載をPRテンプレで要求した。

複雑性予算: 初期表示への純増=なし / 保留操作の距離=不変 / 取り消し導線=あり（「詳細」を再度選択）

## E2E追認 2026-06-29: UX-NAV-01 AC-2 equivalent

- 利用者指定の `UX-NAV-01 AC-2（高度機能パネル抽出）` は、本Issueの AC-2 と `UX-OPERABILITY-03` の選択コンテキスト段階開示契約として扱う。
- 追加E2E `selection context keeps advanced panel extracted behind explicit disclosure` により、既定表示では高度パネルが出ないこと、明示的に「詳細」を選ぶまで `[data-panel-group="advanced"]` が現れないこと、表示後も初期 `aria-expanded=false` であることを確認した。
- 選択コンテキストの基本情報（選択対象、レビュー状態、違和感）は高度パネルの開閉中も維持されることを確認した。
- 結果: 2026-06-29 の対象Playwrightセットで **10 passed**。
- 判定: AC-2 は代表操作として **Pass**。ただし、画面全体の情報設計や実機アクセシビリティ承認は別ゲートに残る。

## E2E追認 2026-07-04: 右パネルの詳細フィルタ / Guided Flow の段階開示

- UIカタログで残課題として扱っていた CB-3（ドメイン状態フィルタの二重化、Guided Flow の常設リーク）について、右側パネル側の詳細ドメインフィルタと Guided Flow を `isAdvancedUiEnabled` の背後へ移した。
- 既定表示では選択コンテキスト先頭の「現在の選択」、文書状態サマリ、基本編集/レビュー導線を優先し、詳細な絞り込み・Guided Flow は「詳細」ON時にだけ表示する。
- `詳細` をOFFにした場合、Guided Flow が見えないまま有効に残らないよう `setGuidedFlowEnabled(false)` で状態を閉じる。
- 回帰固定: `ux_operability_regression.test.ts` に `domain-detail-filters` / `guided-flow` の advanced-content 契約を追加し、`complexity_budget_foregrounding.spec.ts` で既定OFF・詳細ON・再OFFの可視性を確認した。
- 結果: 2026-07-04 の対象検証で `tsc --noEmit`、`vitest run src/ui/ux_operability_regression.test.ts src/ui/DomainStateFilterBar.test.ts`、`playwright test e2e/complexity_budget_foregrounding.spec.ts --reporter=line` が通過。
- ADR影響: ADR-0043 の既存方針（CB-1/CB-3/CB-4）に沿う段階開示の是正であり、新ADRは不要。
