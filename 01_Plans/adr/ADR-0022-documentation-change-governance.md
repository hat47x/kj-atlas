# ADR-0022: Documentation Change Governance（文書変更ガバナンス）

- Status: Proposed
- Date: 2026-03-08
- Deciders: Project Maintainers
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`, `AGENTS.md`

## Context

DOC-OPS-04 の前処理監査では、ADR候補D（Documentation Change Governance）として次の課題が確認された。

- 更新DoD・同期責務・承認責務が Issue 単位で再定義されやすい。
- 文書横断更新時に「誰が何を承認し、どの段階で停止すべきか」が曖昧化しやすい。
- AUTH-OPS-03 / DOC-OPS-02 で固定化した用語・役割・導線・固定値（D1〜D4）が、将来変更時に再ドリフトするリスクがある。

加えて、以下の AC/DoD 不足がある。

- AC不足: 文書変更タスクでの「恒久ルール決定」と「実行記録」の境界定義が不十分。
- DoD不足: 承認段階ごとの停止条件と、未承認時の引き渡し情報の最小要件が不十分。

主要選択肢:

1. 既存運用のまま、Issueごとに都度判断する。
2. **文書変更ガバナンスをADRで固定し、Issueは実行追跡のみに限定する。**（採用）
3. CIゲートだけを強化し、責務分離と承認段階は明文化しない。

## Decision

**文書変更は「責務分離 + 段階承認 + 固定順序同期 + 停止条件」を共通ガバナンスとして運用する。**

### 1) Plan（AC/DoD補完）

文書変更タスクは着手時に、少なくとも次を明記する。

- AC-1: 変更対象文書と対象外文書（非目標）
- AC-2: 上流正本（SSOT）と下流追随文書
- AC-3: 承認段階（G0〜G3）と通過条件
- AC-4: 「恒久ルール変更（ADR）」と「実行記録（Issue/PR）」の記載境界
- DoD-1: 境界曖昧性がない（責務分離・承認段階）
- DoD-2: 同期順序と実施結果を再現可能に記録
- DoD-3: 未承認停止時の引き渡しメモを残す
- DoD-4: 停止理由・停止時刻・再開条件を監査可能な形で記録

境界定義（AC-4）:

- ADRに記載する内容: 恒久ルール（What/Why）、役割、承認段階、停止条件、最小引き渡し要件。
- Issue/PRに記載する内容: 実行日時、差分、承認依頼ログ、未解決論点、再開時の作業メモ。

### 2) Execute（責務分離）

役割を以下に固定する。

- **Spec Owner**: 仕様正本（02_Architecture）更新責任。
- **Doc Owner**: 利用者向け文書（04_Documentation）同期責任。
- **Plan Owner**: 計画・追跡文書（01_Plans）同期責任。
- **Gate Approver**: 段階承認の判定責任（実行者と分離）。

責務分離ルール:

1. 正本更新なしに下流文書だけを先行変更しない。
2. 実行者と最終承認者を同一人物にしない（二者承認）。
3. ADRは恒久ルール（What/Why）のみを保持し、進捗・日次メモはIssueで管理する。
4. 各ゲートで「作成者（Executor）」と「承認者（Approver）」を明示し、同一ゲート内で兼務しない。
5. 承認者不在時は代理承認者を事前指定し、未指定の場合はG0で停止する。

### 3) Verify（承認段階）

承認段階を G0〜G3 で固定する。

- **G0: Scope Gate**
  - 変更範囲・非目標・影響範囲を確定。
  - 役割割当（Spec/Doc/Plan/Gate Approver）と代理承認者を確定。
- **G1: Source-of-Truth Gate**
  - 02_Architecture の正本更新を先に完了。
  - 正本差分に対する承認ログ（誰が何を承認したか）を記録。
- **G2: Cross-doc Sync Gate**
  - 固定順序 `02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md` で同期。
  - 同期結果を順序付きで記録し、順序逸脱があれば差し戻し。
- **G3: Closure Gate**
  - ドリフト4観点（用語/役割/導線/固定値）を確認し、DoDを満たした場合のみ完了。
  - 未解決論点が1件でも残る場合は完了不可。

いずれかのゲートで未承認の場合、次ゲートへ進まず停止する。

停止条件（Fail-safe）:

1. 必須承認者が未割当、または承認記録が欠落している。
2. 固定順序同期に逸脱がある（飛ばし・逆順・同時更新）。
3. ドリフト4観点のいずれかで不一致が解消していない。
4. 未解決論点に「判断者不在」または「再開条件未定義」が残る。

上記いずれかに該当した時点で作業を停止し、G0へ巻き戻して再計画する。

### 4) Proceed（引き渡しメモ）

停止または完了時には、以下を最小セットとして残す。

- 実施済みゲートと未通過ゲート
- 未解決論点（判断が必要な項目）
- 必要承認者と依頼内容
- 再開手順（次に行う1〜3ステップ）
- 停止条件への該当有無（該当時は根拠）

引き渡し最小要件:

1. どのゲートで停止したか（G番号）
2. 次に必要な承認アクション（承認者名/判定観点/期限）
3. 再開時の先頭手順（最初に確認すべきSSOTと差分）

### 非目標

- 文書本文の書き方（文体・表記ゆれ）を一律に規定すること。
- すべての文書変更を重い承認フローへ統一すること。
- 実装コードのレビュー規約を本ADRで再定義すること。

## Consequences

期待効果:

- 文書変更時の責務境界と承認責務が明確になり、判断の属人化を減らせる。
- 固定順序同期により、AUTH-OPS-03 / DOC-OPS-02 の再ドリフトを検知・抑止しやすくなる。
- 未承認停止時でも引き渡しメモにより、次担当者が再開しやすくなる。

副作用/制約:

- 変更前にゲート定義を書く初期コストが増える。
- 軽微修正でも「正本確認」が必要になり、即時反映の速度は下がる可能性がある。
- 役割分離（二者承認）を満たせない体制では、完了判定が遅延し得る。

## Traceability

- Related: `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- Related: `02_Architecture/strict_mode_exception_approval_flow.md`
- Related: `02_Architecture/enterprise_architecture.md`
- Related: `04_Documentation/operations.md`
- Related: `04_Documentation/security.md`
- Related: `01_Plans/project-progress-dashboard.md`
- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Derived-from: `AGENTS.md`
