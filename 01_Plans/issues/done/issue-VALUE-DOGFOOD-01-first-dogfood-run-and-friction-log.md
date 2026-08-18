# Issue: VALUE-DOGFOOD-01 初回ドッグフード走行と摩擦ログ

> 個人OSS段階（`ADR-0039`）の軽量起票。`ADR-0042` の実装入口。定性・非監視のみ。

- Type: Process
- Status: Done
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

- [x] `01_Plans/dogfood-log-<date>.md` が作成され、5手順の完走可否と所感が記録される。（`dogfood/dogfood-log-2026-06-26.md`, `dogfood/dogfood-log-2026-07-10.md`）
- [x] 発見した摩擦点が、根幹価値を損なうもの（高優先）／損なわない使い勝手（低優先）に分類される。
- [x] 高優先の摩擦点は既存 backlog（PRODUCT-VALUE / DOMAIN-EXPR 等）へ紐付くか、R-1 該当時のみ新規 issue/ADR 候補として記録される。（R-1 初事例: `QA-MONKEY-10` 起票）
- [x] `README.md` NOTICE の段階（A/B/C）更新要否が `ADR-0042` 基準で判断される（更新する場合は段階Bへ）。（判断: 段階A維持、更新不要）
- [x] 走行中に SafeMode 既定ON・共有前確認が機能することを目視確認する（安全条件）。（SafeMode ON は実画面確認、共有前確認は前回ログ＋e2eで担保）

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

## 9) 対応記録（2026-07-10）

- 2回目の走行を**実バックエンド構成**（docker compose: db+api+web、provider=none）で実施し、
  `01_Plans/dogfood/dogfood-log-2026-07-10.md` に記録した。前回（2026-06-26、フロントエンド単体）と合わせて
  「フロント単体」「実永続化込み」の両方で5手順の経路を通したことになる。
- 実題材（EXT-AGENT-02 実装の未決事項3点＋メタな不確かさ1点）でカードを置き、
  実保存（「保存しました」）→ postgres 直接確認（4カード全テキスト無傷）→ 再読込での文書一覧再表示、
  まで実地で確認した。
- R-1（実使用の摩擦による再起票）の初事例として、高優先摩擦
  「カスケード配置＋ラベルカリングによる入力直後テキストの見かけ上の消失」を
  `issue-QA-MONKEY-10-cascade-label-culling-hides-fresh-card-text.md` として起票した。
  当初データ喪失と誤認したが、DB直接確認により表示のみの問題と切り分けた（切り分けの経緯も log 参照）。
- NOTICE は段階A維持（QA-MONKEY-10 未解消＋第三者利用未達のため）。README 更新なし。
- 再現スクリプト: `03_Implement/frontend/scripts/dogfood_run_20260709.mjs`（CI には接続しない一回性の探索スクリプト）。
