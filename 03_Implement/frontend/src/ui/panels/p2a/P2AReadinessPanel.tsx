import React from "react";
import { P2A_A2_MOCK_FIXTURES } from "../../../domain/p2a/mock_fixtures";
import {
  buildP2AImplementationReadiness,
  evaluateP2AA3Proceed,
  toP2AValidationLedger,
} from "../../../domain/p2a/validation";
import { P2A02_CONTRACT_ID, P2A02_CONTRACT_VERSION } from "../../../domain/p2a/contract";
import { t } from "../../../i18n/translate";

const panelStyle: React.CSSProperties = {
  border: "1px solid #d0d7de",
  borderRadius: 8,
  padding: 12,
  background: "#f8fafc",
};

function proceedLabel(go: boolean): string {
  return go ? t("p2a.readiness.proceed.go") : t("p2a.readiness.proceed.no_go");
}

function reasonLabel(reason: string): string {
  if (reason === "go") return t("p2a.readiness.reason.go");
  return reason;
}

function validationResultLabel(result: "pass" | "fail"): string {
  return result === "pass" ? t("p2a.readiness.validation.pass") : t("p2a.readiness.validation.fail");
}

export function P2AReadinessPanel(): React.ReactElement {
  const logs = toP2AValidationLedger(P2A_A2_MOCK_FIXTURES);
  const result = evaluateP2AA3Proceed(logs);
  const readiness = buildP2AImplementationReadiness(logs);

  return (
    <section
      style={panelStyle}
      aria-label={t("p2a.readiness.aria_label")}
      data-ui-region="stream-b-p2a-readiness"
      data-contract-id={P2A02_CONTRACT_ID}
      data-contract-version={P2A02_CONTRACT_VERSION}
    >
      <h3 style={{ marginTop: 0 }}>{t("p2a.readiness.title")}</h3>
      <p role="status" aria-live="polite" data-testid="p2a-proceed-status">
        {t("p2a.readiness.proceed")}: <strong>{proceedLabel(result.go)}</strong>
      </p>
      <p>{t("p2a.readiness.reason")}: {reasonLabel(result.reason)}</p>
      <p>
        {t("p2a.readiness.contract")}: <code>{P2A02_CONTRACT_ID}</code> / <code>{P2A02_CONTRACT_VERSION}</code>
      </p>
      <p>
        {t("p2a.readiness.accepted")}: {readiness.acceptedMockCases.join(", ") || "-"} / {t("p2a.readiness.blocked")}: {readiness.blockedMockCases.join(", ")}
      </p>
      <ul aria-label={t("p2a.readiness.validation_log_aria")} data-testid="p2a-validation-log">
        {logs.map((log) => (
          <li key={log.mockCaseId}>
            {log.mockCaseId}: {validationResultLabel(log.validationResult)} ({log.ownerOfFix})
          </li>
        ))}
      </ul>
    </section>
  );
}
