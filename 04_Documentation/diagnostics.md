# Diagnostics Worker Protocol

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部運用者・開発者
> Goal: diagnostics worker 契約を公開runbookとして参照可能にする。
> Non-goal: worker実装ロジックの再設計や内部検証ログ形式の固定化は扱わない。
> Public boundary: 内部検討ログは含めず、契約/フォールバック条件を公開する。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Outcome: 外部運用者が契約・フォールバック・決定論条件を単独で判断できる。
> Related: `02_Architecture/schemas.md`, `03_Implement/frontend/src/worker/diagnostics_protocol.ts`, `01_Plans/documentation_quality.md`, `01_Plans/issues/issue-doc-ops-05-04-04doc-diagnostics.md`



## Reader Guide（最初に確認）

- **この文書の役割**: diagnostics worker の**診断仕様（契約）**。
- **主読者**: フロントエンド実装者 / QA / 運用者。
- **読むタイミング**:
  1. diagnostics worker の実装変更前
  2. `schemaVersion` 変更検討時
  3. worker異常時の fallback 判定時
- **この文書に含めないもの**: 日次の実行履歴（`e2e_verification_log_2026-03-03.md`へ）。

## 文書導線（方針 / ログ / 診断仕様）

- E2E方針・実行手順: `04_Documentation/e2e_testing.md`
- E2E実行履歴: `04_Documentation/e2e_verification_log_2026-03-03.md`
- 診断仕様（本書）: `04_Documentation/diagnostics.md`

上記3文書は役割を固定し、同一内容を重複記載しない。
この文書は Frontend diagnostics worker の I/O 契約を定義する。
公開運用時の用語は `reviewed / unreviewed` を正とし、`true/false` 表記は状態値の説明時にのみ補助的に使う。
品質判定は `01_Plans/documentation_quality.md` の QG-1〜QG-6 に従う。
対象実装:
- `03_Implement/frontend/src/worker/diagnostics_protocol.ts`
- `03_Implement/frontend/src/worker/diagnostics_client.ts`
- `03_Implement/frontend/src/worker/diagnostics.worker.ts`

## diagnosticsData schemaVersion

- Current: `1`
- 対応方針: クライアントは `schemaVersion === 1` のみ受理する。
- pre-release 方針として、旧バージョン互換（schema欠損・旧versionマイグレーション）は提供しない。

## Worker message envelope

### Request
- `diagnostics.request`
- `diagnostics.cancel`

### Response
- `diagnostics.progress`
- `diagnostics.result`
- `diagnostics.error`
- `diagnostics.cancelled`

## Validation / fallback policy

`DiagnosticsWorkerClient` は次を検知した場合、worker結果を破棄し main-thread fallback 計算へ遷移する。

- invalid / unsupported `schemaVersion`
- malformed / array-shaped payload
- malformed result envelope（`result` がobjectでない、`diagnosticsMd` がstringでない）
- malformed progress（stage不正、percent不正）
- unknown message type
- malformed `diagnostics.error`（messageがstringでない）
- required fields 欠落（`recommendations`, `diagnosticsMd`, 各report object）

### requestId isolation

- 別requestIdのメッセージは無視する。
- 別requestIdで malformed なメッセージが来ても、対象requestの処理は継続する。


### fallback 発生時の記録ルール（再現性）

fallback が発生した場合、検証ログには次を記録する。

- requestId
- 検知トリガー（例: unsupported `schemaVersion` / malformed envelope）
- fallback先（main-thread compute）
- 影響範囲（該当テストケースまたは画面操作）

これにより、worker異常の再現手順と切り分けを保持する。

## Compatibility guarantee

- N（current）: 完全サポート
- N 以外: 互換なし（fallbackへ遷移し処理継続）

## Structural metrics contract

`diagnosticsData.structuralMetrics` は次の値を返す（同一入力で同一出力の決定論）。

### Existing metrics

