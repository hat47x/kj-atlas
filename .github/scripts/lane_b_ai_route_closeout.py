from __future__ import annotations

from pathlib import Path
import subprocess

OLD = Path('01_Plans/issues/issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md')
NEW = Path('01_Plans/issues/done/issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    return text.replace(old, new, 1)


text = OLD.read_text(encoding='utf-8')
text = replace_once(text, '- Status: In Progress', '- Status: Done', 'status')
text = replace_once(
    text,
    '- [x] 監査ログに MMR-05 の4項目が記録される。— **MMR-05 branch verified**: 通常LLM audit・runtime system-hold・governance system-holdが共通のtyped proposal-linkage fields (`proposalId` / `sourceBundleHash`) を保持する。standalone/intermediate auditにはlinkage fieldを捏造しない。main統合後に親Issueをcloseoutする。',
    '- [x] 監査ログに MMR-05 の4項目が記録される。— 通常LLM audit・runtime system-hold・governance system-holdが共通のtyped proposal-linkage fields (`proposalId` / `sourceBundleHash`) を保持する。standalone/intermediate auditにはlinkage fieldを捏造しない。PR #3000 / `6428cb39361b8d2e0358bd50e5f51e8dabb74296` でmain統合済み。',
    'MMR-05 AC',
)
text = replace_once(
    text,
    '- [x] integration test でルーティング・監査・安全停止が検証される。— routing audit、R2 runtime system-hold、R3 model-governance安全停止に加え、MMR-05でlinked `check_narrative` / `detect_contradiction` 成功auditとR2/R3 failure auditの `proposalId` / `sourceBundleHash` 一貫性を固定。main統合後にfinal closeoutする。',
    '- [x] integration test でルーティング・監査・安全停止が検証される。— routing audit、R2 runtime system-hold、R3 model-governance安全停止に加え、MMR-05でlinked `check_narrative` / `detect_contradiction` 成功auditとR2/R3 failure auditの `proposalId` / `sourceBundleHash` 一貫性を固定。MMR-05 verification run `34019450046` は31 passed、compileall・docs/lifecycle・diff checkも成功。',
    'integration AC',
)
text = replace_once(
    text,
    '- MMR-06はR3 #2998のmain統合後にcloseout同期済み。MMR-05については、従来の `[x]` が `routingStage` 追加だけを根拠に4項目全達成としていたため `[~]` のまま維持する。`sourceBundleHash` / `proposalId` のlinked telemetry completenessは次残差として扱う。',
    '- MMR-06はR3 #2998のmain統合後にcloseout同期済み。MMR-05はこの時点では `sourceBundleHash` / `proposalId` のlinked telemetry completenessを残差として `[~]` に戻したが、その後PR #3000で解消した。',
    'R3 progress residual history',
)
text = replace_once(
    text,
    '- MMR-05は別残差として未完了。特にlinked final-judgementの通常LLM audit/system-hold auditにおける `sourceBundleHash` / `proposalId` の一貫した保持を追加で固定する必要がある。',
    '- MMR-05はMMR-06 closeout時点では別残差として未完了だった。linked final-judgementの通常LLM audit/system-hold auditにおける `sourceBundleHash` / `proposalId` の一貫した保持は、その後PR #3000で固定した。',
    'MMR-06 historical residual',
)
text = replace_once(
    text,
    '- 本項目はbranch検証green後にMMR-05 / integration ACを完了扱いとし、親Issue `Status: Done` への移動はmain統合後のcloseoutで行う。',
    '- MMR-05 verification run `34019450046` は31 passed、compileall、docs contract、Issue lifecycle 35 tests、diff checkが成功し、PR #3000でmainへ統合した。これによりMMR-05 / integration ACを完了し、本closeoutで親Issueを `Done` へ移動する。',
    'MMR-05 progress closeout',
)
text += '''\n\n## Final closeout（2026-09-06）\n\n- MMR-01〜04: intermediate / final_judgementの責務分離、禁止境界、high-reasoning tier routingを実装済み。\n- MMR-05: linked final-judgementの成功LLM audit、runtime system-hold、governance system-holdで `routingStage` / provider・model / `sourceBundleHash` / `proposalId` の追跡性を固定し、PR #3000（`6428cb39361b8d2e0358bd50e5f51e8dabb74296`）でmainへ統合した。linkageのないstandalone/intermediate auditにはproposal fieldを追加しない。\n- MMR-06: explicit external proposal linkage、runtime unavailable/timeout、tenant model-governance failureをsystem `held` へ接続し、standalone callや非対象failureはstate-neutral、auto-publish fallbackなし。R1/R2/R3およびcloseoutは #2998 / #2999 までにmain統合済み。\n- MMR-05 verification run `34019450046`: focused/adjacent backend 31 passed、compileall、docs contract、Issue lifecycle 35 tests、diff check success。R3 verification run `34018370431`: 51 passed。\n- 以上により本Issueの受入条件はすべて満たしたため、active rootから `done/` へ移動する。\n'''

NEW.parent.mkdir(parents=True, exist_ok=True)
NEW.write_text(text, encoding='utf-8')
OLD.unlink()

# Preserve exact path references in tracked text when archiving the memo.
tracked = subprocess.check_output(['git', 'ls-files', '-z']).decode('utf-8').split('\0')
old_s = OLD.as_posix()
new_s = NEW.as_posix()
updated_refs: list[str] = []
for raw in tracked:
    if not raw or raw in {old_s, new_s} or raw.startswith('.github/'):
        continue
    path = Path(raw)
    if not path.is_file():
        continue
    try:
        candidate = path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        continue
    if old_s not in candidate:
        continue
    path.write_text(candidate.replace(old_s, new_s), encoding='utf-8')
    updated_refs.append(raw)

print('AI-ROUTE-01 closeout synced')
print(f'archived: {OLD} -> {NEW}')
print('updated exact-path refs:', updated_refs)
