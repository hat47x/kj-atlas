# ADR-0022: Documentation Quality Gates

- Status: Proposed
- Date: 2026-03-08
- Deciders: Project Maintainers
- Scope: `01_Plans/adr/`, `04_Documentation/`, `.github/workflows/`

## Context

DOC-OPS-04 の前処理監査では、Documentation Quality に関して以下が未統一であることが確認された。

- docs-check 運用は存在するが、`lint` / `link` / `metadata` の必須境界が文書化されていない。
- 品質確認がレビュー担当者の目視に依存し、回帰検知の一貫性が不足している。
- 例外許可（緊急対応・一時的ドリフト許容）の記録形式が固定されておらず、監査可能性が不足する。

この状態では、同一品質基準でのドキュメント更新が継続しにくく、
文書品質のばらつきと検知遅延が再発しやすい。

加えて、DOC-OPS-04 の並列タスクCとして以下が不足している。

- AC/DoD不足: AC-1〜AC-3 は定義済みだが、判定時の証跡（どのコマンド結果を根拠にするか）が明文化されていない。
- 境界不足: 必須ゲートと例外承認の境界が章内に分散し、Context/Decision/Consequences を横断したときに読み替えが必要になる。
- I/F不足: ADR-A（DOC-OPS-04 情報設計I/F）の「比較可能な判定入力」に合わせた Verify/Proceed の固定出力が未定義である。

本ADRでは上記不足を補完し、AC/DoD判定に必要な最小証跡と境界表現を固定する。

## Decision

Documentation 変更に対する品質ゲートを、**必須ゲート・警告ゲート・例外承認フロー**の3層で定義し、
品質基準と例外運用を分離管理する。

### 0. Acceptance Criteria / Definition of Done

本ADRを「運用開始可能」と判定する最低条件を以下に固定する。

- AC-1（境界明確性）:
  - 必須/警告/例外の判定境界が文面で明示され、レビュー担当者が同じ結論に到達できる。
- AC-2（例外監査性）:
  - 例外記録の必須項目（理由・期限・責任者・解消Issue）が固定され、欠落時は承認不可と定義される。
- AC-3（移行可能性）:
  - Phase 1〜3 の段階導入が定義され、既存 docs-check との差分棚卸し手順が含まれる。

DoD（本ADRの完了定義）は、上記 AC-1〜AC-3 を満たしたうえで `Consequences` と `Traceability` との整合が確認済みであることとする。

#### 0.1 AC/DoD不足への補完提案（Plan）

- 補完提案P-1（判定証跡）:
  - 追加する判定項目: 「AC判定時に実行した docs-check相当コマンドと結果ログの記録有無」
  - 区分: 必須ゲート
  - 期待効果: 判定再現性を確保し、レビュー担当者間の解釈差を減らす。
- 補完提案P-2（例外失効管理）:
  - 追加する判定項目: 「期限切れ例外の再承認有無または是正完了リンク」
  - 区分: 例外承認対象
  - 期待効果: 期限付き例外の無期限化を防止し、監査追跡を維持する。
- 補完提案P-3（継続改善入力）:
  - 追加する判定項目: 「警告ゲート再発（同一種別3回以上）の月次議題登録有無」
  - 区分: 警告ゲート
  - 期待効果: 非blocking警告を放置せず、必須化判断へ接続できる。

### 1. ゲート分類

1. 必須ゲート（merge blocking）
   - Front matter / 必須メタ情報の整合
   - 見出し構造の整合（レベル飛び・必須章欠落）
   - 参照リンク整合（内部リンク切れ）
   - 判定境界: 1件でも不一致・欠落・切れがあれば fail とし、例外承認が無い限り merge 不可
2. 警告ゲート（non-blocking）
   - 可読性スコア（文長・箇条書き密度・見出し粒度）
   - 推奨スタイル違反（用語ゆれ候補、冗長表現）
   - 判定境界: 警告件数は可視化するが、必須ゲート fail を伴わない限り merge 可
3. 例外承認対象
   - 緊急修正・外部要因で必須ゲートを一時的に満たせない変更
   - 期限付き例外として記録し、追補PRで解消する変更
   - 判定境界: 承認済み・期限内・解消Issue紐付け済みの3条件を満たす場合のみ一時通過可

### 1.1 境界違反時の扱い（必須/警告/例外）

- 必須ゲート違反 + 例外未承認: 差し戻し（merge 不可）。
- 必須ゲート違反 + 例外承認済み: 期限付きで merge 可、期限超過時は自動的に「再承認 or 是正完了」へ遷移。
- 警告ゲートのみ違反: merge 可。ただし同一種類の警告が連続3回以上発生した場合、必須化候補として月次レビュー議題に登録する。

### 1.2 品質ゲート境界の固定表現（必須/警告/例外）

Context/Decision/Consequences を通じて同一解釈にするため、境界を次で固定する。