- `cardCount`: ドキュメント中のカード件数
- `islandCount`: ドキュメント中の島件数
- `evidenceLinkCount`: 妥当なカード参照を持つ evidenceLinks 件数
- `evidenceLinkDensity`: `evidenceLinkCount / max(1, cardCount)`
- `isolatedCardCount`: relation（evidenceLinks + card-card edges）に接続していないカード数
- `isolationRate`: `isolatedCardCount / max(1, cardCount)`
- `contradictionRatio`（optional）: 型付き relation における否定系比率
- `reviewedCoverage`（optional）: `textReviewed === true` の割合
- `islandSizeDistribution`: 島ごとの有効カード数分布

### FB-RM-RS-02 metrics

- `connectedComponentCount`:
  - 意味: relation グラフ（card node、undirected edge）における連結成分数
  - 期待: 値が大きいほど分断の可能性が高い
- `largestComponentRatio`:
  - 意味: `largestConnectedComponentSize / max(1, cardCount)`
  - 期待: 1.0 に近いほど全体が連結、低いほど断片化
- `connectivityScore`:
  - 意味: `1 - (max(0, connectedComponentCount - 1) / max(1, cardCount - 1))`
  - 期待: 1.0 に近いほど一体、0.0 に近いほど分断
- `averageDegree`:
  - 意味: relation グラフの平均次数（`2 * |E| / max(1, cardCount)`）
  - 期待: 全体の接続密度の基準値として利用
- `degreeP95`:
  - 意味: card degree 分布の95パーセンタイル（nearest-rank）
  - 期待: 局所ハブの過密検知に利用
- `degreeSkewRatio`:
  - 意味: `degreeP95 / max(1, averageDegree)`
  - 期待: 1.0超で局所ハブ偏重の兆候
- `bridgeEdgeCount`:
  - 意味: 削除すると連結成分数が増える bridge edge 数（無向グラフ）
  - 期待: 値が高いほどボトルネック依存が高い

### Computation scope

- relation グラフの edge は以下を統合して構築する:
  - `evidenceLinks`（fromCardId/toCardId が既知カード）
  - `edges` の card-card 関係（fromKind/toKind が card または未指定）
- 自己ループは除外する。
- bridge 判定は正規化済み無向単純グラフで実施する。

### Metric definitions and formulas (FB-RM-RS-02)

集合を次のように定義する。

- `C`: 全カードID集合（`|C| = cardCount`）
- `E_evidence`: `evidenceLinks` のうち両端が `C` に含まれる link 集合
- `E_edge`: `edges` のうち card-card 関係（`fromKind/toKind` が `card` または未指定）かつ両端が `C` に含まれる集合
- `E`: `E_evidence ∪ E_edge` を無向単純グラフへ正規化した edge 集合（自己ループ除外・重複除去）
- `deg(v)`: 無向グラフ `G=(C,E)` における card `v` の次数

計算式:

- `connectedComponentCount = cc(G)`
- `largestComponentRatio = largestComponentSize(G) / max(1, |C|)`
- `connectivityScore = 1 - (max(0, connectedComponentCount - 1) / max(1, |C| - 1))`
- `isolationRate = isolatedCardCount / max(1, |C|)`
- `averageDegree = 2 * |E| / max(1, |C|)`
- `degreeP95 = percentile_nearest_rank({deg(v) | v ∈ C}, 95)`
  - nearest-rank: `rank = ceil(0.95 * n)`（`n=|C|`, 1-indexed）
- `degreeSkewRatio = degreeP95 / max(1, averageDegree)`
- `bridgeEdgeCount = |{ e ∈ E | cc(C, E \ {e}) > cc(G) }|`

意図:

