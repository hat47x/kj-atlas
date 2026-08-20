# Issue Draft: EXT-CONN-04 「なぜ？」リンクの着地 ― 読み取り専用の根拠トレイルビュー

- Type: Feature request
- Status: Draft
- Source Issue: N/A（`ADR-0054` 役割B。Claude Design P32 先行相談 B-2 の回答で新設が確定）
- Priority: P3
- Owner: TBD
- Scope: `03_Implement/frontend/src/`（読み取り専用ビュー）, `03_Implement/backend/`（トレイル解決。EXT-CONN-01 投影の一部として）
- Related Backlog: `EXT-CONN-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`, `01_Plans/issues/issue-UX-SHARE-01-pre-share-summary-gate.md`（露出規則の正本）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-CONN-04
- RequirementStatement: 外部に配信されたブリーフの「なぜ？」リンクから来訪した閲覧者が、そのブリーフが基づくレビュー済みカード群と関係線を読み取り専用トレイルとして辿れる。
- AcceptanceScenario: 前提=EXT-CONN-01/02 稼働・ブリーフに相関ID（bundleHash等）が埋まっている / 操作=ブリーフの「なぜ？」リンクを開く / 期待結果=基づくレビュー済みカードと根拠経路だけが読み取り専用で提示される / 除外=編集、未レビュー・違和感・保留の既定表示、確からしさ%。
- SecurityGateImpact: SafeMode / share-export / public-exposure
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef: `ADR-0054` は Accepted 済み（2026-07-12）。残るゲートは**段階1/2の進行（相関IDつきブリーフの実在）＋実装レッドライン受領**（充足後に Open 化）。

## 背景

トリガー型AIの構造的弱点は、配信されるブリーフの根拠が見えず誤りの出所を辿れないこと（Lee & See の信頼校正要件）。「このブリーフはどのレビュー済みカードに基づくか」を辿れる監査層が、背後の文脈基盤を「時々信頼を確かめに見に行く場所」にする（リサーチ役割B）。Claude Design P32 は「readOnly＋focus では外部来訪者に文脈が伝わらず不足。専用の読み取り専用トレイルが必要」と回答した。

## 提案する解決策（P32 方向）

- ブリーフ側の相関ID（`bundleHash` / `taskId`）から、**ブリーフ→基づくレビュー済みカード群→（あれば）関係線**を辿れる読み取り専用ビューを提供する。
- 露出規則は共有前確認と同格を継承: **未レビュー・違和感・保留のカードは既定で出さない**。SafeMode 既定ON。
- 反スコアリング: 「確からしさ%」等は出さず、経路（trail）と根拠の有無のみ提示する。
- 既存の readOnly モード・review pack 閲覧の実装資産を再利用し、新設は「トレイル解決（相関ID→カード集合）」と「トレイル表示」に限定する。

## 非目標

- 編集・コメント・リアクション等の書き込み。
- 未レビュー情報の opt-in 表示（将来判断。初期は一律非表示）。
- ブリーフ配信面そのものの実装（プラットフォーマー側）。

## 受け入れ条件（案）

- [ ] AC-1: 相関IDから基づくレビュー済みカード群と関係線が読み取り専用で辿れる。
- [ ] AC-2: 未レビュー・違和感・保留カードが既定で露出しない（共有前確認の露出規則と同一のテストで検証）。
- [ ] AC-3: score/rank/confidence/priority・％表示が存在しない。
- [ ] AC-4: 原本文書は一切変更されない（読み取り専用契約）。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`（追記 2026-07-12 B-2）
- Related: `01_Plans/issues/issue-EXT-CONN-01-readonly-mcp-server.md`（トレイル解決の投影基盤）
- Related: `01_Plans/research/research-2026-07-12-trigger-ai-external-integration.md`（役割B）
