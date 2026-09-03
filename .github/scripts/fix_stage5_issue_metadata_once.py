from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")
text = path.read_text(encoding="utf-8")
before = "- Related Issue: `AI-IR-PROJECTION-01`, `AI-IR-SCALE-01`"
after = "- Related ADR/Spec: `AI-IR-PROJECTION-01`, `AI-IR-SCALE-01`, `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`"
if text.count(before) != 1:
    raise SystemExit("Stage 5 Issueの旧Related Issueメタデータを一意に特定できませんでした")
path.write_text(text.replace(before, after, 1), encoding="utf-8")
