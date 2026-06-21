# ADR-0046: 応答性の性能予算

- Status: Accepted
- Date: 2026-06-10
- Deciders: Maintainer（委譲された意思決定権限）
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/frontend/`

## Context

`ADR-0043`（複雑性予算）は**認知**負荷の歯止めを定めた。一方、**計算**負荷（応答性・性能）の予算は未定義である。両者は別軸であり、機能が増える局面ではどちらも根幹価値（思考を雑にしない＝待たされて思考が途切れない）に影響する。

性能に関する記述は分散し、基準として機能していない（事実）。

- `02_Architecture/architecture.md`: 「カード数が百数十程度であれば実装とデバッグが簡単」と**前提を置くだけ**で、上限・劣化検知の基準がない。
- `02_Architecture/runtime_parameter_registry.md`: HTTP timeout（audit 2.0s / access-control 1.5s）と Failure budget はあるが、**フロントの描画・計算の性能予算はない**。
- worker 群（`diff` / `diagnostics` / `trace` / `bundle_zip`）で重い計算の非ブロッキング化は実装済みだが、**「いつ worker 化すべきか」「メインスレッドを何 ms 以上ブロックしないか」の基準がない**。
- `PRODUCT-UX-04`（大規模文書・低速環境の操作性、Done）は**定性的**（見切れ・待機表示の有無）で、`large_document_operability.spec.ts` も性能アサーション（時間・件数閾値）を持たない＝**回帰を防ぐ定量予算がない**。

質的統合法（KJ法）はカード増殖が前提であり（ROADMAP 中期 A/B）、DOMAIN-EXPR で状態計算（`state_filter` 等）と UI 要素が増えている。応答性の予算がないと、機能追加のたびに静かに遅くなり、ある時点で「思考の道具」として使えなくなるリスクを検知できない。

個人OSS段階（`ADR-0039`）では網羅的な性能保証は過剰だが、**代表規模の基準値と劣化検知の予算**を最小で固定することは低コストで価値が高い。

## Decision

応答性を次の性能予算（PB）で定義し、代表規模・代表操作に対する目安値と検証方針を固定する。本ADRを応答性予算の正本とする。

### 性能予算（PB）

数値は厳密 SLA ではなく**劣化検知のための目安（個人OSS段階）**。代表環境（デスクトップ・中位スペック）での目標。

- **PB-1 代表規模**: 「快適に使える」基準規模をカード約300・島約30とする（architecture.md の「百数十」前提を実用域へ更新）。これを超えても壊れない（degrade gracefully）こと。
- **PB-2 初期表示**: 代表規模の文書を開いてから操作可能になるまでの体感を、明確な待機表示なしで数秒以内に収める。超える場合は待機状態を可視化する（`ADR-0044` UQ-5）。
- **PB-3 メインスレッド非ブロッキング**: 単一の同期処理でメインスレッドを長時間（目安 100ms 超）ブロックしない。超える計算（diff / diagnostics / trace / bundle・大規模集計）は worker へ逃がす。これを **worker 化の判断基準**として固定する。
- **PB-4 対話操作の即応**: 選択・パン/ズーム・フィルタ切替・保留トグル等の対話操作は、入力に対し即応（体感遅延なし）。重い再計算は debounce / メモ化 / worker で分離する。
- **PB-5 劣化の可視化**: 予算を超える状態（大規模・低速）では「反応がない」ように見せず、待機・進捗・キャンセルを提示する（`ADR-0044` UQ-4/UQ-5 と一体）。

### 検証方針（軽量）

- 代表規模 fixture（カード約300）で `large_document_operability.spec.ts` に**最小の性能アサーション**（主要操作完了までの上限時間、worker 利用で UI が固まらないこと）を追加する。厳密ベンチでなく回帰検知が目的。
- 性能に影響する変更（大きなループ・全カード走査・同期重処理の追加）を含む issue は、本文に1行で自己申告する。

```
性能予算: 代表規模での主要操作=<不変/改善/悪化（理由）> / メインスレッド100ms超の同期処理=<なし/あり→worker化>
```

- 「悪化」「worker 化せず 100ms 超」を含む場合は `PRODUCT-QA-01`（性能観点）で明示確認する。

### 非目標

- 厳密な SLA・パーセンタイル目標の固定（段階・環境で変動）。
- 大規模専用のレンダリング刷新（仮想化・キャンバス WebGL 化等）の即時導入（将来 issue 候補）。
- マイクロベンチマーク基盤の新規構築。

## Consequences

- 期待される効果:
  - 機能追加のたびの「静かな劣化」を、代表規模の最小アサーションで検知できる。
  - worker 化の判断が「重そう」でなく「100ms 超か」で行える。
  - `ADR-0043`（認知負荷）と本ADR（計算負荷）が、根幹価値「思考を雑にしない」を二軸で守る体系になる。
- 想定される副作用/制約:
  - 目安値は環境依存で、CI 実行環境では絶対時間がぶれる → アサーションは余裕を持たせ、回帰検知（相対的悪化・worker 不使用）を主目的にする。
  - 自己申告は形骸化しうる → 「悪化」時のみゲート確認で最小の強制力を持たせる。
- 移行時に必要な対応:
  - `02_Architecture/value_traceability.md` に「応答性の性能予算」を価値判断として追記する。
  - `02_Architecture/architecture.md` の「百数十」前提に、PB-1 代表規模（約300）への参照を補足する。
  - 性能アサーション追加 issue（`PERF-BUDGET-01`）を Draft 候補とする（`ADR-0039` 軽量運用）。

## Traceability

- Related: `02_Architecture/architecture.md`（規模前提）, `02_Architecture/runtime_parameter_registry.md`（timeout/Failure budget）
- Related: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`（認知負荷予算と対をなす計算負荷予算）
- Related: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-4 レイアウト堅牢性・UQ-5 状態可視性）
- Related: `01_Plans/issues/issue-PRODUCT-UX-04-responsive-large-document-operability.md`
- Related: `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`（軽量運用）
- Derived-from: 2026-06-10 性能記述の分布調査（規模前提のみで予算・劣化検知の基準なし）
