from pathlib import Path

WORKFLOW = Path(".github/workflows/merge-method-traceability-once.yml")
ROOT = Path(".")


def read_text(path: str) -> str:
    with open(ROOT / path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write_text(path: str, text: str) -> None:
    with open(ROOT / path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


workflow = WORKFLOW.read_text(encoding="utf-8")
marker = "          python - <<'PY'\n"
start = workflow.index(marker) + len(marker)
end = workflow.index("\n          PY\n", start)
embedded = workflow[start:end]
lines: list[str] = []
for line in embedded.splitlines():
    if line.startswith("          "):
        line = line[10:]
    lines.append(line)
script = "\n".join(lines) + "\n"

section_start = script.index("# Append-only audit record carries the same method when known.")
section_end = script.index("# App decision + audit wiring.", section_start)
corrected = r"""# Append-only audit record carries the same method when known.
audit_path = '03_Implement/frontend/src/domain/merge/decision_audit_events.ts'
audit = read_text(audit_path)
newline = '\r\n' if '\r\n' in audit else '\n'

def audit_replace(old: str, new: str) -> None:
    global audit
    old_native = adapt(old, newline)
    new_native = adapt(new, newline)
    count = audit.count(old_native)
    if count != 1:
        raise SystemExit(f'{audit_path}: expected one explicit audit contract fragment, found {count}: {old!r}')
    audit = audit.replace(old_native, new_native, 1)

audit_replace(
    '''export type MergeDecisionAuditEvent = {
  eventId: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  decidedAt: string;
  decidedBy: "human";
  cardIds: string[];
  snapshotVersion: string;
  decisionReason?: string;
};
''',
    '''export type MergeDecisionAuditEvent = {
  eventId: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  decidedAt: string;
  decidedBy: "human";
  cardIds: string[];
  snapshotVersion: string;
  decisionReason?: string;
  mergeMethod?: "near_duplicate" | "kernel_fusion";
};
''',
)
audit_replace(
    '''export function createMergeDecisionAuditEvent(input: {
  eventId: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  decidedAt: string;
  cardIds: string[];
  snapshotVersion: string;
  decisionReason?: string;
}): MergeDecisionAuditEvent {
''',
    '''export function createMergeDecisionAuditEvent(input: {
  eventId: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  decidedAt: string;
  cardIds: string[];
  snapshotVersion: string;
  decisionReason?: string;
  mergeMethod?: "near_duplicate" | "kernel_fusion";
}): MergeDecisionAuditEvent {
''',
)
audit_replace(
    '''    snapshotVersion: input.snapshotVersion,
    decisionReason: input.decisionReason,
''',
    '''    snapshotVersion: input.snapshotVersion,
    decisionReason: input.decisionReason,
    mergeMethod: input.mergeMethod,
''',
)
write_text(audit_path, audit)

audit_test_path = '03_Implement/frontend/src/domain/merge/decision_audit_events.test.ts'
audit_test = read_text(audit_test_path)
newline = '\r\n' if '\r\n' in audit_test else '\n'
old_fragment = adapt('''      snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      decisionReason: "Reviewed by operator",
    });
''', newline)
new_fragment = adapt('''      snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      decisionReason: "Reviewed by operator",
      mergeMethod: "kernel_fusion",
    });
''', newline)
count = audit_test.count(old_fragment)
if count != 2:
    raise SystemExit(f'{audit_test_path}: expected two decisionReason fragments, found {count}')
audit_test = audit_test.replace(old_fragment, new_fragment, 1)
audit_test = audit_test.replace(old_fragment, new_fragment, 1)
write_text(audit_test_path, audit_test)

"""
script = script[:section_start] + corrected + script[section_end:]
exec(compile(script, "<merge-method-traceability>", "exec"))