| 境界対象 | Go条件 | No-Go条件 | 判定結果 |
| --- | --- | --- | --- |
| 必須ゲート | 必須項目が全件pass | 1件でもfail | merge blocking |
| 警告ゲート | 警告0件、または警告ありでも再発閾値未満 | 同一種別警告の連続3回以上 | merge可（ただし必須化候補として月次議題登録） |
| 例外承認（必須fail時のみ適用） | 承認済み かつ 期限内 かつ 解消Issueあり | 3条件のいずれか欠落 | merge不可（差し戻し） |

補足:
- 例外承認は「必須ゲートを恒久的に免除する仕組み」ではなく、期限付きの暫定通過のみを許可する。
- 警告ゲートは上表のGo/No-Go判定に直接影響しないが、再発時に必須化候補へ昇格しうる。

### 1.3 判定境界の機械可読プロファイル（固定値）

判定境界を実装・監査で再利用可能にするため、以下の固定値を **Gate Boundary Profile v1** として定義する。

```yaml
gate_boundary_profile:
  version: 1
  mandatory_gate:
    id: GATE-MANDATORY
    fail_threshold: 1      # fail件数が1以上でNo-Go
    decision_if_triggered: reject_unless_exception
  warning_gate:
    id: GATE-WARNING
    escalation_threshold: 3 # 同一種別の連続再発回数
    decision_if_triggered: keep_mergeable_and_register_monthly_agenda
  exception_gate:
    id: GATE-EXCEPTION
    applies_when: mandatory_gate=fail
    required_fields: [reason, due_date, owner, followup_issue]
    hard_expiry: true
    decision_if_missing_required_field: reject
```

- 本ADRで使う数値境界は `mandatory fail >= 1` と `warning recurrence >= 3` に固定する。
- `required_fields` の4項目は例外承認の最小監査項目であり、1件でも欠落した場合は例外不成立とする。

### 2. 運用原則

- 必須ゲートは CI 上で自動実行し、失敗時は merge しない。
- 警告ゲートは可視化するが、初期段階では merge blocking にしない。
- 例外は「理由・期限・責任者・解消Issue」を必須記録項目とする。
- 例外を無期限化しないため、期限切れ例外は再承認または修正完了を必須とする。

### 2.1 例外記録テンプレート（最小要件）

例外承認は、少なくとも次の構造で記録されることを要件化する。

- 対象PR/コミット
- 失敗した必須ゲート項目
- 例外理由（外部要因 / 緊急対応の分類）
- 期限（YYYY-MM-DD）
- 責任者（Role + Handle）
- 解消Issue（追補PRのトラッキング先）

上記のうち1項目でも欠落した場合は、例外承認を成立させない。

監査時の転記揺れを避けるため、例外承認は次の固定フォーマットで記録する。

```yaml
exception_approval_record:
  exception_id: EX-YYYYMMDD-<seq>
  target_ref: <PR URL or commit SHA>
  failed_mandatory_gates:
    - <gate_id>
  reason: <external_dependency|emergency_fix|other>
  approved_by: <role/handle>
  owner: <role/handle>
  approved_at: <ISO8601>
  due_date: <YYYY-MM-DD>
  followup_issue: <Issue URL/ID>
  status: approved|expired|resolved
  resolution_ref: <PR URL/commit SHA or N/A>
```

- `status=expired` かつ `resolution_ref=N/A` の記録は、その時点で `decision=reject` とする。
- `approved_by` と `owner` は同一人物でも記録可能だが、運用上は分離を推奨する。

### 3. 導入方針

- Phase 1: 既存 docs-check を必須ゲート基準へマッピングする。
- Phase 2: 欠落ゲート（metadata/link など）を段階追加する。
- Phase 3: 警告ゲートのしきい値を観測し、必要に応じて必須化判断を行う。

### 3.1 運用シーケンス（Plan → Execute → Verify → Proceed）

品質ゲート運用時は、判定ぶれを抑えるため下記の順序を固定する。

1. Plan
   - 変更対象ドキュメントと適用対象ゲート（必須/警告）を事前に宣言する。
   - 当該変更に例外の可能性があるかを先に判定する。
2. Execute
   - docs-check を実行し、必須/警告の結果を分離して記録する。
3. Verify
   - 必須違反の有無、警告の再発傾向、例外記録の必須項目充足を確認する。
4. Proceed
   - 必須違反なし: merge 進行。
   - 必須違反あり + 例外承認成立: 期限付きで進行。
   - 必須違反あり + 例外承認不成立: 差し戻し。

### 3.2 AC/DoD 不足時の補完提案ルール

運用中に AC/DoD の不足が検知された場合、以下を満たす補完提案を必須化する。

- 提案内容に「追加する判定項目」「必須/警告/例外のいずれに属するか」「期待される運用効果」を含める。
- 提案は ADR 追補または Issue として記録し、レビュー担当者の明示合意（approve）を得るまでは規約化しない。
- 合意未成立の提案は参考情報として扱い、merge blocking 判定には使用しない。

### 3.3 Self-Correction と停止条件

- 同一変更に対する自己修正（Self-Correction）は最大3回までとする。
- 3回を超えて必須違反が解消しない場合、または前提（入力仕様・依存文書・CI環境）が崩壊した場合は作業を停止し、指示待ちへ遷移する。
- 停止時は、試行回数・未解決ゲート・阻害要因を記録して引き継ぐ。

