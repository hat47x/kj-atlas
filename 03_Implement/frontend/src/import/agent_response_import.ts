import { sanitizeMarkdownForDisplay } from "./markdown_sanitize";
import { ZIP_MAX_TEXT_FILE_BYTES } from "./zip_import";
import type { PatchOp, PatchV1 } from "../domain/patch/patch_types";
import { parsePatchOp } from "../domain/patch/patch_apply";
import { canonicalizeJson } from "../domain/patch/patch_fingerprint";
import { AGENT_TASK_KINDS, type AgentTaskCorrelation } from "../export/agent_task_export";
import type { AgentResponseProvenance } from "../storage/agent_task_ledger";
import { isMergeMethod, type MergeMethod } from "../domain/merge_method";

// EXT-AGENT-02 (ADR-0049 D3, spec `02_Architecture/external_agent_collaboration_spec.md`
// §4/§5): parses/validates/sanitizes an external AI agent's pasted "agent-response.v1"
// JSON (the counterpart to EXT-AGENT-01's exported task sheet). Untrusted-data
// boundary: forbidden scoring fields are discarded+warned (strict mode rejects),
// missing rationale is flagged, patch.ops are checked against the CE3 whitelist,
// every string is sanitized, and the whole payload is size-capped the same as one
// ZIP-imported text file (spec §5: "応答全体に ZIP 取込と同等の容量制限を適用").

export const AGENT_RESPONSE_PROPOSAL_KINDS = [
  "island_title",
  "merge_candidate",
  "narrative_draft",
  "opposing_viewpoint",
  "critique",
  "patch",
] as const;

export type AgentResponseProposalKind = (typeof AGENT_RESPONSE_PROPOSAL_KINDS)[number];

const FORBIDDEN_SCORING_FIELDS = ["score", "rank", "confidence", "priority"] as const;

export type AgentResponseTargetRef = {
  islandId?: string;
  cardIds?: string[];
};

export type AgentResponseProposalContent = {
  title?: string;
  text?: string;
  mergedText?: string;
  mergeMethod?: MergeMethod;
};

export type ParsedAgentProposal = {
  proposalId: string;
  kind: AgentResponseProposalKind;
  targetRef: AgentResponseTargetRef;
  content: AgentResponseProposalContent;
  rationale: string;
  rationaleStated: boolean;
  patch?: PatchV1;
  patchHasDeleteOps: boolean;
  warnings: string[];
};

export type ParsedAgentResponse = {
  schemaVersion: "agent-response.v1";
  taskId: string;
  correlation?: AgentTaskCorrelation;
  respondedAt?: string;
  agent?: string;
  proposals: ParsedAgentProposal[];
};

function parseCorrelation(value: unknown): AgentTaskCorrelation | undefined {
  if (!isRecord(value)) return undefined;
  const fields = ["taskId", "createdAt", "docId", "baseDocSignature", "bundleHash", "queryCanonicalHash"] as const;
  if (value.schemaVersion !== "agent-task.v1" || value.locale !== "ja") return undefined;
  if (fields.some((field) => typeof value[field] !== "string" || value[field].length === 0)) return undefined;
  if (typeof value.taskKind !== "string" || !(AGENT_TASK_KINDS as readonly string[]).includes(value.taskKind)) return undefined;
  return {
    schemaVersion: "agent-task.v1",
    taskId: sanitizeMarkdownForDisplay(value.taskId as string),
    createdAt: sanitizeMarkdownForDisplay(value.createdAt as string),
    docId: sanitizeMarkdownForDisplay(value.docId as string),
    baseDocSignature: sanitizeMarkdownForDisplay(value.baseDocSignature as string),
    bundleHash: sanitizeMarkdownForDisplay(value.bundleHash as string),
    queryCanonicalHash: sanitizeMarkdownForDisplay(value.queryCanonicalHash as string),
    taskKind: value.taskKind as AgentTaskCorrelation["taskKind"],
    locale: "ja",
  };
}

export type AgentResponseImportMode = "strict" | "lenient";

export type AgentResponseImportResult =
  | { ok: true; response: ParsedAgentResponse; warnings: string[] }
  | { ok: false; errors: string[] };

const FENCE_PATTERN = /```(?:json)?\s*([\s\S]*?)```/i;

