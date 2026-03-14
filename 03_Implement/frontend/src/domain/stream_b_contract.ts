export const STREAM_B_CONTRACTS = {
  candidateGroup: {
    contractId: "CTR-2B-01-CANDIDATE-GROUP-V1",
    schemaVersion: "1.0.0",
  },
  decisionLog: {
    contractId: "CTR-2B-02-DECISION-LOG-V1",
    schemaVersion: "1.0.0",
  },
} as const;

export type StreamBContractId =
  | (typeof STREAM_B_CONTRACTS.candidateGroup)["contractId"]
  | (typeof STREAM_B_CONTRACTS.decisionLog)["contractId"];

export type StreamBSchemaVersion =
  | (typeof STREAM_B_CONTRACTS.candidateGroup)["schemaVersion"]
  | (typeof STREAM_B_CONTRACTS.decisionLog)["schemaVersion"];
