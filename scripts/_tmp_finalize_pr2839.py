from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


api = Path("02_Architecture/api.md")
replace_once(
    api,
    "- AI入力は `DocumentV1` をそのまま広げず、対象島の全直接メンバーと、それらへ直接つながるcard relation / evidenceの両端だけへsourceを縮約してからLLM投入IRを構築する。無関係な文書カードはIRにも追加prompt文脈にも送らない。",
    "- AI入力は `DocumentV1` をそのまま広げず、対象島の全直接メンバーと、それらへ直接つながるcard relation / evidenceの両端だけへsourceを縮約してからLLM投入IRを構築する。無関係な文書カードはIRにも追加prompt文脈にも送らない。providerへ送る最終promptの直接メンバー本文もIR正規化後本文から描画し、Document側の生本文を同じ箇所へ再送しない。",
)

issue = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")
replace_once(
    issue,
    "| `suggest-island-summary` | `DocumentV1`、対象島、利用者の違和感 | 対象島の全直接メンバー、表札への異議、島の論理的位置、矛盾・根拠の有無 | **IR構造文脈の配線済み／実入力経路は未完了**。対象島に必要な構造意味はroute固有投影で保護したが、直接メンバー本文は `AI-IR-STAGE5-SUMMARY-PROMPT-01` でIR描画へ移す |",
    "| `suggest-island-summary` | `DocumentV1`、対象島、利用者の違和感 | 対象島の全直接メンバー、表札への異議、島の論理的位置、矛盾・根拠の有無 | **IR移行済み（2026-09-03、merge後監査完了）**。対象島に必要な意味をroute固有投影で保護し、直接メンバー本文もIRからprovider promptへ描画する。必要意味の欠落時はfail-closed |",
)
replace_once(
    issue,
    "- 親島、表札カード、review state、card relation、`contradictionState` をIR由来の構造としてpromptへ渡す。",
    "- 親島、表札カード、review state、card relation、`contradictionState` をIR由来の構造としてpromptへ渡す。\n- providerへ送る最終promptの直接メンバー本文もIR正規化後の同一カード本文から描画し、Document側の生本文を同じ入力箇所へ迂回させない。",
)
replace_once(
    issue,
    "### IR構造文脈の配線済み（実入力経路は未完了）",
    "### IR移行済み",
)
replace_once(
    issue,
    "1. `suggest-island-summary` — 2026-09-03に構造文脈を配線済み。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。merge後監査で、mainでも再現する既知4件以外に新しいbackend回帰が無いことを確認した。一方、providerが実際に受け取るpromptの直接メンバー本文はまだDocument由来であり、`AI-IR-STAGE5-SUMMARY-PROMPT-01` がOpenのため実入力経路の移行は未完了とする。",
    "1. `suggest-island-summary` — 2026-09-03にIR移行を完了。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。merge後監査で、provider promptの直接メンバー本文もIR正規化後本文から描画するよう是正した。mainでも再現する既知4件以外に新しいbackend回帰が無いことを確認し、`AI-IR-STAGE5-SUMMARY-PROMPT-01` は同監査で解消した。",
)
replace_once(
    issue,
    "1. **回帰確認済み・実入力経路は未完了: `suggest-island-summary` の構造意味をintegration regressionで固定し、IRへ配線した。** merge後監査で専用回帰と関連回帰を実行し、二層SafeModeを含めて確認した。backend全体ではmainでも同じ4件が失敗することを別環境で再現し、その4件を除く全テストが成功することを確認した。ただし直接メンバー本文のIR描画は `AI-IR-STAGE5-SUMMARY-PROMPT-01` に残る。",
    "1. **完了: `suggest-island-summary` の必要意味をintegration regressionで固定し、AI実入力をIRへ揃えた。** merge後監査で専用回帰と関連回帰を実行し、二層SafeMode、provider promptと `LLMRequest.inputs` の直接メンバー本文一致、Document生本文の迂回送出防止を確認した。backend全体ではmainでも同じ4件が失敗することを別環境で再現し、その4件を除く全テストが成功することを確認した。",
)
replace_once(
    issue,
    "- [x] `suggest-island-summary` の追加・既存回帰を実行し、結果を確認する。— 専用IR、既存prompt、経路被覆、関連SafeModeを実行して成功を確認した。backend全体はmainでも再現する既知4件を基準差分として切り分け、その4件を除く全回帰に新規失敗が無いことを確認した。なおAI実入力経路の完了条件は `AI-IR-STAGE5-SUMMARY-PROMPT-01` に残る。",
    "- [x] `suggest-island-summary` の追加・既存回帰を実行し、結果を確認する。— 専用IR、既存prompt、経路被覆、関連SafeModeを実行して成功を確認した。backend全体はmainでも再現する既知4件を基準差分として切り分け、その4件を除く全回帰に新規失敗が無いことを確認した。`AI-IR-STAGE5-SUMMARY-PROMPT-01` の直接メンバー本文IR描画回帰も同時に確認した。",
)

