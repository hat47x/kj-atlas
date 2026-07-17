# マスタ系設定データのUI/UX構想

- 区分: Internal / Task Brief（実装契約ではない）
- 対象: Workspaceの文書入口、文書内プリセット、Admin管理面、将来のエージェント登録
- 起点: `01_Plans/issues/issue-DATA-MODEL-OPS-02-management-plane-data-boundary.md`
- 設計依頼: `02_Architecture/design/design-request-2026-07-round8.md`

## 1. 結論

kj-atlasの「マスタ系設定」を1つの汎用マスタ管理画面へ集約しない。データの正本、利用者、機密性、変更頻度が異なるため、次の4面へ分ける。

1. **Workspace文書入口**: 一般利用者が認可済み文書を探して開く。タイトルを扱ってよい唯一の一覧面。
2. **文書内の表示・道具設定**: View/PerspectiveとQueryPresetを、使う場所の近くで維持する。保存範囲を明示する。
3. **Admin管理面**: strict provisioningと外部接続を扱う。通常のキャンバスから分離し、本文を一切扱わない。
4. **デプロイ・運用設定**: LLM providerやendpoint等は環境変数を正本とし、アプリ内では編集しない。必要なら秘密を含まない状態だけを読み取り専用で示す。

この分離により、「編集できる業務上の設定」「端末だけの作業道具」「管理者だけの登録情報」「コード・デプロイで固定する契約」を同じCRUD表へ押し込めずに済む。UIは正本を説明し、未実装のライフサイクル操作が存在するように見せない。

### 1.1 SaaS適用時の前提

現行実装は単一デプロイ／単一テナント相当であり、共有DB型SaaSのテナント分離を保証しない。SaaSでは、上記4面のすべてに**検証済みTenantContext**を追加し、Workspace、Tenant Admin、Platform Control Planeを分離する。

- tenantは画面フィルタではなく、DB/API/cache/audit/agent tokenを貫く安全境界とする。
- UIはbackendの`effectiveCapabilities`を表示に使うが、role名を解釈せず、API側の再認可を代替しない。
- 主体tenantと資源tenantの不一致、tenant不明、PDP不達はEmptyやread-onlyへ倒さず、readも含めてdenyする。
- D5〜D10は`01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`でAcceptedである。ただし、同ADRのImplementation gateを満たすまでSaaS tenant UIを有効化しない。

## 2. 設定データの分類とUI責務

| データ | 正本・保存範囲 | 主な利用者 | UIで提供する維持操作 | UIで提供しない操作 |
| --- | --- | --- | --- | --- |
| 文書インデックス | サーバーの`documents`からの認可済み射影。`GET /docs`は`id/title/updatedAt`だけ | Standard user / Document owner | 一覧、タイトル・IDによる絞り込み、更新日時順、開く | 本文プレビュー、横断本文検索、削除、アーカイブ、所有者移管、一覧からの複製 |
| 文書タイトル | Documentスナップショット | Document owner / 編集可能な利用者 | 文書を開いた状態で変更し、通常の保存競合処理に載せる | 一覧だけを使った背後の全文書PUT。タイトル専用契約がない段階のインライン更新 |
| View/Perspectiveと表示プリセット | `view.json.viewState`。文書本体へ埋め込まない | Standard user | 適用、カスタム保存、名前変更、カスタム削除、viewの入出力に含める | グローバル既定値への昇格、全利用者への自動配布 |
| Patch workspaceのQueryPreset | このブラウザ・端末だけ | Standard user | 保存、実行、名前変更、削除。「この端末のみ」を常時明示 | 同期済み・共有済みと誤認させる表示、サーバー保存、暗黙のexport/import |
| KJ語彙（claimType、関係種別、違和感タグ、holdState） | コードとAccepted ADR | 全利用者 | 意味の説明、凡例 | 任意追加・名称変更・無効化を行う「語彙マスタ」画面 |
| ユーザー / アイデンティティ | サーバーの`users` / `user_identities` | Platform operator | 現契約ではstrict provisioningの登録フォームと登録結果 | 一覧、無効化、削除、SCIM、ロール編集。別契約・ADRなしにライフサイクル管理を描かない |
| 文書アクセス設定（future SaaS） | active tenantの`document_access_metadata`。visibility、非秘密policy binding ID/versionのみ | `document.policy.manage`を持つTenant Admin | docId単位の参照、visibility変更、binding ID/version更新、競合安全な保存receipt | 文書タイトル・本文、raw policyRef/token/URL、bulk変更、role/group編集、他tenant参照 |
| エージェント登録 | 将来のサーバー正本。文書IDに束縛 | Platform operator | 契約実装後に登録、メタデータ一覧、失効。tokenは作成直後の一度だけ表示 | 文書ownerによる発行、平文token再表示、token検索、登録だけでの文書書込権限付与 |
| Auditメタデータ | 外部監査基盤または将来のメタデータ限定API | Security / Audit operator | `DATA-MAINT-04`で解禁された場合だけ固定allowlistを表示 | タイトル、本文、カード、narrative、review pack、diff、未レビュー情報、横断本文検索 |
| LLM provider・endpoint等 | `KJ_ATLAS_*`環境変数 | Platform operator | 秘密を含まない稼働状態の読み取り表示だけを将来検討 | アプリ内編集、秘密値表示、DBマスタ化 |
| constraint輸出セット | `EXT-CONN-03`で契約先行 | 文書利用者 / Platform operator | 将来、共有・外部接続の文脈で明示opt-in | 汎用マスタへの先行追加、既定ON |

