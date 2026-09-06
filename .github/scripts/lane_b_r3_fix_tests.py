from pathlib import Path

path = Path("03_Implement/backend/tests/test_final_judgement_model_governance.py")
text = path.read_text(encoding="utf-8")
anchor = '    monkeypatch.setattr(ai, "_audit_llm_trace", lambda *_args, **_kwargs: None)\n'
count = text.count(anchor)
if count != 2:
    raise SystemExit(f"expected 2 success-path audit anchors, found {count}")
replacement = (
    '    monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *_args, **_kwargs: TENANT)\n'
    + anchor
)
path.write_text(text.replace(anchor, replacement), encoding="utf-8")
print("R3 success-path audit tenant fixtures patched")
