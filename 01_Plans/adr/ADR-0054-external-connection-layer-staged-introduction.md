# ADR-0054: 外部接続レイヤーの段階導入 ― ガラス箱の共有文脈を MCP で公開する

- Status: Proposed
- Date: 2026-07-12
- Deciders: Project Maintainers
- Scope: `03_Implement/backend/`, `03_Implement/frontend/src/export/`・`src/import/`（契約共有）, `01_Plans/`, `02_Architecture/`, `THREAT_MODEL.md`

## Context

- リサーチ（`01_Plans/research-2026-07-12-trigger-ai-external-integration.md`＋同日追補）の結論: トリガー型AI（頼まれず動くAI）はプラットフォーマーの主戦場になったが、トリガー面・配信面は変動が激しい。kj-atlas は前面を取りに行かず、**日常ツールの背後に立つ「認識論的ガバナンス付きの共有文脈基盤」**になる。競合する記憶基盤（mem0/Zep/Letta/knowledgeplane 等）には「この記憶はレビュー済みか・保留中か・根拠は何か・誰が承認したか」の層が丸ごと欠けており、kj-atlas のドメインモデルはこの空白の形をしている。
- 追補で確定した外部事実: (i) MCP は Linux Foundation 傘下 AAIF へ移管済みで 2026-07-28 に大型仕様改訂（ステートレスコア・OAuth 2.1 リソースサーバー正式化）が確定、(ii) ChatGPT Developer Mode / Copilot Studio / Claude の3エコシステムすべてが MCP クライアント対応済み（ただし ChatGPT はリモートHTTPS必須・個人プランは読み取り専用強制）、(iii) TRACE（arXiv:2606.13174）は「Mem0 記憶でも選好違反が57.5%残る」ことを示し、訂正は記憶でなく**実行時制約**として渡す必要があるという役割Cの前提を定量的に裏付けた。
- 既存資産との関係: `ADR-0028` CE-4 は ContextQuery/Bundle の API/CLI 提供を既に予定している（本ADRはその外向き部分の具体化）。`ADR-0049`（外部定額エージェント連携）は copy/paste の**手動レーン**として `agent-task.v1` / `agent-response.v1` 契約とその安全境界（SafeMode本文redaction・未レビュー既定除外・反スコアリング・proposal-only・sanitize-on-import）を実装・検証済み（EXT-AGENT-01/02/03 Done）。本ADRは**同じ契約と安全境界の自動輸送版**であり、新しい安全判断をなるべく増やさない。
- 再起票基準: `ADR-0047` R-2（外部接続という新たな不可逆境界の導入）に該当するため ADR とする。

## Decision

外部接続レイヤーを次の3段階で導入する。**各段階は独立に停止可能で、後段が前段の安全原則を弱めることはない。**

### 段階1 — read-only MCP サーバー（最小リスク）

- ContextBundle IR（CE-0 契約の形）の**制約付き投影**を MCP resources/tools として公開する: reviewed-only / evidence subset / contradiction subset / 島・関係の要約等。
- 安全境界は ADR-0049 のエクスポート側をそのまま適用: SafeMode 既定ON（本文 redaction）、未レビュー既定除外、score/rank/confidence/priority 語彙の不使用、`bundleHash`/`queryCanonicalHash` による監査相関。
- 書き込みツールを一切持たない。
- 輸送: stdio（ローカル Claude Code / Claude Desktop）を先行実装し、streamable HTTP + OAuth 2.1（2026-07-28 仕様）を追加して ChatGPT / Copilot Studio へ到達する。ChatGPT 個人プランの読み取り専用強制は本段階の設計と外部制約が一致していることを意味する。
- 実装は CE-1 の実データ化を待たず、EXT-AGENT-01 が確立した DocumentV2 直接走査＋SafeMode境界の投影ロジックを再利用して開始できる（前例: EXT-AGENT-01 のスコープ判断）。ContextBundle IR の契約形は CE-0 を正とし、輸送（MCP）は薄いアダプタに留める（R4対抗）。

### 段階2 — webhook → 提案カード ingest（proposal-only 書き込み）

