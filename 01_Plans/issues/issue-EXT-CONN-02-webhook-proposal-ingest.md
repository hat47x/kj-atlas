# Issue Draft: EXT-CONN-02 Webhookによるproposal-only取り込み（トリガー型出力の受け皿）

- Type: Feature request
- Status: Draft
- Source Issue: N/A（`ADR-0054` 段階2）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/backend/`（受信エンドポイント）, `03_Implement/frontend/src/import/agent_response_import.ts`（サニタイズの共有）, `THREAT_MODEL.md`
- Related Backlog: `EXT-CONN-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`, `01_Plans/issues/done/issue-EXT-AGENT-02-agent-response-import.md`（サニタイズ・提案着地の正本）, `01_Plans/issues/done/issue-DATA-MODEL-OPS-02-management-plane-data-boundary.md`（D3登録・認可境界）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-CONN-02
- RequirementStatement: 外部エージェントの観察・ブリーフを `agent-response.v1` 互換payloadとしてHTTPで受信し、未レビューの提案カードとしてのみ着地させる。自動確定は行わず、採用後も個別に取り消せることを保証する。
- AcceptanceScenario: 前提=EXT-CONN-01が稼働し、ADR-0054がAcceptedである / 操作=外部エージェントがWebhookへ観察をPOSTする / 期待結果=出力が未レビュー提案として着地し、人間が採用するまで文書本体は変化しない / 除外=Consensusへの直接書き込み、自動採用、通知。
- SecurityGateImpact: import-sanitize / SafeMode / public-exposure
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef: `ADR-0054` はAccepted済み（2026-07-12）、`DATA-MODEL-OPS-02` D3はFixed済み（2026-07-13）。残るゲートは **EXT-CONN-01の運用実績 + D3の契約先行同期・admin認可実装/検証**。通常ownerが登録・失効できず、wrong/revoked/wrong-document tokenが拒否されるまではDraftを維持する。

## 背景

トリガー型AIの出力（会議前ブリーフなど）は、その場限りの情報として流れて消えやすい。これを「提案カード」としてキャンバス周縁へ残し、人間が後からKJ法的に問題を立ち上げる材料として使えるようにする（リサーチ役割D）。書き込み経路では、`EXT-AGENT-02` が確立したproposal-only原則とサニタイズを必ず通し、別経路から回避できないようにする。

現行のMCPはADR-0054段階1として意図的に読み取り専用であり、本issueはMCPへ直接write権限を加えるものではない。外部から届いた内容を、既存の信頼境界を通した未レビュー提案として受け取ることが責務である。

## 2026-09-02 継続dogfoodから得た実使用証拠

KJ Atlas自身を外部AIと継続的に分析するdogfoodで、次の摩擦を実際に観察した。

- 外部AI側からカードや島を育てながら共同分析したい場面があったが、今回のChatGPT接続環境にはKJ AtlasのMCP自体が公開されていなかった。
- 製品側のMCPも、設計どおり読み取り専用である。この二つは別の制約であり、混同しない。
- `EXT-AGENT-02` により、貼り付け・ファイルから `agent-response.v1` を未レビュー提案へ安全に取り込む経路はすでに存在する。そのため、共同分析そのものが不可能なわけではない。
- ただし、長く続く共同分析では、外部AIが成果を書き出し、人が手動で取り込む受け渡しが、思考の流れやカードの系譜を切る摩擦になり得る。
- この観察が示しているのは「MCPに直接writeが必要」ということではなく、「proposal-onlyの安全境界を保ったまま、提案の受け渡しを短くできるか」という本issueの問いである。

この観察は、認知dogfoodの振り分けではF1（既存issueへの証拠追加）として扱う。現時点では一回の観察なので、PriorityはP2のままとし、着手ゲートも変更しない。同種の共同分析で手動受け渡しの負担が反復し、思考の継続性やレビュー可能性へ実害を与えることが確認できた場合に、優先度と着手時期を改めて判断する。

正規のdogfood記録:

- `01_Plans/dogfood/doc_kj_atlas_dogfood_r7.json`
- `01_Plans/dogfood/cognitive-dogfood-continuous-2026-09-02.md`

## 提案する解決策

- 認証必須の受信エンドポイントで `agent-response.v1` 互換payloadを受け、`EXT-AGENT-02` のパーサとサニタイズを強制経路として通す。禁止フィールド（score/rank/confidence/priority）は除去または拒否し、orphan提案は保持し、stale patchは適用を拒否する。解析だけで文書本体を変更しない。
- 着地先は常に未レビュー提案とする。採用は既存のper-proposal Importを通し、採用後も個別に取り消せるようにする。
- 由来（agent名・taskId相関）を保持し、AI由来の視覚区別（ADR-0048 D1）につなぐ。
- ingestログを監査導線（CE-4）へ残す。
- 運搬手段を理由に検証規則を分岐させず、貼り付け・ファイル取り込みとWebhook取り込みで `agent-response.v1` の意味、安全境界、監査原則を共有する。

## 非目標

- 自動採用、Consensusへの直接書き込み。
- MCP段階1へwrite権限を追加すること。
- 通知のpush。着地は静かに行い、人間が必要なときに確認する。
- トリガー側、すなわち「何を、いつ観察するか」の実装。

## 受け入れ条件（案）

- [ ] AC-1: 正常payloadが未レビュー提案として着地し、人間がImportするまで文書本体が変化しない。
- [ ] AC-2: 禁止フィールド、不正schema、stale patchが `EXT-AGENT-02` と同じ規則で処理され、別経路からバイパスできない。
- [ ] AC-3: 認証なしのPOSTは拒否される。受信面の脅威が `THREAT_MODEL.md` に追記される。
- [ ] AC-4: ingestごとに、由来・taskId相関・処理結果を含む監査ログが残る。
- [ ] AC-5: 着地した提案が外部由来と識別できる。視覚言語はClaude Design P32回答で方向確定済みとし、メタ行の出所チップ（「⌂ agent名」、型バッジの後）＋「非人間由来」共通マーク（ADR-0048 D1拡張・色チャネル新設なし）を用いる。受け皿はキャンバス周縁の**縁側レーン**（正式用語はADR-0054用語定義。P32回答時の呼称は「庭」）とし、多数時は集約チップ「外部から n件」を表示する。通知バッジは使わない。レッドラインは実装ラウンドで受領する。
- [ ] AC-6: 同じ `agent-response.v1` を手動取り込みした場合とWebhook経由で取り込んだ場合で、proposal-only、禁止フィールド処理、由来保持、採否・取消の意味が一致する。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/issues/done/issue-EXT-AGENT-02-agent-response-import.md`
- Dogfood evidence: `01_Plans/dogfood/doc_kj_atlas_dogfood_r7.json`, `01_Plans/dogfood/cognitive-dogfood-continuous-2026-09-02.md`
- Related implementation: `03_Implement/frontend/src/import/agent_response_import.ts`
