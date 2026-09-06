from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path('.')
OLD = Path('01_Plans/issues/issue-AI-ROUTE-HELD-LINKAGE-01-link-final-judgement-failure-to-proposal-state.md')
NEW = Path('01_Plans/issues/done/issue-AI-ROUTE-HELD-LINKAGE-01-link-final-judgement-failure-to-proposal-state.md')
PARENT = Path('01_Plans/issues/issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    return text.replace(old, new, 1)


child = OLD.read_text(encoding='utf-8')
child = replace_once(child, '- Status: In Progress', '- Status: Done', 'child status')
child = replace_once(
    child,
    '**R3 verified on branch**',
    '**R3 merged to main (#2998)**',
    'child R3 integration state',
)
child = replace_once(
    child,
    '- [ ] `AI-ROUTE-01` MMR-06の最終closeoutはR3のmain統合後に同期する。併せて、親MMR-05で不足しているlinked final-judgement telemetry（`sourceBundleHash` / `proposalId` の一貫した監査記録）を別残差として解消し、MMR-06安全停止とMMR-05追跡性を混同しない。',
    '- [x] `AI-ROUTE-01` MMR-06の最終closeoutをR3 main統合（#2998）後に同期する。親MMR-05で不足しているlinked final-judgement telemetry（`sourceBundleHash` / `proposalId` の一貫した監査記録）は別残差として維持し、MMR-06安全停止とMMR-05追跡性を混同しない。',
    'child final closeout AC',
)
child = replace_once(
    child,
    '- MMR-06親項目はR3とcloseout/evidence同期が完了するまで未完了のままとする。',
    '- R3は#2998でmain統合済み。MMR-06 closeoutは本closeoutで同期し、MMR-05 telemetry残差は別Issue/残差として扱う。',
    'child R2 historical tail',
)
child += '''\n\n## Closeout（2026-09-06）\n\n- R1 proposal linkage、R2 runtime availability system hold、R3 tenant model-governance boundaryがmainへ統合された。R3統合PRは #2998（squash commit `56ad4cc1daa66b4a6631c34d038548c1c8f811eb`）。\n- MMR-06の安全停止契約は、explicit linkageされたexternal proposalだけを対象に、runtime unavailable/timeoutおよび列挙済みmodel-governance failureで `proposed -> held` とし、standalone callや非対象failureでproposal stateを変更しない形で完了した。\n- R3 verification run `34018370431`: focused/adjacent backend 51 passed、compileall、docs contract、Issue lifecycle 35 tests、diff check success。Evidence sync run `34018867828`: docs contract、Issue lifecycle 35 tests、diff check success。\n- 親MMR-05のlinked telemetry completeness（通常LLM audit/system-hold auditでの `sourceBundleHash` / `proposalId` 一貫記録）は未完了であり、本IssueのMMR-06 closeoutとは分離して継続する。\n'''

NEW.parent.mkdir(parents=True, exist_ok=True)
NEW.write_text(child, encoding='utf-8')
OLD.unlink()

parent = PARENT.read_text(encoding='utf-8')
parent = replace_once(parent, '- Status: Draft', '- Status: In Progress', 'parent status')
parent = replace_once(
    parent,
    '- [ ] final_judgement 利用不能時に held へ遷移し、auto-publish しない（MMR-06）。— R1/R2はmain統合済み、R3 model-governance boundaryはbranchでintegration verified。R3のmain統合とcloseout同期が完了するまで未完了扱いを維持する。',
    '- [x] final_judgement 利用不能時に held へ遷移し、auto-publish しない（MMR-06）。— R1 proposal linkage、R2 runtime availability hold、R3 tenant model-governance boundaryをmainへ統合済み（R3: #2998）。state transitionはexplicitly linked external proposalに限定し、standalone callはstate-neutral、auto-publish fallbackは導入しない。',
    'parent MMR-06 AC',
)
parent = replace_once(
    parent,
    '- MMR-06はR3 main統合後にcloseout同期する。MMR-05については、従来の `[x]` が `routingStage` 追加だけを根拠に4項目全達成としていたため `[~]` へ補正した。`sourceBundleHash` / `proposalId` のlinked telemetry completenessは次残差として扱う。',
    '- MMR-06はR3 #2998のmain統合後にcloseout同期済み。MMR-05については、従来の `[x]` が `routingStage` 追加だけを根拠に4項目全達成としていたため `[~]` のまま維持する。`sourceBundleHash` / `proposalId` のlinked telemetry completenessは次残差として扱う。',
    'parent R3 progress closeout',
)
parent += '''\n\n## MMR-06 closeout（2026-09-06）\n\n- `AI-ROUTE-HELD-LINKAGE-01` R1/R2/R3をmainへ統合し、MMR-06を完了した。R3はPR #2998 / squash commit `56ad4cc1daa66b4a6631c34d038548c1c8f811eb`。\n- explicit proposal linkage、runtime unavailable/timeout、model-governance failure、race/idempotency、system audit、recovery（new proposal）の各契約とintegration evidenceが揃った。\n- MMR-05は別残差として未完了。特にlinked final-judgementの通常LLM audit/system-hold auditにおける `sourceBundleHash` / `proposalId` の一貫した保持を追加で固定する必要がある。\n'''
PARENT.write_text(parent, encoding='utf-8')

# Preserve any exact path references when archiving the completed issue memo.
tracked = subprocess.check_output(['git', 'ls-files', '-z']).decode('utf-8').split('\0')
old_s = OLD.as_posix()
new_s = NEW.as_posix()
updated_refs: list[str] = []
for raw in tracked:
    if not raw or raw in {OLD.as_posix(), NEW.as_posix()}:
        continue
    path = Path(raw)
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        continue
    if old_s not in text:
        continue
    path.write_text(text.replace(old_s, new_s), encoding='utf-8')
    updated_refs.append(raw)

print('R3 closeout synced')
print(f'archived: {OLD} -> {NEW}')
print('updated exact-path refs:', updated_refs)
