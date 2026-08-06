# kj-atlas 活用の到達像 4例 — 機能要件の考察とローカル小規模試行（受入条件）

作成: 2026-07-23 / 対象コミット: `main`（origin と同期）
成果物種別: **設計・定義のみ（コード・既存 issue/ADR は不改変）**。本書は 4 つの活用具体例を、既存の価値→要件フレームワーク（VR 系列 / GENAI-GOV レーン / CVI / EXT-CONN 段階導入）へ接地・トレースし、各例に「開発機で走らせられる小規模試行」を受入条件として提案する。**試行は定義のみで実行しない**。

---

## 0. 接地方針と統合マップ（重複フレームワークを新設しない）

本書は新しい価値クラスタや並行ロードマップを作らない。4 例を既存の 4 つの索引へ**再配置**する:

- **価値ループ V0–V4 と社会目標系列 VR0–VR5**（`ADR-0032`, `value_traceability.md:44-114`）。
- **生成AIレーン A–D**（`GENAI-GOV-01`, `value_traceability.md:230-251`）。
- **根幹価値不変条件 CVI-1..7**（`ADR-0041`, `value_traceability.md:168-181`）。
- **外部接続の段階導入 EXT-CONN-01..04**（`ADR-0054`、issue 群）と**外部エージェント成果物連携**（`ADR-0049` / `02_Architecture/external_agent_collaboration_spec.html`）。

### 0.1 4 例 × 既存索引 対応表

| 具体例 | 主たる VR フェーズ | 主たるレーン | 正本 ADR/spec | 現フェーズ内で「既に在る」中核 | 主なギャップの所在 |
|---|---|---|---|---|---|
| 1. LLMと人間の協調キャンバス | VR2/VR3 | Lane A/B | `ADR-0028`(D11 三層グラフ), `ADR-0048`(視覚言語/憲章), `ADR-0055`(作業モード) | Working/Projection/Consensus 分離・proposal-only・Query Preview 必須・AI提案タブ | 「住み分け」の**操作レベルでの検証可能な契約**が未固定。AI出力の MMI 品質（`ai-prompt-core-redesign` G1-G7） |
| 2. LLMの外部頭脳 | VR2/VR3 + CE-1/CE-4 | Lane B + EXT-CONN | `ADR-0028`(**正本**), `ADR-0057`(W型累積) | ContextQuery/Bundle 決定論基盤・EXT-CONN-01 read-only MCP（**Done**）・provider=none 成立 | 自律的判断の**proposal-only 束縛実装**・クエリ語彙の拡張・InquiryJourney 永続（L0 Planned） |
| 3. 組織情報統合コックピット | VR3/VR4 + EXT-CONN | Lane C | `ADR-0032`, `ADR-0049`, EXT-CONN-02/03 | 成果物パッケージ(V4)・外部エージェント成果物連携(Tier 0)・merge/summary 候補 | 自動整理ループ(EXT-CONN-02 Draft)・**組織横断コックピット**（現行は単一文書）・アクション展開(EXT-CONN-03 Draft) |
| 4. 行政-企業-民間 対話プラットフォーム | VR5 + SaaS | Lane C/D | `ADR-0038`(**正本**), `ADR-0059`(マルチテナント) | 対立非解消/一匹狼保護の憲章・矛盾/根拠リンク・SafeMode 安全共有・EXT-CONN-04 露出規則の前例(共有前確認) | 敵対ステークホルダー協調=SaaS ゲート未完 + SOCIAL-DIFFUSION 全 Draft（活性化延期）。PM ツール協調 |

### 0.2 全試行が侵さない不変条件（試行自体が検証する）

- **提案のみ・自動確定なし**（CVI-2, `ADR-0028:56`）。`human_reviewed` 昇格は人手のみ（CVI-3, `ADR-0028:58`）。
- **SafeMode 既定 ON・未レビュー本文は共有/エクスポート境界を越えない**（CVI-1, `ADR-0028:279` Guard-01, `safe_mode.ts:23-25`）。
- **対立/少数意見の自動解消禁止・一枚一志・一匹狼の保護**（CVI-7, `ADR-0048:40,49`）。
- **非監視型**（`SOCIAL-DIFFUSION-04`）。採用シグナルは監視的手段で取らない。

### 0.3 接地上の既知の注意（試行設計で前提にする）

1. **CVI-1 の砦は挙動でなく文字列を検査している**。`core_value_guard.test.ts:22-26` は `safe_mode.test.ts` の**ソース文字列**を `toContain` するだけで、実際の egress を検査しない。かつ `document.json` 経路に P0 の漏えい（`SEC-EXPORT-BUNDLE-01`, `bundle_export.ts:254,313`、`architecture-coherence-synthesis-2026-07-23.md:18` で確認）が残る。**本書の SafeMode 試行はすべて「番兵秘密が出力に現れないこと」を挙動で確かめる形にし、この弱点を試行側で補う**（同 synthesis 推奨 1c と整合）。
2. **検証系は WSL 側チェックアウトでのみ実行可能**（ユーザーメモ: native npm/Preview 不可、`/mnt/c/...` は node_modules を壊す）。試行の実行コマンドは WSL 側 frontend/mcp/backend チェックアウト前提で記す。**本書は定義のみ**。
3. **InquiryJourney（W型累積）は L0: Planned**。型・bundle I/O・比較・分岐は実装済みだが、backend 永続と保存・再開・SafeMode 派生共有は未実装（`value_traceability.md:152-164`）。具体例2の「情報蓄積」の長期側はここに依存。
4. **SaaS は Accepted だが Implementation gate 未完**（`ADR-0059:105-114`, `SAAS-TENANT-01` In Progress, 越境 negative E2E は `QA-E2E-SAAS-01` 未実施）。具体例4のマルチ組織基盤はここに依存。

