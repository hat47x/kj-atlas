import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  validateHilRsContractErrorEnvelope,
  validateHilRsCritiqueInput,
  validateHilRsRediffPayload,
  validateHilRsReviewAttribution,
} from "./hil_rs_contract";

function readFixture(name: string): unknown {
  const path = resolve(process.cwd(), "tests/fixtures/hil_rs_01", name);
  return JSON.parse(readFileSync(path, "utf8"));
}

describe("HIL-RS-01 A1 fixture schema", () => {
  it("accepts fixed fixtures", () => {
    expect(validateHilRsCritiqueInput(readFixture("critique_input_v1.json"))).toBe(true);
    expect(validateHilRsRediffPayload(readFixture("rediff_v1.json"))).toBe(true);
    expect(validateHilRsReviewAttribution(readFixture("review_attribution_v1.json"))).toBe(true);
    expect(validateHilRsContractErrorEnvelope(readFixture("error_envelope_v1.json"))).toBe(true);
  });
});
