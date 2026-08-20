# Issue: SEC-INQUIRY-BOUND-01 InquiryBundleV1にDocumentV1同等の所有者・可視性境界が無い

- Type: Security / Data model
- Status: Open
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html` §13.2（第4反復三要素分析で発見）, `01_Plans/issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md` AC-11
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`（`InquiryBundleRow`）, `03_Implement/backend/src/kj_atlas_api/routes/inquiry_bundles.py`, `01_Plans/adr/ADR-0073-document-ownership-and-lifecycle-model.md`（参照する既存モデル）
- Related ADR/Spec: `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`, `02_Architecture/inquiry_journey_model.html`, `01_Plans/adr/ADR-0073-document-ownership-and-lifecycle-model.md`, `01_Plans/issues/done/issue-SEC-DOC-BOUND-06-list-and-archive-bypass-visibility-and-capability.md`（同型の境界を`DocumentV1`側で実装した先例）
- Expected verification level: `integration`

## 課題

`post-mvp-business-scope-design-program.html` 第4反復（成果物の複数化）の三要素分析で、`InquiryBundleV1`
（`issue-DOMAIN-W-ITERATION-01`が実装した第2の成果物型）の backend 永続化に、第2反復（`ADR-0073`）が
`DocumentV1`へ確立した所有者・可視性・capabilityの境界が及んでいないことが判明した。

`InquiryBundleRow`（`03_Implement/backend/src/kj_atlas_api/models.py`）の主キーは`(tenant_id, journey_id)`
のみであり、`created_by`や`visibility`に相当する列が無い。`/inquiry-bundles/{journey_id}`のGET/PUT/DELETE
（`routes/inquiry_bundles.py`）はテナント境界のみを`_trusted_session`で確認し、journey_idの作成者以外の
同テナント利用者からのアクセスを区別しない。したがって**同一テナント内の任意の利用者が、journey_idを知る
（または推測する）任意の他利用者の探究bundleを読み書き削除できる**。

これは実装漏れではなく記録された意図的判断（`models.py`のdocstring: "backend deliberately does not
interpret the bundle contract"）だが、`issue-DOMAIN-W-ITERATION-01` AC-11 は「残る部分共有・履歴削除の
境界は未完了（別issueで追跡）」と明記しており、その追跡issueは実際には存在しなかった。本issueがその
追跡issueを起票する。

`local-dev`（単一利用者前提）ではリスクは小さいが、SaaS profile（同一テナントに複数利用者が属する）では
実質的な認可境界の欠落である。

## 対応方針

- 実施すること（三要素での判断）:
  1. **業務設計**: 探究bundleは「本人の思考の器」であり、他者の閲覧・編集を既定で許可すべきかを判断する
     （`DocumentV1`の既定=作成者所有と揃えるか、共同編集を前提に別の既定を設けるか）。
  2. **データ設計**: `InquiryBundleRow`へ`created_by`（不変事実）を追加するか、既存の
     `document_access_metadata`と同型の可視性列を追加するか、あるいは元の`DocumentV1`の可視性を
     継承する参照方式にするかを判断する。opaque payload契約（backendが内容を解釈しない）を維持したまま
     所有者だけを追加するのが最小変更になる可能性がある。
  3. **機能設計**: GET/PUT/DELETEへ`created_by`チェックを追加する場合、既存のCAS契約（ETag/If-Match）と
     どう両立させるか（`SEC-DOC-BOUND-06`の`_authorize_request`拡張と同型のパターンが使えるかを検討）。
  4. 判断結果をADRとして起票するか、`ADR-0057`/`ADR-0073`の補遺として記録するかを決める。
- 実施しないこと:
  1. 本issueでの実装（判断・設計のみ。方針確定後に別issueまたは本issueの続きで実装する）。

## 受入条件

- [ ] AC-1: 探究bundleの所有者・可視性の既定方針が三要素分析で決定される。
- [ ] AC-2: データ設計（列追加方式）が決定され、`ADR-0057`または新規ADRに記録される。
- [ ] AC-3: 決定に基づき、`/inquiry-bundles/*`の認可境界が実装され、backend testで
  他利用者からのアクセス拒否が検証される。

## 検証

- `python 01_Plans/docs_check.py`
- `cd 03_Implement/backend && python -m pytest`
