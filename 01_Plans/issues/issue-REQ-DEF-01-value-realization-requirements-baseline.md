# Issue Draft: REQ-DEF-01 価値実現に向けた要求ベースライン定義

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Product Owner + Platform Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0010`, `ADR-0011`, `ADR-0012`, `02_Architecture/architecture.html`
- Dependencies: N/A
- Expected verification level: `docs-check`


## Requirement meta I/F（REQ-DEF共通キー：最終固定）

> REQ-DEF-01/02/03 の編集分離用に、本文より先にこのキーセットを最終固定する。
> **本Issueを正本（canonical source）** とし、他REQは下記キー名へ準拠する。

| Canonical key | Value / Enum | 必須 | I/F上の扱い |
| --- | --- | --- | --- |
| `RequirementID` | `REQ-DEF-xx` | Yes | 変更禁止（要求識別子） |
| `RequirementStatement` | 要求本文（1要求1文を推奨） | Yes | レビュー/実装が参照する主文 |
| `PriorityClass` | `Must` / `Should` / `Could` | Yes | 優先固定対象の判定キー |
| `RACI` | `A/R/C/I` の役割割当 | Yes | 責任分界点の正規表現 |
| `ContractImpact` | `schema/api/policy/ops` ごとに `あり/なし` | Yes | 変更契約の影響面を明示 |
| `AcceptanceScenario` | `前提/操作/期待結果/除外` | Yes | 受入判定の最小単位 |
| `VerificationLevel` | `docs-check` / `unit` / `integration` / `e2e` | Yes | 検証粒度の宣言 |
| `DecisionStatus` | `Fixed` / `Pending` | Yes | 確定/未確定の状態管理 |
| `DecisionQueueRef` | `Pending-<n>`（未確定時のみ） | Conditional | `DecisionStatus=Pending` のとき必須 |

### REQ依存（REQ-DEF-02/03）向け互換ルール

- 許容する表記ゆれ（例: `Requirement ID`, `Priority class`）は、レビュー時に**上記canonical keyへ読み替えて評価**する。
- 本Issue完了条件は、REQ-DEF-02/03の本文修正ではなく、**依存先が参照可能な正規キー定義を確定**すること。
- したがって本タスクでは REQ-DEF-02/03 本文を編集しない（スコープ外）。

### DecisionQueue運用（REQ-DEF共通）

1. `DecisionStatus=Pending` を設定した時点で `DecisionQueueRef` を必須記入する。
2. `DecisionQueueRef` は `Pending-<連番>` 形式で、同一Issue内で一意とする。
3. Pending項目には「未確定理由 / 解除条件 / 次判断者」を1行で添える。
4. `VerificationLevel` が宣言済みでも、`DecisionStatus=Pending` の要求は「検証完了」扱いにしない。
5. 他REQへ依存する未確定事項は「参照のみ」で連携し、依存先本文の直接編集は行わない。

## 1) 課題 / Problem statement

- 価値原則（ADR-0010）と要求マッピング（ADR-0011）は存在するが、直近の実行優先度で「どの要求を先に固定するか」の合意が不足している。
- Phaseごとの計画（ADR-0012）と実装入口（03_Implement）の間で、要求の凍結範囲が曖昧なため、Issue分解時にスコープドリフトが発生しやすい。
- 人間レビュー時に「価値に対して何が未定義か」を即時判断しづらい。

## 2) 背景 / Context

- AGENTSのRead Orderは上流優先（00→01→02→03）を要求している。
- 価値実現の中核要件（保留尊重、反スコアリング、レビュー追跡、safeMode既定ON）は固定済みだが、要求定義フェーズの壁打ち成果をIssueへ転写する型が不足している。
- `01_Plans/issues/README.md` の運用では、Acceptance/Validation先行固定が必須となっている。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 価値→要求→Issue の変換ロスを減らし、価値実現速度を上げる。
- 安全（THREAT_MODEL / SafeMode）: 要求定義時点で安全境界を固定し、後工程での例外導入を抑制する。
- 企業・行政要件（enterprise_architecture）: 責務分離と監査説明可能性を要求文脈で先に整理できる。
- 後方互換（schemas）: スキーマ変更の有無を要件段階で判定し、互換リスクを先出しできる。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（要求ベースライン定義）。
- 変更の最小単位:
  - T1: 価値原則と要求ID（UX/DATA/AI）の優先固定対象を定義する。
  - T2: 要求ごとの「責任分界点（人間/AI/システム）」を明示する。
  - T3: 要求未確定項目をDecision Queueへ移送する運用ルールを固定する。
- 非目標:
  - Frontend/Backend/Schema の実装変更。
  - 新規価値原則の追加。
  - REQ-DEF-02/03 本文の直接編集。

## 5) 受入条件 / Acceptance criteria

- [x] 価値原則P-01〜P-07に対して、優先固定対象要求（UX/DATA/AI）が明示される。
- [x] 各要求に責任分界点（決定者/実装者/検証者）が紐づく。
- [x] 未確定要求をDecision Queueへ送る判定条件（いつ止めるか）が定義される。
- [x] SafeMode既定ONと漏えい防止（share/export）を弱めない非改変条件が明文化される。
- [x] docs-check の検証コマンドと期待結果が記録される。
- [x] Requirement meta I/F の正規キーが camel-case で最終固定され、他REQが参照できる。
- [x] `DecisionStatus` と `DecisionQueueRef` の相互必須条件（Pending時必須）が明文化される。

## 5.1 判定基準（value→requirements→acceptance 連鎖）

- 判定基準-1（Value整合）: `ADR-0001` の価値原則（P-01〜P-07）と `PriorityClass` が1対1で追跡可能であること。
- 判定基準-2（Requirement整合）: 各要求が `RequirementStatement` と `RACI` を持ち、責務境界が未定義でないこと。
- 判定基準-3（Acceptance整合）: 各要求が `AcceptanceScenario` と `VerificationLevel` を持ち、検証不能要求が残っていないこと。
- 判定基準-4（Fail-safe）: 価値定義と受入基準の不整合を検出した場合、Proceedせず停止しDecision Queueへ移送すること。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 価値原則ごとの要求優先度（Must/Should/Could）を策定する。
- [x] T2: 要求ごとのRACI草案を作成する。
- [x] T3: 未確定要求の停止基準とエスカレーション条件を策定する。
- [x] T4: 固定済み要求を具体Issueへ分割するための計画を明文化する（REQ-DEF-02/03本文編集は本Issueの禁止範囲）。

### T4 分割計画（明文化）

#### Plan（分割対象・依存先宣言）

- 分割対象A（REQ-DEF-02依存）: `RACI` / `ContractImpact` を中心に、責任分界点と契約境界チェックポイントを受け渡す。
- 分割対象B（REQ-DEF-03依存）: `AcceptanceScenario` / `VerificationLevel` / `DecisionStatus` を中心に、受入シナリオとIssue分割運用を受け渡す。
- 依存順序: 先に本Issueの canonical key を固定し、その後に REQ-DEF-02（責任境界）→ REQ-DEF-03（受入と分割運用）で展開する。
- AC/DoD不足の補完提案（本Issue内で先行反映済み）:
  1. ACに「共通I/Fキー最終固定」「Pending時の `DecisionQueueRef` 必須」を保持する。
  2. DoDに「REQ-DEF-02/03 が参照可能な互換読み替え規則」を保持する。

#### Execute（分割基準・引き渡しI/F・停止条件）

- 分割基準:
  1. `PriorityClass` は本Issueで固定し、優先分類の再解釈を下流Issueへ持ち込まない。
  2. `RACI` / `ContractImpact` は REQ-DEF-02 で具体化するが、キー定義の追加・改名は行わない。
  3. `AcceptanceScenario` / `VerificationLevel` は REQ-DEF-03 で具体化するが、`DecisionStatus` 運用と矛盾させない。
- 引き渡しI/F:
  - REQ-DEF-02/03 は本Issueの「Requirement meta I/F（REQ-DEF共通キー：最終固定）」を唯一の参照元として扱う。
  - 受け渡し時の必須項目は `RequirementID` / `RequirementStatement` / `PriorityClass` / `DecisionStatus` の4点を最低セットとする。
- 停止条件（Fail-safe）:
  1. REQ-DEF-02/03本文の直接編集が必要になった時点で本Issueでの作業を停止し、理由を記録する。
  2. canonical key の再定義が必要と判明した時点で停止し、上流（ADR/Template）改訂提案へ切り替える。
  3. Self-Correction が3回を超える見込みになった時点で停止し、未完了理由を報告する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "REQ-DEF-01|価値実現|責任分界点|Decision Queue" 01_Plans`
