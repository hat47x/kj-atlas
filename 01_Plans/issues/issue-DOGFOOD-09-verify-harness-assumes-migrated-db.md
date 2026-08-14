# Issue: DOGFOOD-09 verify_all.sh の API/MCP 検証が DB migration 未適用を 500 としてしか見せない

- Type: Process / Bug
- Status: Open
- Source Issue: DOGFOOD-01（ドッグフーディング検証経路の拡張で発見、2026-08-13）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/verify_all.sh`, `03_Implement/backend/scripts/verify_api_inquiry.sh`（検証経路の前提）
- Related ADR/Spec: `03_Implement/backend/README.md`（`alembic upgrade head` 手順）, `01_Plans/dogfood/README.md`（検証経路の追加規約・DOGFOOD-06）
- Expected verification level: `docs-check`

## 課題

`verify_all.sh` check 9（API/MCP の非Web検証）は、稼働中のバックエンドへ curl/tsx チェックを投げるが、**バックエンドの DB が現在の alembic head に到達しているかを事前に確認しない**。

実地で再現した（2026-08-13、inquiry-bundle CAS 検証スクリプトを追加した直後）:

```text
FAIL: create (If-None-Match: *) returns 201 (expected 201, got 500)
...
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: inquiry_bundles.revision
[SQL: DELETE FROM inquiry_bundles WHERE ... AND inquiry_bundles.revision = ?]
```

原因はコードではなく、**ローカル DB に新 migration（`20260813_0026_add_inquiry_bundle_revision`）が未適用だった**こと。`alembic upgrade head` を実行したところ全チェックが pass した（17/17）。

### なぜ問題か

- **検証経路が「コードの不具合」と「環境の未整備」を区別しない**: 500 だけを見て、コード側に原因があるように読める。実際は手動手順（README 記載の `alembic upgrade head`）の取りこぼしである。
- **DOGFOOD-06 の規約（検証は異常系も assert する）と整合しない**: 検証経路自身が「正常に動作するための前提（DB が head）」を assert していない。
- **migration 追加後の初回実行で必ず踏む**: 新 migration を追加した PR 直後のローカル検証で、この 500 で混乱する。CI では fresh DB を migrate するため顕在化しないが、ローカル・手動運用では再現する。

### 三要素分析

- **機能設計（検証機能）**: check 9 の前提条件（DB が head）が検査されていない。検証は「対象が正しく動く」ことを測るべきで、「対象が起動している」ことしか測っていない（healthz 200 のみ）。
- **データ設計**: migration と DB schema の整合は手動手順のドメインに属し、検証ハーネスの入力前提として明示されていない。`alembic current`（実際の適用状態）と `alembic heads`（正本の期待状態）を比較すれば機械的に判定できる。
- **業務設計**: 検証の目的は「管理者が自前スクリプトで CLI/API を使えるか」の確認（DOGFOOD-01 の拡張）。この経路が環境起因の 500 で壊れると、検証結果の信頼性（CI 化・L3 昇格基準への利用）を損なう。

## 対応方針

- 実施すること:
  1. `verify_all.sh` check 9 の実行前に、DB の migration 状態を検査するガードを追加する。`alembic current` が `alembic heads` と一致しない場合、curl/MCP チェックを実行せず「migrations not applied — run `alembic upgrade head`」と明確に報告して SKIP（または個別 FAIL）にする。
  2. またはバックエンド起動時の `_assert_linear_migration_history` に「DB revision != head なら warning を stderr に出す」を追加する（破壊しない・起動は続行）。
  3. `verify_api_inquiry.sh` / `verify_api_write.sh` の冒頭コメントに「前提: `alembic upgrade head` 済み」を明記する。
- 実施しないこと:
  1. 検証スクリプトが自動で migration を適用する（`upgrade head` を自動実行）— 検証が DB を書き換えるのは意図しない副作用であり、読み取り専用の検証経路の性質を壊す。
  2. 500 を出す backend 側を変更する（環境未整備は backend の不具合ではない。ただし error detail に `no such column` が含まれるのは既に構造化されており、十分判読可能）。

## 受入条件

- [ ] `verify_all.sh` check 9 が、migration 未適用の DB に対して「migrations not applied」と明確に報告し、無意味な 500 の羅列を出さない。
- [ ] migration 適用済み（`alembic upgrade head` 後）では従来どおり全チェックが pass する。
- [ ] DOGFOOD-06 の規約（検証は前提条件も assert する）と整合している。

## 検証計画

- 実行コマンド:
  - migration 未適用の DB + 稼働中バックエンドで `bash 03_Implement/backend/verify_all.sh` → check 9 が「migrations not applied」を報告する。
  - `alembic upgrade head` 後に再実行 → check 9 が全 pass。
- 期待結果: 環境起因の 500 が判読可能な案内へ置き換わる。

## 補足

- 発見経緯: ドッグフーディングで `verify_api_inquiry.sh`（inquiry-bundle CAS 検証、DATA-INQUIRY-CONCURRENCY-01）を新設した際、migration 未適用の DB に対して 17 チェック中 15 が 500 になり、`alembic upgrade head` 後に 17/17 pass へ回復した実地記録。
- DOGFOOD-03/04/06 と同じく「2026-08 に追加された検証経路の前提の CI 未カバー」の系譜にある。
