from pathlib import Path

path = Path('03_Implement/frontend/docs/e2e_testing.md')
text = path.read_text(encoding='utf-8')

old_compose = '''```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
curl -fsS http://localhost:8080/api/docs/doc_phase1_canvas
```
'''
new_compose = '''```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://127.0.0.1:8080/api/healthz
node ../frontend/scripts/e2e_storage_preflight.mjs \\
  --write-base-url http://127.0.0.1:8080/api
```

`e2e_storage_preflight.mjs` は、毎回一意なIDの合成 `DocumentV1` を作成し、frontend proxy 経由で `PUT -> GET` した応答payloadと `ETag` が一致することを確認します。clean PostgreSQLでも成立し、事前seed済みの固定documentには依存しません。これは `ADR-0019` の標準Compose最小受入（health + 実PostgreSQL保存経路のroundtrip）を実行可能な形にしたものです。
'''

old_local = '''```bash
curl -fsS http://127.0.0.1:8000/healthz
curl -fsS http://127.0.0.1:8000/docs/doc_phase1_canvas
curl -fsS http://127.0.0.1:4173/api/docs/doc_phase1_canvas
```
'''
new_local = '''```bash
curl -fsS http://127.0.0.1:8000/healthz
cd 03_Implement/frontend
node scripts/e2e_storage_preflight.mjs \\
  --write-base-url http://127.0.0.1:8000 \\
  --read-base-url http://127.0.0.1:4173/api
```

ローカル経路では backend へ `PUT` し、同じdocumentを frontend proxyから `GET` することで、backend保存とproxy接続を同時に確認します。
'''

old_row = '| 標準サンプル | `doc_phase1_canvas` が backend 直アクセスと frontend proxy の両方で成功する |'
new_row = '| 保存経路 | 一意な合成documentの `PUT -> GET` でpayloadと `ETag` が一致し、固定seedデータに依存しない |'

for old, new, name in [
    (old_compose, new_compose, 'compose preflight'),
    (old_local, new_local, 'local preflight'),
    (old_row, new_row, 'verification table row'),
]:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{name}: expected exactly one match, got {count}')
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('patched E2E runbook to ADR-0019 document roundtrip preflight')
