# Security Operational Guidelines（運用ガイドライン）

本書は、strict / non-strict いずれの運用プロファイルでも参照できる
**セキュリティ運用ガイドライン**です。

> 注意: ここで示す項目は「推奨ガイドライン」です。各組織は法令・規程・システム特性に応じて採否を決定してください。

## 0. 文書分類（DOC-OPS-05-14）

- Classification: **Improve external**（公開可能な運用判断ガイドとして維持）
- Audience: Security Officer / System Owner / Platform Operator / 監査担当
- Goal: strict標準と公開運用プロファイルの選択判断を、役割分離と固定値付きで再利用可能にする
- Non-goal: 承認フロー仕様の再定義（正本は `02_Architecture/strict_mode_exception_approval_flow.md`）
- Public boundary: 組織固有の承認履歴・監査証跡の生データは除外し、公開可能な判断基準と手順のみ提供する
- Outcome: 役割ごとの判断責務とプロファイル選択条件（D1〜D4）を、外部読者が再利用可能な形で確認できる
- Related: `02_Architecture/strict_mode_exception_approval_flow.md`, `04_Documentation/security.md`, `04_Documentation/operations.md`, `01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`

## DOC-OPS-05 統合同期メモ（2026-04-18）

- 連携 issue: `issue-doc-ops-05-06` / `issue-doc-ops-05-11` / `issue-doc-ops-05-13` / `issue-doc-ops-05-14`
- canonical 用語: `Security Officer / System Owner / Platform Operator`
- canonical 状態語彙: `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed`（未確定時 `StoppedForClarification`）
- fixed values (D1〜D4): `4h / 2h / 代理承認なし / 48h + 15m/60m`
- 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md`（`operations.md` は runbook 同値確認先）

## 0.1 Context / Decision / Consequences（AUTH-OPS-03整合）

### Context

- strict mode例外緩和は D1〜D4 固定値で運用する設計が確定している。
- 本書は「運用判断の補助」、`security.md` は「安全境界」、`operations.md` は「実行runbook」を担当する。

### Decision

- 役割語彙を `Security Officer / System Owner / Platform Operator` に統一する。
- D1〜D4（4h承認TTL、最大2h、代理承認なし、48hレビュー+15m/60mSLA）をプロファイル選択時の確認項目として固定する。
- 導線を `strict_mode_exception_approval_flow.md`（正本）-> `security.md`（基底方針）-> `security_operational_guidelines.md`（本書）-> `e2e_testing.md`（検証）として明示する。

### Consequences

- 役割分離と固定値の参照が1ページで確認でき、実運用での判断ブレを抑制できる。
- 文書横断ドリフト（用語/役割/導線/固定値）の差分点検が容易になる。

### 0.2 Verify必須チェック（用語・役割・導線・固定値）

security系文書更新時は、次を同時に満たさない限り Proceed しない。

1. 用語: `Security Officer / System Owner / Platform Operator` を統一している
2. 役割: 2者承認（Security Officer + System Owner）と実行責務分離（Platform Operator）が崩れていない
3. 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` の順で参照可能
4. 固定値: D1〜D4（4h / 2h / 代理承認なし / 48h+15m/60m）に差分がない

### 0.3 Stream D 実行メモ（security docs-only）

Stream D で本書を更新する場合、編集対象は `security.md` / `security_operational_guidelines.md` のみに限定する。

- 承認未了の決定事項は本文へ反映しない（検知時は停止）。
- D1〜D4、役割語彙、導線の3観点を docs-check で同時確認する。
- 自己修復は最大3回。3回で収束しない場合は `Hold` として Proceed しない。

## 1. 目的

- 運用プロファイル選択時の判断材料を共通化する。
- 「誰が何を判断するか」を明確にし、属人化を減らす。
- 監査時に説明可能な最低限の記録粒度をそろえる。

## 2. 役割（登場人物）

- **Security Officer**: セキュリティ妥当性を評価する責任者。
- **System Owner**: 業務継続・提供責任を持つ責任者。
- **Platform Operator**: 実際の設定変更と運用記録を担当する実行者。
- **Reviewer/Auditor**: 定期レビューで運用履歴を検証する担当。

