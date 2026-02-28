# ADR-0007-future-backlog: 将来バックログ管理

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Migrated-from: `01_Plans/phaseX_future_backlog.md`

## Context

`phaseX_future_backlog.md` で管理していた計画・要件・受入条件を、ADR運用へ移管する。

## Decision

以下を本ADRの正本として採用する。

# phaseX_future_backlog

本ドキュメントは、Phase 1以降の未着手項目を優先度付きで管理する。
`phase2_qualitative_integration.md` の要求ID（RQ）・受け入れ基準（AC）にトレース可能であることを必須とする。

優先度定義:
- P0: 次フェーズで必須
- P1: 次フェーズで高優先
- P2: 中期導入
- P3: 長期検討

---

## Backlog Items（Phase 2）

| ID | タイトル | 優先度 | フェーズ | 対応RQ | 対応AC | DoD（完了条件） |
|---|---|---|---|---|---|---|
| FB-P2A-01 | Island階層モデル導入 | P0 | 2A | RQ-2A-01 | AC-2A-1 | `parentIslandId` の作成/変更/保存/再読込で階層が保持される。 |
| FB-P2A-02 | Collapse/Expand操作 | P0 | 2A | RQ-2A-02 | AC-2A-2, AC-2A-3 | collapseで子要素が描画/ヒットテスト対象外になり、expandで復帰する。 |
| FB-P2A-03 | 代表タイトル表示 | P1 | 2A | RQ-2A-03 | AC-2A-4 | collapsed 親Islandで representative title が表示・編集できる。 |
| FB-P2A-04 | Overview/Detail表示モード | P1 | 2A | RQ-V-01, RQ-V-02 | AC-V-1, AC-V-3, AC-V-4 | UIトグル/ショートカットで同一遷移し、永続データ差分が出ない。 |
| FB-P2B-01 | Similar-card候補提示 | P0 | 2B | RQ-2B-01 | AC-2B-1 | candidate group 一覧と対象Cardを確認できる。 |
| FB-P2B-02 | Manual assisted mergeフロー | P0 | 2B | RQ-2B-02 | AC-2B-2, AC-2B-5 | `採用/部分採用/却下/後で` が保存でき、自動確定しない。 |
| FB-P2B-03 | Representative card決定 | P1 | 2B | RQ-2B-03 | AC-2B-3 | merge 採用時に representative card が必ず1件確定する。 |
| FB-P2B-04 | Merge由来トレーサビリティ | P1 | 2B | RQ-2B-04 | AC-2B-4 | representative card から origin link を辿れる。 |
| FB-P2C-01 | Polygon auto-fit | P0 | 2C | RQ-2C-02 | AC-2C-2, AC-2C-3 | 同一入力で同一polygonを生成し、padding制約を満たす。 |
| FB-P2C-02 | Shape切替UI | P1 | 2C | RQ-2C-01 | AC-2C-1 | `rect/rounded_rect/polygon` の表示・保存・再読込が成立する。 |
| FB-P2C-03 | Polygon検証と互換読み込み | P1 | 2C | RQ-2C-03 | AC-2C-4, AC-2C-5 | 自己交差保存を拒否し、shape欠損Documentを `rect` 解釈で表示する。 |
| FB-P2C-04 | Polygon手動編集（頂点移動） | P2 | 2C+ | （拡張） | （将来AC） | 最低3点制約を維持して頂点移動できる（将来導入）。 |

---

## フェーズゲート

- Gate-2A: FB-P2A-01〜04 完了で 2A 終了。
- Gate-2B: FB-P2B-01〜04 完了で 2B 終了。
- Gate-2C: FB-P2C-01〜03 完了で 2C 終了（FB-P2C-04 は次段）。

---

## 依存メモ

- 2B は 2A と並行可能だが、overview/detail 導線共通化のため 2A 先行を推奨。
- 2C は `02_Architecture/island_shapes.md` の shape 制約を実装前提とする。
- 全項目で review flags と反スコアリング原則を維持する。



---

## Roadmap統合バックログ（公開ROADMAPの実装分解）

本セクションは、ルート `ROADMAP.md` の各項目を、既存バックログ体系（`phaseX_future_backlog.md`）へ統合したものである。  
方針は `ROADMAP.md` を正とし、ここでは **実装アクション / DoD / 状態** を管理する。

状態定義:
- Planned: 未着手
- In Progress: 着手中
- Done: 完了

### Next 1–2 Releases（統合）