SaaSではこの表に`Tenant`、`IdentityProvider`、`TenantMembership`が加わる。ただし、roles/groupsの編集画面は作らず外部IdP/PDPを正本とする。Tenant lifecycleはPlatform Control Plane、membership、document access metadata、agent registrationはTenant Adminへ分離する。`document.policy.manage`は`document.write`やPlatform operatorへ暗黙付与しない。

## 3. 情報設計

### 3.1 Workspace文書入口

現行のStartPanelと「最近のドキュメント」ダイアログを、サーバー正本の**ドキュメントを開く**導線へ段階的に置き換える。キャンバスを開いた後はキャンバスが主であり、文書一覧を常設サイドバーにはしない。

- 入口は開始パネルの主操作と、Fileメニューの恒久住所「ドキュメントを開く…」に置く。ツールバーへは増やさない。
- 既定表示は`title`、相対またはローカライズ済み`updatedAt`、補助情報としての`id`、主操作「開く」。本文の抜粋、カード数、レビュー状態、サムネイルは出さない。
- 既定順は更新日時の新しい順。タイトルとIDは、取得済みallowlist内でクライアント側絞り込みを行ってよい。
- active文書は静かな「開いています」表示とし、件数バッジや利用頻度順位は付けない。
- localStorageの「最近」は表示順の補助キャッシュに限る。サーバー一覧取得または認可確認に失敗した場合、キャッシュだけで文書候補を表示・開かせない。エラー時はfail-closedの説明と再試行を示す。
- タイトル変更は文書を開いた編集文脈で行う。一覧のインライン変更は、タイトル専用の競合安全な契約が定義されるまで描かない。
- 一覧には削除、アーカイブ、所有者移管、複製、bulk selectionを置かない。

想定状態:

| 状態 | 表示と挙動 |
| --- | --- |
| Loading | 行の形を保つ静かなskeleton。前回キャッシュの実データは表示しない |
| Empty | 「アクセスできるドキュメントはありません」＋「新規作成」「ファイルから読み込む」。権限不足と空状態を混同しない |
| Ready | タイトル中心のlist/table。キーボードで行と「開く」に到達できる |
| ACL解決不能 / 403 | 一覧を空として偽装せず、確認できないため表示しない旨と再試行。キャッシュfallbackなし |
| Network error | 認可済み一覧を確認できない旨、再試行、ファイルから読み込む導線。キャッシュfallbackなし |
| Read-only | 開くことはできる。新規作成やタイトル変更は表示しないかdisabled理由を明示する |

### 3.2 文書内の表示・道具設定

