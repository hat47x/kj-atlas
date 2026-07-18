import { describe, expect, it } from "vitest";

import { createRepresentativeInquiryBundle } from "./inquiry_journey.fixture";
import {
  computeRoundSnapshotDigest,
  parseInquiryBundleJson,
  serializeInquiryBundle,
} from "./inquiry_bundle_io";

describe("inquiry bundle local roundtrip", () => {
  it("serializes a self-contained bundle with content-derived digests and parses it strictly", async () => {
    const source = createRepresentativeInquiryBundle();
    const serialized = await serializeInquiryBundle(source);

    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;
    expect(source.snapshots[0].canonicalDigest).toBe(`sha256:${"a".repeat(64)}`);
    expect(serialized.bundle.snapshots[0].canonicalDigest).toBe(
      await computeRoundSnapshotDigest(serialized.bundle.snapshots[0].document)
    );

    const parsed = await parseInquiryBundleJson(serialized.json);
    expect(parsed).toEqual({ ok: true, bundle: serialized.bundle });
  });

  it("rejects unknown fields at the bundle, journey, snapshot, and document boundaries", async () => {
    const serialized = await serializeInquiryBundle(createRepresentativeInquiryBundle());
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;

    const payload = JSON.parse(serialized.json);
    payload.unknownTopLevel = true;
    payload.journey.unknownJourneyField = true;
    payload.snapshots[0].unknownSnapshotField = true;
    payload.snapshots[0].document.unknownDocumentField = true;

    const parsed = await parseInquiryBundleJson(JSON.stringify(payload));
    expect(parsed.ok).toBe(false);
    if (parsed.ok) return;
    expect(parsed.errors.map((error) => error.path)).toEqual(expect.arrayContaining([
      "$.unknownTopLevel",
      "$.journey.unknownJourneyField",
      "$.snapshots[0].unknownSnapshotField",
    ]));
    expect(parsed.errors.some((error) => error.message.includes("unknown field 'unknownDocumentField'"))).toBe(true);
  });

  it("rejects unknown artifact, fieldwork outcome, and lineage kinds", async () => {
    const serialized = await serializeInquiryBundle(createRepresentativeInquiryBundle());
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;

    const payload = JSON.parse(serialized.json);
    payload.journey.roundRecords[0].handoff.carryoverRefs[0].kind = "unknown_artifact";
    payload.journey.roundRecords[0].handoff.fieldworkRequests[0].outcome = {
      kind: "unknown_outcome",
      responseCardRefs: [],
    };
    payload.cardLineage[0].kind = "unknown_lineage";

    const parsed = await parseInquiryBundleJson(JSON.stringify(payload));
    expect(parsed.ok).toBe(false);
    if (parsed.ok) return;
    expect(parsed.errors.map((error) => error.path)).toEqual(expect.arrayContaining([
      "$.journey.roundRecords[0].handoff.carryoverRefs[0].kind",
      "$.journey.roundRecords[0].handoff.fieldworkRequests[0].outcome.kind",
      "$.cardLineage[0].kind",
    ]));
  });

  it("computes the same digest regardless of object key order", async () => {
    const document = createRepresentativeInquiryBundle().snapshots[0].document;
    const reordered = Object.fromEntries(Object.entries(document).reverse());

    expect(await computeRoundSnapshotDigest(reordered as typeof document)).toBe(
      await computeRoundSnapshotDigest(document)
    );
  });

  it("rejects a supported-looking digest after snapshot content is changed", async () => {
    const serialized = await serializeInquiryBundle(createRepresentativeInquiryBundle());
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;

    const payload = JSON.parse(serialized.json);
    payload.snapshots[0].document.cards[0].text = "tampered after export";
    const parsed = await parseInquiryBundleJson(JSON.stringify(payload));

    expect(parsed.ok).toBe(false);
    if (parsed.ok) return;
    expect(parsed.errors).toEqual(expect.arrayContaining([
      expect.objectContaining({ code: "digest_mismatch", path: "$.snapshots[0].canonicalDigest" }),
    ]));
  });

  it("rejects unknown versions, malformed JSON, and invalid references without throwing", async () => {
    const serialized = await serializeInquiryBundle(createRepresentativeInquiryBundle());
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;

    const unknownVersion = JSON.parse(serialized.json);
    unknownVersion.schemaVersion = "2.0.0";
    const missingParent = JSON.parse(serialized.json);
    missingParent.journey.roundRecords[1].parentRoundIds = ["missing-round"];

    const [versionResult, parentResult, malformedResult] = await Promise.all([
      parseInquiryBundleJson(JSON.stringify(unknownVersion)),
      parseInquiryBundleJson(JSON.stringify(missingParent)),
      parseInquiryBundleJson("{not-json"),
    ]);

    expect(versionResult.ok).toBe(false);
    expect(parentResult.ok).toBe(false);
    expect(malformedResult).toEqual({
      ok: false,
      errors: [{ code: "invalid_json", path: "$", message: "Invalid JSON." }],
    });
  });
});