| ID | テーマ | 優先度 | 状態 | 具体アクション | DoD（完了条件） | 参照 |
|---|---|---|---|---|---|---|
| FB-RM-UX-01 | 視座プリセット | P0 | Done (2026-02-26) | Explore / Review / Summary を view mode として定義し、ヘッダーのモードトグルと `⌘/Ctrl+1..3` ショートカットで共通導線化。document単位のlocalStorage保存（`kj-atlas/view-mode-by-doc`）を導入し、再読込時に既存modeを復元する。`view_mode.ts` / `view_mode.test.ts` / `storage/view_mode.test.ts` を追加し、mode↔preset対応・保存値パースを回帰固定。 | 同一Document再読込時に mode が再現され、UIトグルとショートカットの双方で同一presetへ到達できる | `RQ-V-01` 系 |
| FB-RM-UX-02 | 島の折りたたみ | P0 | Done (2026-02-26) | 階層Islandの collapse/expand と hit-test 制御を実装。collapse状態を island.collapsed と viewState の双方で保持し、descendant連鎖を共通ヘルパーへ統合。Collapse/Expand all を永続値へ同期。 | collapse時に配下要素が描画・選択対象から外れ、expandと再読込で復帰する | `FB-P2A-02` |
| FB-RM-UX-03 | Polygon islands | P1 | Done (2026-02-26) | polygon shape の保存・再読込・互換読込を統合実装。`validateAndUpgradeImportedDocument` で自己交差polygonを自動破棄して card-bounds フォールバックへ退避し、`validateDocumentV2Strict` では自己交差を検証エラーとして拒否。polygon自己交差判定ユーティリティと回帰テストを追加。 | 欠損shapeで `rect` フォールバックしつつ編集継続でき、自己交差polygonが保存・厳格検証で受理されない | `FB-P2C-01..03` |
| FB-RM-UX-04 | SafeMode UI明示 | P1 | Done (2026-02-26) | ヘッダー常設のSafeMode状態バッジ（ON/OFF）を追加し、クリックでShareパネルを開いて詳細を確認できる導線へ統一。Share & Reproduce内でSafeMode説明・export警告・「Share/Review Packでは赤字化が解除不可」の文言を共通ヘルパーで集約。`safe_mode_status.ts` / `safe_mode_status.test.ts` / `SharePanel.test.tsx` を追加し、文言と状態分岐を回帰固定。 | 閲覧者がヘッダーからSafeMode状態を即時確認でき、Share/export警告と解除不可モード表記が矛盾なく統一される | `03_Implement/frontend/src/ui/safe_mode_status.ts` |
| FB-RM-RS-01 | Trace Analytics | P1 | Done (2026-02-27) | Trace Analytics に根拠リンク本数・孤立ノード・出典密度を追加し、UI/Export/Worker golden で同一集計値を参照できるよう統合。Map/Set→配列化時のソート順固定と roundTo4 により決定論を担保。 | 同一入力で同一統計値を返し、追加指標が markdown/export/UI で一貫表示される | `03_Implement/frontend/src/worker/trace_analytics.ts` |
| FB-RM-RS-02 | 構造メトリクス | P1 | Planned (Issue draft: 2026-02-27) | 健全性指標（例: 連結性/偏り）を diagnostics へ追加 | 指標定義と計算式が文書化されテストで固定される | `01_Plans/issues/issue-FB-RM-RS-02-structural-metrics.md` |
| FB-RM-RS-03 | Diagnostics安定化 | P1 | Done (2026-02-26) | diagnostics出力schemaVersionを固定し、pre-release方針として `schemaVersion===1` のみ受理。invalid/unsupported version・malformed/array payload・worker message/result envelope不正（他request無視含む）・progress不正・unknown type・diagnostics.error不正・必須フィールド欠落/型不正を検知してfallbackするテストを整備。`04_Documentation/diagnostics.md` を追加。 | current version以外はfallbackで安全に処理継続できる（unit testで固定） | `03_Implement/frontend/src/worker/diagnostics_protocol.ts` |
| FB-RM-SEC-01 | ZIP hardening | P0 | Done (2026-02-26) | import時の path traversal（相対/絶対/UNC/NUL）・zip bomb（総量/件数/単体サイズ/圧縮率）・許可拡張子制限を強化し、Z001/Z002で拒否。`zip_import.test.ts` と review-pack workflow 統合テストで回帰固定。 | 悪性fixtureで拒否・通常fixtureで成功する | `03_Implement/frontend/src/import/zip_import.ts` |
| FB-RM-SEC-02 | Worker安定化 | P1 | Done (2026-02-28) | Bundle export の zip 生成を `bundle_zip.worker.ts` + `bundle_zip_client.ts` へ移管し、worker unavailable 時は scheduler fallback を維持。`buildBundleZipBlob` に cancellation/progress を接続し、`bundle_export.test.ts` で worker/fallback/cancel を回帰固定。 | 大規模 export でも zip 圧縮で UI 応答が阻害されず、abort 時は cancelled として終了できる | `03_Implement/frontend/src/worker/bundle_zip_client.ts` |
| FB-RM-SEC-03 | CI回帰防止 | P0 | Done (2026-02-26) | import/serialization/shape互換の回帰テスト群を `test:regression-guards` として固定し、CIに専用ジョブ `Frontend regression guards (import/serialization/shape)` を追加。branch protection に required check として設定する手順を運用ドキュメントに明記。 | import/serialization/shape互換の回帰テストがCI専用ジョブで常時実行され、required check設定手順が文書化されている | `.github/workflows/ci.yml` |

