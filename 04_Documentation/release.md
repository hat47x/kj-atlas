# Release

対象読者: kj-atlas のリリース、検証版配布、公開前確認を担当する人。

目的: リリース前に確認する品質、安全性、文書、E2E の最小手順をまとめます。

範囲外: 組織固有の承認システム、配布先ごとの秘密設定、マーケティング告知。

## リリース前チェック

```bash
git status -sb
git diff --check
```

frontend:

```bash
cd 03_Implement/frontend
npm install
npm run typecheck
npm run test
npm run build
```

backend:

```bash
cd 03_Implement/backend
python -m pytest
```

Docker Compose:

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
```

## 手動確認

- [ ] アプリが開く。
- [ ] 新規ドキュメントを作成できる。
- [ ] カードを追加・移動できる。
- [ ] 保存して再読み込みしても内容が残る。
- [ ] share/export に秘密情報や内部作業ログが含まれない。
- [ ] SafeMode の既定動作が緩んでいない。
- [ ] LLM provider が意図した値になっている。

## 文書確認

- [ ] [installation.md](installation.md) の起動手順が現行実装と合っている。
- [ ] [configuration.md](configuration.md) の環境変数が `settings.py` と矛盾していない。
- [ ] [security.md](security.md) の外部送信境界が維持されている。
- [ ] [e2e_testing.md](e2e_testing.md) の確認手順が再現できる。
- [ ] README や 04 文書に内部 issue 記録や秘密情報が混ざっていない。

## 失敗時の扱い

次のいずれかに当てはまる場合、リリースを止めます。

- build、test、typecheck の失敗理由が説明できない。
- SafeMode、share/export、LLM provider の安全境界が後退している。
- 秘密情報、内部 URL、生の顧客情報が文書や export に混ざっている。
- E2E の主要操作が再現できない。

## リリース記録に残す項目

- 対象 commit
- 実行した確認コマンド
- E2E 結果
- 既知の制限
- rollback 方針

## 関連文書

- [e2e_testing.md](e2e_testing.md)
- [e2e_verification_log_2026-03-03.md](e2e_verification_log_2026-03-03.md)
- [operations.md](operations.md)
- [security.md](security.md)
