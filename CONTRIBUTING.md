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
  - `curl -fsS http://localhost:8080/api/health`
  - `PUT /api/docs/{doc_id}` と `GET /api/docs/{doc_id}` 往復確認
  - `npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line`（smoke + document replace）
- Docker未導入の場合は、SQLite代替E2E（`backend:8000` + `frontend:4173`）を実施してください。
  - `curl -fsS http://localhost:8000/healthz`
  - `curl -fsS http://localhost:4173/api/healthz`
  - `PUT /docs/{doc_id}` と `GET /docs/{doc_id}` 往復確認
  - `npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line`（smoke + document replace）
- それでもE2E実行不能な場合のみ、PR本文に「ブロッカー」「代替検証」「後続手順」と「Compose未確認リスク（PostgreSQL/web proxy/depends_on health）」を必ず記載してください。
- UI変更を含む場合は、原則として Playwright E2E テストの追加/更新（最低1ケース）を行ってください。



## Frontend lint 段階導入ガイド（ADR-0018 Follow-up）

Frontend lint は Phase A/B/C で段階導入します。
既定運用は **Phase B（fail-on-error）** です。

### Phase別チェックリストと完了条件

- **Phase A（warn-only）**
  - [ ] ローカルで `npm run lint` を実行し、結果を確認した。
  - [ ] CI `frontend-lint` が warning可視化として動作している。
  - [ ] lint例外は期限付きIssueで管理している。
- **Phase B（fail-on-error）**
  - [ ] `FRONTEND_LINT_PHASE=B` がCIに設定済み。
  - [ ] `frontend-lint` 失敗時にPRがfailになる。
  - [ ] 期限切れ例外を解消済み。
- **Phase C（tighten）**
  - [ ] 新規ルールは warn期間を経て error 化している。
  - [ ] ルール追加時に規約・CI・本ガイドを同一PRで同期している。

### 開発者の実行手順（`npm run lint`）

```bash
cd 03_Implement/frontend
npm ci
npm run lint
npm run typecheck
npm run test
```

- `npm run lint` が失敗した場合は、違反修正を優先してください。
- 直ちに解消不能な場合のみ、**期限付き例外Issue**（理由・担当・期限）を登録し、PR本文へリンクします。
- 期限の目安は14日以内。期限切れ例外が残るPRは原則マージしません。

### 期限付き例外の運用（必須）

例外申請時は、以下をIssue本文に必ず記載してください。

- 対象ルール（例: `@typescript-eslint/no-explicit-any`）
- 発生箇所（ファイル/行）
- 直ちに解消できない理由
- 解消担当者
- 解消期限（原則14日以内）
- 解消PR（後追いで追記可）

運用ルール:

1. 期限切れ例外が1件でも残る場合、Phase B/Cではマージ停止。
2. 期限延長は1回ごとに理由をIssueコメントで明記。
3. 恒久除外（eslint-disable固定化）は禁止。必要ならADR/Issueで方針決定を行う。

### 失敗時の切り分け（CI / ローカル共通）

1. **`frontend-lint` のみ失敗**
   - `npm run lint` を再実行し、ルール違反を修正。
2. **`frontend-typecheck` のみ失敗**
   - `npm run typecheck` で型エラーを特定し、型定義や呼び出し側を修正。
3. **`frontend-test` のみ失敗**
   - `npm run test` と `npm run build` を分けて再実行し、テスト不安定かビルド破壊かを切り分け。
4. **複数ジョブ失敗**
   - lint → typecheck → test/build の順で修正（上流の静的エラーから潰す）。

CIの `FRONTEND_LINT_PHASE` が `A/B/C` 以外なら設定不正です。Repository Variables を修正してください。

### CI責務分離（保守者向け）

- `frontend-lint`: lintポリシー適用（Phase Aは警告、Phase B/Cは失敗）。
- `frontend-typecheck`: TypeScript型検査。
- `frontend-test`: Frontendテストとbuild検証。

fail-on-error条件:

- `frontend-lint`: `FRONTEND_LINT_PHASE=A` のみ警告継続。それ以外（B/C）は失敗でPRを停止。
- `frontend-typecheck`: 常に失敗でPRを停止。
- `frontend-test`: 常に失敗でPRを停止。

### 差分監査（規約 / CONTRIBUTING / CI）

同一PRで次を確認してください。

1. `02_Architecture/coding_standards.md` にPhaseとexit criteriaがある。
2. 本書に `npm run lint` 手順・失敗時対処・例外運用がある。
3. `.github/workflows/ci.yml` のジョブ責務とfail条件が文書記述と一致する。
4. `01_Plans/adr/ADR-0018-coding-standards-and-smell-remediation.md` の Follow-up 要件と矛盾がない。

確認コマンド:

```bash
rg -n "frontend-lint|frontend-typecheck|frontend-test|FRONTEND_LINT_PHASE|npm run lint|Phase A|Phase B|Phase C" \
  02_Architecture/coding_standards.md CONTRIBUTING.md .github/workflows/ci.yml
```

サンプルPR自己レビュー（推奨）:

1. `FRONTEND_LINT_PHASE` の値が想定（通常は `B`）か。
2. `frontend-lint` 失敗時にCI Summaryへ phase と outcome が出るか。
3. lint/typecheck/test のどのジョブが失敗したかを1行で説明できるか。
4. 規約・本書・CIの記述差分が残っていないか（上記 `rg` で確認）。

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
5. memoのValidation planに加え、issue / docsを変更した場合は `python 01_Plans/docs_check.py` を実行する。
6. Pull Requestで変更理由、対象memo、commandと結果、未実施理由と再開条件を提示する。

小さなtypoや明白なリンク修正は、issue memoなしで直接PRして構いません。脆弱性はDiscussionsや公開PRへ詳細を書かず、`SECURITY.md`を優先してください。

## ラベル運用ガイド / Labeling guidance（GitHub Issues運用開始後）

### 標準ラベル

- `bug`: 不具合・回帰
- `enhancement`: 機能改善・機能追加
- `good first issue`: 初回貢献に適した小さく明確な課題
- `help wanted`: 担当者を広く募集したい課題
- `security`: セキュリティ関連（詳細は `SECURITY.md` 優先）
- `docs`: ドキュメント修正・追記

### `good first issue` の付与目安

- 変更範囲が限定的（目安: 1〜3ファイル）
- 完了条件が箇条書きで明確
- 前提知識が少なくても着手可能（参考リンクあり）
- ローカルで再現・確認しやすい

### メンテナのトリアージ方針（現在）

1. DiscussionsまたはPRで受けた内容を、質問、Action、Decision、Securityへ一次分類する。
2. Actionは既存memoとの重複を確認し、`01_Plans/issues/`へ起票する。
3. DecisionはADR化トリガーを確認し、Securityは公開転記せず`SECURITY.md`へ誘導する。
4. GitHub Issues運用開始後に限り、上記標準ラベルを適用する。


### E2Eドキュメント整合ルール

- 開発者向けE2E手順の正本は `03_Implement/frontend/docs/e2e_testing.md` です。
- 一般利用者向けの画面確認は `04_Documentation/acceptance_check.md` に分離します。
- E2Eのコマンド・受入基準・代替経路（Docker未導入時）を変更する場合は、同一PRで `04_Documentation/acceptance_check.md`、`04_Documentation/installation.md`、`04_Documentation/operations.md` も同期確認してください。
- 不足・不整合を見つけたら「あるべき状態」を先に明文化し、正本へ合わせて同期してください。正本判断が難しい場合はIssueを起票して管理してください。
- PR本文には、更新したE2E関連文書の一覧を記載してください。
