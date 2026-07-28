# Issue Draft: ENV-ARCH-02 未配線のレガシー環境変数猶予期限スキャフォールディング

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/backend/tests/test_settings_env_migration.py`
- Related ADR/Spec: `issue-ENV-ARCH-01`（E3決定: 猶予期限運用は不採用）
- Expected verification level: `unit`

## 課題

`settings.py:11` の `LEGACY_ENV_COMPAT_DEADLINE = date(2026, 12, 31)` と `settings.py:15-16` の `_current_utc_date()` は、レガシー（無プレフィックス）環境変数キーを段階的に拒否する猶予期限の仕組みとして見えるが、実際の検証ロジック `validate_llm_provider_guards`（`settings.py:412-419`）はどちらも呼び出しておらず、レガシーキーが1つでも検出されれば日付に関係なく無条件でエラーを送出する。`_current_utc_date` はこのテストファイル以外に呼び出し元がゼロ（grep確認済み）。

`test_settings_env_migration.py` の2つのテスト（`test_legacy_key_is_rejected_before_deadline` と `test_legacy_key_fails_after_deadline_when_canonical_is_missing`）は `_current_utc_date` を猶予期限の前後にmonkeypatchしているが、無条件拒否という同一理由でどちらも成功しており、実質的に同じ挙動を2度検証しているだけになっている。

**重要な追加根拠**: `issue-ENV-ARCH-01`（本移行の正本Issue、Done）の「3) 人間判断の確定（2026-03-05）」セクションで、E3は明示的に「**考慮外（deprecation期限運用を採用しない）**」と決定されている。つまり現在の無条件拒否という挙動は、この既存決定と整合している。矛盾しているのはコード側（未配線の猶予期限スキャフォールディング）であり、決定そのものではない。

## 論点（人的判断が必要な理由）

- E3決定に従うなら、`LEGACY_ENV_COMPAT_DEADLINE` / `_current_utc_date` および区別のつかない2テストのうち片方を削除するのが筋が通る（現状の無条件拒否という挙動自体は変更しない）。
- ただし、このスキャフォールディングが追加された正確な経緯（大規模squashコミット `4ba6ec45` 経由で他の変更と混在して入っており、単独の意図を追跡しづらい）を完全には確認できておらず、E3以降に方針を再検討する決定が別途あった可能性を否定しきれない。そのため、削除の最終判断は人的確認を経るべきである。

## 影響

現状は実害のあるバグではない（無条件拒否という決定済みの挙動が維持されている）。ただし、未配線のコードと重複したテストが「いつか猶予期限運用に切り替わる」という誤った印象を実装者に与えるリスクがある。
