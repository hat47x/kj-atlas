# 運用（最小）


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。

## 0. 文書分類（DOC-OPS-05-11）

- Classification: **Improve external**（対外文書として改善しつつ維持）
- Audience: self-host 運用担当者 / PoC管理者 / 初見の技術検証担当
- Goal: 最小運用の再現手順（更新・確認・安全運用）を単体読解できる形で提供する
- Non-goal: 実装仕様の正本化、内部判断メモの公開、`03_Implement/*` の仕様変更
- Public boundary: 内部限定の環境固有情報（秘密鍵・閉域URL・個別障害記録）を除外し、公開可能な運用手順のみ記載する
- Outcome: 読者が「どの運用経路を選び、どこを確認すれば安全に運用継続できるか」を判断できる
- This document decides: 公開可能な最小運用runbook（起動/停止/確認/復旧の実行順序とGo/No-Go観点）。
- This document does not decide: セキュリティ制度設計の正本、組織固有の承認台帳、実装仕様の新規確定。
- Related: `04_Documentation/security.md`, `04_Documentation/e2e_testing.md`, `02_Architecture/runtime_parameter_registry.md`, `01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`

## DOC-OPS-05 統合同期メモ（2026-04-18）

- 連携 issue: `issue-doc-ops-05-06` / `issue-doc-ops-05-11` / `issue-doc-ops-05-13` / `issue-doc-ops-05-14`
- canonical 用語: `Security Officer / System Owner / Platform Operator`
- canonical 状態語彙: `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed`（未確定時 `StoppedForClarification`）
- fixed values (D1〜D4): `4h / 2h / 代理承認なし / 48h + 15m/60m`
- 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md`（`operations.md` は runbook 同値確認先）

### 0.1 分類根拠（Audience / Goal / 公開境界）

- Audience適合: 具体コマンドと確認観点を中心に記述しており、外部運用者向け runbook として成立する
- Goal適合: Docker Compose / 代替運用 / 公開運用の境界が明示されており、再現可能性を満たす
- 公開境界: 鍵・内部URL・個人情報の固定値を置かず、公開可能なサンプル値（`<doc_id>` 等）に限定している

### 0.2 上流参照 / 下流適用

- 上流参照（正本）:
  - `02_Architecture/runtime_parameter_registry.md`（実行パラメータ）
  - `04_Documentation/security.md`（セキュリティ運用詳細）
  - `04_Documentation/e2e_testing.md`（E2E方針詳細）
- 下流適用:
  - 日常運用手順（バックアップ、更新、公開物配布、E2E確認）の実行runbook
  - docs-only 変更時の確認観点（links / 用語 / 公開境界）

### 0.3 Go/No-Go（docs-check）

- Go（公開改善を継続可能）:
  - Audience / Goal / Non-goal / Outcome が冒頭で判別可能
  - 正本リンク（runtime parameter registry, security, e2e）が有効
  - 実行手順がコピーペースト可能で、確認コマンドを含む
- No-Go（差し戻し）:
  - 内部限定情報（鍵、内部固有URL、未承認方針）が本文に混入
  - 上流正本と矛盾する運用既定値を本書で独自確定
  - 検証手順が欠落し、再現可能性が担保できない


## 0.4 AUTH-OPS-03 整合メモ（Context / Decision / Consequences）

### Context

- `02_Architecture/strict_mode_exception_approval_flow.md` で、strict mode 例外緩和の固定値 D1〜D4 が確定している。
- `04_Documentation/security.md` は安全境界の正本、`04_Documentation/security_operational_guidelines.md` はプロファイル選択ガイドの正本であり、本書は実行runbookに責務を限定する。

### Decision

- 本書（operations）は **実行手順とGo/No-Go判定** に集中し、承認フローの制度設計そのものは `02_Architecture/strict_mode_exception_approval_flow.md` を参照する。
- 役割語彙は `Security Officer / System Owner / Platform Operator` で統一し、承認（2者）と実行（Platform Operator）の分離を維持する。
- 固定値 D1〜D4（承認TTL=4h、最大2h、代理承認なし、48hレビュー+15m/60mSLA）を runbook の必須チェックとして扱う。

### Consequences

- 運用手順側での判断余地が縮小し、AUTH-OPS-03 と運用文書のドリフトを抑制できる。
- 公開runbookでも内部判断メモを持ち込まずに、再現可能な検証手順を維持できる。

## 0.5 Stream E 横断同期チェック（architecture -> security -> guidelines -> e2e + operations runbook整合）

本書は `02_Architecture/strict_mode_exception_approval_flow.md` を起点に **architecture -> security -> guidelines -> e2e** の固定順序で同期し、operations は runbook整合確認先として同時照合する。次の3点を満たす場合のみ Go とする。

1. 役割語彙が `Security Officer / System Owner / Platform Operator` に一致する。
2. strict mode 例外の状態遷移を
   `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed`
   （未確定時 `StoppedForClarification`）として参照し、別名を使う場合は同義と明記する。
3. 固定値 D1〜D4（4h / 2h / 代理承認なし / 48h + 15m/60m）を security/e2e と同値で保持する。

相違が1つでもあれば No-Go とし、D1〜D4 不整合ゼロになるまで修復する。修復は最大3回までとし、4回目相当は `StoppedForClarification` で停止する。


## 0.6 Phase6 Feedback Loop / KPI運用（Stream E）

Phase6の運用系文書（`issue-0019`, `issue-0020`, `issue-doc-ops-05-11`）と本書を同期する際は、**運用フィードバックとKPI監査を一本化** して次を固定する。

- Gate順序は **Gate C -> Gate D -> Gate E** のみ許可（逆順・並列判定は禁止）。
- Gate Dの必須入力は **測定日 / 対象文書 / 4KPI判定（TFS, Decision Readiness, Support Deflection, Feedback Closure） / 逸脱有無 / 次アクション / 反映先リンク**。
- evidence形式は **Date / Gate / Command / Result / Decision / Next action** の6項目を必須化。
- Gate E Proceed条件は **Go=記録確定後に進行、Conditional=再判定日+担当記録後に限定進行、No-Go=見送り理由+再判定日+担当記録まで停止**。
- KPIしきい値は承認済み台帳のみ有効とし、未承認変更は適用しない。
- 停止条件は **3回超過 / 前提崩れ / 未定義競合** の3項目を固定し、該当時は Proceed しない。
- 2026-04-13 Read同期（Stream E）で、Gate C→D→E の単一路線、scorecard入力契約、停止条件一致を再確認した。

## 0.7 Proceed（未解決点の委譲先）

本書（DOC-OPS-05-11）は公開運用runbookを主責務とし、以下は**未解決点として次Issueへ委譲**する。

- 委譲先: `DOC-OPS-05-13`（`04_Documentation/security.md`）
  - 委譲内容: 脅威分類の詳細、公開時の禁止事項一覧、セキュリティ既定値の背景説明。
- 委譲先: `DOC-OPS-05-14`（`04_Documentation/security_operational_guidelines.md`）
  - 委譲内容: プロファイル選択時の判断フロー、例外承認時の運用判断ガイド詳細。
- 本書で扱わない理由:
  - 重複責務回避（operations は「実行runbook」、security/guidelines は「安全方針と判断補助」）。
  - 文書間ドリフト防止（同一論点の正本を複数箇所で持たない）。

## 0.8 Known gap（DOC-OPS-05 / Stream E）

- Gap-1: 実運用の環境別チェックリスト（single-node / HA / air-gapped）は本書に未収載。
  - 理由: 具体構成ごとに前提が異なり、現行Issue（DOC-OPS-05-11）の docs-only スコープでは確定不可。
  - 委譲先: `01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md` の Proceed で次タスク化する。
- Gap-2: KPI しきい値の最新値は本書で固定しない。
  - 理由: 承認済み台帳が正本であり、本書に二重管理するとドリフトリスクが高い。
  - 委譲先: `01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`（Gate D/E の入力契約監査）。
- Gap-3: AUTH-OPS-03 の将来改訂時における差分追跡テンプレートは未定義。
  - 理由: 仕様変更の有無が未確定で、推測補完は行わない方針。
  - 委譲先: `04_Documentation/security_operational_guidelines.md` と連動する後続DOC-OPS issue。

### Phase6 固定フロー（Read → CDC → Plan → Execute → Verify(docs-check) → Proceed）

1. **Read**: 対象4文書を再読し、Gate契約・KPI契約の差分有無を確認する。
2. **CDC**: Context / Decision / Consequences を先に固定し、ADR衝突を解消する。
3. **Plan**: AC/DoDを固定し、KPI定義→監査指標→運用Runbook の直列化を宣言する。
4. **Execute**: Gate C -> Gate D -> Gate E の単一路線で実行し、運用手順と計測手順を同時更新する。
5. **Verify(docs-check)**: docs-check / 用語整合 / diff整合を実施し、修復は最大3回までとする。
6. **Proceed**: 次回測定サイクル条件を満たし、停止条件非該当の場合のみ引き渡す。

### Fail-safe（Phase6 / ADR衝突時のCDC化）

次のいずれかを検知した場合は、運用更新を停止し **CDC（Context / Decision / Consequences）として論点化** する。

1. KPI定義またはProceed条件が `ADR-0001` / `ADR-0019` / `ADR-0024` / `ADR-0028` と衝突。
2. 責務未定義（測定責任者/承認責任者の欠落）。
3. 未承認の閾値変更（承認記録なしのKPIしきい値改定）。
4. Gate順序が `C→D→E` 以外で記述される。
5. evidence項目欠落、または Command と Result が対応しない。
6. 停止条件（3回超過 / 前提崩れ / 未定義競合）に該当。

### 定点レビュー

- 次回定点レビュー: **2026-04-26 09:00 UTC**
- 担当: **Stream F（Unified Feedback & KPI Audit Owner）**

### 次回監査Runbook（Phase 1〜6固定）

1. **Phase 1 Read**: 対象4文書（`issue-0019` / `issue-0020` / `issue-doc-ops-05-11` / `operations.md`）を再Readし、Gate定義とKPI契約の差分有無を確認する。
2. **Phase 2 ADR明文化**: 上流ADR（`ADR-0001` / `ADR-0019` / `ADR-0024` / `ADR-0028`）に照合し、契約・停止条件を固定する。
3. **Phase 3 Plan**: KPI定義（4KPI）と監査スコアカードの AC / DoD を補完して固定する。
4. **Phase 4 Execute**: Gate C -> Gate D -> Gate E の単一路線で実行し、運用手順と計測手順を同時に更新する。
5. **Phase 5 Verify（docs-check）**: docs-check / 用語整合 / diff整合を実施し、修復は最大3回、4回目相当はFail-safe停止。
6. **Phase 6 Proceed**: 次回測定サイクル条件（Gate C完了、Gate D入力6項目、Gate E Proceed条件一致）を満たした場合のみ引き渡す。

## 0.9 責務境界（operations の単一責務）

### 対象読者
- Platform Operator（一次運用担当）
- System Owner（運用判断の最終責任者）
- PoC / self-host の初期導入担当

### 前提知識
- Docker Compose による起動・停止とログ確認ができること
- `security.md` が定義する安全境界（SafeMode既定ON、漏えい防止）を理解していること
- strict mode例外の制度設計は `02_Architecture/strict_mode_exception_approval_flow.md` が正本であること

### 公開してよい情報
- 日常運用Runbook（起動、停止、更新、確認、復旧）
- 運用者が再現できる最小コマンドとGo/No-Go観点
- 参照導線（security / guidelines / e2e へのリンク）

### 本書で扱わない情報（security / guidelines へ委譲）
- セキュリティ原則の詳細根拠、脅威分類、禁止事項一覧（`security.md`）
- strict / non-strict の採否判断フロー、例外判断の比較観点（`security_operational_guidelines.md`）

## 1. バックアップ / リストア

最小手順はバックエンド README を参照してください。

- [03_Implement/backend/README.md - Minimal backup / restore](../03_Implement/backend/README.md#minimal-backup--restore)

要点のみ:

- SQLite: API停止中にDBファイルをコピーして保全
- PostgreSQL: `pg_dump` / `pg_restore` を利用

## 2. 更新手順（Docker Compose）

1. 停止

```bash
cd /path/to/kj-atlas/03_Implement/deploy
docker compose down
```

2. 配布元の運用手順に従ってコードを更新

3. 再ビルド・起動

```bash
docker compose up --build -d
```

4. 確認

```bash
docker compose ps
docker compose logs api --tail=100
```

## 3. 運用上の注意

- 既定の `KJ_ATLAS_LLM_PROVIDER=none` では外部送信は行いません。
- ローカル/社内LLM利用時は `KJ_ATLAS_LOCAL_LLM_BASE_URL` を到達可能な内部URLに設定してください。
- 画面の JSON Export / Import を利用可能です。

### CE0 契約凍結の運用ゲート（Stream B）

- Query Preview bypass を禁止する（ContextQuery送信は Preview 経由のみ）。
- `ConsensusGraph` への direct write を禁止する（`patch + approval` 以外の更新禁止）。
- `mode=autonomous` でも proposal-only を維持する（auto-apply 禁止）。
- review state の自動昇格を禁止する（AIのみで `human_reviewed` へ遷移しない）。
- 監査4点セット（`query/bundle/proposal/apply`）が欠損した実行は成功扱いにしない。

Go/No-Go 判定（1行）:
- **Go** = 上記5条件がすべて成立。
- **No-Go** = 1条件でも不成立（SafeMode後退、auto-apply許容、review自動昇格兆候を含む）。


### Read-only 表示モード

- URL query で `readonly=true`（同義: `readOnly=1`, `isReadOnly=yes`, `mode=readonly`）を指定すると、Frontend は read-only モードで起動します。
- read-only モードでは編集系更新（カード/島/関係の更新、提案適用など）は保存されず、UI上でも編集操作は disabled 表示になります。
- 閲覧操作（パン/ズーム/検索/参照）は継続可能です。

### Polygon手動編集（FB-P2C-04）

- 対象: `shape.kind = "polygon"` の island。
- 操作: Side Panel の **Edit island boundary** をONにすると、頂点ハンドルを表示できます。
- 頂点移動: ハンドルをドラッグして移動（保存は pointer up 時に1回だけ確定）。
- 頂点追加: `Alt+Click` で辺上に頂点を追加。
- 頂点削除: `Alt+Click` で頂点を削除（ただし最小3点制約を維持）。
- 制約違反時（自己交差/最小頂点数未満）は操作を拒否し、直前の確定済み polygon を維持します。
- read-only モードでは編集チェックボックスは disabled となり、頂点ハンドルは表示されません。

### Bundle export の監査ファイル

- `Export bundle (.zip)` には `merge_decision_audit.json` が同梱されます。
- 本ファイルには merge decision の監査最小情報（`decisionId` / `groupId` / `decisionType` / `actorType` / `decidedAt` / `representativeCardId` / `sourceCardIds` / `missingSourceCardIds`）を含みます。
- 同一入力で同一出力となるよう、decision と cardIds は決定論順序で出力されます。
- `view.json` の `mergeAuditLog` / `reviewEvents` は export 前に `id` 単位で重複排除され、同一 `id` が複数ある場合は `createdAt` が新しいイベントのみ残します。

- `bundle_manifest.json` には `exportGranularity`（`overview` / `detail`）と `generatedAt` を記録します。
- `overview` は俯瞰用に selected-card trace（`evidence_trace_*` / `contradiction_trace_*` / `trace_analytics_*`）を同梱しません。
- `detail` は従来どおり selected-card trace を同梱できます（カード選択時）。

### 静的公開アーティファクト（FB-RM-PUB-03）

`index.html + assets + packs` の最小公開物を生成し、静的ホスティングだけで閲覧できる配布物を作成できます。

1. 生成コマンドを実行

```bash
cd 03_Implement/frontend
npm ci
npm run publish:static -- \
  --document ./tests/fixtures/worker/doc.small.json \
  --out ../deploy/public \
  --pack-id public-main \
  --title "Public sample"
