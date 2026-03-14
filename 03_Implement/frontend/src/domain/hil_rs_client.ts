import type { HilRsRediffPayload } from "./hil_rs_contract";
import { validateHilRsRediffPayload } from "./hil_rs_contract";
import type { HilRsPreviewRediffRequest, HilRsStubClient } from "./hil_rs_stub_client";
import { createHilRsStubClient } from "./hil_rs_stub_client";

export type HilRsRediffProvider = {
  proposeReDiff(input: HilRsRediffPayload): HilRsRediffPayload | null;
};

export type CreateHilRsClientOptions = {
  rediffProvider?: HilRsRediffProvider;
};

function requestToDraftPayload(client: HilRsStubClient, request: HilRsPreviewRediffRequest): HilRsRediffPayload | null {
  return client.previewRediff(request);
}

export function createHilRsClient(options: CreateHilRsClientOptions = {}): HilRsStubClient {
  const stubClient = createHilRsStubClient();

  return {
    collectCritiqueInputs: stubClient.collectCritiqueInputs,
    previewRediff(request) {
      const draftPayload = requestToDraftPayload(stubClient, request);
      if (!draftPayload || !options.rediffProvider) {
        return draftPayload;
      }

      const providerPayload = options.rediffProvider.proposeReDiff(draftPayload);
      if (!providerPayload) {
        return draftPayload;
      }

      return validateHilRsRediffPayload(providerPayload) ? providerPayload : draftPayload;
    },
  };
}
