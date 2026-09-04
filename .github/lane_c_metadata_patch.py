from pathlib import Path

validator = Path("01_Plans/issues/validate_active_issue_memos.py")
text = validator.read_text(encoding="utf-8")

old = '''def extract_field_value(memo_text: str, field_name: str) -> str | None:
    pattern = rf"^- {re.escape(field_name)}:\\s*(.+)$"
    match = re.search(pattern, memo_text, re.M)
    if not match:
        return None
    return match.group(1).strip()


def extract_verification_level(memo_text: str) -> str | None:
    match = re.search(r"^- Expected verification level:\\s*`([^`]+)`", memo_text, re.M)
    if not match:
        return None
    return match.group(1).strip()
'''
new = '''def extract_field_value(memo_text: str, field_name: str) -> str | None:
    # Keep metadata parsing line-local. ``\\s`` also matches newlines, so an
    # empty field could otherwise consume the next metadata line as its value.
    pattern = rf"^- {re.escape(field_name)}:[ \\t]*(.*)$"
    match = re.search(pattern, memo_text, re.M)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def extract_verification_level(memo_text: str) -> str | None:
    raw = extract_field_value(memo_text, "Expected verification level")
    if raw is None:
        return None
    if len(raw) >= 2 and raw.startswith("`") and raw.endswith("`"):
        raw = raw[1:-1].strip()
    return raw or None
'''
if old not in text:
    raise SystemExit("extract helper block did not match expected main content")
text = text.replace(old, new, 1)

old = '''        text = memo_path.read_text(encoding="utf-8")
        for field in REQUIRED_FIELDS:
            if field not in text:
                errors.append(f"{row.memo}: missing field {field}")

        level = extract_verification_level(text)
'''
new = '''        text = memo_path.read_text(encoding="utf-8")
        for field in REQUIRED_FIELDS:
            field_name = field.removeprefix("- ").removesuffix(":")
            if extract_field_value(text, field_name) is None:
                errors.append(f"{row.memo}: missing or empty field {field}")

        level = extract_verification_level(text)
'''
if old not in text:
    raise SystemExit("required field block did not match expected main content")
text = text.replace(old, new, 1)

old = '''        memo_status = extract_field_value(text, "Status")
        memo_source = extract_field_value(text, "Source Issue")
        memo_priority = extract_field_value(text, "Priority")
'''
new = '''        memo_status = extract_field_value(text, "Status")
        memo_source = extract_field_value(text, "Source Issue")
'''
if old not in text:
    raise SystemExit("priority extraction block did not match expected main content")
text = text.replace(old, new, 1)

old = '''        if memo_priority is None or not memo_priority.strip():
            errors.append(f"{row.memo}: missing or empty Priority value")

'''
if old not in text:
    raise SystemExit("priority validation block did not match expected main content")
text = text.replace(old, "", 1)

validator.write_text(text, encoding="utf-8")
