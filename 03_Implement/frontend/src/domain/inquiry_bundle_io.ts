import { canonicalizeJson } from "./patch/patch_fingerprint";
import { validateDocumentV1Strict } from "./validate_doc";
import {
  INQUIRY_SCHEMA_VERSION,
  validateInquiryBundle,
  type InquiryBundleV1,
  type RoundSnapshotV1,
} from "./inquiry_journey";

export type InquiryBundleIoError = {
  code: "invalid_json" | "invalid_shape" | "invalid_bundle" | "digest_mismatch";
  path: string;
  message: string;
};

export type InquiryBundleIoResult =
  | { ok: true; bundle: InquiryBundleV1 }
  | { ok: false; errors: InquiryBundleIoError[] };

type ShapeErrors = InquiryBundleIoError[];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function checkKeys(value: Record<string, unknown>, allowed: readonly string[], path: string, errors: ShapeErrors): void {
  const allowedSet = new Set(allowed);
  for (const key of Object.keys(value)) {
    if (!allowedSet.has(key)) {
      errors.push({ code: "invalid_shape", path: `${path}.${key}`, message: "Unknown field." });
    }
  }
}

function requireString(value: unknown, path: string, errors: ShapeErrors): value is string {
  if (typeof value === "string") return true;
  errors.push({ code: "invalid_shape", path, message: "Must be a string." });
  return false;
}

function requireStringArray(value: unknown, path: string, errors: ShapeErrors): value is string[] {
  if (!Array.isArray(value)) {
    errors.push({ code: "invalid_shape", path, message: "Must be an array of strings." });
    return false;
  }
  let valid = true;
  value.forEach((entry, index) => {
    if (!requireString(entry, `${path}[${index}]`, errors)) valid = false;
  });
  return valid;
}

function requireEnum(value: unknown, allowed: readonly string[], path: string, errors: ShapeErrors): value is string {
  if (!requireString(value, path, errors)) return false;
  if (allowed.includes(value)) return true;
  errors.push({ code: "invalid_shape", path, message: `Must be one of: ${allowed.join(", ")}.` });
  return false;
}

function validateAddress(value: unknown, path: string, errors: ShapeErrors): void {
  if (!isRecord(value)) {
    errors.push({ code: "invalid_shape", path, message: "Must be a card address object." });
    return;
  }
  checkKeys(value, ["snapshotId", "cardId"], path, errors);
  requireString(value.snapshotId, `${path}.snapshotId`, errors);
  requireString(value.cardId, `${path}.cardId`, errors);
}

function validateArtifactRef(value: unknown, path: string, errors: ShapeErrors): void {
  if (!isRecord(value)) {
    errors.push({ code: "invalid_shape", path, message: "Must be an artifact reference object." });
    return;
  }
  checkKeys(value, ["snapshotId", "kind", "entityId"], path, errors);
  requireString(value.snapshotId, `${path}.snapshotId`, errors);
  requireEnum(value.kind, ["card", "island", "narrative", "relation_summary"], `${path}.kind`, errors);
  requireString(value.entityId, `${path}.entityId`, errors);
}

function validateHandoff(value: unknown, path: string, errors: ShapeErrors): void {
  if (!isRecord(value)) {
    errors.push({ code: "invalid_shape", path, message: "Must be a handoff object." });
    return;
  }
  checkKeys(value, ["carryoverRefs", "heldRefs", "unresolvedQuestions", "fieldworkRequests", "understandingDelta"], path, errors);
  for (const key of ["carryoverRefs", "heldRefs"] as const) {
    if (!Array.isArray(value[key])) {
      errors.push({ code: "invalid_shape", path: `${path}.${key}`, message: "Must be an array." });
    } else {
      value[key].forEach((entry, index) => validateArtifactRef(entry, `${path}.${key}[${index}]`, errors));
    }
  }
  requireStringArray(value.unresolvedQuestions, `${path}.unresolvedQuestions`, errors);
  if (!Array.isArray(value.fieldworkRequests)) {
    errors.push({ code: "invalid_shape", path: `${path}.fieldworkRequests`, message: "Must be an array." });
  } else {
    value.fieldworkRequests.forEach((request, requestIndex) => {
      const requestPath = `${path}.fieldworkRequests[${requestIndex}]`;
      if (!isRecord(request)) {
        errors.push({ code: "invalid_shape", path: requestPath, message: "Must be a fieldwork request object." });
        return;
      }
      checkKeys(request, ["requestId", "question", "outcome"], requestPath, errors);
      requireString(request.requestId, `${requestPath}.requestId`, errors);
      requireString(request.question, `${requestPath}.question`, errors);
      if (request.outcome !== undefined) {
        const outcomePath = `${requestPath}.outcome`;
        if (!isRecord(request.outcome)) {
          errors.push({ code: "invalid_shape", path: outcomePath, message: "Must be a fieldwork outcome object." });
        } else {
          checkKeys(request.outcome, ["kind", "responseCardRefs", "note"], outcomePath, errors);
          requireEnum(request.outcome.kind, ["answered", "no_result", "unexpected"], `${outcomePath}.kind`, errors);
          if (!Array.isArray(request.outcome.responseCardRefs)) {
            errors.push({ code: "invalid_shape", path: `${outcomePath}.responseCardRefs`, message: "Must be an array." });
          } else {
            request.outcome.responseCardRefs.forEach((address, index) => validateAddress(address, `${outcomePath}.responseCardRefs[${index}]`, errors));
          }
          if (request.outcome.note !== undefined) requireString(request.outcome.note, `${outcomePath}.note`, errors);
        }
      }
    });
  }
  if (value.understandingDelta !== undefined) requireString(value.understandingDelta, `${path}.understandingDelta`, errors);
}

