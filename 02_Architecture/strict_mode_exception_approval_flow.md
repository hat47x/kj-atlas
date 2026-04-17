# strict mode例外緩和 承認フロー仕様（AUTH-OPS-03）

- Status: Accepted (2026-03-06, D1〜D4 fixed)
- Owner: Security Officer / System Owner / Platform Operator
- Scope: `02_Architecture/enterprise_architecture.md`, `04_Documentation/operations.md`, `04_Documentation/security.md`, `04_Documentation/security_operational_guidelines.md`, `04_Documentation/e2e_testing.md`
- Related: `01_Plans/issues/issue-AUTH-OPS-03-strict-mode-exception-relaxation-runbook-plan.md`

## 0. この文書の読み方（最初にここだけ読む）

認証の専門知識が深くなくても、次の順序で読むと判断しやすい。

1. **1章（目的）**で「何を決める文書か」を把握する。
2. **4章（状態遷移）**で「どの順で処理が進むか」を確認する。
3. **6章（Q1〜Q10の選択肢）**で、未決事項を選ぶ。
4. **8章（停止/復旧）**で、止める条件と戻す条件を確認する。

---

## 0.5 登場人物（先に確認）

- **Security Officer**: セキュリティ妥当性を判断する責任者。
- **System Owner**: 業務継続上の妥当性を判断する責任者。
- **Platform Operator**: 設定変更と運用記録を行う実行担当。

## 1. 目的

`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` を本番標準（strict）としつつ、
例外的に `true` へ緩和する際の**承認フローを設計レベルで固定**する。

この文書の役割は次の2つ。

1. 人間が「何を決めれば作業開始できるか」を短時間で判断できること。
2. AIエージェントが推測で承認フローを補完せず、停止条件を守れること。

---

## 1.0.1 DOC-OPS-02 同期順序（固定）

AUTH-OPS-03 / DOC-OPS-02 の文書同期は、次の順序を固定する。

1. `02_Architecture/strict_mode_exception_approval_flow.md`（本書 / 正本）
2. `04_Documentation/security.md`
3. `04_Documentation/security_operational_guidelines.md`
4. `04_Documentation/e2e_testing.md`

`04_Documentation/operations.md` は実行runbookとして **常に整合確認対象** とし、D1〜D4・役割語彙・状態語彙の一致を維持する。

## 1.1 ミニ用語集（この文書で使う言葉）

- **strict**: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` の状態。未登録主体を拒否する。
- **例外緩和**: `...=true` に変更して運用すること（短期運用か恒常運用かはプロファイルで区別）。
- **承認フロー**: 例外緩和を実施してよいかを決める手順。
- **復旧**: 例外終了後に `...=false` へ戻すこと。
- **Q1〜Q10**: 現在未確定の運用判断項目（順序、TTL、代理承認など）。

---

## 2. 非目標

- コードで承認バイパスを実装すること。
- 監査スキーマへPIIを追加すること。
- 既存のSafeMode/read-only優先順位を変更すること。

---

## 3. 固定済み契約（変更不要）

以下は既存文書で確定しているため、本仕様では再決定しない。

- strict標準: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`。
- strict標準では、例外緩和は通常「一時変更」として扱う。
- ただし組織ポリシーにより `true` を恒常採用する場合は、本書の「例外フロー」ではなく、別途「公開運用プロファイル」を定義して審査・監査する。
- 2者承認責務: Security Officer + System Owner。
- 実行責務: Platform Operator（承認済み変更のみ実行）。
- 監査最小項目: `時刻 / 理由 / 承認者 / 対象環境 / 復旧条件`。
- PII非保存（subject生値、roles/groups/policyRef生値、自由記述PII）。

---

## 3.1 運用プロファイルの選択（追加）

本書は主に **strict標準 + 例外フロー** を扱う。
ただし、データ機密性や運用方針により、次の2プロファイルを選択できる。

1. **strict標準プロファイル（推奨既定）**
   - `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` を通常運用とし、`true` は承認付き一時運用。
2. **公開運用プロファイル（条件付き）**
   - `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` を継続運用する。
   - SNS的な多ユーザ閲覧など、事前登録制を維持しづらいケースを想定。
   - この場合は、アクセス境界・監視・フェイルセーフ・定期レビューの補完統制を、別文書の運用ガイドラインとして提示する。

