# Issue: ENV-ARCH-02 未配線のレガシー環境変数猶予期限スキャフォールディング

- Type: Process
- Status: Done
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

## 実装記録（2026-08-06）: 起票時に残った不確実性を解消し、削除を実施

上記「論点」が最終判断を人的確認に委ねた理由は一点だけだった：`LEGACY_ENV_COMPAT_DEADLINE`の導入経緯（大規模squashコミット`4ba6ec45`）から単独の意図を追跡しづらく、「E3以降に方針を再検討する決定が別途あった可能性」を否定しきれなかったこと。この一点を次の2つの独立した確認で解消した。

1. `git log --all -S "LEGACY_ENV_COMPAT_DEADLINE" -- 03_Implement/backend/src/kj_atlas_api/settings.py`（pickaxe検索、全履歴・全ブランチ対象）は、この文字列を導入した`4ba6ec45`以外のコミットを一件も返さない。つまりこの定数は導入以降、一度も変更・再配線・再検討されていない。
2. `4ba6ec45`へsquashされた個別コミット`df8bc3c0`（"fix(CI): fix unreachable provider validation + remove nonexistent migration test"）を直接確認した。この時点で`validate_llm_provider_guards`から`populate_by_name=True`と早期return（`if not detected_legacy: return self`）が除去され、レガシーキー検出時は即座にエラーを送出する形になっている（=関数内でこの時点より後にある猶予期限比較コードへは、この変更以降そもそも到達し得ない）。このコミットの意図は明示的に「無関係な別バグ（provider validationが到達不能だった問題と、存在しない移行パスをテストしていた1テストの削除）」であり、E3方針の再検討ではない。

以上より、「E3以降の再検討」を裏付ける形跡は存在せず、現在の無条件拒否という挙動はE3決定と一貫して整合していると確認できた。よって以下を実施した。

- `settings.py`: `LEGACY_ENV_COMPAT_DEADLINE`定数、`_current_utc_date()`関数、および使用箇所が無くなった`from datetime import date`importを削除。
- `test_settings_env_migration.py`を全体削除（3テストいずれも削除した`LEGACY_ENV_COMPAT_DEADLINE`への依存のみで、独立した価値のある検証は無かった）。「legacy key単独が拒否される」という同ファイルが検証していた実質的な挙動は、`test_settings_env_prefix_migration.py`の`test_settings_rejects_legacy_key_only`・`test_settings_rejects_mixed_prefixed_and_legacy_keys`（いずれも同じ`DATABASE_URL`キーで検証）で既に、猶予期限の疑似ロジックなしに、かつより厳密に（拒否理由の文字列だけでなく対象キー名の文字列一致も検証）カバーされていることを確認済み。

検証結果:
- 対象テスト（`test_settings_env_prefix_migration.py`）: 22 passed。
- backend全体: 645 passed・25 skipped・failed 0（削除前648 passedから、削除した3テストちょうど分の減少のみ。新規failedは無い）。
- `ruff check .`: pass。