## 3. 運用プロファイル別ガイド

### 3.1 strict標準プロファイル（`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`）

推奨:

- 事前ユーザ登録フロー（手動/自動連携）を定義する。
- 未登録拒否イベントの監視と問い合わせ導線を整える。
- 例外運用が必要な場合の承認・記録テンプレートを用意する。

### 3.2 公開運用プロファイル（`KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` 継続）

推奨:

- 認証境界（IdP設定、到達経路、公開範囲）を明示する。
- 編集系操作（write/share/export）を少人数へ制限する。
- 新規作成件数・異常増加の監視閾値を定義する。
- 事故時に strict または read-only へ戻す切替手順を整備する。

## 4. 記録ガイド（最小）

運用決定時に残すことを推奨:

- 決定日時、決定者、対象環境
- 採用プロファイル（strict / 公開運用）
- 主な理由（機密性、公開要件、運用体制）
- 見直し予定日（定期レビュー）

## 5. 見直し

- 四半期または主要インシデント後に見直すことを推奨。
- 見直し時は `04_Documentation/security.md` と `02_Architecture/strict_mode_exception_approval_flow.md` の整合を確認する。


## 6. AUTH-OPS-03 固定値（D1〜D4）チェック

- D1: Security Officer先行、承認TTL=4h
- D2: tenant単位、最大2h（超過時はstrictへ自動復帰）
- D3: 2者共同判定、代理承認なし
- D4: 変更台帳+監査ID相互参照、48hレビュー、15m一次/60m二次エスカレーション

運用時は上記4点を同時に満たすこと。満たせない場合は `StoppedForClarification` 扱いで停止し、再承認を行う。

A3 docs同期では `operations.md` を runbook整合確認先として扱い、canonical語彙・D1〜D4固定値の是正が必要な場合のみ最小修正を許可する。

## 7. 関連導線（読む順序）

1. 設計正本: `02_Architecture/strict_mode_exception_approval_flow.md`
2. セキュリティ基底方針: `04_Documentation/security.md`
3. 実行runbook: `04_Documentation/operations.md`
4. 検証方針: `04_Documentation/e2e_testing.md`（docs-check 観点の回帰確認）

## 8. 同一ワークフロー（Read → C/D/C → Execute → Verify → Proceed）

運用判断ガイドの更新は次の共通手順で行う。

1. **Read**
   - `strict_mode_exception_approval_flow.md` / `security.md` / `operations.md` を順に再読する。
   - 用語・役割・導線・固定値（D1〜D4）の差分がないことを確認する。
2. **ADR CDC**
   - Context: 本書は運用判断の補助文書であり、承認フロー仕様そのものではない。
   - Decision: Verify時の必須4観点（用語/役割/導線/固定値）を固定する。
   - Consequences: ドキュメント横断同期時の停止条件を明確化できる。
3. **Plan**
   - 役割（Security Officer / System Owner / Platform Operator）と D1〜D4 を正本と照合する。
   - SafeMode・share/export漏洩防止の後退表現が差分にないことを確認する。
4. **Execute**
   - 本書の責務を「運用判断補助」に限定し、承認フロー正本の再定義は行わない。
5. **Verify**
   - docs-check とリンク整合確認を行う。
   - 失敗時は最小修正で再実行し、**自己修復は最大3回**までとする。
6. **Proceed**
   - 3回で収束しない場合は fail-safe 停止し、Decision Queue / issue memo に記録する。

### フェイルセーフ停止条件

- SafeMode 既定ONの後退要求
- share/export 漏洩防止の緩和要求
- D1〜D4・役割分離・導線の不一致が解消しない状態
- 承認未了の決定事項（未確定Q項目、再承認待ち）を確定事項として反映しようとした場合

## 9. DOC-OPS-05 Stream F 専任サイクル（P1→P6）

> 1サイクルで1文書のみを扱う。各Phase冒頭で本書を再読する。

### P1 Read（再読）

- 本書の Classification / Audience / Goal / Non-goal / Public boundary を再確認する。
- D1〜D4、役割語彙（Security Officer / System Owner / Platform Operator）、SafeMode境界を再確認する。