> 重要: どちらのプロファイルでも SafeMode既定ON、PII最小化、監査最小化契約は維持する。
> 具体運用は `04_Documentation/security_operational_guidelines.md` を参照する。

---

## 4. 設計全体像（状態遷移）

```text
DraftRequest
  -> ApprovalPending
  -> Approved
  -> ActiveException
  -> RollbackPending
  -> Closed

(any state) -> StoppedForClarification  (未確定項目が実施に必須の場合)
(any state) -> Rejected                 (承認却下)
```

### 4.1 状態定義（平易版）

- `DraftRequest`: 申請を書き始めた段階（まだ承認判定できない）。
- `ApprovalPending`: 2者承認待ち。
- `Approved`: 承認済みだが、まだ設定変更は実行していない。
- `ActiveException`: `...=true` が適用中。
- `RollbackPending`: 戻し作業待ち（期限到来/停止条件成立）。
- `Closed`: `...=false` へ戻し、記録も完了。
- `StoppedForClarification`: 未確定事項があるため実行停止。
- `Rejected`: 承認却下で終了（再申請は新しい requestId で実施）。

### 4.2 強制ガード（Fail Fast）

- 承認情報が欠損している場合、`Approved` へ遷移してはならない。
- 復旧記録が未完了の場合、`Closed` へ遷移してはならない。
- `StoppedForClarification` 中は `ActiveException` へ遷移してはならない。

### 4.3 1件の申請を追う例（時系列）

1. Operator が `DraftRequest` を作成。
2. Security Officer と System Owner が承認し `ApprovalPending -> Approved`。
3. Operator が設定変更を実施し `ActiveException`。
4. TTL到達または停止条件成立で `RollbackPending`。
5. `...=false` へ戻して記録を完了し `Closed`。

---

## 5. 役割分離（RACI）

| タスク | Security Officer | System Owner | Platform Operator |
|---|---|---|---|
| 申請妥当性レビュー（安全） | A/R | C | I |
| 申請妥当性レビュー（業務継続） | C | A/R | I |
| 例外発動実行 | I | I | A/R |
| 復旧実行（strict復帰） | C | C | A/R |
| 監査記録の整合確認 | A | A | R |

凡例: A=Accountable, R=Responsible, C=Consulted, I=Informed

> ポイント: 承認（A/R）と実行（A/R）を分離し、単独判断で緩和が常態化しないようにする。

---

## 6. Q1〜Q10 決裁結果（AUTH-OPS-03 固定値）

> 人間判断により Q1〜Q10 の運用値を次で固定する。
> 本節の値と異なる運用を行う場合は、新しい requestId で再承認する。

### 6.1 承認順序 / 承認TTL（Q1, Q2）

- **採択: A**（Security Officer先行、承認TTL=4h）

### 6.2 適用スコープ / 例外最大継続時間（Q3, Q4）

- **採択: A**（tenant単位、最大2h、TTL超過で自動strict復帰）

### 6.3 復旧判定者 / 代理承認（Q5, Q6）

- **採択: A**（復旧判定は2者共同、代理承認なし）

### 6.4 保存先 / 再申請 / 事後レビュー / 違反SLA（Q7〜Q10）

- **採択: A**（変更台帳+監査ID相互参照、48hレビュー、15m一次/60m二次エスカレーション）

### 6.5 採択記録フォーマット（必須）

```md
[Approval Flow Decision Record]
- Date (UTC):
- Decider(s):
- Selected options: Q1-2=A, Q3-4=A, Q5-6=A, Q7-10=A
- Rationale:
- Effective from:
- Review date:
```

### 6.6 決めきれない場合の扱い

- 「未決のまま実行」は禁止。
- 未決項目が1つでも実施判断に影響する場合は `StoppedForClarification`。
- 停止中は `...=true` を適用しない。


### 6.7 決裁記録（確定）

[Approval Flow Decision Record]
- Date (UTC): 2026-03-06
- Decider(s): Security Officer, System Owner, Platform Architecture Owner
- Selected options: Q1-2=A, Q3-4=A, Q5-6=A, Q7-10=A
- Rationale: strict既定運用を維持しつつ、例外運用時間・承認期限・監査SLAを最小化して誤運用余地を縮小する。
- Effective from: 2026-03-06
- Review date: 2026-06-30

