# ROADMAP

**English summary**  
kj-atlas aims to become a safe, human-in-the-loop diagramming environment for structured qualitative synthesis.  
This roadmap prioritizes UX refinement, structural analysis tools, localization readiness, and community-driven evolution, while maintaining privacy-by-default and offline-first principles.

この文書は、**開発コミュニティ向けの公開コミュニケーション文書**です。  
詳細な実装順序・個別タスクは `01_Plans/` を参照してください。
特に、ロードマップ項目を実装アクションへ分解した管理は `01_Plans/adr/ADR-0007-future-backlog.md` の「Roadmap統合バックログ」を正とします。

## 基本方針

kj-atlas は以下を中核とする：

- 🧠 意味の保留（Ambiguity Preservation）
- 🔁 Human-in-the-loop 構造思考支援
- 🔒 SafeMode デフォルトの安全設計
- 🌐 オフライン / 自前ホスト前提
- 📦 OSSとして持続可能な規模感

## 近接フェーズ（Next 1–2 Releases）

### 1. UX深化

- 視座プリセット（Explore / Review / Summary）
- 島の折りたたみ（階層可視性制御）
- 多角形島（Polygon islands）
- SafeMode のUI明示性強化

### 2. 研究用途強化

- Trace Analytics（根拠構造の統計）
- 構造メトリクス（健全性指標）
- Diagnostics出力の安定化

### 3. セキュリティ維持

- ZIP import の継続的ハードニング
- Workerベース処理の安定化
- CIによる回帰防止

## 中期フェーズ（Mid-term Vision）

### A. 類似カード統合（Card Consolidation）

#### 背景
- 大規模運用ではカード数が増えすぎる
- 類似カードは代表1枚へ統合する必要がある

#### 想定機能
- 類似度検出（非AI deterministic heuristic）
- 統合候補提示
- 統合ログ保持（監査対象）
- 代表カード下に「統合済みカード一覧」を保持（折りたたみ対応）

### B. 質的統合法対応（Hierarchical Qualitative Synthesis）

#### 背景
- 質的統合法（KJ法）の本来のプロセスにおいて、階層的統合は核心となる
- デジタル環境でも、ボトムアップな統合過程を可逆的に再現できることが重要

#### 想定拡張
- 島の中にサブ島（階層ネスト）を持つ入れ子構造の可視化
- 「表札（見出し）カード」による下位カード群の代表・要約
- 鳥観⇄枝葉切替UI（レベルスライダー）による全体像と詳細のシームレスな移行
- 構造レベル別エクスポート（抽出レベルに応じたアウトライン出力を含む）

### C. LLMアダプタ基盤（Local / Large-scale 共通）

- 標準的な運用では大規模LLMの利用を想定する
- 同一の抽象インタフェースで、ローカルLLM（例：Ollama等）と大規模LLMの双方を扱う
- LLMは「補助提案」専用（決定は常に人間）
- SafeModeポリシー適用対象（利用形態に依存せず統一適用）
- 外部接続の可否はデプロイポリシーで切り替え可能にする

### D. API課金回避のための定額/オフライン AI 補完経路

#### 背景
- 生成AIのAPI利用は従量課金がかさみ、MVP段階では API 利用が困難な場合がある。
- 定額のチャットやAIエージェントで高度な思考を補完するワークロードが現実解になりうる。

#### 想定機能
- キャンバスの文脈（カード/島/関係など）と生成AI向けプロンプトを一体で書き出す。
- 外部の定額AI/エージェントによる思考結果を、次のいずれかでキャンバスへ反映する：
  - 低額なローカルLLMを用いて反映する経路、または
  - 構造化された変更指示（スキーマ化したパッチ/操作列）を出力させ、専用の適用ロジックで反映する経路（要・適用ロジック）。
- SafeMode と人間による承認（HIL）を維持し、自動確定はしない。

> MVP において API 利用が困難であることへの回答。LLMアダプタ基盤（C）と整合させる。
>
> 仕様化（2026-07-05）: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（決定）＋ `02_Architecture/external_agent_collaboration_spec.md`（契約正本）。(b) 構造化変更指示ルートを AgentTaskPackage/AgentResponse v1 として具体化（Copilot / Copilot Studio プロファイル同梱・Tier 0 手動授受を MVP とする）。実装は `EXT-AGENT-01/02/03`。

## ローカライゼーション（Localization Strategy）

### 基本方針

- 日本語を一次言語とする
- UI文字列は内部的に英語キー管理
- 翻訳可能構造にするが、初期段階で多言語化は強制しない
- Packデータ（`document.json`）は言語非依存

### 段階的対応

#### Phase 1: 内部i18n準備
- UI文言をハードコードから分離
- JSON翻訳ファイル構造を用意
- 英語UIの最低限サポート

#### Phase 2: 多言語対応拡張
- 英語完全対応
- コミュニティ翻訳導入可能構造
- 言語選択設定（view単位）

#### Phase 3: Packの多言語安全設計
- `document.json` は言語非依存
- 表示言語はview依存
- SafeMode下で言語変換による情報漏洩が起きない設計

## 長期ビジョン（Long-term）

### 1. 島形状の高度化
- 自由曲線（Spline）
- 不定形包囲
- 密度ヒートマップ重畳

### 2. 多人数利用（慎重に検討）
- 同時編集はスコープ外
- 将来的に「差分レビュー共有」型で対応可能性

### 3. 監査強化（Optional）
- 署名付きレビュー記録
- 監査ログハッシュ
- 研究用途向けエビデンス保存

## 展開・公開運用（Publishing & Access Control）

企業・行政などの運用では、公開範囲や認可要件が大きく異なるため、以下を並行検討する。

### 方式A：静的配信（広域公開向け）
- Export（Bundle/Review Pack）を定期連携し、S3 + CDN 等の静的配信へ展開
- SafeMode 強制（既定ON、解除不可の公開モードを用意）
- 公開に必要な最小ファイル（index + assets + packs）を生成する「Static Publish」モード

### 方式B：認証付き配信（限定公開向け）
- 統合認証（OIDC/SAML）でユーザ識別
- API層で認可（RBAC/ABAC）を実施し、文書単位の公開範囲を制御
- 監査ログと連動（閲覧/エクスポートのイベント記録は外部ログ基盤に送信可能）

### 方式C：ハイブリッド（現実解）
- 内部は方式Bで厳格管理
- 市民向けは方式Aで低コスト公開
- 「公開版生成」をエクスポートパイプラインで担保（匿名化・伏字・SafeMode強制）

### Mid-term 実装候補
- visibility（Public / Unlisted / Org / Restricted）を pack/view メタに導入
- `isReadOnly` を受け取ってUIを制御（アプリ内RBACは持たない）
- Static Publish 出力（S3/静的Web向け）を公式サポート
- DocumentACL 抽象I/F（roles/groups/policyRef）を定義し、実装は外部に委譲

## 非目標（Out of Scope）

- SNS型公開プラットフォーム化
- AIによる自動結論生成
- SaaS依存設計
- 大規模リアルタイム共同編集

## 設計原則（常に維持する）

- `document.json` は純粋構造データ
- `view.json` は視座とメタ情報
- safeMode は既定ON
- 個人情報は保存しない
- Workerによる非ブロッキング処理
