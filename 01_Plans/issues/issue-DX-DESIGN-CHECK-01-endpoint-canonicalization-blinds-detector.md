# Issue: DX-DESIGN-CHECK-01 エンドポイント正規化が過剰で、実装42ルート中26本を検査不能にしている

- Type: Bug / Process
- Status: Open
- Source Issue: `DX-DOC-08`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/check_design_consistency.py`, `01_Plans/issues/issue-DX-DOC-08-api-md-endpoint-coverage-gap.md`, `AGENTS.md` §1.3
- Related ADR/Spec: `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`, `01_Plans/adr/ADR-0075`（L2昇格判定）
- Expected verification level: `unit`

## 課題

`check_design_consistency.py` の警告は 139 → 41 → 1 件へ削減された（`aa70d3cf` ほか）。削減の一部は api.md への実エンドポイント追記という**正しい対応**だが、同時に導入された正規化・除外ロジックが過剰で、**検出器が実装ルートを区別できなくなっている**。

### 実測（2026-08-12、`routes/*.py` から抽出した実装ルート42本に対して）

| 区分 | 件数 |
|---|---|
| 実装ルート総数 | 42 |
| `_is_external_or_wildcard()` で**検査対象外**となるもの | 3 |
| 正規化で他ルートと**衝突し区別不能**になるもの | 23（6グループ） |
| **個別に検証できないルート合計** | **26 / 42（62%）** |

衝突グループ（抜粋）:

| 正規化後 | 実ルート数 | 例 |
|---|---|---|
| `POST /ai/{param}` | **10** | `/ai/refine-card-text`, `/ai/detect-contradiction`, `/ai/generate-narrative` … |
| `POST /docs/{param}` | 4 | `/docs/{doc_id}/context-audit`, `/docs/{doc_id}/export-audit` … |
| `GET /docs/{param}` | 3 | `/docs/{doc_id}`, `/docs/{doc_id}/similar-candidate-groups` … |
| `GET /{param}` | 2 | `/inquiry-bundles/{journey_id}`, **`/tenant-admin/document-access/{doc_id}`** |

検査対象外の3本: `POST /bundle`, `POST /bundles:resolve`, `POST /query`。

### 原因は2つの独立した規則

**(1) `_CONCRETE_ID_RE` がハイフン語すべてを `{param}` へ潰す**

```python
_CONCRETE_ID_RE = re.compile(r"([a-z][a-z0-9]+(?:[-_][a-z0-9]+)+)")
```

意図は「テストfixtureの具体ID（`e2e-qa-roundtrip` 等）をプレースホルダ化する」ことだが、**ケバブケースのパスセグメントと区別がつかない**。kj-atlas のAI系エンドポイントは全てケバブケースであるため、`/ai/*` 10本が1つに潰れる。`/tenant-admin/document-access/{doc_id}` は両セグメントがケバブケースのため `GET /{param}` まで縮退する。

**(2) `_is_external_or_wildcard()` がスラッシュ1個以下のパスを一律除外する**

```python
stripped = path.rstrip("/")
if "/" not in stripped or stripped.count("/") <= 1:
    return True
```

意図は「`/ai/` のようなコレクション参照・将来参照を弾く」ことだが、**単一セグメントの実エンドポイントも巻き込む**。

## なぜ重要か（2つの判断の根拠を無効化している）

**(a) `DX-DOC-08` の受入条件2の証拠が成立しない。** 同issueは「全実装済みバックエンドルートがapi.mdに文書化されている」を「route_docs警告0件」で満たしたとしてDoneにしている。しかし `/ai/*` が10本まとめて1つに見える以上、**api.mdに1本書けば10本が網羅済みと判定される**。0件は網羅の証明になっていない。

**(b) `AGENTS.md` §1.3 のL2昇格条件①「設計整合警告50件未満」が、検出能力の低下によって部分的に満たされている。** 昇格判定（`ADR-0075`）はこの指標を根拠の一つにしている。指標そのものが無効というより、**指標が「api.mdの網羅性」ではなく「チェッカーの識別力」を測ってしまっている**状態である。

## 論点（人的判断が必要な理由）

正規化を単純に外すと 138 件の偽陽性が戻る可能性が高く、それでは `DX-DOC-08` 以前へ逆戻りする。**識別力を回復しつつ偽陽性を戻さない**設計が要る。以下は選択肢であり、どれを採るかは保守者判断とする。

- **案A: 正規化をパスパラメータ位置に限定する。** `{...}` プレースホルダのみを `{param}` 化し、`_CONCRETE_ID_RE` は廃止する。fixtureの具体IDは、比較対象を「設計文書中の参照」ではなく「実装ルート定義」に変えることで別途排除する。
- **案B: `_CONCRETE_ID_RE` を「最後のセグメントかつ既知の実ルートに一致しないもの」に限定する。** 実装ルート一覧を先に読み込み、実在するセグメントは正規化しない。
- **案C: 除外条件をセグメント数ではなく明示allowlistにする。** `_is_external_or_wildcard` のスラッシュ数ヒューリスティックを廃し、外部IdP系prefixと `*` を含むものだけを除外する。

いずれの案でも、**検出器の識別力そのものを守る回帰テスト**（下記受入条件3）を同時に入れることを推奨する。

## 受入条件

- [ ] AC-1: 実装ルート42本のうち、正規化後に他ルートと衝突するものが0件になる（`/ai/*` の10本が個別に判定される）。
- [ ] AC-2: `_is_external_or_wildcard()` によって実装ルートが除外されない（現状3本を0本にする）。外部IdP系（`/oauth/`, `/saml`, `/.well-known/`）とワイルドカードのみ除外する。
- [ ] AC-3: **検出器の識別力を守る回帰テストを追加する。** 既知の相異なるエンドポイント集合（最低でも `/ai/*` 全10本）を与え、正規化後も全て相異なることをアサートする。この検査があれば、将来の正規化強化が識別力を落とした時点でCIが落ちる。
  - **進捗**: `tests/test_design_consistency_discrimination.py` を追加（LIVE の `_PARAM_TOKEN_RE`/`_CONCRETE_ID_RE` をソースから読んで検証。実装 `/ai/*` 9本が `1` キーへ潰れることを確認）。現状は検出器が欠陥のため **xfail(strict=False)** — 案A/B/C の修正が入ると XPASS になり、その時点で un-xfail してCIガード化する。
- [ ] AC-4: 修正後の警告数を実測し、`DX-DOC-08` の受入条件2を**再検証**する。api.md未記載のルートが見つかった場合はそれを記録する（`DX-DOC-08` をReopenするか後続issueを立てるかは保守者判断）。
- [ ] AC-5: `02_Architecture/design_consistency_baseline.json` の `total_warnings` を修正後の実測値へ更新する。

## 検証

- `python 03_Implement/backend/scripts/check_design_consistency.py --baseline ...` の警告数を修正前後で比較する。
- 本issue記載の衝突計測を再実行し、衝突グループ0件を確認する。
- backend全体回帰（スクリプト変更のみのため影響は限定的だが、CIのDocs contractジョブが通ることを確認する）。

## 補足

- 発見経緯: ドッグフーディング状況確認の一環で、L2昇格を支える4指標の妥当性を検証した際に発見した。他の3指標（三要素検証76/76、実API検証2/2、コード生成成功率）は**内容を確認した上で妥当**と判断している。特に `codegen_results.md` は「これは骨格生成成功率でありL3基準を完全には表さない」と自ら限界を明記し、重複コード生成を失敗として計上し直しており、記録の誠実性は高い。本issueは指標全体への疑義ではなく、1つの検出器に限定した欠陥の指摘である。
- `check_contract_drift.py` の「11→2」削減（router prefix解決）は本issueでは未検証。同種の識別力低下がないか、AC-3の回帰テストを入れる際に併せて確認することを推奨する。
