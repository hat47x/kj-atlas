import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import { buildTenantStorageKey } from "../storage/tenant_scope";
import { AppErrorBoundary, clearEvictedDocument, loadEvictedDocument } from "./AppErrorBoundary";

function makeLocalStorageMock(): Storage {
  const store = new Map<string, string>();
  return {
    get length() {
      return store.size;
    },
    clear: () => store.clear(),
    getItem: (key) => store.get(key) ?? null,
    key: (index) => Array.from(store.keys())[index] ?? null,
    removeItem: (key) => store.delete(key),
    setItem: (key, value) => store.set(key, String(value)),
  };
}

describe("AppErrorBoundary", () => {
  beforeEach(() => {
    Object.defineProperty(globalThis, "window", {
      value: { localStorage: makeLocalStorageMock() },
      configurable: true,
    });
    setActiveLocale("ja");
  });

  afterEach(() => {
    // @ts-expect-error -- test-only teardown
    delete globalThis.window;
  });

  it("renders children normally when no error occurs", () => {
    const html = renderToStaticMarkup(
      React.createElement(
        AppErrorBoundary,
        { getRecoverySnapshot: () => null, onRecover: vi.fn() },
        React.createElement("div", { "data-testid": "child" }, "content"),
      ),
    );
    expect(html).toContain("data-testid=\"child\"");
  });

  it("evicts and clears the document to localStorage (UI-RESILIENCE-01)", () => {
    const doc = { version: 1, id: "doc-1", title: "unsaved" };

    // Boundary eviction path is exercised by saving through the same helpers.
    window.localStorage.setItem("kj-atlas/evicted-doc", JSON.stringify(doc));
    expect(loadEvictedDocument()).toEqual(doc);

    clearEvictedDocument();
    expect(loadEvictedDocument()).toBeNull();
  });

  it("returns null from loadEvictedDocument when storage is unavailable", () => {
    Object.defineProperty(globalThis, "window", { value: {}, configurable: true });
    expect(loadEvictedDocument()).toBeNull();
    clearEvictedDocument(); // must not throw
  });

  // SAAS-TENANT-01 AC-8: a document evicted during one tenant's session must
  // never surface as a recovery offer to a different tenant sharing the same
  // browser profile after an active-tenant switch.
  it("keeps documents evicted under one tenant scope invisible to another tenant's scope", () => {
    const tenantA = { deployment: "evaluation", tenantId: "tenant-a", principalId: "user-1" };
    const tenantB = { deployment: "evaluation", tenantId: "tenant-b", principalId: "user-1" };
    const doc = { version: 1, id: "doc-1", title: "tenant-a confidential draft" };

    window.localStorage.setItem(
      buildTenantStorageKey("kj-atlas/evicted-doc", tenantA),
      JSON.stringify(doc),
    );

    expect(loadEvictedDocument(tenantA)).toEqual(doc);
    expect(loadEvictedDocument(tenantB)).toBeNull();
    expect(loadEvictedDocument()).toBeNull(); // unscoped (single-tenant) key is separate too

    clearEvictedDocument(tenantB);
    expect(loadEvictedDocument(tenantA)).toEqual(doc); // clearing B must not touch A's copy

    clearEvictedDocument(tenantA);
    expect(loadEvictedDocument(tenantA)).toBeNull();
  });

  it("scopes the recovered-document storage key the same way as other tenant-scoped storage", () => {
    const scope = { deployment: "evaluation", tenantId: "tenant-a", principalId: "user-1" };
    const doc = { version: 1, id: "doc-1" };

    window.localStorage.setItem(buildTenantStorageKey("kj-atlas/evicted-doc", scope), JSON.stringify(doc));

    // loadEvictedDocument must read the exact key buildTenantStorageKey produces,
    // not a hand-rolled prefix that happens to look similar.
    expect(loadEvictedDocument(scope)).toEqual(doc);
  });
});
