# Issue: PGM-ITER-05-03 組織IdP外ゲスト受入プリミティブの要求確定

- Type: Design / Security
- Status: Open
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html` §18（Maintainer直接指示、2026-08-25）, `01_Plans/issues/done/issue-PGM-ITER-05-02-cross-tenant-sharing-external-comparison.md`（外部比較調査）
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/adr/`（新規ADR候補）, `03_Implement/backend/src/kj_atlas_api/tenant_context.py`, `03_Implement/backend/src/kj_atlas_api/models.py`（`tenant_identity_providers`・新規テーブル候補）
- Related ADR/Spec: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`, `01_Plans/adr/ADR-0080-idp-independent-guest-admission-primitive.md`, `02_Architecture/cross-tenant-sharing-external-comparison-2026-08-25.html`
- Expected verification level: `integration`

## 課題

`issue-PGM-ITER-05-02`（組織境界を越えた共有パターンの外部比較調査）完了の直後、Maintainerから実運用フィードバックを待たずに直接、次の4要求が確定要求として示された（`post-mvp-business-scope-design-program.html` §18）。

1. 組織間だけでなく、小規模の**個人間**利用もサポートする。
2. 行政・企業等が、市民や外部協力者のような**組織IdP外のユーザー**を受け入れられる。
3. 組織IdP外ユーザーの受付可否を、**テナント全体より詳細な単位**で制御できる。
4. **既定は拒否**。既定の共有対象ドキュメントは**0件**。

現行の`resolve_verified_claim_tenant_context()`（`tenant_context.py`）は`tenant_identity_providers`が(tenant, IdP)単位でactiveであることだけを要求する、単一の粗い信頼プリミティブしか持たない。要求2は既存の三要素分析（§15.1・§15.2）の射程を超える——これまでの分析は「別テナントのIdPを個人単位で信頼する」プリミティブを前提にしていたが、要求2は**IdPそのものを持たない個人**を対象に含む。

## 対応方針

- 実施すること:
  1. 上記4要求を確定した受入条件として本issueに固定する（既に確定済みであり、再検討の対象ではない）。
  2. `AGENTS.md` §1.1（三要素牽制設計法、`ADR-0067`）に従い、業務設計・データ設計・機能設計の三次元から、IdP認証を経由しない個人単位の招待・許可プリミティブを分析する。着工前チェックリスト（`02_Architecture/three-element-constraint-checklist.html`）を通す。
  3. 三要素分析の結果を新規ADRとして起票し、Maintainerの承認（Accepted）を経てから実装に着手する。
- 実施しないこと:
  1. 三要素分析・ADR化を経ないプリミティブの実装。
  2. 4要求自体の再検討・縮小（Maintainerが確定要求として直接指示したものであり、本issueの論点は「どう実現するか」であって「実現するかどうか」ではない）。

## 論点（三要素分析で扱うべき問い、本issueでは未確定）

- **個人単位の信頼レコードの形**: `tenant_identity_providers`のような(tenant, IdP)単位ではなく、(tenant, 招待された個人, 対象ドキュメント/範囲)単位の新しいテーブルが必要になる可能性が高い。Google Workspaceのtrust rules（ドメイン単位 or 個人アドレスを含むグループ単位を条件として選択可能）が参考になる先例。
- **IdPを持たない個人の認証方法**: 招待された個人がkj-atlasにログインする手段そのものが無い（現行はSaaS向けtrusted auth edgeがIdP発行JWTを前提とする）。Notionのメール招待＋リンク経由の暗黙受諾、GoogleのVisitor Sharing（Googleアカウント不要な一時アクセス）、Slackのゲストアカウント（個人単位、IdP不問）のいずれかに類する、新しい認証経路の要否を判断する必要がある。
- **既定拒否・既定ゼロ件の実装位置**: 新しい招待レコードが作成された瞬間から「その個人がアクセスできるドキュメントは明示的に追加されたものだけ」であることを、データ設計（既定値）と機能設計（認可チェックの順序）の両方で保証する必要がある。
- **取り消し・失効**: `issue-PGM-ITER-05-02`の調査（Microsoft Entra B2Bの知見）によれば、リソース側テナントが招待した個人のアクセスを、相手側の状態と無関係に単独で取り消せることが望ましい。

## 受入条件

- [x] AC-1: 上記4要求への対応方針が三要素分析（`ADR-0067`）で決定され、着工前チェックリストを通過する。— 2026-08-25、`ADR-0080`（Proposed）とこのADRを反映した`post-mvp-business-scope-design-program.html` §19、`three-element-constraint-checklist.html`の適用記録を参照。D1（ゲスト本人確認）・D2（信頼レコードの形）・D3（既定拒否・既定ゼロ件の保証層）・D4（取り消しの独立性）の4論点を、基本チェック・クロスチェックを通した三要素分析として決定した。
- [ ] AC-2: 決定内容が新規ADRとして起票され、Maintainerの承認（Accepted）を得る。— **部分**: `ADR-0080`として起票済み（起票はAC-1と同時に完了）。Maintainerの承認（Accepted）は未実施のため、本ACは未チェックのまま維持する。
- [ ] AC-3: ADR承認後、個人単位・IdP不問の招待・許可プリミティブが実装され、既定拒否・既定ゼロ件がintegration testで固定される。— `ADR-0080`がAcceptedになるまで着手しない（本issue「実施しないこと」）。
- [ ] AC-4: 招待の取り消し・失効が、相手側（招待された個人の状態）と無関係にテナント側から単独で実行できることがtestで固定される。— AC-3と同様、ADR Accepted後。

## 検証

- `python 01_Plans/docs_check.py`
- ADR承認後の実装に対する`cd 03_Implement/backend && python -m pytest`（該当領域）
