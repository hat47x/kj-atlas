#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
from pathlib import Path
p = Path('.github/scripts/r20_fix_merge_method_contract.py')
s = p.read_text(encoding='utf-8')
old = '''    '      "rationale",\\n      "representativeCardId",',
    '      "rationale",\\n      "mergeMethod",\\n      "representativeCardId",','''
new = '''    '"snapshotVersion", "rationale", "representativeCardId",',
    '"snapshotVersion", "rationale", "mergeMethod", "representativeCardId",','''
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('strict-validator patch shape is neither old nor current')
p.write_text(s, encoding='utf-8')
PY

python .github/scripts/r20_fix_merge_method_contract.py

cd 03_Implement/frontend
npm ci
npx vitest run \
  src/api/client.test.ts \
  src/domain/merge_candidates.test.ts \
  src/domain/merge_suggestion_decisions.test.ts \
  src/domain/merge_suggestion_apply.test.ts \
  src/domain/stream_b_mock_validation.test.ts \
  src/domain/stream_b_contract_handoff.test.ts \
  src/domain/validate_doc.test.ts \
  src/domain/validate.test.ts \
  src/ui/MergeSuggestionsPanel.test.ts \
  src/ui/MergeSuggestionsPanel.merge_method.test.ts \
  src/ui/merge_method_label.test.ts
npm run typecheck
cd ../..

python -m pip install -e './03_Implement/backend[test]'
cd 03_Implement/backend
python -m pytest tests/test_ai_merge_ir.py tests/test_ai_merge_semantics.py tests/test_models_backward_compat.py -q
cd ../..

python 01_Plans/issues/validate_active_issue_memos.py
python 01_Plans/triage_actionable_plans.py --format text >/tmp/triage.txt
test -s /tmp/triage.txt
python 01_Plans/dogfood/validate_dogfood_docs.py
git -c core.whitespace=cr-at-eol diff --check

rm -f \
  .github/workflows/r20-persistence-contract-fix-once.yml \
  .github/workflows/r20-contract-correction-once.yml \
  .github/workflows/tmp-r20-merge-method-contract-fix.yml \
  .github/workflows/r20-persistence-fix-runner.yml \
  .github/scripts/r20_fix_merge_method_contract.py \
  .github/scripts/r20_persistence_contract_runner.sh

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -A
git diff --cached --check
git commit -m 'fix: mergeMethodの保存・再読込契約を閉じる'
git push origin HEAD:dogfood/r20-merge-method-traceability-20260904
