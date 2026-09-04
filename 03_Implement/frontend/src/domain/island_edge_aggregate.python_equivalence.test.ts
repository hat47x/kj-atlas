import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { getDerivedIslandEdges } from "./island_edge_aggregate";
import type { DocumentV1 } from "./types";

/**
 * AC-7 spot-check (issue AI-IR-PROJECTION-01, ADR-0069 D4=A) — the TS half.
 *
 * Its Python counterpart is
 * `03_Implement/backend/tests/test_derived_island_relations_ts_equivalence.py`,
 * which runs `llm_input_ir.derived_island_relations()` over the SAME document
 * fixture and asserts against the SAME expected file. Neither side executes the
 * other: the shared file is what makes this a contract instead of two goldens
 * that can drift apart quietly. Both fixtures live under the backend's
 * `tests/fixtures/` because the Python side is the newer implementation and the
 * one the IR path depends on; the direction of the cross-tree read mirrors
 * `test_ts_python_contract_drift.py`, which reads `types.ts` from here.
 *
 * The fixture stays inside the overlap of the two implementations on purpose —
 * every edge is card-to-card, every type is one of the five canvas values, no
 * `(from, to, type)` triple repeats, and no card sits in two islands. Outside
 * that overlap the IR's own projection rules (spec §2.3 rule 6, §2.3 rule 3,
 * §2.2A first-match-wins) make the two differ BY DESIGN; the Python test's
 * docstring enumerates each case.
 *
 * A FIFTH difference is of a different kind — not a condition on the input but a
 * KNOWN BUG on THIS side, so the two arrays in the expected file are not
 * interchangeable:
 *
 * - DOMAIN-KJ-01 (`02_Architecture/schemas.md` §3.3.1) makes `causal` the one
 *   DIRECTED edge type (`fromId` = cause, `toId` = effect) and states that
 *   aggregation may normalize the pair of an UNDIRECTED type but must preserve
 *   direction for `causal`. `getDerivedIslandEdges()` calls
 *   `normalizeUndirectedIslands()` for every type with no exemption, so it
 *   reverses causal pairs whose effect island sorts first (island ids are
 *   `crypto.randomUUID()` values, so that is about half of them) and keys
 *   opposite directions identically, collapsing them into one aggregate.
 *   `derived_island_relations()` (Python) was fixed to obey §3.3.1; this
 *   function was NOT — the fix is its own unit of work, filed as
 *   `01_Plans/issues/issue-DOMAIN-KJ-CAUSAL-DIRECTION-01-derived-island-edge-causal-pair-normalization.md`.
 *   The counter-example already in this tree is `src/export/abstract_map_export.ts`,
 *   which special-cases `causal` out of its own `normalizePair()`.
 *
 * So: `derivedIslandEdges` in the expected file is the contract-correct output
 * (what Python asserts, and what this function will assert again once the issue
 * above is fixed and `tsCurrentDerivedIslandEdges` is deleted), while
 * `tsCurrentDerivedIslandEdges` pins today's behaviour. The third test below
 * holds the divergence to causal rows only, so any OTHER drift still fails loudly.
 *
 * This is one narrow comparison, not a general equivalence framework.
 */

const FIXTURE_DIR = resolve(process.cwd(), "../backend/tests/fixtures");

type ExpectedEdge = { id: string; type: string };

function readFixture(name: string): any {
  return JSON.parse(readFileSync(resolve(FIXTURE_DIR, name), "utf8"));
}

function readDocument(): DocumentV1 {
  return readFixture("derived_island_edges_document.json") as DocumentV1;
}

describe("getDerivedIslandEdges <-> derived_island_relations (AC-7)", () => {
  it("produces the pinned current output for the shared fixture", () => {
    const expected = readFixture("derived_island_edges_expected.json").tsCurrentDerivedIslandEdges;

    expect(getDerivedIslandEdges(readDocument())).toEqual(expected);
  });

  it("emits the derived edges in ascending id order, as the Python side does", () => {
    // TS sorts with localeCompare and Python by code point. The fixture ids are
    // chosen so the two coincide; asserting the order here means a fixture edit
    // that breaks the coincidence fails loudly rather than making the two halves
    // disagree only on some machines. The causal divergence changes WHICH ids
    // each side emits, not how either side orders the ids it has.
    const expected = readFixture("derived_island_edges_expected.json").tsCurrentDerivedIslandEdges;

    const ids = getDerivedIslandEdges(readDocument()).map((edge) => edge.id);

    expect(ids).toEqual(expected.map((edge: ExpectedEdge) => edge.id));
    expect(ids).toEqual([...ids].sort());
  });

  it("differs from the contract-correct (Python) output on causal rows ONLY", () => {
    // DOMAIN-KJ-01 §3.3.1 / issue DOMAIN-KJ-CAUSAL-DIRECTION-01. Non-causal rows
    // are still a strict contract between the two implementations; only the
    // causal rows are allowed to differ, and only in the direction this bug
    // produces. Delete this test together with tsCurrentDerivedIslandEdges when
    // the issue is fixed.
    const fixture = readFixture("derived_island_edges_expected.json");
    const contractCorrect: ExpectedEdge[] = fixture.derivedIslandEdges;
    const tsCurrent: ExpectedEdge[] = fixture.tsCurrentDerivedIslandEdges;
    const nonCausal = (rows: ExpectedEdge[]) => rows.filter((row) => row.type !== "causal");

    expect(getDerivedIslandEdges(readDocument())).toEqual(tsCurrent);
    expect(nonCausal(tsCurrent)).toEqual(nonCausal(contractCorrect));
    expect(tsCurrent).not.toEqual(contractCorrect);

    // The specific shape of the bug: `causal:c7:c1` runs isl-b (cause) -> isl-a
    // (effect); normalization both reverses it and folds it into the opposite
    // direction's aggregate, which is why Python has two causal rows and this
    // one has a single row of three.
    expect(contractCorrect.filter((row) => row.type === "causal").map((row) => row.id)).toEqual([
      "derived-island:isl-a|isl-b|causal",
      "derived-island:isl-b|isl-a|causal",
    ]);
    expect(tsCurrent.filter((row) => row.type === "causal").map((row) => row.id)).toEqual([
      "derived-island:isl-a|isl-b|causal",
    ]);
  });
});
