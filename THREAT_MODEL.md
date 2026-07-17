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
7. 標準Composeのネットワーク公開境界

## 資産 / Assets

- ユーザーが作成したドキュメント（カード・メモ・配置情報）
- インポート入力（ZIP/markdown/JSON）
- ビルド・配布成果物
- 依存ライブラリ由来の実行コード

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
- 外部結線前に、全constraintで未レビューentity/refの既定除外と、SafeMode出力に原文由来hashが無いことを検証

### 6-1) HTTP transport / OAuth 2.1 resource server（Subslice C, ADR-0054）

stdio段階では listen port を開かず外部到達不可だったが、streamable-HTTP transport（`KJ_ATLAS_MCP_TRANSPORT=http`）は本リポジトリ初の公開ネットワークリスナーであり、リスクの質が変わる。

- 未認証／偽造／期限切れbearer tokenによる `POST/GET/DELETE /mcp` への到達
- 他リソース向けに発行されたtoken（audience違い）や、信頼していないissuerが発行したtokenの受理（confused deputy）
- 本サーバーが誤って authorization server 相当の機能（token発行・client登録・consent）を持ってしまうscope creep
- 単純なリクエスト洪水によるCPU/メモリ枯渇（DoS）
- 認証エラー応答から到達可能性・内部実装がfingerprintされる情報漏えい
- `/.well-known/oauth-protected-resource` のような未認証で公開する必要があるエンドポイントが、意図せず認証必須のエンドポイントにも認証バイパスの糸口を与える

**想定対策**

- ADR-0054/ADR-0020方針どおり、本サーバーは OAuth 2.1 **resource serverのみ**として実装し、token発行・client登録・authorization endpointは一切持たない（そのコードパス自体が存在しない）
- `jose`の`jwtVerify`でtoken署名・`iss`（`KJ_ATLAS_MCP_TRUSTED_ISSUER`と厳密一致、prefix/wildcard一致は行わない）・`aud`（`KJ_ATLAS_MCP_RESOURCE_URL`）・`exp`を検証し、失敗経路はすべて`InvalidTokenError`にfail-closedで正規化（未知の失敗が既定で通過することはない）
- SDKの`requireBearerAuth`により、認証失敗は常に401 + `WWW-Authenticate: Bearer ... resource_metadata=...`ヘッダーで応答し、tokenの有効性以外の情報（存在確認・詳細な失敗理由）を返さない
- `/.well-known/oauth-protected-resource`（RFC 9728）は仕様上未認証公開が前提のdiscovery文書であり、`resource`/`authorization_servers`/`bearer_methods_supported`など非秘匿情報のみを返す。`/mcp`自体の認証要件は変えない
- 全route（metadata含む）に60 req/min/IPのrate limitを適用し、単純な洪水要求を早期にthrottleする
- transportはstateless（`sessionIdGenerator: undefined`）とし、session固定化やsession storageに起因する攻撃面を持たない
- request bodyは1MBに制限し、過大payloadでのメモリ消費を防ぐ

### 7) 標準Composeのネットワーク公開境界（DEPLOY-NET-01）

`http://localhost:8080` という案内は、サービスがloopbackだけでlistenすることを意味しない。host IPを省略したDockerのport公開（`"${KJ_ATLAS_WEB_PORT:-8080}:80"`）はホストの全interfaceを対象にし、同一LANや誤設定されたport forwardingから到達できる未認証主体に、評価環境そのものを公開してしまう。

- 保護資産: document本文、レビュー情報、設定・診断情報
- 攻撃者: 同一LAN、共有ホスト、誤設定されたport forwardingから到達する未認証主体
- 入口: nginx配信面（`web`サービス）と、そこから転送される`/api`
- 誤解しやすい非対策: SafeMode（share/exportの漏洩抑制であり、ネットワーク経由の到達を認証しない）、`KJ_ATLAS_API_KEY`（同梱SPAが`X-API-Key`を送らないため、通常のブラウザ利用を保ったまま既定露出を補う認証にはならない）、URLに`localhost`と表示すること

**想定対策**

- 標準`docker-compose.yml`の`web.ports`をloopback（`127.0.0.1:${KJ_ATLAS_WEB_PORT:-8080}:80`）へ明示bindし、`KJ_ATLAS_WEB_PORT`はport番号だけを変え、bind範囲を拡張しない契約にする
- 別端末・LAN・Internetからの利用が必要な場合は、TLS終端・SPAとAPIの双方を覆う認証proxy・接続元制限・secret管理を伴う明示的な別deployment profileとして分離し、base Composeの直接書き換えでは対応しない
- READMEとinstallation/deployment文書で、標準Composeを「同一ホストからだけ使う評価構成」と明記する
- contract testで、標準Composeのweb port mappingがhost IP省略・`0.0.0.0`・loopback以外へ戻らないことを検証する

## 検証・運用 / Verification

- import / sanitize / diff・merge 系の回帰テストを維持
- PRでセキュリティ影響を明示（必要時）
- 脆弱性報告フローは `SECURITY.md` を参照

## Out of Scope / 範囲外

- 完全オフライン運用時における、広域ネットワーク攻撃者モデル
- OS/ブラウザ/企業内基盤そのもののゼロデイ対策
