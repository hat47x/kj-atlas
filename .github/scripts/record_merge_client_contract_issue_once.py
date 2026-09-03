import os
from pathlib import Path

run_id = os.environ["GITHUB_RUN_ID"]
path = Path(
    "01_Plans/issues/done/"
    "issue-AI-MERGE-CLIENT-CONTRACT-01-remote-merge-response-rejected-by-frontend.md"
)
path.write_text(
    f"""# Issue: AI-MERGE-CLIENT-CONTRACT-01 remote統合提案をfrontendがStream B契約として拒否する

- Type: Bug / Integration / Contract
- Status: Done
- Source Issue: `AI-MERGE-SEMANTICS-01`, 継続dogfood
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/domain/merge_candidates.ts`, `03_Implement/frontend/src/api/client.test.ts`, `02_Architecture/api.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `02_Architecture/api.md`, `03_Implement/backend/src/kj_atlas_api/models.py`
- Expected verification level: integration

## 課題

`POST /ai/suggest-merges` のbackend正本は、`MergeSuggestion` を `groupId`、2件以上の `cardIds`、`mergedTextDraft`、任意の `rationale` として返す。一方、frontendの `suggestMerges()` は、この4項目に加えて、決定論的なローカル候補生成で使う Stream B の `targetCardId`、`candidateCardIds`、`scoreSummary`、`reasonCodes`、`snapshotVersion` まで必須として検査していた。

このため、AIプロバイダーがbackend契約どおりの正常な200応答を返しても、frontend側では `Invalid merge suggestions contract payload` として拒否される。ローカル候補の再現性メタデータとremote AI提案のAPI契約が、一つの型とdecoderへ混在したことが原因である。

継続dogfood中の契約面走査で、backend `MergeSuggestion`、`routes/ai.py` のresponse schema、frontend `client.ts`、既存frontend contract testを突き合わせて再現した。既存test自体がStream B拡張形だけを「正しいremote payload」として固定していたため、backend正本とのずれを検出できていなかった。

## 対応

remote AI提案の共通 `MergeSuggestion` をbackend正本と同じ4項目へ戻した。frontend API decoderはこの共通契約だけを検証する。

決定論的なローカル候補については、共通 `MergeSuggestion` を拡張した `DeterministicMergeSuggestion` を `merge_candidates.ts` に置き、`targetCardId`、候補ID、score、reason code、Stream B snapshot versionを引き続き保持する。したがって、ローカル候補の再現性情報は失わず、remote AI提案に存在しないscoreやsnapshotを捏造する必要もない。

## 受入条件

- [x] backend正本どおり4項目だけのremote `MergeSuggestion` をfrontendが受理する。
- [x] `cardIds` が2件未満、または共通必須項目が欠けるpayloadは引き続きfail-closedで拒否する。
- [x] 決定論的ローカル候補はStream Bのcandidate metadataとsnapshot versionを保持する。
- [x] remote AI提案へローカルscoreやsnapshotを補作しない。
- [x] frontendの型検査を通す。

## 検証結果（2026-09-04）

GitHub Actions run `{run_id}` で、外部LLMを呼ばずに次を実行した。

- `npm test -- src/api/client.test.ts src/domain/merge_candidates.test.ts`
- `npm run typecheck`
- `python 01_Plans/docs_check.py`
- `python 01_Plans/dogfood/validate_dogfood_docs.py`
- `python 01_Plans/triage_actionable_plans.py --format json`
- `git diff --check`

すべて成功した後に本IssueをDoneとして記録した。検証用workflow/helperは最終差分から削除する。

## 文書品質の仕上げ

原因を「AI提案がStream Bに従っていない」とせず、「異なる責務を持つ二つの契約をfrontendが混同していた」と記述した。remoteとlocalのどちらを正規化して消すのでもなく、それぞれの意味を残したまま境界を分ける文章へ整えた。
""",
    encoding="utf-8",
)
