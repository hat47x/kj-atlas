# ADR-0017: CLI セキュリティ/運用 Gate と受入チェック（ADR-0008分割）

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Derived-from: `01_Plans/adr/ADR-0008-cli-tooling-plan.md`

## Context

CLI導入では、機能追加より先に「漏洩しない・監査できる・運用手順が崩れない」を満たす必要がある。
本ADRは安全・運用の判定軸だけを独立し、仕様検討と混線しないようにする。

## Decision

### 1) 今決めること（固定）

1. 秘密情報（APIキー/トークン/認証ヘッダ）は `--debug` を含めログ出力禁止。
2. CLI設定の優先順位は `CLI引数 > 環境変数 > 設定ファイル > デフォルト`。
3. CLIの実行はAPI監査ログに帰属可能であることを前提要件とする。
4. SafeModeと矛盾する共有/公開導線をCLIで標準化しない。
5. CE4監査ゲートでは `proposal-only` を強制し、`auto-apply` / `auto-confirm` / `auto-publish` をポリシー違反として fail-closed 停止する。
6. CE1未整備時は `sourceBundleHash=mock:<64hex>` を許容し、実実装依存を切断した監査検証を許可する（同一 fail-closed 規律を適用）。

### 2) 後で決めること（保留）

- 鍵ローテーションの運用周期。
- principal識別子のマスキング方式（可逆/不可逆の選択）。
- MCP連携時の監査帰属フォーマット詳細。

## Security/Ops Gate（判定可能条件）

### Gate-S1: Secret Handling

- 判定条件:
  - 機密情報がログ・エラー出力・監査エクスポートに平文露出しない。
- 検証粒度（実装後）:
  - `pytest 03_Implement/backend/tests/cli_security/test_secret_redaction.py`

### Gate-S2: Audit Attribution

- 判定条件:
  - CLI起点実行が principal/request-id と紐づいて追跡可能。
  - 監査4イベント `query -> bundle -> proposal -> apply` が同一 `equivalenceKey` で連結可能。
  - API/CLI同値判定が `equivalenceKey AND bundleHash` のAND条件で再演算可能。
- 検証粒度（実装後）:
  - `pytest 03_Implement/backend/tests/cli_security/test_audit_attribution.py`

### Gate-S3: SafeMode Alignment

- 判定条件:
  - SafeMode既定ONに反する操作フローをデフォルト動線にしない。
- 検証粒度（実装後）:
  - `pytest 03_Implement/frontend/tests/safe_mode/test_cli_alignment_policy.py`

### Gate-O1: Operations Consistency

- 判定条件:
  - CLI運用手順の変更が `04_Documentation/operations.md` に同期される。
  - CE4契約変更時は `01_Plans/issues/issue-CE4-api-cli-audit-integration.md` / `02_Architecture/api.md` / `ADR-0016` / `ADR-0017` の4文書同期を必須とする（契約監査ドリフト防止）。
- 検証粒度（Docs運用）:
  - PRチェックリストで「CLI運用変更時の同時更新」を必須項目化。

## DoD

1. Gate-S1/S2/S3/O1 の合否判定が Yes/No で記録できる。
2. 各Gateに最低1つの検証コマンドまたは運用チェック項目が紐づく。
3. セキュリティ要件と機能仕様の責務が分離される（機能詳細はADR-0016へ委譲）。

## Non-Goals

- 認証方式（OAuth/API key）の最終選定。
- 監査基盤そのものの実装方式確定。

## Consequences

- CLIの機能検討より前に、安全/運用の不成立を検出できる。
- 監査観点レビューを独立実施でき、レビュー抜けを減らせる。
- CE1依存が未実装でも mock 接続で監査ゲート検証を継続でき、契約適合監査を実装待ちから分離できる。

## Traceability

- Parent: `01_Plans/adr/ADR-0008-cli-tooling-plan.md`
- Related: `01_Plans/adr/ADR-0015-cli-scope-phasing.md`
- Related: `01_Plans/adr/ADR-0016-cli-command-contract.md`
- Related: `01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- Related: `THREAT_MODEL.md`
- Related: `04_Documentation/security.md`
- Related: `04_Documentation/operations.md`
- Related: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
