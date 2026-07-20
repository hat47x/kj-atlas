import { describe, expect, test } from "vitest";
import { STREAM_B_CONTRACTS } from "./stream_b_contract";
import type { StreamBContractId, StreamBSchemaVersion } from "./stream_b_contract";

describe("STREAM_B_CONTRACTS", () => {
  test("candidateGroup has a non-empty contractId and schemaVersion", () => {
    expect(STREAM_B_CONTRACTS.candidateGroup.contractId).toBeTruthy();
    expect(STREAM_B_CONTRACTS.candidateGroup.schemaVersion).toBeTruthy();
  });

  test("decisionLog has a non-empty contractId and schemaVersion", () => {
    expect(STREAM_B_CONTRACTS.decisionLog.contractId).toBeTruthy();
    expect(STREAM_B_CONTRACTS.decisionLog.schemaVersion).toBeTruthy();
  });

  test("contract IDs differ between the two entries", () => {
    expect(STREAM_B_CONTRACTS.candidateGroup.contractId).not.toBe(
      STREAM_B_CONTRACTS.decisionLog.contractId,
    );
  });

  test("schema versions are valid semver strings", () => {
    const semverPattern = /^\d+\.\d+\.\d+$/;
    expect(STREAM_B_CONTRACTS.candidateGroup.schemaVersion).toMatch(semverPattern);
    expect(STREAM_B_CONTRACTS.decisionLog.schemaVersion).toMatch(semverPattern);
  });

  test("derived union types accept literal contract IDs", () => {
    const id: StreamBContractId = STREAM_B_CONTRACTS.candidateGroup.contractId;
    expect(id).toBe("CTR-2B-01-CANDIDATE-GROUP-V1");
  });

  test("derived union types accept literal schema versions", () => {
    const version: StreamBSchemaVersion = STREAM_B_CONTRACTS.decisionLog.schemaVersion;
    expect(version).toBe("1.0.0");
  });
});
