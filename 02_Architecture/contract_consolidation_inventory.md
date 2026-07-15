# 現行契約統合inventory

Status: Informative working inventory

対象revision: `1367740d8d03cf53bc0ad1eb09ffc45684ff51e1`

更新日: 2026-07-15

目的: `DOC-ARCH-02` の物理SSOT化に先立ち、現行契約候補、異義定義、合成型欠落、履歴移動候補をanchor単位で固定する。本書は契約値を決める正本ではなく、移動・統合時の情報欠落と暗黙変更を防ぐチェックリストである。

非目標: Contract ID、field、endpoint、error、version、安全境界の追加・変更。Conflict欄の値を実装だけから推測して決めない。

関連Action: `01_Plans/issues/issue-DOC-ARCH-02-current-contract-history-physical-separation.md`

## 1. 責務別の到達先

| 対象 | 統合後の唯一の正本 | 他文書に残してよい内容 |
| --- | --- | --- |
| コンポーネント、信頼境界、責務 | `architecture.md` | 型名・endpoint名への参照 |
| 型、required/optional key、列挙、既定値、version互換 | `schemas.md` | schema anchorへの参照 |
| endpoint、status/error、認証、副作用 | `api.md` | request/response型名とschema anchor |
| 物理保存、CRUD、support level、運用責任 | `data_model_operations_overview.md` | schema型名とAPI endpointへの参照 |
| Contract ID/論点からの入口 | `contract_reading_guide.md` | 契約値を複製しない索引 |
| freeze、Stream、rerun、checkpoint、reaffirmation | `history/` | Informativeメタ、対象期間、元文書、現行正本への逆リンク |

## 2. 現行契約のConflict inventory

`Resolution` が `Conflict` の行は、移動作業中にどちらかへ寄せてはならない。Accepted ADRと上流契約でも一意にならない場合は専用のcontract issueへ分離する。

| Inventory ID | 対象 | 定義A | 定義B | 実装証拠の用途 | Resolution |
| --- | --- | --- | --- | --- | --- |
| CI-CE1-01 | `ContextQueryV1` | `architecture.md` §7A.2.1: `scope:string[]`、depth文字列列挙、SafeMode object、`queryId`/`previewConfirmed`なし | `schemas.md` §1.2: `queryId`、scope列挙、depth数値、`safeModePolicy:"strict"`。後段freezeでは`previewConfirmed`もrequired | model/fixture/contract testは候補比較の証拠。上位契約を置換する根拠にはしない | **Delegated: `CE1-CONTRACT-01`**。本Issueでは値を統合しない |
| CI-CE1-02 | `ContextBundleV1` | `architecture.md` §7A.2.1: `queryRef/cards/islands/...` | `schemas.md` §1.2: `queryCanonicalHash/selected/evidence/...`。`api.md` §2.8はさらにrequired `queryId`を含める | backend response modelとroute testで実装現況を確認する | **Delegated: `CE1-CONTRACT-01`**。v1 key削除/誤記判定を分離 |
| CI-CE1-03 | `schemaVersion` | `api.md` §2.8/後段freezeでrequest/response掲載位置が揺れる | `schemas.md` の型本体・後段freezeでrequired集合の記述が分かれる | fixtureのclosed-world key集合を列挙する | **Delegated: `CE1-CONTRACT-01`**。logical typeとHTTP envelopeを分離して判定 |
| CI-DOC-01 | `Card`合成型 | `schemas.md` §3.2の先頭型は基本fieldのみ | §14 `holdState`、§15 `meta`、§17 `ka`が加算定義 | frontend/backend roundtrip testでoptional field保持を確認する | **Merged 2026-07-15 without semantic change** |
| CI-DOC-02 | `DocumentV2`合成型 | `schemas.md` §3.5の先頭型 | §14 `shelf`、§16 `contradictionSignalDecisions`が加算定義 | import/export/backend保存testでoptional field保持を確認する | **Merged 2026-07-15 without semantic change** |
| CI-DOC-03 | support level | `data_model_operations_overview.md` §4.1は`cards[].meta`、`contradictionSignalDecisions`、`cards[].ka`を掲載 | `holdState`と`shelf`は`cards[]`説明へ包含され、独立行がない | support levelを変えず、検索可能な独立行が必要か確認する | **Clarified 2026-07-15**。`cards[].holdState` / `shelf`をL2.5独立行として追加 |

## 3. 合成型へ統合する採択済みoptional field

次は新規fieldではなく、同じ`version: 2`で既に採択・実装された加算定義である。先頭の合成型へ統合するときもoptional性、未知キー拒否、SafeMode、共有既定を変えない。

