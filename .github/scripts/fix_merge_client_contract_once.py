from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

client_path = ROOT / "03_Implement/frontend/src/api/client.ts"
client = client_path.read_text(encoding="utf-8")
stream_import = 'import { STREAM_B_CONTRACTS } from "../domain/stream_b_contract";\n'
if client.count(stream_import) != 1:
    raise SystemExit("STREAM_B_CONTRACTS import anchor drifted")
client = client.replace(stream_import, "", 1)
start = client.index("export type MergeSuggestion = {")
end = client.index("\nexport async function suggestMerges(", start)
client_contract = '''export type MergeSuggestion = {
  groupId: string;
  cardIds: string[];
  mergedTextDraft: string;
  rationale?: string;
};

function isMergeSuggestion(value: unknown): value is MergeSuggestion {
  if (!value || typeof value !== "object") {
    return false;
  }

  const suggestion = value as Partial<MergeSuggestion>;
  return (
    isNonEmptyString(suggestion.groupId)
    && isStringArray(suggestion.cardIds)
    && suggestion.cardIds.length >= 2
    && isNonEmptyString(suggestion.mergedTextDraft)
    && (suggestion.rationale === undefined || isNonEmptyString(suggestion.rationale))
  );
}
'''
client = client[:start] + client_contract + client[end:]
client_path.write_text(client, encoding="utf-8")

candidates_path = ROOT / "03_Implement/frontend/src/domain/merge_candidates.ts"
candidates = candidates_path.read_text(encoding="utf-8")
insert_anchor = 'import { STREAM_B_CONTRACTS } from "./stream_b_contract";\n\n'
if candidates.count(insert_anchor) != 1:
    raise SystemExit("merge_candidates import anchor drifted")
deterministic_type = '''import { STREAM_B_CONTRACTS } from "./stream_b_contract";

export type DeterministicMergeSuggestion = MergeSuggestion & {
  targetCardId: string;
  candidateCardIds: string[];
  scoreSummary: {
    min: number;
    max: number;
    avg: number;
  };
  reasonCodes: string[];
  snapshotVersion: string;
};

'''
candidates = candidates.replace(insert_anchor, deterministic_type, 1)
candidates = candidates.replace(
    "function toSuggestions(groups: CandidateGroup[]): MergeSuggestion[] {",
    "function toSuggestions(groups: CandidateGroup[]): DeterministicMergeSuggestion[] {",
    1,
)
candidates = candidates.replace(
    "      } satisfies MergeSuggestion;",
    "      } satisfies DeterministicMergeSuggestion;",
    1,
)
candidates = candidates.replace(
    "export function collectMergeCandidates(document: DocumentV1): MergeSuggestion[] {",
    "export function collectMergeCandidates(document: DocumentV1): DeterministicMergeSuggestion[] {",
    1,
)
candidates_path.write_text(candidates, encoding="utf-8")

test_path = ROOT / "03_Implement/frontend/src/api/client.test.ts"
test_text = test_path.read_text(encoding="utf-8")
test_start = test_text.index('describe("suggestMerges contract validation", () => {')
test_end = test_text.index('\ndescribe("PROV-ERROR-01:', test_start)
new_tests = '''describe("suggestMerges contract validation", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("accepts the backend MergeSuggestion contract without local Stream B metadata", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [
            {
              groupId: "m1",
              cardIds: ["c1", "c2"],
              mergedTextDraft: "Risk mitigation",
              rationale: "Both cards express the same core concern.",
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const result = await suggestMerges(createDocument(), "collect candidates");

    expect(result.suggestions).toEqual([
      {
        groupId: "m1",
        cardIds: ["c1", "c2"],
        mergedTextDraft: "Risk mitigation",
        rationale: "Both cards express the same core concern.",
      },
    ]);
  });

  it("preserves backend suggestion order without requiring deterministic-candidate scoring fields", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [
            { groupId: "m1", cardIds: ["c1", "c2"], mergedTextDraft: "Risk mitigation" },
            { groupId: "m2", cardIds: ["c3", "c4"], mergedTextDraft: "Timeline review" },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const result = await suggestMerges(createDocument());
    expect(result.suggestions.map((suggestion) => suggestion.groupId)).toEqual(["m1", "m2"]);
  });

  it("fails fast when a core backend field is missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [{ groupId: "m1", mergedTextDraft: "Risk mitigation" }],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    await expect(suggestMerges(createDocument())).rejects.toMatchObject({
      message: "Invalid merge suggestions contract payload",
      status: 500,
    });
  });

  it("fails fast when a merge suggestion contains fewer than two cards", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [{ groupId: "m1", cardIds: ["c1"], mergedTextDraft: "Risk mitigation" }],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    await expect(suggestMerges(createDocument())).rejects.toMatchObject({
      message: "Invalid merge suggestions contract payload",
      status: 500,
    });
  });
});
'''
test_text = test_text[:test_start] + new_tests + test_text[test_end:]
test_path.write_text(test_text, encoding="utf-8")

api_path = ROOT / "02_Architecture/api.md"
api = api_path.read_text(encoding="utf-8")
old = '''- Response: `SuggestMergesResponse`\n  - `suggestions: MergeSuggestion[]` — 統合候補の配列\n- 類似カードの統合候補を提案する。各候補は統合対象カード群と統合理由を含む。\n'''
new = '''- Response: `SuggestMergesResponse`\n  - `suggestions: MergeSuggestion[]` — 統合候補の配列。各要素のAPI契約は `groupId`、2件以上の `cardIds`、`mergedTextDraft`、任意の `rationale`。\n- 類似カードの統合候補を提案する。各候補は統合対象カード群と統合理由を含む。\n- フロントエンドの決定論的ローカル候補は、このAPI契約に Stream B の `targetCardId` / `candidateCardIds` / `scoreSummary` / `reasonCodes` / `snapshotVersion` を付加した派生表現を使う。これらはローカル候補生成の再現性メタデータであり、AIプロバイダーが生成する `MergeSuggestion` の必須フィールドではない。remote AI提案に存在しないスコアやsnapshotを補作しない。\n'''
if api.count(old) != 1:
    raise SystemExit("api suggest-merges anchor drifted")
api_path.write_text(api.replace(old, new, 1), encoding="utf-8")
