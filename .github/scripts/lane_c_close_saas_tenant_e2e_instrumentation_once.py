from __future__ import annotations

from pathlib import Path
import re
import subprocess

ISSUES = Path("01_Plans/issues")
CHILD_NAME = "issue-SAAS-TENANT-E2E-01-ai-mutation-guard-instrumentation-gap.md"
OLD_CHILD = ISSUES / CHILD_NAME
NEW_CHILD = ISSUES / "done" / CHILD_NAME
PARENT = ISSUES / "issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md"
SCRIPT = Path(".github/scripts/lane_c_close_saas_tenant_e2e_instrumentation_once.py")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {text.count(old)}")
    return text.replace(old, new, 1)


def update_child() -> None:
    if not OLD_CHILD.exists() or NEW_CHILD.exists():
        raise SystemExit(f"unexpected child placement: {OLD_CHILD} -> {NEW_CHILD}")

    body = OLD_CHILD.read_text(encoding="utf-8")
    body = replace_once(body, "# Issue Draft:", "# Issue:", "child title")
    body = replace_once(body, "- Status: Draft", "- Status: Done", "child status")
    body = replace_once(
        body,
        "- [ ] 上記(a)/(b)/(c)のいずれかを選択する。",
        "- [x] 選択肢(b)に相当するtest-harness-only観測を採用する。PR #2917でPlaywright page側から `StaleTenantSessionResultError` の生成を直接観測し、production codeへtest専用hookを追加せず機構固有E2Eを成立させた。",
        "child acceptance choice",
    )
    body = replace_once(
        body,
        "- [ ] (a)または(b)を選ぶ場合、AI mutation 7種のうち残り6種（layout、merge、island summary、proposal audit、relation summary、narrative check）にも同水準の計装を展開するか、narrative generationの1種で代表させて十分とするかを判断する。",
        "- [x] narrative generation 1種をshared `TenantSessionGenerationGuard` の機構代表とする。残り6種へ同一probeを複製せず、各tenant-scoped callが共通guard境界を通ることは既存のfail-closed frontend call-site/session-header契約で担保する。これは各AI機能の業務意味や全越境matrixの完了を主張するものではない。",
        "child acceptance representative",
    )

    marker = "## Validation\n"
    if body.count(marker) != 1:
        raise SystemExit("child Validation section is not unique")
    prefix, _ = body.split(marker, 1)
    body = prefix + """## Validation

- PR #2917（merge `3d6ed603a4cd9d19aed5287525dc544602367f23`）でreal Chromium SaaS baseline 8/8とprobe付きmatrix 8/8が成功した。
- tenant switch前とblocked直後はprobe count=0、遅延AI narrative response解放後にcount=1となることを固定し、generic blocked viewだけでは満たせないassertへ分離した。
- mutation proofとして `TenantSessionGenerationGuard.run()` のstale throwを一時無効化すると、対象scenarioが `generation guard must reject the stale AI result` で失敗することを確認した。production source復元後のbuildも成功した。
- probeはPlaywright harness内で `Error.prototype.name` を観測するため、production code/API/schemaへtest専用surfaceを追加していない。

## 完了判断（2026-09-05）

- 元Issueの欠落は「汎用blocked viewとは独立にgeneration guard固有の発火を観測できない」ことであり、PR #2917のprobe＋mutation proofで解消した。
- shared guardそのものの判別力を1つの実ブラウザ経路で固定できたため、同一機構の確認だけを目的として7種類すべてへprobeを複製する必要はない。route/call-siteのguard包含は既存のfail-closed contract testに委ねる。
- `SAAS-TENANT-01` のAC-10は別責務であり、API/MCP/worker/browser cacheを含むsame-docId越境negative matrix全体が未完のため、親Issueは引き続きactiveとする。
"""
    OLD_CHILD.write_text(body, encoding="utf-8")
    subprocess.run(["git", "mv", OLD_CHILD.as_posix(), NEW_CHILD.as_posix()], check=True)


def update_parent() -> None:
    body = PARENT.read_text(encoding="utf-8")
    pattern = re.compile(r"^- \[ \] AC-10:.*$", re.M)
    matches = pattern.findall(body)
    if len(matches) != 1:
        raise SystemExit(f"parent AC-10: expected exactly one match, got {len(matches)}")
    replacement = (
        "- [ ] AC-10: tenant A/Bへ同じdocIdを作成した越境negative matrixが、API/MCP/worker/browser cacheを含めて成功する。"
        "— **2026-09-05再監査**: API層のsame-docId RLS matrixに加え、PR #2917でshared `TenantSessionGenerationGuard` のstale-result拒否をreal Chromium上の代表narrative経路から直接観測し、stale throwを無効化するとtestが失敗するmutation proofまで完了した。"
        "したがって `SAAS-TENANT-E2E-01` の『機構固有計装待ち』は解消済みで、同一shared guardを7種類のAI mutationへ重複probeすることはAC-10の残条件としない。"
        "残る未充足は、same-docId越境negative matrixをAPI/MCP/worker/browser cacheの4次元として一体で完走した証拠であり、AI各機能の業務意味まで代表1経路で証明したとは扱わない。"
    )
    body = pattern.sub(replacement, body, count=1)
    PARENT.write_text(body, encoding="utf-8")


def update_exact_path_references() -> None:
    old = OLD_CHILD.as_posix()
    new = NEW_CHILD.as_posix()
    completed = subprocess.run(
        ["git", "grep", "-Il", "-F", old, "--", f":!{SCRIPT.as_posix()}", f":!{NEW_CHILD.as_posix()}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        raise SystemExit(completed.stderr.strip() or "git grep failed")
    refs = [line for line in completed.stdout.splitlines() if line]
    print(f"old child path references={len(refs)}")
    for name in refs:
        path = Path(name)
        text = path.read_text(encoding="utf-8")
        replaced = text.replace(old, new)
        if replaced == text:
            raise SystemExit(f"reference replacement missed: {name}")
        path.write_text(replaced, encoding="utf-8")
        print(f"  - {name}")


def main() -> None:
    update_child()
    update_parent()
    update_exact_path_references()


if __name__ == "__main__":
    main()
