# E2E Verification Log Template

対象読者: E2E 実施結果を共有する開発者、QA、運用担当者。

目的: 公開可能な検証結果を、再現に必要な最小情報だけで記録する形式を示します。

範囲外: 個人情報、秘密情報、内部承認履歴、生の顧客データ、非公開 URL。

公開区分: 開発者/検証記録向け。一般利用者向け Gist には含めず、E2E検証結果の記録と後続確認のために使います。

## 記録方針

- 実行環境とコマンドは再現できる粒度で書きます。
- 失敗した場合は、期待結果、実際の結果、回避策、次の確認先を書きます。
- スクリーンショットやログは、秘密情報が含まれないことを確認してから添付します。
- 内部 issue 番号や作業ログは、公開文書ではなく内部管理側に残します。

## テンプレート

````markdown
## E2E verification

- Date:
- Commit:
- Environment:
- Browser:
- URL:
- Dataset:

### Commands

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
```

### Manual smoke

- [ ] Opened the application.
- [ ] Created a document.
- [ ] Added and moved cards.
- [ ] Saved and reloaded the document.
- [ ] Confirmed toolbar/header controls are visible.
- [ ] Confirmed export/share output excludes secrets and internal logs.

### Automated checks

- [ ] `npm run typecheck`
- [ ] `npm run test`
- [ ] `npm run e2e`
- [ ] backend tests, if backend changed

### Result

- Status: Pass / Fail / Blocked
- Notes:
- Follow-up:
````

## 記録例

````markdown
## E2E verification

- Date: 2026-03-03
- Commit: <commit sha>
- Environment: local Docker Compose
- Browser: Chrome
- URL: http://localhost:8080
- Dataset: synthetic sample only

### Commands

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
```

### Result

- Status: Pass
- Notes: document create/save/reload succeeded. No secrets were used.
- Follow-up: none
````

## 関連文書

- [開発者向け E2E Testing](https://github.com/hat47x/kj-atlas/blob/main/03_Implement/frontend/docs/e2e_testing.md)
- [release.md](release.md)
- [security.md](security.md)