- 外部エージェントの観察・ブリーフを `agent-response.v1` 互換 payload として HTTP で受け、**提案（未レビュー・自動確定なし・個別undo可）としてのみ**着地させる。
- EXT-AGENT-02 のパーサ・サニタイズをそのまま再利用: 禁止フィールド除去（lenient）/拒否（strict）、orphan 提案の保持、stale patch のファイル退避、解析だけでは文書を変えない原則。
- トリガー型AIの使い捨て出力（ephemeral な会議前ブリーフ等）の「堆積場」となり、人間が後から KJ 法的に問題を立ち上げる素材にする（リサーチ役割D）。

### 段階3 — critique/constraint の機械可読エクスポート（訂正ループの輸出）

- 人間がエージェント由来カードへ付けた違和感タグ・保留・却下を、**次回以降のエージェント実行への制約**として機械可読に輸出する（`agent-task.v1` のガードレール節拡張、または独立の constraint 文書）。
- TRACE の知見（訂正→原子ルール→実行時強制）に接続する。違和感は理由不要（domain.md）のまま輸出できる形式とし、説明責任を人間に課さない。
- 仕様設計を要するため最後に置く。効果は最大（「同じ誤りを繰り返すAI」への、記憶ではなく制約による訂正チャネル）。

### 採用理由

- 順序はリスク昇順: 読み取り公開（既存の SafeMode/投影契約の再利用のみ）→ proposal-only 原則で守られた書き込み → 新規仕様設計を要する訂正輸出。
- ADR-0049 手動レーンで契約と安全境界が実地検証済みのため、本ADRで新設する安全判断は「公開エンドポイントの認証・認可」に集中できる。
- kj-atlas は「Agent Inbox（処理すべき受信箱）」ではなく「庭（処理義務のない余白）」であり、critique は notify/question/review に続く第4のHITLパターンとして差別化される（追補A5）。

### 非目標

- トリガー/スケジューラ面（カレンダー監視・定期実行等）の実装。前面はプラットフォーマーのものを使う。
- 通知プッシュ。エージェントは庭に書き込み、人間は好きな時に見る。
- Consensus（レビュー済み層）への直接書き込み。human approval を経ない昇格は今後も存在しない。
- 行動テレメトリ・利用計測（ADR-0042 非監視制約の維持）。
- MCP Apps（チャット内サーバー描画UI）の実装。役割B「なぜ？リンク」の将来オプションとして記録のみ。
- リアルタイム共同編集。

## Consequences

- 期待される効果: 1つのサーバーで3大エコシステムに到達し、ADR-0049 手動レーンが自動化される。「エージェント記憶側の訂正ループ」と「キャンバス側の意味形成」を認識論的状態で結合した共有マップという空白（リサーチ§4）を先行確保する。
- 副作用/制約: (i) HTTP輸送時は OAuth 2.1 リソースサーバー運用が入る（鍵管理・トークン検証）。公開面の追加は `THREAT_MODEL.md` の更新と、PRODUCT-QA-01 ゲートでのセキュリティ照合を実装前提とする。(ii) 段階2の受信エンドポイントは悪性入力の一次面になるため、EXT-AGENT-02 の sanitize を強制経路とし、バイパス経路を作らない。(iii) 監査導線（CE-4: query log / ingest log）の整合が各段階の Exit Criteria に入る。
- 移行時の対応: 段階1は新規サービスまたは既存 backend への同居のどちらでも成立する（実装issueで決定）。ContextBundle IR が輸送非依存である限り、MCP 仕様改訂への追随はアダプタ層の改修に閉じる。

## Traceability

- Related: `01_Plans/research-2026-07-12-trigger-ai-external-integration.md`（Context の根拠。追補含む）
- Related: `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`（CE-4 の具体化）
- Related: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（契約・安全境界の正本。本ADRはその自動輸送版）
- Related: `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`（再起票基準 R-2）
- Related: `THREAT_MODEL.md`, `01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md`（非監視制約）
- Related: `01_Plans/issues/issue-EXT-CONN-01-readonly-mcp-server.md`, `issue-EXT-CONN-02-webhook-proposal-ingest.md`, `issue-EXT-CONN-03-critique-constraint-export.md`（実装Issue、Draft）

---

## Authoring Checklist（人間/生成AI 共通）

- [x] 必須ヘッダ（Status/Date/Deciders/Scope）を記載した。
- [x] 必須章（Context/Decision/Consequences/Traceability）を記載した。
- [x] Decision に採用理由と非目標がある。
- [x] Traceability に関連文書を1件以上記載した。
- [x] 実装進捗は ADR ではなく Issue で管理する前提を維持した。