function validateRound(value: unknown, path: string, errors: ShapeErrors): void {
  if (!isRecord(value)) {
    errors.push({ code: "invalid_shape", path, message: "Must be a round record object." });
    return;
  }
  checkKeys(value, ["roundId", "createdAt", "updatedAt", "stage", "iteration", "parentRoundIds", "status", "theme", "inputSnapshotIds", "outputSnapshotId", "handoff"], path, errors);
  for (const key of ["roundId", "createdAt", "updatedAt", "stage", "status", "theme"] as const) {
    requireString(value[key], `${path}.${key}`, errors);
  }
  if (!Number.isSafeInteger(value.iteration)) {
    errors.push({ code: "invalid_shape", path: `${path}.iteration`, message: "Must be a safe integer." });
  }
  requireStringArray(value.parentRoundIds, `${path}.parentRoundIds`, errors);
  requireStringArray(value.inputSnapshotIds, `${path}.inputSnapshotIds`, errors);
  if (value.outputSnapshotId !== undefined) requireString(value.outputSnapshotId, `${path}.outputSnapshotId`, errors);
  if (value.handoff !== undefined) validateHandoff(value.handoff, `${path}.handoff`, errors);
}

function validateJourney(value: unknown, path: string, errors: ShapeErrors): void {
  if (!isRecord(value)) {
    errors.push({ code: "invalid_shape", path, message: "Must be an inquiry journey object." });
    return;
  }
  checkKeys(value, ["schemaVersion", "journeyId", "title", "originSnapshotIds", "roundRecords", "headRoundIds", "defaultHeadRoundId", "createdAt", "updatedAt"], path, errors);
  for (const key of ["schemaVersion", "journeyId", "title", "createdAt", "updatedAt"] as const) {
    requireString(value[key], `${path}.${key}`, errors);
  }
  requireStringArray(value.originSnapshotIds, `${path}.originSnapshotIds`, errors);
  requireStringArray(value.headRoundIds, `${path}.headRoundIds`, errors);
  if (value.defaultHeadRoundId !== undefined) requireString(value.defaultHeadRoundId, `${path}.defaultHeadRoundId`, errors);
  if (!Array.isArray(value.roundRecords)) {
    errors.push({ code: "invalid_shape", path: `${path}.roundRecords`, message: "Must be an array." });
  } else {
    value.roundRecords.forEach((round, index) => validateRound(round, `${path}.roundRecords[${index}]`, errors));
  }
}

function validateSnapshot(value: unknown, path: string, errors: ShapeErrors): void {
  if (!isRecord(value)) {
    errors.push({ code: "invalid_shape", path, message: "Must be a round snapshot object." });
    return;
  }
  checkKeys(value, ["schemaVersion", "snapshotId", "createdAt", "canonicalDigest", "document"], path, errors);
  for (const key of ["schemaVersion", "snapshotId", "createdAt", "canonicalDigest"] as const) {
    requireString(value[key], `${path}.${key}`, errors);
  }
  const documentResult = validateDocumentV1Strict(value.document);
  if (!documentResult.ok) {
    documentResult.errors.forEach((message) => errors.push({ code: "invalid_shape", path: `${path}.document`, message }));
  }
}

function validateLineage(value: unknown, path: string, errors: ShapeErrors): void {
  if (!isRecord(value)) {
    errors.push({ code: "invalid_shape", path, message: "Must be a lineage object." });
    return;
  }
  checkKeys(value, ["lineageId", "kind", "from", "to"], path, errors);
  requireString(value.lineageId, `${path}.lineageId`, errors);
  if (!requireEnum(value.kind, ["carried", "edited", "derived", "split", "merged", "new", "retired"], `${path}.kind`, errors)) return;

  if (value.kind === "new") {
    validateAddress(value.to, `${path}.to`, errors);
  } else if (value.kind === "retired") {
    validateAddress(value.from, `${path}.from`, errors);
  } else if (value.kind === "derived" || value.kind === "merged") {
    if (!Array.isArray(value.from)) {
      errors.push({ code: "invalid_shape", path: `${path}.from`, message: "Must be an array." });
    } else {
      value.from.forEach((address, index) => validateAddress(address, `${path}.from[${index}]`, errors));
    }
    validateAddress(value.to, `${path}.to`, errors);
  } else if (value.kind === "split") {
    validateAddress(value.from, `${path}.from`, errors);
    if (!Array.isArray(value.to)) {
      errors.push({ code: "invalid_shape", path: `${path}.to`, message: "Must be an array." });
    } else {
      value.to.forEach((address, index) => validateAddress(address, `${path}.to[${index}]`, errors));
    }
  } else if (value.kind === "carried" || value.kind === "edited") {
    validateAddress(value.from, `${path}.from`, errors);
    validateAddress(value.to, `${path}.to`, errors);
  }
}