---

## 具体例1: LLMと人間との協調キャンバス（適切な MMI・住み分けの設計）

### 1-1. 位置づけ・現状

**対応する価値・ADR・コード**: この例は価値ループ V3「レビュー」（`ADR-0032:33`）を中核に、Lane A/B（`value_traceability.md:236-237`）で成立する。「住み分け」の骨格は既に **`ADR-0028` D11** が三層グラフとして固定している。

**既に在るもの**:
- **三層グラフによる住み分けの正本定義**: Working Graph（主体別探索）/ Context Projection Graph（問い合わせ投影）/ Consensus Graph（合意済み）（`ADR-0028:324-328`）。Consensus への反映は patch + approval のみ（`ADR-0028:334`, CG-02）。
- **人間の空間文脈は AI へ「補助信号のみ」**、一次入力は KJ 構造＋構造化メタに限定（`ADR-0028:295` Gate-1）。これが MMI の住み分けの根幹。
- **proposal-only と人手レビュー昇格**が挙動テストで担保（CVI-2/3, `core_value_guard.test.ts:29-63`）。AI は候補生成器、`human_reviewed` は人手のみ。
- **Query Preview 必須・バイパス禁止**（`ADR-0028:296` Gate-1）。実装は `query_preview.ts:67-87`（`previewConfirmed` が false なら `canSubmit=false`, `buildQueryPreviewState:75`）。
- **AI 用サーフェスの物理分離**: 作業モードの 5 タブに「AI提案」を独立面として置く（`ADR-0055:17`「差分、選択マージ、AI提案、診断、文章化」）。非選択パネルは DOM 保持で状態を失わない（`ADR-0055:17`）。
- **視覚言語による人間/AI 由来の識別**: amber を保留・違和感に予約、AI 由来の識別マーク（`ADR-0048:26,40`）。
- **PatchWorkspace（CE-3）** で AI 提案の比較・部分採用・保留・破棄が可逆（`ADR-0028:90-101`）。

**ギャップ**:
- 住み分けは**アーキ/契約レベルでは固定済みだが、「人間の担当 vs AI の担当」を対話操作レベルで一枚の検証可能な契約として提示する成果物が無い**。GENAI-GOV レーン表（`value_traceability.md:234-239`）は存在するが in-product には出ない。
- **AI 出力の MMI 品質が弱い**。backend 5 プロンプトは出力言語指定・反スコアリング・KJ 憲章が欠落（`ai-prompt-core-redesign-2026-07-23.md:48-52` G1-G3）。住み分けが成立しても AI 提案文の質が低ければ MMI として不足。
- 「AI 提案 → 専用面でレビュー → 採用/保留/却下 → 可逆」の全ループを**単一の MMI 契約として通す受入試行が無い**（個別 e2e は存在: `keyboard_release_candidate_flow.spec.ts` 等）。

### 1-2. 機能要件（考察〜具体化）

- **FR1-1（既存の統合・新規実装なし）**: GENAI-GOV レーン表（`value_traceability.md:230-251`）と `ADR-0028` D11 三層グラフを、作業モード「AI提案」タブ（`ADR-0055`）の**運用契約**として索引化する。要件本体は既存で被覆済み（`value_traceability.md:129` V3）。**新規要件ではなく、既存契約の運用面への接続**。過剰スコープ回避のため in-product レーン表 UI は作らない。
- **FR1-2（`ai-prompt-core-redesign` の drop-in 適用の要件化）**: backend 5 プロンプトの地の文へ、出力日本語化・反スコアリング固定文・KJ 憲章（一枚一志/一匹狼）を追加（`ai-prompt-core-redesign-2026-07-23.md` 第2章）。**schema リテラルとデータ行は不変**（SafeMode 面・パーサ契約を後退させない）。これは MMI 品質要件であり、Lane B の proposal-only を変えない。トレース先は既存の再設計文書（正本は `llm_quality_strategy.md` 第3章ルーブリック）。
- **FR1-3（住み分けの操作契約の検証可能化）**: 「AI が触れてよいのは Working/Projection、Consensus は人手 patch+approval のみ」を、AI提案タブでの採用フローに対する回帰試行として固定（下記 T1-A）。既存 CVI-2/4 を作業モード面へ延伸するもので、新不変条件は追加しない（`ADR-0041:45` 非目標に整合）。

### 1-3. 受入条件＝ローカル小規模試行