- `connectedComponentCount`: 分断された島/論点群の多さを検知
- `largestComponentRatio`: 全体の一体性（最大連結塊への集中）を検知
- `connectivityScore`: 連結性の健全度を 0.0〜1.0 で比較
- `isolationRate`: 孤立カードの割合（孤立率）を比較
- `averageDegree`: 全体接続密度（平均的な結合度）を比較
- `degreeP95`: 局所ハブ偏重（過密接続）を検知
- `degreeSkewRatio`: 平均次数に対する偏り（ハブ偏重）を比較
- `bridgeEdgeCount`: 単一関係に依存する脆弱な接続（ボトルネック）を検知

決定論ルール:

- graph 正規化時に undirected pair をソートし、重複排除後も安定順序を維持する。
- bridge 判定 DFS は隣接ノードをID昇順で走査する。
- 小数は `round(value * 10_000) / 10_000` で丸める。
- これにより同一入力で同一 `diagnosticsData.structuralMetrics` を返す。

## E2E verification (FB-RM-RS-02)

- Playwright: `03_Implement/frontend/e2e/diagnostics_structural_metrics.spec.ts`
- Scope:
  - Share Panel から `document.json` を置換し、bundle export を実行する。
  - export された `diagnostics.md` に構造メトリクス行（`connectedComponentCount`, `largestComponentRatio`, `bridgeEdgeCount`, `isolationRate`, `connectivityScore`, `degreeSkewRatio`）が含まれることを確認する。
  - 同一入力で 2 回 export した `diagnostics.md` が一致すること（決定論）を確認する。

### Initial threshold hints (warning defaults)

- `connectedComponentCount >= 3`
- `largestComponentRatio < 0.7`
- `degreeP95 >= 6`
- `bridgeEdgeCount >= 5`

> しきい値は初期運用値であり、プロジェクトデータ特性に応じて調整する。

## Quality gate (Phase 1〜6, Doc-Ops-05 Set 2)

本書の更新時は、次の順序で品質ゲートを適用する。

1. **Phase 1: Scope固定**
   - 変更範囲を `04_Documentation/diagnostics.md` のみ（またはSet 2許可範囲）に限定する。
2. **Phase 2: 構造整合**
   - Audience / Goal / Public boundary が冒頭メタで判別できることを確認する。
3. **Phase 3: 用語整合**
   - review状態の語彙を `reviewed / unreviewed` に統一し、他表現を混在させない。
4. **Phase 4: 導線整合**
   - 関連正本（Architecture / Plans / 実装パス）への参照が維持されていることを確認する。
5. **Phase 5: 再現性整合**
   - E2E確認項目と期待結果（決定論確認を含む）が本文から追跡できることを確認する。
6. **Phase 6: 公開判定**
   - 公開不可情報がなく、Go/No-Go判断に必要な情報が本文だけで読めることを確認する。

失敗時は **最大3回まで修復して再判定** し、3回を超える場合は変更を停止して論点を `01_Plans/` にエスカレーションする。

## 共通ワークフローとフェイルセーフ（DOC-OPS-05 共通）

本書の更新は次の固定順序で実施する。

1. Phase 1 Read
2. Phase 2 Plan（品質ゲート宣言）
3. Phase 3 Execute（局所更新）
4. Phase 4 Verify（リンク/語彙/整形）
5. Phase 5 Proceed（残課題明示）

`01_Plans/issues/issue-doc-ops-05-04-04doc-diagnostics.md` と **同一ワークフロー**を採用する。

フェイルセーフ:

- Verify 失敗時は **自己修復を最大3回まで** 実施する。
- 4回目相当は作業を停止し、`01_Plans/issues/` にブロッカーを記録してエスカレーションする（**同一停止条件**）。

- Stream G フェイルセーフ: テスト方針の矛盾または監査要件未達が判明した時点で更新を停止し、Proceedでは未解消項目を明示する。

## Stream F DQ-CONTRACT-v1 適用（2026-04-20）

本書の品質判定は `01_Plans/documentation_quality.md` に定義した **DQ-CONTRACT-v1（DQ-A1〜A6）** に従う。

