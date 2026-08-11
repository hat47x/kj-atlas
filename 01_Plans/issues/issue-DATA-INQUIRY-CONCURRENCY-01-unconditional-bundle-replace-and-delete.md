# Issue: DATA-INQUIRY-CONCURRENCY-01 探究bundleの無条件上書き・削除をCAS化する

- Type: Data / API / Security
- Status: Draft
- Source Issue: `DOMAIN-W-ITERATION-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/database_content_store.py`, `03_Implement/backend/src/kj_atlas_api/routes/inquiry_bundles.py`, frontend inquiry client、migration
- Related ADR/Spec: `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`, `02_Architecture/inquiry_journey_model.html`, `02_Architecture/api.md`
- Expected verification level: `integration`

## 課題

現行`POST /inquiry-bundles/{journey_id}`は、既存rowの`payload_json`と`updated_at`を条件なしで置換する。`DELETE`も`tenant_id + journey_id`だけで削除する。GETはETag／revisionを返さず、保存・削除は`If-Match`等のexpected bundle versionを要求しない。

したがって、同じ探究を開いたtab A/Bで、Bが新しいラウンドや分岐を保存した後にAが古いbundleを保存すると、Bの成果が通知なく失われる。Aの古い削除確認も、確認後にBが更新したbundleを削除できる。tenant session version guardはtenant切替のstale contextを止めるだけで、同じtenant内resourceのlost updateを防がない。

frontendローカルbundleは不変snapshot DAGを持つが、backend row全体の置換競合を解決しない。payload内部のdigestは破損検知用であり、認可・真正性・server row versionとして利用しないというAccepted契約がある。

## 設計候補

### 案A: server生成row revision

- `inquiry_bundles.revision`を正整数として追加する。
- GETは本文とETag（revisionのopaque表現）を返す。
- createは`If-None-Match: *`、update/deleteは単一canonical `If-Match`を必須化し、DBの`tenant_id + journey_id + revision`条件でatomic update/deleteする。
- 成功updateでrevisionを1増加し、新ETagを返す。

### 案B: server計算payload digest

- canonical保存JSONのSHA-256をrowへ保存しETagにする。
- update/deleteを旧digest条件でCAS化する。
- 内容同一保存ではETagが変わらないため、更新時刻・lifecycle stateを含むrow mutationの世代としては弱い。

採用候補は案Aである。Documentの公開ETagとは別resource契約とし、tenant session version、bundle内部digest、content-addressed revision digestを流用しない。Maintainerが後方互換とcreate semanticsを確認してから実装する。

## 三要素牽制

| 次元 | 必要な判断 | 他次元への制約 |
|------|------------|---------------|
| **業務設計** | 長時間停止・再開や複数tabで、他者／他tabの新成果を黙って失わない | conflict時は新しいbundleへ旧操作を自動再送・自動mergeしない。利用者が比較して再実行する |
| **データ設計** | server-owned revisionをbundle payloadと分離し、tenant＋journey内で単調更新する | payload内部digestやtenant session versionをrow revisionへ流用しない。別tenantのrevision値を存在確認に使わせない |
| **機能設計** | GET→If-Match付きPOST/DELETEをatomic CASにし、欠損428・不一致409へ閉じる | resource lookup前のtenant session guardを維持し、その後resource CASを行う。conflict responseへ本文や現在ETagを不要に反射しない |

## 受入条件

- [ ] AC-1: create、同一内容再保存、update、delete、missing resource、concurrent updateのprecondition semanticsが決定される。
- [ ] AC-2: GETがserver-owned ETagを返し、update/deleteは`If-Match`欠損を428、不正・複数・wildcard・不一致をstableな409/422へfail-closedにする。
- [ ] AC-3: update/deleteが`tenant_id + journey_id + expected revision`の単一atomic文で確定し、事前SELECTだけのcheck-then-writeにしない。
- [ ] AC-4: 同じ旧revisionを使う2 workerの同時updateは一方だけ成功し、敗者がpayload、監査、revisionを変更しない。
- [ ] AC-5: delete確認後に更新されたbundleを古いDELETEが削除せず、削除成功時だけcontent-free監査を同一transactionへ追加する。
- [ ] AC-6: frontendは409を新しいbundleへの自動retry／mergeへ倒さず、旧画面を操作可能な成功状態として扱わない。
- [ ] AC-7: tenant A/Bに同じjourney IDとrevisionを作り、ETagを知っていても越境read/update/deleteできない。
- [ ] AC-8: SQLiteと全Verified server DBでmigration往復、atomic CAS、connection pool再利用、backup/restoreが通る。
- [ ] AC-9: API文書、frontend/backend client、E2Eが同期し、offline/local-only bundle I/Oは既存どおり動作する。

## 非目標

- serverがopaque InquiryBundleV1をmergeしない。
- conflict時に最終書込優先や自動retryを既定にしない。
- Document ETag、tenant session version、revision DAG head versionを共通counterへ統合しない。
- per-roundの部分更新APIを同時導入しない。

## 検証計画

- 2 session／2 DB connectionで同じexpected revisionを使う競合integration test。
- update対delete、delete対update、同一内容update、再送、rollbackのmatrix。
- tenant A/B同一ID・同一revision negative test。
- frontendで409後に保存成功表示、download、画面破棄が発生しないE2E。

