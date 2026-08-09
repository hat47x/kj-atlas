import {
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { t } from "../i18n/translate";
import { redirectToBrokerLogin } from "../session/oauth_login";
import {
  bootstrapTenantSession,
  type TenantSessionBlockReason,
  type TenantSessionBootstrapResult,
  type TenantSessionContextLoader,
} from "../session/session_bootstrap";

type TenantSessionBootstrapGateProps = Readonly<{
  deployment: string;
  loadSessionContext?: TenantSessionContextLoader;
  renderApp: (
    result: Extract<TenantSessionBootstrapResult, { status: "ready" }>,
  ) => ReactNode;
}>;

const pageStyle = {
  minHeight: "100%",
  boxSizing: "border-box",
  display: "grid",
  placeItems: "center",
  padding: 24,
  background: "#f8fafc",
  color: "#0f172a",
  fontFamily: "system-ui, sans-serif",
} as const;

const panelStyle = {
  width: "min(100%, 480px)",
  boxSizing: "border-box",
  display: "grid",
  gap: 14,
  padding: 24,
  border: "1px solid #cbd5e1",
  borderRadius: 12,
  background: "#ffffff",
  boxShadow: "0 8px 24px rgba(15, 23, 42, 0.08)",
} as const;

export function TenantSessionLoadingView() {
  return (
    <main style={pageStyle} aria-busy="true">
      <div style={panelStyle} role="status" aria-live="polite">
        {t("tenant_session.bootstrap.loading")}
      </div>
    </main>
  );
}

export function TenantSessionBlockedView({
  reason,
  onRetry,
}: Readonly<{
  reason: TenantSessionBlockReason;
  onRetry: () => void;
}>) {
  const headingRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    headingRef.current?.focus();
  }, [reason]);

  return (
    <main style={pageStyle}>
      <section style={panelStyle} role="alert" aria-labelledby="tenant-session-blocked-title">
        <h1
          id="tenant-session-blocked-title"
          ref={headingRef}
          tabIndex={-1}
          style={{ margin: 0, fontSize: 22 }}
        >
          {t("tenant_session.bootstrap.blocked.title")}
        </h1>
        <p style={{ margin: 0, lineHeight: 1.6 }}>
          {t(`tenant_session.bootstrap.blocked.${reason}`)}
        </p>
        {reason === "authentication_required" ? (
          <button
            type="button"
            onClick={() => { void redirectToBrokerLogin(); }}
            style={{
              justifySelf: "start",
              border: "1px solid #2563eb",
              borderRadius: 8,
              padding: "8px 14px",
              background: "#2563eb",
              color: "#ffffff",
              cursor: "pointer",
            }}
          >
            {t("tenant_session.bootstrap.login") || "Sign in"}
          </button>
        ) : (
          <button
            type="button"
            onClick={onRetry}
            style={{
              justifySelf: "start",
              border: "1px solid #334155",
              borderRadius: 8,
              padding: "8px 14px",
              background: "#ffffff",
              color: "#0f172a",
              cursor: "pointer",
            }}
          >
            {t("tenant_session.bootstrap.retry")}
          </button>
        )}
      </section>
    </main>
  );
}

export function TenantSessionBootstrapGate({
  deployment,
  loadSessionContext,
  renderApp,
}: TenantSessionBootstrapGateProps) {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<TenantSessionBootstrapResult | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setState(null);
    void bootstrapTenantSession({
      deployment,
      signal: controller.signal,
      loadSessionContext,
    }).then((result) => {
      if (!controller.signal.aborted) {
        setState(result);
      }
    }).catch(() => {
      if (!controller.signal.aborted) {
        setState({ status: "blocked", reason: "session_unavailable" });
      }
    });
    return () => controller.abort();
  }, [attempt, deployment, loadSessionContext]);

  if (!state) {
    return <TenantSessionLoadingView />;
  }
  if (state.status === "blocked") {
    return (
      <TenantSessionBlockedView
        reason={state.reason}
        onRetry={() => setAttempt((current) => current + 1)}
      />
    );
  }
  return <>{renderApp(state)}</>;
}
