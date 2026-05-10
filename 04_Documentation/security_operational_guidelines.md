# Security Operational Guidelines

対象読者: Security Officer、System Owner、Platform Operator、監査担当者。

目的: kj-atlas の安全設定を変更するときの役割分離、判断基準、停止条件を利用者向けに整理します。

範囲外: 組織固有の承認システム、個別の監査証跡、非公開の例外承認履歴。

## 役割

| 役割 | 主な責務 |
| --- | --- |
| Security Officer | セキュリティ例外、外部送信、SafeMode 緩和の可否を確認する |
| System Owner | 業務上の必要性と利用者影響を確認する |
| Platform Operator | 設定変更、ロールバック、運用ログ確認を実行する |
| 監査担当 | 変更理由、確認結果、復旧可能性を確認する |

同じ人が複数の役割を兼ねる場合でも、判断責務と実行責務は記録上分けます。

## 変更前に確認する4点

1. 何を変えるか: 対象の環境変数、サービス、データ出力。
2. なぜ必要か: 利用者価値、障害対応、検証目的。
3. 何が外へ出るか: LLM 入力、audit event、export、ログ。
4. 戻せるか: rollback 手順、停止条件、確認コマンド。

## 例外判断の固定値

| ID | 基準 |
| --- | --- |
| D1 | 例外の有効期間は原則 4h 以内 |
| D2 | 緊急例外でも 2h 以内に再確認 |
| D3 | 代理承認だけで SafeMode 緩和を確定しない |
| D4 | 48h を超える例外は、15m/60m の監視観点を含めて再評価 |

これらは公開可能な運用基準です。組織固有の承認者名や証跡 ID はここに書きません。

## よくある判断

### local LLM を有効にする

Go 条件:

- 宛先が local または組織内 endpoint である。
- endpoint が `/generate` に `{ "text": "..." }` を返す。
- 入力に秘密情報を含めない運用が確認済み。

Stop 条件:

- 宛先が外部サービスだった。
- 入力内容の保持・二次利用条件が確認できない。

### large-scale LLM を有効にする

Go 条件:

- `KJ_ATLAS_LLM_ESCALATION_ENABLED=true`
- `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true`
- `KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST` に実際の host が入っている。
- Security Officer と System Owner の確認がある。

Stop 条件:

- allowlist と実際の host が一致しない。
- 未レビュー情報や秘密情報が送信される可能性が残っている。

### audit HTTP export を有効にする

Go 条件:

- audit endpoint が管理済み。
- timeout と queue size が設定済み。
- 送信 payload に秘密情報が含まれない。

Stop 条件:

- audit endpoint の所有者や保持期間が不明。
- SafeMode 中の外部送信を許可する理由が記録されていない。

## 変更記録に残す項目

- 変更日時
- 対象環境
- 変更した環境変数
- 承認した役割
- 実行した人
- rollback 手順
- 確認コマンドと結果

## 確認コマンド

```bash
curl -fsS http://localhost:8080/api/healthz
docker compose logs api --tail=100
```

API key を有効にしている場合:

```bash
curl -H "X-API-Key: <key>" http://localhost:8080/api/docs/<doc_id>
```

## 関連文書

- [security.md](security.md)
- [configuration.md](configuration.md)
- [operations.md](operations.md)
- [e2e_testing.md](e2e_testing.md)
- [strict_mode_exception_approval_flow.md](../02_Architecture/strict_mode_exception_approval_flow.md)