### 6.8 D1〜D4 決定固定（実務で参照する要約）

| Decision ID | 決定テーマ | 固定値 | 実務メモ |
|---|---|---|---|
| D1 | 承認順序 / 承認TTL | Security Officer先行、承認TTL=4h | 4h以内に2者承認が揃わない申請は失効。 |
| D2 | 適用スコープ / 例外最大継続時間 | tenant単位、最大2h | 2h経過時は自動で strict 復帰へ遷移。 |
| D3 | 復旧判定者 / 代理承認 | 2者共同判定、代理承認なし | 代理承認は常に不可（緊急時も再申請）。 |
| D4 | 保存先 / 事後レビュー / 違反時SLA | 変更台帳+監査ID相互参照、48hレビュー、15m一次/60m二次エスカレーション | SLA違反はインシデント管理へ接続。 |

---

## 7. 最小データ契約（実行記録）

```json
{
  "requestId": "AUTH-OPS-03-YYYYMMDD-###",
  "state": "ActiveException | Closed | StoppedForClarification | Rejected",
  "approvedBy": ["security_officer_id", "system_owner_id"],
  "executedBy": "platform_operator_id",
  "startedAt": "UTC timestamp",
  "rollbackBy": "UTC timestamp",
  "endedAt": "UTC timestamp | null",
  "targetEnvironment": "prod|stg|dev",
  "reasonCode": "predefined enum",
  "policyRefPresent": true
}
```

制約:

- `approvedBy` は2者必須（重複不可）。
- `policyRefPresent` は存在フラグのみ（生値保存禁止）。
- 自由記述フィールドに個人識別子を含めない。

---

## 8. 運用停止・復旧ルール

### 8.1 停止条件

次のいずれかで `StoppedForClarification` へ遷移する。

- Q1〜Q10の未確定項目が、発動/復旧判定に必要。
- 2者承認の片方が不在で代理承認条件が未定義。
- 監査保存先が不明で記録責務を満たせない。

### 8.2 復旧条件

`ActiveException` 中に次のいずれか成立で strict復帰を実行する。

- 承認TTL到達。
- 例外最大継続時間到達。
- Security Officer または System Owner が停止指示。
- 監査記録不整合が発見された。

### 8.3 復旧完了判定

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ復帰済み。
- `endedAt` と復旧理由が記録済み。
- 事後レビューの期限と担当が記録済み。

### 8.4 停止条件と復旧条件の非矛盾ルール

- 停止条件は「例外を有効化してよいか」の判定にのみ使用し、1つでも成立した時点で `ActiveException` へ遷移しない。
- 復旧条件は「すでに有効な例外を strict に戻す」判定にのみ使用し、1つでも成立した時点で `RollbackPending` へ遷移する。
- 停止条件と復旧条件の両方が同時に成立した場合、優先順位は `復旧実行 > 停止記録` とする（先に strict 復帰を完了させる）。

---

## 9. 実装/文書反映トレース

1. 本書でQ1〜Q10の採択結果を確定する。
2. `02_Architecture/enterprise_architecture.md` の 4.5節へ採択値を同期する。
3. `04_Documentation/operations.md` のRunbookテンプレへ採択値を反映する。
4. `04_Documentation/security.md` の停止条件・監査項目へ採択値を反映する。
5. `01_Plans/issues/issue-AUTH-OPS-03-...` を `Draft -> Open` へ更新する。

## 10. AUTH-OPS-03 状態更新方針（Issue/Dashboard共通）

| 状態 | 移行条件 | 必須エビデンス |
|---|---|---|
| Draft | D1〜D4 のうち1つでも未確定 | 未確定項目の列挙 |
| Open | D1〜D4確定、反映先未同期 | 本書6.8節の固定値 |
| In Progress | `enterprise_architecture.md` / `operations.md` / `security.md` へ同期開始 | 同期差分への参照 |
| Done | 3文書同期 + dashboard/issue README/decision-pack が整合 | docs-check結果と最終要約 |

本方針により、AUTH-OPS-03 は「決定固定だけでDoneにしない」。運用文書同期と進捗管理同期の両方が完了した時点で Done とする。