中央の「設定ハブ」へ移さず、既存の使用文脈を維持する。

#### View/Perspective

- View controls内の「表示プリセット」に置く。
- 見出し近傍に「表示設定ファイルを書き出すときに含まれます」と表示する。サーバーへ自動同期されるようには見せない。
- 既定プリセットは鍵アイコン等の非色チャネルで固定を表し、適用のみ可能とする。
- カスタムプリセットは適用、名前変更、削除を提供する。削除前に対象名を示し、削除後は選択を安全な既定値へ戻す。
- SafeModeをOFFにする値をプリセットが含みうる設計にはしない。レビュー用既定プリセットはSafeMode ONを維持する。

#### QueryPreset

- Patch workspaceのQueryPreset節に置く。
- 見出しと保存ボタンの近傍に、文字で**「この端末のみ」**、補足で「ブラウザのデータを消すと失われます」を示す。色だけで保存範囲を表さない。
- 保存後の項目は、名称、scope/depth/filterの短い要約、実行、その他メニュー（名前変更・削除）で構成する。
- 端末間同期、共有、バックアップ、exportを示すクラウド形状や文言を置かない。
- 保存失敗時は実行条件そのものを失わず、保存だけ失敗したことを明確にする。

### 3.3 Admin管理面

Adminは通常のWorkspaceとは別サーフェスとする。現行のアクセス登録は認可されたPlatform operator、future SaaSの文書アクセス設定はactive tenantの`document.policy.manage`を持つTenant Adminにだけ、恒久住所としてメニューまたはアカウント領域から入口を示す。両者を同じ権限・audienceとして扱わず、キャンバス上のスリムツールバーには置かない。

入口の表示制御は認可の代わりにならない。各面のcapabilityをbackendで検証できない構成では該当Admin面を提供せず、APIもfail-closedにする。現行strict provisioning APIの認可主体を固定するまではアクセス登録UIを、trusted SaaS auth/capability adapterとruntime binding resolverが揃うまでは文書アクセス設定UIを実装しない。

推奨する管理面の区分:

1. **アクセス登録**: strict provisioningフォーム。現契約では登録だけを提供し、ユーザー一覧や無効化があるように見せない。
2. **文書アクセス設定（future SaaS）**: active tenantのdocIdに対するvisibilityと非秘密policy binding metadata。管理API scaffoldとtransactional auditは実装済みだが、trusted auth edge・実capability/binding resolver・PDP配線後だけ有効化する。
3. **外部接続**: `EXT-CONN-02`契約実装後のエージェント登録・失効。
4. **システム状態**: providerの有効/無効、SafeMode既定、構成プロファイル等、秘密を含まない診断値だけを読み取り専用で表示する将来候補。値の編集はデプロイ手順へ案内する。
5. **監査**: `DATA-MAINT-04`が解禁されるまでナビゲーションにも空の一覧にも追加しない。

Adminヘッダーには、通常Workspaceと混同しない名称と「この画面は文書本文を表示しません」という境界説明を置く。文書を参照する必要がある行では`docId`だけを使い、タイトルへ解決しない。

#### アクセス登録

- フォーム項目は現行API契約のprovider、external UID、display name、email（任意）の範囲に限定する。
- 送信前に「新しいIDを事前登録する操作」であることを示す。削除・無効化・ロール付与を連想させない。
- 成功後は結果receiptを表示し、同じ値の再送や競合の扱いを説明する。
- 一覧・検索・棚卸しをUIへ追加するには別契約が必要であり、本構想からは除外する。

#### 文書アクセス設定（future SaaS / implementation gated）

