# Architecture history

Status: Informative history index

このディレクトリは、現行契約を形成したfreeze note、Stream実行ログ、checkpoint、reaffirmation等を、現在の規範定義から物理分離して保持する場所です。

ここに置かれた文書は、現行の型、endpoint、既定値、error、運用支援レベルを上書きしません。現在の値は [Contract Reading Guide](../contract_reading_guide.md) から責務別の正本へ進んで確認してください。

## 収録条件

各履歴ファイルは、次のメタデータを必須とします。

- `Status: Informative history`
- 元文書と元anchor
- 対象期間
- snapshotまたはsource revision
- 保持理由
- 現行の規範anchorへの逆リンク

上記が揃わない断片や、現行契約と区別できない複製は収録しません。移動計画とConflict一覧は [現行契約統合inventory](../contract_consolidation_inventory.md) を参照してください。

## 収録済み履歴

| 履歴 | 元文書 | 対象期間 | 現行正本 |
|---|---|---|---|
| [Architecture contract-freeze formation history](architecture-contract-freeze-formation-2026-04-to-05.md) | `architecture.md` former §7A.0 snapshot / §7A.2.1 / post-§12 baseline / §13 | 2026-04-27〜2026-05-04 | `architecture.md` responsibility boundary、`schemas.md` types、`api.md` endpoints/errors |
| [Data Model Operations — Stream D formation history](data-model-operations-stream-d-2026-05.md) | `data_model_operations_overview.md` former §1.2/§1.3/§8〜§13 | 2026-05-19〜2026-05-20 | `data_model_operations_overview.md` §1〜§7、`schemas.md` versioning |

## 移動規律

1. 元節と移動先の対応表を先に作る。
2. 履歴ファイルと逆リンクを追加する。
3. contract testと相対リンクを確認する。
4. 元文書を現行契約または短い履歴参照へ縮約する。
5. 情報欠落、契約値変更、リンク切れがあればそのbatchだけ戻す。

履歴の破壊的削除や意味の書換えは行いません。
