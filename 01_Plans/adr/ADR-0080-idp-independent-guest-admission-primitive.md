# ADR-0080: IdP不問・個人単位のゲスト受入プリミティブ

- Status: Proposed
- Date: 2026-08-25
- Deciders: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/tenant_context.py`, `models.py`（新規table候補）, `trusted_auth_edge.py`, `02_Architecture/schemas.md`, `02_Architecture/api.md`, `THREAT_MODEL.md`

## Context

`issue-PGM-ITER-05-03`は、Maintainerが2026-08-25に直接指示した4つの確定要求を扱う（`post-mvp-business-scope-design-program.html` §18）。

1. 組織間だけでなく、小規模の**個人間**利用もサポートする。
2. 行政・企業等が、市民や外部協力者のような**組織IdP外のユーザー**を受け入れられる。
3. 組織IdP外ユーザーの受付可否を、**テナント全体より詳細な単位**で制御できる。
4. **既定は拒否**。既定の共有対象ドキュメントは**0件**。

これらは再検討の対象ではない（同issue「実施しないこと」）。本ADRの論点は**どう実現するか**である。

コードで確認した事実: `resolve_verified_claim_tenant_context()`（`tenant_context.py:188-227`）は、verified claimの`tenant_id`に対して`tenant_identity_providers`が`(tenant, identity_provider)`単位でactiveであることを要求し、そこから`user_identities`（`identity_provider_id + subject`）経由でしか個人を解決できない。**IdPを持たない個人を表現する経路が構造的に存在しない。** `issue-PGM-ITER-05-02`（外部比較調査、`02_Architecture/cross-tenant-sharing-external-comparison-2026-08-25.html`）の結論（§0）は、比較した4製品のうち3製品（Slack・Microsoft・Google）が「組織単位の信頼」と「個人単位の信頼」を別々のプリミティブとして持ち、Notionは組織単位の信頼という概念自体を持たない、という点で一致することを示した。kj-atlasはこの4製品のいずれとも異なり、個人単位の信頼を組織単位の信頼から独立に表現できない。

## 決定すべき論点

- **D1**: IdPを持たない個人が、そもそもどう認証するか（ゲスト自身の本人確認手段）。
- **D2**: 個人単位の信頼レコードの形（テーブル設計）。
- **D3**: 既定拒否・既定ゼロ件を、どの層で構造的に保証するか。
- **D4**: 招待の取り消し・失効を、招待した側が相手の状態と無関係に単独で実行できる保証をどこに置くか。

## 選択肢

### D1: ゲスト本人確認の手段

`issue-PGM-ITER-05-02`の調査結果: Notionは招待リンクを開くだけで暗黙受諾（明示的な同意画面はない）。Googleのvisitor sharingはGoogleアカウント自体を要求しない一時アカウントを発行する。Slackのゲストアカウントはメールアドレス単位でIdPを介さない。

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **A** | メールアドレス宛の**単回・短命の署名付きリンク**（一度redeemすると無効化、期限切れも失効）。redeem時に`ADR-0074`が確立したserver-owned session境界と同じ形（`SaasAuthSessionRow`相当）で短命sessionへ交換する | 招待記録（メールアドレス＋招待ID）と紐づき、リンクの単回性を構造的に保証できる。既存のserver-owned session基盤を再利用できる | リンク転送されると転送先の人物がredeemできてしまう（Notionと同じ残存リスク。§検証で明示） |
| B | メールアドレス宛の**単回コード（OTP）を毎回入力**させ、リンクより検証段階を1つ増やす | リンク転送だけでは突破できない（コードも要る） | 実装・UXコストが増える。既存4製品の先例はいずれもここまでは要求していない |
| C | 招待された個人にも何らかの外部IdP（本人の個人Googleアカウント等、org IdPではない）でのログインを要求する | 既存のtrusted auth edge実装をほぼ流用できる | **要求2に反する**——Googleのvisitor sharingはGoogleアカウント自体を要求しない。「組織IdP不問」を「個人の外部IdPなら可」に縮小してしまい、IdPを持たない市民を排除し得る |

### D2: 個人単位の信頼レコードの形

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **A** | 新規`guest_invitations`（tenant_id, invitation_id, invited_email, status[pending/redeemed/revoked], created_by, created_at, expires_at, redeemed_guest_principal_id）と`guest_document_grants`（tenant_id, guest_principal_id, doc_id, granted_by, granted_at, revoked_at）を追加。既存の`tenant_identity_providers`・`user_identities`とは独立 | 「テナント全体のIdP信頼」と「個人単位・文書単位の信頼」が構造的に別テーブルになり、要求2・3が求める分離をデータ設計そのもので表現できる。`ADR-0073`のD1（`created_by`は不変事実）と同型のパターンを再利用できる | 新規テーブル・新規migrationが要る |
| B | `tenant_identity_providers`に「IdPなし」を表す特殊行を許容する | 新規テーブル不要 | **却下**。「テナント単位の全体信頼」を表すテーブルの意味を「個人単位・文書単位の信頼」に上書きすることになり、要求2・3が指摘した粒度混在の欠陥を別の場所で再生産する |
| C | ゲストを通常の`UserRow`＋`TenantMembershipRow`（`membership_kind=guest`フラグ付き）として表現する | 既存のmembership解決経路を流用できる | **却下**。`list_active_tenant_summaries`等、既存コードは`TenantMembershipRow`の存在を「そのテナントに（何らかの形で）所属する」の意味で使っている。ゲストをここに混ぜると、文書単位の絞り込みを後付けし忘れた経路がテナント全体相当の可視性を暗黙に与えるリスクを生む（要求4のゼロ件既定に反する） |

### D3: 既定拒否・既定ゼロ件の保証層

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **A** | `guest_document_grants`に**一致する行がある場合のみ**アクセスを許可する構造的deny-by-default。ゲストprincipalに対して、tenant-wide fallbackや「その他の文書も見える」経路を一切実装しない。既存の`_require_active_tenant`・PostgreSQL RLSのfail-closed方針と同型 | 「見えるのは明示的に付与された文書だけ」がデータモデルの構造から導かれ、実装の見落としに依存しない | なし（既存方針との一貫性が高い） |
| B | capability/PDPのpolicy設定で既定拒否を表現する | 既存のcapability機構と統一的に扱える | 設定依存になり、`ADR-0062`が繰り返し指摘してきた「明示選択のfail-fast」ではなく「設定忘れがfail-open」になるリスクを再導入する |

### D4: 取り消し・失効の独立性

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **A** | `guest_document_grants.revoked_at`／`guest_invitations.status=revoked`は**招待した側のテナントだけが**書き込める状態遷移とし、ゲスト側の同意・応答を待たない。書き込み後は次回以降の全requestで即時反映（`ADR-0074`の`tenantSessionVersion`と同型のCAS更新） | `issue-PGM-ITER-05-02`が確認したMicrosoft Entra B2Bの先例（リソース側テナントが単独で無効化できる）と一致する | 既発行済みの短命session（D1）が期限切れまで残る可能性がある（Entraも同じ残存リスクを公式に認めている。§検証で明示し、隠さない） |
| B | 取り消しにゲスト側の確認応答を要求する | なし | **却下**。要求されている「相手側の状態と無関係に単独で取り消せる」に反する |

## Three-Element Verification（ADR-0067・着工前チェックリスト適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | CHK-B1: 現行は個人単位・IdP不問の受入journeyが構造的に不可能（「あったほうがいい」ではなく皆無）。CHK-B4: 招待できる利用者種別はテナント側の`document.write`または新設capabilityを持つ主体に限る（ゲスト自身に招待権限は与えない）。CHK-B5: ゲストの無効化（招待取り消し）時、当該ゲストが見ていた文書の可視性は即時失われる（D4） | データ: D2でtenant-wide信頼と個人単位信頼を別テーブルに分離することを要求する。機能: D3でdeny-by-defaultの構造化を要求する |
| **データ設計** | CHK-D1: 新規データの正本はサーバー（`guest_invitations`／`guest_document_grants`）であり、招待メールアドレス以外の秘密値（トークン本体等）はハッシュのみ保持する（既存の`session_key_hash`等と同じ方針）。CHK-D4: SafeMode ON時、ゲストへの表示はカードSafeMode制約を通常利用者と同様に適用する（本ADRはSafeModeの境界自体を変更しない） | 業務: D1のリンク転送残存リスクを、業務要件（招待は「特定の個人」宛の意図であり、転送は想定外の使用）として明記し、実装側の技術対策の限界を隠さない。機能: D2のテーブル設計がD3のdeny-by-default構造を可能にする前提を提供する |
| **機能設計** | D1=A（単回短命リンク→`ADR-0074`型session交換）、D2=A（新規2テーブル）、D3=A（構造的deny-by-default）、D4=A（招待側単独revoke、即時反映）の一貫した機能連鎖 | 業務: 既存のcapability/PDP経路とは別に、ゲストという新しい主体種別をtrusted auth edgeの外側（IdP検証を経由しない）に追加することになるため、既存の`VerifiedTenantClaim`ベースの経路とゲスト経路が混線しない境界（ゲストprincipalは`identity_provider_id`を持たない、という型レベルの区別）を要求する。データ: D4の即時失効が、D2のテーブルへの単純な状態更新で表現できることを要求する（複雑な連鎖更新を要さない） |

CHK-X1〜X6（次元間クロスチェック）: 業務要求（個人単位受入）はデータの非表示原則（SafeMode・文書本体の秘匿）を侵さない（ゲストも通常利用者と同じSafeMode制約を受ける）。データ境界クラス（新規2テーブル）は機能のCRUDサポートレベルと一致させる（招待発行・取消はテナント側write、ゲストの文書readは付与された`doc_id`のみ）。機能の状態遷移（pending→redeemed→revoked）は業務シナリオ（招待→受諾→利用→取消）の全経路をカバーする。

## 推奨（保守者の判断を拘束しない）

**D1=A、D2=A、D3=A、D4=A** を推奨する。

理由: D2=A・D3=Aは、`issue-PGM-ITER-05-02`が発見した「kj-atlasには個人単位の信頼を組織単位の信頼から独立に表現する経路がない」という欠陥を、データモデルの構造そのもので解消する。既存の`tenant_identity_providers`を流用する案（D2=B）は、粒度混在という同じ欠陥を別の場所で再生産するため推奨しない。D1=Aは、要求2（IdP不問）を字面どおり満たす最小の認証手段であり、D4=Aは要求されている取り消しの独立性と直接一致する。D1のリンク転送残存リスクはMicrosoft Entra B2B・Notionのいずれにも存在する既知のトレードオフであり、本ADRはこれを解消すると主張しない——短命期限とredeem後の即時失効で被害範囲を限定するに留める。

D1=Bはより安全だが、比較した4製品のいずれもここまでのUXコストを課していない。着工後の運用フィードバックで招待の誤送信・転送リスクが実際に問題化した場合、D1をAからBへ強化する余地は残す（本ADRはA→Bへの後日強化を禁じない）。

## Non-goals

- ゲスト側からの「相互の」共有（ゲストが自分のテナントへ相手を招く等）は対象外。本ADRは常にテナント側からゲスト個人への一方向の招待だけを扱う。
- ゲストに対するcapability体系の一般化（`tenant.provision`等の既存capabilityとの統合）は対象外。ゲストの権限は「付与された`doc_id`集合への読み書き」のみとし、他のcapabilityとは独立に扱う。
- ゲストの組織的な一括管理（CSVインポート、SCIM等）は対象外（`ADR-0039`の個人OSS・プレリリース段階の対応外）。
- ライブ共同編集の並行性モデル自体の変更は対象外（`ADR-0076`が既に決定済み。本ADRはその適用対象にゲストprincipalを含めるかどうかを新たに決定しない）。

## Traceability

- Implementation: `01_Plans/issues/issue-PGM-ITER-05-03-cross-tenant-guest-admission-primitive-requirements.md`
- Related: `02_Architecture/cross-tenant-sharing-external-comparison-2026-08-25.html`（外部比較調査。D1〜D4の各選択肢の先例根拠）
- Related: `02_Architecture/post-mvp-business-scope-design-program.html` §15・§18（三要素分析の先行部分・確定要求の記録）
- Related: `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`
- Related: `01_Plans/adr/ADR-0073-document-ownership-and-lifecycle-model.md`（D2=Aが再利用する「不変事実としての`created_by`」パターンの先例）
- Related: `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（session-binding。D1=Aが再利用するserver-owned session交換パターンの先例）
- Related: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`（tenant境界の正本。ゲストprincipalはこの境界の外側の新しい主体種別として追加される）