- Tenant Adminのactive tenant固定面とし、scope見出しにtenant名とopaque tenant IDを示す。tenant自由入力、他tenant検索、Platform Control Planeからの横断表示は設けない。
- 一覧／検索対象は`docId`、visibility、binding状態（設定済み／未設定／解決不能）、policy version、updatedAtだけとする。文書タイトル、本文、カード、review状態、件数集計は取得も表示もしない。
- 編集フォームは`docId`を固定表示し、visibilityと非秘密の`policyBindingId`、`policyVersion`だけを扱う。`Org/Restricted`ではbinding IDを必須、`Public/Unlisted`では任意とし、生のpolicyRef、policy URL、token、secretを入力する欄を作らない。
- metadata未登録は`Restricted / binding未設定`として表示し、Public既定やread-only fallbackにしない。binding resolver不達は「権限設定を確認できないため利用不可」とし、文書0件のEmptyと区別する。
- 変更は即時反映に見せず、差分確認、保存中の二重実行防止、成功receipt（policy version）、409競合時の再読込を用意する。bulk edit、CSV import/export、全doc一括公開は提供しない。
- UI表示は`document.policy.manage`を使うがAPIが同じcapabilityとactive tenantを再検証する。`document.write`、Platform operator、文書ownerから管理権限を推測しない。
- `GET /session/context`のrouteとstrict frontend fetch境界は実装済みだが、trusted auth edge、App session bootstrap、active tenant変更、cleanup hookが揃うまで本画面を有効化しない。identity／tenant／capability解決失敗は権限なしのEmptyへ偽装せず、再試行可能な利用不可状態として扱う。

#### エージェント登録（将来）

- 一覧の表示候補は`registrationId`、表示名、`docId`、状態、作成日時、作成主体の固定メタデータ。文書タイトルと本文は表示しない。
- 登録フォームでは対象文書をタイトル検索させず、認可済みの`docId`を明示入力または別の安全な選択契約で指定する。
- tokenは作成直後の完了面で一度だけ表示する。「後から再表示できない」ことを表示前と表示中に伝え、copy操作と閉じる確認を用意する。
- 保存後の一覧ではtokenを伏字にせず、token欄そのものを持たない。
- 失効は対象名・registrationId・docId・影響を確認して実行する。再有効化を描かず、必要なら新規登録する。
- 登録成功は書込権限の付与を意味しないことを説明する。ingestごとのaccess-control判定は別に行われる。

### 3.4 SaaSのtenant contextと管理面分離（ADR採択後）

- Workspaceヘッダーにはactive tenantを静かに示す。membershipが1件ならswitcherにせずlabel、複数ならサーバーが返した選択肢だけをswitcherにする。tenantId自由入力は許可しない。
- tenant切替時に未保存変更があれば保存・破棄・取消を選ばせる。確定後は文書、選択、検索、work mode、import preview、recent、QueryPreset、request cacheを破棄し、新tenantで再取得する。
- 切替確認中やbackend未確認の間、旧tenantの本文と新tenantの管理UIを同時に表示しない。
- **Tenant Admin**はactive tenantのmembership provisioning、document access metadata、agent registrationだけを扱う。本文と文書タイトルは表示しない。
- **Platform Control Plane**はtenant lifecycle、IdP接続状態、非秘密のsystem statusだけを扱い、全tenant文書を横断する一覧を持たない。
- role名やgroup名からfrontendが操作可否を推測しない。backendが返すcapabilityと理由コードで表示し、APIが再検証する。
- tenant mismatch、membership失効、PDP不達は権限なしのEmptyに見せず、「範囲を確認できないため表示しない」状態と再認証/戻る導線を示す。

## 4. 共通UI規則

- 汎用の「マスタ」「CRUD」という語を利用者向けラベルに使わず、目的を表す「ドキュメント」「表示プリセット」「アクセス登録」「外部接続」を使う。
- 各編集面に保存範囲ラベルを置く: `サーバー`、`表示設定ファイルに含む`、`この端末のみ`、`デプロイ設定（読み取り専用）`。SaaSではactive tenantも併記し、アイコンだけに依存しない。
- 画面は現在の能力だけを示す。将来項目をdisabledで並べたロードマップ画面にしない。
- Admin/Auditは本文非表示を視覚だけでなく、fixtureとアクセシビリティ名でも守る。
- amberは保留・違和感の保持系に予約し、管理上の注意やtoken警告に使わない。管理警告はslate/redと文言・アイコンで表す。
- 成功・失敗を色だけで伝えない。送信中の二重実行防止、Escapeの段階閉鎖、triggerへのfocus復帰、dialog内focus trapを維持する。
- 一覧はマウスhoverだけに操作を隠さない。390pxではカード型、768px以上ではlist/tableを許容し、同じ情報順を保つ。
- 件数、利用頻度、準備度、優先順位によるスコアリングを導入しない。
- Tenant Admin / Platform Control Plane / Workspaceを色違いだけで区別しない。名称、見出し、パンくず、accessible nameで現在のscopeを示す。
- support担当の暗黙impersonationや「全tenantを表示」切替を設けない。将来のbreak-glassは別ADRとする。

