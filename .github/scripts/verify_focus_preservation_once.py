from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_REL = Path(
    "01_Plans/issues/issue-AI-IR-FOCUS-PRESERVATION-01-preserve-focus-adjudication-under-truncation.md"
)
DONE_REL = Path(
    "01_Plans/issues/done/issue-AI-IR-FOCUS-PRESERVATION-01-preserve-focus-adjudication-under-truncation.md"
)
ACTIVE = ROOT / ACTIVE_REL
DONE = ROOT / DONE_REL

run_id = os.environ["GITHUB_RUN_ID"]
run_url = f"https://github.com/hat47x/kj-atlas/actions/runs/{run_id}"

text = ACTIVE.read_text(encoding="utf-8")
old_status = "- Status: In Progress"
old_acceptance = (
    "- [ ] 実行可能な環境で、共有IR回帰と `/ai/detect-contradiction` の300カードintegration regressionが成功することを記録する。"
)
new_acceptance = (
    "- [x] 実行可能な環境で、共有IR回帰と `/ai/detect-contradiction` の300カードintegration regressionが成功することを記録する。"
)
anchor = "## 完了境界"

for required in (old_status, old_acceptance, anchor):
    if required not in text:
        raise SystemExit(f"focus-preservation memo anchor not found: {required}")

text = text.replace(old_status, "- Status: Done", 1)
text = text.replace(old_acceptance, new_acceptance, 1)
verification = f"""## 検証結果（2026-09-03）

既にmainへ統合済みの実装を変更せず、一回限りのGitHub Actions実行環境で、完了条件として残っていた回帰を実行した。外部LLMは呼び出していない。

- `python -m pytest tests/test_llm_input_ir_required_cards.py tests/test_ai_detect_contradiction_ir_scale.py tests/test_ai_route_required_meaning_scale.py -q` — 成功。
- 共有IRでは、required指定なしの従来投影、末尾required pairとevidenceの保持、決定性、予算超過時のfail-closedを実行確認した。
- `/ai/detect-contradiction` では、300カードの末尾pairについて `confirmed` / `held` を再提案せず、`unconfirmed` / `resolved` は対象pairを保持したままLLM stubへ進むことを実行確認した。
- 実行記録: `{run_url}`（run id `{run_id}`）。

この確認により、本Issue固有の未完了条件は満たした。300カード全体の意味保存戦略やnamed providerのtoken予算は、引き続き `AI-IR-SCALE-01` の責務とする。

"""
text = text.replace(anchor, verification + anchor, 1)

DONE.parent.mkdir(parents=True, exist_ok=True)
DONE.write_text(text, encoding="utf-8")
ACTIVE.unlink()

old_path = ACTIVE_REL.as_posix()
new_path = DONE_REL.as_posix()
text_suffixes = {
    ".md",
    ".html",
    ".json",
    ".py",
    ".ts",
    ".tsx",
    ".yml",
    ".yaml",
    ".txt",
}

for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in text_suffixes:
        continue
    if ".git" in path.parts:
        continue
    try:
        body = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if old_path not in body:
        continue
    path.write_text(body.replace(old_path, new_path), encoding="utf-8")

remaining: list[str] = []
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in text_suffixes or ".git" in path.parts:
        continue
    try:
        body = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if old_path in body:
        remaining.append(path.relative_to(ROOT).as_posix())
if remaining:
    raise SystemExit(f"stale focus-preservation paths remain: {remaining}")
