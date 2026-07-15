## 概要 / Summary

- このPRで何を変更したか
- なぜ必要か

## 変更内容 / Changes

- [ ] ドキュメント更新
- [ ] フロントエンド変更
- [ ] バックエンド変更
- [ ] CI / ワークフロー変更

## テスト / Testing

ローカルとCIで再現できるよう、実行証跡を記載してください。未実施の場合も理由と再開条件を空欄にせず、該当しない項目は `N/A` とします。

```md
- command: `python 01_Plans/docs_check.py`
- result: pass | fail | not executed（要約またはCI run URL）
- not_executed_reason: N/A | 未実施の理由
- resume_condition: N/A | 実行を再開できる条件
```

必要なコマンドが複数ある場合は、この4項目をコマンドごとに複製してください。

### 複雑性予算（UI変更時）

UI の操作や常設表示を追加・変更する場合は、`ADR-0043` に沿って記載してください。UI変更がない場合は `N/A` とします。

```md
- 初期表示への純増: なし | +N（理由）
- 保留・違和感操作の距離: 不変 | 改善 | 悪化（理由）
- 取り消し・復帰導線: あり | N/A
```

### AUTH verification log（AUTH関連変更時は必須）

```md
- classification: Smoke | Core | Safety

- Level 1 (required): pass | fail
  - command:
    - `cd 03_Implement/frontend && npx playwright test -g "auth" --reporter=line`
    - `cd 03_Implement/backend && pytest tests/test_auth_jit_provisioning.py -m auth_level1`
  - result:

- Level 2 (conditional): pass | fail | skipped
  - trigger matched: yes | no
  - trigger reason:
    - `AUTH-IMPL-01: <schema only | auth boundary changed>`
    - `AUTH-API-02: <contract changed | boundary unchanged | not in scope>`
  - command:
    - `cd 03_Implement/backend && AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh`
  - fixture (required when executed): `tests/federation/profiles/google_oidc.json`
  - result:
  - skip reason (if skipped):
```

## チェックリスト / Checklist

- [ ] 関連Issueをリンクした
- [ ] 破壊的変更の有無を明記した
- [ ] diff / merge / import に影響する変更ならテストを追加・更新した
- [ ] セキュリティ影響がある場合は `SECURITY.md` に沿って対応した
