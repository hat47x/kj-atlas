# Security Operational Guidelines（運用ガイドライン）

本書は、strict / non-strict いずれの運用プロファイルでも参照できる
**セキュリティ運用ガイドライン**です。

> 注意: ここで示す項目は「推奨ガイドライン」です。各組織は法令・規程・システム特性に応じて採否を決定してください。

## 0. 文書分類（DOC-OPS-05-14）

- Classification: **Improve external**（公開可能な運用判断ガイドとして維持）
- Audience: Security Officer / System Owner / Platform Operator / 監査担当
- Goal: strict標準と公開運用プロファイルの選択判断を、役割分離と固定値付きで再利用可能にする
- Non-goal: 承認フロー仕様の再定義（正本は `02_Architecture/strict_mode_exception_approval_flow.md`）

## 0.1 Context / Decision / Consequences（AUTH-OPS-03整合）

### Context

- strict mode例外緩和は D1〜D4 固定値で運用する設計が確定している。
- 本書は「運用判断の補助」、`security.md` は「安全境界」、`operations.md` は「実行runbook」を担当する。

### Decision

- 役割語彙を `Security Officer / System Owner / Platform Operator` に統一する。
- D1〜D4（4h承認TTL、最大2h、代理承認なし、48hレビュー+15m/60mSLA）をプロファイル選択時の確認項目として固定する。
- 導線を `security.md`（基底方針）と `operations.md`（実行）へ明示する。

### Consequences

- 役割分離と固定値の参照が1ページで確認でき、実運用での判断ブレを抑制できる。
- 文書横断ドリフト（用語/役割/導線/固定値）の差分点検が容易になる。

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

## 7. 関連導線（読む順序）

1. 設計正本: `02_Architecture/strict_mode_exception_approval_flow.md`
2. セキュリティ基底方針: `04_Documentation/security.md`
3. 実行runbook: `04_Documentation/operations.md`
4. 検証方針: `04_Documentation/e2e_testing.md`（docs-check 観点の回帰確認）

## 8. 同一ワークフロー（Plan → Execute → Verify → Proceed）

運用判断ガイドの更新は次の共通手順で行う。

1. **Plan**
   - 役割（Security Officer / System Owner / Platform Operator）と D1〜D4 を正本と照合する。
   - SafeMode・share/export漏洩防止の後退表現が差分にないことを確認する。
2. **Execute**
   - 本書の責務を「運用判断補助」に限定し、承認フロー正本の再定義は行わない。
3. **Verify**
   - docs-check とリンク整合確認を行う。
   - 失敗時は最小修正で再実行し、**自己修復は最大3回**までとする。
4. **Proceed**
   - 3回で収束しない場合は fail-safe 停止し、Decision Queue / issue memo に記録する。

### フェイルセーフ停止条件

- SafeMode 既定ONの後退要求
- share/export 漏洩防止の緩和要求
- D1〜D4・役割分離・導線の不一致が解消しない状態
