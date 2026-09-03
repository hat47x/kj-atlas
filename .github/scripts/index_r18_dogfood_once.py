from pathlib import Path

path = Path("01_Plans/dogfood/cognitive-dogfood-index.md")
text = path.read_text(encoding="utf-8")

old_date = "- Date: 2026-09-03"
if text.count(old_date) != 1:
    raise SystemExit("dogfood index date anchor drifted")
text = text.replace(old_date, "- Date: 2026-09-04", 1)

anchor = '''- `doc_kj_atlas_dogfood_r17.json`
  - R17のKJキャンバス。
- `ai-ir-required-semantic-coverage-map-2026-09-03.md`
'''
replacement = '''- `doc_kj_atlas_dogfood_r17.json`
  - R17のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-04.md`
  - R18。意味保存型mergeの実装済み利用経路を横断照合し、backendのremote提案契約とfrontendの決定論fallback契約が混線して正常なprovider応答を拒否し得ることを発見・修正した記録。
- `doc_kj_atlas_dogfood_r18.json`
  - R18のKJキャンバス。既存testが誤った契約前提を非退行条件として固定し得ること、Done-at-rootの計画legacy差、merge方式の追跡性を別の残差として保持する。
- `ai-ir-required-semantic-coverage-map-2026-09-03.md`
'''
if text.count(anchor) != 1:
    raise SystemExit("R17 index anchor drifted")
text = text.replace(anchor, replacement, 1)
path.write_text(text, encoding="utf-8")