**T1-A: MMI 住み分けループ（AI 提案 → 人手レビュー → 可逆）**
- 前提/セットアップ: WSL frontend チェックアウト。`KJ_ATLAS_LLM_PROVIDER=none`（CVI-6）。SafeMode 既定 ON。fixture は `product_value_fixtures.ts` の `buildDomainExpressionDocument()`（既存）で 5〜8 枚のカード・1〜2 島。
- 操作: (1) 作業モードを開き「AI提案」タブへ（`ADR-0055` の manual activation、左右矢印で移動・Enter で確定）。(2) 島タイトル候補を要求（provider=none のため `ce2_suggestion_candidates` の決定論フォールバックが proposal-only 候補を返す）。(3) 候補を 1 件「採用」。(4) `⌘Z` で取り消す。
- 観測可能な期待結果（機械判定可能）: 候補は必ず `reviewState=unreviewed` の提案として出現し、採用しても `human_reviewed` へ**自動昇格しない**（CVI-3）。Consensus への直接書き込みが発生しない（CVI-4）。採用は 1 履歴ステップで `⌘Z` により完全復元（CVI-5 の可逆性思想）。番兵として「AIが確定した」旨のバッジ・自動公開が**存在しない**ことを DOM で確認。→ 既存 `core_value_guard.test.ts` の CVI-2/3/4 索引と、新規 e2e 1 本（AI提案タブ経由の採用→undo）で判定。

**T1-B: Query Preview ゲートと SafeMode 整合（ユニット）**
- 前提: `query_preview.ts` のユニット試行（vitest）。
- 操作: `ContextQueryDraft` を (a) `previewConfirmed=false`、(b) `safeModePolicy="strict"` かつ `reviewFilter="includeUnreviewed"` の 2 パターンで `buildQueryPreviewState` に通す。
- 期待結果（機械判定）: (a) は `canSubmit=false` かつ blockers に `"previewConfirmed must be true before submit"`（`query_preview.ts:75`）。(b) は blockers に `"safeMode strict requires reviewFilter=reviewedOnly"`（`query_preview.ts:72-74`）。→ Preview バイパス不可・SafeMode strict 下で未レビュー投影不可を挙動で固定（不変条件検証）。

---

## 具体例2: LLMの外部頭脳としての活用（情報蓄積〜自律的判断〜効果的クエリ）

### 2-1. 位置づけ・現状

**正本**: `ADR-0028`（認知外在化の正本）と `ADR-0057`（W型累積探究）。VR2「曖昧さネイティブ作業」＋ CE-1/CE-4 のクエリ基盤（`value_traceability.md:107,110`）。

**既に在るもの**:
- **効果的クエリの決定論基盤（CE-1）**: `ContextQuery`（goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode）と決定論 `bundleHash`（`ADR-0028:56` CE0-CTX-IF）。実装は frontend `query_preview.ts:47-65`（canonical hash）と backend `context.py`（`/context/query:39-46`, `/context/bundle:49-72`、決定論違反は 409 `nondeterministic_bundle` `context.py:60-61`）。
- **外部頭脳への「読み取りクエリ」= EXT-CONN-01 read-only MCP が実装済み・Done**（`EXT-CONN-01` close-out `:119-125`, `PR #2602` merge）。外部エージェント（Claude Code/ChatGPT/Copilot）が `get_context_projection({docId, constraint, safeMode?})` で kj-atlas を知識源として問い合わせできる。制約は `reviewed-only | evidence | contradiction | summary`（`mcp/README.md:16-19`）。書き込みツールはゼロ（`context_projection_tool.test.ts:53-77`）。
- **蓄積の中核（W型累積）**: `InquiryJourneyV1` + 不変 `RoundSnapshotV1` DAG + `CardLineageEdgeV1`（`ADR-0057:96-102`）。現場との往復・前段階分岐・停止再開を非破壊で保持（`ADR-0057:116-118`）。
- **provider=none で蓄積・構造化・共有前確認が成立**（CVI-6, `value_traceability.md:179`）。外部頭脳は「LLM 無し」でも一次的に成立。

**ギャップ**:
- **「高度な自律的判断」は proposal-only に束縛したまま実装が無い**。`ADR-0028` D11-2 決定B は `mode=autonomous`（AI 単独運用の Working Graph）を許すが（`ADR-0028:320`）、CG-03 が「autonomous でも safeMode/監査契約を緩和しない」と縛る（`ADR-0028:340`）。自律ループの実装は未着手で、**入る場合も CVI-2/3 を越えてはならない**。
- **クエリ語彙が固定 4 制約**（`mcp/README.md:16`）。claimType 別・矛盾駆動などの「より効果的なクエリ」は自然な拡張だが未実装（`ai-prompt-core-redesign-2026-07-23.md:56` G5 が同方向を指摘: claimType/矛盾を入力へ）。
- **InquiryJourney の永続は L0: Planned**（`value_traceability.md:152`）。長期蓄積の backend 保存・再開は未実装。
- **過去の違和感を次回クエリの制約として渡す EXT-CONN-03（constraint export）は Draft**（`EXT-CONN-03` DecisionStatus Pending, `:23-24`）。契約 `agent-constraints.v1` は `schemas.md §18` に先行固定済みだが実装未了。

