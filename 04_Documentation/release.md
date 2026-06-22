# Release

対象読者: kj-atlas のリリース、検証版配布、公開前確認を担当する人。

目的: リリース前に確認する品質、安全性、文書、受け入れ確認の最小手順をまとめます。

範囲外: 組織固有の承認システム、配布先ごとの秘密設定、マーケティング告知。

公開区分: リリース/04文書保守者向け管理文書。一般利用者向け Gist の本文には原則含めず、公開前確認と安全境界レビューのチェックリストとして使います。

## リリース前チェック

```bash
git status -sb
git diff --check
```

この文書でいうリリースは、利用者が触れる状態へ変更を出すことです。正式版だけでなく、検証版や社内配布でも同じ考え方を使います。

## 前提知識

リリース担当者は、すべての実装詳細を理解している必要はありません。ただし、次の違いは確認できるようにしておきます。

| 用語 | 意味 |
| --- | --- |
| build | 利用者が実行できる形に frontend などを組み立てること |
| test | 期待した動作を機械的に確認すること |
| smoke test | 主要操作だけを短時間で手動確認すること |
| rollback | 問題が出たときに前の状態へ戻すこと |

## リリース判断の流れ

1. 差分の範囲を確認する。
2. 影響するテストを実行する。
3. 手動 smoke test で利用者の主要操作を確認する。
4. security / SafeMode / 外部サービスとの共有の安全境界が後退していないことを確認する。
5. data handling の観点で export、share、ログ、外部サービスとの共有の扱いを確認する。
6. rollback 方針を確認する。

frontend:

```bash
cd 03_Implement/frontend
npm ci
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
- [ ] 監査ログの HTTP 連携や外部アクセス制御を有効にした場合、連携先と失敗時の動作が説明できる。

## 文書確認

- [ ] [installation.md](installation.md) の起動手順が現行実装と合っている。
- [ ] [configuration.md](configuration.md) の環境変数が `settings.py` と矛盾していない。
- [ ] [data_handling.md](data_handling.md) の保存・外部サービスとの共有・共有前確認が現行実装と矛盾していない。
- [ ] [security.md](security.md) の外部サービスとの共有の境界が維持されている。
- [ ] [acceptance_check.md](acceptance_check.md) の確認手順が再現できる。
- [ ] README や 04 文書に内部 issue 記録や秘密情報が混ざっていない。

## 失敗時の扱い

次のいずれかに当てはまる場合、リリースを止めます。

- build、test、typecheck の失敗理由が説明できない。
- SafeMode、share/export、LLM provider の安全境界が後退している。
- 秘密情報、内部 URL、生の顧客情報が文書や export に混ざっている。
- 受け入れ確認の主要操作が再現できない。

止めることは失敗ではありません。利用者に影響する不確実性を見つけた状態なので、原因、回避策、再開条件を記録してから次の確認に進みます。

## リリース記録に残す項目

- 対象 commit
- 実行した確認コマンド
- 受け入れ確認の結果
- 既知の制限
- rollback 方針

## 関連文書

- [acceptance_check.md](acceptance_check.md)
- [e2e_verification_log_2026-03-03.md](e2e_verification_log_2026-03-03.md)
- [data_handling.md](data_handling.md)
- [operations.md](operations.md)
- [security.md](security.md)

## 運用手順（DOC-OPS-05）
1. 対象読者（Audience）と目的（Goal）を先に確認する。
2. 公開境界（Public boundary）を確認し、内部手順は公開文書へ直接書かない。
3. 実行後は関連文書の導線（Related links）と矛盾がないか確認する。

## 判断基準（DOC-OPS-05 品質ゲート）
- 可読性: 用語が定義済み語彙と一致し、読者の次アクションが明確であること。
- 検証可能性: 手順・確認コマンド・期待結果が対応していること。
- 保守性: 上流（00〜02）と矛盾せず、関連文書へ責務を分離していること。

## 失敗時対応
- 参照不整合、用語不一致、公開境界の曖昧化を検出した場合は更新を停止する。
- 自己修復は最大3回までとし、4回目相当は Hold として論点化する。
- Architecture/ADR 本体の変更が必要な場合は、この文書では確定せず提案に留める。