- メタ完全性: Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
- 契約整合: worker契約（schemaVersion / fallback / requestId isolation / structural metrics）への導線を維持する。
- Verify最小セット（docs-check）:
  - `rg -n "DQ-CONTRACT-v1|reviewed / unreviewed|schemaVersion|fallback|requestId|structuralMetrics|Related" 04_Documentation/diagnostics.md 01_Plans/documentation_quality.md`
  - `git diff --check`
- 失敗時ポリシー: 自己修復は最大3回。4回目相当は Stop とし、Proceed を保留にする。

## Related

- `01_Plans/documentation_quality.md`
- `02_Architecture/schemas.md`
- `04_Documentation/diagnostics.md`（本書）
- `03_Implement/frontend/src/worker/diagnostics_protocol.ts`
- `03_Implement/frontend/src/worker/diagnostics_client.ts`
- `03_Implement/frontend/src/worker/diagnostics.worker.ts`


## Stream G docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **Plan**: 品質ゲート（Audience/Goal/Non-goal/Public boundary/Outcome/Related）と停止条件を宣言する。
3. **Execute**: docs-only スコープ（`03_Implement/**` 非変更）で本文を局所更新する。
4. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
5. **Proceed**: Ready/Hold/Needs-decision を記録し、残課題を次Issueへ引き継ぐ。


### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## Phase6 KPI/Audit 連携メモ（Stream F）

diagnostics の構造メトリクスは Gate D（KPI scorecard audit）の補助指標として扱えるが、**KPI定義そのものを置き換えない**。
運用時は次の直列を固定する。

1. KPI定義（TFS / Decision Readiness / Support Deflection / Feedback Closure）を `issue-0020` で確定。
2. 監査指標として diagnostics の該当メトリクス（`isolationRate`, `connectivityScore`, `bridgeEdgeCount` など）を補助参照。
3. Runbook判定は `operations.md` の Gate C→D→E と Proceed条件に従って記録する。

Fail-safe: diagnostics 指標とKPI判定が矛盾した場合は、Gate E の前に CDC（Context / Decision / Consequences）を作成し、未承認のしきい値変更を禁止する。

## DOC-OPS-05 追加実行記録（2026-04-16 / Target 05-01..05）

### Phase 1 Read（再Read）
- 本書と関連Issueを再Readし、公開境界とdocs-onlyスコープを確認。

### Phase 2 Plan（再Read）
- 5Phase（Read→Plan→Execute→Verify→Proceed）で進行し、対象外文書へは非接触とする。

### Phase 3 Execute（再Read）
- 本書の既存分類・公開境界メタを維持しつつ、05-01..05セットの実行記録を追記。

### Phase 4 Verify（再Read）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/diagnostics.md 01_Plans/documentation_quality.md`
- `git diff --check`
- 修復は最大3回まで。3回超過は停止（Hold）。

### Phase 5 Proceed（再Read）
- 判定: **Ready**
- 次アクション: 同一セット内Issue本文とScope本文の整合を維持して進行。

## DOC-OPS-05 Stream G 前半フェーズ実行記録（2026-04-16）

- Classification確認: **Improve external**（再判定なし）
- フェイルセーフ固定: 用語ドリフト検知・固定値不一致検知・自己修復3回超過で停止（Hold）

### Phase 1: Read（対象ファイル再読）
- 本ファイルを再読し、Scope / Audience / Goal / Public boundary / Related の整合を確認。

### Phase 2: Plan（対象ファイル再読）
- 本ファイルを再読したうえで、docs-only の変更範囲と受入条件を固定。

### Phase 3: Execute（対象ファイル再読）
- 本ファイルを再読したうえで、分類方針（Move internal / Improve external）を維持して更新。

### Phase 4: Verify（docs-check、対象ファイル再読）
- 本ファイルを再読したうえで docs-check を実施。
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/diagnostics.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。

## Stream H docs群1 serial cycle (2026-04-18)