### 2-2. 機能要件（考察〜具体化）

- **FR2-1（既存 EXT-CONN-01 の運用実績化）**: read-only MCP を外部頭脳クエリの一次経路として運用検証する。**新規実装は不要**（Done）。これは EXT-CONN-02/03 が待つ「EXT-CONN-01 の運用実績」ゲート（`EXT-CONN-02:24`, `EXT-CONN-03:24`）を埋める作業でもあり、具体例3/4 への波及が大きい。
- **FR2-2（クエリ語彙の加算拡張・現フェーズ内の小拡張）**: `constraint` に「claimType 別投影」を加算する候補。ただし SafeMode 面を変えないこと（構造ラベルは低リスク、KA voice/value 等の散文追加は不可、`ai-prompt-core-redesign-2026-07-23.md:57` の SafeMode 注意）。**EXT-CONN-01 の投影コア `context_bundle_projection.ts` の加算**として設計し、新輸送を作らない（EXT-CONN 段階原則）。
- **FR2-3（自律的判断の境界の明文化・現フェーズ外の実装）**: `mode=autonomous`（`ADR-0028:320`）の実装は **Lane B/D の判断ゲート**に属し現フェーズ外。着手時は CG-03（`ADR-0028:340`）と GENAI-GOV Lane D 起票条件（`GENAI-GOV-01:96,137`）に従い、実装 PR ではなく ADR を先行。本書はこの束縛の**受入試行のみ**を定義する（T2-C）。
- **FR2-4（長期蓄積の永続・現フェーズ外）**: InquiryJourney backend 永続は `DOMAIN-W-ITERATION-01`（In Progress）と `PERF-INQUIRY-01` の完了後。現フェーズはローカル bundle I/O まで（`value_traceability.md:154`）。

### 2-3. 受入条件＝ローカル小規模試行

**T2-A: 外部頭脳への reviewed-only クエリ（MCP ライブ試行）— 最重要**
- 前提/セットアップ: WSL で backend 起動（`KJ_ATLAS_LLM_PROVIDER=none`、SQLite）。小文書を 1 件保存: reviewed カード N=2（`textReviewed:true`）＋ unreviewed カード M=2（`textReviewed:false`）（`context_projection_tool.test.ts:20-32` の fixture 形状に準拠）。`03_Implement/mcp/` を stdio で起動（`KJ_ATLAS_MCP_TRANSPORT=stdio`、`KJ_ATLAS_MCP_API_BASE_URL` を backend へ）。
- 操作: MCP クライアントから `get_context_projection({docId, constraint:"reviewed-only"})` を `safeMode` 省略で呼ぶ。
- 観測可能な期待結果（機械判定）: (1) 返るカード id は reviewed のみ（unreviewed の id が**いかなる形でも現れない**）。(2) `safeMode` 省略時 true が既定で、reviewed カードの本文も redact される（`redacted:true`、共有境界扱い、`context_projection_tool.test.ts:97-100`）。(3) 出力に `score|rank|confidence|priority` が現れない（`:127`）。(4) 監査行が stderr に `mcp-context-read.v1` として出て `bundleHash`/`queryCanonicalHash` が 64hex（`:157-160`）。stdout には監査行が混入しない（`:163`）。→ **不変条件（SafeMode 境界・未レビュー除外・反スコアリング・監査）を一度に検証**。既存 `context_projection_tool.test.ts` をライブ経路で再現する形。

**T2-B: 蓄積クエリの決定論（backend 契約試行）**
- 前提: backend 起動、provider=none。
- 操作: `POST /context/query`（`previewConfirmed=true`）を同一 payload で 2 回。続けて `POST /context/bundle`。次に `previewConfirmed=false` で 1 回。
- 期待結果（機械判定）: 2 回の query は同一 `queryCanonicalHash`（`context.py:45-46`）。bundle は決定論検証を通り（`context.py:60-61` の 409 が出ない）同一 `bundleHash`。`previewConfirmed=false` は 422 `preview_required`（`context.py:42-43`）。→ 「同一クエリ＝同一投影」で外部頭脳の再現性を固定。

**T2-C: 自律判断は proposal-only に留まる（契約試行・現フェーズ外機能のガード先行定義）**
- 前提: 定義のみ（`mode=autonomous` 未実装のため、着手時に満たすべき受入契約として先行固定）。
- 操作（着手時）: autonomous Working Graph が生成した出力を Consensus へ渡す経路を叩く。
- 期待結果: 出力は `proposalId + diff + rationale` の提案に留まり（`ADR-0028:275`）、`human_reviewed` 自動昇格・Consensus 直接更新・SafeMode 緩和が**発生しない**（CG-03 `ADR-0028:340`、CVI-2/3/4）。→ 自律化しても不変条件が保たれることを、実装前に受入条件として固定（Lane D ADR 起票時の必須 AC 候補）。

---

