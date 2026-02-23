# future_backlog

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

本セクションは、ルート `ROADMAP.md` の各項目を、既存バックログ体系（`future_backlog.md`）へ統合したものである。  
方針は `ROADMAP.md` を正とし、ここでは **実装アクション / DoD / 状態** を管理する。

状態定義:
- Planned: 未着手
- In Progress: 着手中
- Done: 完了

### Next 1–2 Releases（統合）

| ID | テーマ | 優先度 | 状態 | 具体アクション | DoD（完了条件） | 参照 |
|---|---|---|---|---|---|---|
| FB-RM-UX-01 | 視座プリセット | P0 | Planned | Explore / Review / Summary を view mode として定義し、保存・復元可能にする | 同一Document再読込時に mode が再現される | `RQ-V-01` 系 |
| FB-RM-UX-02 | 島の折りたたみ | P0 | Planned | 階層Islandの collapse/expand と hit-test 制御を実装 | collapse時に配下要素が描画・選択対象から外れる | `FB-P2A-02` |
| FB-RM-UX-03 | Polygon islands | P1 | Planned | polygon shape の保存・再読込・互換読込を統合実装 | 欠損shapeで `rect` フォールバックしつつ編集継続できる | `FB-P2C-01..03` |
| FB-RM-UX-04 | SafeMode UI明示 | P1 | Planned | SafeMode状態バッジ・解除不可モード表記・export警告を統一 | 閲覧者が現在モードを1クリック以内で確認できる | 新規Issue化 |
| FB-RM-RS-01 | Trace Analytics | P1 | Planned | 根拠リンク本数・孤立ノード・出典密度の集計を追加 | deterministicに同一入力で同一統計値を返す | 新規Issue化 |
| FB-RM-RS-02 | 構造メトリクス | P1 | Planned | 健全性指標（例: 連結性/偏り）を diagnostics へ追加 | 指標定義と計算式が文書化されテストで固定される | 新規Issue化 |
| FB-RM-RS-03 | Diagnostics安定化 | P1 | Planned | diagnostics出力schemaを固定し、後方互換バージョンを付与 | 旧バージョン読込時に互換変換で失敗しない | 新規Issue化 |
| FB-RM-SEC-01 | ZIP hardening | P0 | Planned | import時の path traversal / zip bomb / 拡張子偽装対策を追加 | 悪性fixtureで拒否・通常fixtureで成功する | 新規Issue化 |
| FB-RM-SEC-02 | Worker安定化 | P1 | Planned | 長時間処理を worker/off-main-thread へ寄せる | UIスレッドblockの再現ケースが解消される | 新規Issue化 |
| FB-RM-SEC-03 | CI回帰防止 | P0 | Planned | import/serialization/shape互換の回帰テストをCI必須化 | main branch で required check 化される | 新規Issue化 |

### Mid-term Vision（統合）

| ID | テーマ | 優先度 | 状態 | 具体アクション | DoD（完了条件） | 参照 |
|---|---|---|---|---|---|---|
| FB-RM-MID-01 | 類似度検出 | P1 | Planned | 非AI heuristic による候補生成をバッチ化 | 同一入力で候補順序が安定する | `FB-P2B-01` |
| FB-RM-MID-02 | 統合候補提示 | P1 | Planned | 採用/部分採用/却下/後で を記録できるUI | 自動確定なしで人間承認履歴が残る | `FB-P2B-02` |
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
