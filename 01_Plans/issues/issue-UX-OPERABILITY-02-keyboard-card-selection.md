# Issue Draft: UX-OPERABILITY-02 カードをキーボードで選択できない

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/src/canvas/CanvasShell.tsx`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-OPERABILITY-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `02_Architecture/architecture.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-OPERABILITY-02
- RequirementStatement: 一般利用者がマウスを使えない状況でも、カードをキーボードで選択し、選択結果と次の操作を確認できる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプル `doc_phase1_canvas` を `?locale=ja` で開く / 操作=`Tab`、矢印キー、`Enter` または `Space` でカード選択へ到達する / 期待結果=カードがフォーカス可能で、選択後にカード本文または選択状態が分かり、右側パネルの関連操作へ移れる / 除外=高度な座標編集やドラッグ移動の完全キーボード代替。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0030`

## 1) 課題 / Problem statement

- 2026-05-14 のキーボード操作検証で、`Tab` を70回進めてもキャンバス上のカード本文へフォーカス到達しなかった。
- `CardView.tsx` はカードを `div` として描画し、pointer handler はあるが `tabIndex`、`role`、`onKeyDown` がない。
- そのためカード選択は実質的にマウス/ポインター操作に偏り、一般利用者向けのキーボード操作確認で主要対象へ到達できない。

## 2) 背景 / Context

- `ADR-0001` の `UX-06` は俯瞰と詳細の往復を要求している。
- 島については `QA-MONKEY-05` で重複アクセシビリティ修正が行われたが、カード本体のキーボード選択は別課題として残っている。
- カードはKJ Atlasの主要オブジェクトであり、検索結果、レビュー、根拠リンク、読み順の起点になる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 思考素材であるカードへ直接到達できないと、意味の保留や詳細確認がキーボード利用者に成立しにくい。
- 安全（THREAT_MODEL / SafeMode）: 直接の漏えい境界ではない。
- 企業・行政要件（enterprise_architecture）: 組織導入ではキーボード操作とアクセシビリティが採用条件になりやすい。
- 後方互換（schemas）: 表示/操作の改善であり、document schema は変更しない。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - `CardView.tsx` にフォーカス可能な操作対象としての意味付けを追加する。
  - `Enter` / `Space` でカード選択できるようにする。
  - 選択状態を視覚的な outline だけでなく、キーボードフォーカスでも確認できるようにする。
  - Playwrightで `Tab` からカード選択し、右側パネルに選択状態が反映されるE2Eを追加する。
- 変更の最小単位:
  - カード選択のみを対象にし、カード移動のキーボード実装は別Issueに分ける。
- 非目標:
  - キーボードでの自由ドラッグ移動、複数選択矩形、座標微調整を本Issueで完了しない。

## 5) 受入条件 / Acceptance criteria

- [ ] 少なくとも標準カード3件がキーボードでフォーカス可能である。
- [ ] `Enter` または `Space` でカードを選択できる。
- [ ] 選択後、カード選択状態が画面上で確認できる。
- [ ] 選択後、次の `Tab` 移動で関連するカード確認/編集導線へ自然に進める、または明示的なショートカット/ジャンプ導線がある。
- [ ] 既存のマウスクリック、ドラッグ、検索ハイライトを壊さない。
- [ ] E2Eで `locale=ja` のカード選択フローを検証する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 `CardView` のフォーカス、ロール、キーボードイベント設計を決める。
- [ ] T2 `Enter` / `Space` による選択を実装する。
- [ ] T3 選択後のフォーカス移動または関連パネル誘導を `UX-OPERABILITY-03` と整合させる。
- [ ] T4 Playwright E2Eを追加する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/canvas/IslandView.accessibility.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test <new-card-keyboard-spec> --reporter=line`
- 期待結果:
  - キーボードだけでカード選択が成立し、既存の島操作アクセシビリティテストも通る。
- 未実施時の理由・代替検証:
  - Playwright実行環境がない場合は、render test とブラウザ手動操作ログで一時代替し、E2E追加を未完了として残す。

## 8) 代替案 / Alternatives considered

- 代替案A: 検索結果の前へ/次へだけをキーボード選択の代替にする。検索語がないカード確認に使えないため不十分。
- 代替案B: 右側パネルのリストからカードを選ばせる。キャンバス上の主要対象へ直接到達できない問題が残るため補助策に留める。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: フォーカス可能要素が増えすぎ、Tab移動がかえって長くなる。
- 影響範囲: キャンバス、カード選択、検索、右側パネル、E2E。
- ロールバック手順: `CardView` のキーボード意味付けとE2E追加を戻し、従来のpointer操作へ戻す。

## 10) Additional context

- 2026-05-14 検証:
  - Edge Chromium（Chrome代替） / `http://127.0.0.1:5173/?locale=ja` / viewport `1440x900`
  - `Tab` 70回の巡回にカード本文は含まれず、右側パネルの高度操作へ長く流入した。
  - `CardView.tsx` に `tabIndex` / `role` / `onKeyDown` は見当たらない。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
