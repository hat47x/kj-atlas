# 生成AIの認知外在化機能としての kj-atlas 拡張要件

**English summary**  
This document defines kj-atlas as a cognitive externalization framework for human–AI collaborative reasoning.  
Its goal is not to let AI decide for humans, but to provide an external structured workspace that enables deeper, safer, and more context-sensitive information processing than current generative AI can sustain on its own.

---

# 0. 本文書の位置づけ

本書は、今後の kj-atlas プロジェクトにおける **中核文書** である。  
ここで定義するのは単なる追加機能ではない。kj-atlas を、

- 人間のための空間的思考環境
- 生成AIのための認知外在化フレームワーク

として再定義するための、設計原理・射程・要件・実装方針である。

本書は、以下の上流文書と整合する。

- `00_Prompt/domain.md`
- `01_Plans/adr/ADR-0001-value-to-requirements.md`
- `02_Architecture/design/architecture.html`
- `02_Architecture/schemas.md`

今後、AI関連機能を追加する際は、本書を参照して整合性を確認すること。

本書に基づく実行計画の正本は `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md` とし、
フェーズ進行・受入条件・検証導線は ADR 側で管理する。

---

# 1. 問題設定

## 1.1 現在の生成AIの限界

生成AIは、単発の要約・変換・応答において高い能力を示す一方、高度な意思決定や長期的思考支援に必要な以下の能力に限界がある。

- 文脈の長期保持
- 多層的な前提関係の維持
- 反対視点や矛盾の保留
- 事実・主張・仮説の峻別
- 「まだ決めるべきでないこと」を保留すること
- 認知的作業空間そのものの持続

このため、生成AIをそのまま「結論生成器」として使うと、

- 早すぎる収束
- もっともらしい誤り
- 反対仮説の消失
- レビュー不能な要約の流通

が起きやすい。

## 1.2 必要なのは“賢いAI”ではなく“賢く考え続けられる場”である

高度な判断に必要なのは、単なる知識量ではなく、**文脈に即した情報の蓄積と配置** である。  
すなわち、

- 何が前提か
- 何が事実で何が仮説か
- どこに対立があるか
- どこまでがレビュー済みか
- 何が未整理で保留されているか

が、構造として保持される必要がある。

生成AIはこの「思考の地形」を自前では十分に維持できない。  
したがって、外部に **認知の足場** を作る必要がある。

---

# 2. 基本コンセプト

## 2.1 kj-atlas の再定義

kj-atlas は、単なるKJ法図解ツールではない。  
また、単なる生成AI支援ツールでもない。

kj-atlas は、

> **生成AIと人間が、高度な情報処理と熟慮を継続するための、構造化された認知外在化環境**

である。

## 2.2 「知の竹馬」という比喩

ここでのAI拡張は、AIそのものを作り替えることではない。  
kj-atlas は、生成AIに対して、人間が高度な判断に必要とする

- 構造
- 保留
- 対立
- 根拠
- 履歴
- 文脈の配置

を与えることで、AIが単独では届かない地点まで **安全に到達できるよう支える補助具** として機能する。

つまり、kj-atlas は「AIの代わりに考える」ものではなく、

> **AIがまだ自前では維持しにくい思考の足場を、外部に作るもの**

である。

---

# 3. 目標（Goal）

本拡張の目標は、次の三つに整理される。

## 3.1 人間向け目標

- 空間配置を通じて意味や違和感を扱えること
- 曖昧さを保留したまま思考を継続できること
- AIの出力を飲み込まず、比較・保留・修正・承認できること

## 3.2 生成AI向け目標

- 構造化された文脈投影を受け取れること
- 探索の深さ・範囲・制約を明示的に与えられること
- 単なる自由テキストではなく、思考済みの地形の上で推論できること

## 3.3 システム全体としての目標

- AI出力を常に差分・候補・パッチとして扱えること
- 人間のレビュー状態が明示されること
- safeMode を共有・配布時の既定とすること
- 後から監査・差分確認・再評価ができること
- 中間処理（分類/要約/整形/条件分岐）と最終判断（採否・統合方針）を分離し、
  モデル能力とコストに応じて責務分担できること

---

# 4. 非目標（Non-goals）

本拡張は、以下を目的としない。

- AIによる最終結論の自動生成
- AIによる自動分類・自動確定の全面委任
- 「もっともらしくまとまった文章」を素早く作ること自体
- チャットUIを主とし、キャンバスを従属させること
- 生成AIの内部モデル改善そのもの

---

# 5. 設計原則

## 原則1：単一の真実源と複数の投影を分ける

正規データは `document` と `view` に保持する。  
AI向けコンテキストは、それらから都度構成される **投影（projection）** であり、一次データではない。