- 期待結果:
  - issue memo validator が成功し、要求ベースライン定義の記述が検索可能である。
- 未実施時の理由・代替検証:
  - Python未導入時は `rg` と目視レビューで代替し、理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既存ADRだけを参照し、要求ベースライン文書を追加しない。
  - 却下理由: 実行優先度と責任分界が曖昧なまま残る。
- 代替案B: 実装Issueを先に作り、要求定義を後追いする。
  - 却下理由: 上流未確定のまま下流着手となり、手戻りが増える。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 要求の粒度が粗すぎて、具体Issueに落とせない。
- 影響範囲: `01_Plans/` と関連するArchitecture文書の参照整合。
- ロールバック手順: 追加した要求優先度の分類を撤回し、既存ADR参照のみへ戻す。

## 9.1 分割戦略（REQ-DEF共通判定軸の引き渡し）

- 分割単位:
  1. `責務境界` は REQ-DEF-02 へ引き渡す（RACI/ContractImpactの詳細化）。
  2. `受入・検証` は REQ-DEF-03 へ引き渡す（AcceptanceScenario/VerificationLevelの詳細化）。
- 分割ルール:
  - 本Issueは canonical key と停止条件の固定のみを担当し、下流Issueの再定義を許可しない。
  - 判定軸が競合した場合は `REQ-DEF-01` を正本として上書き統合する。
