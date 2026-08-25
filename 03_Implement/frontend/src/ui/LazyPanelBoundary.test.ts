import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import {
  LazyPanelBoundary,
  LazyPanelErrorBoundary,
  LazyPanelFallback,
  useMountOnceOpened,
} from "./LazyPanelBoundary";

// Note on why the retry logic below is tested by instantiating
// LazyPanelErrorBoundary directly instead of rendering a throwing child
// through LazyPanelBoundary: this project's vitest setup has no jsdom (see
// vite.config.ts -- test.environment is "node"), so class-component tests
// here use react-dom/server's renderToStaticMarkup (see AppErrorBoundary's
// own test file for the existing precedent). That legacy synchronous SSR
// renderer does not run error boundaries the way a browser does -- verified
// empirically: with no Suspense ancestor a thrown render error propagates
// out of renderToStaticMarkup uncaught, and with one (as LazyPanelBoundary
// always has) it is silently treated as a suspend, so the Suspense fallback
// renders and the boundary's getDerivedStateFromError never runs. The real
// catch-and-retry behavior is exercised in the browser instead (see the
// issue's checkpoint notes for the manual broken-import/retry verification).

describe("LazyPanelBoundary", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  it("renders children normally when no error occurs", () => {
    const html = renderToStaticMarkup(
      React.createElement(
        LazyPanelBoundary,
        null,
        React.createElement("div", { "data-testid": "child" }, "content"),
      ),
    );
    expect(html).toContain('data-testid="child"');
  });
});

describe("LazyPanelFallback", () => {
  it("is a visible, non-focus-stealing loading indicator (aria-busy, no tabIndex/autofocus)", () => {
    const html = renderToStaticMarkup(React.createElement(LazyPanelFallback));
    expect(html).toContain('role="status"');
    expect(html).toContain('aria-live="polite"');
    expect(html).toContain('aria-busy="true"');
    expect(html.toLowerCase()).not.toContain("tabindex");
    expect(html.toLowerCase()).not.toContain("autofocus");
  });
});

describe("LazyPanelErrorBoundary", () => {
  // This project's vitest environment is "node" (see vite.config.ts) --
  // `window` does not exist by default, so the retry tests below (which
  // exercise window.confirm/window.location.reload) need a minimal stand-in.
  beforeEach(() => {
    setActiveLocale("ja");
    Object.defineProperty(globalThis, "window", {
      value: { confirm: vi.fn(), location: { reload: vi.fn() } },
      configurable: true,
    });
  });

  afterEach(() => {
    // @ts-expect-error -- test-only teardown
    delete globalThis.window;
  });

  it("getDerivedStateFromError flags hasError regardless of the thrown value", () => {
    expect(LazyPanelErrorBoundary.getDerivedStateFromError()).toEqual({ hasError: true });
  });

  it("passes children through unchanged while hasError is false", () => {
    const instance = new LazyPanelErrorBoundary({ children: "ok" });
    expect(instance.render()).toBe("ok");
  });

  it("renders a first-stage retry affordance once hasError is true", () => {
    const instance = new LazyPanelErrorBoundary({ children: "ok" });
    instance.state = { hasError: true, attempt: 0 };
    const html = renderToStaticMarkup(instance.render() as React.ReactElement);
    expect(html).toContain('role="alert"');
    expect(html).toContain("<button");
    expect(html).toContain("再試行");
  });

  it("renders a reload affordance once a retry attempt has already been made", () => {
    const instance = new LazyPanelErrorBoundary({ children: "ok" });
    instance.state = { hasError: true, attempt: 1 };
    const html = renderToStaticMarkup(instance.render() as React.ReactElement);
    expect(html).toContain('role="alert"');
    expect(html).toContain("再読み込み");
    expect(html).not.toContain("再試行");
  });

  // A browser's module registry permanently caches a *rejected* dynamic
  // import() per URL (confirmed empirically against both `vite dev` and a
  // production `vite preview` build -- see the issue's checkpoint notes):
  // resetting this boundary and letting Suspense call the same lazy(() =>
  // import(...)) factory again re-renders, but if the chunk request itself
  // failed, the browser re-rejects from cache without a new network
  // attempt. So only the FIRST retry is a cheap in-place state reset; a
  // second consecutive failure needs a full reload instead.
  it("first retry (attempt 0) just resets state in place, no reload", () => {
    const instance = new LazyPanelErrorBoundary({ children: "ok" });
    const setStateSpy = vi.fn();
    instance.setState = setStateSpy;

    (instance as unknown as { handleRetry: () => void }).handleRetry();

    expect(setStateSpy).toHaveBeenCalledWith({ hasError: false, attempt: 1 });
    expect(window.location.reload).not.toHaveBeenCalled();
  });

  it("a second consecutive failure (attempt 1) confirms then reloads the page", () => {
    const instance = new LazyPanelErrorBoundary({ children: "ok" });
    instance.state = { hasError: true, attempt: 1 };
    const setStateSpy = vi.fn();
    instance.setState = setStateSpy;
    vi.mocked(window.confirm).mockReturnValue(true);

    (instance as unknown as { handleRetry: () => void }).handleRetry();

    expect(window.confirm).toHaveBeenCalledTimes(1);
    expect(window.location.reload).toHaveBeenCalledTimes(1);
    expect(setStateSpy).not.toHaveBeenCalled();
  });

  it("a second consecutive failure does NOT reload if the user cancels the confirmation", () => {
    const instance = new LazyPanelErrorBoundary({ children: "ok" });
    instance.state = { hasError: true, attempt: 1 };
    vi.mocked(window.confirm).mockReturnValue(false);

    (instance as unknown as { handleRetry: () => void }).handleRetry();

    expect(window.location.reload).not.toHaveBeenCalled();
  });
});

describe("useMountOnceOpened", () => {
  function Probe({ isOpen }: { isOpen: boolean }) {
    const mounted = useMountOnceOpened(isOpen);
    return React.createElement("span", { "data-mounted": String(mounted) });
  }

  it("reflects false when a component first renders with isOpen=false", () => {
    const html = renderToStaticMarkup(React.createElement(Probe, { isOpen: false }));
    expect(html).toContain('data-mounted="false"');
  });

  it("reflects true when a component first renders with isOpen=true", () => {
    const html = renderToStaticMarkup(React.createElement(Probe, { isOpen: true }));
    expect(html).toContain('data-mounted="true"');
  });
});
