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
PROBE_DONE_REL = Path(
    "01_Plans/issues/done/issue-AI-IR-SCALE-PROBE-01-layout-card-visibility-json-serialization.md"
)
ACTIVE = ROOT / ACTIVE_REL
DONE = ROOT / DONE_REL
PROBE_DONE = ROOT / PROBE_DONE_REL

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

PROBE_DONE.write_text(
    f"""# Issue: AI-IR-SCALE-PROBE-01 layout規模プローブの日本語本文可視性判定を修正する

- Type: Bug / Verification
- Status: Done
- Source Issue: AI-IR-SCALE-01
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/measure_ai_route_required_meaning.py`, `03_Implement/backend/tests/test_ai_route_required_meaning_scale.py`
- Related ADR/Spec: `01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md`, `02_Architecture/llm_input_ir_spec.md`
- Expected verification level: unit

## 課題

`AI-IR-FOCUS-PRESERVATION-01` の実行証跡を得るため300カード規模の回帰群を実行したところ、`layout-late-structure` の「末尾カード本文がlegacy `Cards:` 節に残る」というcharacterizationだけが失敗した。初回実行は GitHub Actions run `33722634825` で、14件成功・1件失敗だった。

実装を照合すると、`_build_prompt()` は現在も全Documentカードを `Cards:` 節へ出力しており、`_parse_suggestion()` も全カードを1回ずつ返すことを要求している。欠落していたのはカード本文ではなく、測定側の文字列表現への対応だった。

代表入力の本文は日本語を含む。layout promptはカード本文を `json.dumps()` で直列化するため、既定の `ensure_ascii=True` によって非ASCII文字が `\\u...` 形式になる。一方、route-required probeは生の日本語本文だけで部分一致を取っていたため、実際にはprovider promptへ存在するカードを「見えない」と誤判定していた。広域prompt計測の `measure_ai_route_prompt_coverage.py` は既にraw/JSONの両表現を同一の意味として扱っている。

## 対応

`measure_ai_route_required_meaning.py` のlayoutカード本文可視性判定を、生の本文または `json.dumps()` 後の本文のどちらかがpromptへ存在すれば可視と判定するよう修正した。

これはpromptの内容やproduction routeを変更する修正ではない。測定を「文字列の表記」ではなく「同じ意味の本文がprovider promptへ届いたか」に合わせる。既存の `test_ai_route_required_meaning_scale.py` の期待値は変更せず、測定側だけを直すことで、characterizationの意味を維持した。

## 受入条件

- [x] 300カードの `suggest-layout` promptで末尾 `c298` / `c299` の本文が可視と判定される。
- [x] raw文字列とJSON escaped文字列を意味上同じ本文として扱う。
- [x] 相対座標と末尾 `causal` / `negate` が現行IR上で失われるcharacterizationは変更しない。
- [x] production prompt builder、IR上限、route契約を変更しない。
- [x] route-required scale regressionを再実行して成功する。

## 検証結果（2026-09-03）

- 初回実行 `{run_url.replace(str(run_id), "33722634825")}` で本false-negativeを再現した。
- 修正後、`python -m pytest tests/test_llm_input_ir_required_cards.py tests/test_ai_detect_contradiction_ir_scale.py tests/test_ai_route_required_meaning_scale.py -q` を再実行し成功した。
- 修正後の実行記録: `{run_url}`（run id `{run_id}`）。
- 外部LLMは使用していない。

## 文書品質の仕上げ

原因をproduction欠落と測定表現の差へ分けた後、意味を変えずに全文を読み直した。「テストを通すため期待値を変えた」のではなく、既存の全カード出力契約を正しく観測する修正であることが自然に読める日本語へ整えた。
""",
    encoding="utf-8",
)

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