- 分割完了条件:
  - REQ-DEF-02/03 が本Issueの判定軸（key名/停止条件）を参照し、矛盾が0件であること。

## Definition of Done（DoD）

- [x] 共通I/Fキーが本Issue先頭と `01_Plans/issues/TEMPLATE.md` の双方で同一表記になっている。
- [x] ACに「安全（SafeMode既定ON/漏えい防止）」「検証（docs-check）」が含まれ、チェック状態が整合している。
- [x] 非目標に `REQ-DEF-02/03` 直接編集禁止が反映され、スコープ逸脱を防いでいる。
- [x] Decision Queueの未確定項目が `DecisionStatus=Pending` と対応づけ可能である。
- [x] REQ-DEF-02/03 のI/F依存を満たすため、正規キーと表記ゆれの読み替え規則を本Issueで固定した。

## Self-Correction Log（最大3回）

1. 修正1: 共通I/Fキーの命名をスペース区切りから固定キー（`PriorityClass` 等）へ統一。
2. 修正2: 受入条件へ SafeMode既定ON/漏えい防止の非改変条件を明示。
3. 修正3: タスクT4へ禁止スコープ（REQ-DEF-02/03本文編集禁止）を追記して逸脱を防止。

### Plan / Execute / Verify（この改訂での実施）

1. Plan
   - AC/DoD不足として「正規キー最終固定」「Pending運用必須条件」を補強対象に設定。
2. Execute
   - 本Issue内のみを更新し、canonical key表・DecisionQueue運用ルール・互換読み替え規則を追記。
3. Verify
   - docs-check相当（validator / unit test / `rg`）で文書整合と検索可能性を確認。

## 10) Additional context

- 要件定義フェーズの壁打ち結果を、Issue化可能な粒度で固定するための起点Issue。
- ADR化が必要になる条件（トレードオフ閾値）:
  1. 要求優先度分類をプロジェクト恒久ルールへ昇格する場合。
  2. RACI定義を全Backlog共通ルールとして適用する場合。


## Decision Queue（残る未確定）

