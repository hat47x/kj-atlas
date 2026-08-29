# Issue Draft: QA-MONKEY-09 Start panel focus scope

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/ui/StartPanel.tsx`, `03_Implement/frontend/e2e/first_run_document_entry.spec.ts`
- Related Backlog: `QA-MONKEY-09`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/done/issue-PRODUCT-UX-01-first-run-document-entry.md`, `04_Documentation/acceptance_check.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-09
- RequirementStatement: 起動直後の「作業を開始」パネル表示中は、キーボードフォーカスが背後のヘッダー、キャンバス、右側パネル操作へ抜けず、開始操作だけを順に選べるようにする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ブラウザでkj-atlasを初回起動し開始パネルが表示される / 操作=Tab と Shift+Tab でフォーカス移動する / 期待結果=フォーカスは開始パネル内の閉じる、新規作成、サンプル、読み込み、レビューパック、最近の文書操作に閉じる / 除外=開始パネルを閉じた後の通常ヘッダー/キャンバス操作。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / import-sanitize

## 1) 課題 / Problem statement

- Browser plugin / in-app browser で `http://127.0.0.1:4173/?locale=ja` を開き、開始パネル表示中のフォーカス可能要素を確認した。
- 開始パネルが表示されているにもかかわらず、Tab順の先頭にヘッダーの SafeMode、表示モード、検索、新規/複製、右側パネル由来の操作が多数入っていた。
- 視覚的には開始パネルが入口に見えるが、キーボード利用者やスクリーンリーダー利用者には背後操作が先に提示され、初回導線の自然さを損なう。

## 2) 背景 / Context

- `PRODUCT-UX-01` は初回文書入口をDoneとしているが、完了時のE2Eは開始パネルのボタンを直接フォーカスし、Tab順がパネル外へ抜けないことまでは固定していなかった。
- `04_Documentation/acceptance_check.md` は、キーボードだけで主要操作に届かない、または同名操作が複数出て迷う場合はUI/UX課題として記録するよう案内している。
- 開始パネルは製品の最初の操作面であり、背後UIよりも先に安全な入口を提示する必要がある。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 初回利用者が迷わず作業を開始できることは、製品価値の入口である。
- 安全（THREAT_MODEL / SafeMode）: SafeMode確認と取り込み検証の入口を先に提示できないと、誤った取り込みや共有前確認の見落としにつながる。
- 企業・行政要件（enterprise_architecture）: キーボード操作や支援技術での到達性は、組織導入時の受け入れ条件になり得る。
- 後方互換（schemas）: UIフォーカス制御のみで、document/view/review pack schema は変更しない。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - `StartPanel` を `role="dialog"` / `aria-modal="true"` の開始ダイアログとして扱う。
  - 表示時にパネル内の最初の操作へフォーカスを移す。
  - `Tab` / `Shift+Tab` をパネル内で循環させ、背後のヘッダー、キャンバス、右側パネルへ抜けないようにする。
- 変更の最小単位:
  - 背景UIの情報設計や主要ナビゲーションは変えず、開始パネル表示中のキーボードフォーカスだけを閉じ込める。
- 非目標:
  - フルスクリーンのオンボーディング再設計。
  - header / side panel の通常時Tab順序変更。
  - schema、SafeMode規則、import/export仕様の変更。

## 5) 受入条件 / Acceptance criteria

- [x] 開始パネル表示時、初期フォーカスが開始パネル内にある。
- [x] 開始パネルに `role="dialog"` と `aria-modal="true"` がある。
- [x] `Tab` を繰り返してもフォーカスが開始パネル外へ抜けない。
- [x] `Shift+Tab` でもフォーカスが開始パネル外へ抜けない。
- [x] 既存の新規作成、サンプル、文書読み込み、レビューパック取り込み導線は維持される。
- [x] No schema, SafeMode, share/export, API, or backend behavior changes.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Browser pluginで開始パネル表示中のフォーカス可能要素を観測する。
- [x] T2 `StartPanel` にdialog semantics、初期focus、Tab循環を追加する。
- [x] T3 `first_run_document_entry.spec.ts` にフォーカススコープ回帰を追加する。
- [x] T4 frontend E2E と型検査で回帰を確認する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\typescript\bin\tsc --noEmit`
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/first_run_document_entry.spec.ts --reporter=line`
  - Browser plugin / in-app browser で `http://127.0.0.1:4173/?locale=ja` を開き、開始パネルの初期focusとTab循環を確認する。
- 期待結果:
  - 開始パネル表示中のフォーカスはパネル内に留まる。
  - パネルを閉じた後の通常操作は既存どおり使える。

## 8) 代替案 / Alternatives considered

- 代替案A: 背景UI全体を構造的に `inert` にする。より強いが、`Shell` のheader/sidePanel/main境界をまたぐため変更範囲が広い。今回の回帰修正では採用しない。
- 代替案B: 既存の直接focus E2Eだけで十分とみなす。実Chrome観測でTab順の混乱が確認されたため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 開始パネル内のフォーカス循環が、ファイル選択や最近の文書select操作を阻害する。
- 影響範囲: 初回起動時の開始パネル表示中のキーボード操作。
- ロールバック手順: `StartPanel` のdialog/focus trap追加とE2E追加を戻し、既存の非モーダルsection表示へ戻す。

## 10) Additional context

- ADR化が必要になる条件: 初回起動面をフルスクリーンオンボーディング、ルーティング、または製品全体のモーダル戦略として再定義する場合。

## 11) Closeout

- Implementation: `StartPanel` now acts as a modal entry dialog, focuses the first available panel control on mount, and loops `Tab` / `Shift+Tab` within the panel.
- Regression coverage: `first_run_document_entry.spec.ts` verifies dialog semantics and focus containment.
- Browser evidence: in-app browser initially showed focusable header/right-panel controls before start-panel controls; this issue records that observation and fixes the keyboard path.

---
