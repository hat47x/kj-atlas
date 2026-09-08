# Issue: SEC-ADMIN-MODEL-02 登録APIが既存provider/model IDを暗黙上書きした

- Type: Security / Correctness
- Status: Done
- Source Issue: 管理UI・CLI・API協調モンキーテスト（2026-08-17）
- Priority: P1
- Owner: Maintainer
- Scope: `backend/src/kj_atlas_api/routes/model_registry.py`, `model_registry_repository.py`, management CLI/API tests
- Related ADR/Spec: `ADR-0072`, `AI-MODEL-GOVERNANCE-01`, `02_Architecture/api.md`
- Expected verification level: `integration`

## 課題

`POST /admin/provision/models/providers`と`POST /admin/provision/models`は「登録」APIだが、repositoryの`Session.merge`を使っていた。同じIDを再送すると409ではなく既存rowを更新し、provider kind、modelのprovider所属、表示名、capabilities、作成時刻を暗黙に置換できた。

管理者の再送やautomation競合が、明示的な更新操作・差分・確認なしに実行transportやtenantの実効model集合を変えるためP1とした。

## 対応

- 動的登録APIはinsert-onlyのrepository経路へ分離した。起動時seedのupsert経路は維持する。
- provider ID重複は`409 provider_already_exists`、model ID重複は`409 model_already_exists`で拒否する。
- 競合後も既存provider kind、model providerId、表示名が変わらないことを統合testで固定した。
- CLIは既存の構造化error契約によりcodeを表示し、非0終了する。

## 受入条件

- [x] 同一provider IDの再登録で既存rowを変更しない。
- [x] 同一model IDを別providerへ再登録しても所属を変更しない。
- [x] 競合は安定した409 codeで返る。
- [x] seedの冪等upsertと管理APIのinsert-only契約が分離される。

## 検証記録（2026-08-17）

provider/modelの初回登録、異なる内容での再登録、DB row不変、CLI error伝播を近接testで確認した。


## 配置の整理（2026-09-05）

- 本Issueは、model registryから実行transportへ渡る管理・credential・配送先の境界をfail-closedに固定し、必要な統合確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 既存のライフサイクル契約に従い、本変更では同じprovider/model registry境界の完了済みIssue 3件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を49から46へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