### Mid-term Vision（統合）

| ID | テーマ | 優先度 | 状態 | 具体アクション | DoD（完了条件） | 参照 |
|---|---|---|---|---|---|---|
| FB-RM-MID-01 | 類似度検出 | P1 | Done (2026-02-28) | `collectMergeCandidates` を導入し、normalized-text / token-signature の2段 heuristic で merge candidate をローカル生成。source/merged済み card を除外し、group/card順序を安定ソートで固定。UI導線は API 呼び出しから deterministic local batch へ置換。 | 同一入力で candidate group と group内 card 順が一致し、候補一覧で対象Cardを確認できる（AC-2B-1整合） | `FB-P2B-01` |
| FB-RM-MID-02 | 統合候補提示 | P1 | Done (2026-02-28) | Merge Suggestions を4アクション（accept/partial/reject/defer）へ更新し、decision log (`mergeSuggestionDecisions`) を document に保存。候補再収集時に latest decision と編集済みテキストを復元し、自動 canonical merge を無効化。Frontend strict validation / backend roundtrip を同期。 | 自動確定なしで人間承認履歴が残り、保存再読込後も decision 状態を再現できる | `FB-P2B-02` |
| FB-RM-MID-03 | 統合ログ監査 | P2 | Planned | merge decision log を監査用にエクスポート可能化 | representative と source の追跡が可能 | `FB-P2B-03..04` |
| FB-RM-MID-04 | 階層質的統合 | P1 | Planned | sub-island + 表札（見出し）カード + レベル切替UIを段階導入 | level切替で表示粒度のみ変化しデータ欠落しない | `FB-P2A-*` |
| FB-RM-MID-05 | 構造レベル別export | P2 | Planned | overview/detail の2階層出力をサポート | 同一Documentから複数粒度でexport可能 | 新規Issue化 |
| FB-RM-MID-06 | 共通LLM adapter | P1 | Planned | provider abstraction（none/local/large-scale）を定義し、同一枠組みで切替可能にする | decision確定APIを提供せず、provider切替でUI/監査仕様が一貫する | `P-07`, `AI-07-*` |

### Localization Strategy（統合）

| ID | 優先度 | 状態 | 具体アクション | DoD（完了条件） |
|---|---|---|---|---|
| FB-RM-I18N-01 | P1 | Planned | UI文言をkey化し、ハードコード文言を削減 | 主要画面の表示文言が辞書経由になる |
| FB-RM-I18N-02 | P1 | Planned | 翻訳JSONフォーマットとfallback順序を固定 | 欠損キー時に既定言語へフォールバック |
| FB-RM-I18N-03 | P2 | Planned | 英語UIを機能等価で提供 | 日本語/英語で機能差がない |
| FB-RM-I18N-04 | P2 | Planned | view単位言語設定を保存 | view切替後も表示言語が保持される |
| FB-RM-I18N-05 | P2 | Planned | `document.json` 言語非依存を検証する互換テストを追加 | 言語変更前後でdocument hashが不変 |
| FB-RM-I18N-06 | P2 | Planned | SafeMode下の言語変換時データ漏洩チェックを追加 | 外部送信なし・ログマスキングを満たす |

### Publishing / Access Control（統合）

