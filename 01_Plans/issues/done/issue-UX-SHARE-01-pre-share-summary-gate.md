# Issue Draft: UX-SHARE-01 共有直前サマリ（未レビュー・違和感・矛盾の既定非表示を明示）

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-SHARE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 憲章・反スコアリング）, `01_Plans/issues/done/issue-PRODUCT-UX-03-safe-share-export-flow.md`（Done・目的起点フローの強化であり再決定ではない）, `01_Plans/issues/done/issue-DOMAIN-TRACE-01-serial-number-and-source-provenance.md`（出典トグルの所有元）, `01_Plans/issues/done/issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md`（起票者などの主体メタ境界）
- Norms: `DOM-SHARE-03`（矛盾k件の明示）, `DOM-SHARE-02`（価値記述の「保留」も対象だが、サマリの3件数自体は保留を直接数えていない）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-SHARE-01
- RequirementStatement: 共有・書き出しの直前に「未レビュー n件・違和感 m件・矛盾 k件は既定で非表示（SafeMode）」であることを1枚のサマリで明示し、利用者が保持中の情報の露出範囲を確認してから出力できるようにする。件数は所在提示であり評価ではない（反スコアリング）。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=未レビュー・違和感・矛盾を含む文書で「共有と再現」を開く / 操作=書き出しを実行しようとする / 期待結果=直前サマリに3種の件数と「既定で非表示」の説明が表示され、戻って編集または続行を選べる。準備度・スコア・%は表示されない / 除外=共有フロー全体の再設計（PRODUCT-UX-03 Done の再決定）、公開範囲・粒度選択そのものの変更、出典参照トグル（DOMAIN-TRACE-01 所有）。
- SecurityGateImpact: SafeMode / share-export（安全境界の明示性強化。境界自体は不変・弱めない）

## 1) 課題 / Problem statement

- 現行の共有前チェック（PRODUCT-UX-03）は SafeMode・公開範囲・未レビュー情報の設定確認を提供するが、**出力直前の要約1枚**（何件が既定で外れるか）が無く、保持中の曖昧さ・対立が「静かに落ちる」ことに利用者が気づきにくい。
- 壁打ち Round 4（拡張提案 §領域5）で設計確定: サマリは所在提示のみで評価語・スコアを使わない。

## 2) 背景 / Context

- ADR-0048 D3 憲章「未レビューの自動承認禁止・対立の自動解消禁止」の共有面での運用形。DOMAIN-EXPR-04（In Progress）の矛盾状態・narrative grounding summary と整合させる。
- PRODUCT-UX-03（Done）の「目的起点の共有フロー」「preflight 内容」は再決定しない。本Issueは直前サマリ1枚の**挿入**のみ。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-01/P-03、判断軸3/4）: 保留・対立・未レビューの保持を共有時にも可視化し、露出判断を人間に返す。
- 安全: 誤共有リスクの低減。境界は不変で明示性のみ強化。
- 規模拡大: 文書が大きいほど「静かに落ちる」件数が増え、サマリの価値が上がる。
- 後方互換: スキーマ変更なし。

## 3.2 非目標 / Non-goals

- 共有フロー全体・preflight 構成の再設計。公開範囲/粒度モデルの変更。準備度スコア等の導入（反スコアリング）。出典参照トグル（DOMAIN-TRACE-01）。起票者・作成者・最終更新者などの主体メタ同梱判断（CARD-META-UI-01）。

## 4) 提案する解決策 / Proposed solution

- 書き出し実行の直前に確認サマリを1枚挿入: 「未レビュー n件・違和感 m件・矛盾 k件は既定で非表示になります」＋戻る/続行。SafeMode 状態を併記。
- 件数はリンクとして該当フィルタへ誘導可能（戻って確認する導線）。評価語（不足/未達/危険等）は使わない。
- a11y: 開いたらサマリ見出しへフォーカス、フォーカストラップ、Esc で取消しトリガへ復帰（Round 4 §a11y 仕様に従う）。
- i18n（ja/en）。
- 出典参照トグル（`DOMAIN-TRACE-01`）と、起票者などの主体メタ同梱（`CARD-META-UI-01`）は別項目として扱う。起票者メタは個人/組織識別になり得るため、UX-SHARE-01の直前サマリだけで同梱可にしない。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: 3種の件数と「既定で非表示」の説明が出力直前に表示され、戻る/続行が選べることが e2e で固定される。
- [x] AC-2: 準備度・スコア・%・評価語がサマリに存在しない。
- [x] AC-3: SafeMode 既定ON・既存 preflight（PRODUCT-UX-03）の内容が非回帰。
- [x] AC-4: フォーカス初期位置・トラップ・Esc 復帰が仕様どおり（UX-OPERABILITY-04 契約整合）。
- [x] AC-5: 件数ゼロの文書ではサマリが簡潔化（または省略）され、共有を不必要に妨げない。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 件数集計（既存の domain 状態導出を再利用）。
- [x] T2 直前サマリ UI＋フォーカス契約＋i18n。
- [x] T3 件数→フィルタ誘導リンク（「戻って確認する」ボタンが同じ役割を果たすため独立実装は不要と判断。詳細は完了記録参照）。
- [x] T4 e2e（表示・非スコア・非回帰・ゼロ件時）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`
- SharePanel 既存 e2e（PRODUCT-UX-03 系）の非回帰確認。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（共有操作時のみ1枚） / 保留操作の距離=改善（保持中の情報の露出判断が共有直前に1操作で確認可能） / 取り消し導線=あり（戻って編集で可逆）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/issues/done/issue-PRODUCT-UX-03-safe-share-export-flow.md`, `issue-DOMAIN-EXPR-04-evidence-claim-contradiction-review.md`, `issue-DOMAIN-TRACE-01-serial-number-and-source-provenance.md`
- Related: `01_Plans/issues/done/issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md`
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（§領域5・2026-07-04 版）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 完了記録 2026-07-09（Claude Code）