## 具体例3: 組織全体の収集情報を統合するコックピット（自動整理〜最小人的整理〜戦略/アクション展開）

### 3-1. 位置づけ・現状

VR3「レビュー可能成果物」〜 VR4「価値観測」（`value_traceability.md:108-109`）、Lane C（外部エージェント成果物連携, `value_traceability.md:238`）。単体の正本 ADR は無く、`ADR-0032`（価値ループ）＋ `ADR-0049`/`02_Architecture/external_agent_collaboration_spec.html`（外部エージェント）＋ EXT-CONN-02/03 の合成。

**既に在るもの**:
- **外部エージェントへの思考委任（Tier 0）**: 組織が定額契約した AI（Copilot/ChatGPT Enterprise 等）へ依頼パッケージを渡し、応答を import 境界で取り込む（`02_Architecture/external_agent_collaboration_spec.html` §01 原則）。kj-atlas は文脈供給・検証・レビュー・可逆適用に徹する。
- **応答の proposal-only 着地**: `AgentResponse v1` は種別ごとに未レビュー提案として着地（`02_Architecture/external_agent_collaboration_spec.html` §04 取り込み経路）。実装は `agent_response_import.ts`。禁止フィールド（score/rank/confidence/priority）は破棄/拒否（同 §04 制約）。
- **AI 補助の構造化候補（CE-2）**: 島タイトル候補・merge 候補・矛盾/根拠由来の論点候補（`ADR-0028:78-81`）、すべて proposal-only。
- **「最小人的整理」の成果物化（V4）**: 確定点/保留点/未レビュー/根拠導線/SafeMode 結果を束ねた review pack / narrative（`PRODUCT-VALUE-03` 受入条件 `:30-35`、証跡 `review_pack_trace_export.spec.ts`）。これが「戦略・アクションの読み手向け入力」。
- **トリガー型出力の堆積場（EXT-CONN-02, Draft）**: 会議前ブリーフ等 ephemeral な AI 出力を「提案カード」として縁側レーンへ堆積（`EXT-CONN-02:27-28,49`）。

**ギャップ**:
- **「AI エージェントによる自動整理」の常設ループは EXT-CONN-02 に依存し Draft**（DecisionStatus Pending、残ゲート=EXT-CONN-01 運用実績＋D3 admin 認可, `EXT-CONN-02:24`）。現状の自動整理は CE-2 の単発候補と Tier 0 手動取込まで。
- **「第一級のコックピット」= 組織横断の統合ビューが無い**。現行は単一 `DocumentV1` 中心（`ADR-0057:20` が単一スナップショット運用を明記）。複数文書/組織横断の集約は未定義であり、**新規 ADR を要する領域**（現フェーズ外）。
- **「戦略・具体アクションへの展開支援」= PM ツール協調は EXT-CONN-03（constraint export, Draft）**。契約 `agent-constraints.v1` は `schemas.md §18` に固定済みだが実装未了（`EXT-CONN-03:93` AC-1 のみ充足）。
- **P0 の SafeMode 漏えい（`document.json`）が bundle export に残る**（`SEC-EXPORT-BUNDLE-01`）。コックピットの共有経路を review pack に限定すれば回避できるが、フル bundle 共有は現時点で不可（試行で番兵検査する）。

### 3-2. 機能要件（考察〜具体化）

- **FR3-1（Tier 0 自動整理の運用検証・既存経路）**: 外部エージェント成果物連携（`ADR-0049`）を「組織の収集情報を AI に束ねさせ、proposal として取り込む」自動整理の一次形態として運用検証。**新規実装不要**（`agent_response_import.ts` 既存）。EXT-CONN-02 の webhook 化は現フェーズ外（Draft・admin 認可ゲート）。
- **FR3-2（最小人的整理→成果物の運用検証）**: proposal から人手で島化し review pack を生成する導線（V4）を、コックピットの「戦略入力」出口として運用検証。要件は `PRODUCT-VALUE-03`（Done）で被覆済み。
- **FR3-3（アクション展開=EXT-CONN-03 の段階ゲート順守・現フェーズ外実装）**: critique/hold/reject を `agent-constraints.v1` として輸出し PM ツール側エージェントへ渡す。着手は EXT-CONN-01 subslice C 稼働＋EXT-CONN-02 実装後（`EXT-CONN-03:24`）。opt-in 既定 OFF・未レビュー ID 非露出（件数のみ）を維持（`EXT-CONN-03:37` D4）。
- **FR3-4（組織横断コックピット=現フェーズ外・要 ADR）**: 複数文書/テナント横断の集約ビューは `ADR-0057:20` の単一文書前提と `ADR-0059` テナント境界を跨ぐため、**実装 PR でなく新 ADR を先行**（`GENAI-GOV-01:137`, `value_traceability.md:255-261` の設計判断手順）。本書は near-term を「単一文書 + Tier 0 取込」に限定推奨。

### 3-3. 受入条件＝ローカル小規模試行

