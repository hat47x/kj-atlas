import React from "react";
import { P2A_A2_MOCK_FIXTURES } from "../../../domain/p2a/mock_fixtures";
import { evaluateP2AA3Proceed, toP2AValidationLedger } from "../../../domain/p2a/validation";

const panelStyle: React.CSSProperties = {
  border: "1px solid #d0d7de",
  borderRadius: 8,
  padding: 12,
  background: "#f8fafc",
};

export function P2AReadinessPanel(): React.ReactElement {
  const logs = toP2AValidationLedger(P2A_A2_MOCK_FIXTURES);
  const result = evaluateP2AA3Proceed(logs);

  return (
    <section style={panelStyle} aria-label="p2a-readiness-panel">
      <h3 style={{ marginTop: 0 }}>FB-P2A A3 readiness</h3>
      <p>
        Proceed: <strong>{result.go ? "go" : "no-go"}</strong>
      </p>
      <p>Reason: {result.reason}</p>
      <ul>
        {logs.map((log) => (
          <li key={log.mockCaseId}>
            {log.mockCaseId}: {log.validationResult} ({log.ownerOfFix})
          </li>
        ))}
      </ul>
    </section>
  );
}
