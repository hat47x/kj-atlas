# ADR-0030: UI操作モデルの段階的開示とキーボードスコープ

- Status: Proposed
- Date: 2026-05-14
- Deciders: Project Maintainers
- Scope: `03_Implement/frontend/src/`, `04_Documentation/acceptance_check.md`, `03_Implement/frontend/docs/e2e_testing.md`

## Context

- 2026-05-14 の UI/UX 操作検証で、標準サンプル `doc_phase1_canvas` を開き、マウス操作とキーボード操作の代表フローを確認した。
- マウスでカードを選択しても、選択内容の確認・編集に関わる領域は右側パネルの下部にあり、直後に見えるのはレビュー差分、文章化、候補比較、CE3、批評入力などの高度な領域だった。
- キーボードの `Tab` 操作ではカードそのものに到達できず、右側パネルの多数の操作を長く巡回してからでないと文脈に合う領域へ近づけない。
- `表示` と `共有と再現` はキーボードで開けるが、`Escape` で閉じられず、明示的な閉じるボタンやフォーカス復帰方針も定義されていない。
- これらは個別のラベル修正だけでは解決しにくく、主要作業、文脈作業、高度な作業の配置とフォーカススコープを定める判断が必要である。

## Decision

- kj-atlas の UI 操作モデルは、次の方針を採用する。
  - キャンバス上のカード・島は、マウスだけでなくキーボードでも選択できる主要操作対象として扱う。
  - カードまたは島を選択した直後は、選択対象の確認・編集・レビュー導線を右側パネルの最上位または現在の文脈スコープへ表示する。
  - 高度なレビュー、差分、パッチ、文章化、診断などは、初期表示で常時すべて展開せず、タブ、折りたたみ、または明示的な作業モードで段階的に開示する。
  - `表示`、`共有と再現` などの一時パネルは、`Escape` で閉じ、閉じた後は起点ボタンへフォーカスを戻す。
  - `Tab` 順序は現在の作業スコープを優先し、起動直後や選択直後に関係の薄い高度操作へ長く流れ込まないようにする。
- 採用理由:
  - ADR-0001 の `UX-06`（俯瞰と詳細の往復）と `UX-03`（レビュー状態の明示）を、実際のマウス・キーボード操作で成立させるため。
  - 一般利用者が「選んだものを確認する」「戻る」「共有前に安全状態を見る」という基本操作に迷わない状態を作るため。
  - SafeMode と share/export の安全境界を、キーボード利用者にも同等に到達可能にするため。
- 非目標:
  - 本ADRは画面デザインの全面刷新を決めない。
  - 個別コンポーネントの実装進捗は issue memo で管理する。
  - すべての高度機能を削除または非表示にすることは目的にしない。

## Consequences

- 期待される効果:
  - カード選択、レビュー確認、共有前確認のような基本フローで、マウス利用者とキーボード利用者の到達性が近づく。
  - 右側パネルの認知負荷が下がり、初回利用者が高度機能に先に迷い込むリスクを下げられる。
  - E2E で「操作対象を選ぶ」「パネルを開く」「閉じる」「フォーカスが戻る」を明確に検証できる。
- 想定される副作用/制約:
  - 右側パネルの構成変更により、既存の熟練利用者の操作位置が変わる可能性がある。
  - タブ化や折りたたみを導入する場合、状態保持とE2E待機条件を設計する必要がある。
  - カードをキーボード到達可能にすると、キャンバス内のフォーカス数が増えるため、ショートカットや検索移動との責務分担が必要になる。
- 移行時に必要な対応:
  - 既存の `IslandView` アクセシビリティ修正と衝突しない形で `CardView` のキーボード選択を追加する。
  - 右側パネルの領域を「選択対象」「表示/レビュー」「高度ツール」に分け、初期展開ルールをE2Eに固定する。
  - `表示` / `共有と再現` パネルに閉じる操作、`Escape`、フォーカス復帰を追加する。

## Traceability

- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Related: `02_Architecture/architecture.md`
- Related: `01_Plans/issues/issue-UX-OPERABILITY-01-pointer-keyboard-flow-review.md`
- Related: `01_Plans/issues/issue-UX-OPERABILITY-02-keyboard-card-selection.md`
- Related: `01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`
- Related: `01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`
- Supersedes: N/A
- Superseded by: N/A
- Derived-from: `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`

---

## Authoring Checklist（人間/生成AI 共通）

- [x] 必須ヘッダ（Status/Date/Deciders/Scope）を記載した。
- [x] 必須章（Context/Decision/Consequences/Traceability）を記載した。
- [x] Decision に採用理由と非目標がある。
- [x] Traceability に関連文書を1件以上記載した。
- [x] 実装進捗は ADR ではなく Issue で管理する前提を維持した。