### 要件の再定義

- **ゲート対象の確定**: 「共有と再現」内の複数の書き出しボタン（PNG/SVG/view.json等）のうち、レビューパック本体（Export bundle .zip）のみをゲート対象とした。単一ピクセル/座標の書き出しは矛盾・違和感・未レビュー状態を含まないため、issue が想定する「保持中の曖昧さ・対立が静かに落ちる」リスクの対象外と判断。
- **T3（件数→フィルタ誘導リンク）を独立実装しない判断**: 5つのACのいずれもフィルタ誘導リンクを要求していない（ACには「戻る/続行」のみが明記）。加えて「戻る」ボタン自体が既にドキュメントへ戻って確認する導線として機能しており、個別カード/島への誘導は対象が一意に定まらない集計値（件数の合計）のため、具体的なジャンプ先を持たせると誤誘導になりかねない。既存の「戻る」で要件を満たすと判断し、独立した実装は行わなかった。
- **カウントの再利用**: 新規集計ロジックは追加せず、既存の `domainExpressionSummary.unreviewedCards/unreviewedIslands/critiqueTargets/contradictionLinks`（PRODUCT-UX-03で導入済み）をそのまま参照。schemaやAPIの変更は一切なし。

### 実装

- **ゲート**: SharePanel の「Export bundle」ボタンのonClickを変更し、直接 `onExportBundleZip` を呼ぶ代わりに、3種の合計が全てゼロなら従来どおり即時実行（AC-5）、非ゼロならネストした確認ダイアログ（`role="alertdialog"`、`data-panel="pre-share-summary-gate"`）を表示。ダイアログは既存の外側 SharePanel ダイアログと同じ focus-on-open（`tabIndex={-1}` + `requestAnimationFrame` でフォーカス）／Escape-復帰パターンを踏襲。
- **バグ発見・修正**: 実装直後の e2e で、ネストしたダイアログの Escape キー処理が `stopPropagation()` を呼んでいなかったため、外側の SharePanel 全体まで閉じてしまう不具合を検出・修正（イベントバブリングにより両方の `onKeyDown` ハンドラが発火していた）。
- **既存 e2e の広範な影響**: `EXPORT_BUNDLE_BUTTON` を直接クリックして即座にダウンロードイベントを待つ既存 e2e が7ファイルに存在し（多くのフィクスチャは `textReviewed: true` を明示しないカードを含むため新ゲートが必ず表示される）、いずれも新ゲートによって "Export bundle" クリック直後の即時ダウンロード前提が崩れることが判明。共有ヘルパー `continueThroughPreShareGateIfPresent()` を `e2e/helpers/i18n.ts` に追加し、7ファイルすべて（`review_pack_trace_export`, `ops_recovery_guidance`, `polygon_autofit_qa_boundary`, `polygon_import_validation`, `large_document_operability`, `hierarchy_level_persistence`, `diagnostics_structural_metrics`）のダウンロード待機直前に挿入して対応。

### 検証

- typecheck 0 / vitest **962 passed**（185 files。回帰アンカー1件を追加）
- backend: 変更なし（スキーマ非変更のため）。ruff クリーン / pytest 287 passed（既存回帰確認のみ）
- e2e 新規 `pre_share_summary_gate.spec.ts` **5/5 passed**（件数・非スコア表示／戻るでフォーカス復帰・非エクスポート／Escapeで同様に復帰／続行で従来どおり書き出し／ゼロ件時のゲート省略）
- 影響を受けた既存7 e2e ファイルすべて非回帰確認（`continueThroughPreShareGateIfPresent` 挿入後、全テスト意図どおりのアサーションを維持）。バッチ実行時に6件失敗が出たが、いずれもクリーンな main チェックアウトで同一条件・同一エラーで再現する既存の不安定性（`diagnostics_structural_metrics`／`hierarchy_level_persistence`／`large_document_operability`／`polygon_autofit_qa_boundary`×2／`polygon_import_validation`）であり、本Issueの変更による回帰ではないことを個別に確認した。

### 追記 2026-07-09: 実装照合レビューでの発見・修正

`02_Architecture/design/design-qa-checklist.md`（Claude Design Round 5 起源の実装照合チェックリスト）を本機能に初適用し、実機スクリーンショット（Docker Playwright）で確認した結果、共有直前サマリのSafeMode表示が「SafeMode: セーフモード: ON」と二重表記になっていることを発見した（`safeModeIndicator.label` が既に「セーフモード: ON」という接頭辞付き文字列を返すのに、`share.panel.pre_share_gate.safe_mode` の i18n テンプレートで再度「SafeMode: {value}」とラップしていたため）。`SharePanel.tsx` を修正して `safeModeIndicator.label` を直接表示するよう変更し、未使用化した該当i18nキーを両ロケールから削除、回帰アンカーを追加した。typecheck 0 / vitest 963 passed / 関連e2e 7 passed で再検証済み。詳細は `design-qa-checklist.md` 第2回記録を参照。
