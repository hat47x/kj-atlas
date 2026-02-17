import type { PatchV1 } from "./patch_types";

type JsonPrimitive = string | number | boolean | null;
type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function compareCodeUnitString(left: string, right: string): number {
  if (left === right) return 0;
  return left < right ? -1 : 1;
}

function normalizeForFingerprint(value: unknown, path: string[]): JsonValue {
  if (value === null || typeof value === "string" || typeof value === "boolean") {
    return value;
  }

  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null;
  }

  if (Array.isArray(value)) {
    if (path.length === 1 && path[0] === "ops") {
      const sorted = [...value].sort((left, right) => {
        const leftId = isRecord(left) && typeof left.id === "string" ? left.id : "";
        const rightId = isRecord(right) && typeof right.id === "string" ? right.id : "";
        return compareCodeUnitString(leftId, rightId);
      });
      return sorted.map((item, index) => normalizeForFingerprint(item, [...path, String(index)]));
    }

    return value.map((item, index) => normalizeForFingerprint(item, [...path, String(index)]));
  }

  if (isRecord(value)) {
    const result: { [key: string]: JsonValue } = {};
    const keys = Object.keys(value).sort(compareCodeUnitString);

    for (const key of keys) {
      const nextPath = [...path, key];
      result[key] = normalizeForFingerprint(value[key], nextPath);
    }

    return result;
  }

  return null;
}

function toCanonicalJson(value: JsonValue): string {
  if (value === null) return "null";
  if (typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number") return Number.isFinite(value) ? JSON.stringify(value) : "null";
  if (typeof value === "boolean") return value ? "true" : "false";

  if (Array.isArray(value)) {
    return `[${value.map((item) => toCanonicalJson(item)).join(",")}]`;
  }

  const entries = Object.keys(value)
    .sort(compareCodeUnitString)
    .map((key) => `${JSON.stringify(key)}:${toCanonicalJson(value[key])}`);

  return `{${entries.join(",")}}`;
}

// Fingerprint uses canonicalized JSON with normalized `ops` order by op.id.
// This does not affect patch execution order in runtime.
export function canonicalizeJson(value: unknown): string {
  return toCanonicalJson(normalizeForFingerprint(value, []));
}

async function sha256Hex(input: string): Promise<string> {
  const encoder = new TextEncoder();
  const bytes = encoder.encode(input);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

export async function computePatchFingerprint(patch: PatchV1): Promise<string> {
  const { patchFingerprint: _ignoredFingerprint, ...rest } = patch;
  const payload = { ...rest, patchFingerprint: null };
  const canonical = canonicalizeJson(payload);
  return sha256Hex(canonical);
}

export async function verifyPatchFingerprint(patch: PatchV1): Promise<{ ok: boolean; expected: string; actual?: string }> {
  if (!patch.patchFingerprint) {
    return { ok: false, expected: "" };
  }

  const actual = await computePatchFingerprint(patch);
  return {
    ok: actual === patch.patchFingerprint,
    expected: patch.patchFingerprint,
    actual,
  };
}
