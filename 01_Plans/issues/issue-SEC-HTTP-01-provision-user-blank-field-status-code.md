# Issue: SEC-HTTP-01 provision_userの必須文字列空チェックが400、他は422

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
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

- [ ] `api.md` §4と§9.3の関係が明確化される。
- [ ] `admin.py`と`ai.py`/`ai_relations.py`が同じステータスコード規約に揃う。

## 検証計画

- 実行する確認: 対応後、`python3 -m pytest`（backend、該当route）。
- 期待結果: 既存のprovisioning/narrative関連テストが新しい規約と整合する。

## 補足

- 発見経緯: 第12ラウンドの棚卸し（HTTPステータスコード一貫性観点）で発見。当初は「422へ揃えるだけの機械的修正」と評価したが、検証フェーズで`api.md` §4の一般方針が実は400を支持し得ることが判明し、判断が必要な項目へ格下げした。
