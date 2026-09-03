from pathlib import Path

path = Path('03_Implement/frontend/e2e/merge_suggestion_partial_persistence.spec.ts')
text = path.read_text(encoding='utf-8')
old = '''        suggestions: [{
          groupId: "partial-three-cards",
          cardIds: ["c1", "c2", "c3"],
          mergedTextDraft: MERGED_TEXT,
          rationale: "The first two can be represented together while the third may remain independent.",
        }],'''
new = '''        suggestions: [{
          groupId: "partial-three-cards",
          targetCardId: "c1",
          candidateCardIds: ["c2", "c3"],
          scoreSummary: { min: 0.9, max: 0.95, avg: 0.925 },
          reasonCodes: ["e2e:partial-selection-contract"],
          snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
          cardIds: ["c1", "c2", "c3"],
          mergedTextDraft: MERGED_TEXT,
          rationale: "The first two can be represented together while the third may remain independent.",
        }],'''
if text.count(old) != 1:
    raise SystemExit(f'expected one E2E suggestion fixture, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('partial E2E fixture corrected')
