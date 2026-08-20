# リサーチ: マスタデータ管理UIに先立つ「あるべきデータ設計」の見直し

- Date: 2026-07-12
- Author: Claude Code（maintainer 委任による調査）
- Status: 調査文書（ADRではない）
- 位置づけ: maintainer 提示「マスタデータ管理用のUI/UX設計も必要に思うが、そもそものあるべきデータ設計から一度見直したほうがよいかもしれない」を受け、現状データ設計の全量棚卸しと、UI設計要求（Claude Design）に先立って固定すべき設計判断を特定する。

## 0. 結論（先出し）

**maintainer の直感は正しい。ただし見直すべきは文書スナップショット正本ではなく、その周辺に暗黙のまま散在している「管理面（マスタデータ）レイヤー」である。** 現状、文書一覧はブラウザ localStorage、プリセットはデバイスローカル、ユーザーは登録APIのみ、そして ADR-0054 が要求する新エンティティ（エージェント登録）は未設計。この層の設計判断（後述 D1〜D4）を固定してから管理UIの設計要求を出すべきで、順序を逆にすると「localStorage の見た目を整える」UIができてしまう。

## 1. 現状の全量棚卸し（3層整理）

既存の正本 `02_Architecture/data_model_operations_overview.html`（ER図・CRUD表・サポートレベル L1〜L3）を基礎に、「マスタデータ管理」の観点で再整理した。

### 層1: 業務データ本体 — 見直し不要（意図的設計）

`documents.payload_json` への **DocumentV2 スナップショット保存**（Card/Edge/Island等は個別行にしない）は ADR-0033 で固定された意図的な境界であり、可逆性・ラウンドトリップ非損失・スキーマ進化の柔軟性という根幹価値に直結している。これを正規化DBへ見直すことは ADR-0033 の再起票かつ大規模マイグレーションであり、**本検討の対象外とすべき**（見直しの利益が現時点で示されていない）。

### 層2: 管理面データ（＝「マスタデータ」の実像）— ここが暗黙・分散

| # | データ | 現状の正本 | 現状の管理手段 | 問題 |
|---|---|---|---|---|
| M1 | **文書インデックス**（id・タイトル・更新日時の一覧） | **存在しない**。DB には行があるが一覧APIなし | 「最近のドキュメント」= ブラウザ **localStorage**（`storage/recent.ts`）。UI表示は id のみ（タイトル未使用） | 別ブラウザ/別端末から自分の文書が見えない。タイトルがあるのに一覧に出ない。削除・リネーム・複製の導線ゼロ |
| M2 | **ユーザー / アイデンティティ** | `users` / `user_identities` テーブル | `POST /admin/provision/users`（登録のみ）。一覧・無効化・棚卸しは「読み取り専用のDB直接確認」（DATA-MAINT-01） | ライフサイクル管理UIなし（意図的保留: 無効化・削除・SCIM は ADR 必須と既定義） |
| M3 | **プリセット**（patch workspace 検索条件・perspective） | ブラウザ **localStorage** | 各パネル内で保存/実行 | デバイスローカル。共有・バックアップ・端末間移動の設計なし。「保存済み」の期待と実態（端末限り）が乖離しうる |
| M4 | **語彙**（claimType / edge種別 / 違和感5タグ / holdState） | コード内固定 enum | 変更＝コード変更 | **問題ではない**。KJ語彙は ADR-0048 で固定した設計判断。ユーザー編集可能なマスタにしないことが反スコアリング・語彙分離の防波堤 |
| M5 | **エージェント登録・認証情報**（ADR-0054 段階2の受信認証: どのエージェントが POST してよいか・トークン） | **未設計** | — | EXT-CONN-02（webhook ingest）の実装前提。由来表示（P32 の「⌂ agent名」チップ）の正本もここになる |
| M6 | **constraint 輸出セット**（段階3） | 未設計（schemas.md 先行固定を EXT-CONN-03 で予定） | — | 設計順序は既に issue 化済み |
| M7 | **プロバイダ設定**（LLM provider・エンドポイント） | 環境変数（`KJ_ATLAS_*`） | デプロイ設定 | **問題ではない**。実行環境の契約として意図的（ADR-0050）。DBマスタ化はかえって監査を弱める |

### 層3: 派生・監査データ — 境界管理中（変更不要）

