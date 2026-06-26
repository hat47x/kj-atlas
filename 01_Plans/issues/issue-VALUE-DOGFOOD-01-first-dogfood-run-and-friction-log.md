# Issue: VALUE-DOGFOOD-01 初回ドッグフード走行と摩擦ログ

> 個人OSS段階（`ADR-0039`）の軽量起票。`ADR-0042` の実装入口。定性・非監視のみ。

- Type: Process
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Maintainer dogfood steward)
- Scope: `01_Plans/`, `README.md`（NOTICE 段階更新の判断のみ）
- Related Backlog: `VALUE-DOGFOOD-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md`, `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`（R-1 起動）
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

`README.md` NOTICE のとおり、本ツールは「人的レビュー・利用を伴っていない」。機能は出揃ったが（CE/DOMAIN-EXPR/PRODUCT-VALUE 進行）、**作られた価値が実在するか（曖昧さを保留したまま思考が前に進むか）を誰も検証していない**。改善フィードバックループが閉じていない。

## 2) 背景 / Context

- `ADR-0042` が最小ドッグフード経路（5手順）と NOTICE 脱却の段階A/B/C を定義済み。
- `ADR-0047` は「次に最も価値があるのは新ADRでなく実行＋ドッグフード」とし、本走行を R-1（実使用の摩擦による再起票）の起点と位置づけた。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 価値実在の確認は、次に何を直すべきかを価値起点で決める前提。P1。
- 安全（THREAT_MODEL / SafeMode）: 走行中も SafeMode 既定ON・共有前確認を実地で確認できる。
- 非目標との整合: 行動ログ・テレメトリ・個人追跡は導入しない（`ADR-0042` 非監視制約）。

## 4) 提案する解決策 / Proposed solution

- 実施（`ADR-0042` の経路を Maintainer 自身の実題材で1回完走）:
  1. 空状態または自分のメモからカードを置く。
  2. 保留（Hold）・違和感（Critique）・根拠不足を「作業状態」として残す。
  3. まとまり/関係を作り、俯瞰⇄詳細を往復（必要なら undo で配置やり直し）。
  4. 共有前確認を通し、確定点・保留点・未レビュー情報・根拠への戻り方を含む成果物を1つ出す。
  5. 「思考が雑にならなかったか」「早すぎる収束を強いられなかったか」の所感を記録。
- 成果物: `01_Plans/dogfood-log-<date>.md`（所感＋摩擦点 friction を箇条書き）。重量級テンプレ・スコアカードは課さない。
- 非目標: 第三者ユーザー調査、KPI 観測（VR4 延期中）、自動計測。

## 5) 受入条件 / Acceptance criteria

- [ ] `01_Plans/dogfood-log-<date>.md` が作成され、5手順の完走可否と所感が記録される。
- [ ] 発見した摩擦点が、根幹価値を損なうもの（高優先）／損なわない使い勝手（低優先）に分類される。
- [ ] 高優先の摩擦点は既存 backlog（PRODUCT-VALUE / DOMAIN-EXPR 等）へ紐付くか、R-1 該当時のみ新規 issue/ADR 候補として記録される。
- [ ] `README.md` NOTICE の段階（A/B/C）更新要否が `ADR-0042` 基準で判断される（更新する場合は段階Bへ）。
- [ ] 走行中に SafeMode 既定ON・共有前確認が機能することを目視確認する（安全条件）。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - frontend を起動（`ADR-0045` / `.claude/README.md` の手順、`npm run preview` → `http://127.0.0.1:4173`）。
  - `rg -n "friction|摩擦|保留|違和感" 01_Plans/dogfood-log-*.md`（記録の存在確認）。
- 期待結果: 5手順の完走可否と摩擦点が再確認可能な形で残る。
- 未実施時の理由・代替検証: preview 起動不可時は既存 e2e（first_meaningful_map / domain_expression_keyboard_access）を手順の代理確認に用いる。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: 自己評価のバイアス。→ 段階C（第三者利用）まで NOTICE を完全には外さない設計（`ADR-0042`）で緩和。
- 影響範囲: ドキュメントのみ（dogfood-log と NOTICE）。ロールバック=ログ削除・NOTICE 据え置き。

## 8) Additional context

- 本issueは `ADR-0047` の execution-first 転換の最初の一手。ここで出た高優先の摩擦が、次の ADR/issue を「価値起点で」決める。