| ID | 優先度 | 状態 | 具体アクション | DoD（完了条件） |
|---|---|---|---|---|
| FB-RM-PUB-01 | P1 | Planned | Public / Unlisted / Org / Restricted を pack/view metadataへ追加 | schema検証と既存データ互換を両立 |
| FB-RM-PUB-02 | P1 | Planned | `isReadOnly` で編集系UIを一括制御 | 直編集操作が抑止される |
| FB-RM-PUB-03 | P1 | Planned | index/assets/packs の最小公開アーティファクトを出力 | 静的ホスティングで閲覧成立 |
| FB-RM-PUB-04 | P2 | Planned | roles/groups/policyRef 抽象I/Fを定義し実装を外部委譲 | アプリ本体にRBACロジックを持ち込まない |
| FB-RM-PUB-05 | P2 | Planned | 閲覧/エクスポートイベントを外部監査基盤へ送信可能化 | 監査連携のON/OFFを設定で切替できる |

### 完了済み（文書統合）

| ID | 状態 | 内容 | 完了条件 |
|---|---|---|---|
| FB-RM-DOC-01 | Done | ルート文書の位置づけ（公開コミュニケーション）と更新タイミングの明確化 | `README.md` に文書役割マトリクスが存在し、更新運用ルールが定義済み |
| FB-RM-DOC-02 | Done | ROADMAPのLLM方針を共通アダプタ（local/large-scale）へ更新 | `ROADMAP.md` と `01_Plans` 側の対応項目が整合している |


## Consequences

- 旧文書 `phaseX_future_backlog.md` は廃止し、本ADRへ参照を統一する。
- 既存リンクは `01_Plans/adr/ADR-0007-future-backlog.md` へ更新する。

## Traceability

- Source: `01_Plans/phaseX_future_backlog.md`
- Supersedes: `01_Plans/phaseX_future_backlog.md`


#### FB-RM-UX-01 実装TODO（完了ログ）

- [x] Explore / Review / Summary を `ViewMode` として型定義し、default preset との対応を固定。
- [x] ヘッダーに view mode トグル（3分割）を追加。
- [x] `⌘/Ctrl+1..3` で mode 切替ショートカットを実装。
- [x] `kj-atlas/view-mode-by-doc` に document単位で mode を保存。
- [x] document読込時に保存済み mode を復元。
- [x] `view_mode.test.ts` / `storage/view_mode.test.ts` で mode変換・保存値検証を追加。



#### FB-RM-RS-01 実装TODO（完了ログ）

- [x] `TraceAnalytics` 型へ `evidenceLinkCount` / `isolatedNodeCount` / `isolatedNodeIds` / `sourceDensity` を追加し、互換フィールドを維持した。
- [x] `computeTraceAnalytics` で根拠リンク本数・孤立ノード・出典密度を決定論ソート（ID昇順）で算出するようにした。
- [x] `buildTraceAnalyticsMd` に追加指標を出力し、孤立ノードがある場合のみ `## Isolated nodes` セクションを生成するようにした。
- [x] `trace_analytics.test.ts` で追加指標・孤立ノード順序・決定論・markdown出力の回帰テストを先行追加して固定した。
- [x] `worker_golden.test.ts` と fixture `trace_analytics_c1.md` を同期し、worker経路でも追加指標の出力を固定した。
- [x] SidePanel の Trace Analytics 表示へ追加指標（Evidence links / Isolated nodes / Source density）を反映した。

#### FB-RM-RS-03 実装TODO（完了ログ）

- [x] Protocol: `diagnosticsData.schemaVersion` を current=1 として固定。
- [x] Validation: unsupported/invalid schema version を検知し fallback。
- [x] Validation: payload/result envelope の malformed/array を検知。
- [x] Validation: progress / unknown type / diagnostics.error 不正を検知。
- [x] Isolation: 他requestIdメッセージは無視。
- [x] Required fields: `recommendations` / report objects / `diagnosticsMd` 欠落を検知。
- [x] Docs: `04_Documentation/diagnostics.md` に schemaVersion/互換/fallback を明記。
- [x] Tests: `diagnostics_protocol.test.ts` / `diagnostics_client.test.ts` を更新して回帰固定。


#### FB-RM-SEC-01 実装TODO（完了ログ）

- [x] Path validation: `../` に加えて absolute path / Windows drive path / UNC path / NUL byte を拒否。
- [x] Zip bomb guard: file count / per-file size / total uncompressed size / compression ratio の上限を導入。
- [x] Extension policy: `.json/.md/.png` 以外を取り込み対象から除外（警告件数に加算）。
- [x] Tests: `src/import/zip_import.test.ts` に悪性ケース（絶対パス・圧縮率・サイズ上限）を追加。
- [x] Integration: `src/diff/review_pack_workflow.integration.test.ts` の悪性ZIP拒否を維持。





#### FB-RM-SEC-02 実装TODO（完了ログ）

