# Contributing Guide / コントリビューションガイド

この文書は、`kj-atlas` への変更提案・実装・レビューの最小ルールを定義します。

## リポジトリ構成 / Repository Structure

本リポジトリは階層化方針で運用します。

- `00_Prompt/`: 最上位の開発制約・用語定義
- `01_Plans/`: 実装計画
- `02_Architecture/`: 構造・インターフェース定義
- `03_Implement/`: 実装コード（frontend/backend/deploy）
- `04_Documentation/`: 利用者向けドキュメント

## ローカル実行 / Local Development

### 1) フルスタック（推奨）

```bash
cd 03_Implement/deploy
docker compose up --build
```

### 2) フロントエンド

```bash
cd 03_Implement/frontend
npm ci
npm run dev
```

### 3) バックエンド

```bash
cd 03_Implement/backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
export PYTHONPATH=src
alembic upgrade head
pytest
```

## コーディング規約 / Coding Conventions

詳細規約は [`02_Architecture/coding_standards.md`](02_Architecture/coding_standards.md) を正本として参照してください。

最低限の必須ルール:

- **識別子（変数名・関数名・型名・ファイル名）は英語**で記述する。
- 上位階層（`00_`〜`02_`）と矛盾する仕様変更は、実装前にIssue/PRで合意する。
- 1ファイル1責務を守り、重複ロジック・重複スタイルを増やさない。
- `except Exception` などの広域例外捕捉は原則禁止（期待例外を明示する）。
- SafeMode既定ONやshare/exportの安全既定を壊す変更は禁止。

## テスト方針 / Test Policy

- 差分に対するテスト追加・更新を原則とします。
- 特に以下の領域は回帰防止を重視します。
  - diff / merge
  - import（ZIP / markdown / schema validation）
- 既存テストを壊す変更は、意図と移行方針をPRに明記してください。
- `03_Implement/*` 変更時は、原則として `docker compose` によるE2E確認（`web + api + db`）を実施してください。
  - `docker compose up --build -d`
  - `docker compose ps`
  - `curl -fsS http://localhost:8080/api/healthz`
  - `PUT /api/docs/{doc_id}` と `GET /api/docs/{doc_id}` 往復確認
  - `npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line`（smoke + document replace）
- Docker未導入の場合は、SQLite代替E2E（`backend:8000` + `frontend:4173`）を実施してください。
  - `curl -fsS http://localhost:8000/healthz`
  - `curl -fsS http://localhost:4173/api/healthz`
  - `PUT /docs/{doc_id}` と `GET /docs/{doc_id}` 往復確認
  - `npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line`（smoke + document replace）
- それでもE2E実行不能な場合のみ、PR本文に「ブロッカー」「代替検証」「後続手順」と「Compose未確認リスク（PostgreSQL/web proxy/depends_on health）」を必ず記載してください。
- UI変更を含む場合は、原則として Playwright E2E テストの追加/更新（最低1ケース）を行ってください。



## Frontend の品質ゲート

CI の frontend ゲートは2つだけです。どちらも失敗すればPRを止めます。

- `frontend-typecheck`: `tsc --noEmit`
- `frontend-test`: `vitest run`（全件）

ローカルでは `cd 03_Implement/frontend && npm ci` の後、`npm run typecheck` と `npm run test` を実行します。

独立したリンタは導入していません（`npm run lint` は `npm run typecheck` の別名です）。特定範囲だけ再実行したい場合は `npm run test:i18n` や `npm run test:regression-guards` を使えますが、CIはこれらを個別ジョブにせず `frontend-test` で一括検証します。

## MCP の品質ゲート

`03_Implement/mcp/` の変更時は、CI の `mcp` ジョブ（`npm ci` → `npm run typecheck` → `npm test`）が走ります。`03_Implement/mcp/**` が変更されたPRは、このゲートが通らないとマージできません。

ローカルでは `cd 03_Implement/mcp && npm ci` の後、`npm run typecheck` と `npm test` を実行します。

## Issue と ADR の使い分け（必須）

IssueとADRは混在させず、次の基準で分離して運用します。

### 目的の違い

- **Issue**: Action管理（What/How）。バグ修正・実装タスク・運用作業の進捗追跡。
- **ADR**: Decision & Context管理（Why）。重要な設計判断とトレードオフの記録。

