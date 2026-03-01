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
