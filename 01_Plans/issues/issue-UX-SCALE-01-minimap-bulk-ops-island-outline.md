# Issue Draft: UX-SCALE-01 スケール操作の拡充（ミニマップ・一括操作・島の直交描線・関係線エスカレーション）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD
- Scope: `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/domain/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-SCALE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D1/D3）, `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`（PB-1..5）, `01_Plans/issues/issue-PERF-BUDGET-01-large-document-performance-assertions.md`（In Progress・性能検証の正本）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-SCALE-01
- RequirementStatement: 大規模文書（PB-1: 約300カード/30島）での見通しと操作を、(a) ミニマップ、(b) 複数選択の一括操作バー、(c) 島の直交描線（矩形/L字/コの字）＋複雑さ表示＋可逆な「整える」、(d) ズーム連動の関係線エスカレーション、で拡充する。いずれも既存 LOD・構造レベル・読み順可視化（実装済み）を再決定せず拡張する。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=300カード/30島規模のフィクスチャ / 操作=縮小して俯瞰→ミニマップでビュー移動→複数選択して一括保留→島の「整える」→ズームアウト / 期待結果=現在ビューがミニマップに表示され移動できる。一括操作が1回の取り消しで戻る。島は凸空白を含まない直交描線になり複雑さが表札に出る。省略カードの関係線は同島内=内部化・異島間=表札へ昇格 / 除外=WebGL 化・仮想化等のレンダリング刷新（ADR-0046 非目標）、LOD 閾値の再設計。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: N/A
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048。ただし着手は段階1/2 issue 完了後）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- LOD・構造レベル・読み順は実装済みだが、規模拡大時の (a) 全体ナビ手段が無い、(b) 多数選択後の操作が個別で重い、(c) 島の外接矩形が空白の角を含み面積過大＝散らかりの原因が見えない、(d) 縮小時にカードが省略されると関係線の扱いが未定義、という残課題がある。
- 配置の散らかりを「点数」でなく**描線複雑さ（凹み角数）のサイン**として可視化し、可逆な「整える」候補で応える設計（反スコアリング整合）が壁打ちで確立した。

## 2) 背景 / Context

- 壁打ち成果（拡張提案 観点2・図R/S/T・複雑さメトリクス・エスカレーション規則）がプロトタイプ検証済み: 直交単純多角形の複雑さ=(頂点数−4)/2、JOIN/LEAVE 二重閾値、同島内関係の内部化・異島間の表札昇格。
- 性能の正本は ADR-0046（PB-4 対話操作の即時感）と PERF-BUDGET-01（In Progress）。本Issueは性能検証を重複させず、PB 準拠を宣言して同フィクスチャに乗る。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-06）: 俯瞰↔詳細の視点制御の完成形。俯瞰でも保留・違和感・規模（N枚）を落とさない（全体性の保持）。
- 安全: N/A（表示・整列のみ。整列は自動実行せず人間起動・可逆）。
- 規模拡大: 本Issueがスケール UX の中核。ただし基盤（視覚言語・入力体系）完了後の段階3。
- 後方互換: スキーマ変更なし（描線・ナビ・一括操作は表示/操作層）。

## 3.2 非目標 / Non-goals

- レンダリング刷新（仮想化・WebGL）。LOD 閾値・構造レベルの再設計。自動整列の既定化（提案・人間起動・可逆に限る）。関係記号の種別追加（DOMAIN-KJ-01 の領分）。

## 4) 提案する解決策 / Proposed solution

- (a) **ミニマップ**: 隅に小型・控えめ表示（既定表示は要 CB-1 宣言。折りたたみ可）。現在ビュー枠のドラッグで移動。
- (b) **一括操作バー**: 複数選択時のみ出現（島に束ねる・一括保留/違和感・一括型変更・削除）。1操作=履歴1ステップで取消可能。保持系を左端（最上位）に配置。
- (c) **島の直交描線**: メンバー矩形のグリッド占有から縦横線のみのポリゴンを生成（≤2枚は丸角矩形）。複雑さ（凹み角数）を表札に小さく表示し、「整える」（右クリック/⌘K から人間起動・⌘Z で一括取消）で密なグリッドへ再配置。点数化しない（見直しのサインに留める）。
- (d) **関係線エスカレーション**: 鳥瞰でカードが表札チップに省略された際、同一島内に両端が集約された関係=非表示（内部化）、異なる島/残存カードへの関係=表札へ昇格して描画（昇格線はラベルで区別）。ズーム復帰で可逆。
- すべて PB-4（対話操作の即時感）を満たすこと。劣化時は PB-5 の可視化に従う。

## 5) 受け入れ条件 / Acceptance criteria

- [ ] AC-1: ミニマップで現在ビューの把握と移動ができ、折りたたみ状態が保持される。
- [ ] AC-2: 一括操作（束ねる・保留・型変更）が複数選択時のみ出現し、1回の取り消しで全体が戻る。
- [ ] AC-3: 島の描線が空白の角を含まない直交ポリゴンで描かれ、複雑さ表示→「整える」→複雑さ低減が e2e で固定される（自動実行しない）。
- [ ] AC-4: 鳥瞰時の関係線が内部化/昇格規則どおりに増減し、ズーム復帰で元に戻る。
- [ ] AC-5: PERF-BUDGET-01 のフィクスチャ上で PB-4 相当の対話性が維持される（同Issueの計測系を再利用し重複計測しない）。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 ミニマップ（ビュー枠・折りたたみ・CB-1 宣言）。
- [ ] T2 一括操作バー（選択数連動・履歴1ステップ）。
- [ ] T3 直交描線ジェネレータ＋複雑さ算出＋「整える」。
- [ ] T4 エスカレーション規則（内部化/昇格/ラベル）。
- [ ] T5 e2e＋PB 準拠確認。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`
- PERF-BUDGET-01 の大規模フィクスチャでの操作スモーク（同Issueのハーネスを利用）。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=+1（ミニマップ。ただし小型・隅・折りたたみ可。理由=俯瞰ナビは規模拡大時の中核導線） / 保留操作の距離=改善（一括操作バーで複数カードの保留が1操作） / 取り消し導線=あり（一括操作・整えるは1ステップで可逆、エスカレーションはズームで可逆）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `01_Plans/issues/issue-PERF-BUDGET-01-large-document-performance-assertions.md`
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（観点2・図R/S/T）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