### P2 ADR CDC

- Context: 本書は公開向け運用判断ガイドであり、承認フロー仕様の正本ではない。
- Decision: `Improve external` を維持し、内部正本（`02_Architecture/strict_mode_exception_approval_flow.md`）への導線を固定する。
- Consequences: 公開境界と内部正本の責務が分離され、運用判断の再現性が上がる。

### P3 Plan

- docs-only で更新し、実装/設定値の変更は行わない。
- Verify手順（docs-check + 差分整合）を先に固定する。

### P4 Execute

- 本書内の公開ガイド記述を、役割語彙・固定値・導線の一致を保ったまま更新する。
- 重複説明は `security.md` / `operations.md` 側へ委譲し、責務混在を避ける。

### P5 Verify

- `rg -n "Classification|Audience|Goal|Non-goal|Public boundary|D1|D2|D3|D4|Security Officer|System Owner|Platform Operator|Read → C/D/C → Execute → Verify → Proceed|フェイルセーフ" 04_Documentation/security_operational_guidelines.md`
- `git diff --check`
- D1〜D4 固定値の不一致を検知した場合は即時停止し、修復完了まで Proceed へ進めない。

### P6 Proceed

- Ready条件: 用語ドリフトなし、固定値一致、スコープ競合なし。
- 停止条件: 自己修復3回超過、用語ドリフト未収束、スコープ競合検出（例: `operations.md` 変更要求）。


## Stream F docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **CDC**: Context / Decision / Consequences を明文化し、分類結果（Move internal / Improve external）を固定する。
3. **Plan**: AC/DoD を先に定義し、docs-only スコープ（`03_Implement/**` 非変更）を明示する。
4. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
5. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
6. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## 0.4 Phase 1-5 実行記録（2026-04-16 / DOC-OPS-05-14）

- Phase 1 Read: 各Phase開始時に `security_operational_guidelines.md` / `security.md` / `operations.md` / `strict_mode_exception_approval_flow.md` を再Read。
- Phase 2 Plan: docs-only で公開運用判断ガイドに限定し、承認フロー正本の再定義を回避。
- Phase 3 Execute: プロファイル判断と役割分離の記述を維持しつつ、導線を固定。
- Phase 4 Verify（必須）:
  - 語彙: `Security Officer / System Owner / Platform Operator`
  - 役割: 2者承認と Platform Operator 実行責務分離
  - 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md`（`operations.md` は runbook 同値確認先として並行参照）
  - 固定値: D1=4h, D2=2h, D3=代理承認なし, D4=48h+15m/60m
  - 実施コマンド: `rg` と `git diff --check`
- Phase 5 Proceed: 判定は **Ready**。自己修復3回超過時は **StoppedForClarification** で停止。

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

## Stream I 専任サイクル（DOC-OPS-05 security guidelines / 2026-04-18）

### Phase 1) Read

- `strict_mode_exception_approval_flow.md` / `security.md` / `operations.md` の関連導線と固定値（D1〜D4）を再読した。
- Stream G 競合回避のため、対象は `security.md` / `security_operational_guidelines.md` と対応issueのみに限定した。

### Phase 2) Plan（語彙・責務・導線・固定値）

- 語彙: `Security Officer / System Owner / Platform Operator` を統一維持。
- 責務: 2者承認 + 実行責務分離を維持。
- 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` を維持。
- 固定値: D1=4h, D2=2h, D3=代理承認なし, D4=48h + 15m/60m を維持。

### Phase 3) Execute

- 本書に Stream I 実行記録を追加し、運用判断補助という責務境界を維持した。

### Phase 4) Verify（docs-check + 参照整合）

- docs-check: `rg` と `git diff --check` で必須語彙・固定値・体裁整合を確認。
- 参照整合: `security.md` と対応issueの同一ワークフロー、停止条件（自己修復3回上限）を確認。

### Phase 5) Proceed（運用注意点）

- 判定: **Ready**（Stream G 競合検出なし）。
- 運用注意点: 競合検出時は即停止、自己修復は最大3回。3回超過時は `Hold` / `StoppedForClarification` で停止する。

