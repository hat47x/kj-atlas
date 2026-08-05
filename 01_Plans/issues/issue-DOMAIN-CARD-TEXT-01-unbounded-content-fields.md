# Issue: DOMAIN-CARD-TEXT-01 主要コンテンツfieldに文字数上限がない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/frontend/src/domain/validate_doc.ts`
- Related ADR/Spec: `02_Architecture/schemas.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: このコードベースは監査・セッション関連fieldを一貫して文字数上限で境界づけている（`audit.py`の`MAX_AUDIT_IDENTIFIER_LENGTH`等、`models.py`の`RelationSummary.text`は`Field(max_length=RELATION_SUMMARY_TEXT_MAX_LENGTH)`）。一方、同じ`models.py`内の主要コンテンツfield — `Card.text`、`Island.title`/`summaryText`、`Narrative.text`/`title`、`EvidenceLink.note`、`MergeSuggestion.mergedTextDraft` — にはいずれも`max_length`が指定されていない（`grep max_length 03_Implement/backend/src/kj_atlas_api/models.py`でヒットするのは`RelationSummary.text`関連の1箇所のみ）。frontend側の`validate_doc.ts`も非空・trimの確認のみで文字数上限は確認していない。
- 利用者または開発への影響: 極端に長い文字列を持つ文書が保存・共有された場合、他のfieldが持つ境界保護（監査ログの肥大化防止、HTTP転送量の制限等）と一貫しない挙動になる。ただし、この資料型ツールの性質上「長い引用・議事録の丸ごと保持」が正当な用途であり得るため、適切な上限値そのものは製品判断を要する。

## 対応方針

- 実施すること: `Card.text`等の主要コンテンツfieldに、この用途に見合った`max_length`を設定するかどうか、設定する場合の具体的な値をMaintainerが判断する。
- 実施しないこと: 本issueでは具体的な上限値を提案・実装しない。上限値の選定はUXへの影響（ユーザーが正当に長い引用を貼り付けるユースケースを壊さないか）を伴う製品判断であり、コーディングエージェントが独断で決めるべきではない。

## 受入条件

- [ ] 各主要コンテンツfieldについて、上限を設けるか・設けないかの方針が明文化される。
- [ ] 上限を設ける場合、backend Pydanticモデルとfrontendの`validate_doc.ts`が同じ上限を適用する。
- [ ] 既存の正当なドキュメント（長い引用等）を破壊しないことを確認する。

## 検証計画

- 実行する確認: 方針決定後、`python3 -m pytest tests/`と`npx vitest run`で新規テストがgreenであることを確認する。
- 期待結果: 上限値が決定・実装された場合、上限超過時にbackend/frontend双方が一貫してvalidationエラーを返す。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸しで、監査・セッション系fieldの境界づけパターンとの非対称性として発見。セキュリティ上の既知の脆弱性ではなく、一貫性・DoS耐性の観点からの改善余地。
