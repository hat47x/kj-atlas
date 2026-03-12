import type { DocumentV2 } from "./types";
import type { HilRsCritiqueInput, HilRsRediffPayload } from "./hil_rs_contract";
import { validateHilRsCritiqueInput, validateHilRsRediffPayload } from "./hil_rs_contract";

type BuildHilRsRediffStubOptions = {
  suggestionId: string;
  iteration: number;
  critiqueInputs: readonly HilRsCritiqueInput[];
};

function buildTraceKey(critiqueInputs: readonly HilRsCritiqueInput[]): string {
  const canonicalCritiqueIds = [...new Set(critiqueInputs.map((input) => input.critiqueId))].sort();
  return `trace:${canonicalCritiqueIds.join("+")}`;
}

export function buildHilRsRediffStub(
  currentDocument: DocumentV2,
  suggestedDocument: DocumentV2,
  options: BuildHilRsRediffStubOptions,
): HilRsRediffPayload | null {
  if (!Number.isInteger(options.iteration) || options.iteration < 1 || options.suggestionId.trim().length === 0) {
    return null;
  }
  if (options.critiqueInputs.length === 0) {
    return null;
  }
  if (
    options.critiqueInputs.some(
      (input) => !validateHilRsCritiqueInput(input) || input.iteration !== options.iteration,
    )
  ) {
    return null;
  }

  const currentCardsById = new Map(currentDocument.cards.map((card) => [card.id, card] as const));
  const suggestedCardsById = new Map(suggestedDocument.cards.map((card) => [card.id, card] as const));

  const diffOps: HilRsRediffPayload["diffOps"] = [];

  for (const suggestedCard of suggestedDocument.cards) {
    const currentCard = currentCardsById.get(suggestedCard.id);
    if (!currentCard) {
      diffOps.push({
        opId: `op:add:${suggestedCard.id}`,
        opType: "add",
        targetRef: `card:${suggestedCard.id}`,
        before: null,
        after: { x: suggestedCard.x, y: suggestedCard.y },
      });
      continue;
    }

    if (currentCard.x !== suggestedCard.x || currentCard.y !== suggestedCard.y) {
      diffOps.push({
        opId: `op:move:${suggestedCard.id}`,
        opType: "move",
        targetRef: `card:${suggestedCard.id}`,
        before: { x: currentCard.x, y: currentCard.y },
        after: { x: suggestedCard.x, y: suggestedCard.y },
      });
    }
  }

  for (const currentCard of currentDocument.cards) {
    if (!suggestedCardsById.has(currentCard.id)) {
      diffOps.push({
        opId: `op:remove:${currentCard.id}`,
        opType: "remove",
        targetRef: `card:${currentCard.id}`,
        before: { x: currentCard.x, y: currentCard.y },
        after: null,
      });
    }
  }

  if (diffOps.length === 0) {
    return null;
  }

  const candidate: HilRsRediffPayload = {
    proposalId: options.suggestionId,
    basedOnIteration: options.iteration,
    traceKey: buildTraceKey(options.critiqueInputs),
    diffOps,
  };

  return validateHilRsRediffPayload(candidate) ? candidate : null;
}