### Phase 1 Read
- 対象ファイルを再読し、`Audience / Goal / Non-goal / Public boundary / Outcome / Related` の整合を確認した。
- Scopeを docs-only に固定し、編集禁止対象（`security.md` / `security_operational_guidelines.md` / shared files）へ非接触であることを確認した。

### Phase 2 Plan
- 1Phase1責務で進行し、変更は「実行記録の同期」と「公開境界の維持」に限定する。
- AC/DoD不足があれば先に補完提案し、未合意の新規仕様決定は持ち込まない。

### Phase 3 Execute（1ファイル直列）
- Classification: **Improve external**
- 04_Documentation/diagnostics.md は公開可能な診断手順に限定し、内部監査詳細は持ち込まない。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/diagnostics.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。

## DOC-OPS-05 Stream J2 execution record (2026-04-18)

### Phase 1: Read
- Target issue scope and this document were re-read to confirm Audience / Goal / Public boundary.
- Classification remains **Improve external** and no Stream H-owned file edits are required.

### Phase 2: ADR CDC
- CDC update is **not required** because the existing placement policy is within current DOC-OPS-05 decisions.

### Phase 3: Plan
- AC/DoD補足: 分類根拠（Audience/Goal/公開境界）・次アクション・検証一致（docs-check）を1セットで記録する。
- 次アクション固定: 公開runbookとして契約・フォールバック説明を維持する。

### Phase 4: Execute
- docs-onlyで本ファイルのみを更新し、実装仕様変更は行わない。

### Phase 5: Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|DOC-OPS-05 Stream J2" 04_Documentation/diagnostics.md`
- `git diff --check`
- Self-correction policy: max 3 attempts, then stop and reassign if unresolved.

### Phase 6: Proceed
- 判定: **Ready**
- 根拠: 分類根拠・次アクション・検証一致を同一文書内で追跡可能。


## Stream H serial cycle（2026-04-19 / DOC-OPS-05-04）

### Phase 1 Read
- `issue-doc-ops-05-04` と本書を再Readし、Classification=**Improve external** と DecisionStatus=Fixed を確認。

### Phase 2 ADR CDC
- 追加ADR不要。公開runbook方針を維持。

### Phase 3 Plan
- AC/DoD不足なし。契約/フォールバック/決定論の公開品質を維持。

### Phase 4 Execute
- 公開境界内で文書整備を継続し、内部監査詳細は対象外とした。

### Phase 5 Verify
- docs-check（語彙整合・関連参照・`git diff --check`）を実施。
- 自己修復上限3回。

### Phase 6 Proceed
- 状態: **Ready**


## DOC-OPS-05-04 serial run log（2026-04-19）

### Phase 1 Read
- Read対象: `04_Documentation/diagnostics.md` と対応Issue `01_Plans/issues/issue-doc-ops-05-04-04doc-diagnostics.md`。
- 公開境界/内部境界と `VerificationLevel=docs-check` を再確認。

### Phase 2 Plan
- 本ファイルは docs-only で局所更新し、対象外（05-06以降・共有統合3ファイル・コード）へ非接触。

### Phase 3 Execute
- 既存分類 `Improve external` と Audience/Goal/Non-goal/Public boundary/Outcome/Related を維持したまま、2026-04-19 実行ログを追記。

### Phase 4 Verify
- `rg -n "DOC-OPS-05-04 serial run log|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 04_Documentation/diagnostics.md 01_Plans/issues/issue-doc-ops-05-04-04doc-diagnostics.md`
- `git diff --check`

### Phase 5 Proceed
- 状態: **Ready**
- 次アクション: 本セット（05-01..05）内での整合維持を継続。

## Stream D execution log（2026-04-20 / DOC-OPS-05-04）

### Phase 1 Read
- 対象: `04_Documentation/diagnostics.md` と対応Issueの Requirement meta I/F を再読し、docs-only 境界を確認。
- 判定: Classification=`Improve external` を維持し、編集禁止範囲（README / dashboard / decision-pack / 実装コード）へ非接触。