## 5. 実装スライスとゲート

本書は設計入力であり、次の実装許可を与えない。

1. **Workspace文書入口**: `GET /docs`の`api.md` / `schemas.md`契約、認可、fail-closed、キャッシュ規約を先に固定する。
2. **QueryPreset表示改善**: device-local契約を維持し、「この端末のみ」のi18n・a11y・回帰テストを伴う独立スライスにする。
3. **アクセス登録UI**: 現行strict provisioning APIの認可主体とエラー契約を固定・照合してから起票する。UIの非表示だけを認可にしない。ユーザー一覧は含めない。
4. **エージェント登録UI**: `EXT-CONN-02`でテーブル/API/失効/監査契約を固定してから実装する。
5. **Audit UI**: `DATA-MAINT-04`の判断とallowlist契約なしに実装しない。
6. **SaaS tenant UI**: `ADR-0059`のImplementation gateに従い、TenantContext、membership、tenant従属DB列、DB側tenant guard、capability API、deny-only SaaS profile、storage namespace、migration、越境テストが揃うまで有効化しない。
7. **文書アクセス設定UI**: `document.policy.manage`のAPI再認可、metadata管理API、transactional audit、strict external HTTP capability/binding resolverとcapability lifecycle配線は実装済み。trusted SaaS auth edge、binding/capability service・PDP実接続、PostgreSQL RLS実地検証、実PDPを含むtenant A/B negative matrixが揃うまで実画面へ追加しない。

複雑性予算: 初期表示への純増=なし（開始パネル/既存ダイアログ/既存設定節の置換・包含、Adminは別面） / 保留操作の距離=不変 / 取り消し導線=プリセット削除は既定復帰、登録・失効は確認と新規再登録（契約後）

## 6. 検証観点

- Standard userにはAdmin入口が見えず、Platform operatorでもWorkspaceの本文がAdminへ漏れない。
- Workspace一覧レスポンスとDOMに`payload_json`、card text、narrative、review pack、diffが存在しない。
- ACL解決失敗時にlocalStorageの履歴だけで一覧・open候補を復元しない。
- View/PerspectiveとQueryPresetの保存範囲が、ja/enの両方で視覚・スクリーンリーダーから判別できる。
- tokenは作成直後以外の画面・DOM・ログ・再読み込み後に存在しない。
- 390 / 768 / 1440pxで主要操作にキーボード到達でき、dialogを閉じると起点へfocusが戻る。
- provider=`none`、SafeMode既定ON、read-onlyの各状態で、管理機能がコア作業の前提にならない。
- 同じdocIdを持つtenant A/Bで、list、open、write、export、MCP、webhook、agent registration、recent、QueryPresetが越境しない。
- tenant切替後のDOM、memory、object URL、query cacheに旧tenantのタイトル・本文・選択状態が残らない。
- Platform Control PlaneとTenant Adminのどちらからも、capabilityなしにWorkspace本文を読めない。

## Traceability

- `01_Plans/issues/issue-DATA-MODEL-OPS-02-management-plane-data-boundary.md`（D1〜D4）
- `02_Architecture/data_model_operations_overview.md` §4、§5.2
- `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`
- `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`
- `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
- `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- `02_Architecture/design/ui_design_handoff.md`
- `01_Plans/research-2026-07-16-saas-tenant-authorization-boundary.md`
- `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`（Accepted）
- `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- `02_Architecture/enterprise_architecture.md`（SaaS multi-tenantは現行非目標）
- `THREAT_MODEL.md`
