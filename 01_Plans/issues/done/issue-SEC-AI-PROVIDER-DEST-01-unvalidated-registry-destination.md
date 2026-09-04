# Issue: SEC-AI-PROVIDER-DEST-01 model providerの配送先・種別を登録時に検証していない

- Type: Security / SSRF boundary
- Status: Done
- Source Issue: `AI-MODEL-GOVERNANCE-03`動的provider dispatch実装時のモンキーテスト（2026-08-26）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/model_registry.py`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, model registry tests
- Related ADR/Spec: `ADR-0065`, `AI-MODEL-GOVERNANCE-03`, trusted HTTP endpoint contract
- Expected verification level: `integration`

## 課題

管理APIはproviderの`baseUrl`と`providerKind`を長さだけ検証して保存していた。短期実装ではprocess-wide providerだけを使うためregistry URLは配送先にならなかったが、providerId駆動dispatchではこの値が外向き通信先になる。非loopback HTTP、userinfo/query/fragmentを含むURL、未知provider種別を受け入れると、SSRF面の拡大または意図しないtransport選択につながる。

## 対応方針

- 登録時に共通trusted HTTP endpoint契約を適用し、HTTPはloopbackだけ、HTTPSはuserinfo/query/fragmentなしに限定する。
- provider種別をlocal／DeepSeek／large-scaleと既知aliasに限定する。
- DB直接投入・旧データを考慮し、実行時provider factoryでもURLと種別を再検証する。
- 不正値を応答へ反射せず、provider unavailableとしてfail-closedにする。

## 受入条件

- [x] 非loopback HTTP配送先は登録時に422となりDBへ保存されない。
- [x] 未知provider種別は登録時に422となりDBへ保存されない。
- [x] HTTPSとloopback HTTPの正規URLは登録できる。
- [x] DBに不正な旧値が存在してもLLM transportを開始しない。
- [x] 拒否応答に入力URLを反射しない。

## 対応結果（2026-08-26）

provider登録validatorとruntime factoryへ同じtrusted endpoint／provider kind検証を追加した。registry値が実行配送先へ昇格しても、管理APIを新しい任意HTTP clientとして利用できない境界を固定した。


## 配置の整理（2026-09-05）

- 本Issueは、model registryから実行transportへ渡る管理・credential・配送先の境界をfail-closedに固定し、必要な統合確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 既存のライフサイクル契約に従い、本変更では同じprovider/model registry境界の完了済みIssue 3件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を49から46へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
