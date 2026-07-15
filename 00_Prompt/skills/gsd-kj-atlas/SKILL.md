---
name: gsd-kj-atlas
description: Get Shit Done の phase 運用を kj-atlas の 00〜04 階層ルールに適合させる補助スキル。
---

# gsd-kj-atlas

## Purpose

Get Shit Done（GSD）のタスク分割を使って、kj-atlas の変更を
**小さく・再開可能に**進める。

## Use this skill when

- 複数ファイルにまたがる変更を行う。
- 受入条件（Acceptance）を先に固定したい。
- 中断・再開を前提に進める。

## Mandatory constraints

1. 仕様の正本は `00_Prompt` / `01_Plans` / `02_Architecture`。
2. GSD は実行管理のみで、仕様決定を行わない。
3. SafeMode 既定ON と漏えい防止（share/export）を破らない。

## Workflow

1. `AGENTS.md` から現在のタスクに必要な正本だけを確認する。
2. タスクを milestone / phase に分割する。
3. 各 phase に以下を固定する。
   - Scope
   - Non-Goals
   - Acceptance Criteria
   - Checks
4. 実装後に verify を実施し、結果を記録する。
5. 必要な `04_Documentation` を同期する。

## Phase template

```md
## Task Brief
- Scope:
- Non-Goals:
- Acceptance Criteria:
  - [ ] ...
  - [ ] ...
- Checks:
  - [ ] tests/lint
  - [ ] docs sync
  - [ ] safeMode impact
```

## Output contract

- 実施済み: 変更内容と検証結果を明確に分離。
- 未実施: 次の1手（開始コマンド/編集対象）を明示。
