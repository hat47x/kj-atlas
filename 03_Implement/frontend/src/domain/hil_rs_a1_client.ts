import {
  HIL_RS_CONTRACT_IDS,
  HIL_RS_ERROR_CODES,
  HIL_RS_ERROR_SCHEMA_VERSION,
  HIL_RS_REDIFF_SCHEMA_VERSION,
  type HilRsContractErrorEnvelope,
  type HilRsCritiqueInput,
  type HilRsErrorCode,
  type HilRsRediffPayload,
  type HilRsReviewAttribution,
  validateHilRsContractErrorEnvelope,
  validateHilRsCritiqueInput,
  validateHilRsRediffPayload,
} from "./hil_rs_contract";
import { createHilRsReviewAttribution } from "./hil_rs_payload";

export type UnknownFailure = {
  message: string;
  contractId?: HilRsContractErrorEnvelope["contractId"];
  errorCode?: HilRsErrorCode;
  retryable?: boolean;
  occurredAt?: string;
};

export type CritiqueAcceptedV1 = {
  contractId: typeof HIL_RS_CONTRACT_IDS.critique;
  schemaVersion: HilRsCritiqueInput["schemaVersion"];
  critiqueId: string;
  accepted: true;
};

export type ReDiffAcceptedV1 = {
  contractId: typeof HIL_RS_CONTRACT_IDS.rediff;
  schemaVersion: typeof HIL_RS_REDIFF_SCHEMA_VERSION;
  proposalId: string;
  traceKey: string;
  accepted: true;
};

export type AttributionRecordedV1 = {
  contractId: typeof HIL_RS_CONTRACT_IDS.attribution;
  schemaVersion: HilRsReviewAttribution["schemaVersion"];
  reviewState: HilRsReviewAttribution["reviewState"];
  recorded: true;
};

export function submitCritique(input: HilRsCritiqueInput): CritiqueAcceptedV1 {
  if (!validateHilRsCritiqueInput(input)) {
    throw new Error("A1-CRITIQUE-IF validation failed");
  }

  return {
    contractId: HIL_RS_CONTRACT_IDS.critique,
    schemaVersion: input.schemaVersion,
    critiqueId: input.critiqueId,
    accepted: true,
  };
}

export function proposeReDiff(input: HilRsRediffPayload): ReDiffAcceptedV1 {
  if (!validateHilRsRediffPayload(input)) {
    throw new Error("A1-REDIFF-IF validation failed");
  }

  return {
    contractId: HIL_RS_CONTRACT_IDS.rediff,
    schemaVersion: input.schemaVersion,
    proposalId: input.proposalId,
    traceKey: input.traceKey,
    accepted: true,
  };
}

export function recordReviewAttribution(input: HilRsReviewAttribution): AttributionRecordedV1 {
  const normalized = createHilRsReviewAttribution(input);
  if (!normalized) {
    throw new Error("A1-ATTR-IF validation failed");
  }

  return {
    contractId: HIL_RS_CONTRACT_IDS.attribution,
    schemaVersion: normalized.schemaVersion,
    reviewState: normalized.reviewState,
    recorded: true,
  };
}

export function toContractError(input: UnknownFailure): HilRsContractErrorEnvelope {
  const occurredAt = input.occurredAt ?? new Date().toISOString();
  const normalizedCode = input.errorCode ?? "A1_REQUIRED_FIELD_MISSING";
  const errorCode = HIL_RS_ERROR_CODES.includes(normalizedCode) ? normalizedCode : "A1_REQUIRED_FIELD_MISSING";
  const message = input.message.trim();

  const envelope: HilRsContractErrorEnvelope = {
    schemaVersion: HIL_RS_ERROR_SCHEMA_VERSION,
    errorCode,
    message,
    contractId: input.contractId ?? HIL_RS_CONTRACT_IDS.critique,
    retryable: Boolean(input.retryable),
    occurredAt,
  };

  if (!validateHilRsContractErrorEnvelope(envelope)) {
    throw new Error("A1-ERROR-IF validation failed");
  }

  return envelope;
}