**T3-A: AI 自動整理の proposal 堆積（Tier 0 取込のローカル試行）**
- 前提/セットアップ: WSL frontend。SafeMode ON、provider=none。手作りの `agent-response.v1` JSON（`02_Architecture/external_agent_collaboration_spec.html` §04 スキーマ準拠）を模擬応答として用意（島タイトル候補 2 + narrative_draft 1）。
- 操作: 「応答を取り込む」で JSON を貼付（`agent_response_import.ts` 経路）。
- 期待結果（機械判定）: 提案は全件 `unreviewed` で着地し、**人間が採用するまで文書本体（カード/島）が変わらない**（`02_Architecture/external_agent_collaboration_spec.html` §01 原則2、`PRODUCT-VALUE-02` 受入 `:35`）。取込前後で document のカード集合ハッシュが不変。→ 自動整理でも proposal-only を保つことを検証。

**T3-B: 最小人的整理→成果物 6 要素（既存 e2e の受入化）**
- 前提: fixture `buildReviewPackTraceDocument()`（`PRODUCT-VALUE-03` 証跡 `:40`）。
- 操作: 共有前確認を通し review pack を生成、読み取り専用閲覧へ。
- 期待結果（機械判定）: 成果物に確定点/保留点/未レビュー情報/根拠導線/SafeMode 結果が含まれ（`PRODUCT-VALUE-03` 受入 `:30-35`）、read-only 閲覧者が元カード/島/関係/レビュー状態へ戻れる。→ 既存 `review_pack_trace_export.spec.ts` を「コックピット出力」受入として再利用。

**T3-C: 取込時の反スコアリング（番兵試行）**
- 前提: `agent-response.v1` に `score:0.9`・`rank:1` 等の禁止フィールドを混入させた模擬応答。
- 操作: 取込。
- 期待結果（機械判定）: 禁止フィールドは破棄されるか取込拒否（`02_Architecture/external_agent_collaboration_spec.html` §04 制約）。着地提案の直列化に `score|rank|confidence|priority` が現れない（正規表現）。→ 数値評価を採否の正本にしない不変条件を検証。

**T3-D（番兵・現フェーズ外の安全確認）: フル bundle 共有の SafeMode 漏えい検査**
- 前提: 既知 P0（`SEC-EXPORT-BUNDLE-01`）を試行で検出する目的。fixture の未レビューカード本文に一意な番兵文字列 `SENTINEL-XYZ` を入れる。
- 操作: SafeMode ON でフル bundle エクスポート（`bundle_export.ts`）。
- 期待結果: **本来** 生成物のどのファイルにも `SENTINEL-XYZ` が現れないこと。現状は `document.json` に漏える可能性が高い（`architecture-coherence-synthesis-2026-07-23.md:18`）。→ この試行は**現状 fail が期待**であり、コックピット共有を review pack 経路に限定すべき根拠を機械的に示す。修正（synthesis 項目1a/1c）まではフル bundle をコックピット共有に使わない。

---

## 具体例4: 行政-企業-民間の対話情報集積プラットフォーム（敵対的ステークホルダー協調・リスク早期検出・PM ツール協調）

### 4-1. 位置づけ・現状

**正本**: `ADR-0038`（説明可能な合意形成の社会的普及＝VR5）と `ADR-0059`（SaaS テナント境界＝マルチ組織基盤）。VR5（`value_traceability.md:110`）、Lane C/D。

**既に在るもの**:
- **敵対ステークホルダーに本質的な設計憲章**: 対立の自動解消禁止・一枚一志・一匹狼（少数意見）の保護（`ADR-0048:40,49`）。CVI-7 が保留/違和感の非破壊を挙動で担保（`core_value_guard.test.ts:94-107`）。これが「高度な敵対的利害関係」で最重要。
- **矛盾/根拠の保持と人間レビュー**: `EvidenceLink.contradictionState`（unconfirmed/confirmed/held/resolved）と `analyzeContradictions()`（`contradiction_checks.ts`）、矛盾シグナルへの人間決定（採用/保留/却下、`DOMAIN-EXPR-04` Done, `value_traceability.md:62`）。実装は `contradiction_checks.ts`、e2e `contradiction_signal_decision.spec.ts`。→ 「リスク/課題の早期検出」の一次基盤。
- **安全配布の露出規則（EXT-CONN-04 の前例）**: 「なぜ？」根拠トレイルの露出規則は共有前確認と同格＝未レビュー/違和感/保留は既定非表示（`EXT-CONN-04:33-34`）。この規則自体は `pre_share_summary_gate.spec.ts`（Done）で既に成立。
- **マルチ組織基盤の契約**: テナント境界 D5–D10（`ADR-0059:18-104`）。tenant は role でなく構造境界、越境は not-found 相当（`ADR-0059:79`）。
- **社会的普及の 4 本柱の要件化（Draft/延期）**: `SOCIAL-DIFFUSION-01`（複数レビュア再現性）/`-02`（経時的見直し）/`-03`（証拠定着配布）/`-04`（非監視シグナル）（`ADR-0038:26-45`）。

