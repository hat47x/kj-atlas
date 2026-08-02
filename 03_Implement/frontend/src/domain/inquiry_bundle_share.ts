import {
  serializeInquiryBundle,
  type InquiryBundleIoError,
} from "./inquiry_bundle_io";
import {
  deriveInquiryRoundBundle,
  type InquiryBundleProjectionResult,
} from "./inquiry_bundle_projection";
import { deriveInquirySafeModeBundle } from "./inquiry_bundle_safe_mode";
import type { InquiryBundleV1 } from "./inquiry_journey";

export type InquiryBundleShareResult =
  | { ok: true; bundle: InquiryBundleV1; json: string }
  | Exclude<InquiryBundleProjectionResult, { ok: true }>
  | { ok: false; reason: "serialization_failed"; errors: InquiryBundleIoError[] };

/**
 * Builds an external-use inquiry artifact with a verifiable scope declaration.
 *
 * Existing export metadata is removed before projection so callers cannot carry
 * a stale scope or SafeMode claim into a new artifact. The source bundle remains
 * unchanged, and SafeMode is always applied regardless of the current UI toggle.
 */
export async function prepareInquiryBundleForShare(
  source: InquiryBundleV1,
  selectedRoundId?: string,
): Promise<InquiryBundleShareResult> {
  const sourceWithoutExportInfo = structuredClone(source);
  delete sourceWithoutExportInfo.exportInfo;

  const projection = selectedRoundId
    ? deriveInquiryRoundBundle(sourceWithoutExportInfo, selectedRoundId)
    : { ok: true as const, bundle: sourceWithoutExportInfo };
  if (!projection.ok) return projection;

  const safeModeResult = await deriveInquirySafeModeBundle(projection.bundle);
  if (!safeModeResult.ok) {
    return {
      ok: false,
      reason: "serialization_failed",
      errors: safeModeResult.errors,
    };
  }

  const externalBundle: InquiryBundleV1 = {
    ...safeModeResult.bundle,
    exportInfo: selectedRoundId
      ? {
          scope: "round",
          selectedRoundId,
          safeModeApplied: true,
        }
      : {
          scope: "full",
          safeModeApplied: true,
        },
  };
  const serialized = await serializeInquiryBundle(externalBundle);
  return serialized.ok
    ? { ok: true, bundle: serialized.bundle, json: serialized.json }
    : {
        ok: false,
        reason: "serialization_failed",
        errors: serialized.errors,
      };
}
