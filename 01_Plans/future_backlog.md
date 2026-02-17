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

