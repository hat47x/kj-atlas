import { Component, Suspense, useRef, type ReactNode } from "react";
import { t } from "../i18n/translate";

// UX-PERF-01: shared loading/retry wrapper for the React.lazy()-loaded
// advanced-feature panels (SharePanel, PatchWorkspacePanel,
// InquiryJourneyPrototypePanel, RepresentativeVisualCuePrototypePanel,
// AgentResponseImportPanel, DiagnosticsBundlePanel -- see App.tsx). None of
// these are needed for the initial card-creation/editing workflow, so their
// module code is split out of the main chunk and fetched on first render.
//
// Suspense alone has no recovery path if the dynamic import() rejects (e.g.
// a flaky/slow network -- the exact scenario this split targets). This file
// adds a small ErrorBoundary so a failed chunk load offers a retry instead
// of leaving the panel stuck. Kept intentionally minimal: one boundary, one
// fallback, reused at each of the six call sites -- not a generic abstraction.
//
// Two-stage retry, confirmed empirically (real Chromium, both `vite dev` and
// a production `vite preview` build -- see the issue's checkpoint notes):
// a browser's module registry permanently caches a *rejected* dynamic
// import() per resolved URL. Resetting this boundary's state and letting
// Suspense call the SAME lazy(() => import("./ui/X")) factory again does
// re-render the tree, but if the chunk request itself failed, the browser
// re-rejects from its cache WITHOUT ever issuing a new network request --
// confirmed by watching request counts while a Playwright `page.route()`
// abort was lifted before clicking Retry. So a first click is a cheap,
// harmless in-place retry (it *does* help if the failure was a one-off
// render error in an already-loaded module), but if the SAME boundary
// catches again right after, only a full reload starts a fresh module
// registry and gets a genuinely new fetch attempt -- confirmed via
// window.confirm() first, since this reload is not scoped to just this
// panel and would also discard unsaved work elsewhere in the document.
type LazyPanelErrorBoundaryState = {
  hasError: boolean;
  attempt: number;
};

// Exported only so LazyPanelBoundary.test.ts can exercise the retry logic
// directly: react-dom/server's legacy renderToStaticMarkup (no jsdom in this
// project's vitest environment) does not run error boundaries the way a
// browser does -- with no Suspense ancestor a thrown render error propagates
// out of renderToStaticMarkup uncaught, and with one it gets silently treated
// as a suspend (the Suspense fallback renders, the boundary never sees it).
// The real behavior this class exists for is verified in the browser instead
// (see the issue's checkpoint notes for the manual broken-import/retry check).
export class LazyPanelErrorBoundary extends Component<{ children?: ReactNode }, LazyPanelErrorBoundaryState> {
  override state: LazyPanelErrorBoundaryState = { hasError: false, attempt: 0 };

  static getDerivedStateFromError(): Pick<LazyPanelErrorBoundaryState, "hasError"> {
    return { hasError: true };
  }

  private handleRetry = (): void => {
    if (this.state.attempt === 0) {
      this.setState({ hasError: false, attempt: 1 });
      return;
    }
    if (window.confirm(t("app.lazy_panel.reload_confirm"))) {
      window.location.reload();
    }
  };

  override render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }
    const isReloadStage = this.state.attempt > 0;
    return (
      <div
        role="alert"
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: 8,
          fontSize: 12,
          color: "#991b1b",
        }}
      >
        <span>{t(isReloadStage ? "app.lazy_panel.load_failed_retry" : "app.lazy_panel.load_failed")}</span>
        <button
          type="button"
          onClick={this.handleRetry}
          style={{
            border: "1px solid #991b1b",
            borderRadius: 6,
            padding: "2px 10px",
            background: "#ffffff",
            color: "#991b1b",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          {t(isReloadStage ? "app.error_boundary.reload" : "app.lazy_panel.retry")}
        </button>
      </div>
    );
  }
}

// Deliberately not focusable and not aria-live="assertive": this must never
// steal keyboard focus away from whatever the user was doing when a panel's
// chunk started loading (e.g. the trigger button that just fired the async
// mount) -- see AGENTS.md focus-preservation expectations for panel opens.
export function LazyPanelFallback() {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: 8,
        fontSize: 12,
        color: "#475569",
      }}
    >
      {t("app.lazy_panel.loading")}
    </div>
  );
}

export function LazyPanelBoundary({ children }: { children?: ReactNode }) {
  return (
    <LazyPanelErrorBoundary>
      <Suspense fallback={<LazyPanelFallback />}>{children}</Suspense>
    </LazyPanelErrorBoundary>
  );
}

// Some advanced-feature overlays (AgentResponseImportPanel,
// DiagnosticsBundlePanel) are rendered unconditionally in App.tsx and only
// return null internally while `isOpen` is false. Simply wrapping those in
// LazyPanelBoundary would trigger their dynamic import() -- and flash the
// loading fallback -- on every initial page load, before the user ever asks
// to open them. This hook lets the call site defer even mounting the
// Suspense/lazy boundary until the panel is opened for the first time, and
// then keep it mounted (matching today's always-mounted-after-first-render
// behavior, so in-panel local state such as DiagnosticsBundlePanel's
// classification/HTTP-status fields keeps surviving a close/reopen cycle).
export function useMountOnceOpened(isOpen: boolean): boolean {
  const everOpenedRef = useRef(false);
  if (isOpen) {
    everOpenedRef.current = true;
  }
  return everOpenedRef.current;
}