`merge_decision_logs`（追記のみ）、export/context audit events（アプリ内閲覧UIなし・DATA-MAINT-04 が本文なしメタデータ閲覧を Draft 管理・ADR-0035 Accepted 待ち）。既存の境界設計が機能しており、本検討で動かさない。

## 2. 判定: 固定すべき設計判断は4つ

管理UIの設計要求に先立ち、次の判断（D1〜D4）を固定する必要がある。**いずれも「UIの見た目」ではなくデータの正本と権限の問題**であり、Claude Design ではなく本リポジトリの ADR/issue で決める種類のもの。

- **D1: 文書インデックスのサーバー正本化**（M1）
  - 一覧API（id・タイトル・更新日時。**本文を含めない**メタデータ限定）を新設するか。localStorage「最近」はキャッシュに格下げ。
  - 削除・アーカイブ・リネーム・複製をどこまで標準機能にするか — 削除/アーカイブ/所有者移管は **ADR-0035（Proposed）の受理が前提**（高権限ライフサイクル境界）。リネーム（タイトル編集）と複製は既存 PUT の範囲で低リスク。
  - 論点: 一覧APIは「本文を含まない」点で DATA-MAINT-04 の監査メタデータ閲覧と同じ設計原則を共有できる。
- **D2: プリセットの置き場**（M3）
  - 案(a) デバイスローカル維持＋「この端末のみ」明示、案(b) DocumentV2 埋め込み（文書と一緒に移動）、案(c) サーバー別テーブル（ユーザー従属）。
  - view.json（表示設定の輸出）との整合: プリセットが「表示の再現」に属するなら view 系、「作業の道具」なら独立。
- **D3: エージェント登録の正本と認可モデル**（M5）
  - EXT-CONN-02 の前提。最小案: `agent_registrations`（id・表示名・トークンハッシュ・作成者・有効/無効・作成日時）＋ ingest ログとの相関。
  - スコープ判断: 登録・失効を admin API に置くか（M2 と同じ strict provisioning 型）、文書所有者に委ねるか。
- **D4: 管理面データの表示原則**
  - 管理UIは一般利用者の操作導線から分離する（既定: `02_Architecture/data_model_operations_overview.html` §6 の方針を踏襲）。
  - 本文非表示原則: 管理面（一覧・棚卸し・監査）では `payload_json` 本文を出さない（DATA-MAINT-01/04 と同一原則）。

## 3. 提言（次アクション・maintainer 判断待ち）

1. **DATA-MODEL-OPS-02 を Draft 起票**（本文書と同時）: D1〜D4 を受入条件の形で固定する「管理面データ境界」issue。DecisionStatus は Pending（D1 の削除/アーカイブ部分が ADR-0035 の受理に依存。ただし一覧API・リネーム・複製・D2・D3 は ADR-0035 と独立に判断可能）。
2. **順序**: D1〜D4 の判断固定 → schemas.md / `02_Architecture/data_model_operations_overview.html` の同期 → **その後に** Claude Design へ管理UI（マスタデータ管理面）の設計要求（Round 8 候補）。UI要求時に渡す入力は「確定した正本・権限・本文非表示原則」であり、これが無いまま要求すると localStorage 実態を追認する画面になる。
3. **ADR 要否**: D1 のうち削除・アーカイブ・所有者移管は ADR-0035 の領分（既存）。一覧API・タイトル編集・複製・プリセット置き場・エージェント登録は、`02_Architecture/data_model_operations_overview.html` §7 の更新ルール（新しい標準APIはER/CRUD表の同時更新）に従えば **新規ADRなしで issue 側で決められる**見込み。ただし D3 は EXT-CONN-02 の認可設計と一体なので、ADR-0054 の Accepted 判断に含めて確認するのが安全。

## Traceability

- Related: `02_Architecture/data_model_operations_overview.html`（現状の正本。§4 CRUD表・§5 ステークホルダー不足・§6 起票先）
- Related: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`（層1を動かさない根拠）
- Related: `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`（D1 の削除/アーカイブ/移管ゲート）
- Related: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`（D3 の背景）
- Related: `01_Plans/issues/issue-DATA-MODEL-OPS-02-management-plane-data-boundary.md`（本提言の起票先）
- Related: `03_Implement/frontend/src/storage/recent.ts`, `03_Implement/frontend/src/ui/workspace/PatchWorkspacePanel.tsx`（M1/M3 の現状実装）
