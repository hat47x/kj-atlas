from pathlib import Path

ISSUE = Path("01_Plans/issues/issue-AI-MERGE-SEMANTICS-01-define-card-merge-semantics.md")
STAGE5 = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")
API = Path("02_Architecture/api.md")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, got {count}")
    return text.replace(old, new, 1)


issue = ISSUE.read_text(encoding="utf-8")
issue = replace_once(issue, "- Status: Open", "- Status: In Progress", "issue status")

implementation_anchor = "## 受入条件\n"
implementation_result = """## 実装結果（2026-09-03）

AIへの入力と応答検査について、意味境界を実装へ反映した。

- `holdState` が付いたカードと `mergedIntoCardId` 済みカードは候補集合から除外し、候補が2枚未満ならproviderを呼ばず空提案を返す。
- 候補カードの本文は共有LLM入力IRで正規化し、`claimType`、全島所属、`canonicalId` / `repOf`、出典の同一性をroute固有の構造化入力として重ねる。
- `sources` の生値はproviderへ送らず、文書内で同じ出典を共有しているかだけを比較できる不透明なローカル参照へ変換する。
- 候補カード本文、候補間relation、候補間evidenceがIR上限によって欠ける場合は、不完全な入力で統合を提案せずfail-closedにする。
- SafeModeはroute側検査を一次防御、IR生成時の検査を第二層として維持し、PIIを含む候補本文もprovider呼出前に拒否する。
- provider promptは `LLMRequest.inputs` と同じroute固有入力から候補本文・relation・evidence・補助文脈を描画し、Document側の生本文を同じ意味の迂回入力として使わない。
- 応答後は既存の決定論的guardにより、hold、既merge、`negate`、`contradicts` evidence、異なる既知 `claimType`、同一カードを複数候補へ含める競合提案を拒否する。

一方、**提案を人間が採用した後の実merge適用経路**について、元カード・`sources`・残差・canonical/representation系譜が十分に保持されることは、この変更ではまだ完了根拠を得ていない。`mergeMethod` / `residuals` をresponse契約へ追加するかどうかも、適用経路の監査後に判断する。

"""
if implementation_result not in issue:
    issue = replace_once(
        issue,
        implementation_anchor,
        implementation_result + implementation_anchor,
        "issue implementation section",
    )

checks = {
    "- [ ] 上記のroute-required meaningをintegration regressionとして固定する。": "- [x] 上記のroute-required meaningをintegration regressionとして固定する。",
    "- [ ] `suggest-merges` のprovider実入力をgeneric Document IRまたはroute固有投影へ移す。": "- [x] `suggest-merges` のprovider実入力をgeneric Document IRまたはroute固有投影へ移す。",
    "- [ ] promptを意味保存型の統合契約へ更新する。": "- [x] promptを意味保存型の統合契約へ更新する。",
    "- [ ] LLM応答後の決定論的merge guardを実装する。": "- [x] LLM応答後の決定論的merge guardを実装する。",
    "- [ ] 同一カードが複数候補へ出た場合のfail-closedをテストで固定する。": "- [x] 同一カードが複数候補へ出た場合のfail-closedをテストで固定する。",
    "- [ ] SafeMode二層、PII最小化、structured-text-only、IR上限のfail-closedを確認する。": "- [x] SafeMode二層、PII最小化、structured-text-only、IR上限のfail-closedを確認する。",
    "- [ ] `02_Architecture/api.md` と `AI-IR-STAGE5-SCOPE-01` を実装結果へ同期する。": "- [x] `02_Architecture/api.md` と `AI-IR-STAGE5-SCOPE-01` を実装結果へ同期する。",
}
for old, new in checks.items():
    issue = replace_once(issue, old, new, old)
ISSUE.write_text(issue, encoding="utf-8")

