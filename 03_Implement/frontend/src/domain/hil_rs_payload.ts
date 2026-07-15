import type { A1TargetRef, DocumentV1 } from "./types";
import {
  HIL_RS_CRITIQUE_SCHEMA_VERSION,
  type HilRsCritiqueInput,
  type HilRsCritiqueType,
  type HilRsReviewAttribution,
  validateHilRsCritiqueInput,
  validateHilRsReviewAttribution,
} from "./hil_rs_contract";

type BuildCritiqueOptions = {
  iteration: number;
  createdAt: string;
};

const TAG_TO_CRITIQUE_TYPE: Readonly<Record<string, HilRsCritiqueType>> = {
  too_close: "too_close",
  too_far: "too_far",
  not_the_same: "not_the_same",
  feels_off: "feels_off",
};

function resolveCritiqueTypeFromTags(tags: readonly string[] | undefined): HilRsCritiqueType {
  if (!tags) {
    return "no_articulable_reason";
  }

  for (const tag of tags) {
    const resolved = TAG_TO_CRITIQUE_TYPE[tag];
    if (resolved) {
      return resolved;
    }
  }

  return "no_articulable_reason";
}

function pushCritiqueInput(
  collected: HilRsCritiqueInput[],
  targetRef: A1TargetRef,
  critique: string | undefined,
  critiqueTags: readonly string[] | undefined,
  options: BuildCritiqueOptions,
): void {
  const normalizedComment = typeof critique === "string" && critique.trim().length > 0 ? critique.trim() : undefined;
  const normalizedTags = Array.isArray(critiqueTags)
    ? critiqueTags
        .filter((tag): tag is string => typeof tag === "string")
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0)
    : [];

  if (!normalizedComment && normalizedTags.length === 0) {
    return;
  }

  const candidate: HilRsCritiqueInput = {
    schemaVersion: HIL_RS_CRITIQUE_SCHEMA_VERSION,
    critiqueId: `${targetRef}:${options.iteration}`,
    targetRef,
    critiqueType: resolveCritiqueTypeFromTags(normalizedTags),
    createdAt: options.createdAt,
    iteration: options.iteration,
    comment: normalizedComment,
    constraintHints: normalizedTags.length > 0 ? [...normalizedTags] : undefined,
  };

  if (validateHilRsCritiqueInput(candidate)) {
    collected.push(candidate);
  }
}

export function buildHilRsCritiqueInputs(doc: DocumentV1, options: BuildCritiqueOptions): HilRsCritiqueInput[] {
  if (!Number.isInteger(options.iteration) || options.iteration < 1) {
    return [];
  }

  const collected: HilRsCritiqueInput[] = [];

  for (const card of doc.cards) {
    pushCritiqueInput(collected, `card:${card.id}`, card.critique, card.critiqueTags, options);
  }

  for (const island of doc.islands) {
    pushCritiqueInput(collected, `island:${island.id}`, island.critique, island.critiqueTags, options);
  }

  return collected;
}

export function createHilRsReviewAttribution(attribution: HilRsReviewAttribution): HilRsReviewAttribution | null {
  return validateHilRsReviewAttribution(attribution) ? attribution : null;
}