**ギャップ**:
- **敵対ステークホルダー協調の実運用はマルチテナント実装に依存し、Implementation gate 未完**（`ADR-0059:105-114`、越境 negative E2E は `QA-E2E-SAAS-01` 未実施、`SAAS-TENANT-01` In Progress）。現フェーズは single-tenant `local-default` 互換のみ（`ADR-0059:98`）。
- **SOCIAL-DIFFUSION-01..04 は全て Draft・活性化延期**（実ユーザー/協力者 milestone まで、`ADR-0038:51,78-87`, `ADR-0039`）。社会層は direction 保持のみ。
- **PM ツール協調 = EXT-CONN-02（ingest）+ EXT-CONN-03（export）で、いずれも Draft**（前述）。
- **「リスク早期検出」の "プロジェクトリスク" 枠組みは新規**。矛盾検出は在るが、リスク台帳/課題管理としての PM ツール連携は未定義。

### 4-2. 機能要件（考察〜具体化）

- **FR4-1（敵対協調の中核＝憲章の運用検証・既存）**: 対立非解消・一匹狼保護を敵対ステークホルダー文脈の一次要件として運用検証。**新規実装不要**（`ADR-0048` 憲章＋ CVI-7 既存）。これが具体例4 で唯一 near-term に検証可能な本質部分。
- **FR4-2（リスク早期検出＝矛盾レビューの運用検証・既存）**: `analyzeContradictions()` の検出→人間決定（採用/保留/却下）を「リスク/課題の早期検出→対応判断」の一次形態として運用検証。要件は `DOMAIN-EXPR-04`（Done）で被覆。**"プロジェクトリスク台帳" への昇格は現フェーズ外**（PM ツール協調＝EXT-CONN 依存）。
- **FR4-3（安全配布＝EXT-CONN-04 露出規則の先行検証・現フェーズ外実装）**: 外部来訪者向け read-only 根拠トレイルの露出規則（未レビュー/違和感/保留を既定非表示、%非表示）を、既存の共有前確認ゲートで先行検証（T4-B）。EXT-CONN-04 実装は相関 ID つきブリーフの実在後（`EXT-CONN-04:24`）＝現フェーズ外。
- **FR4-4（マルチ組織・社会層＝現フェーズ外・ゲート順守）**: SaaS 有効化は `ADR-0059:105-114` の 6 ゲート順守後。SOCIAL-DIFFUSION は実ユーザー milestone まで docs/planning-first（`ADR-0038:78`）。本書は near-term を「single-tenant ローカルで敵対的題材を代理シミュレーション」に限定推奨。
- **FR4-5（非監視シグナル＝SOCIAL-DIFFUSION-04 の定義先行・現フェーズ外）**: 採用シグナルは成果物ベース・集計・opt-in・ローカルファーストのみ（`SOCIAL-DIFFUSION-04:19`）。外部送信ゼロ。定義は docs-check レベルで先行可能だが活性化は延期。

### 4-3. 受入条件＝ローカル小規模試行

**T4-A: 敵対的対立の非解消と一匹狼保護（最重要・敵対協調の本質）**
- 前提/セットアップ: WSL frontend、SafeMode ON、provider=none。fixture: 相互に矛盾する reviewed カード 2 枚（例: 「案A を採用すべき」/「案A は不可」）を `contradicts` の EvidenceLink で結び、さらにどの島にも属さない単独カード（一匹狼）1 枚を置く。
- 操作: (1) `analyzeContradictions()` を走らせ矛盾シグナルを表示。(2) provider=none で島要約/narrative ドラフトを生成（決定論フォールバック）。(3) 矛盾シグナルに「保留」を選択。
- 観測可能な期待結果（機械判定）: (1) 矛盾は**自動解消されず**「対立がある」として両論が保持される（`ADR-0048:40`、CVI-7）。要約/narrative が片方を裁定・削除しない。(2) 一匹狼カードが要約統合で消えない（`ADR-0048:49` 少数意見保護）。(3) 「保留」決定が非破壊で、⌘Z 可逆（`contradiction_signal_decision.spec.ts` 準拠、CVI-7）。→ 敵対的利害関係の協調で最も本質的な不変条件を検証。

**T4-B: 安全配布の露出規則（外部来訪者向け・EXT-CONN-04 先行検証）**
- 前提: fixture に reviewed カード・unreviewed カード・違和感付きカード・held カードを混在。番兵として unreviewed カード本文に `SENTINEL-4B`。SafeMode ON。
- 操作: 共有前確認（`pre_share_summary_gate.spec.ts` 経路）を通し read-only 閲覧を生成。
- 期待結果（機械判定）: 未レビュー・違和感・保留カードが**既定で露出しない**（`EXT-CONN-04:34` の露出規則＝共有前確認と同一）。生成物に `SENTINEL-4B` が現れない（番兵・挙動検査、0.3節の砦弱点を補う）。`score|rank|confidence|priority`・`%` 表示が無い（`EXT-CONN-04:47` AC-3）。→ 敵対的環境での安全配布を挙動で固定。

