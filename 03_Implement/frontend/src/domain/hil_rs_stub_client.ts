import { buildHilRsCritiqueInputs } from "./hil_rs_payload";
import { buildHilRsRediffStub } from "./hil_rs_rediff_stub";
import type { HilRsCritiqueInput, HilRsRediffPayload } from "./hil_rs_contract";
import type { DocumentV1 } from "./types";

export type HilRsCollectCritiqueRequest = {
  document: DocumentV1;
  iteration: number;
  createdAt: string;
};

export type HilRsPreviewRediffRequest = {
  currentDocument: DocumentV1;
  suggestedDocument: DocumentV1;
  suggestionId: string;
  iteration: number;
  critiqueInputs: readonly HilRsCritiqueInput[];
};

export type HilRsStubClient = {
  collectCritiqueInputs(request: HilRsCollectCritiqueRequest): HilRsCritiqueInput[];
  previewRediff(request: HilRsPreviewRediffRequest): HilRsRediffPayload | null;
};

export function createHilRsStubClient(): HilRsStubClient {
  return {
    collectCritiqueInputs(request) {
      return buildHilRsCritiqueInputs(request.document, {
        iteration: request.iteration,
        createdAt: request.createdAt,
      });
    },
    previewRediff(request) {
      return buildHilRsRediffStub(request.currentDocument, request.suggestedDocument, {
        suggestionId: request.suggestionId,
        iteration: request.iteration,
        critiqueInputs: request.critiqueInputs,
      });
    },
  };
}
