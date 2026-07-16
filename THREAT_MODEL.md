# Threat Model / 脅威モデル（簡易）

この文書は本アプリケーションの現実的なリスクを、公開OSS運用向けに短く整理したものです。

## 対象範囲 / Scope

主に以下を対象とします。

1. ZIP import
2. Markdown rendering
3. Supply chain（npm/pip依存）
4. データプライバシー（エクスポート挙動を含む）
5. サポート診断バンドル
6. 外部エージェント向けMCP投影
7. SaaSを想定したテナント分離（現行非対応の適用限界を含む）

## 資産 / Assets

- ユーザーが作成したドキュメント（カード・メモ・配置情報）
- インポート入力（ZIP/markdown/JSON）
- ビルド・配布成果物
- 依存ライブラリ由来の実行コード
- 認証主体、テナント所属、外部エージェント登録とtoken

## 脅威とリスク / Threats

### 1) ZIP import

- Zip bomb による過大展開（CPU/メモリ/ディスク枯渇）
- `../` を含むパスによる path traversal
- 想定外の巨大ファイル・大量エントリ投入

**想定対策**

- 圧縮前後サイズ・エントリ数・1ファイル上限の cap
- 正規化パス検証（ルート外書き込み禁止）
- タイムアウト/中断可能な処理設計

### 2) Markdown rendering

- スクリプト埋め込みや危険属性による XSS
- URLスキーム悪用（`javascript:` など）

**想定対策**

- サニタイズのデフォルト適用
- 許可タグ/属性の allowlist 管理
- レンダリング前の危険スキーム除去

### 3) Supply chain

- npm/pip 依存の悪性アップデート
- 乗っ取り済みパッケージ混入
- トランジティブ依存経由の脆弱性流入

**想定対策**

- lockfile の利用と差分レビュー
- CI で lint/test を常時実行
- 依存更新PRの分離、最小権限でのレビュー

### 4) データプライバシー

- エクスポート物に不要な個人情報が混入
- 共有時に機微情報が漏えい

**想定対策**

- `safeMode` をエクスポート既定値として **ON**
- 既定でPIIを含めない運用（必要時のみ明示的に含める）
- 共有前の人手確認（human-in-the-loop）

### 5) サポート診断バンドル

- raw UserAgent、Document識別子、error message、ログや本文が診断JSONへ混入する
- SafeMode OFF時だけ露出項目が増え、共有境界を迂回する
- プレビューと実際のコピー/ダウンロード内容が異なる

**想定対策**

- `ADR-0053` の `diag-bundle.v1` allowlistだけから新規オブジェクトを構成し、未知キーを拒否
- SafeMode ON/OFFで露出境界を変えず、raw UserAgent、Document id/title、entity id/ref、message/stack、URL、秘密情報、本文を常時除外
- 明示操作・全文プレビュー必須・ローカル生成に限定し、自動送信、永続保存、生成時の追加通信を禁止
- プレビューとコピー/ダウンロードに同一の不変JSON文字列を使用

### 6) 外部エージェント向けMCP投影

- MCP SDKの依存追加によるsupply-chain面の拡大
- read-onlyと称したsurfaceにwrite/sampling/elicitation capabilityが混入する
- 未レビューentityや原文由来fingerprintがSafeMode投影から漏れる

**想定対策**

- MCPをfrontendから独立したprivate packageへ隔離し、SDK/peer dependencyを正確なversionでpinしてlockfileをレビュー
- capability allowlistと `tools/list` / `resources/list` の固定テストでwrite/ingest/apply/publish/sampling/elicitationを禁止
- stdio段階ではlisten portを開かず、HTTP/OAuth公開面は別スライスで脅威分析する
- 外部結線前に、全constraintで未レビューentity/refの既定除外と、SafeMode出力に原文由来hashが無いことを検証

### 7) SaaSテナント分離

- docIdの差し替えによる他テナント文書へのIDOR
- list/search/count/cacheからのタイトル・更新日時・利用状態の越境漏えい
- client指定のtenant/visibility/policy header偽装
- PDP不達時のread-only許可、adapter欠損時のnoop退避による他テナントread
- Admin API、agent token、API key、signed linkの他テナント再利用
- worker/job、監査、object storage、backup/restoreでtenant contextが欠落する
- 同一ブラウザのrecent/QueryPreset/選択状態がtenant切替後に残る

**SaaS提供前に必要な対策**

- TenantContextをverified claimまたはtrusted host mappingから一意に解決し、自由入力headerを信頼しない
- すべてのtenant従属行、子テーブル、agent registration、job、cache、auditへtenantIdを持たせ、複合unique/FKで補強
- 主体tenantと資源tenantの不一致をPDP呼出前にアプリ内で常にdeny
- tenant/visibility/policyRefをサーバー正本から解決し、クライアント値を認可根拠にしない
- SaaS profileではaccess-control欠損、noop、PDP不達、tenant不明をreadも含めてdenyし、設定不備はfail-fast
- recent/QueryPreset等をdeployment origin + tenantId + userIdで名前空間分離し、切替時にmemory/DOM/cacheを破棄
- 2つのtenantへ同じdocIdを用意したnegative matrixで、全API・export・MCP・webhook・auditの越境拒否を統合検証

**現行の適用限界**

現行DBにはtenantIdがなく、AuthContext/AccessRequestにもtenant境界がないため、共有DB型のマルチテナントSaaSとして運用してはならない。現行の`enterprise-production`は単一組織デプロイ向けと解釈する。`ADR-0059`はAcceptedだが、`01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`で契約・migration・DB側tenant guard・越境テストを完了してからSaaSを解禁する。

## 検証・運用 / Verification

- import / sanitize / diff・merge 系の回帰テストを維持
- PRでセキュリティ影響を明示（必要時）
- 脆弱性報告フローは `SECURITY.md` を参照
- SaaS関連変更では、同一docIdを持つ2tenantの越境negative matrixを必須にする

## Out of Scope / 範囲外

- 完全オフライン運用時における、広域ネットワーク攻撃者モデル
- OS/ブラウザ/企業内基盤そのもののゼロデイ対策