### 3.4 Verify用の再現可能コマンド要件

運用開始後のAC/DoD判定で「再現可能性あり」と判定するには、少なくとも次を記録する。

- docs-check相当の実行コマンド（例: `rg -n "^# ADR-" 01_Plans/adr` のような検査コマンド）
- 実行日時と実行結果（pass/fail）
- 必須違反時は、例外承認記録との対応ID

コマンド名そのものは運用リポジトリの実装に従ってよいが、**「第三者が同じ入力で再実行できる粒度」** を満たさない記録は無効とする。

### 3.5 Verify/Proceedの固定出力（ADR-A I/F整合）

DOC-OPS-04 の比較可能判定入力を維持するため、VerifyとProceedは次の固定フォーマットで記録する。

```text
[Verify]
mandatory_gate: pass|fail
warning_gate: pass|warn
exception_record: present|absent
evidence_commands: <再現可能コマンド一覧>
result: ready_for_proceed|blocked

[Proceed]
decision: merge|conditional_merge|reject
reason: <必須違反/例外承認状態/警告再発状況>
owner: <責任者>
due: <期限 or N/A>
followup_issue: <Issue URL/ID or N/A>
```

- `decision=conditional_merge` は「必須ゲートfailかつ例外承認成立」の場合にのみ使用できる。
- `evidence_commands` が空の場合は Verify 不成立（`result=blocked`）として扱う。

### 3.6 停止条件の判定式（Fail-safe固定化）

Fail-safeの解釈を固定するため、停止条件を次の判定式で定義する。

```text
stop_if:
  self_correction_attempts > 3
  OR mandatory_gate = fail AND exception_record = absent
  OR mandatory_gate = fail AND exception_record = present AND exception_status = expired
  OR evidence_commands = empty
```

- `stop_if` が真になった時点で Proceed は `decision=reject` 固定とし、追加修正は新しい指示があるまで停止する。
- 停止ログには `attempts`, `blocking_gate`, `exception_id(or N/A)`, `next_action` を必須記録する。

### 4. 非目標（このADRで扱わない範囲）

- 具体的なCI実装コマンドやワークフローYAMLの即時変更。
- 全文書の一括リライト。
- 可読性警告を初版から全面的に merge blocking へ昇格すること。

## Consequences

### 期待効果

- ドキュメント品質をレビュー属人性から分離し、最低品質を自動ゲートで維持できる。
- 必須と推奨を分離することで、導入初期の運用負荷を抑えつつ品質改善を継続できる。
- 例外承認の記録が標準化され、監査時の説明責任を確保しやすくなる。
- 必須/例外境界のGo/No-Go条件が固定され、Context→Decision→Consequencesで同一判定を維持できる。
- AC/DoD判定時に再現可能コマンドを必須化することで、審査の再現性を監査可能にできる。

### 副作用・制約

- 初期導入では、既存文書の不整合検出により一時的に修正負荷が増える。
- 必須ゲートの境界設計を誤ると、実務速度を不必要に低下させる可能性がある。
- 例外記録の運用が形骸化すると、品質改善サイクルが停止する。

### 移行時の対応

- docs-check 実装との差分棚卸しを行い、必須/警告の判定表を先に作成する。
- 期限付き例外テンプレートを整備し、記録形式を統一する。
- 運用開始後に月次で例外件数と再発傾向をレビューする。
- Verifyログに再現可能コマンドを必須添付し、コマンド欠落時はDoD未達として扱う。

### 成功指標（運用レビュー）

- 必須ゲート起因の差し戻し率と再発率を月次で追跡する。
- 期限切れ例外の未解消件数を 0 件維持する。
- 警告ゲートのうち頻出上位3種を四半期ごとに見直し、必須化の是非を判断する。
- 再現可能コマンド欠落による「判定保留件数」を月次 0 件へ収束させる。

## Verify

- A-I/F準拠確認:
  1. ADR必須章（Context / Decision / Consequences / Traceability）を維持。
  2. DOC-OPS-04 I/F（判定比較可能性）に合わせ、Verify観点とProceed条件を明文化。
  3. B/C/D並列ルールに従い、統合ファイル更新を行わない。
- 再現可能コマンド有無確認:
  - 本ADR本文に「Verify用の再現可能コマンド要件（3.4）」を追加し、コマンド記録をDoD判定入力へ昇格した。

判定: **Ready for approval / Not accepted yet**（`Status: Proposed` のため承認待ち）

## Proceed

- 承認依頼先: Project Maintainers
- 依頼内容:
  1. AC/DoD補完提案（0.1）の採用可否
  2. 必須/例外境界の固定表現（1.2）の採用可否
  3. Verify用再現可能コマンド要件（3.4）の採用可否
- 停止条件:
  - 承認完了までは本ADR以外（統合文書・実装・他ADR）を更新しない。

## Traceability

- Derived-from: `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `01_Plans/adr/ADR-0018-coding-standards-and-smell-remediation.md`
- Related: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Related: `04_Documentation/operations.md`
- Related: `04_Documentation/security.md`
