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
 * fixture and asserts the SAME expected file. Neither side executes the other:
 * the shared file is what makes this a contract instead of two goldens that can
 * drift apart quietly. Both fixtures live under the backend's `tests/fixtures/`
 * because the Python side is the newer implementation and the one the IR path
 * depends on; the direction of the cross-tree read mirrors
 * `test_ts_python_contract_drift.py`, which reads `types.ts` from here.
 *
 * The fixture stays inside the overlap of the two implementations on purpose —
 * every edge is card-to-card, every type is one of the five canvas values, no
 * `(from, to, type)` triple repeats, and no card sits in two islands. Outside
 * that overlap the IR's own projection rules (spec §2.3 rule 6, §2.3 rule 3,
 * §2.2A first-match-wins) make the two differ BY DESIGN; the Python test's
 * docstring enumerates each case.
 *
 * This is one narrow comparison, not a general equivalence framework.
 */

const FIXTURE_DIR = resolve(process.cwd(), "../backend/tests/fixtures");

function readFixture(name: string): any {
  return JSON.parse(readFileSync(resolve(FIXTURE_DIR, name), "utf8"));
}

describe("getDerivedIslandEdges <-> derived_island_relations (AC-7)", () => {
  it("produces the shared expected output the Python implementation is held to", () => {
    const document = readFixture("derived_island_edges_document.json") as DocumentV1;
    const expected = readFixture("derived_island_edges_expected.json").derivedIslandEdges;

    expect(getDerivedIslandEdges(document)).toEqual(expected);
  });

  it("emits the derived edges in the same order the Python side does", () => {
    // TS sorts with localeCompare and Python by code point. The fixture ids are
    // chosen so the two coincide; asserting the order here means a fixture edit
    // that breaks the coincidence fails loudly rather than making the two halves
    // disagree only on some machines.
    const document = readFixture("derived_island_edges_document.json") as DocumentV1;
    const expected = readFixture("derived_island_edges_expected.json").derivedIslandEdges;

    const ids = getDerivedIslandEdges(document).map((edge) => edge.id);

    expect(ids).toEqual(expected.map((edge: { id: string }) => edge.id));
    expect(ids).toEqual([...ids].sort());
  });
});