```

2. 出力物を確認（最小構成）

- `03_Implement/deploy/public/index.html`
- `03_Implement/deploy/public/assets/*`
- `03_Implement/deploy/public/packs/index.json`
- `03_Implement/deploy/public/packs/public-main.document.json`

3. ローカル静的サーバで確認

```bash
cd 03_Implement/deploy/public
python3 -m http.server 4173
```

ブラウザで `http://localhost:4173/` を開くと、`pack=public-main&readonly=1` へ自動遷移して閲覧モードで表示されます。

4. 改ざん検知（SHA-256 + 署名）

- `publish:static` は `integrity.json` を自動生成し、公開物のハッシュ一覧を記録します。
- 署名を付与する場合は `--signing-key`（RSA private key PEM）と `--key-id` を指定します。

```bash
cd 03_Implement/frontend
npm run publish:static -- \
  --document ./tests/fixtures/worker/doc.small.json \
  --out ../deploy/public \
  --pack-id public-main \
  --title "Public sample" \
  --signing-key ./keys/publish-private.pem \
  --key-id ops-2026q1

node ./scripts/verify_artifact_integrity.mjs \
  --root ../deploy/public \
  --public-key ./keys/publish-public.pem \
  --key-id ops-2026q1
```

- 検証失敗時（hash mismatch / signature mismatch / key-id mismatch）は **配布停止（fail-safe）** し、再生成または鍵ローテーション手順へ進みます。


#### Visibility metadata 運用（FB-RM-PUB-01）

- `view.json` の `visibility` は `Public | Unlisted | Org | Restricted` のみ許可されます。
- 既存互換のため、`view.json` で未設定なら `Restricted` として読み込みます。
- `packs/index.json` の各packでも同じ enum を使い、未設定なら `Public` を補完します。
- `visibility` が存在する場合、enum外値（例: `FriendsOnly`）や型不正（`null`/number/object）は strict validation で拒否されます。
- 互換fallback（欠損時補完）と strict validation（不正値拒否）は責務を分離し、補完後に再exportすると `visibility` は必ず明示されます。
- invalid値（例: `FriendsOnly`）を含む `view.json` は検証エラーとして拒否されます。
- これらの metadata は公開意図の表示用途であり、SafeMode既定ON・read-only公開の既存制御は継続されます。

#### SafeMode / 公開モード整合

- 公開packを読み込んだときは Frontend 側で `safeMode=true` を強制します。
- 生成された `index.html` は `readonly=1` 付きURLへ遷移するため、公開配布物は編集不可の閲覧モードを既定にします。
- `packs/index.json` には `enforceSafeMode: true` / `readOnly: true` を記録し、公開配布の意図を明示します。

## 4. セキュリティ運用メモ（MVP）

- 公開時は API を直接公開せず、Nginx / Traefik などのリバースプロキシ配下で TLS 終端してください。
- イントラネット / VPN 境界での運用を前提にし、可能であれば IP 許可リストを設定してください。
- 迅速な保護が必要な場合は、プロキシ側 Basic 認証を有効化してください。
- API と DB はネットワークを分離し、DB ポートの外部公開を避けてください。
- 定期バックアップとパッチ適用を運用手順に含めてください。

詳細は [security.md](./security.md) を参照してください。


## 5. E2E動作確認ポリシー（運用必須）

`03_Implement/*` に変更が入る場合は、原則として `docker compose` による
`web + api + db` の連動確認を実施します（詳細は `ADR-0019` / `e2e_testing.md`）。

最小手順:

```bash
cd /path/to/kj-atlas/03_Implement/deploy
docker compose up --build -d
docker compose ps
curl -fsS http://localhost:8080/api/health
curl -fsS -X PUT http://localhost:8080/api/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8080/api/docs/<doc_id>

cd /path/to/kj-atlas/03_Implement/frontend
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
```

- 実行不能時（Docker未導入等）は、ブロッカー/代替検証/後続手順をPRに明記してください。
- 本運用は「テストが通っていてもE2E未確認ならリスクを明示する」ことを目的とします。
- 本節の内容は `04_Documentation/e2e_testing.md`（正本）と常に一致させます。

## 6. Docker未導入時の代替運用（SQLite + ローカル起動）

Composeが利用できない場合、以下で運用確認できます。

```bash
# terminal A: backend
cd /path/to/kj-atlas/03_Implement/backend
source .venv/bin/activate
export PYTHONPATH=src
export KJ_ATLAS_DATABASE_URL="sqlite:///./kj_atlas.db"
alembic upgrade head
uvicorn kj_atlas_api.main:app --host 0.0.0.0 --port 8000

# terminal B: frontend
cd /path/to/kj-atlas/03_Implement/frontend
npm run dev -- --host 0.0.0.0 --port 4173

# terminal C: checks
curl -fsS http://localhost:8000/healthz
curl -fsS http://localhost:4173/api/healthz
curl -fsS -X PUT http://localhost:8000/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8000/docs/<doc_id>

cd /path/to/kj-atlas/03_Implement/frontend
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
```

- `PUT /docs/{doc_id}` と `GET /docs/{doc_id}` を往復し、SQLite永続化も確認してください。
- この代替手順を利用した場合も、PR本文に実施コマンドと結果を記載します。




## Access Control Adapter 運用境界（FB-RM-PUB-04）

### 1. 責務境界（何を本体で実装しないか）

- KJ Atlas本体は `roles/groups/policyRef` を **入力として受け渡すのみ** で、RBAC/ABACの評価式を実装しません。
- 認可判定（allow/deny/readOnly/reason）の生成は外部 policy adapter（IdP/Policy Engine 側）の責務です。
- `visibility` は公開範囲ラベル用途であり、単独で認可可否を確定しません。

### 2. 環境変数

- `ACCESS_CONTROL_ADAPTER=noop|mock|external_http|<custom>`（既定: `noop`）
  - `noop`: 後方互換のため既定許可。
  - `mock`: 契約検証用。`x-policy-ref: mock:deny` / `mock:read_only` で決定論テストが可能。
  - `external_http`: OIDC/SAML運用環境の policy engine（PDP）へ POST 委譲。
  - 未知の値は `noop` へフォールバック（既存挙動維持）。
- `ACCESS_CONTROL_FAIL_SAFE_MODE=read_only|deny`（既定: `read_only`）
  - `Org/Restricted` で `policyRef` 欠損・不達・無効・adapter例外時に fail-safe を適用。
- `ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT`（任意）
  - `external_http` 選択時の委譲先URL。未設定時は `noop` へフォールバック。
- `ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS`（既定: `1.5`）
  - 外部 policy adapter 呼び出しの timeout 秒数。
- `ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE=none|oidc|saml`（既定: `none`）
  - adapter が policy engine へ通知する認証モード。
- `ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN`（任意）
  - PDP 経路で静的トークンが必要な環境向け。
- `ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER`（任意）
  - OIDC/SAML の issuer/entity ID を `x-idp-issuer` ヘッダで引き渡す。
- `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER=user_id|sso_subject`（既定: `user_id`）
  - `user_id`: `reviewerRef/ownerRef = user:<users.id>`（既存互換）。
  - `sso_subject`: `reviewerRef/ownerRef = user:sso:<provider>:<externalUid>`。subject欠損時は `actorRef` フォールバック。

### 3. 最小監査記録（PII非保存）

- 記録対象（最小）: `eventType`, `eventVersion`, `occurredAt`, `docId`, `action`, `decision_allow`, `policyRefPresent`。
- 任意記録: `decision_readOnly`, `decision_reason`, `visibility`, `adapterName`, `traceId`。
- 非保存: `roles/groups` 生値, `policyRef` 生値, ドキュメント本文。

### 3.1 AuthContext属性の監査取扱い（PII最小化）

- `amr/acr/aal/auth_time` はアプリDBへ保存しない。
- 監査へ出力する場合も生値は使用せず、次の正規化のみ許可する。
  - `hasStepUp`（boolean）
  - `assuranceLevel`（`low|substantial|high|unknown`）
  - `authAgeBucket`（`fresh|stale|unknown`）
- `roles/groups/policyRef` は外部照会入力であり、監査では `policyRefPresent` など存在フラグのみ扱う。

### 3.2 strict mode の例外承認責任（発動条件 / 停止条件 / 復旧条件）

参照正本: `02_Architecture/strict_mode_exception_approval_flow.md`（決定）、`04_Documentation/security.md` 8.1〜8.3（安全性チェック）。

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`は本番標準（strict）とする。
- 例外発動条件: 例外的に緩和する場合（`true` へ変更）は Security Officer + System Owner の2者承認を必須とする。
- 停止条件: D1〜D4 固定値のいずれかを満たせない場合は、Platform Operator は `StoppedForClarification`（確認待ちで停止）を記録し、適用を禁止する。
- Platform Operator 記録必須項目: 実施時刻・理由・承認者・対象環境・復旧条件。承認記録がない変更を禁止する。
- 復旧条件: 期限到来または停止条件成立時に `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ戻し、復旧時刻と検証結果を記録する。
- 違反時SLA: 15m以内に一次エスカレーション、60m以内に二次エスカレーションを実施する。
- backend 開発者はコードで一時バイパスを実装してはならない。

固定値サマリ（D1〜D4）:

| Decision ID | 固定値 | 運用上の必須アクション |
|---|---|---|
| D1 | Security Officer先行、承認TTL=4h | 4h以内に2者承認未達なら申請失効。 |
| D2 | tenant単位、最大2h | 2h到達時は `RollbackPending` へ遷移し strict 復帰。 |
| D3 | 復旧判定は2者共同、代理承認なし | 代理承認は常時不可、必要時は再申請。 |
| D4 | 変更台帳+監査ID相互参照、48hレビュー、15m/60mエスカレーション | 記録未完了のまま `Closed` へ遷移しない。 |

状態遷移（strict mode例外運用）:

- `DraftRequest`（申請作成）
  - 申請内容を作成し、承認審査へ進むと `ApprovalPending`。
  - 必須情報不足・固定値不一致がある場合は `StoppedForClarification`。
- `ApprovalPending`（2者承認待ち）
  - D1 の承認順序（Security Officer先行）で2者承認が揃うと `Approved`。
  - 承認TTL=4hを超過した場合は申請失効（再申請）。
- `Approved`（2者承認完了）
  - Platform Operator が適用した時点で `ActiveException`。
- `ActiveException`（一時緩和中）
  - D2 の最大2h到達時、または停止条件成立時に `RollbackPending`。
- `RollbackPending`（復旧待ち）
  - `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ復帰し検証完了で `Closed`。
- `StoppedForClarification`（確認待ちで停止）
  - 未確定事項が解消されるまで適用禁止。解消後は `DraftRequest` から再開。

### 3.3 strict mode例外 Runbookテンプレート（2者承認 + 実行記録）

> 本テンプレートは D1〜D4 固定値で運用する。逸脱時は `StoppedForClarification`（確認待ちで停止）へ遷移する。

#### A. 2者承認テンプレート（Security Officer + System Owner）

```markdown
- Request ID:
- DraftRequest at (UTC):
- Reason (業務/障害文脈):
- Target environment:
- Requested change: KJ_ATLAS_ALLOW_JIT_PROVISIONING false -> true
- Planned rollback condition:
- Planned rollback by (UTC):
- Security Officer approval: [Approved/Rejected] / Name / Timestamp(UTC)
- System Owner approval: [Approved/Rejected] / Name / Timestamp(UTC)
- Decision profile: D1-D4 compliant
```

#### B. Platform Operator 実行記録テンプレート

```markdown
- Executed at (UTC):
- Reason:
- Approvers (Security Officer + System Owner):
- Target environment:
- Rollback condition:
- Rollback executed at (UTC):
- Rollback verification result:
- Evidence links (ticket/change ledger):
- PII minimization check result:
- SafeMode/read-only integrity check result:
```

### 3.4 strict mode例外 事前/事後チェックリスト

- 事前チェック（実行前）
  - [ ] 2者承認が揃っている（Security Officer + System Owner）。
  - [ ] 必須記録5項目（時刻/理由/承認者/対象環境/復旧条件）をテンプレートに記入済み。
  - [ ] `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` を適用する対象環境を明示済み。
  - [ ] D1〜D4 固定値を満たせない項目がある場合、「停止」と記録した。
  - [ ] SafeMode既定ONを弱める変更（share/export制約緩和）が含まれていない。
- 事後チェック（復旧後）
  - [ ] `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ復帰済み。
  - [ ] 復旧時刻と復旧条件充足を記録済み。
  - [ ] 監査記録が最小化契約（PII非保存・最小項目）を満たす。
  - [ ] `04_Documentation/security.md` の「8.1 strict mode例外時の安全性チェック」と整合している。

### 3.5 strict mode例外の時系列Runbook（運用本手順）

実運用では以下の順で実施し、各ステップの記録を残す。

1. **申請作成（DraftRequest）**
   - Platform Operator が申請を起票し、理由・対象tenant・復旧予定時刻を記録。
2. **承認審査開始（ApprovalPending）**
   - Security Officer 先行の承認順序で審査へ進める。
3. **一次承認（Security Officer）**
   - D1の承認順序に従い、Security Officer が先行承認。
4. **二次承認（System Owner）**
   - 承認TTL=4h内に System Owner 承認を完了。未達時は申請失効。
5. **適用（ActiveException）**
   - Platform Operator が `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` を適用し、開始時刻を監査記録へ追記。
6. **監視（ActiveException中）**
   - 15分/60分エスカレーション監視を有効化し、最大2hを超えないことを確認。
7. **復旧開始（RollbackPending）**
   - 2h到達または停止条件成立で `RollbackPending` へ遷移。
8. **復旧完了（Closed）**
   - `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ戻し、検証結果を添えて `Closed` へ遷移。
9. **事後監査（48h以内）**
   - 変更台帳と監査IDの相互参照を完了し、48hレビューを実施。

失敗系の扱い:
- 不明点・固定値不一致・承認不備を検知した時点で `StoppedForClarification` を記録し、手順を中断する。
- 中断後は推測で進めず、解消後に `DraftRequest` から再開する。

### 4. SafeMode/read-only 優先

- 判定順は常に `safeMode` → `readOnly` → adapter判定。
- adapterが許可を返しても、SafeMode/read-only拒否は上書きできません。
- `external_http` は HTTP 4xx(400/401/403/422)・不正JSON・契約不整合を `policy_ref_invalid` に、接続障害/timeout/5xx を `policy_ref_unreachable` に正規化します。
- adapter未設定/無効時でも `noop` にフォールバックし、既存運用を阻害しません。

## 監査連携（view/export）運用

### 1. 基本方針

- 監査連携は `KJ_ATLAS_AUDIT_EXPORT_ENABLED=false`（既定）で **完全ローカル動作**。
- 有効化時のみ、`view` / `export` の最小イベントを外部送信。
- 送信データは最小化され、`docId` / `eventType` / `safeMode` / 最小メタデータのみ送信します。
- `x-actor-ref` は平文保存せず、SHA-256短縮ハッシュ (`actorRefHash`) に変換します。

### 2. 最小イベントスキーマ

```json
{
  "schemaVersion": 1,
  "eventId": "audit-<uuid>",
  "occurredAt": "2026-03-01T12:34:56.000000+00:00",
  "eventType": "view | export",
  "docId": "<document-id>",
  "safeMode": true,
  "actorRefHash": "<optional-24hex>",
  "metadata": {
    "route": "...",
    "method": "...",
    "exportKind": "..."
  }
}
```

### 3. 障害時ポリシー（fail-open / queue / drop）

- 監査送信失敗時も、閲覧/エクスポート本体は継続（**fail-open**）。
- 失敗イベントはメモリキューへ退避し、次回送信時に best-effort flush。
- キュー上限 (`KJ_ATLAS_AUDIT_QUEUE_SIZE`) 超過時は最古イベントを drop（ログ警告のみ）。
- 送信障害は運用監視（ログ収集）で検知し、アプリの可用性を優先。

### 4. 鍵・エンドポイント設定

1. `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true`
2. `KJ_ATLAS_AUDIT_TRANSPORT=http`
3. `AUDIT_HTTP_ENDPOINT=https://<audit-gateway>/events`
4. 必要なら `AUDIT_HTTP_API_KEY=<secret>` を設定（Bearer送信）
5. `AUDIT_HTTP_TIMEOUT_SECONDS` を短め（例: 2.0）に維持

### 5. SafeModeポリシー

- 既定は `AUDIT_ALLOW_IN_SAFE_MODE=false`（SafeMode時は外部送信しない）。
- 組織要件でSafeMode中の監査送信が必要な場合のみ明示的に `true` を設定。
- いずれの設定でも payload は最小化・マスキング済みを維持します。


## i18n SafeMode 漏洩防止検証（FB-RM-I18N-06）

### 1. テストマトリクス（経路 × モード × 期待値）

| 経路 | モード | シナリオ | 期待値 |
|---|---|---|---|
| fetch/XHR/Worker | SafeMode=ON | 翻訳アダプタが外部送信を試みる実装でも、ガード経由実行 | アダプタ未実行・送信試行 0 件・`translation.safe_mode_blocked` を記録 |
| telemetry/audit dispatch | SafeMode=ON | telemetry/audit 有効化フラグあり | dispatch 未実行（fail-safe block） |
| telemetry dispatch | SafeMode=OFF | telemetry dispatch が例外を返す | 翻訳処理を fail-safe で停止（adapter 未実行）、`fail_safe_dispatch` を返す |
| adapter timeout | SafeMode=OFF | タイムアウト到達 | `timeout` 返却、返却文とログが `[REDACTED]` のみ |
| adapter error | SafeMode=OFF | adapter error | `adapter_error` 返却、ログに生テキストを含めない |
| 正常系 | SafeMode=OFF | adapter 成功 + telemetry/audit 有効 | `success` 返却、dispatch payload は digest のみ（原文なし） |

### 2. 追加ガード一覧

- `runLocaleConversionWithGuard`:
  - SafeMode 時は翻訳処理・telemetry・audit dispatch を即時遮断。
  - telemetry/audit 送信で例外が出た場合は fail-safe（変換停止）に倒す。
  - timeout/adapter error 時は原文ではなく `SafeModePolicy.redactText` を返す。
  - ログは `SafeModePolicy.summarizeForSafeMode` の digest のみを記録。
- `installNetworkLeakMonitor`:
  - `fetch` / `XMLHttpRequest` / `Worker` をテスト時にフックし、送信経路を網羅監視。
  - 送信試行を即時例外化して漏洩を検出可能にする。

### 3. CI 組み込み方法

1. Frontend の script に以下を追加済み:

```bash
npm run test:i18n-security
```

2. GitHub Actions `CI` に専用ジョブ `Frontend i18n safe-mode leakage guards` を追加済み。

3. branch protection の required check に同ジョブを追加し、
   SafeMode 漏洩テスト未通過のマージを禁止する。

### 4. インシデント時手順（漏洩疑い）

1. `npm run test:i18n-security` をローカルで再実行し、どの経路（fetch/XHR/worker/dispatch）で失敗したかを確認。
2. 失敗ケースのログに原文（機微情報）が含まれていないかを確認（digestのみ許容）。
3. 直近変更で翻訳 adapter / telemetry / audit dispatch の呼び出し位置が SafeMode 判定より先行していないかを確認。
4. 必要なら一時的に翻訳機能を feature flag で停止し、`SafeMode=ON` 時の外部送信 0 件を復旧条件にする。
5. 復旧後に CI の `Frontend i18n safe-mode leakage guards` を required check として再確認する。

## i18n document hash 不変検証（FB-RM-I18N-05）

### 1. テスト観点（ハッシュ対象と分離保証）

- ハッシュ対象は **`document.json` のみ**。`view.json` や UI state は対象外。
- ハッシュ計算前に canonicalize（オブジェクトキー順序正規化）を適用し、順序差分を排除。
- 言語切替時の期待値は2系統で検証する。
  - `document hash` は常に不変。
  - `view metadata`（`viewState.locale` / 解決ソースなど）はシナリオに応じて変化。
- 差分検知時は `ui-state` / `view-metadata` / `document-payload` の層別診断ログで切り分ける。

### 2. ケース表（前提 / 操作 / 期待）

| ケースID | 前提 | 操作 | 期待値 |
|---|---|---|---|
| I18N05-01 | 同一 `document.json`、view locale=ja | `ja -> en -> ja` の順で bundle export | `document.json` hash が3回とも一致。`view.json` は locale 変化に追随 |
| I18N05-02 | metadata=ja, persisted=ja | URL `?locale=en` を付けて locale 解決 | locale source は `url`。`document.json` hash は URL なしケースと一致 |
| I18N05-03 | metadata=en, persisted=ja, read-only=true | locale 解決後に bundle export | `shouldPersist=false`。`document.json` hash は read-write ケースと一致 |

### 3. 失敗時の切り分け手順（層別診断ログ）

1. `npm run test:i18n-regression` を再実行し、失敗ケースIDを特定する。
2. テスト出力の層別診断を確認する。
   - `document-payload`: `document.json` canonical payload が変化（重大）。
   - `view-metadata`: `view.json` の locale など表示メタのみ差分（想定内）。
   - `ui-state`: locale 遷移事実のログ（想定内、ただし document 変化と同時発生なら要調査）。
3. `document-payload` が出た場合は、`buildExportBundle` へ渡す `doc` と `viewState` の境界を確認し、UI状態混入を除去する。
4. 併せて `resolveViewLocale` の source/shouldPersist 判定が read-only と URL 優先規約を満たしているかを再確認する。

### 4. CI組込要件

1. Frontend script:

```bash
npm run test:i18n-regression
```

2. GitHub Actions `CI` に専用ジョブ `Frontend i18n document hash regression` を追加済み。
3. branch protection の required check に同ジョブを設定し、hash不変テスト未通過のマージを禁止する。

### 5. 完了条件（DoD）

- `ja -> en -> ja`、URL優先、read-only の3シナリオで `document.json` hash が不変。
- 期待値を `document hash` と `view metadata` に分離して検証している。
- 差分発生時に、漏洩層（ui-state/view-metadata/document-payload）を診断ログで一意に特定できる。
- CIで deterministic 実行（固定時刻・canonicalize・乱数未使用）が維持される。

## i18n辞書更新ルール（FB-RM-I18N-03 運用）

新しい UI 文言キーを追加したときは、以下を同一PRで実施します。

1. `03_Implement/frontend/src/i18n/locales/ja.json` と `en.json` に同じキーを追加する。
2. 変数展開を使う場合は、`{name}` プレースホルダ名を ja/en で一致させる。
3. 追加後に次の検証を実行し、キー欠損・プレースホルダ不整合・機能回帰を検出する。

```bash
cd 03_Implement/frontend
pnpm -s vitest run src/i18n/catalog_integrity.test.ts src/i18n/key_consistency.test.ts src/ui/i18n_equivalence.integration.test.ts
```

4. 表示言語の切替が document payload に影響しないことを `document_locale_invariance.test.ts` で確認する。
5. SafeMode の漏洩防止回帰（`locale_conversion_guard.test.ts` 等）を必ず再実行する。

## HIL-RS-02-A3 運用同期（仮運用 / モック証跡）

`ADR-0026` の D1〜D4、および A1 契約と B 実装確定内容に合わせ、
次フェーズの運用手順は以下を最小セットとして固定します。

参照契約（A1）:

- RequirementID: `HIL-RS-01-A1`
- 契約境界: Critique入力 / 再提案差分 / レビュー帰属
- Contract Keys: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`
- Freeze Flags: `contractLinkLocked=true` / `sharedResourceFreeze=true`
- 契約参照先（正本）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`

仮運用タグ（依存切断ルール）:

- `status=provisional`
- `evidenceType=mock-trace`
- `replaceOnNextSync=true`
- A2実コード完成待ちをせず、A1契約I/Fと想定運用フローに基づく先行同期として扱う。

### 1. 実行順序（A1 → A2 → A3）

1. A1（Architecture契約）で固定された境界を先に確認する。
   - Critique入力
   - 再提案差分
   - レビュー帰属
2. A2（Frontend実装）で UI 導線を分離して実装する。
   - A2-1 Candidate comparison
   - A2-2 Critique input
   - A2-3 Diff visualization
   - `HilRsWorkflowPanel` 上の表示ラベルと説明文を運用文言として固定する。
     - A2-1: `Collect and compare merge/layout candidates before any commit.`
     - A2-2: `Capture critique and re-suggest iteratively while keeping human final approval.`
     - A2-3: `Review deterministic diffs before apply/discard to keep the workflow reversible.`
3. A3（Documentation同期）で本書・`security.md`・`e2e_testing.md` の
   手順と制約を同期し、検証コマンドを記録する。

### 1.1 A3運用固定（再現手順）

1. `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF` の4契約を、運用手順・検証手順・停止条件のすべてで同一表記に揃える。
2. `HilRsWorkflowPanel` の3導線ラベルと説明文を、運用文言の固定値として扱う。
3. `hil_rs_contract.ts` の検証制約（PII-like field拒否 / reversible diff必須 / human review帰属必須）と矛盾する運用記述を禁止する。
4. `contractLinkLocked=true` / `sharedResourceFreeze=true` が崩れている場合は、推測補完せず更新を停止する。
5. 契約未固定（ID未記載・契約境界の欠落）を検知した場合は、推測補完せず更新を停止する。

### 1.4 可逆統合フローの運用手順（仮運用）

1. 候補比較（A2-1）
   - 候補は「提案」のみで確定ではないことを記録する。
   - 監査記録には `phase=candidate_comparison` と `decisionPending=true` を残す。
2. Critique入力（A2-2）
   - Critiqueは iteration ごとに入力し、空コメント+空tagsは破棄する。
   - 監査記録は PII最小化（subject生値なし）を維持し、`traceKey` を必須化する。
3. 差分可視（A2-3）
   - `before/after` の差分が欠けた提案は適用禁止にする。
   - 差分レビューは apply/discard の可逆操作で記録し、自動確定へ昇格しない。
4. 人間確定
   - 最終承認は人間のみ実施し、`reviewAttribution` の妥当性が検証できない場合は停止する。

### 1.5 Plan → Execute → Verify → Proceed（A3運用固定）

可逆統合フローの運用は、毎回次の直列手順で実施する。

1. **Plan**
   - 対象ドキュメントを `operations.md` / `security.md` / `e2e_testing.md` に限定し、A1契約境界との差分を先に列挙する。
   - 差分ごとに `audit-minimum`（PII最小化）と `rollback trigger`（停止条件）をセットで定義する。
2. **Execute**
   - 手順更新時は `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF` を固定表記で記載する。
   - `status=provisional` と `evidenceType=mock-trace` を同時記録し、実コード確定前の暫定同期であることを明示する。
3. **Verify**
   - docs-check（本節 3）で契約キー、Freeze Flags、3導線固定文言、payload制約の一致を検証する。
   - 失敗時は最大3回まで自己修復し、4回目以降は更新停止・差し戻しへ移行する。
4. **Proceed**
   - `status` を `provisional_reapplied` へ更新し、変更理由・運用影響・次回置換条件（`replaceOnNextSync=true`）を記録する。

### 1.2 A2挙動との対応表（A3同期対象）

| A2挙動（実装意図） | A3で固定する運用文言 | 逸脱時の扱い |
| --- | --- | --- |
| A2-1 Candidate comparison は意思決定補助であり確定操作ではない | 「候補提示」と「確定操作（人間のみ）」を明記する | 自動確定へ拡張する提案は停止して上位合意へ戻す |
| A2-2 Critique input は反復改善の入力導線である | 入力は可逆編集前提、監査はPII最小化で記録する | subject生値や自由記述PIIの監査転記は禁止 |
| A2-3 Diff visualization は再提案の比較導線として使う | 差分は可逆操作で追跡可能であることを維持する | 一方向適用のみの導線は非目標として却下 |

実装整合メモ（B handoff反映済み）:

- UI導線名は `03_Implement/frontend/src/ui/HilRsWorkflowPanel.tsx` の見出しを正として同期済み。
- 運用上の制約は `03_Implement/frontend/src/domain/hil_rs_contract.ts` の validator 制約（PII-like field拒否、可逆差分必須、人間レビュー帰属）と一致させる。

### 1.3 A2 payload 正規化ルール（A3で固定する実装整合）

`03_Implement/frontend/src/domain/hil_rs_payload.ts` の挙動に合わせ、運用手順でも次の固定値を保持する。

1. Critique tags 正規化:
   - 既知タグ（`too_close` / `too_far` / `not_the_same` / `feels_off`）のみ Critique type へ写像する。
   - tags未指定、または未知タグのみの場合は `no_articulable_reason` を採用する。
2. Critique入力の最小発行条件:
   - コメントと tags がともに空の場合は payload を発行しない。
   - `iteration` は 1 以上の整数のみ許可し、条件を満たさない場合は空配列で fail-fast する。
3. レビュー帰属の生成条件:
   - `createHilRsReviewAttribution` は validator 成功時のみ attribution を返し、失敗時は `null` を返す。
   - 不正な帰属値を運用で補完しない（再入力または再承認を要求する）。
4. 再提案差分とエラー契約の最低整合:
   - 再提案差分（`A1-REDIFF-IF`）は `traceKey` を必須とし、欠落時は処理を中止する。
   - 契約違反・必須欠落・PII違反は `A1-ERROR-IF` の固定コード（5件）へ写像し、独自コードを追加しない。

### 2. 制約（非目標と停止条件）

- SafeMode 既定ONと share/export 漏えい防止を弱める変更は不可。
- 単一スコア・ランキングなど「単一正解」を示唆する運用は禁止。
- `domain.md` の保留/可逆性と矛盾する場合は、実装を進めず上位文書（00〜02）を先に修正提案する。

非目標（A3では扱わない）:

- LLM Provider 再設計
- Frontend コンポーネント実装
- SafeMode 既定ON の緩和

ロールバック条件（A3同期の停止/差し戻し）:

- Contract Keys / Freeze Flags のいずれかに不一致がある。
- `traceKey` 欠落や可逆差分欠落など、A2 handoff で固定した必須整合に違反する。
- PII-like field拒否・人間レビュー帰属必須のいずれかを満たせない。

ロールバック手順:

1. 文書更新を停止し、逸脱箇所（契約ID/固定値/実装差分）を列挙する。
2. A1正本（`02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`）へ照合し、差分をA1差し戻しとして起票する。
3. 差分解消までA3更新を再開しない（推測補完禁止）。

### 2.1 異常時ロールバック運用（仮運用）

- Trigger-1: `A1-ERROR-IF` 固定コード外のエラーが記録された。
- Trigger-2: `contractLinkLocked=true` または `sharedResourceFreeze=true` が満たされない。
- Trigger-3: 監査ログにPII-like field混入が検知された。

対応手順:

1. `status=rollback_pending` を記録し、以降のA3同期を停止。
2. 直近の `status=provisional` 更新を基準に差分を切り戻す。
3. A1差し戻し票に「契約キー」「逸脱内容」「再実行条件」を記載。
4. 是正後に `status=provisional_reapplied` として再同期する。

### 3. docs-check 記録

- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg -n "HIL-RS-01|ADR-0026|SafeMode|可逆|Critique|レビュー帰属" 04_Documentation 01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`
- `rg -n "A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF|contractLinkLocked|sharedResourceFreeze" 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/e2e_testing.md`
- `rg -n "A2-1 Candidate comparison|A2-2 Critique input|A2-3 Diff visualization|Collect and compare merge/layout candidates before any commit.|Capture critique and re-suggest iteratively while keeping human final approval.|Review deterministic diffs before apply/discard to keep the workflow reversible." 03_Implement/frontend/src/ui/HilRsWorkflowPanel.tsx 04_Documentation/operations.md 04_Documentation/e2e_testing.md 04_Documentation/security.md`
- `rg -n "no_articulable_reason|createHilRsReviewAttribution|iteration" 03_Implement/frontend/src/domain/hil_rs_payload.ts 04_Documentation/operations.md`
- `cd 03_Implement/frontend && pnpm -s vitest run src/ui/HilRsWorkflowPanel.test.ts src/domain/hil_rs_contract.test.ts src/domain/hil_rs_payload.test.ts src/domain/hil_rs_rediff_stub.test.ts`

判定メモ:

- `rg` で `HIL-RS-01-A1` と 3 Contract Key の同時出現を確認し、表記揺れを禁止する。
- vitest は文書固定値（3導線ラベル）と validator 制約の整合確認として扱う。

### 3.1 監査証跡テンプレート（仮運用）

作業記録には次の最小項目を残す。

- `requirementId`: `HIL-RS-01-A1`
- `syncScope`: `HIL-RS-02-A3`
- `status`: `provisional | rollback_pending | provisional_reapplied`
- `evidenceType`: `mock-trace`
- `operatorRole`: `Platform Operator`
- `approverRoles`: `Security Officer`, `System Owner`
- `traceKeyPresence`: `true | false`
- `piiMinimized`: `true | false`
- `nextSyncAction`: `replace_with_A2_actual_evidence`

上記コマンドの結果を PR/作業記録に残し、再現可能性を担保します。

## Stream B 運用同期（FB-P2B-01 / FB-P2B-02, A3）

Stream C/D の実装確定内容に合わせ、Similar-card 候補提示と Manual assisted merge の運用手順を固定する。

参照契約ID（A1/A2/A3共通）:

- `CTR-2B-01-CANDIDATE-GROUP-V1`（候補グループ）
- `CTR-2B-02-DECISION-LOG-V1`（決定ログ）

### 1. 実行順序（Plan → Execute → Verify → Proceed）

1. **Plan**
   - Similar-card 候補収集は deterministic heuristic とし、`Collect candidates` は確定操作を行わない。
   - 4値決定（`accept` / `partial` / `reject` / `defer`）以外を運用で追加しない。
2. **Execute**
   - `MergeSuggestionsPanel` で候補グループを確認し、必要時のみ `editedText` を編集する。
   - 最終判断は人間が実施し、決定時に `mergeSuggestionDecisions` へ append する。
3. **Verify**
   - 同一 `groupId` の履歴は append 順序を保持し、`snapshotVersion` が `CTR-2B-02-DECISION-LOG-V1` のレコードだけを復元対象とする。
   - read-only モード時は候補収集/決定ボタンが disabled であることを確認する。
4. **Proceed**
   - 契約ID不一致、4値外の decision、または自動確定の導線を検知した場合は停止し、A1契約の再確認へ戻す。

### 2. 運用上の制約

- 「Deterministic heuristic only (no AI decision). Final merge decision remains human-in-the-loop.」の方針を固定値として扱う。
- `accept` は監査記録であり、即時にカード統合を自動実行しない（確定導線は別操作）。
- 候補対象カードが2件未満になった場合、`Merge suggestion is no longer applicable.` として決定を拒否する。
- `groupId` 空文字、`cardIds` 空、`editedText` 空文字は fail-fast で拒否する。

### 3. docs-check 記録（最小）

```bash
cd 03_Implement/frontend
pnpm -s vitest run src/ui/MergeSuggestionsPanel.test.ts src/domain/merge_suggestion_decisions.test.ts src/domain/stream_b_contract_handoff.test.ts
```

```bash
rg -n "CTR-2B-01-CANDIDATE-GROUP-V1|CTR-2B-02-DECISION-LOG-V1|accept|partial|reject|defer|human-in-the-loop" \
  03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx \
  03_Implement/frontend/src/domain/merge_suggestion_decisions.ts \
  03_Implement/frontend/src/domain/stream_b_contract.ts \
  03_Implement/frontend/src/domain/stream_b_contract_handoff.ts \
  04_Documentation/operations.md 04_Documentation/e2e_testing.md 04_Documentation/security.md
```

## 7. CE1 ContextQuery / ContextBundle 運用

- `POST /context/query` は Query Preview 通過済み `ContextQuery` の契約検証APIです。`queryId/goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode/previewConfirmed` を必須契約として受け取り、`previewConfirmed=false` は常に `422 preview_required` で拒否します。
- `POST /context/bundle` は deterministic bundle generator です。同一 canonical query を再実行した場合、`bundleHash` は常に一致する前提で運用します。
- `safeModePolicy=strict` かつ `reviewFilter=reviewedOnly` の場合、未レビュー本文は bundle へ含めず、`excludedReason` に `unreviewed_filtered` を必須記録します。
- Query Preview 未通過の送信導線は無効化し、mock `/context/query` `/context/bundle` でも同一契約（bypass禁止）を維持します。
- Verify/Proceed の自己修復は最大3回まで許可し、4回目失敗時は即停止します。
- 監査用途では `queryId` / `bundleHash` / `excludedReason` をログ相関キーとして固定します。


## Stream G docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **CDC**: Context / Decision / Consequences を明文化し、分類結果（Move internal / Improve external）を固定する。
3. **Plan**: AC/DoD を先に定義し、docs-only スコープ（`03_Implement/**` 非変更）を明示する。
4. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
5. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
6. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## 0.8 Phase 1-5 実行記録（2026-04-16 / DOC-OPS-05-11）

- Phase 1 Read: 開始時に `operations.md` / `security.md` / `security_operational_guidelines.md` / `strict_mode_exception_approval_flow.md` を再Readし、役割語彙・導線・固定値の差分有無を確認。
- Phase 2 Plan: docs-only での改善に限定し、公開境界（Audience/Goal/Non-goal/Public boundary）を維持する計画を固定。
- Phase 3 Execute: 運用runbook責務に限定して追記し、承認フロー正本の再定義は行わない。
- Phase 4 Verify: `rg` と `git diff --check` で体裁・導線・語彙整合を確認。自己修復上限は3回。
- Phase 5 Proceed: 判定は **Ready**。4回目相当の修復が必要になった場合は **StoppedForClarification** で停止する。

## Stream H 専任: DOC-OPS-05後半 実行記録（2026-04-16）

### Phase 1 Read

- 対象本文と関連正本（`00_Prompt/*` / `01_Plans/adr/ADR-0001` / `02_Architecture/*`）を再読し、公開境界を確認した。
- 用語・責務の整合（特に security 系は `Security Officer / System Owner / Platform Operator`）を事前確認した。

### Phase 2 Plan（AC/DoD補完）

- AC補完:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の冒頭メタを維持する。
  - 本文は docs-only で更新し、実装仕様・設定値の新規決定を持ち込まない。
  - 参照導線（関連文書・issue memo）を切断しない。
- DoD補完:
  - Read → Plan → Execute → Verify → Proceed の記録を残す。
  - Verify で `docs-check` とリンク整合を確認する。

### Phase 3 Execute

- 本文の方針を維持したまま、Stream H後半の実行責務（Phase運用・停止条件）を追記した。
- 編集範囲外（backend/frontendコード、shared統合3ファイル）は変更しない。

### Phase 4 Verify（docs-check + リンク整合）

- `rg` で必須メタ語彙・Phase見出し・停止条件語彙を確認した。
- `git diff --check` で体裁崩れがないことを確認した。
- security 系は D1〜D4 と役割語彙の整合を追加確認した。

### Phase 5 Proceed

- 判定: **Ready**
- 継続条件: 次回更新でも同一フェーズ順序と docs-only 制約を維持する。

### 停止条件（固定）

- 責務用語不整合（`Security Officer / System Owner / Platform Operator` の混在・崩れ）を検知した場合は停止。
- D1〜D4 固定値矛盾（`4h / 2h / 代理承認なし / 48h+15m/60m`）を検知した場合は停止。
- Verify の自己修復が3回を超える場合は `StoppedForClarification` として停止。

## 0.9 Stream G dedicated cycle（2026-04-19 / DOC-OPS-05-11）

- Phase 1 Read: `issue-doc-ops-05-11-04doc-operations.md` と本書のみ再Readし、`1 issue : 1 doc` 制約を再確認。
- Phase 2 Plan: 既存分類 `Improve external` を維持し、内部移設ではなく公開runbookの可読性維持を優先。
- Phase 3 Execute: 方針変更なしのため本文の実行手順は据え置き、実行証跡のみを最小追記。
- Phase 4 Verify: `docs-check`（issue validator / `rg` / `git diff --check`）を実施し、修復上限3回ルールを維持。
- Phase 5 Proceed: 判定 **Ready**。次担当へ「内部限定情報の混入監査を優先し、担当外docは非編集」を引き継ぐ。

## Stream J（DOC-OPS-05 中盤2）実行記録（2026-04-19）

### Phase 1 Read
- 開始時に対応Issueと本ドキュメントを再読し、Classification=**Improve external** と公開境界メタの有効性を確認。
- 変更範囲を `01_Plans/issues/issue-doc-ops-05-*`（担当4件）と本ドキュメントに限定。

### Phase 2 ADR CDC（必要時のみ）
- 判定: **不要**（既存の分類・公開境界・Go/No-Go方針は上流文書と整合）。

### Phase 3 Plan
- AC/DoD不足の補完方針:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の再確認結果を記録。
  - Verify は docs-check（`rg` / issue memo validator / `git diff --check`）で実施。
  - Verify失敗時は自己修復を最大3回まで許容し、4回目相当は停止して判断依頼。

### Phase 4 Execute
- docs-only 追記を実施。既存手順・分類方針は維持し、実装仕様やコード変更は行わない。

### Phase 5 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream J（DOC-OPS-05 中盤2）" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md 04_Documentation/operations.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**。
- 引き継ぎ: 次担当は各Phase開始時に issue/doc の再読を継続し、競合・前提崩壊・3回超過時は即停止する。

## Stream G 実行記録（DOC-OPS-05文書群② / 2026-04-19）

### Phase 1 Read同期
- `02_Architecture/strict_mode_exception_approval_flow.md` を正本として再読し、`operations.md` / `security.md` / `security_operational_guidelines.md` の用語・責務・固定値（D1〜D4）を照合した。
- canonical 用語を `Security Officer / System Owner / Platform Operator` に統一維持し、状態語彙（`DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed` と `StoppedForClarification`）の一致を確認した。

### Phase 2 CDC明文化（判断分岐時のみ）
- 判定: **分岐なし（CDC追加なし）**。
- 理由: 分類（Improve external）と責務境界（runbook専任）は既存決定で固定済みであり、新規の二択判断を伴わないため。

### Phase 3 Execute（文書更新）
- Stream G の docs-only 進行記録を追加し、運用runbookの責務（実行手順）を維持した。
- SafeMode既定ON / share-export漏洩防止 / D1〜D4固定値に変更がないことを明示した。

### Phase 4 Verify（docs-check + 用語/固定値照合）
- docs-check: `rg -n "Security Officer|System Owner|Platform Operator|D1|D2|D3|D4|StoppedForClarification" 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/security_operational_guidelines.md`
- diff-check: `git diff --check`
- 判定: Pass（用語ドリフトなし、固定値不一致なし、体裁崩れなし）。

### Phase 5 Proceed/Stop
- 判定: **Proceed（Ready）**。
- 停止条件: 用語/責務/固定値（D1〜D4）のいずれかに不一致が再発した場合は `StoppedForClarification` で停止する。


## Stream F HIL-RS-02-A3 sync log（2026-04-19）

- Phase 1 Read: `strict_mode_exception_approval_flow.md` / `security.md` / `security_operational_guidelines.md` / `e2e_testing.md` を再読し、runbook記述の同値性を確認。
- Phase 2 用語同期: `Security Officer / System Owner / Platform Operator` を維持し、承認2者と実行責務分離の一致を確認。
- Phase 3 D1〜D4整合: `4h / 2h / 代理承認なし / 48h+15m/60m` の固定値一致を確認。
- Phase 4 Verify: docs-check（validator / `rg` / `git diff --check`）で不整合0件を確認。
- Phase 5 Proceed: **Ready**。不一致再発時は `StoppedForClarification` で停止し、統合ストリームへ差分を引き継ぐ。

## Stream E serial cycle（2026-04-20 / DOC-OPS-05後半 docs-only）

### Phase 1 Read
- 本文先頭メタ（Classification / Audience / Goal / Non-goal / Public boundary / Outcome / Related）を再確認。

### Phase 2 Plan
- 変更は docs-only に限定し、Plan→Execute→Verify→Proceed の固定順序で進める。
- Verify失敗時の自己修復は最大3回、4回目相当は停止する。

### Phase 3 Execute
- 本文の公開境界・導線を維持し、safeMode既定ON／漏えい防止後退禁止を再確認。

### Phase 4 Verify
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Outcome|Related" 04_Documentation/operations.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**。
- 次担当へ: 致命的矛盾（上位文書不整合・安全境界後退・自己修復3回超過）を検知した場合は停止してIssueへ記録する。

## 0.10 Track 4 sync addendum（2026-04-22）

- 本書は DOC-OPS Track 4 の順序 `05-05 → 05-11 → 05-13 → 05-14` に従って更新する。
- 各Phase開始時に Read同期を実施し、`security.md` / `security_operational_guidelines.md` / `strict_mode_exception_approval_flow.md` との差分を先に確認する。
- ADR関連変更は Context / Decision / Consequences を先行明文化し、合意（DecisionStatus=Fixed）確認後に Execute する。
- Verify失敗時の自己修復は最大3回。超過時は `StoppedForClarification` で停止する。

## 0.11 Stream L serial lane log（2026-04-26 / DOC-OPS-05-11）

### Phase 1 Read
- `issue-doc-ops-05-11-04doc-operations.md` と本書を再読し、公開runbook責務を確認。

### Phase 2 ADR/CDC
- Context: operations は実行runbookであり、security/guidelines の制度設計を内包しない。
- Decision: 本書は `Improve external` を維持し、`Security Officer / System Owner / Platform Operator` と 2者承認+実行分離、D1〜D4同値確認をGo判定前提に固定。
- Consequences: 役割語彙ドリフトと責務混在を抑止し、公開境界を維持できる。

### Phase 3 Plan
- Scope: docs-onlyの追記。
- Non-goal: 実装変更・承認制度の再定義。
- AC/DoD: 冒頭分類メタと本節の整合が確認できること。
- Validation: `rg` / `git diff --check`。
- Stop: 自己修復3回超過、用語/責務/固定値不一致。

### Phase 4 Execute
- 本節を追加し、DOC-OPS-05-11の直列完遂証跡を固定。

### Phase 5 Verify
- docs-check観点で不整合なし（自己修復 0/3）。

### Phase 6 Proceed
- 判定: **Ready**（次順序は security 文書）。

## Stream F HIL-RS-02-A3 operations sync log（2026-04-27）

### Phase 1 Read
- `strict_mode_exception_approval_flow.md` と `issue-HIL-RS-02-A3-operations-documentation-sync.md` を再読し、語彙（Security Officer / System Owner / Platform Operator）と固定値（D1〜D4、safeModeDefault=ON、overridePolicy=human_dual_control_only）の一致を確認。

### Phase 2 Plan
- docs-only で `operations.md` / `security.md` / `e2e_testing.md` の同期に限定。
- A3は `mock I/F preparation only` を維持し、契約値の再定義・Open化を行わない。

### Phase 3 Execute
- Runbook側のA3同期証跡を追記し、`contractLinkLocked=true` / `sharedResourceFreeze=true` の freeze 条件を再確認。

### Phase 4 Verify
- `rg -n "Security Officer|System Owner|Platform Operator|safeModeDefault=ON|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true" 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/e2e_testing.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 5 Proceed
- 判定: **Conditional（Draft維持の準備継続）**。