## 10. Stream K docs-only execution log（2026-04-19 / DOC-OPS-05-14）

### Phase 1 Read

- `security_operational_guidelines.md` / `security.md` と対応issue（DOC-OPS-05-13, 05-14）を再読し、Scope・公開境界・運用責務の整合を確認。

### Phase 2 ADR CDC

- Context: 本書は公開向け運用判断ガイドであり、承認フロー正本の再定義を行わない。
- Decision: 既存方針（Improve external、D1〜D4固定、役割分離）を維持し、Stream K の実行証跡のみ追記。
- Consequences: 他ストリームとの責務競合を増やさず、再利用可能な運用記録を追加できる。

### Phase 3 Plan

- docs-only / 最小差分で更新し、実装や共有統合ファイルの編集は行わない。
- Verify で `docs-check + リンク整合 + git diff --check` を実施する。

### Phase 4 Execute

- 本節を追加し、Plan → Execute → Verify → Proceed の固定ワークフローに沿った実施証跡を残した。

### Phase 5 Verify

- 実施: `rg -n "Stream K docs-only execution log|Phase 1 Read|Phase 5 Verify|D1|D2|D3|D4|Security Officer|System Owner|Platform Operator" 04_Documentation/security_operational_guidelines.md`
- 実施: `git diff --check`
- 結果: 体裁崩れなし。自己修復 0/3。

### Phase 6 Proceed

- 判定: **Ready**
- 停止条件: 自己修復3回超過、または用語/役割/導線/固定値不一致が残る場合は fail-safe 停止。

## Stream G 実行記録（DOC-OPS-05文書群② / 2026-04-19）

### Phase 1 Read同期
- `strict_mode_exception_approval_flow.md` / `security.md` / `operations.md` / 本書を再読し、4観点（用語・役割・導線・固定値）を同期確認した。
- 役割分離（2者承認: Security Officer + System Owner、実行: Platform Operator）と D1〜D4 固定値の同値を確認した。

### Phase 2 CDC明文化（判断分岐時のみ）
- 判定: **分岐なし（CDC追加なし）**。
- 理由: 本書は運用判断補助として既存Decisionを維持する更新であり、追加の方針分岐が発生していない。

### Phase 3 Execute（文書更新）
- Stream G のフェーズ進行記録を追記し、公開境界（Improve external / Non-goal: 承認フロー正本の再定義禁止）を維持した。
- 既存の fail-safe 停止条件（不一致時停止、自己修復3回上限）を変更していない。

### Phase 4 Verify（docs-check + 用語/固定値照合）
- docs-check: `rg -n "Classification|Audience|Goal|Non-goal|Public boundary|Security Officer|System Owner|Platform Operator|D1|D2|D3|D4|StoppedForClarification" 04_Documentation/security_operational_guidelines.md 04_Documentation/security.md 04_Documentation/operations.md`
- diff-check: `git diff --check`
- 判定: Pass（必須メタ・用語・固定値の不一致なし）。

### Phase 5 Proceed/Stop
- 判定: **Proceed（Ready）**。
- 停止条件: D1〜D4不一致、導線切断、または語彙ドリフトが残る場合は `StoppedForClarification` として停止する。

## Stream I boundary-first execution record（2026-04-19 / DOC-OPS-05-14）

### Phase 1) Read
- 正本 `02_Architecture/strict_mode_exception_approval_flow.md` と `04_Documentation/security.md` を再読。

### Phase 2) セキュリティ境界優先
- D1〜D4、2者承認、Platform Operator実行責務分離、SafeMode後退禁止を最優先で確認。

### Phase 3) e2e/testing/release整合
- `operations.md` と `e2e_testing.md` の runbook/検証導線が本書の運用判断基準と一致することを確認。

### Phase 4) installation/config/narratives/local-llm整合
- 公開向け導入・LLM運用・narratives説明の境界が security guideline を逸脱していないことを確認。

### Phase 5) Verify
- docs-check + `git diff --check` を実施。

### Phase 6) Proceed
- 判定: **Ready**（公開運用判断ガイドとして Improve external 方針を維持）。
