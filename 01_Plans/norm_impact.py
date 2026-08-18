"""The question the whole programme exists to answer.

"If I change this norm, which plans are affected?" -- previously unanswerable.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEF_RE = re.compile(r"^(?:#{2,4} |- \*\*)((?:DOM|KJT|WIR)-[A-Z]*-?\d{2})\b", re.M)
NORMS_RE = re.compile(r"^- Norms:(.*)$", re.M)
ID_RE = re.compile(r"(?:DOM|KJT|WIR)-[A-Z]*-?\d{2}")

definitions: dict[str, str] = {}
for source in sorted((ROOT / "00_Prompt").glob("*.md")):
    for identifier in DEF_RE.findall(source.read_text(encoding="utf-8")):
        definitions.setdefault(identifier, source.name)

declared: dict[str, list[str]] = {}
mentioned: dict[str, list[str]] = {}
for md in sorted(ROOT.rglob("*.md")):
    if any(p in {".git", "node_modules", "build"} for p in md.parts):
        continue
    if "00_Prompt" in md.parts:
        continue
    # Templates carry placeholder identifiers as examples, not as declarations.
    if md.stem == "TEMPLATE":
        continue
    text = md.read_text(encoding="utf-8")
    for line in NORMS_RE.findall(text):
        for identifier in ID_RE.findall(line):
            declared.setdefault(identifier, []).append(md.stem[:48])
    for identifier in ID_RE.findall(text):
        if identifier in definitions:
            mentioned.setdefault(identifier, []).append(md.stem[:48])

target = sys.argv[1] if len(sys.argv) > 1 else "DOM-CORE-04"
print(f"=== 逆引き: {target} を変更したら何が影響を受けるか ===")
print(f"定義元: {definitions.get(target, '未定義')}")
print()
print("Norms 欄で明示的に依拠している計画:")
for name in sorted(set(declared.get(target, []))) or ["  （なし）"]:
    print(f"  - {name}")
print()
print("本文で言及している文書:")
for name in sorted(set(mentioned.get(target, []))) or ["  （なし）"]:
    print(f"  - {name}")
print()
print(f"--- 全体: 定義 {len(definitions)} / Norms 欄で追跡中 {len(declared)} ---")