- [x] `bundle_zip_protocol.ts` を追加し request/progress/result/cancel/error のメッセージ契約を定義した。
- [x] `bundle_zip.worker.ts` を追加し、zip圧縮を off-main-thread で実行する経路を実装した。
- [x] `bundle_zip_client.ts` を追加し、worker unavailable 時は main-thread scheduler fallback へ退避するようにした。
- [x] `buildBundleZipBlob` を worker client 経由へ置換し、abort signal/progress 連携を実装した。
- [x] `App.tsx` の bundle export で zip progress を表示し、cancelled を失敗扱いしないようにした。
- [x] `bundle_export.test.ts` に worker/fallback/cancel 回帰を追加し、`test:regression-guards` で通過確認した。

#### FB-RM-SEC-03 実装TODO（完了ログ）

- [x] Frontend向けに import/serialization/shape互換の回帰テスト対象を選定。
- [x] `03_Implement/frontend/package.json` に `test:regression-guards` スクリプトを追加。
- [x] `.github/workflows/ci.yml` に専用ジョブ `Frontend regression guards (import/serialization/shape)` を追加。
- [x] CIジョブ名を branch protection の required check に設定可能な安定名に固定。
- [x] `04_Documentation/release.md` に required check 設定手順（GitHub UI）を追記。
- [x] ローカルで `test:regression-guards` を実行し、通過を確認。


#### FB-RM-UX-04 実装TODO（完了ログ）

- [x] ヘッダーに SafeMode 状態バッジ（ON/OFF）を常設し、1クリックで Share パネルへ遷移できるようにした。
- [x] Share & Reproduce 内の SafeMode 説明・export警告・解除不可モード表記を共通ヘルパーで統一した。
- [x] SafeMode ON/OFF の文言分岐を `safe_mode_status.test.ts` で固定した。
- [x] `SharePanel.test.tsx` で SafeMode 表示の回帰テストを追加した。


#### FB-RM-UX-02 実装TODO（完了ログ）

- [x] collapse対象判定を `collapse_visibility.ts` の共通ヘルパーへ集約し、親collapse時のdescendant連鎖を固定した。
- [x] `collapse_visibility.test.ts` を拡張し、階層Islandでの collapsed island ids / hidden card ids を回帰固定した。
- [x] Island単位の collapse/expand 操作時に `island.collapsed` 永続値を更新するよう `App.tsx` を修正した。
- [x] Collapse all / Expand all 操作で UI状態と永続状態が乖離しないよう同期した。
- [x] `npm run test -- src/domain/view/collapse_visibility.test.ts` / `npm run typecheck` / `npm test` の通過を確認した。
- [x] collapse永続更新ロジックを `collapse_state.ts` に分離し、単体/全体collapse更新の純粋関数テストを追加した。


#### FB-RM-UX-03 実装TODO（完了ログ）

- [x] `validateDocumentV2Strict` に polygon 自己交差検証を追加し、保存時バリデーションで拒否するようにした。
- [x] `validateAndUpgradeImportedDocument` に自己交差polygon除外を追加し、互換読込時は card-bounds フォールバックで編集継続可能にした。
- [x] `polygon_self_intersection.ts` を追加して判定ロジックを共通化し、幾何判定を再利用可能にした。
- [x] `validate_doc.test.ts` / `validate.test.ts` / `polygon_self_intersection.test.ts` を追加・更新し、自己交差ケースの回帰を固定した。
- [x] E2E追加有無を確認し、本改修は Domain validation（非UI導線）中心で Playwright シナリオ追加対象外だったため、PRに未追加理由と代替検証（unit + regression-guards）を明記する運用へ修正した（ADR-0018連携）。
- [x] Playwright E2E `e2e/polygon_import_validation.spec.ts` を追加し、自己交差polygonを含む document.json の取込→置換→bundle export で shape が除去されることを実動作で確認した。


#### FB-RM-MID-02 実装TODO（完了ログ）

- [x] `MergeSuggestionsPanel` を accept/partial/reject/defer の4アクションに更新。
- [x] `mergeSuggestionDecisions` を `DocumentV2` に追加し、decision append log を保存可能化。
- [x] decision記録時に自動 canonical merge を実行しないフローへ変更。
- [x] 候補再収集時に latest decision / edited text を復元するよう `App.tsx` を更新。
- [x] Frontend strict validator (`validate_doc.ts`) に decision schema 検証を追加。
- [x] Backend `DocumentV2` モデルと docs roundtrip test を更新し、PUT/GETで decision log 保持を確認。
