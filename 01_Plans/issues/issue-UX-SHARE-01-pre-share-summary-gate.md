# Issue Draft: UX-SHARE-01 共有直前サマリ（未レビュー・違和感・矛盾の既定非表示を明示）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-SHARE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 憲章・反スコアリング）, `01_Plans/issues/issue-PRODUCT-UX-03-safe-share-export-flow.md`（Done・目的起点フローの強化であり再決定ではない）, `01_Plans/issues/issue-DOMAIN-TRACE-01-serial-number-and-source-provenance.md`（出典トグルの所有元）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-SHARE-01
- RequirementStatement: 共有・書き出しの直前に「未レビュー n件・違和感 m件・矛盾 k件は既定で非表示（SafeMode）」であることを1枚のサマリで明示し、利用者が保持中の情報の露出範囲を確認してから出力できるようにする。件数は所在提示であり評価ではない（反スコアリング）。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=未レビュー・違和感・矛盾を含む文書で「共有と再現」を開く / 操作=書き出しを実行しようとする / 期待結果=直前サマリに3種の件数と「既定で非表示」の説明が表示され、戻って編集または続行を選べる。準備度・スコア・%は表示されない / 除外=共有フロー全体の再設計（PRODUCT-UX-03 Done の再決定）、公開範囲・粒度選択そのものの変更、出典参照トグル（DOMAIN-TRACE-01 所有）。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: SafeMode / share-export（安全境界の明示性強化。境界自体は不変・弱めない）
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048 憲章の適用。Round 4 設計 §領域5）
- DecisionQueueRef: `ADR-0048`

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

- 共有フロー全体・preflight 構成の再設計。公開範囲/粒度モデルの変更。準備度スコア等の導入（反スコアリング）。出典参照トグル（DOMAIN-TRACE-01）。

## 4) 提案する解決策 / Proposed solution

- 書き出し実行の直前に確認サマリを1枚挿入: 「未レビュー n件・違和感 m件・矛盾 k件は既定で非表示になります」＋戻る/続行。SafeMode 状態を併記。
- 件数はリンクとして該当フィルタへ誘導可能（戻って確認する導線）。評価語（不足/未達/危険等）は使わない。
- a11y: 開いたらサマリ見出しへフォーカス、フォーカストラップ、Esc で取消しトリガへ復帰（Round 4 §a11y 仕様に従う）。
- i18n（ja/en）。

## 5) 受け入れ条件 / Acceptance criteria

- [ ] AC-1: 3種の件数と「既定で非表示」の説明が出力直前に表示され、戻る/続行が選べることが e2e で固定される。
- [ ] AC-2: 準備度・スコア・%・評価語がサマリに存在しない。
- [ ] AC-3: SafeMode 既定ON・既存 preflight（PRODUCT-UX-03）の内容が非回帰。
- [ ] AC-4: フォーカス初期位置・トラップ・Esc 復帰が仕様どおり（UX-OPERABILITY-04 契約整合）。
- [ ] AC-5: 件数ゼロの文書ではサマリが簡潔化（または省略）され、共有を不必要に妨げない。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 件数集計（既存の domain 状態導出を再利用）。
- [ ] T2 直前サマリ UI＋フォーカス契約＋i18n。
- [ ] T3 件数→フィルタ誘導リンク。
- [ ] T4 e2e（表示・非スコア・非回帰・ゼロ件時）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`
- SharePanel 既存 e2e（PRODUCT-UX-03 系）の非回帰確認。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（共有操作時のみ1枚） / 保留操作の距離=改善（保持中の情報の露出判断が共有直前に1操作で確認可能） / 取り消し導線=あり（戻って編集で可逆）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/issues/issue-PRODUCT-UX-03-safe-share-export-flow.md`, `issue-DOMAIN-EXPR-04-evidence-claim-contradiction-review.md`, `issue-DOMAIN-TRACE-01-serial-number-and-source-provenance.md`
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（§領域5・2026-07-04 版）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
