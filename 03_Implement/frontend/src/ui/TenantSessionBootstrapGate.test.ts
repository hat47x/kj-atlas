import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import {
  redirectToTenantSessionLogin,
  TenantSessionBlockedView,
  TenantSessionBootstrapGate,
  TenantSessionLoadingView,
} from "./TenantSessionBootstrapGate";

describe("tenant session bootstrap views", () => {
  afterEach(() => setActiveLocale("ja"));

  it("renders a neutral loading state without mounting tenant content", () => {
    const renderApp = vi.fn();
    const html = renderToStaticMarkup(React.createElement(
      TenantSessionBootstrapGate,
      {
        deployment: "https://atlas.example.test",
        loadSessionContext: async () => new Promise(() => undefined),
        renderApp,
      },
    ));

    expect(html).toContain('role="status"');
    expect(html).toContain('aria-busy="true"');
    expect(html).toContain("利用環境を確認しています");
    expect(renderApp).not.toHaveBeenCalled();
  });

  it("renders every failure as an accessible blocked state", () => {
    for (const reason of [
      "authentication_required",
      "access_denied",
      "session_unavailable",
      "invalid_session_response",
      "invalid_deployment",
    ] as const) {
      const html = renderToStaticMarkup(React.createElement(
        TenantSessionBlockedView,
        { reason, onRetry: () => undefined },
      ));

      expect(html).toContain('role="alert"');
      expect(html).toContain("アクセスを確認できません");
      expect(html).toContain("<button");
      if (reason === "authentication_required") {
        expect(html).toContain("ログイン");
      } else {
        expect(html).toContain("再試行");
      }
      expect(html).not.toContain("user-1");
      expect(html).not.toContain("tenant-a");
    }
  });

  it("starts SaaS authentication through the same-origin BFF endpoint", () => {
    const assign = vi.fn();

    redirectToTenantSessionLogin({ assign } as Pick<Location, "assign">);

    expect(assign).toHaveBeenCalledOnce();
    expect(assign).toHaveBeenCalledWith("/session/login");
  });

  it("keeps the pre-App state available in English", () => {
    setActiveLocale("en");
    const loadingHtml = renderToStaticMarkup(
      React.createElement(TenantSessionLoadingView),
    );
    const blockedHtml = renderToStaticMarkup(React.createElement(
      TenantSessionBlockedView,
      { reason: "session_unavailable", onRetry: () => undefined },
    ));

    expect(loadingHtml).toContain("Checking your access");
    expect(blockedHtml).toContain("We couldn’t verify access");
    expect(blockedHtml).toContain("Retry");
  });
});
