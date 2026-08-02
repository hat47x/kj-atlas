import { describe, expect, it } from "vitest";

import { parseInquiryBundleJson, serializeInquiryBundle } from "./inquiry_bundle_io";
import { prepareInquiryBundleForShare } from "./inquiry_bundle_share";
import { createRepresentativeInquiryBundle } from "./inquiry_journey.fixture";

describe("prepareInquiryBundleForShare", () => {
  it("creates a full SafeMode derivative with persistent export metadata", async () => {
    const source = createRepresentativeInquiryBundle();
    const original = structuredClone(source);

    const result = await prepareInquiryBundleForShare(source);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.bundle.exportInfo).toEqual({
      scope: "full",
      safeModeApplied: true,
    });
    expect(result.json).not.toContain("受付開始直後に来庁者が同じ質問を三度尋ねた");
    expect(result.json).toContain("[REDACTED]");
    expect(await parseInquiryBundleJson(result.json)).toEqual({
      ok: true,
      bundle: result.bundle,
    });
    expect(source).toEqual(original);
  });

  it("records and validates a selected-round share scope", async () => {
    const result = await prepareInquiryBundleForShare(
      createRepresentativeInquiryBundle(),
      "round-r3-1",
    );

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.bundle.exportInfo).toEqual({
      scope: "round",
      selectedRoundId: "round-r3-1",
      safeModeApplied: true,
    });
    expect(result.bundle.journey.roundRecords.map((round) => round.roundId)).toEqual([
      "round-r2-1",
      "round-r3-1",
    ]);
    expect(result.bundle.journey.headRoundIds).toEqual(["round-r3-1"]);
  });

  it("rejects false SafeMode claims and scope metadata that disagrees with the DAG", async () => {
    const full = await prepareInquiryBundleForShare(createRepresentativeInquiryBundle());
    const partial = await prepareInquiryBundleForShare(
      createRepresentativeInquiryBundle(),
      "round-r3-1",
    );
    expect(full.ok).toBe(true);
    expect(partial.ok).toBe(true);
    if (!full.ok || !partial.ok) return;

    const falseClaim = JSON.parse(full.json);
    falseClaim.exportInfo.safeModeApplied = false;
    const mismatchedScope = JSON.parse(partial.json);
    mismatchedScope.exportInfo.selectedRoundId = "round-r2-1";

    const [falseClaimResult, mismatchedScopeResult] = await Promise.all([
      parseInquiryBundleJson(JSON.stringify(falseClaim)),
      parseInquiryBundleJson(JSON.stringify(mismatchedScope)),
    ]);
    expect(falseClaimResult.ok).toBe(false);
    expect(mismatchedScopeResult.ok).toBe(false);
    if (falseClaimResult.ok || mismatchedScopeResult.ok) return;
    expect(falseClaimResult.errors).toEqual(expect.arrayContaining([
      expect.objectContaining({
        code: "invalid_shape",
        path: "$.exportInfo.safeModeApplied",
      }),
    ]));
    expect(mismatchedScopeResult.errors).toEqual(expect.arrayContaining([
      expect.objectContaining({
        code: "invalid_bundle",
        path: "exportInfo.selectedRoundId",
      }),
    ]));
  });

  it("rejects a true SafeMode claim when raw inquiry text remains", async () => {
    const local = await serializeInquiryBundle(createRepresentativeInquiryBundle());
    expect(local.ok).toBe(true);
    if (!local.ok) return;
    const forged = JSON.parse(local.json);
    forged.exportInfo = {
      scope: "full",
      safeModeApplied: true,
    };

    const result = await parseInquiryBundleJson(JSON.stringify(forged));

    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.errors).toEqual([expect.objectContaining({
      code: "invalid_bundle",
      path: "$.exportInfo.safeModeApplied",
    })]);
  });
});
