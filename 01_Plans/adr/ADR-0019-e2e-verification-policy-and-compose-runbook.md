# ADR-0019-e2e-verification-policy-and-compose-runbook: E2E確認方針とCompose実行手順の標準化

- Status: Accepted
- Date: 2026-02-26
- Deciders: Project Maintainers
- Scope: `01_Plans/`, `03_Implement/`, `04_Documentation/`, `CONTRIBUTING.md`

## Context

`kj-atlas` は Canvas/UI（Frontend）・API（Backend）・永続化（DB）の連動で価値を提供する。
このため unit/integration が通過していても、結合境界で不整合が残ると人間レビュー時に
「実装不具合の切り分け」に時間を使い、仕様評価に集中できない。

本ADRの目的は次の1点に集約する。

- **人間が仕様を評価するフェーズでは、結合レベルのバグを極小化し、評価認知負荷を下げること。**

また、開発/検証環境によっては `docker compose` が利用できないため、
非Docker環境でも同等の結合確認を継続できる方針が必要である。

---

## Decision

以下を標準運用として採用する。

### 1. 目的駆動の原則（なぜE2Eを行うか）

1. E2E確認は「デモのため」ではなく、**仕様評価前に結合バグを除去する品質ゲート**として扱う。
2. `03_Implement/*` の変更では、原則E2E確認を必須とする。
3. UIを伴う変更では、**PlaywrightベースのE2E追加/更新を原則必須**とする。

### 2. 実行優先順位（どの経路でE2Eするか）

1. **第一選択: Compose統合経路（標準）**
   - `web + api + db` を `docker compose` で起動し、実運用に最も近い構成で確認する。
2. **第二選択: SQLite代替経路（Docker未導入時）**
   - `backend(SQLite)` + `frontend dev server` の2プロセスで、API/永続化/UI連動を確認する。
3. **第三選択: 例外記録（上記が実行不能な場合のみ）**
   - ブロッカー・代替検証・後続手順をPRに明記し、未確認リスクを可視化する。

### 3. 最小受入基準（PRマージ前に満たすもの）

#### 3.1 共通（必須）

- ヘルス確認:
  - Compose: `curl -fsS http://localhost:8080/api/health`（または同等）
  - SQLite代替: `curl -fsS http://localhost:8000/healthz` と `curl -fsS http://localhost:4173/api/healthz`
- ドキュメント往復保存確認:
  - `PUT /docs/{doc_id}` → `GET /docs/{doc_id}` が成功し、保存内容が保持される。

#### 3.2 UI変更時（必須）

- Playwrightで smoke + 変更対象フロー1ケース以上を実行する。
- PR本文に実行コマンドと結果（pass/fail/未実施理由）を記載する。

### 4. kj-atlas向けE2E設計原則（将来拡張でも維持）

1. **仕様境界優先**
   - カード編集、Island操作、保存復元、SafeMode、import/export など
     仕様の価値境界を優先してE2E対象を選ぶ。
2. **安全境界優先**
   - SafeMode既定ON、漏えい防止、悪性入力拒否など安全性に関わる経路を優先する。
3. **決定論優先**
   - flakeを避けるため、非決定的待機を減らし、入力と期待結果を固定する。
4. **最小維持コスト**
   - すべてをE2Eで覆わず、unit/integrationとの責務分担を維持する。

### 5. 現時点で見えている実務課題（2026-02時点）

1. Docker未導入環境の存在により、Compose確認が常に実行できるとは限らない。
2. Frontend/Backendのローカル起動手順が分散すると、確認漏れが発生しやすい。
3. UI改修の増加に伴い、Playwrightシナリオを「価値境界ベース」で整理しないと肥大化する。

対処方針:
- `04_Documentation/e2e_testing.md` をE2E実務手順の正本とし、
  シナリオ追加時は Smoke / Core / Safety のどこを守るかを明示する。

### 6. ドキュメント同期ルール

- 以下の文書は本ADRと整合させる。
  - `04_Documentation/installation.md`
  - `04_Documentation/operations.md`
  - `04_Documentation/e2e_testing.md`
  - `CONTRIBUTING.md`
  - `01_Plans/coding_standards.md`

---

## Consequences

- 結合不具合が仕様レビューに流入しにくくなり、人間は仕様評価に集中しやすくなる。
- 非Docker環境でもSQLite代替経路で連動確認を継続できる。
- E2Eの目的・優先順位・受入基準が固定され、将来機能拡張時も判断軸を共有できる。
- Playwrightの適用範囲を「価値境界ベース」で管理することで、回帰防止と運用コストを両立できる。

## Traceability

- Related: `03_Implement/deploy/docker-compose.yml`
- Related: `03_Implement/backend/README.md`
- Related: `04_Documentation/installation.md`
- Related: `04_Documentation/operations.md`
- Related: `04_Documentation/e2e_testing.md`
- Related: `CONTRIBUTING.md`
- Related: `01_Plans/coding_standards.md`
- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
