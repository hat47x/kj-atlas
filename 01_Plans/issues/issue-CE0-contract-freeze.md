# Issue Draft: CE0 Contract Freeze（ACCI + Graph Contract）

- Type: Process
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `00_Prompt/ai_cognitive_externalization_requirements.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE0-CONTRACT-FREEZE`
- RequirementStatement: ACCI方式・Guard-01〜05・CG-01〜05 を文書横断で凍結する。
- PriorityClass: Must
- AcceptanceScenario: 前提=ADR-0028更新済 / 操作=契約ID同期 / 期待結果=定義衝突0件 / 除外=実装コード変更
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- Stream: `B` (Contracts only / Docs-Plan only)
- DecisionQueueRef: `UNC-VSC-CE-01-01`, `UNC-VSC-CE-02-01`


## 0) Phase 1 Read（I/F必須項目抽出 + mock前提確認）

- CE0必須I/Fキーを `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` に固定し、後続Issueの再定義を禁止する。
- CE1/CE2/CE4 は **実装待機禁止** とし、依存は `mock I/F` で切断して契約検証を先行する。
- CE3（実装レーン）へ渡す情報は本Issueの Contract ID Matrix を参照専用で利用する（本Issueで実装詳細は扱わない）。

## 1) Context

- CE-1以降の実装で参照する契約が複数文書に散在しており、語彙ズレ（Core/Consensus、reviewed/unreviewed、safeMode）が発生しやすい。
- ADR-0028 の CE-0 は「設計前固定」を要求しており、実装着手前に I/F と禁止事項を先に凍結する必要がある。

## 2) Decision

### 2.1 責務境界（Responsibility）

- CE0が固定する対象:
  - 認知外在化AIの最小契約（ContextQuery/ContextBundle/PatchProposal）
  - Graph責務境界（Working / Projection / Consensus）
  - 安全境界（safeMode既定ON・unreviewed保護・auto-apply禁止）
- CE0が固定しない対象:
  - API詳細スキーマ・CLI引数・UI配置・モデル選定・RBAC実装

### 2.2 入出力境界（Input / Output）

- 入力（許可）:
  - `document/view/patch` の正規入力のみ
  - ContextQuery（`goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode`）
- 出力（許可）:
  - Patch Proposal（`proposalId + diff + rationale`）
  - 監査4点セット（`query/bundle/proposal/apply`）
- 出力（禁止）:
  - Consensus Graphへの直接書込
  - `human_reviewed` の自動昇格
  - Query Previewを通さない送信経路

### 2.3 CE-0 Contract ID Matrix（固定）

| Contract ID | Responsibility | Input | Output | Prohibitions |
| --- | --- | --- | --- | --- |
| `CE0-CTX-IF` | ContextQuery/ContextBundle最小I/Fを固定 | `goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode` | deterministic `bundleHash` を持つ ContextBundle | Query Previewバイパス、非決定論bundle |
| `CE0-SAFEMODE-IF` | safeMode既定ONと未レビュー保護を固定 | `safeMode=true` 時のreview state情報 | `allowUnreviewedText=false` を既定適用 | 未レビュー本文のAI入力混入、保護緩和 |
| `CE0-REVIEW-IF` | review状態遷移の責務境界を固定 | `human_reviewed`/`unreviewed` state | 人手操作でのみ `human_reviewed` 昇格 | AIによるreview自動昇格 |
| `CG-01..05` | Working/Projection/Consensus責務固定 | KJ構造 + query constraints + actor/modelTier | proposal-only運用（patch+approval経由） | Consensus直接更新、監査欠損成功扱い |

### 2.4 AC/DoD補強ドラフト（Phase 3: Plan）

- 追加AC（ドラフト→本Issueで採用）:
  - [ ] Query Preview を経由しない ContextQuery 送信経路が 0 件である。
  - [ ] `ConsensusGraph` への direct write（patch+approval 以外）が 0 件である。
  - [ ] `mode=autonomous` でも `proposal-only` 契約が明文化されている。
  - [ ] 監査4点セット（`query/bundle/proposal/apply`）欠損時は No-Go と定義される。
- DoD（CE0完了判定）:
  - Plan → Execute → Verify → Proceed の順序で記録され、各段の証跡（定義表・同期差分・検証コマンド）が残る。
  - CE0-CTX-IF / CE0-SAFEMODE-IF / CE0-REVIEW-IF / CG-01..05 の語彙が `01/02/04` で一致する。

### 2.5 Go/NoGo Key（固定）

- **Go**:
  - Query Preview 必須経路が維持される。
  - `patch + approval` 以外で Consensus 更新が発生しない。
  - SafeMode既定ON・未レビュー本文保護・review自動昇格禁止が同時に成立する。
- **No-Go**:
  - Query Preview bypass の導線が1件でも存在する。
  - direct write / auto-apply / review自動昇格を許容する記述が1件でも存在する。
  - SafeMode後退（既定OFF化・例外既定化）の兆候を検知する。

## 3) Consequences

- CE-1〜CE-4 は本Issueの Contract ID を参照し、契約再定義を禁止する。
- `safeMode` 後退、share/export緩和、Core Graph直接更新許容の兆候を検知した場合は即時No-Goとする。
- CE0完了後にのみ、実装レーンへ API/型/UI 具体化を引き渡す。

## 4) 受入条件 / Acceptance criteria

- [ ] ACCIの5段手順が 01/02/04 で同語彙定義される。
- [ ] Guard-01〜05 の意味が文書間で一致し、禁止事項に矛盾がない。
- [ ] CG-01〜05（Consensus/Working契約）が Architecture と Ops に反映される。
- [ ] `safeMode` と `unreviewed` の後退表現が 0 件。
- [ ] Go/NoGo判定を1行で実施できる（Yes/No）。

## 5) タスク分解（文書限定）

- [ ] T1: 契約IDマトリクス表を ADR-0028 と本Issueで一致させる。
- [ ] T2: `02_Architecture` の関連文書へ語彙同期（Core→Consensus, Working, autonomous mode）。
- [ ] T3: `04_Documentation/operations.md` に運用上の禁止事項（auto-apply禁止・review昇格禁止）を明文化。
- [ ] T4: ドリフト検知コマンド結果をIssue末尾へ記録。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "Guard-0[1-5]|CG-0[1-5]|Consensus Graph|Working Graph|autonomous|safeMode|unreviewed" 01_Plans/adr 01_Plans/issues 02_Architecture 04_Documentation`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 用語不一致がなく、validatorが成功する。
- 未実施時の理由・代替検証:
  - 未実施不可（CE-0 Gate条件）。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: 語彙同期不足によりCE-1以降のI/Fが多義化する。
- ロールバック: 変更文書を契約ID単位でrevertし、ADR-0028を正本として再同期。


## 8) Phase 6 Proceed（CE3実装レーン向け参照専用I/F）

> 参照専用。CE3は以下を変更せず利用すること。

- `CE0-CTX-IF`: Query Preview必須 + deterministic `bundleHash` 前提。
- `CE0-SAFEMODE-IF`: `safeMode` 既定ON、`allowUnreviewedText=false` 既定。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみ。
- `CG-01..05`: Working/Projection/Consensus 分離、`patch + approval` 以外の適用禁止、監査4点セット必須。

フェイルセーフ（即停止）: SafeMode後退 / auto-apply許容 / 未レビュー昇格許容。