function validateBundleShape(value: unknown): { ok: true; bundle: InquiryBundleV1 } | { ok: false; errors: ShapeErrors } {
  const errors: ShapeErrors = [];
  if (!isRecord(value)) {
    return { ok: false, errors: [{ code: "invalid_shape", path: "$", message: "Bundle must be an object." }] };
  }
  checkKeys(value, ["schemaVersion", "journey", "snapshots", "cardLineage"], "$", errors);
  requireString(value.schemaVersion, "$.schemaVersion", errors);
  validateJourney(value.journey, "$.journey", errors);
  if (!Array.isArray(value.snapshots)) {
    errors.push({ code: "invalid_shape", path: "$.snapshots", message: "Must be an array." });
  } else {
    value.snapshots.forEach((snapshot, index) => validateSnapshot(snapshot, `$.snapshots[${index}]`, errors));
  }
  if (!Array.isArray(value.cardLineage)) {
    errors.push({ code: "invalid_shape", path: "$.cardLineage", message: "Must be an array." });
  } else {
    value.cardLineage.forEach((edge, index) => validateLineage(edge, `$.cardLineage[${index}]`, errors));
  }
  return errors.length > 0 ? { ok: false, errors } : { ok: true, bundle: value as InquiryBundleV1 };
}

async function sha256Hex(value: unknown): Promise<`sha256:${string}`> {
  const bytes = new TextEncoder().encode(canonicalizeJson(value));
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  const hex = Array.from(new Uint8Array(digest), (entry) => entry.toString(16).padStart(2, "0")).join("");
  return `sha256:${hex}`;
}

export async function computeRoundSnapshotDigest(document: RoundSnapshotV1["document"]): Promise<`sha256:${string}`> {
  // Digest the JSON artifact representation. Runtime documents can have own
  // optional properties set to undefined, which JSON serialization omits.
  const jsonDocument = JSON.parse(JSON.stringify(document)) as unknown;
  return sha256Hex(jsonDocument);
}

async function validateDigests(bundle: InquiryBundleV1): Promise<InquiryBundleIoError[]> {
  const errors: InquiryBundleIoError[] = [];
  for (let index = 0; index < bundle.snapshots.length; index += 1) {
    const snapshot = bundle.snapshots[index];
    const actual = await computeRoundSnapshotDigest(snapshot.document);
    if (actual !== snapshot.canonicalDigest) {
      errors.push({
        code: "digest_mismatch",
        path: `$.snapshots[${index}].canonicalDigest`,
        message: `Digest does not match snapshot '${snapshot.snapshotId}'.`,
      });
    }
  }
  return errors;
}

export async function prepareInquiryBundleForExport(bundle: InquiryBundleV1): Promise<InquiryBundleV1> {
  const prepared = structuredClone(bundle);
  prepared.schemaVersion = INQUIRY_SCHEMA_VERSION;
  prepared.journey.schemaVersion = INQUIRY_SCHEMA_VERSION;
  for (const snapshot of prepared.snapshots) {
    snapshot.schemaVersion = INQUIRY_SCHEMA_VERSION;
    snapshot.canonicalDigest = await computeRoundSnapshotDigest(snapshot.document);
  }
  return prepared;
}

export async function serializeInquiryBundle(bundle: InquiryBundleV1): Promise<{ ok: true; json: string; bundle: InquiryBundleV1 } | { ok: false; errors: InquiryBundleIoError[] }> {
  const prepared = await prepareInquiryBundleForExport(bundle);
  const shape = validateBundleShape(prepared);
  if (!shape.ok) return shape;

  const issues = validateInquiryBundle(shape.bundle);
  if (issues.length > 0) {
    return {
      ok: false,
      errors: issues.map((issue) => ({ code: "invalid_bundle", path: issue.path, message: issue.code })),
    };
  }
  return { ok: true, json: `${JSON.stringify(shape.bundle, null, 2)}\n`, bundle: shape.bundle };
}

export async function parseInquiryBundleJson(rawText: string): Promise<InquiryBundleIoResult> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(rawText);
  } catch {
    return { ok: false, errors: [{ code: "invalid_json", path: "$", message: "Invalid JSON." }] };
  }

  const shape = validateBundleShape(parsed);
  if (!shape.ok) return shape;

  const issues = validateInquiryBundle(shape.bundle);
  if (issues.length > 0) {
    return {
      ok: false,
      errors: issues.map((issue) => ({ code: "invalid_bundle", path: issue.path, message: issue.code })),
    };
  }

  const digestErrors = await validateDigests(shape.bundle);
  return digestErrors.length > 0 ? { ok: false, errors: digestErrors } : { ok: true, bundle: shape.bundle };
}