## 原則2：人間向け空間文脈とAI向け文脈を分ける

人間にとって意味を持つものと、AIにとって有効なものは異なる。

- 人間向け：位置、近接、見た目、脇置き、暫定配置
- AI向け：対象集合、関係集合、深さ、範囲、レビュー状態、除外条件

両者は対応してよいが、同一である必要はない。

## 原則3：AIは常に「候補生成器」である

AIは、

- 下書き
- 複数候補
- 差分案
- パッチ提案

を返す存在として扱う。  
Consensus Graph（旧称: Core Graph）を直接変更してはならない。

### 原則3a：カードの元の意味を品質支援より優先する

AIは、カードの分割、文脈補足、出典追加、観察と解釈の分離を提案してよい。ただし、品質を点数や合否で示さず、出典・話者・日時・因果関係を推測せず、利用者の採用前に本文や状態を変更してはならない。

利用者は本文だけでカードを保存できる。品質支援は保存後または利用者が求めたときに、一つずつ確認できる任意の提案として提示する。詳細は `00_Prompt/qualitative_card_quality_requirements.md` を正本とする。

### 原則3b：視覚手掛かりを意味の正本にしない

AIは、島または利用者が明示的に選んだ情報集合を見つけ直すための小さな画像候補を提示してよい。ただし、画像は表札、要約、本文、根拠の代替ではなく、人間向けの任意の再認識補助とする。画像の生成、取得、採用は明示操作を必要とし、採用前に正規データを変更しない。

絵文字、同梱プリセット、権利確認済み外部素材、生成画像は、通信・権利・来歴が異なる経路として扱う。外部検索または生成へ渡す投影は利用者が事前に確認でき、SafeModeと暗黙のprovider切替禁止を守る。曖昧さや対立を一つの具体像へ収束させず、画像なし、中立的な候補、複数候補を許容する。詳細は `00_Prompt/representative_visual_cue_requirements.md` を正本とする。

利用者の手描き、基本図形、撮影写真はAI機能へ従属させない。写真・図が一次資料である場合、AIが作るサムネイルや説明は投影・提案に留まり、元資料、撮影文脈、出典を変更または置換しない。

### 原則3c：表札（島タイトル）の代弁性を分類名化より優先する

AIは島タイトル候補を提案してよい。ただし、その候補が別の島の上に置いても成立してしまう一般的な分類名（例：「重要な論点」「今後の課題」）になっていないかを検査し、該当する場合は書き直し案を示す。AIはタイトルを確定または自動適用してはならない。詳細は `00_Prompt/qualitative_card_quality_requirements.md` 第5章、転写検査そのものは `00_Prompt/kj_technique.md` 第3章を正本とする。

## 原則4：曖昧さ・対立・未解決を保持する

AIは収束したがる。  
kj-atlas は、

- contradictions
- unknowns
- hypothesis
- unreviewed
- pending

を構造として保持し、消去対象ではなく **保留対象** として扱う。

## 原則5：共有時は安全側に倒す

共有・レビュー配布・静的公開などの経路では、safeMode を既定ONとし、未レビューAI文章や生テキストを漏らさない。

## 原則6：推論パイプラインを二層化する（中間処理層 / 最終判断層）

分類・要約・フォーマット変換・条件分岐などの中間処理は、
高速・低コスト層（例: Groq 上の Llama / Qwen）へ委譲してよい。

ただし、次の最終判断は高信頼層（例: Claude / GPT-5）に限定する。

- patch の採否判定
- competing proposal の統合方針
- 保留解除の提案（hold解除候補）
- 公開前の最終 narrative 承認候補

最終判断層であっても **自動確定は禁止** し、出力は常に proposal-only とする。

---

# 6. 三層アーキテクチャ

本拡張では、文脈を三層で扱う。

## 6.1 Consensus Graph（旧称: Core Graph）

唯一の正規データ層。

含まれるもの：
- Card
- Island
- Membership
- Relation / Edge
- EvidenceLink
- ClaimType
- ReviewState
- Summary / RelationSummary
- PatchLog / AuditLog

## 6.2 Human Spatial Context

人間の認知のための空間層。

含まれるもの：
- card.position
- island.geometry
- collapsed state
- reading order hints
- visual clusters
- temporary placement
- current focus / zoom / perspective

これは人間の思考補助であり、AI入力へ直接渡すことを前提としない。

## 6.3 AI Context Projection（ContextProjectionGraph）

AI問い合わせのたびに Consensus Graph / WorkingGraph から生成される読取専用の投影層。

