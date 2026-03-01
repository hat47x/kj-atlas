export const PUBLISH_VISIBILITY_VALUES = ["Public", "Unlisted", "Org", "Restricted"] as const;

export type PublishVisibility = (typeof PUBLISH_VISIBILITY_VALUES)[number];

export const DEFAULT_VIEW_VISIBILITY: PublishVisibility = "Restricted";
export const DEFAULT_PACK_VISIBILITY: PublishVisibility = "Public";

export function isPublishVisibility(value: unknown): value is PublishVisibility {
  return typeof value === "string" && PUBLISH_VISIBILITY_VALUES.includes(value as PublishVisibility);
}

export function normalizeViewVisibility(value: unknown): PublishVisibility {
  return isPublishVisibility(value) ? value : DEFAULT_VIEW_VISIBILITY;
}

export function normalizePackVisibility(value: unknown): PublishVisibility {
  return isPublishVisibility(value) ? value : DEFAULT_PACK_VISIBILITY;
}