### ADR化のトリガー（いずれかを満たす）

1. 複数案の比較（トレードオフ）がある。
2. 非機能要件（性能・セキュリティ・保守性・可用性）へ影響が大きい。
3. 将来参加メンバーに背景説明が必要な判断である。

### 連携フロー

- Issueで議論した結果、設計判断が必要になったらADRを起票して合意を固定する。
- ADRがAcceptedになったら、実装・検証・移行はIssueへ分解して管理する。
- ADR本文を進捗管理ボード代わりに使わない（進捗はIssueで管理）。


### GitHub Issue と `01_Plans` issue 記述の位置づけ

- 現在のAction管理の正本は **`01_Plans/issues/` のissue memo** です。GitHub Issuesは運用開始していません。
- 利用相談、バグ候補、機能案を外部から共有する場合は、秘密情報を除いてGitHub Discussionsへ投稿してください。メンテナが実行可能なActionへ整理するときにissue memoを作成します。
- GitHub Issuesへ切り替える場合は、メンテナが開始を明示し、この文書、`01_Plans/issues/README.md`、`SUPPORT.md`、`DISCUSSIONS.md`を同時に更新します。それまでは `Source Issue: N/A` またはリポジトリ内の明示的な起点参照が正常です。
- 設計判断が必要な場合はissue memoからADRへ分離し、Accepted後の実装・検証をissue memoへ戻します。


## コミット規約（軽量） / Commit Convention

- 1コミット1目的を推奨します。
- 例: `docs: OSS公開向けポリシー文書を追加`
- 破壊的変更は本文に明記してください。

## 変更提案フロー / How to Propose Changes

1. READMEから本文書へ来たら、リポジトリrootで `python 01_Plans/triage_actionable_plans.py` を実行する。
2. 生成された`Ready issues`から1件選び、`01_Plans/issues/README.md`の運用ルールと対象memoを確認する。固定Active表は持たない。仕様が未確定ならGitHub Discussionsで背景・目的・影響範囲を共有する。新規Actionは`01_Plans/issues/TEMPLATE.md`から作る。
3. 受入条件、Non-goal、Validation plan、参照ADRをmemoで確認する。設計判断が未確定なら実装より先にADRを確定する。
4. `codex/`接頭辞など衝突しないブランチを作成し、memoのScope内だけを変更する。
5. memoのValidation planに加え、issue / docsを変更した場合はrepository rootで `python 01_Plans/docs_check.py` を実行する。現在有効なruleと未有効化ruleはコマンド出力で確認する。
6. Pull Requestで変更理由、対象memo、commandと結果、未実施理由と再開条件を提示する。

小さなtypoや明白なリンク修正は、issue memoなしで直接PRして構いません。脆弱性はDiscussionsや公開PRへ詳細を書かず、`SECURITY.md`を優先してください。

## ラベル運用ガイド / Labeling guidance（GitHub Issues運用開始後）

GitHub Issuesは現在運用していません（`ADR-0039`により、移行runbookと通知体制は実運用開始まで延期）。ラベル分類は運用開始時に定めます。

### メンテナのトリアージ方針（現在）

1. DiscussionsまたはPRで受けた内容を、質問、Action、Decision、Securityへ一次分類する。
2. Actionは既存memoとの重複を確認し、`01_Plans/issues/`へ起票する。
3. DecisionはADR化トリガーを確認し、Securityは公開転記せず`SECURITY.md`へ誘導する。


### E2Eドキュメント整合ルール

- 開発者向けE2E手順の正本は `03_Implement/frontend/docs/e2e_testing.md` です。
- 一般利用者向けの画面確認は `04_Documentation/acceptance_check.md` に分離します。
- E2Eのコマンド・受入基準・代替経路（Docker未導入時）を変更する場合は、同一PRで `04_Documentation/acceptance_check.md`、`04_Documentation/installation.md`、`04_Documentation/operations.md` も同期確認してください。
- 不足・不整合を見つけたら「あるべき状態」を先に明文化し、正本へ合わせて同期してください。正本判断が難しい場合はIssueを起票して管理してください。
- PR本文には、更新したE2E関連文書の一覧を記載してください。