含まれるもの：
- 対象ノード集合
- 対象島集合
- 対象関係集合
- reviewed-only subset
- contradiction subset
- evidence subset
- traversal depth / scope
- exclusion rules
- safeMode constraints
- output mode

AIはこの投影層を入力として受け取る。
`patch + approval` を経ない direct write / auto-apply は禁止する。

---

# 7. AI Context IR（中間表現）要件

## 7.0 CE0 Contract Freeze 参照（Stream B）

本書で扱う契約語彙は、CE0 Contract Freeze の参照専用固定値に従う。

- `CE0-CTX-IF`: ContextQuery/ContextBundle 最小I/F（Query Preview必須、決定論bundle）
- `CE0-SAFEMODE-IF`: safeMode既定ON、`allowUnreviewedText=false` 既定
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみ
- `CG-01..05`: WorkingGraph / ContextProjectionGraph / ConsensusGraph の責務分離、`patch + approval` 以外の適用禁止

衝突検知ポリシー: Contract ID collision=0、語彙 collision=0、安全後退（safeMode緩和・auto-apply許容・review自動昇格）=0。

## 7.1 IR の基本方針

## 7.1a Multi-Model Routing 要件（MMR-01〜06）

本節は、モデル責務分担を固定する要件である。

- **MMR-01（責務分離）**:
  `intermediate`（中間処理）と `final_judgement`（最終判断）を論理的に分離する。
- **MMR-02（許可タスク）**:
  `intermediate` は `classify/summarize/format_transform/branch_resolve` に限定する。
- **MMR-03（禁止タスク）**:
  `intermediate` は `accept/reject/merge/finalize/publish` を実行してはならない。
- **MMR-04（モデル階層）**:
  `final_judgement` は high-reasoning tier（例: Claude / GPT-5）へルーティングする。
- **MMR-05（監査性）**:
  監査ログに `routingStage`（intermediate/final_judgement）、
  `provider/model`、`sourceBundleHash`、`proposalId` を必須記録する。
- **MMR-06（安全停止）**:
  `final_judgement` 経路が利用不能な場合は auto-publish へフォールバックせず、
  `held` へ遷移して人手確認待ちにする。

AIに渡す入力は、キャンバスの見た目や雑多な履歴ではなく、**問い合わせ目的に応じて切り出された構造化コンテキスト束** であるべきである。

基本形：

```text
ContextQuery -> ContextBundle
```

## 7.2 ContextBundle に最低限含むべき要素

- query metadata
- selected cards / islands
- adjacency / relation subset
- contradiction subset
- evidence subset
- summaries with review flags
- claimType distribution
- unresolved items
- safeMode policy
- truncation / limit metadata

## 7.3 IR の性質

- 決定論的に生成できること
- query が同じなら同じ bundle を再生成できること
- 実装依存の内部状態に引きずられないこと
- diff / audit 対象にできること

---

# 8. ContextQuery 要件

## 8.1 必要性

自然言語だけでAIへの文脈指定を行うと、探索範囲・深さ・制約が曖昧になり、AIに過度な裁量を与えてしまう。  
そのため、**探索条件を明示的に指定するクエリ機構** を持つことが望ましい。

## 8.2 クエリで指定できるべき軸

### 対象
- card
- island
- document
- relation cluster
- contradiction cluster
- evidence cluster

### 深さ
- direct only
- hop depth 1 / 2 / 3 ...
- reverse evidence depth
- contradiction chain depth

### 範囲
- selected only
- same island only
- adjacent islands
- reviewed-only
- exclude unknown
- include hypothesis

### モード
- summarize
- outline-draft
- title-candidates
- contradiction-trace
- evidence-trace
- critique
- merge-candidates
- next-focus suggestions

### 制約
- safeMode
- maxNodes
- maxChars
- reviewedOnly
- includeUnreviewed
- includeRawText

## 8.3 クエリ表現

初期段階では、厳密な言語仕様よりも、**探索の深さ・範囲・制約を明示できる軽量DSL** を目指す。

例：

```text
focus island:i12
mode contradiction-trace
depth 2
reviewed-only true
exclude unknown
max-nodes 30
```

将来的には、
- UI
- CLI
- API
- AI呼び出し内部

の共通問い合わせフォーマットとして用いる。

---

# 9. AIにやらせる処理 / やらせない処理

## 9.1 AIにやらせる処理

### 候補生成
- 島タイトル候補
- B型文章ドラフト
- 代表カード候補
- 反対視点候補
- 欠落論点候補

### 制約付き変換
- reviewed-only からの要約
- contradiction cluster からの論点整理
- evidence graph からの narrative draft

### 探索支援
- 次に見るべき島・カード候補
- 根拠不足の仮説抽出
- 整理が必要な混在島の指摘

