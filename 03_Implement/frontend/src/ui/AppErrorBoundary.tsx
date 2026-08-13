import { Component, type ErrorInfo, type ReactNode } from "react";
import { t } from "../i18n/translate";
import { buildTenantStorageKey, type TenantBrowserStorageScope } from "../storage/tenant_scope";

// UI-RESILIENCE-01: React error boundary with emergency state eviction.
// The app has no autosave and keeps the in-progress document in App's
// history state; an uncaught render error unmounts the whole tree and loses
// it. This boundary preserves the current document to localStorage before the
// tree goes down, and offers reload / recover.
//
// SAAS-TENANT-01 AC-8: the key must carry the same tenant/principal scope as
// every other storage helper (see storage/agent_task_ledger.ts). Without it,
// a document evicted during Tenant A's session would be offered for recovery
// to Tenant B after an active-tenant switch on the same browser profile.

const EVICTED_DOC_KEY = "kj-atlas/evicted-doc";

function key(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(EVICTED_DOC_KEY, scope) : EVICTED_DOC_KEY;
}

export function loadEvictedDocument(scope?: TenantBrowserStorageScope): unknown | null {
  try {
    const raw = window.localStorage.getItem(key(scope));
    return raw ? (JSON.parse(raw) as unknown) : null;
  } catch {
    return null;
  }
}

export function clearEvictedDocument(scope?: TenantBrowserStorageScope): void {
  try {
    window.localStorage.removeItem(key(scope));
  } catch {
    // storage unavailable — nothing to clear
  }
}

export type AppErrorBoundaryProps = {
  /** Returns the in-progress document (App's history.present) to preserve. */
  getRecoverySnapshot: () => unknown | null;
  /** Called with the recovered document when the user chooses to recover. */
  onRecover: (doc: unknown) => void;
  /** Same tenant/principal scope as the rest of this App instance's storage. */
  storageScope?: TenantBrowserStorageScope;
  children?: ReactNode;
};

type AppErrorBoundaryState = {
  hasError: boolean;
  message: string | null;
};

export class AppErrorBoundary extends Component<AppErrorBoundaryProps, AppErrorBoundaryState> {
  override state: AppErrorBoundaryState = { hasError: false, message: null };

  static getDerivedStateFromError(error: unknown): Partial<AppErrorBoundaryState> {
    return { hasError: true, message: error instanceof Error ? error.message : String(error) };
  }

  override componentDidCatch(_error: Error, _info: ErrorInfo): void {
    // Preserve the in-progress document before the tree unmounts (no autosave).
    try {
      const snapshot = this.props.getRecoverySnapshot();
      if (snapshot != null) {
        window.localStorage.setItem(key(this.props.storageScope), JSON.stringify(snapshot));
      }
    } catch {
      // storage full/unavailable — fall through to the reload fallback
    }
  }

  private handleReload = (): void => {
    window.location.reload();
  };

  private handleRecover = (): void => {
    const doc = loadEvictedDocument(this.props.storageScope);
    if (doc != null) {
      this.props.onRecover(doc);
    }
    clearEvictedDocument(this.props.storageScope);
    this.setState({ hasError: false, message: null });
  };

  override render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }
    return (
      <div
        role="alert"
        style={{ display: "flex", flexDirection: "column", gap: "12px", maxWidth: "640px", margin: "48px auto", padding: "24px" }}
      >
        <h1 style={{ fontSize: "18px", fontWeight: 700, margin: 0 }}>{t("app.error_boundary.title")}</h1>
        <p style={{ margin: 0 }}>{t("app.error_boundary.message")}</p>
        <p style={{ margin: 0, fontSize: "12px", color: "#666" }}>{this.state.message}</p>
        <div style={{ display: "flex", gap: "8px" }}>
          <button onClick={this.handleRecover}>{t("app.error_boundary.recover")}</button>
          <button onClick={this.handleReload}>{t("app.error_boundary.reload")}</button>
        </div>
      </div>
    );
  }
}