| 位置 | field | 現在の詳細anchor | 非後退条件 |
| --- | --- | --- | --- |
| `Card` | `holdState?` | `schemas.md` §14.1 | 省略時`active`相当。保留はAIが自動確定しない |
| `DocumentV2` | `shelf?` | `schemas.md` §14.2 | optional。既存document読込を拒否しない |
| `Card` | `meta?` | `schemas.md` §15.1 | 未知キーfail-closed。共有向け既定除外 |
| `DocumentV2` | `contradictionSignalDecisions?` | `schemas.md` §16.2 | 人間のレビュー決定だけを書き込む |
| `Card` | `ka?` | `schemas.md` §17.1 | SafeMode露出は`card.text`と同一チャネル |

## 4. 履歴移動候補

この表は移動対象候補であり、まだ移動完了を意味しない。各batchは「履歴ファイル追加→双方向リンク→contract/link test→元節縮約」を同一変更で行う。

| Batch | 元文書 | 移動候補anchor | 現行正本として残すもの |
| --- | --- | --- | --- |
| H-A | `architecture.md` | **Moved 2026-07-15** to `history/architecture-contract-freeze-formation-2026-04-to-05.md`: §7A.0 snapshot、§7A.2.1 Interface Freeze、§12後の`Contract Freeze Baseline`、§13 Stream Reflection Note | コンポーネント責務、信頼境界、採択済み契約IDへの索引 |
| H-B | `api.md` | **Moved 2026-07-15** to `history/api-contract-formation-2026-04-to-05.md`: §2.8 Phase/mock plan、§2.10 Stream A log、§2.8.x〜§2.11 sync/freeze、§9.5、末尾Freeze Addendum/handoff | endpoint、status/error、認証、副作用、唯一のrequest/response型参照 |
| H-C | `schemas.md` | §1.0.1 Stream gate、§11.1 snapshot、§1.3以降のfreeze manifest/memo/Stream log/reaffirmation | 合成型、validation、version互換、Contract ID |
| H-D | `data_model_operations_overview.md` | §1.2/1.3 Stream注記、§8〜§13 execution log/checkpoint/record/sync | **Moved 2026-07-15** to `history/data-model-operations-stream-d-2026-05.md`。現行物理モデル、CRUD、support level、運用責任は元文書に維持 |

## 5. 移動時の必須メタ

`history/`へ移す各ファイルは、次を冒頭に持つ。

```text
Status: Informative history
Source document:
Source anchors:
Covered period:
Snapshot / source revision:
Retention reason:
Current normative anchors:
```

履歴本文に`Decision`や`fixed`が残っても、`Status: Informative history`と現行anchorへの逆リンクなしでは公開しない。

## 6. 統合順序と停止条件

1. `ContextQueryV1` / `ContextBundleV1` / `schemaVersion`のConflictを専用差異表とcontract testで確認する。
2. 一意に決まらないCE1差異は子Issueへ分離し、値を変えないまま履歴移動だけ先行できるか判定する。
3. `Card` / `DocumentV2`の加算fieldを先頭合成型へ統合する。
4. APIは型の再掲をやめ、schemasの型名/anchor参照へ置換する。
5. H-A〜H-Dを1batchずつ移動し、各batchでリンクとcontract testを実行する。
6. reading guideとAGENTSの導線を最終構成へ同期する。

停止条件:

- Accepted ADRを読んでもrequired key、列挙、既定値を一意に決められない。
- `version: 3`、既存Contract IDの意味変更、新error、新しい安全・共有境界が必要になる。
- SafeMode、proposal-only、未レビュー保護、人手レビュー昇格の意味が変わる。
- 元anchorを参照するリンクまたはtestを、新しいanchorへ安全に移せない。

## 7. 検証コマンド

```powershell
rg -n "ContextQueryV1|ContextBundleV1|ProposalPatchV1|AuditEventV1" 02_Architecture
rg -n "holdState|shelf|meta|contradictionSignalDecisions|ka" 02_Architecture/schemas.md 02_Architecture/data_model_operations_overview.md
rg -n "^#{1,4} .*?(Stream|freeze|Freeze|rerun|execution log|checkpoint|reaffirmation|handoff)" 02_Architecture/architecture.md 02_Architecture/api.md 02_Architecture/schemas.md 02_Architecture/data_model_operations_overview.md
```

最終的なDone判定には、backend/frontendの対象contract/roundtrip test、相対リンク検査、`git diff --check`が必要である。
