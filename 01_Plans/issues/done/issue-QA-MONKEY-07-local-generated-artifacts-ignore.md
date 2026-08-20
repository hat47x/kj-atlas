# Issue Draft: QA-MONKEY-07 Local generated artifacts ignore rules

- Type: Process / Bug
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD
- Scope: `.gitignore`
- Related Backlog: `QA-MONKEY-07`
- Related ADR/Spec: `04_Documentation/installation.md`, `AGENTS.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-07
- RequirementStatement: Local fallback setup artifacts must not appear as accidental untracked source changes.
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=manual SQLite/frontend setup / 操作=install frontend dependencies and create local SQLite DB / 期待結果=`node_modules/` and local `*.db` files are ignored / 除外=tracked fixture databases, if introduced intentionally later.
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A

## 1) 課題 / Problem statement

- Manual setup created `03_Implement/frontend/node_modules/` and `03_Implement/backend/kj_atlas.db`.
- Both appeared as untracked files, making the worktree noisy and increasing the risk of accidental add.

## 2) 背景 / Context

- `04_Documentation/installation.md` documents SQLite fallback with `kj_atlas.db`.
- Frontend dependency installation creates `node_modules/`.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Cleaner local setup reduces review noise.
- 安全（THREAT_MODEL / SafeMode）: Avoids accidental local DB inclusion.
- 企業・行政要件（enterprise_architecture）: Keeps local artifacts out of source review.
- 後方互換（schemas）: Ignore-only change; no runtime effect.

## 4) 提案する解決策 / Proposed solution

- 変更対象: `.gitignore`.
- 変更の最小単位: Ignore `node_modules/`, `*.db`, and `*.db-journal`.
- 非目標: Removing generated files from the local workspace or changing install instructions.

## 5) 受入条件 / Acceptance criteria

- [x] Local node dependencies are ignored.
- [x] Local SQLite DB artifacts are ignored.
- [x] `git status --short` no longer lists these generated artifacts as source changes.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Add ignore rules.
- [x] T2 Re-check `git status --short`.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git status --short`
  - `git diff --check`
- 期待結果:
  - Generated `node_modules/` and `kj_atlas.db` are not listed as untracked changes.
- 未実施時の理由・代替検証:
  - N/A.

## 8) 代替案 / Alternatives considered

- 代替案A: Delete generated artifacts after every run. Rejected because the local environment remains useful for verification.
- 代替案B: Ignore only the exact `kj_atlas.db` file. Rejected because SQLite local DB names may vary.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: A deliberately created DB fixture could be ignored until force-added.
- 影響範囲: Git ignore behavior only.
- ロールバック手順: Remove the new ignore rules.

## 10) Additional context

- ADR化が必要になる条件: Repository-wide fixture/artifact policy changes.

---
