import type { DocumentV1, PatchApplyLogEntry } from "../types";
import type { ApplyResultMeta, PatchDocument } from "./patch_apply";

function createEntryId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `patch-apply-log-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function stableSerialize(value: unknown): string {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    return `[${value.map((item) => stableSerialize(item)).join(",")}]`;
  }

  const entries = Object.entries(value).sort(([left], [right]) => left.localeCompare(right));
  return `{${entries.map(([key, item]) => `${JSON.stringify(key)}:${stableSerialize(item)}`).join(",")}}`;
}

function hashString(value: string): string {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }

  return (hash >>> 0).toString(16).padStart(8, "0");
}

function buildPatchSourceSignature(patch: PatchDocument): string {
  const stable = stableSerialize(patch);
  return `fnv1a:${hashString(stable)}`;
}

export function appendPatchApplyLog(doc: DocumentV1, patch: PatchDocument, applyResultMeta: ApplyResultMeta): DocumentV1 {
  const nextEntry: PatchApplyLogEntry = {
    id: createEntryId(),
    createdAt: new Date().toISOString(),
    patchVersion: "1",
    patchTitle: applyResultMeta.patchTitle,
    baseDocSignature: applyResultMeta.baseDocSignature,
    patchSourceSignature: buildPatchSourceSignature(patch),
    appliedOpIds: [...applyResultMeta.appliedOpIds],
    stats: { ...applyResultMeta.stats },
    conflictMeta: applyResultMeta.conflictMeta,
    note: applyResultMeta.note,
  };

  return {
    ...doc,
    patchApplyLog: [...(doc.patchApplyLog ?? []), nextEntry],
  };
}

export function formatPatchApplyLogEntryMarkdown(entry: PatchApplyLogEntry): string {
  const lines = [
    `### Patch apply log: ${entry.id}`,
    `- createdAt: ${entry.createdAt}`,
    `- patchVersion: ${entry.patchVersion}`,
    `- patchTitle: ${entry.patchTitle ?? "(none)"}`,
    `- baseDocSignature: ${entry.baseDocSignature ?? "(none)"}`,
    `- patchSourceSignature: ${entry.patchSourceSignature ?? "(none)"}`,
    `- appliedOpCount: ${entry.appliedOpIds.length}`,
    `- stats: cards +${entry.stats.upsertCards}/-${entry.stats.deleteCards}, islands +${entry.stats.upsertIslands}/-${entry.stats.deleteIslands}, edges +${entry.stats.upsertEdges}/-${entry.stats.deleteEdges}, relations +${entry.stats.upsertRelationSummaries}/-${entry.stats.deleteRelationSummaries}, evidence +${entry.stats.upsertEvidenceLinks}/-${entry.stats.deleteEvidenceLinks}`,
  ];

  if (entry.conflictMeta) {
    lines.push(
      `- conflictMeta: total=${entry.conflictMeta.totalConflicts}, yours=${entry.conflictMeta.chosenYours}, theirs=${entry.conflictMeta.chosenTheirs}, skip=${entry.conflictMeta.chosenSkip}`
    );
  }

  if (entry.note) {
    lines.push(`- note: ${entry.note}`);
  }

  lines.push("", "#### appliedOpIds");
  if (entry.appliedOpIds.length === 0) {
    lines.push("- (none)");
  } else {
    for (const opId of entry.appliedOpIds) {
      lines.push(`- ${opId}`);
    }
  }

  return lines.join("\n");
}