prompt_issue = Path("01_Plans/issues/issue-AI-IR-STAGE5-SUMMARY-PROMPT-01-render-direct-members-from-ir.md")
replace_once(prompt_issue, "- Status: Open", "- Status: Done")
replace_once(
    prompt_issue,
    "## 完了状態の扱い\n\n本IssueがOpenである間、`suggest-island-summary` は「IR構造文脈の配線と回帰確認は済んだが、AI実入力経路の移行は未完了」と扱う。専用pytestやbackend回帰が成功しても、それだけを理由に `AI-IR-STAGE5-SCOPE-01` 上で本経路を実装完了へ昇格しない。\n\nmerge後監査用の一回限りworkflow/scriptが、本Issueの発見前の前提で「回帰成功＝Stage 5第1経路完了」と記録しようとする場合、その自動更新は採用せず、本Issue解消後の事実に合わせて正本文書を更新する。\n",
    "## 解消結果\n\nmerge後監査で、providerへ送る最終promptの直接メンバー本文をIR正規化後本文から再描画するようrouteを局所修正した。従来の島不存在・空島エラー境界を保つため、最初のprompt builder呼び出しはvalidation-onlyとして残し、IR context構築後にprovider用promptをIR本文付きで再構築する。\n\n回帰では、IR正規化で本文が変わる入力を用い、`LLMRequest.inputs` とprovider promptの直接メンバー本文が一致し、Document側の生本文が最終promptに残らないことを固定した。\n",
)
replace_once(
    prompt_issue,
    "- [ ] 直接メンバー本文をIRからprovider promptへ描画する。",
    "- [x] 直接メンバー本文をIRからprovider promptへ描画する。— IR context構築後にprovider用promptを再描画する。",
)
replace_once(
    prompt_issue,
    "- [ ] Document側の生カード本文が同じ箇所へ迂回して送られないことをintegration regressionで固定する。",
    "- [x] Document側の生カード本文が同じ箇所へ迂回して送られないことをintegration regressionで固定する。— IR正規化で変化する本文を使い、生本文が最終promptに存在しないことを確認する。",
)
replace_once(
    prompt_issue,
    "- [ ] `LLMRequest.inputs` とpromptの直接メンバー本文一致を固定する。",
    "- [x] `LLMRequest.inputs` とpromptの直接メンバー本文一致を固定する。",
)
replace_once(
    prompt_issue,
    "- [ ] 既存の表札prompt / SafeMode / proposal-only回帰を実行して成功を確認する。",
    "- [x] 既存の表札prompt / SafeMode / proposal-only回帰を実行して成功を確認する。— 専用回帰9件、既存prompt 30件、経路被覆3件、関連SafeMode/IR 87件とbackend基準差分を確認した。",
)
replace_once(
    prompt_issue,
    "- [ ] `02_Architecture/api.md` に「直接メンバー本文もIRから描画する」境界を同期する。",
    "- [x] `02_Architecture/api.md` に「直接メンバー本文もIRから描画する」境界を同期する。",
)

done_dir = Path("01_Plans/issues/done")
done_dir.mkdir(parents=True, exist_ok=True)
done_prompt_issue = done_dir / prompt_issue.name
if done_prompt_issue.exists():
    raise SystemExit(f"destination already exists: {done_prompt_issue}")
prompt_issue.rename(done_prompt_issue)

# Final assertions: drift or an incomplete close must fail closed.
api_text = api.read_text(encoding="utf-8")
for needle in (
    "無関係な文書カードはIRにも追加prompt文脈にも送らない",
    "最終promptの直接メンバー本文もIR正規化後本文から描画",
    "required_text_truncated",
    "required_card_context_mismatch",
):
    if needle not in api_text:
        raise SystemExit(f"api.md synchronization failed: {needle}")

issue_text = issue.read_text(encoding="utf-8")
for needle in (
    "backend全体はmainでも再現する既知4件を基準差分として切り分け",
    "IR移行済み（2026-09-03、merge後監査完了）",
    "AI-IR-STAGE5-SUMMARY-PROMPT-01` は同監査で解消",
):
    if needle not in issue_text:
        raise SystemExit(f"Stage 5 issue synchronization failed: {needle}")

done_text = done_prompt_issue.read_text(encoding="utf-8")
if "- Status: Done" not in done_text or "- [ ]" in done_text:
    raise SystemExit("summary prompt input-path issue was not fully closed")

print("PR #2839 synchronized: summary direct-member prompt now uses IR and the defect memo is closed.")
