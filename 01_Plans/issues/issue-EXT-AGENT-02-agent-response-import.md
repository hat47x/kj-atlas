# Issue Draft: EXT-AGENT-02 エージェント応答の取り込みと提案化（AgentResponse v1）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/import/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/domain/`, `03_Implement/frontend/e2e/`
- Related Backlog: `EXT-AGENT-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（D3）, `02_Architecture/external_agent_collaboration_spec.md`（§4/§5 正本）, `01_Plans/issues/issue-CE3-patch-workspace-presets.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-AGENT-02
- RequirementStatement: 外部エージェントの応答（agent-response.v1・貼り付け/ファイル）を import 信頼境界（検証・サニタイズ・容量制限）で受け、種別ごとに既存の提案面（マージ候補・島タイトル候補・ナラティブ草稿・違和感候補・PatchWorkspace）へ AI 由来・未レビューの提案として流し込む。自動確定なし・全操作可逆・監査記録を不変条件とする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=EXT-AGENT-01 で書き出した依頼に対する応答 JSON を得ている / 操作=「応答を取り込む」へ貼付け→検証結果を確認→取り込み / 期待結果=提案が種別ごとの既存面に未レビューとして出現し、taskId でグルーピング表示される。score/rank/confidence フィールドは破棄され警告表示。baseDocSignature 不一致時は conflict/rediff 経路に乗り黙って適用されない。1件採用→⌘Z で復帰できる / 除外=外部からの自動受信、応答の自動適用、エージェント品質の保証。
- GoNoGoGate（Required / Optional / N/A）: Required（外部由来データの取り込み経路の新設のため、import-sanitize 検証を完了条件とする）
- SecurityGateImpact: import-sanitize（非信頼データの新規取込面。指示文言をデータとして扱いいかなる自動動作にも接続しない）
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0049 D3・spec §4）
- DecisionQueueRef: `ADR-0049`

## 1) 課題 / Problem statement

- 定額エージェント経路の入力側が未実装。構造化応答を安全に検証し既存レビュー機構へ流し込む取込面（spec の設計ギャップ (2)(5)）が無い。

## 2) 背景 / Context

- 再利用する信頼境界: zip_import の制限値・markdown_sanitize・document/view import の寛容/厳格検証・merge items→選択レビュー→原子的適用・merge-decision-logs・PatchWorkspace（lint/conflict/採否/ロールバック）。本Issueは**パーサ＋変換＋グルーピング表示**のみを新設する。

## 3) 判断基準による優先度評価

- 価値（P-03/P-04）: 外部の思考結果を、レビュー追跡可能な提案として取り込む HIL の完成。EXT-AGENT-01 と対で要件Dを充足。
- 安全: 非信頼データ境界。禁止フィールド破棄（反スコアリング）・サニタイズ・自動確定なしをテスト固定。
- 規模拡大: あらゆる定額エージェントに対応（契約準拠なら取り込める）。
- 後方互換: スキーマ変更なし（提案は既存型・PatchV1 を運搬するのみ）。

## 3.2 非目標 / Non-goals

- 外部からの自動受信（Tier 1/2）。応答の自動適用・自動レビュー昇格。エージェント出力品質の補正（壊れた JSON の再依頼は運用定型文＝EXT-AGENT-03）。ローカルLLMによる反映経路（要件D (a)・別判断）。

## 4) 提案する解決策 / Proposal solution

- `import/agent_response_import.ts`（新規）: フェンス付き JSON 抽出→スキーマ検証（厳格/寛容）→禁止フィールド破棄＋警告→全文字列サニタイズ→容量制限。
- 変換: spec §4.3 の対応表どおり既存面へ（すべて AI 由来・未レビュー）。patch は lint→conflict 検出→PatchWorkspace へ。orphaned targetRef は破棄せず「孤立提案」として保持表示。
- 整合: baseDocSignature 照合・taskId 相関・同一応答の再取込は冪等。取り込みイベントを context-audit（operation=proposal）へ記録。
- UI: 「応答を取り込む」（貼付け＋ファイル）。取込結果サマリ（受理 n・警告 m・破棄フィールド一覧）。

## 5) 受け入れ条件 / Acceptance criteria

- [ ] AC-1: 正常応答の取り込みで、5種別が各既存面に未レビュー提案として出現することが e2e で固定される（採用→⌘Z 復帰含む）。
- [ ] AC-2: score/rank/confidence を含む応答で、寛容=破棄＋警告・厳格=拒否となることが integration で固定される。
- [ ] AC-3: baseDocSignature 不一致の patch が黙って適用されず conflict/rediff 経路に乗る。orphaned 提案が保持表示される。
- [ ] AC-4: 同一 taskId＋同一応答の再取込が重複を作らない（冪等）。
- [ ] AC-5: 応答中の指示的文言が表示のみで、自動動作に接続しない（コードレビュー＋テストで確認）。
- [ ] AC-6: 「自動確定なし」（取り込み直後に文書が変化しない）がテストで固定される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 パーサ＋検証＋サニタイズ（unit/golden）。
- [ ] T2 種別→既存面への変換（taskId グルーピング・孤立提案保持）。
- [ ] T3 staleness（署名照合・conflict/rediff 接続・冪等）。
- [ ] T4 取込 UI＋結果サマリ＋i18n。
- [ ] T5 監査（context-audit）＋integration/e2e 一式。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`（模擬応答フィクスチャで書き出し→取込→採用→取消のラウンドトリップ）

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（取込は明示操作の面のみ） / 保留操作の距離=不変（提案の保留=held は既存決定語彙で1操作） / 取り消し導線=あり（採用は ⌘Z・patch はロールバック・取込自体は文書を変えない）

## Traceability

- Related: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `02_Architecture/external_agent_collaboration_spec.md`（§4/§5/§6）
- Related: `01_Plans/issues/issue-EXT-AGENT-01-agent-task-package-export.md`, `issue-CE3-patch-workspace-presets.md`, `issue-QA-MONKEY-01-safemode-export-boundary.md`
- Derived-from: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`
