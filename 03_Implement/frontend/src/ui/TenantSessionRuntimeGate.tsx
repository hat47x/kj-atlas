import { useEffect, useState, type ReactNode } from "react";

import type { TenantSessionBootstrapResult, TenantSessionContextLoader } from "../session/session_bootstrap";
import {
  verifyTenantSessionRuntimePolicy,
  type TenantSessionBootstrapPolicyLoader,
} from "../session/runtime_activation";
import {
  TenantSessionBlockedView,
  TenantSessionBootstrapGate,
  TenantSessionLoadingView,
} from "./TenantSessionBootstrapGate";

type TenantSessionRuntimeGateProps = Readonly<{
  deployment: string;
  loadPolicy?: TenantSessionBootstrapPolicyLoader;
  loadSessionContext?: TenantSessionContextLoader;
  renderApp: (
    result: Extract<TenantSessionBootstrapResult, { status: "ready" }>,
  ) => ReactNode;
}>;

export function TenantSessionRuntimeGate({
  deployment,
  loadPolicy,
  loadSessionContext,
  renderApp,
}: TenantSessionRuntimeGateProps) {
  const [attempt, setAttempt] = useState(0);
  const [policyVerified, setPolicyVerified] = useState<boolean | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setPolicyVerified(null);
    void verifyTenantSessionRuntimePolicy({
      signal: controller.signal,
      loadPolicy,
    }).then((verified) => {
      if (!controller.signal.aborted) {
        setPolicyVerified(verified);
      }
    }).catch(() => {
      if (!controller.signal.aborted) {
        setPolicyVerified(false);
      }
    });
    return () => controller.abort();
  }, [attempt, loadPolicy]);

  if (policyVerified === null) {
    return <TenantSessionLoadingView />;
  }
  if (!policyVerified) {
    return (
      <TenantSessionBlockedView
        reason="session_unavailable"
        onRetry={() => setAttempt((current) => current + 1)}
      />
    );
  }
  return (
    <TenantSessionBootstrapGate
      deployment={deployment}
      loadSessionContext={loadSessionContext}
      renderApp={renderApp}
    />
  );
}
