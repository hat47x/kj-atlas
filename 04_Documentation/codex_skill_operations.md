# Codex Skill Operations

> Audience: 外部コントリビュータ / 運用担当者
> Purpose: Codex skill運用の公開境界と参照導線を示す。
> This document decides: 公開可能な運用原則、正本参照先、最低限の検証手順。
> This document does not decide: 内部監査詳細、環境固有の実行秘密、仕様の新規決定。
> Related: `00_Prompt/codex_gsd_skill_ops.md`, `00_Prompt/agent_handover.md`, `01_Plans/documentation_quality.md`

## 1. 位置づけ（責務境界）

- skill は「実行補助」であり、仕様の正本ではありません。
- 仕様の正本は `00_Prompt` / `01_Plans` / `02_Architecture` です。
- 本書は「どう参照し、どう安全に運用するか」を定義します。

## 2. Go/No-Go gate（公開判定）

次を満たす場合のみ公開運用を Go とします。

1. Audience / decides / does not decide が明示されている。
2. 内部手順（秘密情報・組織依存設定）を本文に混在させていない。
3. SafeMode既定ON・share/export境界を後退させる記述がない。

未充足時は No-Go として内部文書側で修正してから再判定します。

## 3. 内部正本への導線

- 運用方針（詳細）: `00_Prompt/codex_gsd_skill_ops.md`
- タスク実行テンプレ / DoD: `00_Prompt/agent_handover.md`
- 公開品質ゲート: `01_Plans/documentation_quality.md`

## 4. 最小運用ルール

1. 作業開始前に `AGENTS.md` の Read Order を確認する。
2. docs-only タスクではコード変更を行わない。
3. 上流文書（00〜02）と矛盾が見つかった場合、実装を止めて論点化する。
4. Verify の自己修復は最大3回。3回超過は `StoppedForClarification`。

## 5. 環境依存手順の前提

skill導入/実行コマンドを使う場合は、前提条件を必ず明記します。

- Codex実行環境が利用可能であること。
- `$CODEX_HOME/skills` が参照可能であること。
- 組織ポリシー上、外部取得が許可されていること（必要時）。

> 環境が満たせない場合は、コマンド実行を省略し「未実施理由」を記録してください。

## 6. Verify

```bash
rg -n "Audience|This document decides|This document does not decide|Go/No-Go|SafeMode|StoppedForClarification" 04_Documentation/codex_skill_operations.md
git diff --check
```
