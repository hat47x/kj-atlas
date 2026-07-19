import {
  type CardAddressV1,
  type CardLineageEdgeV1,
  type InquiryBundleV1,
  type InquiryValidationIssue,
  validateInquiryBundle,
} from "./inquiry_journey";

export type InquiryBundleProjectionResult =
  | { ok: true; bundle: InquiryBundleV1 }
  | { ok: false; reason: "round_not_found" }
  | { ok: false; reason: "invalid_bundle"; issues: InquiryValidationIssue[] }
  | { ok: false; reason: "dependency_outside_scope"; snapshotIds: string[] };

function lineageAddresses(edge: CardLineageEdgeV1): { from: CardAddressV1[]; to: CardAddressV1[] } {
  if (edge.kind === "new") return { from: [], to: [edge.to] };
  if (edge.kind === "retired") return { from: [edge.from], to: [] };
  return {
    from: Array.isArray(edge.from) ? edge.from : [edge.from],
    to: Array.isArray(edge.to) ? edge.to : [edge.to],
  };
}

function collectRoundScope(bundle: InquiryBundleV1, selectedRoundId: string): Set<string> | null {
  const roundsById = new Map(bundle.journey.roundRecords.map((round) => [round.roundId, round]));
  if (!roundsById.has(selectedRoundId)) return null;

  const includedRoundIds = new Set<string>();
  const pendingRoundIds = [selectedRoundId];
  while (pendingRoundIds.length > 0) {
    const roundId = pendingRoundIds.pop()!;
    if (includedRoundIds.has(roundId)) continue;
    includedRoundIds.add(roundId);
    pendingRoundIds.push(...(roundsById.get(roundId)?.parentRoundIds ?? []));
  }
  return includedRoundIds;
}

/**
 * Creates the smallest self-contained bundle for a selected round and its ancestors.
 *
 * Cross-scope handoff or lineage dependencies fail closed. The caller must ask the
 * user to widen or change the share scope instead of silently omitting meaning or
 * including another branch. The source bundle and snapshots are never mutated.
 */
export function deriveInquiryRoundBundle(
  source: InquiryBundleV1,
  selectedRoundId: string
): InquiryBundleProjectionResult {
  const sourceIssues = validateInquiryBundle(source);
  if (sourceIssues.length > 0) {
    return { ok: false, reason: "invalid_bundle", issues: sourceIssues };
  }

  const includedRoundIds = collectRoundScope(source, selectedRoundId);
  if (!includedRoundIds) return { ok: false, reason: "round_not_found" };

  const includedRounds = source.journey.roundRecords.filter((round) => includedRoundIds.has(round.roundId));
  const includedSnapshotIds = new Set(source.journey.originSnapshotIds);
  for (const round of includedRounds) {
    for (const snapshotId of round.inputSnapshotIds) includedSnapshotIds.add(snapshotId);
    if (round.outputSnapshotId) includedSnapshotIds.add(round.outputSnapshotId);
  }

  const outsideDependencies = new Set<string>();
  for (const round of includedRounds) {
    const artifactRefs = [
      ...(round.handoff?.carryoverRefs ?? []),
      ...(round.handoff?.heldRefs ?? []),
    ];
    for (const ref of artifactRefs) {
      if (!includedSnapshotIds.has(ref.snapshotId)) outsideDependencies.add(ref.snapshotId);
    }
    for (const request of round.handoff?.fieldworkRequests ?? []) {
      for (const ref of request.outcome?.responseCardRefs ?? []) {
        if (!includedSnapshotIds.has(ref.snapshotId)) outsideDependencies.add(ref.snapshotId);
      }
    }
  }

  const includedLineage: CardLineageEdgeV1[] = [];
  for (const edge of source.cardLineage) {
    const addresses = lineageAddresses(edge);
    const targetSnapshotIds = addresses.to.map((address) => address.snapshotId);
    const hasIncludedTarget = targetSnapshotIds.some((snapshotId) => includedSnapshotIds.has(snapshotId));

    if (addresses.to.length > 0 && !hasIncludedTarget) continue;
    if (
      addresses.to.length === 0
      && !addresses.from.some((address) => includedSnapshotIds.has(address.snapshotId))
    ) continue;

    const edgeSnapshotIds = [...addresses.from, ...addresses.to].map((address) => address.snapshotId);
    const edgeOutsideSnapshotIds = edgeSnapshotIds.filter((snapshotId) => !includedSnapshotIds.has(snapshotId));
    if (edgeOutsideSnapshotIds.length > 0) {
      for (const snapshotId of edgeOutsideSnapshotIds) outsideDependencies.add(snapshotId);
      continue;
    }
    includedLineage.push(edge);
  }

  if (outsideDependencies.size > 0) {
    return {
      ok: false,
      reason: "dependency_outside_scope",
      snapshotIds: [...outsideDependencies].sort(),
    };
  }

  const projected: InquiryBundleV1 = {
    ...structuredClone(source),
    journey: {
      ...structuredClone(source.journey),
      roundRecords: structuredClone(includedRounds),
      headRoundIds: [selectedRoundId],
      defaultHeadRoundId: selectedRoundId,
    },
    snapshots: structuredClone(source.snapshots.filter((snapshot) => includedSnapshotIds.has(snapshot.snapshotId))),
    cardLineage: structuredClone(includedLineage),
  };

  const projectedIssues = validateInquiryBundle(projected);
  return projectedIssues.length > 0
    ? { ok: false, reason: "invalid_bundle", issues: projectedIssues }
    : { ok: true, bundle: projected };
}
