# Issue: SEC-HTTP-01 provision_userの必須文字列空チェックが400、他は422

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/admin.py`
- Related ADR/Spec: `02_Architecture/api.md` §4, §9.3
- Expected verification level: `unit`

## 課題

- 現在の問題: `routes/admin.py:97-99`（`POST /admin/provision/users`）は、`provider`/`externalUid`が空文字列の場合に`status_code=400`を返す。一方、同種の「必須文字列フィールドがtrim後に空」という検証失敗は、`routes/ai.py:70-72`（`narrativeText`）・`ai.py:288-289`・`routes/ai_relations.py:101-102`（`Summary text`）ではすべて`422`を返しており、リポジトリ全体でこの`admin.py`の1箇所だけが`400`である。
- 判断が必要な理由: `02_Architecture/api.md` §9.3（`POST /admin/provision/users`の契約）は`2xx`/`403`/`409`の3分岐のみを規定し、400分岐は文書化されていない。一方、同じ`api.md` §4（エラー設計の一般方針）は「入力スキーマ不正 → 400」「A1契約フィールドやenumなどの契約違反 → 422」という一般ポリシーを定めており、これによれば必須フィールドの空文字列チェックはむしろ400が正しく、`ai.py`/`ai_relations.py`側の422が一般ポリシーからの逸脱である可能性がある。どちらの方向に揃えるべきかは、§4の一般方針と§9.3個別契約のどちらを優先するかというドキュメント/コードの整合判断が必要で、機械的に決められない。
- 利用者または開発への影響: クライアント実装者が「必須フィールド空」エラーのステータスコードをエンドポイントごとに個別対応する必要がある。実害はまだ顕在化していない。

## 対応方針

- 実施すること: `api.md` §4の一般方針と§9.3個別契約のどちらを正とするか、または両方を明確化する形で決定し、`admin.py`と`ai.py`/`ai_relations.py`のいずれかをもう一方に揃える。
- 実施しないこと: `admin.py`の`400`を`422`へ機械的に置き換えること。§4の一般方針を確認せずに多数派（422側）に揃えると、ドキュメントの一般方針と矛盾する可能性がある。

## 受入条件

- [x] `api.md` §4と§9.3の関係が明確化される。→ §4のtaxonomyを明文化（400＝トランスポート/パース境界のみ、422＝ドメイン契約違反＝必須フィールド空・enum・operation/command不一致等）。§9.3のprovision_users契約は2xx/403/409のみ規定で400/422とも非文書化のため、どちらへ揃えても文書契約を壊さない。
- [x] `admin.py`と`ai.py`/`ai_relations.py`が同じステータスコード規約に揃う。→ **422へ統一**（2026-08-15・仮承認）。ai.py `narrativeText must not be empty` 等と同一クラス。`admin.py:142` の `provider and externalUid must be non-empty` を 400→422 へ変更。

## 対応記録（2026-08-15・iteration 38）

- 判断: §4の「入力スキーマ不正→400」と既存多数派の「必須フィールド空→422」の矛盾は、**400はトランスポート/パース境界のみ**とtaxonomyを整理して解決。Pydantic body validation の既定が FastAPI では422である点も§4に明記。
- `routes/admin.py:142`: provision_users の必須文字列空チェックを 400→422 へ変更（コメントでSEC-HTTP-01根拠を明記）。
- `api.md` §4: taxonomy追記＋SEC-HTTP-01注記（IdP登録系の `unsupported_protocol`/`invalid_jwks_uri` は構造化コードを持つ別クラスとして400のまま・将来標準化対象）。
- テスト: `test_auth_jit_provisioning.py` の blank_provider / blank_external_uid アサーションを 400→422 へ更新。`test_auth_jit_provisioning.py` 19 pass・`test_control_plane_authorization.py` 31 pass・docs-check pass。

## 検証計画

- 実行する確認: 対応後、`python3 -m pytest`（backend、該当route）。
- 期待結果: 既存のprovisioning/narrative関連テストが新しい規約と整合する。
- 実績（2026-08-15）: 上記の通り。ai.py/ai_relations.py は変更不要（既に422）。

## 補足

- 発見経緯: 第12ラウンドの棚卸し（HTTPステータスコード一貫性観点）で発見。当初は「422へ揃えるだけの機械的修正」と評価したが、検証フェーズで`api.md` §4の一般方針が実は400を支持し得ることが判明し、判断が必要な項目へ格下げした。
