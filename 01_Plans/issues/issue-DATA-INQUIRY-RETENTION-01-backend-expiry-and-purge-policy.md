# Issue: DATA-INQUIRY-RETENTION-01 探究bundleの保持期限・expiry・purge契約

- Type: Architecture / Data / Operations
- Status: Draft
- Source Issue: `DOMAIN-W-ITERATION-01` AC-11
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/database_content_store.py`, `03_Implement/backend/src/kj_atlas_api/routes/inquiry_bundles.py`, migration、purge runner、運用文書
- Related ADR/Spec: `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`, `02_Architecture/inquiry_journey_model.html` §4.3
- Expected verification level: `integration`

## 課題

tenant-scopedな探究bundle保存、読取、探究全体削除、本文を含まない削除監査は実装済みである。しかし保持期限、期限後のread/write挙動、purge実行主体、legal hold相当の保持、失敗時再試行が未定義・未実装である。

backendはbundleをopaque JSONとして保存するため、payload内の日時・stage・個人情報有無から保持期限を推測してはならない。現行rowは`tenant_id`、`journey_id`、`payload_json`、`updated_at`しか持たず、期限切れと単なる長期停止を区別できない。現在の削除監査も利用者による`inquiry_bundle.delete`／`deleted`だけを許すため、自動purgeを同じ意味で記録できない。

## 決定が必要な点

### D1: 保持方針の供給元

- 案A: 自動期限を導入せず、利用者／tenant管理者の明示削除だけを正式機能とする。
- 案B: tenant policyがdefault retentionをserver-sideに決め、保存時に`expires_at`とpolicy versionをsnapshotする。
- 案C: bundleごとに利用者が期限を選ぶ。ただし自由入力、権限、最低／最大期間、共有・監査との整合が必要になる。

実利用・法的要件が無い現段階では案Aが最小で安全である。自動期限が必要と確認された場合は案Bを優先候補とし、client payloadやrequest自由入力を正本にしない。Maintainerが判断するまでpurge jobを実装しない。

### D2: expiry後の状態

- readを404へ偽装するか、410等のstable expiry応答にするか。
- 同じ`journey_id`の再保存を新規作成として許すか、purge完了まで拒否するか。
- expiry判定とrow削除を同一requestで行わず、`active -> expired -> purging -> deleted`等の明示状態を持つか。

### D3: 保持例外

- legal hold、incident preservation、利用者pinを導入するか。
- tenant停止・membership停止・利用者削除要求と保持例外の優先順位。
- backup、replica、export済みfileに対する削除保証の範囲。

## 三要素牽制

| 次元 | 必要な判断 | 他次元への制約 |
|------|------------|---------------|
| **業務設計** | 誰が期限を決め、誰が明示削除・保持例外・再試行を実行できるか | UIは「画面から消えた」と「物理削除完了」を混同しない。期限切れを品質や進捗判定に使わない |
| **データ設計** | expiry、policy version、状態、保持例外、最小監査metadataをserver-owned列として保持するか | payload本文やclient日時から期限を推測しない。監査へ本文・locator・digest生値を複製しない |
| **機能設計** | read/write/delete/purgeの状態遷移、CAS、batch上限、worker lease、失敗再試行を定義する | tenant境界とsession preconditionを先に検証し、別tenantや更新直後のbundleをpurgeしない |

## 対応記録（2026-08-14）

**D1 = 案A（自動期限を導入せず、利用者／tenant管理者の明示削除だけを正式機能とする）を採択した。**

- 根拠: 本issueが指摘する通り、実利用・法的要件が無い現段階では案Aが最小で安全。自動期限を導入すると期限判定・purge・保持例外・legal holdの設計が全て必要になり、未使用の機能へ設計を先行投資することになる。
- 採択の意味: 探究bundleは**明示DELETEまで永続**する。期限切れ・自動purgeは存在せず、read/write/deleteの状態遷移は現行のまま（`inquiry_bundle.delete`／`deleted`の本文なし監査のみ）。
- 将来、自動期限が必要と確認された場合は案B（tenant policyがdefault retentionをserver-sideに決め、保存時に`expires_at`とpolicy versionをsnapshot）を優先候補とする。その際は本issueのD2（expiry後の状態）・D3（保持例外）を再検討する。
- D2・D3（expiry後の状態・保持例外）は案Aでは**該当なし**（期限が存在しないため）。legal hold等の要件が出た時点で再訪する。

## 受入条件

- [x] AC-1: D1〜D3がMaintainerにより決定され、必要なら補足ADRがAcceptedになる。— **D1=案Aを採択**（上記対応記録）。D2/D3は案Aでは該当なしとして記録。補足ADRは不要（案Aは現行挙動の明文化であり、新規設計判断を含まない）。
- [x] AC-2: 自動期限を採る場合、server-owned `expires_at`、policy version、状態、保持例外がportableなORM/migration契約として定義される。自動期限を採らない場合は、その非保証をUI・API・運用文書へ明記する。— **案Aを採択**。非保証（明示DELETEまで永続・自動purgeなし）を api.md・frontend UI・運用文書へ明記した。
- [ ] AC-3: expiry直前の更新、明示削除、purge claimが競合しても、更新済みrowや別tenant rowを削除しない。
- [ ] AC-4: purgeはtenant-scoped、件数上限付き、冪等であり、失敗を成功扱いせず再試行可能な状態と本文なし監査を残す。
- [ ] AC-5: legal hold等を採る場合、通常expiryより優先してpurgeを停止し、解除権限と監査を固定する。
- [ ] AC-6: SQLiteと全Verified server DBでmigration往復、時刻境界、競合、pool再利用、tenant A/B negative testが通る。
- [ ] AC-7: backup／restore後もexpiry stateと保持例外が保存され、削除保証の対象外媒体が運用文書に明記される。
- [ ] AC-8: `DOMAIN-W-ITERATION-01` AC-11とsupport levelを実際の保証へ同期する。

## 非目標

- ラウンドやsnapshotだけを部分削除しない。Accepted契約どおり探究全体を最小完全削除単位とする。
- AIが保持期限、legal hold、削除例外を決めない。
- 不変DAGを理由に個人情報・機密情報の明示削除を拒まない。
- content-addressed revision GCと同じtable・状態機械へ統合しない。opaque inquiry bundleとrevision/blobでは参照構造が異なる。

## 検証計画

- clockを固定したexpiry境界unit test。
- tenant A/B、同一journey ID、更新対purge、delete対purgeのintegration matrix。
- migration upgrade／downgrade／upgradeと全Verified DB promotion contract。
- purge失敗後の状態、再試行、本文なし監査、batch上限の確認。