### パッチ提案
- summary rewrite proposal
- merge proposal
- relation summary draft

## 9.2 AIにやらせない処理

- 分類の最終確定
- 関係線の自動確定
- 真偽判定の断定
- reviewed 状態の自動付与
- Consensus Graph（旧称: Core Graph）の暗黙更新
- 未レビューのまま外部共有向け文章を正式版として出すこと

---

# 10. 機能要件（MVP〜拡張）

## 10.1 MVPで実装すべきもの

### M1. Context Query Preview

AIに渡る前に、
- どのカードが含まれるか
- どの島が含まれるか
- どの関係が含まれるか
- どの制約が適用されるか

を人間が確認できること。

### M2. 島タイトル候補生成

- 1つの島または島群を対象に、タイトル候補を複数提示
- 自動適用はしない
- 選択・編集・破棄を可能にする

### M3. B型文章ドラフト生成

- reviewed-only を既定とする
- unreviewed を含める場合は明示
- 出力は常に draft とする
- patch / diff として比較可能であること

### M4. 反対視点・根拠不足提案

- contradiction / evidence 構造をもとに、未検討論点や根拠不足箇所を提案
- 結論ではなく、考えるべき点を提示する

## 10.2 中期拡張

### M5. AI Patch Proposal Workspace

AIが出した複数案を並置し、
- 比較
- 一部採用
- 保留
- 廃棄

をキャンバス上で扱えること。

### M6. Query Presets

頻出する問い合わせ（例：reviewed-only contradiction trace）をプリセット化する。

### M7. AI-aware Perspective Mode

人間向け視座とは別に、AI問い合わせに適した視座モードを導入する。

---

# 11. UI / UX 要件

## 11.1 キャンバス主、チャット従

AIとのやりとりは、チャット欄を主とするのではなく、**キャンバスに対して作用する補助操作** として設計する。

## 11.2 AI由来と人間由来を明確に区別

最低限、視覚的に区別すべき状態：

- AI提案
- 人間未確認
- 人間レビュー済
- 人間修正済
- AI由来だが人間承認済

## 11.3 保留を操作可能にする

- 採用しないが保持
- 比較候補として残す
- 反証待ちにする
- 根拠不足として保留する

など、「未決着」を表現できる必要がある。

---

# 12. 安全・統治要件

## 12.1 SafeMode

共有・配布・レビュー用途では safeMode を既定ONとする。

safeMode時：
- 未レビューAI文章は既定で出さない
- 生カードテキストは既定で出さない
- IDs / counts / reviewed flags 中心に落とす

## 12.2 Review Attribution

AI出力が最終的に採用される場合でも、
- 誰がレビューしたか
- どの時点で承認されたか
- どの差分が適用されたか

を追跡可能にする。

## 12.3 Auditability

AI Context Query と AI出力は、必要に応じて
- query log
- generated patch
- apply log

として監査可能であることが望ましい。

---

# 13. 既存設計との接続

本拡張は、既存の以下の設計資産を前提とする。

- patch / diff / conflict detect
- review attribution
- safe mode policy
- diagnostics / contradiction / evidence trace
- perspective / reading path / presets
- worker-based computation

したがって、新機能は既存資産を置き換えるのではなく、**AI問い合わせ層として接続** することを原則とする。

---

# 14. プロジェクト判断基準

この方向性に沿う機能かどうかは、次の問いで判定する。

1. これは人間の思考を雑にしないか
2. これはAIに早すぎる収束を与えないか
3. これは保留・対立・未レビューを保持できるか
4. これは差分・監査・レビューに載るか
5. これは人間向け文脈とAI向け文脈を混同していないか

いずれかに強く反するなら、採用しない。

---

# 15. 今後の設計・実装フェーズ

## Phase A：文脈投影の確立
- ContextQuery / ContextBundle の仕様化
- Preview UI
- safeMode制約統合

## Phase B：低リスクAI支援
- 島タイトル候補
- B型文章ドラフト
- 反対視点候補

## Phase C：高度化
- AI Patch Workspace
- Query Presets
- AI-aware Perspective

## Phase D：CLI / API 連携
- Query を API / CLI から呼べるようにする
- バッチ生成・評価・監査を可能にする

---

# 16. 結論

kj-atlas のAI拡張の本質は、AIを賢くすることではない。  
本質は、

> **生成AIが単独では維持しにくい高度な文脈・対立・保留・根拠の構造を、人間と共有できる外部思考空間として保持すること**

にある。

この方向性において、kj-atlas は単なる図解ツールではなく、

> **生成AI時代の高度な情報処理を支える、認知外在化フレームワーク**

として位置づけられる。
