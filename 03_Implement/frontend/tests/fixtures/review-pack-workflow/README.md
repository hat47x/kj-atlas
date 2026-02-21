# review-pack-workflow fixtures (generated in tests)

このディレクトリにはバイナリ ZIP を配置しません。
`tests/utils/review_pack_fixture.ts` がユニットテスト実行時に deterministic な ZIP を生成します。

## Generated fixtures
- `base_pack.zip`
- `incoming_pack.zip`
- `malicious_pack.zip`

## Intended payload summary

### base_pack.zip
- `kj-atlas-review-pack-20260221-000000/document.json`
  - cards:
    - `c1` text=`Alpha`, claimType=`unknown`
    - `c2` text=`Beta`, claimType=`fact`
  - island `i1` with `[c1,c2]`
  - evidenceLinks: empty
- `kj-atlas-review-pack-20260221-000000/view.json`
  - perspectiveMode: `default`
- `kj-atlas-review-pack-20260221-000000/diagnostics.md`
  - harmless string `<script>alert(1)</script>` for sanitization checks

### incoming_pack.zip
- card `c1` claimType `unknown -> claim`
- `evidence.add`: `c2 supports c1`
- readingOrder changed (`view.field` diff path)
- view metadata changed (`camera`, `perspectiveMode=review`)

### malicious_pack.zip
- contains `../document.json` path traversal entry
- must be rejected by zip import with `Z002`
