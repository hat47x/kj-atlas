# リサーチ: トリガー型AI時代における kj-atlas の外部接続の役割と独自性

- Date: 2026-07-12
- Author: Claude Code（maintainer 委任による調査）
- Status: 調査文書（ADRではない。方向の採否は ADR-0047 の再起票基準 R-1..4 に従い別途判断）
- 位置づけ: maintainer 提示の「トリガー型AI」仮説を外部証拠で検証し、kj-atlas の外部ツール・インフラ接続戦略の上流入力とする。`00_Prompt/ai_cognitive_externalization_requirements.md`（認知外在化フレームワーク）および ADR-0028 Phase D（CLI/API連携）の延長線上に位置する。

## 0. 検討の起点（maintainer 提示仮説）

> 注力すべきは、使わなくても勝手に起動して仕事をするトリガー型AI。例: Googleカレンダーを定期チェックして、会議前に「これから会う人はこういう人・こういう会社」というサマリーを Slack/LINE/メール等へ勝手に貼っておく。新しいアプリを作るのではなく、普段のツールに埋め込む方が筋がいい。理由: ほとんどの人はAIにお題を立てられない——現状をうまく説明できず、本当に欲しいものも言語化できない。そこをユーザーに投げっぱなしなのが今のAIの課題。

## 方法と限界

- deep-research ワークフロー（5角度 × 並列WebSearch、計30ソース）+ 意外性の高い最重要3クレームの直接検証（一次資料 WebFetch / 追加検索）。
- 敵対的全数検証フェーズはセッション上限により未了。そのため各クレームに確度ラベルを付す:
  - **[検証済]** 一次資料または複数独立ソースで直接確認
  - **[中確度]** 検索結果スニペット・単一ソース準拠（一次資料未読）
  - **[知識]** モデル知識ベース（2026-01時点）による補完

---

## 1. 起点仮説の検証結果: 「概ね正しい。ただし2つの重大な条件が付く」

### 1.1 支持する証拠 — トリガー型は業界の主戦場になった

