import { DEFAULT_PACK_VISIBILITY, isPublishVisibility, type PublishVisibility } from "../domain/policy/publish_visibility";
import { normalizeAccessControlMetadata, validateAccessControlMetadata, type AccessControlMetadata } from "../domain/policy/access_control_metadata";

export type PublicPackManifestEntry = {
  id: string;
  title?: string;
  documentPath: string;
  viewPath?: string;
  enforceSafeMode?: boolean;
  readOnly?: boolean;
  visibility: PublishVisibility;
  accessControl?: AccessControlMetadata;
};

export type PublicPackManifest = {
  defaultPackId?: string;
  packs: PublicPackManifestEntry[];
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function parseEntry(value: unknown): PublicPackManifestEntry | null {
  if (!isRecord(value)) {
    return null;
  }
  if (typeof value.id !== "string" || value.id.trim().length === 0) {
    return null;
  }
  if (typeof value.documentPath !== "string" || value.documentPath.trim().length === 0) {
    return null;
  }

  if (value.visibility !== undefined && !isPublishVisibility(value.visibility)) {
    return null;
  }

  const accessControlError = validateAccessControlMetadata(value.accessControl, "packs[*].accessControl");
  if (accessControlError) {
    return null;
  }

  return {
    id: value.id,
    ...(typeof value.title === "string" ? { title: value.title } : {}),
    documentPath: value.documentPath,
    ...(typeof value.viewPath === "string" ? { viewPath: value.viewPath } : {}),
    ...(typeof value.enforceSafeMode === "boolean" ? { enforceSafeMode: value.enforceSafeMode } : {}),
    ...(typeof value.readOnly === "boolean" ? { readOnly: value.readOnly } : {}),
    visibility: value.visibility === undefined ? DEFAULT_PACK_VISIBILITY : value.visibility,
    ...(normalizeAccessControlMetadata(value.accessControl) ? { accessControl: normalizeAccessControlMetadata(value.accessControl) } : {}),
  };
}

export function parsePublicPackManifest(input: unknown): PublicPackManifest {
  if (!isRecord(input)) {
    return { packs: [] };
  }

  const rawPacks = Array.isArray(input.packs) ? input.packs : [];
  const packs = rawPacks.map((entry) => parseEntry(entry)).filter((entry): entry is PublicPackManifestEntry => entry !== null);

  return {
    ...(typeof input.defaultPackId === "string" ? { defaultPackId: input.defaultPackId } : {}),
    packs,
  };
}