- Pending-1: Must/Should/Could のレビュー承認を全Issue必須化する範囲（全Backlog適用かREQ-DEF限定か）。
- Pending-2: RACI/Contract impact を `01_Plans/issues/TEMPLATE.md` に必須昇格する時期。
- Pending-3: 要求粒度↔検証粒度マッピングを「必須」へ引き上げる運用開始日。

- Pending-4: REQ-DEF-02/03 の適用時に canonical key 以外の派生キー導入提案が出た場合、Decision Queue で事前承認する。


## Decision status sync (2026-03-08)

- REQ-DEF共通I/Fは本Issueを正本として固定し、REQ-DEF-02/03 は参照専用とする。
- 禁止範囲（REQ-DEF-02/03本文の先行編集禁止）を維持し、未確定は Decision Queue に集約する。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream I 要件契約固定パック（2026-05-18）

### Phase 1: Read同期サマリ
- 重複論点: 画面導線の分かりやすさ、SafeMode境界、検証証跡要件。
- 曖昧論点: Open化の判定条件と、依存関係が契約依存か実装依存かの境界。
- 欠落補完: 価値→要件→受入→測定の追跡行と、Draft→Open判定を明文化。

### Phase 2-3: ADR要素 + 要件契約
| Context | Decision | Consequences |
| --- | --- | --- |
| 上流価値定義（ADR-0001/0031/0032）を実装入口へ接続する必要がある。 | AC/DoDを機械検証可能な粒度で固定し、未確定はDecision Queueへ隔離する。 | 下流実装Streamは要件の再発明をせず、検証可能なIssue単位で着手できる。 |

### 価値→要件→受入→測定 対応表（最小）
| 価値仮説 | 要件（Requirement） | 受入条件（AC） | 測定（Evidence/KPI） |
| --- | --- | --- | --- |
| 利用者が安全に判断を共有できる。 | SafeMode境界を保持し、共有前確認を必須化する。 | SafeMode/公開範囲/未レビュー状態を実行前に提示できる。 | docs-check + E2E記録 + 文言一致確認。 |
| 要件から実装へ手戻りなく移行できる。 | AC/DoDをOpen前に固定し、未確定はPending化する。 | Draft→Open条件を満たしたIssueのみ実装に着手する。 | checklist充足率、No-Go件数、Pending解消件数。 |

### Phase 4: Draft→Open 条件（要件側ゲート）

### Phase 5-6: Verify / Proceed 引き継ぎ条件
- Verify合格条件: 価値仮説とACの1対1追跡が可能で、非検証要件が残っていない。
- Proceed条件: 実装ストリームが「どのACをどのテストで満たすか」を追加解釈なしで決定できる。
- フェイルセーフ: 上流価値定義との矛盾・非検証要件・競合編集を検出した場合はOpen化を停止する。

## Stream H addendum (2026-05-20): AC/DoD不足時のドラフト提案運用

### Read同期トリガー
- 各Phase開始時に `REQ-DEF-01/02/03` の `DecisionStatus`, `Acceptance criteria`, `Validation plan` を再読する。
- 不整合がある場合、実装要求へ進まず `AC補完ドラフト` を先に追記して合意待ちへ移行する。

### AC補完ドラフト最小テンプレ
- Gap ID:
- 欠落種別: `AC不足 | DoD不足 | Verification不整合`
- 追加提案:
- 影響範囲:
- 合意状態: `Pending | Approved | Rejected`

### Stop条件
- self-repair 3回以内で整合不能な場合は停止し、`原因/影響/再開条件` を記録する。


## 11) Stream H requirements baseline lock（2026-06-13）

- Classification: Open-ready planning rule; current memo remains Done until a new activation request reopens it.
- Value→Requirement flow: `ADR-0001` value principle → `ADR-0032/0040` product/domain value loop → requirement statement → acceptance scenario → split issue.
- AC minimum: every requirement must state the user/social value protected, the acceptance evidence type, and the non-goal that prevents early collapse or surveillance expansion.
- Scope lock: this issue defines planning rules only; it does not require implementation or documentation edits outside `01_Plans/issues/`.
