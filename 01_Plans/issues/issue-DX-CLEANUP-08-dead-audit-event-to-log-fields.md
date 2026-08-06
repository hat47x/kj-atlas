# Issue Draft: DX-CLEANUP-08 audit.event_to_log_fields が未使用

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/audit.py`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

`src/kj_atlas_api/audit.py:400` の `event_to_log_fields(event: AuditEvent) -> dict[str, object]` は `json.loads(event.model_dump_json())` を返すモジュールレベル関数で、リポジトリ全体（srcとtests）を検索しても呼び出し箇所がゼロ件である。

`audit.py` の他の export（`build_audit_dispatcher` / `build_event` / `normalize_ce4_audit_metadata` / `CE4_AUDIT_SCHEMA_VERSION`）は `main.py` / `cli.py` / `routes/docs.py` から参照されている。この関数だけが取り残されている。類似の JSON変換は `event.model_dump_json()` を直接呼ぶ形で既存consumerに実装済みの可能性が高く、この関数は不要である。

## 対応方針

- 削除する: `event_to_log_fields` 関数を削除する。
- または、既存のaudit consumer（`routes/docs.py` のCE4監査）でこの関数を使う形に統一する。

## 受入条件

- [ ] 削除または利用のどちらかを決定し、実施する。
- [ ] 削除の場合、`git grep -rn "event_to_log_fields" 03_Implement/backend/` がゼロ件になる。

## 検証計画

- `git grep -rn "event_to_log_fields" 03_Implement/backend/` が期待どおりの結果。
- `cd 03_Implement/backend && python -m pytest tests/ -x -q` が通る。