stage5 = STAGE5.read_text(encoding="utf-8")
stage5 = replace_once(
    stage5,
    "2026-09-03に `suggest-island-summary` をStage 5の第1経路、`propose-opposing-viewpoint` を第2経路として移行し、現在は**6経路がIR経由、未移行は5経路**である。",
    "2026-09-03に `suggest-island-summary`、`propose-opposing-viewpoint`、`suggest-merges` を順に移行し、現在は**7経路が構造化入力経由、未移行は4経路**である。`suggest-merges` は共有Document IRだけでは判断に必要な意味が足りないため、共有IRにroute固有の意味文脈を重ねる方式を採った。",
    "stage5 counts",
)
stage5 = replace_once(
    stage5,
    "| `suggest-merges` | `DocumentV1`、全カード | 類似カード候補。既存の島・hold・対立関係を「mergeを避ける制約」として扱うべきかは未決 | **受入条件を先に定める**。IRに情報があるという理由だけでmerge判断へ使わない |",
    "| `suggest-merges` | `DocumentV1`、全カード | 04ステップ型の近接整理または核融合法型の意味核統合。hold、claimType、島文脈、relation/evidence、既存系譜、出典同一性を意味保存に使う | **route固有structured inputへ移行済み（2026-09-03）**。共有IRを正規化・SafeMode・上限管理の基底にし、merge固有文脈を外側へ重ねる。必要意味が欠ける場合はfail-closed |",
    "stage5 suggest-merges row",
)
section_anchor = "### 5. `summarize-island-relation`"
merge_result = """#### 実装結果（2026-09-03）

受入条件を `AI-MERGE-SEMANTICS-01` で先に固定したうえで、Stage 5の第3経路として `suggest-merges` をroute固有structured inputへ移行した。

- hold中または既merge済みのカードを候補集合から除外し、候補2枚未満ではproviderを呼ばない。
- 候補本文・card relation・evidenceは共有IRを正本とし、`claimType`、全島所属、`canonicalId` / `repOf`、出典同一性だけをmerge固有文脈として重ねる。
- raw `sources` はproviderへ送らず、不透明な文書内参照へ変換する。
- 全候補を `required_card_ids` として保護し、本文・relation・evidenceの必要意味が上限で欠ければfail-closedにする。
- provider promptも `LLMRequest.inputs` と同じ投影から描画し、Document生本文の迂回入力を回帰で禁止する。
- 応答後のhold・既merge・`negate`・contradiction evidence・claimType差・候補競合の決定論的guardは維持する。

これにより `suggest-merges` のAI入力移行は完了した。ただし、人間が提案を採用した後のmerge適用でsource・残差・系譜が保持されるかは別の完了条件として `AI-MERGE-SEMANTICS-01` に残す。

"""
if merge_result not in stage5:
    stage5 = replace_once(stage5, section_anchor, merge_result + section_anchor, "stage5 merge result")
STAGE5.write_text(stage5, encoding="utf-8")

api = API.read_text(encoding="utf-8")
api_section = """

### 2.10 AIカード統合提案（`POST /ai/suggest-merges`）

`POST /ai/suggest-merges` は、複数カードを一枚へ統合できる可能性を**提案するだけ**のAI APIである。AIはカードを削除・上書き・自動統合しない。04ステップ型の近接カード整理と、複数カードの意味核を保つ核融合法型の統合を候補として扱うが、単なる語彙類似や同一テーマだけでは統合理由にしない。

入力境界は次のとおり。

- SafeModeを既定で維持し、未レビュー本文やPIIをproviderへ送らない。
- `holdState` が付いたカードと `mergedIntoCardId` 済みカードは統合候補から除外する。候補が2枚未満ならproviderを呼ばず空の提案を返す。
- 候補本文、候補間のcard relation、`evidenceLinks` は共有LLM入力IRを正本とする。
- `claimType`、全島所属、`canonicalId` / `repOf`、出典の同一性は `suggest-merges` 専用の構造化文脈として重ねる。
- `sources` の生値はproviderへ送らず、同じ出典を共有しているかを判別できる文書内の不透明参照へ変換する。
- 全候補カードをroute-requiredとして扱う。IR上限により候補本文、候補間relation、候補間evidenceが欠ける場合は、不完全な入力で統合を提案せず422でfail-closedにする。
- provider promptは `LLMRequest.inputs` と同じ構造化入力から描画し、Document側の生本文を同じ意味の迂回入力として使わない。

LLM応答は信頼境界の外側として扱う。未知ID・重複ID・2件未満・件数上限に加え、hold、既merge、明示的な `negate`、`type=contradicts` のevidence、異なる既知 `claimType`、同じカードを複数候補へ含める競合提案を決定論的に拒否する。

Responseの外形は従来どおり `SuggestMergesResponse` / `MergeSuggestion` を維持する。現時点では `groupId`、`cardIds`、`mergedTextDraft`、任意の `rationale` であり、統合方法や残差を表す追加フィールドは、実merge適用時の来歴・残差保持を監査した後に判断する。
"""
if "### 2.10 AIカード統合提案（`POST /ai/suggest-merges`）" not in api:
    api = api.rstrip() + api_section + "\n"
API.write_text(api, encoding="utf-8")

print("suggest-merges route IR docs synchronized")