### Phase 2 Plan（AC/DoD不足補完）
- AC補完: Audience / Goal / Non-goal / Public boundary / Outcome / Related と Go/No-Go 判定導線が追跡可能であること。
- DoD補完: Read → Plan → Execute → Verify → Proceed の5Phase記録を残し、Verifyは docs-check 手順を明示すること。

### Phase 3 Execute
- 既存の分類方針と公開境界メタを維持し、DOC-OPS-05前半（01〜05）の同期記録を本節へ追加。
- 非目標を維持し、仕様正本（00〜02）の上書き・実装変更は行わない。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream D execution log" 04_Documentation/diagnostics.md 04_Documentation/diagnostics.md`
- `git diff --check`
- 失敗時は自己修復を最大3回まで。4回目相当は停止して Hold とする。

### Phase 5 Proceed（残課題記録）
- 状態: **Ready**
- 残課題: worker契約更新時は schemas / worker実装参照と同時にdocs同期を行う。


## DOC-OPS Track 2 serial cycle（2026-04-22 / 05-04 linked）

### Phase 1 Read（同期）
- 本文と対応Issue（`issue-doc-ops-05-04-04doc-diagnostics.md`）を再読し、Improve external方針を確認。

### Phase 2 ADR/CDC（承認待ち）
- Context: diagnosticsは公開契約文書として、再現可能性と公開境界の両立が必要。
- Decision（提案）: 本書は契約・fallback・決定論条件の説明に限定し、内部進行ログの混在を避ける。
- Consequences: 参照性は向上するが、最終固定はレビュー承認まで **Pending approval**。

### Phase 3 Plan
- Plan: schemaVersion/fallback/requestId isolation/structural metrics の追跡可能性を維持する。

### Phase 4 Execute
- Track 2 の6Phase運用記録を本文に追記（docs-only）。

### Phase 5 Verify
- `rg -n "DOC-OPS Track 2 serial cycle|Pending approval|Phase 2 ADR/CDC" 04_Documentation/diagnostics.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Proceed（承認待ち）**
- 自己修復: 最大3回、超過時は停止。

## DOC-OPS Track 2 follow-up cycle（2026-04-22 / 05-04 ownership）

### Phase 1 Read（再同期）
- `04_Documentation/diagnostics.md` と `01_Plans/issues/issue-doc-ops-05-04-04doc-diagnostics.md` を再読し、Classification=`Improve external` を再確認。
- docs-only / 指定外ファイル非編集 / Verify自己修復上限3回を固定条件として再宣言。

### Phase 2 Plan（ワークフロー固定）
- Plan-1: Audience / Goal / Non-goal / Public boundary / Outcome / Related の追跡可能性を維持。
- Plan-2: `schemaVersion` / `requestId` / fallback / structural metrics の契約導線を維持。
- Plan-3: Verifyは docs-check（`rg` + `git diff --check`）のみで再現可能にする。

### Phase 3 Execute
- Track 2 follow-up の5Phase記録を追記し、公開runbook境界の維持を明文化。

### Phase 4 Verify
- `rg -n "DOC-OPS Track 2 follow-up cycle|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 04_Documentation/diagnostics.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**
- フェイルセーフ: Verify失敗時の自己修復は最大3回。超過時は **Hold** として停止。


## Stream J serial cycle（2026-04-26 / DOC-OPS-05-04）

### Phase 1 Read
- 本文と対応Issue（DOC-OPS-05-04）を再読し、Classification=Improve external と docs-check 前提を確認。

### Phase 2 ADR/CDC
- Context: diagnostics は外部運用者が参照する診断仕様であり、内部実行ログとは分離が必要。
- Decision: 本書を「診断仕様の正本」として維持し、運用履歴は verification log 側へ分離する。
- Consequences: 本書の更新は仕様・期待結果・フォールバック記述に限定され、日付付き実測ログは記載しない。

