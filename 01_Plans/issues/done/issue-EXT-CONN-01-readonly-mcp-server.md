# Issue Draft: EXT-CONN-01 read-only MCP サーバー（ContextBundle 制約付き投影の公開）

- Type: Feature request
- Status: Done
- Progress: サブスライスA・B・C（実装・テスト・`THREAT_MODEL.md`追記）完了。サブスライスC（[PR #2602](https://github.com/hat47x/kj-atlas/pull/2602)）はセキュリティレビュー後、Maintainer（hat47x）により2026-07-16にマージ済み。受け入れ条件AC-1〜AC-5はすべて充足済み（下記「実装記録」参照）。

## Draft→Open 2026-07-12
`ADR-0054` が maintainer により Accepted（受理時条件: 用語「庭」→「縁側」置換、ADR側で対応済み）。本Issueの唯一のゲートが解消したため Open 化。
- Source Issue: N/A（`ADR-0054` 段階1）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/backend/`（または新規 `03_Implement/mcp/`）, `03_Implement/frontend/src/export/agent_task_export.ts`（投影ロジックの共有・抽出）, `THREAT_MODEL.md`, `02_Architecture/api.md`
- Related Backlog: `EXT-CONN-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`, `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`（CE-4）
- Expected verification level: `integration`（HTTP輸送を実装する場合は `e2e` へ引き上げ）

## Requirement meta I/F（共通キー）

- RequirementID: EXT-CONN-01
- RequirementStatement: 外部エージェント（Claude Code / ChatGPT / Copilot Studio）が、レビュー済み等の制約付き投影として kj-atlas の文脈を読み取れる read-only MCP サーバーを提供する。書き込みツールは持たない。
- AcceptanceScenario: 前提=ADR-0054 Accepted / 操作=MCPクライアントから制約付き投影（reviewed-only 等）を読む / 期待結果=SafeMode境界どおりの内容だけが返り、監査相関（bundleHash等）が記録される / 除外=書き込み、トリガー実装、通知。
- SecurityGateImpact: SafeMode / share-export / public-exposure

## 背景

`ADR-0049` の手動レーン（copy/paste）で確立した安全境界（SafeMode本文redaction・未レビュー既定除外・反スコアリング・監査相関）を、MCP 輸送で自動化する第一段。読み取り専用のため最小リスクで、ChatGPT個人プランの「カスタムコネクタは読み取り専用」制約とも一致する。

## 提案する解決策

- MCP resources/tools として公開する投影: reviewed-only カード集合、根拠（evidence）サブセット、矛盾（contradiction）サブセット、島/関係の要約。ContextBundle IR（CE-0契約）の形を正とする。
- 投影ロジックは `agent_task_export.ts` の DocumentV2 直接走査＋SafeMode境界を再利用（バックエンドへ移植またはNode共有）。CE-1 実データ化を待たない。
- 輸送は stdio 先行（ローカル Claude Code）。streamable HTTP + OAuth 2.1（MCP 2026-07-28 仕様）は同一契約の追加アダプタとして分割可。
- すべての読み取りに `bundleHash` / `queryCanonicalHash` 相当の監査相関を残す（CE-4 整合）。

## 非目標

- 書き込み・提案受信（`EXT-CONN-02`）。
- トリガー/スケジューラ・通知プッシュ。
- MCP Apps（チャット内UI描画）。
- score/rank/confidence/priority を含む投影。

## 受け入れ条件（案）

- [x] AC-1: MCPクライアントから reviewed-only 投影を取得でき、未レビュー本文・SafeMode対象が含まれない。→ reviewed-only constraintに加え、evidence/contradiction/summaryの全constraintで未レビューentity/refをlink単位（両端点reviewed必須）で除外し、SafeMode redactionから短縮hashを除去済み（2026-07-13、下記「実装記録」参照）。MCP経由の取得（実結線）はサブスライスBで行う。
- [x] AC-2: サーバーは書き込み系ツールを一切公開しない（tools/list で検証）。→ `kj-atlas-mcp`（`03_Implement/mcp/`）実装完了。`tools/list` は `get_context_projection` の1件のみ、`resources`capabilityは`initialize`応答に一切含まれない（登録ゼロのため`resources/list`はメソッド自体が存在しない）。固定snapshotテストで検証済み（下記「実装記録」参照）。
- [x] AC-3: 読み取りごとに監査相関が記録され、CE-4 の監査導線から追跡できる。→ ローカル構造化監査ログ（stderr、`mcp-context-read.v1`）で`bundleHash`/`queryCanonicalHash`相当を全readで記録。**2026-08-16 に CE-4 バックエンド`POST /docs/{id}/context-audit`（`channel="mcp"`）への実結線を完了**（下記「実装記録（2026-08-16）」参照。それ以前は既知ギャップとしてローカルログのみ）。
- [x] AC-4: `THREAT_MODEL.md` に公開面（認証・認可・レート・失敗時挙動）が追記され、PRODUCT-QA-01 ゲートで照合される。→ `THREAT_MODEL.md` §6-1 として追記完了（2026-07-16、下記「実装記録」参照）。
- [x] AC-5: 投影IRは輸送非依存で、MCPアダプタ層の差し替えが契約変更なしに可能な構造になっている。→ `context_bundle_projection.ts` として実装。純粋関数・輸送非依存・`ContextProjectionV1` IR固定。

## 実装記録（2026-07-12）: サブスライスA 完了 — 輸送非依存の投影コア

本Issueを輸送別に3サブスライスへ分割し、最も安全性が重くかつ今すぐ検証できる投影コアから着手した:

- **サブスライスA（本コミット・完了）**: `03_Implement/frontend/src/export/context_bundle_projection.ts`。`buildContextProjection(doc, constraint, safeMode)` が reviewed-only / evidence / contradiction / summary の4制約で read-only 投影を生成する純粋関数。安全境界は既存 `SafeModePolicy` を**そのまま**使用（`agent_task_export.ts` と同一の "share" 境界。2言語複製によるredactionドリフトを回避）。外部読み取り面は常に share 境界とみなし、SafeMode ON では reviewed カード本文も出さない。反スコアリング（score/rank/confidence/priority を出力・ハッシュとも一切含めない）と決定的 `bundleHash`（redact された本文は原文でなく null をハッシュ＝原文が相関ハッシュへ漏れない）を単体テストで固定（`context_bundle_projection.test.ts`、11 tests）。
- **サブスライスB（次）**: stdio MCP アダプタ。`resources`/`tools` として投影を公開（read-only、書き込みツールなし＝AC-2）、`GET /docs/{id}` から DocumentV2 を取得、bundleHash を ingest/query ログへ記録（AC-3）。配置は `03_Implement/mcp/`（新規 Node パッケージ）を第一候補とし、本モジュールを monorepo import で共有する（ドリフト回避）。共有の物理配置（frontend/src 直下のままか shared パッケージへ hoist するか）はサブスライスB着手時の構造判断。
- **サブスライスC（後）**: streamable HTTP + OAuth 2.1（MCP 2026-07-28 仕様）輸送を追加し ChatGPT / Copilot Studio へ到達。公開面の脅威追記（AC-4）と PRODUCT-QA-01 セキュリティ照合はここで実施。

## Maintainer代理裁可（2026-07-13）: サブスライスB Conditional Go

MCP SDK依存の追加と `03_Implement/mcp/` 新設を承認する。ただし、次をサブスライスBの固定条件とする。

- `03_Implement/mcp/` はfrontendとは独立したprivate Node packageとし、独自の `package.json` / `package-lock.json` / `tsconfig.json` を持つ。root workspace化は行わず、frontendの依存・lockfileへMCP SDKを混ぜない。
- 現在の公式推奨に従い、stdio実装は `@modelcontextprotocol/sdk` v1系の**正確なversion**をpinする（判断時点の採用値は `1.29.0`）。必須peer dependencyのZodも互換な4.xの正確なversionをpinし、lockfile差分と依存監査を同じ変更で確認する。開発中/pre-alphaのv2分割packageは採用せず、stable v2公開後に別スライスで移行可否を判断する。
- runtimeはリポジトリの `.nvmrc` と同じNode 20を使う。stdio以外のlisten portを開かず、サブスライスBではHTTP server/OAuth依存を追加しない。
- 投影コアはコピーせず、現行 `context_bundle_projection.ts` をmonorepo source importしてSafeModeロジックを一系統に保つ。第2の非frontend利用者が現れるまではshared packageへのhoistを行わない。
- MCP capabilityはread-only resourcesとread-only toolsだけにallowlistし、write/ingest/apply/publish/sampling/elicitationを登録しない。`tools/list` / `resources/list` の固定snapshotで検証する。
- 依存追加・package新設は承認するが、外部クライアントへの結線前に投影コアを再検証する。全constraintで未レビューentity/refを既定除外し、SafeMode出力に原文由来の短縮hashを含めないことをテストで固定する。現在のサブスライスAがこの条件を満たさない場合は、Bの公開結線を停止してAを先に修正する。
- すべてのreadで `bundleHash` / `queryCanonicalHash` 相当を監査相関へ渡す。監査失敗は本文露出を広げず、読み取り結果と相関欠損を成功扱いにしない。

この判断は依存と配置の可否を確定するもので、サブスライスBの実装完了を意味しない。未使用依存だけを先行追加せず、server skeleton・capability test・投影安全テストと同じ変更単位で導入する。

## 実装記録（2026-07-13）: 投影コア安全ゲート修正完了 — サブスライスB着手可能に

Maintainer代理裁可が課した「外部結線前の投影コア再検証」を実施し、2件の実欠陥を修正した（`context_bundle_projection.ts`）。

1. **他constraintの未レビューentity/refリーク**: `evidence`/`contradiction` constraintはリンクの両端点カードを「そのリンクが存在する」という理由だけでscopeに含めており、reviewed状態でのフィルタを一切適用していなかった。`summary` constraintの`relations`（edge一覧）も同様に全カードを対象にしていた。結果、未レビューカードの本文は既定どおり redact されるものの、その **id・claimType・リンクの存在自体（＝未レビューカードが特定の主張と矛盾/根拠関係にあるという事実）** が全constraintで露出していた。修正: `supports`/`contradicts`/`relations` のいずれも「両端点が reviewed であるリンクのみ」をscope対象とするよう統一。未レビューカードはリンクの片方に現れた時点でそのリンクごと除外され、bare な id としても一切現れない。
2. **SafeMode redaction の短縮hash露出**: `projectCardText` は非公開時に `SafeModePolicy.summarizeForSafeMode()` を使っており、これは `[REDACTED]:h########`（原文の32bit短縮hash）を返す。この関数は人間が1回選んでコピー&ペーストする `agent_task_export.ts` 向けに設計されたもので、**繰り返し問い合わせ可能な常設外部面（MCP）では、同一hashが返ることで「この2枚のredact済みカードは実は同一本文」という相関情報を与えてしまう**。`SafeModePolicy.redactText()`（文字数のみを含む、hashなしのプレースホルダ）へ置き換えた。
3. **bundleHashへの影響なし**: `hashPayload` は元々 `redacted ? null : text` としており、redactプレースホルダ文字列自体をhash対象に含めていなかった（`bundleHash`の相関漏れは元から無し）。今回の修正は投影の**出力**（`cards[].text`）側のみに影響する。

`context_bundle_projection.test.ts` を 11→15 tests へ拡張し、両修正を固定した（未レビュー端点を含むリンクの完全除外、reviewed端点のみのリンクは維持、短縮hash不在の正規表現アサーション、全constraint横断での未レビューid不在チェック）。既存1030テスト・typecheckともに回帰なし。

この修正により、Maintainer代理裁可が定めた「外部クライアントへの結線前」条件が満たされたため、AC-1をFixedとし、サブスライスB（stdio MCPアダプタ）へ進める。

## 実装記録（2026-07-16）: サブスライスC 完了 — streamable-HTTP輸送 + OAuth 2.1 resource server

`ADR-0054`/`ADR-0020`が定める「本サーバーはresource serverのみ、authorization server機能は一切持たない」方針に厳密に従い、外部トークン発行者（既に信頼済みの外部IdP）が発行したbearer tokenを検証する層のみを追加した。token発行・client登録・consent画面などの実装は行っていない（そのコードパス自体が存在しない）。

- **輸送選択**: `KJ_ATLAS_MCP_TRANSPORT`環境変数（既定`stdio`）で`stdio`/`http`を選択（`src/index.ts`）。stdio経路は無改修。
- **HTTP設定 (`src/oauth_config.ts`)**: `loadHttpTransportConfigFromEnv()`が`KJ_ATLAS_MCP_RESOURCE_URL`/`KJ_ATLAS_MCP_TRUSTED_ISSUER`/`KJ_ATLAS_MCP_JWKS_URI`を必須環境変数としてfail-closedで読み込む（未設定は起動時エラー、安全側デフォルトへのフォールバックはしない）。`KJ_ATLAS_MCP_AUTHORIZATION_SERVERS`（省略時は`KJ_ATLAS_MCP_TRUSTED_ISSUER`）・`KJ_ATLAS_MCP_HTTP_HOST`/`_PORT`（既定`127.0.0.1:8787`）は省略可。
- **Token検証 (`src/oauth_verifier.ts`)**: `jose`の`jwtVerify`で署名・`iss`（`trustedIssuer`と厳密一致）・`aud`（`resource`）・`exp`を検証。すべての失敗経路（署名不正・issuer不一致・audience不一致・期限切れ・claim欠落・不正形式token）を`InvalidTokenError`へ正規化し、SDKの`requireBearerAuth`が401として応答する（未知のErrorをthrowすると500になる既知の落とし穴を回避）。`client_id`→`azp`→`sub`の順でclient識別子を解決。CVI反スコアリング（`ADR-0041`）の防御的テストとして、token claimに`score`/`rank`/`confidence`/`priority`を含めても`AuthInfo`にその語彙が一切現れないことを固定。
- **HTTP app (`src/http_server.ts`)**: `express`上に、`GET /.well-known/oauth-protected-resource`（RFC 9728、未認証で公開必須のdiscovery文書）と、認証必須の`POST/GET/DELETE /mcp`（`StreamableHTTPServerTransport`、`sessionIdGenerator: undefined`のstateless構成）を構築。全route共通で60 req/min/IPのrate limitとrequest body 1MB上限を適用。
  - **実装中に発見・修正した実欠陥**: SDKの`metadataHandler()`は内部に独自の`/`routeを持つExpress Routerを返す設計だが、当初`app.get(path, metadataHandler(...))`でマウントしていたためExpressがmount pathを`req.url`から剥がさず、Routerの`/`routeが常に不一致となって404を返す状態だった（`app.use(path, ...)`が必要）。`http_server.test.ts`の実HTTPリクエストによる統合テストで検出し、`app.use`へ修正して解消。
- **依存追加**: `express@5.2.1`・`express-rate-limit@8.5.2`・`jose@6.2.3`（SDK 1.29.0が既に解決するtransitive依存と正確に一致するversionをpin、Maintainer代理裁可の既存慣行を継続）。`npm audit`は`found 0 vulnerabilities`。
- **テスト**: `oauth_config.test.ts`（8）・`oauth_verifier.test.ts`（10、CVI防御込み）・`http_server.test.ts`（5、実Express appへの実HTTPリクエストによる統合テスト。ローカルJWKSへ`vi.mock("jose")`で`createRemoteJWKSet`のみ差し替え、ネットワークアクセス・モックIdPプロセスとも不要）を新規追加。既存`document_client.test.ts`/`audit_log.test.ts`/`context_projection_tool.test.ts`（計21 tests）は無改修・無回帰。全44 tests green、typecheck 0 errors。
- **`THREAT_MODEL.md`更新**: §6-1として、未認証/偽造/audience違いtoken・authorization server機能への意図しないscope creep・DoS・エラー応答からの情報漏えいの各脅威と、resource-server-only scope・fail-closed検証・rate limit・stateless transport・body size上限の対策を追記（AC-4）。
- **README更新**: `03_Implement/mcp/README.md`に新規環境変数一覧・HTTP輸送時の挙動・resource-server-onlyの非目標を追記。
- **AC-3の既知ギャップは継続**: CE-4バックエンド監査エンドポイントへの実結線は本サブスライスでも未実施（サブスライスB記録済みのギャップと同一理由、backend `channel` enumの拡張が必要）。HTTP輸送でも同じローカル構造化ログ方式を継続する。
- **意図的にレビュー保留**: 本サブスライスは本リポジトリ初の公開ネットワークリスナー・初のOAuthコードであるため、Maintainer裁可済みの自動マージ運用（サブスライスA/B適用）を今回は適用せず、セキュリティレビュー完了までPRをマージ待ちで保持する。

## 実装記録（2026-07-13）: サブスライスB 完了 — stdio MCPアダプタ

Maintainer代理裁可の固定条件に従い、`03_Implement/mcp/` を新設した。

- **独立パッケージ**: 独自の `package.json`/`package-lock.json`/`tsconfig.json`。frontendとは依存もlockfileも共有しない。root workspace化なし。
- **依存pin**: `@modelcontextprotocol/sdk@1.29.0`（決定時点の最新かつ承認値と一致を`npm view`で確認済み）、peer dependency `zod@4.4.3`（`^3.25 || ^4.0`要件を満たす最新4.x）。`npm audit` は当初 `vitest` UI serverの critical 脆弱性（devDependency、`vitest run`のみ使用のため無関係）を検出したため `vitest@4.1.10` へ修正pinし、`found 0 vulnerabilities` を確認。
- **投影コアの共有**: コピーせず `../frontend/src/export/context_bundle_projection.ts` を相対パスでmonorepo source import。frontend側の拡張子省略import規約（Vite/bundler前提）と衝突したため、本パッケージの`tsconfig.json`は`moduleResolution: "NodeNext"`ではなく`"bundler"`を採用（実行も`tsx`＝esbuildベースのため実挙動と一致）。frontend側のファイルは無改修。
- **実装**: `get_context_projection({docId, constraint, safeMode?})` の1ツールのみを登録（`src/context_projection_tool.ts`）。`safeMode`省略時は`true`（安全側既定）。`document_client.ts`が`GET /docs/{id}`から`DocumentV2`を取得（`KJ_ATLAS_MCP_API_BASE_URL`・`KJ_ATLAS_API_KEY`環境変数、後者はブラウザ側が送らない`X-API-Key`をこのプロセス自身が送信）。stdio輸送のみ（`StdioServerTransport`）、listen portなし。
- **AC-3の既知ギャップ**: `bundleHash`/`queryCanonicalHash`相当は全readで算出しているが、バックエンドの`POST /docs/{id}/context-audit`（CE-4）への実結線は**今回実施しなかった**。同エンドポイントの`channel`enumは`"api"|"cli"|"gui"`に固定され、`command`もbackend側whitelist制御（`agent_response_import.ts`の同種ギャップをApp.tsx自身のコメントが記録済み）で、MCP由来のreadを流す枠がない。これを追加するのはbackendの共有監査契約を変更することになり、本サブスライスの承認範囲（MCP SDK依存＋パッケージ新設のみ）を超える。暫定として、全readをローカル構造化ログ（stderr、`mcp-context-read.v1`スキーマ）に記録する方式を採用した。CE-4への実結線はサブスライスCまたは専用backend issueへ切り出す。
- **capability allowlist検証**: `context_bundle_projection.test.ts`と対をなす形で、`InMemoryTransport.createLinkedPair()`で実際のClient⇔Serverペアをプロセス内接続し、`tools/list`が`get_context_projection`一件のみであること、`resources`capabilityが`initialize`応答に一切含まれないこと（`resources/list`はメソッド自体が存在せず`-32601`を返す＝空リストより強い「未登録」の証明）、write/ingest/apply/publish/create/update/delete/sampling/elicit名を持つツールが存在しないことを固定した。加えて、実際の`tsx src/index.ts`プロセスへ生JSON-RPC（initialize→initialized→tools/list）を送るスモーク検証で、stdoutにプロトコルメッセージ以外が一切混入しないことも確認した。
- **テスト**: `document_client.test.ts`（8）・`audit_log.test.ts`（5）・`context_projection_tool.test.ts`（8、上記capability allowlist込み）、計21 tests、typecheck 0。
- **非目標（維持）**: 書き込み・提案受信、HTTP/OAuth輸送、MCP Apps。

## Close-out（2026-07-16）: サブスライスC マージ、Issue Done化

`PR #2602` はMaintainer（hat47x）によるセキュリティレビュー後、2026-07-16にマージされた（マージコミット `8ebd28e97138facf3d140ddb4f37d883b11a4d2b`）。サブスライスA・B・Cの実装・テスト・脅威分析はすべて完了し、AC-1〜AC-5は充足済みのため、本Issueを `Done` とする。

- AC-3のCE-4実結線ギャップ（backendの`channel`enum拡張が必要）は、本Issueの承認範囲外として明示的に切り出し済みの既知の未実装であり、`Done`化のブロッカーとしては扱わない。CE-4への実結線が必要になった時点で、専用のbackend issueとして別途起票する。
- `EXT-CONN-02`（webhook提案ingest）は引き続き`Draft`であり、本Issueの`Done`化とは別に「EXT-CONN-01の運用実績」ゲートが残る。運用実績はマージ後の実利用を通じて蓄積されるものであり、本Issueの完了条件には含まれない。

## 実装記録（2026-08-16）: CE-4 監査結線（`channel="mcp"`）で AC-3 の既知ギャップを解消

`Close-out` で「既知の未実装」として切り出していた AC-3 の CE-4 実結線ギャップ（backend `channel` enum に `"mcp"` スロットが無い）を、専用 backend issue 相当の変更として解消した。

- **backend**: `ContextAuditPayload.channel` を `Literal["api", "cli", "gui", "mcp"]` へ拡張（`03_Implement/backend/src/kj_atlas_api/routes/docs.py`）。`api.md` の channel enum・消費者境界注記を `"mcp"` 込みへ更新。
- **MCP**: 成功した投影読み取りごとに、`emitContextAuditEvent`（`src/audit_log.ts`）が `POST /docs/{id}/context-audit` へ `operation=query` / `command=context-query` / `channel="mcp"` / `equivalenceKey=queryCanonicalHash` / `bundleHash=projection.bundleHash` / `safeMode` / `dryRun=true` / `sideEffect=none` を送出（`src/context_projection_tool.ts`）。MCP由来の read が api/cli/gui と同じ監査トレイルに載る。
- **best-effort 設計を明示**: CE-4 送出は追加の backend 可視シンクであり、読み取り自身の相関は従来どおり同期ローカル `mcp-context-read.v1`（stderr）エントリ。送出失敗は読み取りを失敗させず、構造化警告を stderr へ書く（`api.md` 消費者境界注記・MCP README runbook に明記）。
- **テスト**: backend `test_context_audit_endpoint_accepts_mcp_channel`（channel=mcp の受容と監査イベント伝播）＋ MCP `audit_log.test.ts` の `emitContextAuditEvent` 3件（POST body・非2xx・ネットワーク失敗の best-effort）。backend 29 passed・MCP 61 tests pass・docs-check passed。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/research/research-2026-07-12-trigger-ai-external-integration.md`
- Related: `03_Implement/frontend/src/export/agent_task_export.ts`（投影・redactionの前例実装）
- Related: `03_Implement/mcp/README.md`（パッケージの使い方・環境変数・非目標。stdio/HTTP両輸送）
- Related: `THREAT_MODEL.md` §6-1（HTTP transport / OAuth 2.1 resource serverの脅威分析、AC-4）
