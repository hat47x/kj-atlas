import { DEFAULT_PACK_VISIBILITY, isPublishVisibility, type PublishVisibility } from "../domain/policy/publish_visibility";

export type PublicPackManifestEntry = {
  id: string;
  title?: string;
  documentPath: string;
  viewPath?: string;
  enforceSafeMode?: boolean;
  readOnly?: boolean;
  visibility: PublishVisibility;
};

export type PublicPackManifest = {
  defaultPackId?: string;
  packs: PublicPackManifestEntry[];
};

export type PublicPackManifestValidationError = {
  path: string;
  message: string;
};

type PublicPackManifestValidationResult =
  | { ok: true; manifest: PublicPackManifest }
  | { ok: false; errors: PublicPackManifestValidationError[] };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function parseEntry(value: unknown, index: number): { ok: true; entry: PublicPackManifestEntry } | { ok: false; errors: PublicPackManifestValidationError[] } {
  const entryPath = `packs[${index}]`;
  const errors: PublicPackManifestValidationError[] = [];

  if (!isRecord(value)) {
    return { ok: false, errors: [{ path: entryPath, message: "Entry must be an object." }] };
  }

  if (typeof value.id !== "string" || value.id.trim().length === 0) {
    errors.push({ path: `${entryPath}.id`, message: "id must be a non-empty string." });
  }
  if (typeof value.documentPath !== "string" || value.documentPath.trim().length === 0) {
    errors.push({ path: `${entryPath}.documentPath`, message: "documentPath must be a non-empty string." });
  }

  if (value.visibility !== undefined && !isPublishVisibility(value.visibility)) {
    errors.push({ path: `${entryPath}.visibility`, message: 'visibility must be "Public" | "Unlisted" | "Org" | "Restricted" when present.' });
  }

  if (value.enforceSafeMode !== undefined && typeof value.enforceSafeMode !== "boolean") {
    errors.push({ path: `${entryPath}.enforceSafeMode`, message: "enforceSafeMode must be a boolean when present." });
  }

  if (value.readOnly !== undefined && typeof value.readOnly !== "boolean") {
    errors.push({ path: `${entryPath}.readOnly`, message: "readOnly must be a boolean when present." });
  }

  if (errors.length > 0) {
    return { ok: false, errors };
  }

  const id = value.id as string;
  const documentPath = value.documentPath as string;
  const visibility = (value.visibility === undefined ? DEFAULT_PACK_VISIBILITY : value.visibility) as PublishVisibility;

  return {
    ok: true,
    entry: {
      id,
      ...(typeof value.title === "string" ? { title: value.title } : {}),
      documentPath,
      ...(typeof value.viewPath === "string" ? { viewPath: value.viewPath } : {}),
      ...(typeof value.enforceSafeMode === "boolean" ? { enforceSafeMode: value.enforceSafeMode } : {}),
      ...(typeof value.readOnly === "boolean" ? { readOnly: value.readOnly } : {}),
      visibility,
    },
  };
}

export function validatePublicPackManifest(input: unknown): PublicPackManifestValidationResult {
  if (!isRecord(input)) {
    return { ok: false, errors: [{ path: "", message: "Manifest must be an object." }] };
  }

  if (!Array.isArray(input.packs)) {
    return { ok: false, errors: [{ path: "packs", message: "packs must be an array." }] };
  }

  const packs: PublicPackManifestEntry[] = [];
  const errors: PublicPackManifestValidationError[] = [];

  input.packs.forEach((entry, index) => {
    const parsedEntry = parseEntry(entry, index);
    if (!parsedEntry.ok) {
      errors.push(...parsedEntry.errors);
      return;
    }

    packs.push(parsedEntry.entry);
  });

  if (errors.length > 0) {
    return { ok: false, errors };
  }

  const manifest: PublicPackManifest = {
    packs,
  };

  if (input.defaultPackId !== undefined && typeof input.defaultPackId !== "string") {
    return { ok: false, errors: [{ path: "defaultPackId", message: "defaultPackId must be a string when present." }] };
  }

  if (typeof input.defaultPackId === "string") {
    manifest.defaultPackId = input.defaultPackId;
  }

  return { ok: true, manifest };
}

export function parsePublicPackManifest(input: unknown): PublicPackManifest {
  const result = validatePublicPackManifest(input);
  if (!result.ok) {
    return { packs: [] };
  }

  return result.manifest;
}