- **[検証済]** OpenAI は ChatGPT Pulse（夜間に非同期リサーチし、チャット履歴・メモリ・Gmail/カレンダー連携から翌朝カード型ブリーフを「頼まれずに」届ける）を 2025-09 に発表。さらに 2026-06-17 に Scheduled Tasks を Plus/Pro/Business/Enterprise へ展開（[9to5Mac](https://9to5mac.com/2026/06/17/openai-launches-scheduled-tasks-in-chatgpt-details-here/)）。
- **[中確度]** OpenAI workspace agents: Slack 常駐・スケジュール起動で「不在時も働き続ける」共有エージェントを公式発表（[OpenAI](https://openai.com/index/introducing-workspace-agents-in-chatgpt/)）。
- **[検証済]** Microsoft は Ignite 2025（2025-11-18）で Copilot エージェントを Teams/Outlook 等の日常ツールへ常駐・埋め込みする戦略を発表（[Microsoft 365 Blog](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-ignite-2025-copilot-and-agents-built-to-power-the-frontier-firm/)）。
- **[中確度]** LangChain は「人間のメッセージではなくイベントで起動し、複数エージェントが並行動作する」ambient agents 概念と notify/question/review の human-in-the-loop パターンを提唱（[LangChain Blog](https://www.langchain.com/blog/introducing-ambient-agents)）。

→ 「使わなくても勝手に働くAI」「既存ツールへの埋め込み」は、プラットフォーマー自身が既に主戦場として製品化している。**仮説の方向認識は正しい**。

### 1.2 条件1 — トリガー面（センサー・配信面）は変動が激しく、プラットフォーマーが握る

- **[検証済]** ChatGPT Pulse は発表から約9ヶ月で引退し Scheduled Tasks へ統合された。移行は自動ではなく、ユーザーは14日以内に手動で再設定（[digit.in](https://www.digit.in/news/general/openai-is-retiring-chatgpt-pulse-and-replacing-it-with-scheduled-tasks-here-is-why.html), [techjacksolutions](https://techjacksolutions.com/ai-brief/agentic-ai-news-openai-launches-scheduled-tasks-in-chatgpt-a/)）。
- **[検証済]** AIキャンバス Cove（元Google Mapsチーム、Sequoia出資$6M、「AI応答もテキストもPDFも全てカードとして無限キャンバスに置き人間とAIの共有文脈にする」設計）は 2026-03 に Microsoft へ acqui-hire され、**製品は2026-04-01終了、ユーザーデータは削除**（エクスポート提供・3月分返金あり）（[TechCrunch](https://techcrunch.com/2026/03/18/microsoft-hires-the-team-of-sequioa-backed-ai-collaboration-platform-cove/)）。

→ 教訓は二重: (i) トリガー面・キャンバス面ともに大手の吸収と統廃合が速い。小規模OSSがここで正面から戦うのは筋が悪い。(ii) Cove のデータ削除は、**可搬性・ラウンドトリップ非損失（kj-atlas の根幹価値）こそがこのレイヤーの信頼の土台**であることを図らずも証明した。

### 1.3 条件2 — 「勝手にやるAI」には実証された心理的・信頼的コストがある

- **[中確度]** 職場でAIが自発的にイニシアチブを取ることの心理的コストを扱う実証研究があり、プロアクティブ支援は割り込みリスクを伴い実際にはしばしば利用されない（CHIWORK 2026, [doi](https://doi.org/10.1145/3808045.3808054)）。
- **[中確度]** 頼んでいないAI支援は「能力不足のシグナル」として自己観を脅かし受容を損なう（help backfires）。提案のみ→信頼形成に応じ段階的に主導性を上げる設計が示唆される（[arXiv:2509.09309](https://arxiv.org/abs/2509.09309)）。
- **[知識/中確度]** Horvitz の mixed-initiative 12原則（CHI 1999, [doi](https://dl.acm.org/doi/10.1145/302979.303030)）は誤推測コストの最小化・ユーザー修正からの学習・タイミング考慮を一級要件とし、Lee & See（2004, [Human Factors](https://journals.sagepub.com/doi/10.1518/hfes.46.1.50_30392)）は信頼の校正に「自動化の目的・過程・実績の可視性」を要求する。

→ 「勝手にやる」を成立させる鍵は、**誤りの訂正が効くこと・根拠が見えること・割り込まないこと**。これはトリガー型AIの実装側ではなく、**その背後の文脈・監査・訂正の基盤**の問題であり、まさに kj-atlas の領分である。

---

## 2. 「人はAIにお題を立てられない」は実在する——そしてトリガー型は回避策であって解決策ではない

- **[検証済/知識]** "Why Johnny Can't Prompt"（CHI 2023, [doi](https://dl.acm.org/doi/10.1145/3544548.3581388)）: 非AI専門家は場当たり的にプロンプトを設計し系統的に失敗する。プロンプト設計自体が暗黙知を要する技能。
- **[検証済/知識]** "Bridging the Gulf of Envisioning"（CHI 2024, [doi](https://dl.acm.org/doi/10.1145/3613904.3642754)）: ユーザーの目標とLLMへ伝える意図の定式化の間に「構想の淵」がある——capability gap / instruction gap / intentionality gap。仮説の「現状を説明できず欲しいものを言語化できない」の最も直接的な学術的定式化。
- **[中確度]** Polanyi「我々は語れる以上のことを知っている」をLLM文脈へ接続する査読論文（Springer 2025, [link](https://link.springer.com/article/10.1007/s11138-025-00710-5)）: プロンプト＝完全な言語化を前提とするインタラクションには原理的限界がある。

ここで決定的なのは次の非対称性である:

- **トリガー型AIはこの問題を「回避」する**（お題を不要にする）。カレンダーという明示的な構造があるからブリーフが出せる。しかし、本当に重要な仕事——何が問題かを定めること——には依然としてお題の形成（problem formulation）が要る。
- **KJ法はこの問題を「解決」する側の方法論である**。川喜田二郎がヒマラヤのフィールドワークで、演繹の通用しない未構造データから仮説を立ち上げるために開発した「渾沌をして語らしめる」技法そのもの（[Roosen論考, 中確度]）。言語化できないもの（違和感・近さの感覚・保留）を空間操作として扱い、そこから言葉（表札・仮説）を立ち上げる。
- **[中確度]** HCI最前線もこの方向を正当化しつつある: DesignerlyLoop（DIS 2026, [doi](https://dl.acm.org/doi/10.1145/3800645.3812885)）は、キャンバス上で未構造の意図（問題フレーミング・制約・評価基準）を外化・キュレーションしてから human-LLM アラインメントを形成する。

→ **kj-atlas は「お題を立てられない問題」の根治側を担い、トリガー型AI（対症側）と補完関係に立つ**。トリガー型の観察が kj-atlas に堆積し、人間がそこからお題を立ち上げ、立ち上がったお題（構造化された文脈）が以後のエージェントの前提になる——この循環が接続戦略の骨格である。

---

## 3. エージェント記憶・文脈基盤の空白は、kj-atlas の根幹価値の形をしている

- **[中確度]** mem0 / Zep(Graphiti) / Letta / LangMem 等の記憶フレームワーク横断比較は、全てに共通するガバナンス空白を指摘する: 「**全ての記憶が認識論的に等価——品質階層も承認機構も『権威ある知識 vs 未検証知識』の概念も存在しない**」、監査証跡・出所(lineage)・削除ポリシーの不在（[Atlan比較](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/)。ただしAtlan自身が同領域を狙う点にバイアス留意）。
- **[中確度]** Letta の Agent Development Environment はメモリブロックを可視化し人間が編集できる「ガラス箱」に最も近いが、対象は**エージェント開発者のデバッグ**であり、知識労働者の意味形成の場ではない（[Letta Blog](https://www.letta.com/blog/introducing-the-agent-development-environment/)）。
- **[中確度]** knowledgeplane（[GitHub](https://github.com/camplight/knowledgeplane)）は「エージェントとチームの共有記憶」を掲げるMCPサーバーで、監査証跡・ダッシュボードを持つ直接競合（要注視）。ただしグラフ+ダッシュボード型であり、空間配置キャンバス・保留/違和感タグ・双方向の意味形成は持たない。
- **[知識]** ChatGPT / Claude のメモリ機能はユーザー可視性・可搬性が限定的で、ベンダーに縛られる。

→ 記憶基盤競合は「保存と検索の最適化」を競っており、**「この記憶はレビュー済みか・保留中か・根拠は何か・誰が承認したか」という認識論的ガバナンスの層が丸ごと空いている**。kj-atlas のドメインモデル（claimType / holdState / critique / evidenceLink / contradictionState / reviewed / review attribution / safeMode）は、偶然ではなくこの空白の形をしている。

---

## 4. 空白領域の検証: 「双方向に尊重された共有マップ」は未確立

「エージェントがトリガー起動で観察をカードとして書き込み、人間が違和感/保留で応答し、その訂正が以後のエージェント挙動に蓄積反映される共有マップ」の先行例を探した結果:

- **半分は存在する**: Miro は Canvas 25（2025-10-14）でキャンバス常駐の会話型AIエージェント Sidekicks を発表し「完全な可視性・編集可能性・各ステップでの制御」を強調 **[検証済]**（[Miro Newsroom](https://miro.com/newsroom/miro-puts-ai-where-teams-work/)。なお「自発的な非同期コメント書き込み」までは一次資料で確認できず **[未確認]**）。Cove は「全てがカード」の共有文脈を実装したが終了した **[検証済]**。
- **研究側も部品ごとに散在**: Sensecape（UIST 2023）は空間キャンバス×LLMだが生成は常に人間起点のpull型 **[中確度]**。LLooM（CHI 2024, [doi](https://dl.acm.org/doi/full/10.1145/3613904.3642830)）は概念抽出のガラス箱化だがバッチ型 **[中確度]**。プロアクティブなエージェント書き込みは割り込み管理の中間構造が必要という実証（CHI 2026, [arXiv](https://arxiv.org/html/2602.17864v1)）**[中確度]**。
- **訂正→挙動反映ループは存在するが未結合**: TRACE（[arXiv:2606.13174](https://arxiv.org/pdf/2606.13174)）はユーザー訂正を構造化ルールにコンパイルし以後のエージェント実行へ強制適用する——ただしコーディング領域で、空間的意味形成・違和感タグとは結合していない **[中確度]**。

→ **判定: 空白は実在する**。「エージェント記憶側の訂正ループ」と「キャンバス側の意味形成」が別々に存在しており、**両者を認識論的状態（保留・違和感・根拠・レビュー）で結合した持続的な共有マップは、製品にも研究にも確立していない**。

---

## 5. 考察: kj-atlas が外部接続で果たすべき4つの役割

前提となる構図: **前面（トリガー・配信）はプラットフォーマーが握り、churnする。kj-atlas は前面を取りに行かず、日常ツールの背後に立つ文脈基盤になる。**

### 役割A — エージェントが読み書きする「ガラス箱の共有記憶の正本」
`ContextQuery → ContextBundle` 投影（ADR-0028 / CE0契約で設計済み）を **MCP サーバーとして外部エージェントに公開**する。エージェントは reviewed-only / contradiction subset / evidence subset 等の制約付き投影を読む。書き込みは既存原則どおり **proposal（patch）のみ**で、Consensus Graph へは human approval を経てのみ入る。会議前ブリーフを作るトリガー型AIは、闇雲にWebを漁るのではなく「この相手について、チームがレビュー済みの文脈」を読んでから動ける。

### 役割B — プロアクティブ出力の「監査・根拠層」
トリガー型AIの構造的弱点は、ブリーフの根拠が見えず、誤りの出所を辿れないこと（Lee & See の信頼校正要件を満たせない）。kj-atlas の evidenceLink / review attribution / contradictionState / safeMode は、**「このブリーフはどのレビュー済みカードに基づくか」を辿れる監査層**を提供する。配信されるブリーフに「なぜ？」リンクを埋め、根拠を見に来る動線を作る——これが「行き先アプリ」の再定義（毎日開く場所ではなく、信頼を確かめに時々見に行く機械室/庭）。

### 役割C — 人間の訂正が蓄積され、エージェント挙動に反映される場
kj-atlas には既に critique（違和感）→ constraint（再配置条件）の設計がある。これを外部エージェントへ輸出する: エージェントの書き込みに人間が違和感タグ/保留で応答すると、それが**次回以降のエージェントの制約として機械可読に渡る**（TRACE の知見と接続）。「同じ誤りを繰り返すAI」問題への、説明責任を人間に課さない（違和感は理由不要＝domain.md）訂正チャネル。

### 役割D — 使い捨てブリーフの「堆積場」と意味形成
トリガー型出力は ephemeral で、流れて消える。webhook ingest で**ブリーフや観察を「提案カード」として堆積**させ（WorkingGraph 着地・未レビュー明示・自動確定なし）、人間が後から KJ 法的に問題を立ち上げる素材にする。これが §2 の循環（観察の堆積→お題の形成→エージェントの文脈）を閉じる。

### 「余白」の設計原理
役割A〜Dはいずれも**通知プッシュではない**。エージェントは庭に書き込み、人間は好きな時に見て、違和感だけ残す。割り込み研究（§1.3）と calm technology の含意に整合し、maintainer 提示の方向性(c)「相互に尊重された余白のある交流の場」の具体的な実装形になる。

---

## 6. リスクと反証

| リスク | 内容 | 対抗 |
|---|---|---|
| R1: プラットフォーマー統合 | ChatGPT memory + Tasks が事実上の文脈正本になる | ベンダー中立（MCP）・ローカル/OSS・ラウンドトリップ非損失。Cove のデータ削除が対照例 **[検証済]** |
| R2: 隣接競合の空白参入 | knowledgeplane / Atlan 等が「ガバナンス付き記憶」を狙う | 認識論的タグ体系×空間的意味形成×proposal-onlyの結合は未保有。ここを速く固める |
| R3: エージェント書き込みによる汚染 | キャンバスがAI生成物で溢れ、人間の場でなくなる | 既存設計で対応済み: WorkingGraph分離・proposal-only・AI由来の視覚区別（ADR-0048 D1）・safeMode |
| R4: MCP自体の変動 | プロトコル改廃 | 投影IR（ContextBundle）は輸送非依存に保ち、MCPは薄いアダプタに留める |
| R5: 誰も見に来ない | 背後の基盤は存在感が出ない | ブリーフ側に根拠リンクを埋める（役割B）。「見に来る理由＝信頼の確認」を配信面に寄生させる |

## 7. 提言（次アクション候補・maintainer判断待ち）

1. **ADR起票候補**: 「外部接続レイヤーの段階導入」— (1) read-only MCP サーバー（ContextBundle投影の公開、safeMode既定）→ (2) webhook→提案カード ingest → (3) critique/constraint の機械可読エクスポート。ADR-0028 Phase D の具体化として位置づけ可能（再起票基準は R-2「外部接続という新たな不可逆判断」に該当しうる）。
2. **順序の根拠**: 読み取り公開が最小リスク（既存の safeMode/投影契約をそのまま使う）。書き込み（ingest）は proposal-only 原則があるため二番目。訂正エクスポートは効果最大だが仕様設計が要るため三番目。
3. **本文書の扱い**: 上記が採択される場合、本文書を当該ADRの Context 節から参照する。

## 追補（2026-07-12 同日・追加検証ラウンド）

初版で未了だった検証を追加実施した（対象: ADR起票の土台となる[中確度]クレーム＋技術的空白）。結果、**初版の判断はすべて維持され、うち3点は判断を強化する方向の新事実が得られた**。

### A1. R4（MCP変動リスク）は大幅に緩和されている **[検証済]**

- MCP は 2025-12 に Anthropic から **Linux Foundation 傘下の Agentic AI Foundation (AAIF) へ移管**済み。OpenAI・Block が共同創設、AWS/Google/Microsoft/Cloudflare/Bloomberg がプラチナ会員。単一ベンダーの都合で改廃されるリスクは初版想定より低い（[MCP Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/), [WorkOS解説](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026)）。
- **2026-07-28 に大型仕様改訂が確定**（RC公開済み）: ステートレスコア（通常のHTTP LBで運用可）、`Mcp-Method` ヘッダによるルーティング、`ttlMs` キャッシュ制御、**OAuth 2.1 リソースサーバーとしての正式化**（RFC 8707 Resource Indicators 必須）、長時間処理の Tasks 拡張、サーバー描画UIの **MCP Apps** 拡張。
- 含意: (i) 投影IRを輸送非依存に保つ方針（R4対抗）は維持しつつ、実装は 2026-07-28 仕様（streamable HTTP + OAuth 2.1）へ直接合わせるのが最短。(ii) MCP Apps は将来、役割Bの「なぜ？リンク」を**チャットクライアント内で根拠トレイルとして描画する**選択肢になり得る（コミットはしない）。

### A2. クロスベンダー到達性の確認 — ただし接続形態に制約 **[検証済]**

- ChatGPT は Developer Mode（ベータ）で **フルMCPクライアント対応**。ただし (i) **リモートHTTPSサーバーのみ**（stdio不可）、(ii) 個人プラン（Plus/Pro）は**読み取り専用**コネクタに制限、書き込みは Business/Enterprise のみ（[OpenAI Help](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt), [解説](https://www.usecarly.com/blog/chatgpt-mcp/)）。
- Copilot Studio はエージェントのツールとして MCP サーバーをネイティブ追加可能（[ShareGate手順例](https://sharegate.com/mcp/install)）。Claude/Claude Code は当然対応。
- 含意: **1つのMCPサーバーで3大エコシステムに到達できる**（ADR-0049 の copy/paste レーンの自動化版として自然な次段）。段階1はローカル stdio（Claude Code向け）から始めてよいが、ChatGPT/Copilot 到達には streamable HTTP + OAuth 2.1 が必須なので、契約設計時点で両輸送を想定する。ChatGPT個人プランが読み取り専用強制である事実は、**段階1=read-only の順序設計と外部制約が一致**していることを意味する（好都合）。

### A3. 「記憶だけでは訂正が効かない」の定量証拠 **[検証済]**

- TRACE（[arXiv:2606.13174](https://arxiv.org/abs/2606.13174), Notre Dame/IBM Research/Tencent, 2026-06）の正式名称は "Getting Better at Working With You: Compiling User Corrections into Runtime Enforcement for Coding Agents"。実利用の摩擦事例から導出したタスクで、**Mem0 記憶を使っても適用可能な選好チェックの57.5%が違反されたまま残る**ことを示し、訂正を原子的ルールへコンパイルして実行時強制する方式を提案。
- 含意: 役割C（違和感→制約の機械可読輸出）の価値仮説「記憶への保存では不十分で、次回実行の制約として渡す必要がある」に直接の定量的裏付けが付いた。

### A4. knowledgeplane の実像確認 — 空白判定は維持 **[検証済]**

- [knowledgeplane](https://github.com/camplight/knowledgeplane)（[公式](https://knowledgeplane.io/)）: 知識グラフ＋ベクトル検索＋自動統合（auto-consolidation）のMCPサーバー。全ファクトに出所・所有者・タイムスタンプの監査証跡。REST APIも併設。
- ただし確認された設計は「エージェントが**直接CRUDで読み書き**する共有記憶」であり、(i) proposal-only の承認ゲートなし、(ii) 保留/違和感/矛盾/レビュー済みの認識論的状態なし、(iii) 空間配置による意味形成なし、(iv) **自動統合はむしろ人間の承認を経ない書き換え**を含意する。初版§3の空白判定（認識論的ガバナンス層の不在）はそのまま成立。競合ではなく対照例に近い。

### A5. LangChain HITL 3パターンと kj-atlas の位置 **[検証済]**

- ambient agents の human-in-the-loop は **notify / question / review** の3パターン＋「Agent Inbox」（メール型の未処理キューUI）として整理されている（[LangChain Docs](https://docs.langchain.com/oss/python/langchain/frontend/human-in-the-loop), [Blog](https://www.langchain.com/blog/introducing-ambient-agents)）。
- 含意: kj-atlas の critique（違和感・理由不要・事後・非ブロッキング）は、この分類に**存在しない第4パターン**にあたる。notify/question/review はいずれも「人間が処理すべきキュー」を作るが、critique は処理義務を作らない（余白の設計原理と一致）。Agent Inbox が「受信箱」なら kj-atlas は「庭」であり、この対比は設計語彙としてそのまま外部発信に使える。

### 追補後の確度サマリ

初版の主要クレームのうち、[中確度]だった R4関連・knowledgeplane・TRACE・ambient agents HITL は本追補で **[検証済]** へ昇格。未検証のまま残る主要項目: CHIWORK 2026（プロアクティブ支援の心理コスト）と help-backfires（一次資料未読・方向性は複数ソース一致）、Miro Sidekicks の自発的書き込み範囲 **[未確認のまま]**。いずれも提言の骨格には影響しない。

## 出典一覧（主要）

一次資料・検証済: [OpenAI Pulse発表](https://openai.com/index/introducing-chatgpt-pulse/) / [9to5Mac: Scheduled Tasks展開とPulse引退](https://9to5mac.com/2026/06/17/openai-launches-scheduled-tasks-in-chatgpt-details-here/) / [TechCrunch: Cove→Microsoft](https://techcrunch.com/2026/03/18/microsoft-hires-the-team-of-sequioa-backed-ai-collaboration-platform-cove/) / [Miro Canvas 25](https://miro.com/newsroom/miro-puts-ai-where-teams-work/) / [Microsoft Ignite 2025](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-ignite-2025-copilot-and-agents-built-to-power-the-frontier-firm/) / [LangChain ambient agents](https://www.langchain.com/blog/introducing-ambient-agents)

学術: [Why Johnny Can't Prompt (CHI 2023)](https://dl.acm.org/doi/10.1145/3544548.3581388) / [Gulf of Envisioning (CHI 2024)](https://dl.acm.org/doi/10.1145/3613904.3642754) / [Horvitz mixed-initiative (CHI 1999)](https://dl.acm.org/doi/10.1145/302979.303030) / [Lee & See 2004](https://journals.sagepub.com/doi/10.1518/hfes.46.1.50_30392) / [Sensecape (UIST 2023)](https://dl.acm.org/doi/10.1145/3586183.3606756) / [LLooM (CHI 2024)](https://dl.acm.org/doi/full/10.1145/3613904.3642830) / [DesignerlyLoop (DIS 2026)](https://dl.acm.org/doi/10.1145/3800645.3812885) / [Tacit knowledge in LLMs (2025)](https://link.springer.com/article/10.1007/s11138-025-00710-5) / [Proactive Systems survey](https://arxiv.org/abs/2606.25149) / [Psychological Costs of Proactive AI (CHIWORK 2026)](https://doi.org/10.1145/3808045.3808054) / [Help backfires](https://arxiv.org/abs/2509.09309) / [Proactive programming support](https://arxiv.org/abs/2502.18658) / [TRACE](https://arxiv.org/pdf/2606.13174) / [MindTrellis](https://arxiv.org/pdf/2604.23129)

記憶基盤: [Atlan比較](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/) / [Letta ADE](https://www.letta.com/blog/introducing-the-agent-development-environment/) / [knowledgeplane](https://github.com/camplight/knowledgeplane) / [記憶システム6次元比較](https://medium.com/@wasowski.jarek/i-compared-5-ai-agent-memory-systems-across-6-dimensions-none-wins-6a658335ed0a) / [Markdown記憶論](https://dev.to/imaginex/ai-agent-memory-management-when-markdown-files-are-all-you-need-5ekk)

KJ法: [Roosen: Reconsidering Jiro Kawakita](https://www.christopherroosen.com/blog/2020/7/17/what-came-before-the-affinity-map-reconsidering-professor-jiro-kawakita-and-the-kj-method)
