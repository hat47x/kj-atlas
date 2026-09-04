import type { MergeMethod } from "../domain/merge_method";

export type MergeMethodLabelLocale = "ja" | "en";

export function mergeMethodFieldLabel(locale: MergeMethodLabelLocale): string {
  return locale === "ja" ? "統合方式" : "Merge method";
}

export function mergeMethodLabel(method: MergeMethod, locale: MergeMethodLabelLocale): string {
  if (locale === "ja") {
    return method === "near_duplicate"
      ? "類似カードの整理（04ステップ型）"
      : "意味核の統合（核融合法型）";
  }

  return method === "near_duplicate"
    ? "Near-duplicate consolidation (04-step style)"
    : "Meaning-kernel integration (KJ nuclear-fusion style)";
}