async function sha256Hex(value: string): Promise<string> {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export async function fingerprintAgentProposal(proposal: ParsedAgentProposal): Promise<string> {
  return sha256Hex(canonicalizeJson(proposal));
}

export async function buildExternalProposalAuditId(taskId: string, proposalId: string): Promise<string> {
  return `external-${await sha256Hex(canonicalizeJson({ taskId, proposalId }))}`;
}

export function extractJsonPayload(rawInput: string): string {
  const fenceMatch = rawInput.match(FENCE_PATTERN);
  return (fenceMatch ? fenceMatch[1] : rawInput).trim();
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function sanitizeString(value: unknown): string | undefined {
  return typeof value === "string" ? sanitizeMarkdownForDisplay(value) : undefined;
}

function parseTargetRef(value: unknown): AgentResponseTargetRef {
  if (!isRecord(value)) return {};
  const islandId = typeof value.islandId === "string" ? value.islandId : undefined;
  const cardIds = Array.isArray(value.cardIds) ? value.cardIds.filter((id): id is string => typeof id === "string") : undefined;
  return { islandId, cardIds };
}

function parseContent(value: unknown): AgentResponseProposalContent {
  if (!isRecord(value)) return {};
  return {
    title: sanitizeString(value.title),
    text: sanitizeString(value.text),
    mergedText: sanitizeString(value.mergedText),
    mergeMethod: isMergeMethod(value.mergeMethod) ? value.mergeMethod : undefined,
  };
}

function parsePatch(value: unknown, mode: AgentResponseImportMode, warnings: string[]): { patch?: PatchV1; hasDeleteOps: boolean } {
  if (!isRecord(value) || value.kind !== "kj-atlas-patch" || value.version !== 1 || !Array.isArray(value.ops)) {
    warnings.push("patch.invalid_shape");
    return { hasDeleteOps: false };
  }

  const validOps = value.ops
    .map((op) => parsePatchOp(op))
    .filter((op): op is PatchOp => op !== null);
  if (validOps.length !== value.ops.length) {
    warnings.push("patch.ops_outside_whitelist_discarded");
  }
  if (mode === "strict" && validOps.length !== value.ops.length) {
    return { hasDeleteOps: false };
  }

  const hasDeleteOps = validOps.some((op) => op.kind.startsWith("delete_"));

  const patch: PatchV1 = {
    kind: "kj-atlas-patch",
    version: 1,
    baseDocSignature: typeof value.baseDocSignature === "string" ? value.baseDocSignature : undefined,
    author: sanitizeString(value.author),
    authorNote: sanitizeString(value.authorNote),
    sourceApp: sanitizeString(value.sourceApp),
    ops: validOps,
  };
  return { patch, hasDeleteOps };
}

function parseProposal(value: unknown, mode: AgentResponseImportMode): { proposal?: ParsedAgentProposal; errors: string[]; warnings: string[] } {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!isRecord(value)) {
    return { errors: ["proposal.not_an_object"], warnings };
  }

  const proposalId = typeof value.proposalId === "string" && value.proposalId.length > 0 ? value.proposalId : undefined;
  const kind = typeof value.kind === "string" && (AGENT_RESPONSE_PROPOSAL_KINDS as readonly string[]).includes(value.kind)
    ? (value.kind as AgentResponseProposalKind)
    : undefined;
  if (!proposalId || !kind) {
    return { errors: ["proposal.missing_proposalId_or_kind"], warnings };
  }

  // §4.2 anti-scoring: forbidden numeric-evaluation fields are discarded and
  // warned in lenient mode; strict mode rejects the whole proposal outright.
  const forbiddenFieldsPresent = FORBIDDEN_SCORING_FIELDS.filter((field) => field in value);
  if (forbiddenFieldsPresent.length > 0) {
    if (mode === "strict") {
      return { errors: [`proposal.forbidden_scoring_fields:${forbiddenFieldsPresent.join(",")}`], warnings };
    }
    warnings.push(`proposal.forbidden_scoring_fields_discarded:${forbiddenFieldsPresent.join(",")}`);
  }

  const rationaleRaw = sanitizeString(value.rationale);
  const rationaleStated = Boolean(rationaleRaw && rationaleRaw.trim().length > 0);
  if (!rationaleStated) {
    if (mode === "strict") {
      return { errors: ["proposal.missing_rationale"], warnings };
    }
    warnings.push("proposal.missing_rationale_labeled");
  }

  let patch: PatchV1 | undefined;
  let patchHasDeleteOps = false;
  if (kind === "patch") {
    const parsedPatch = parsePatch(value.patch, mode, warnings);
    if (!parsedPatch.patch) {
      return { errors: ["proposal.patch_missing_or_invalid"], warnings };
    }
    patch = parsedPatch.patch;
    patchHasDeleteOps = parsedPatch.hasDeleteOps;
  }

  const content = parseContent(value.content);
  if (kind === "merge_candidate" && !isMergeMethod(content.mergeMethod)) {
    return { errors: ["proposal.merge_candidate_missing_or_invalid_merge_method"], warnings };
  }

  const proposal: ParsedAgentProposal = {
    proposalId: sanitizeMarkdownForDisplay(proposalId),
    kind,
    targetRef: parseTargetRef(value.targetRef),
    content,
    rationale: rationaleStated ? (rationaleRaw as string) : "(根拠未記載)",
    rationaleStated,
    patch,
    patchHasDeleteOps,
    warnings,
  };
  return { proposal, errors, warnings };
}

export function parseAgentResponse(rawInput: string, mode: AgentResponseImportMode = "lenient"): AgentResponseImportResult {
  const byteLength = new TextEncoder().encode(rawInput).byteLength;
  if (byteLength > ZIP_MAX_TEXT_FILE_BYTES) {
    return { ok: false, errors: [`payload.exceeds_size_limit:${ZIP_MAX_TEXT_FILE_BYTES}`] };
  }

  const jsonText = extractJsonPayload(rawInput);
  let parsedJson: unknown;
  try {
    parsedJson = JSON.parse(jsonText);
  } catch {
    return { ok: false, errors: ["payload.invalid_json"] };
  }

  if (!isRecord(parsedJson)) {
    return { ok: false, errors: ["payload.not_an_object"] };
  }
  if (parsedJson.schemaVersion !== "agent-response.v1") {
    return { ok: false, errors: ["payload.unsupported_schema_version"] };
  }
  const taskId = typeof parsedJson.taskId === "string" && parsedJson.taskId.length > 0 ? parsedJson.taskId : undefined;
  if (!taskId) {
    return { ok: false, errors: ["payload.missing_taskId"] };
  }
  if (!Array.isArray(parsedJson.proposals)) {
    return { ok: false, errors: ["payload.missing_proposals_array"] };
  }

  const correlation = parseCorrelation(parsedJson.correlation);
  if (!correlation) {
    if (mode === "strict") return { ok: false, errors: ["payload.missing_or_invalid_correlation"] };
  } else if (correlation.taskId !== taskId) {
    return { ok: false, errors: ["payload.correlation_taskId_mismatch"] };
  }

  const allWarnings: string[] = correlation ? [] : ["payload.correlation_missing:unverified_provenance"];
  const proposals: ParsedAgentProposal[] = [];
  for (const [index, rawProposal] of parsedJson.proposals.entries()) {
    const { proposal, errors, warnings } = parseProposal(rawProposal, mode);
    if (errors.length > 0) {
      if (mode === "strict") {
        return { ok: false, errors: errors.map((error) => `proposals[${index}].${error}`) };
      }
      allWarnings.push(...errors.map((error) => `proposals[${index}].${error}:discarded`));
      continue;
    }
    if (proposal) {
      proposals.push(proposal);
      allWarnings.push(...warnings.map((warning) => `proposals[${index}].${warning}`));
    }
  }

  return {
    ok: true,
    response: {
      schemaVersion: "agent-response.v1",
      taskId: sanitizeMarkdownForDisplay(taskId),
      correlation,
      respondedAt: sanitizeString(parsedJson.respondedAt),
      agent: sanitizeString(parsedJson.agent),
      proposals,
    },
    warnings: allWarnings,
  };
}

// UX-PERF-01: moved from ui/AgentResponseImportPanel.tsx. App.tsx's
// AgentResponseImportPanel component is React.lazy()-loaded (code-split
// out of the main chunk); a static import of this bounding helper from
// the same module would have pulled the whole panel back into the main
// chunk (Rollup merges a module into any chunk that statically reaches
// it, regardless of a separate dynamic import elsewhere), so the
// non-component exports live here instead, where App.tsx can keep
// importing them statically without defeating the split.
export type ImportedProposalStatus = "pending" | "adopted" | "rejected";

export type ImportedProposalReview = ParsedAgentProposal & {
  reviewKey: string;
  taskId: string;
  auditProposalId?: string;
  sourceBundleHash?: string;
  provenance: AgentResponseProvenance;
  status: ImportedProposalStatus;
  orphaned: boolean;
  patchSignatureMismatch?: boolean;
};

// FB-RM-UX-02: bound the review list without ever dropping unresolved work.
// A pending review must survive (the user still has to act on it); only the
// most recent `resolvedLimit` adopted/rejected entries are retained, so the
// DOM/heap cannot grow without limit across repeated agent-response imports.
export function boundResolvedAgentImportedProposalReviews(
  reviews: ImportedProposalReview[],
  resolvedLimit = 50,
): ImportedProposalReview[] {
  const pending: ImportedProposalReview[] = [];
  const resolved: ImportedProposalReview[] = [];
  for (const review of reviews) {
    (review.status === "pending" ? pending : resolved).push(review);
  }
  return [...pending, ...resolved.slice(-Math.max(resolvedLimit, 0))];
}