**T4-C: 非監視シグナルの定義健全性（docs-check・SOCIAL-DIFFUSION-04）**
- 前提: 定義のみ（活性化延期中）。成果物ベースの集計指標を 1 つ定義（例: review pack 6 要素の充足率＝ローカル計算・外部送信なし）。
- 操作: 定義文書に対し「外部送信ゼロ・個人追跡なし・opt-in」を確認。
- 期待結果（機械判定に近い docs-check）: シグナルが成果物内充足率の自己診断に留まり、ネットワーク送信・利用者識別・行動スコアリングを含まない（`SOCIAL-DIFFUSION-04:52-56`）。→ 観測自体が漏えい/監視経路にならないことを検証。

**T4-D（現フェーズ外・ゲート先行定義）: 越境非表示のテナント分離**
- 前提: 定義のみ。SaaS Implementation gate（`ADR-0059:113`）と `QA-E2E-SAAS-01` が未了のため、**着手時に満たすべき受入契約として先行固定**。
- 操作（着手時）: 同一 docId を持つテナント A/B で GET/list/search/export/MCP の越境 negative matrix を叩く。
- 期待結果: 他テナント資源は not-found 相当で存在を漏らさない（`ADR-0059:79`）。→ 敵対的マルチ組織での基盤要件を、実装前に受入条件として固定。

---

## 5. dogfood issue への昇格推奨（依存順）

各受入試行のうち、追跡用 dogfood issue（`PRODUCT-VALUE` の 目的/受入条件/証跡/境界/検証 様式、または `VALUE-DOGFOOD-01` の dogfood-log + 摩擦分類様式）へ昇格すべきものを、依存順で 3 つに絞って推奨する。物量での追加はしない（`ADR-0039` 適正化・`value_traceability.md:120`「本物の穴が現れたときのみ起票」に整合）。

**推奨1（最優先・他に先行）: T2-A を昇格 — 外部頭脳 MCP クエリの運用実績 dogfood。**
- 理由: EXT-CONN-01 は Done だが「運用実績」ゲートが EXT-CONN-02/03（具体例3/4 の PM ツール協調）を止めている（`EXT-CONN-02:24`, `EXT-CONN-03:24`）。この試行を回すこと自体が下流ゲートを解除する。新規実装ゼロ・依存ゼロで最高レバレッジ。
- 様式: `VALUE-DOGFOOD-01` 様式（実題材で 1 回完走 + 摩擦ログ）。不変条件（SafeMode 境界・未レビュー除外・反スコアリング・監査）を実 MCP 経路で確認。

**推奨2: T1-A を昇格 — MMI 住み分けループ dogfood。**
- 理由: 具体例1 の中核。依存（CE-2/CE-3/`ADR-0055`）はすべて Done。provider=none で完結し、`ai-prompt-core-redesign` の MMI 品質改善（FR1-2）の before/after を測る土台になる。
- 様式: `PRODUCT-VALUE` 様式（AI提案タブ経由の採用→undo を証跡化）。推奨1 の後（外部頭脳クエリで得た文脈を人間協調面へ載せる順）。

**推奨3: T4-A を昇格 — 敵対的対立の非解消 dogfood。**
- 理由: 具体例4 で唯一 near-term に検証可能な本質部分。依存（`DOMAIN-EXPR-04`, CVI-7, `ADR-0048` 憲章）は Done。SaaS/SOCIAL-DIFFUSION の活性化を待たずに「敵対的利害関係の協調」の核（対立非解消・一匹狼保護）を回帰固定できる。
- 様式: `PRODUCT-VALUE` 様式。矛盾 fixture + 保留決定 + ⌘Z 可逆を証跡化。

依存順の要点: **推奨1 → 推奨2 → 推奨3**。推奨1 が具体例3/4 の外部連携ゲートを解除し、推奨2 が人間協調面を固め、推奨3 が敵対文脈の不変条件を固める。T2-C/T3-D/T4-D は「現フェーズ外機能のガード先行定義」または「既知 P0 の番兵」であり、dogfood 昇格ではなく該当実装 issue（Lane D ADR / `SEC-EXPORT-BUNDLE-01` / `SAAS-TENANT-01`）の AC 候補として残すのが適切。

---

## 6. 不確実性・未確認事項（明示）

- **CVI-1 の production 漏えい（`SEC-EXPORT-BUNDLE-01`）は synthesis 文書の記述に依拠**（`architecture-coherence-synthesis-2026-07-23.md:18`）。本書は `bundle_export.ts` の該当行を直接精読しておらず、T3-D/T4-B は「番兵が出ないことを挙動で確かめる」形にして、この不確実性を試行側で吸収している。
- **`mode=autonomous` の実装状態は未精読**。`ADR-0028:320` の決定は確認したが実装コードの有無は未確認のため、T2-C は「実装前の受入契約」として定義した。
- **EXT-CONN-02/03/04 の Draft は issue 本文で確認済み**だが、`schemas.md §18`（agent-constraints.v1 正本）は本セッションで直接精読していない（EXT-CONN-03 の要約引用に依拠）。
- 昇格様式（`PRODUCT-VALUE` / `VALUE-DOGFOOD`）は実 issue（`PRODUCT-VALUE-01/02/03`, `VALUE-DOGFOOD-01`）の構造を確認して選定した。
