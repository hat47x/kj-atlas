export const MERGE_METHODS = ["near_duplicate", "kernel_fusion"] as const;

export type MergeMethod = (typeof MERGE_METHODS)[number];

export function isMergeMethod(value: unknown): value is MergeMethod {
  return typeof value === "string" && MERGE_METHODS.includes(value as MergeMethod);
}
