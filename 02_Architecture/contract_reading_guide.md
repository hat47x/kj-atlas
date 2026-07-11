# Contract Reading Guide

この文書は、`02_Architecture` の設計文書を読むときに、どの記述を現在の正本として扱い、どの記述を履歴・監査ログとして扱うかを示す案内です。

`api.md` と `schemas.md` には、現行契約、将来拡張、Contract Freeze、Stream 実行ログが同じファイル内に残っています。これは履歴を失わない利点がある一方、初見の利用者や開発者には「どこを読めばよいか」が分かりにくくなります。

---

## 1. 基本ルール

- 現在の設計判断は、各文書の本文中で「正本」「固定」「契約」「Validation rules」として明示された箇所を優先します。
- `Stream`、`rerun`、日付付き `freeze note`、`handoff` は、原則として履歴・監査ログです。現在の契約を上書きするためには使いません。
- 環境変数と実行時パラメータは、常に [runtime_parameter_registry.md](runtime_parameter_registry.md) を正本にします。
- 価値判断との対応は [value_traceability.md](value_traceability.md) を参照します。
- 履歴ログを削除する場合や契約本文から分離する場合は、内部 issue または ADR で作業範囲を固定します。

---

## 2. 現在の参照順

| 知りたいこと | 先に読む文書 | 補足で読む文書 |
|---|---|---|
| プロジェクト価値と設計の対応 | `value_traceability.md` | `00_Prompt/domain.md`, `ADR-0001` |
| 全体構成と責務境界 | `architecture.md` | `deployment.md`, `enterprise_architecture.md` |
| API の入出力契約 | `api.md` | `schemas.md` |
| 永続データと view/pack metadata | `schemas.md` | `api.md` |
| 環境変数と実行プロファイル | `runtime_parameter_registry.md` | `deployment.md`, `enterprise_architecture.md` |
| 企業・行政運用 | `enterprise_architecture.md` | `strict_mode_exception_approval_flow.md`, `runtime_parameter_registry.md` |
| LLM 実行制約 | `llm_runtime_constraints.md` | `llm_provider_spec.md`, `llm_escalation_policy.md` |

---

## 3. `api.md` の読み分け

`api.md` は、次の順で読むと現在の契約を追いやすくなります。

1. MVPの基本API: `1. 基本方針` と `2. エンドポイント`
2. CE系の監査・Context契約: `2.7` 以降の CE1 / CE4 関連節
3. 公開・アクセス制御: `7. Publishing metadata` と `8. AccessControlAdapter API契約`
4. 認証・事前プロビジョニング: `9. AUTH-SCHEMA-01 API契約`

`Stream ... freeze ...` と日付付きの節は、契約形成時の履歴です。新しい実装要件として読むのではなく、現在の契約値を変更しないための監査証跡として扱います。

---

## 4. `schemas.md` の読み分け

`schemas.md` は、次の順で読むと現在のデータ契約を追いやすくなります。

1. MVPスキーマの対象範囲: `1. スコープ`
2. CE0/CE1/CE2/CE4 の固定I/F: `1.1` と `1.2`
3. Document / View / Pack / Publishing metadata: 本文中の型定義と `8. Publishing / Access metadata`
4. Identity schema: `10. AUTH-SCHEMA-01`
5. Decision Log / HIL-RS error envelope: 該当する契約節

`Stream ...`、`Contract Freeze Addendum`、日付付き `freeze note` は、既存契約をどう凍結したかの履歴です。新しい正本を追加する場所ではありません。

---

## 5. 変更時の扱い

設計や実装を変更する場合は、次の順に確認します。

1. 上流価値に影響するかを `00_Prompt/domain.md` と `value_traceability.md` で確認する。
2. 契約値を変更する場合は、`api.md` または `schemas.md` の現在の契約節を更新する。
3. 環境変数を変更する場合は、先に `runtime_parameter_registry.md` を更新する。
4. 履歴ログは、必要な場合だけ追記する。履歴ログだけを更新して現在の契約を変更した扱いにしない。
5. 大きな分離や再編が必要な場合は、内部 issue または ADR を起票してから進める。

---

## 6. 将来の分離方針

`DOC-ARCH-02` で、次の物理分離を進行中です。現行のConflictと移動batchは [現行契約統合inventory](contract_consolidation_inventory.md) を参照してください。

- 現行契約: API、schema、runtime parameter の正本文書に残す。
- 履歴・freeze note: [`02_Architecture/history/`](history/README.md) へ移す。
- Stream実行ログ: issue memo または dashboard 側へ集約する。

この分離は、参照リンクと契約IDに影響するため、`DOC-ARCH-02` のbatch単位で扱います。Conflictが未解決の型は推測で統合せず、専用のcontract issueへ分離します。