### Phase 3 Plan
- AC補完: Audience/Goal/Public boundary/Outcome/Related を冒頭メタで追跡可能にする。
- DoD補完: docs-check（メタ/導線/体裁）に合格し、6Phase記録を残す。

### Phase 4 Execute
- Stream J の6Phase記録を追記（docs-only、最小差分）。

### Phase 5 Verify
- `rg -n "Stream J serial cycle|Phase 2 ADR/CDC|diagnostics は外部運用者" 04_Documentation/diagnostics.md`
- `git diff --check`
- 修復回数: 0/3

### Phase 6 Proceed
- 判定: **Ready**


## Stream G mini-Phase serial run（2026-04-27）

### Phase 1 Read
- 対応Issue（`DOC-OPS-05-04`）と本書の分類ヘッダを再読し、公開境界を確認。

### Phase 2 Plan
- 変更責務を docs-only の記録同期に限定し、本文の分類（Move internal / Improve external）を維持。
- 共通ACテンプレ（Scope固定 / 境界明示 / GoNoGo / docs-check / 3回上限）を適用。

### Phase 3 Execute
- 本節を追記し、Read→Plan→Execute→Verify→Proceed の直列実行証跡を固定。
- 指定外ファイル・実装コード・共有統合ファイルは未編集。

### Phase 4 Verify
- `rg -n "DOC-OPS|Classification|Audience|Goal|Public boundary|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/diagnostics.md`
- `git diff --check`
- self-repair count: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（分類方針と公開境界を維持）。

## Stream E共通: Draft課題のOpen化条件（DOC-OPS-05）

- 本文書で扱う Draft 課題は、次の **5条件をすべて満たした場合のみ Open 化** する。
  1. **Read**: 対象本文書と上位根拠（00〜02、必要なADR）を再読し、参照差分を列挙済み。
  2. **Plan**: Scope / Non-Goals / Acceptance / Validation / Stop Conditions を明文化済み。
  3. **Execute**: docs-only 境界（実装コード非変更）を維持し、allowlist 外の差分が 0。
  4. **Verify**: 再現可能な docs-check コマンドと結果（成功/未実施理由）を記録済み。
  5. **Proceed**: Go/No-Go/Conditional を明示し、未確定事項を「決定」扱いせず次アクションに分離済み。
- 未確定事項は `TBD` / `Assumption` / `Decision Needed` で明示し、**承認前に仕様確定文へ昇格しない**。
- 自己修復（同一原因への再試行）は最大3回まで。4回目相当は Stop とし、Open 化を保留する。



## Stream F targeted quality uplift (2026-05-07)

### Read → Plan(AC/DoD補完) → Execute → Verify → Proceed
- Read: 本文の判定語彙（Go/NoGo, Proceed/Hold/Stop, pass/fail/blocked）と依存状態を再確認した。
- Plan: AC/DoD の不足項目を「単体再読で判定できるか」「docs-checkで検証できるか」に限定した。
- Execute: 本文の目的・非目的・停止条件を明示し、推測での gate確定を禁止した。
- Verify: docs-check 前提を維持し、自己修復上限を 3 回に固定した。
- Proceed: gate未確定事項は Hold 維持、Assumption/TODO を明示して停止する。

### AC/DoD delta（補完）
- AC-Delta-1: 判定語彙を 1 セット（Go/NoGo, Proceed/Hold/Stop, pass/fail/blocked）に固定。
- AC-Delta-2: 依存未確定時の扱いを `ProceedDecision: Hold` として明示。
- DoD-Delta-1: `self-correction <= 3` を超える場合は `Stop`。
- DoD-Delta-2: gate未確定事項は推測せず、TODO/Assumptionを残して停止。

### Stopper handling（推測禁止）
- TODO: `DOC-OPS-05` Open gate の最終承認証跡（日時/承認者/evidence link）確定待ち。
- TODO: 05-05/05-06/05-07 の Proceed 再判定日の同期。
- Assumption: 依存Issueの最終合意までは本Draftの分類（Move internal / Improve external）を暫定維持する。

