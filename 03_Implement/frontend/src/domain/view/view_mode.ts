export const VIEW_MODE_VALUES = ["explore", "review", "summary"] as const;

export type ViewMode = (typeof VIEW_MODE_VALUES)[number];

export function isViewMode(value: unknown): value is ViewMode {
  return typeof value === "string" && VIEW_MODE_VALUES.includes(value as ViewMode);
}

export function getPresetIdForViewMode(mode: ViewMode): string {
  if (mode === "review") return "default-review";
  if (mode === "summary") return "default-summary";
  return "default-explore";
}

export function getViewModeForPresetId(presetId: string | null | undefined): ViewMode | null {
  if (presetId === "default-explore") return "explore";
  if (presetId === "default-review") return "review";
  if (presetId === "default-summary") return "summary";
  return null;
}

export function getViewModeLabel(mode: ViewMode): string {
  if (mode === "review") return "Review";
  if (mode === "summary") return "Summary";
  return "Explore";
}
