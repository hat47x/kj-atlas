from __future__ import annotations

from pathlib import Path


REPLACEMENTS = {
    "01_Plans/dogfood/doc_kj_atlas_dogfood_r15.json": (
        "01_Plans/issues/issue-AI-IR-PROMPT-EVIDENCE-01-render-ir-evidence-in-provider-prompts.md",
        "01_Plans/issues/done/issue-AI-IR-PROMPT-EVIDENCE-01-render-ir-evidence-in-provider-prompts.md",
    ),
    "01_Plans/dogfood/doc_kj_atlas_dogfood_r18.json": (
        "01_Plans/issues/issue-DOC-ISSUE-LIFECYCLE-01-done-memos-remain-at-active-root.md",
        "01_Plans/issues/done/issue-DOC-ISSUE-LIFECYCLE-01-done-memos-remain-at-active-root.md",
    ),
    "01_Plans/dogfood/doc_kj_atlas_dogfood_r2.json": (
        "01_Plans/issues/issue-DX-CI-MCP-01-mcp-tests-not-run-in-ci.md",
        "01_Plans/issues/done/issue-DX-CI-MCP-01-mcp-tests-not-run-in-ci.md",
    ),
    "01_Plans/research/core-value-realization-priorities-2026-07-18.md": (
        "01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md",
        "01_Plans/issues/done/issue-MVP-EXIT-01-productization-readiness.md",
    ),
    "01_Plans/research/mvp-exit-01-human-acceptance-handoff.md": (
        "01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md",
        "01_Plans/issues/done/issue-MVP-EXIT-01-productization-readiness.md",
    ),
    "01_Plans/dogfood/cognitive-dogfood-case-003-round1-source-manifest.json": (
        "01_Plans/issues/issue-OPS-SAAS-SCALE-01-in-process-state-blocks-horizontal-scaling.md",
        "01_Plans/issues/done/issue-OPS-SAAS-SCALE-01-in-process-state-blocks-horizontal-scaling.md",
    ),
}


def main() -> None:
    for raw_path, (old, new) in REPLACEMENTS.items():
        path = Path(raw_path)
        body = path.read_text(encoding="utf-8")
        count = body.count(old)
        if count != 1:
            raise SystemExit(f"expected exactly one stale reference in {raw_path}, found {count}")
        path.write_text(body.replace(old, new), encoding="utf-8")
        print(f"updated {raw_path}: {old} -> {new}")


if __name__ == "__main__":
    main()
