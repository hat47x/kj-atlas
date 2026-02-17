import type { PatchV1 } from "./patch_types";
import { computePatchFingerprint } from "./patch_fingerprint";

export type PatchExportMetadata = {
  author?: string;
  authorNote?: string;
  sourceApp?: string;
};

function cleanOptionalText(value: string | undefined): string | undefined {
  if (!value) return undefined;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

export async function buildPatchForExport(patch: PatchV1, metadata: PatchExportMetadata): Promise<PatchV1> {
  const next: PatchV1 = {
    ...patch,
    author: cleanOptionalText(metadata.author),
    authorNote: cleanOptionalText(metadata.authorNote),
    sourceApp: cleanOptionalText(metadata.sourceApp) ?? "kj-atlas",
  };

  const fingerprint = await computePatchFingerprint(next);
  return {
    ...next,
    patchFingerprint: fingerprint,
  };
}
