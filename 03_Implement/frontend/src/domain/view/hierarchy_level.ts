export const HIERARCHY_LEVELS = ["overview", "mid", "detail"] as const;

export type HierarchyLevel = (typeof HIERARCHY_LEVELS)[number];

export function resolveHierarchyLevel(maxDepth: number | "all"): HierarchyLevel {
  if (maxDepth === "all") {
    return "detail";
  }

  if (maxDepth <= 0) {
    return "overview";
  }

  return "mid";
}

export function maxDepthForHierarchyLevel(level: HierarchyLevel): number | "all" {
  if (level === "overview") {
    return 0;
  }

  if (level === "mid") {
    return 1;
  }

  return "all";
}

/**
 * QA-MONKEY-13 regression guard: clamps `maxDepth` to `maxAvailableDepth`
 * only when the document actually has nested islands (`maxAvailableDepth >
 * 0`). Without that guard, a document with zero nested islands
 * (`maxAvailableDepth === 0`) would clamp an explicit "mid" choice
 * (`maxDepth = 1`) down to 0, which the sync effect in App.tsx then
 * re-resolves to "overview" -- silently overriding the user's selection.
 * `"all"` (detail) is never clamped.
 */
export function clampMaxDepthToAvailable(maxDepth: number | "all", maxAvailableDepth: number): number | "all" {
  if (typeof maxDepth !== "number") {
    return maxDepth;
  }
  if (maxDepth > maxAvailableDepth && maxAvailableDepth > 0) {
    return maxAvailableDepth;
  }
  return maxDepth;
}
