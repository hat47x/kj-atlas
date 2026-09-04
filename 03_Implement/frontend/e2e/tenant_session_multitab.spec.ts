import {
  expect,
  test,
  type BrowserContext,
  type Page,
  type Route,
} from "@playwright/test";
import JSZip from "jszip";
import { openAdvancedWorkMode, selectWorkModeTab } from "./helpers/i18n";

const TENANT_SESSION_HEADER = "kj-atlas-tenant-session-version";
const START_PANEL = '[data-panel="start-document-entry"]';

type TenantId = "tenant-a" | "tenant-b";

type ServerState = {
  activeTenantId: TenantId;
  tenantSessionVersion: string;
  staleRequestCount: number;
  documentLookupCount: number;
  acceptedMutationCount: number;
  documents: Record<TenantId, ReturnType<typeof buildDocument>>;
};

function buildDocument(tenantId: TenantId) {
  const now = "2026-08-02T00:00:00.000Z";
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: `${tenantId} fixture`,
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "shared-card",
        text: `${tenantId} confidential card`,
        textReviewed: true,
        x: 120,
        y: 120,
      },
    ],
    edges: [],
    islands: [],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

function createServerState(): ServerState {
  return {
    activeTenantId: "tenant-a",
    tenantSessionVersion: "session-v1",
    staleRequestCount: 0,
    documentLookupCount: 0,
    acceptedMutationCount: 0,
    documents: {
      "tenant-a": buildDocument("tenant-a"),
      "tenant-b": buildDocument("tenant-b"),
    },
  };
}

function sessionContext(state: ServerState) {
  const activeTenant = state.activeTenantId === "tenant-a"
    ? { id: "tenant-a", displayName: "Tenant A" }
    : { id: "tenant-b", displayName: "Tenant B" };
  return {
    principalId: "principal-1",
    activeTenant,
    availableTenants: [
      { id: "tenant-a", displayName: "Tenant A" },
      { id: "tenant-b", displayName: "Tenant B" },
    ],
    effectiveCapabilities: [
      "document.read",
      "document.write",
      "document.export",
    ],
    capabilityVersion: `capability-${state.activeTenantId}`,
    tenantSessionVersion: state.tenantSessionVersion,
  };
}

async function fulfillJson(route: Route, status: number, body: unknown, headers: Record<string, string> = {}) {
  await route.fulfill({
    status,
    contentType: "application/json",
    headers,
    body: JSON.stringify(body),
  });
}

async function installSaasServer(context: BrowserContext, state: ServerState) {
  // Public packs are served from the static /packs surface rather than /api.
  // Keep the SaaS fixture deterministic so the tenant-scoped document remains
  // the only startup document under test.
  await context.route("**/packs/index.json", async (route) => {
    await fulfillJson(route, 404, {});
  });

  await context.route(/^https?:\/\/[^/]+\/api\//, async (route) => {
    const request = route.request();
    const url = new URL(request.url());

    if (url.pathname === "/api/session/bootstrap-policy") {
      await fulfillJson(route, 200, { tenantSessionMode: "tenant-session-required" });
      return;
    }
    if (url.pathname === "/api/session/context") {
      await fulfillJson(route, 200, sessionContext(state));
      return;
    }
    if (url.pathname === "/api/session/active-tenant") {
      const payload = request.postDataJSON() as {
        tenantId?: string;
        expectedTenantSessionVersion?: string;
      };
      if (payload.expectedTenantSessionVersion !== state.tenantSessionVersion) {
        state.staleRequestCount += 1;
        await fulfillJson(route, 409, {
          detail: {
            code: "tenant_session_changed",
            message: "Session context changed",
          },
        });
        return;
      }
      if (payload.tenantId !== "tenant-a" && payload.tenantId !== "tenant-b") {
        await fulfillJson(route, 404, { detail: { code: "tenant_not_available" } });
        return;
      }
      state.activeTenantId = payload.tenantId;
      state.tenantSessionVersion = state.tenantSessionVersion === "session-v1"
        ? "session-v2"
        : "session-v3";
      await fulfillJson(route, 200, sessionContext(state), {
        "Cache-Control": "no-store",
      });
      return;
    }
    if (url.pathname === "/api/packs/index.json") {
      await fulfillJson(route, 404, {});
      return;
    }
    if (url.pathname === "/api/ai/provider-status") {
      await fulfillJson(route, 200, { providerKind: "none" });
      return;
    }
    if (url.pathname === "/api/docs/doc_phase1_canvas") {
      const expectedVersion = request.headers()[TENANT_SESSION_HEADER];
      if (expectedVersion !== state.tenantSessionVersion) {
        state.staleRequestCount += 1;
        await fulfillJson(route, 409, {
          detail: {
            code: "tenant_session_changed",
            message: "Session context changed",
          },
        });
        return;
      }

      state.documentLookupCount += 1;
      if (request.method() === "PUT") {
        state.acceptedMutationCount += 1;
        state.documents[state.activeTenantId] = request.postDataJSON() as ReturnType<typeof buildDocument>;
      }
      await fulfillJson(route, 200, state.documents[state.activeTenantId], {
        ETag: `"${state.activeTenantId}-revision"`,
      });
      return;
    }

    await fulfillJson(route, 404, { detail: { code: "not_found" } });
  });
}

async function openWorkspace(page: Page, locale: "en" | "ja" = "en") {
  await page.goto(`/?locale=${locale}`);
  await expect(page.locator(START_PANEL)).toBeVisible();
  await page.locator(START_PANEL).getByRole("button", {
    name: locale === "en" ? "Close start panel" : "開始パネルを閉じる",
  }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();
}

async function openSharePanel(page: Page) {
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  await expect(page.getByRole("dialog", { name: "Share & Reproduce" })).toBeVisible();
}

async function installControllableBundleZipWorker(context: BrowserContext) {
  await context.addInitScript(() => {
    const NativeWorker = window.Worker;

    class ControllableBundleZipWorker extends EventTarget {
      private requestId: string | null = null;

      constructor(scriptUrl: string | URL, options?: WorkerOptions) {
        super();
        if (!String(scriptUrl).includes("bundle_zip.worker")) {
          return new NativeWorker(scriptUrl, options) as unknown as ControllableBundleZipWorker;
        }
      }

      postMessage(message: unknown) {
        if (!message || typeof message !== "object") {
          return;
        }

        const payload = message as { type?: string; requestId?: string };
        if (payload.type === "bundle.zip.request" && payload.requestId) {
          this.requestId = payload.requestId;
          Object.defineProperty(window, "__kjTenantBundleZipStarted", {
            configurable: true,
            value: true,
          });
          return;
        }
        if (payload.type === "bundle.zip.cancel" && payload.requestId === this.requestId) {
          Object.defineProperty(window, "__kjTenantBundleZipCancelled", {
            configurable: true,
            value: true,
          });
          this.dispatchEvent(new MessageEvent("message", {
            data: {
              type: "bundle.zip.cancelled",
              requestId: payload.requestId,
            },
          }));
        }
      }

      terminate() {
        this.requestId = null;
      }
    }

    window.Worker = ControllableBundleZipWorker as unknown as typeof Worker;
  });
}

async function installControllableReviewPackRead(context: BrowserContext) {
  await context.addInitScript(() => {
    const nativeArrayBuffer = File.prototype.arrayBuffer;
    let releaseRead: (() => void) | null = null;

    File.prototype.arrayBuffer = function arrayBuffer() {
      if (this.name !== "stale-review-pack.zip") {
        return nativeArrayBuffer.call(this);
      }

      Object.defineProperty(window, "__kjTenantPackReadStarted", {
        configurable: true,
        value: true,
      });
      return new Promise<ArrayBuffer>((resolve, reject) => {
        releaseRead = () => {
          nativeArrayBuffer.call(this).then((value) => {
            Object.defineProperty(window, "__kjTenantPackReadFinished", {
              configurable: true,
              value: true,
            });
            resolve(value);
          }, reject);
        };
        Object.defineProperty(window, "__kjReleaseTenantPackRead", {
          configurable: true,
          value: () => releaseRead?.(),
        });
      });
    };
  });
}

test.skip(
  process.env.KJ_ATLAS_E2E_SAAS !== "1",
  "Runs only with playwright.saas.config.ts and the SaaS runtime profile.",
);

test("cross-tab switch blocks the old DOM and discards a delayed tenant result", async ({ browser }) => {
  const state = createServerState();
  const context = await browser.newContext();
  await installSaasServer(context, state);
  const pageA = await context.newPage();
  const pageB = await context.newPage();

  await Promise.all([openWorkspace(pageA), openWorkspace(pageB)]);
  await expect(pageA.getByRole("button", { name: "tenant-a confidential card" })).toBeVisible();

  let releaseDelayedResponse: (() => Promise<void>) | undefined;
  await pageA.route("**/api/docs/doc_phase1_canvas", async (route) => {
    releaseDelayedResponse = async () => {
      await fulfillJson(route, 200, state.documents["tenant-a"], {
        ETag: '"tenant-a-delayed"',
      });
    };
  });
  await pageA.reload({ waitUntil: "domcontentloaded" });
  await expect(pageA.getByLabel("Current workspace: Tenant A")).toBeVisible();
  await expect.poll(() => releaseDelayedResponse).toBeDefined();

  await pageB.getByLabel("Current workspace: Tenant A").selectOption("tenant-b");
  await expect(pageB.getByLabel("Current workspace: Tenant B")).toBeVisible();
  await expect(pageB.getByRole("button", { name: "tenant-b confidential card" })).toBeVisible();

  const blockedHeading = pageA.getByRole("heading", { name: "We couldn’t verify access" });
  await expect(blockedHeading).toBeVisible();
  await expect(blockedHeading).toBeFocused();
  await expect(pageA.getByText("tenant-a confidential card", { exact: true })).toHaveCount(0);

  await releaseDelayedResponse?.();
  await expect(blockedHeading).toBeVisible();
  await expect(pageA.getByText("tenant-a confidential card", { exact: true })).toHaveCount(0);

  await context.close();
});

test("without BroadcastChannel a stale PUT is rejected before document lookup and never retried", async ({ browser }) => {
  const state = createServerState();
  const context = await browser.newContext();
  await context.addInitScript(() => {
    Object.defineProperty(window, "BroadcastChannel", {
      configurable: true,
      value: undefined,
    });
  });
  await installSaasServer(context, state);
  const pageA = await context.newPage();
  const pageB = await context.newPage();

  await Promise.all([openWorkspace(pageA), openWorkspace(pageB)]);
  const lookupsBeforeSwitch = state.documentLookupCount;

  await pageB.getByLabel("Current workspace: Tenant A").selectOption("tenant-b");
  await expect(pageB.getByLabel("Current workspace: Tenant B")).toBeVisible();

  await expect(pageA.getByRole("button", { name: "tenant-a confidential card" })).toBeVisible();
  await pageA.getByRole("button", { name: "New card" }).click();
  const editor = pageA.getByRole("textbox", { name: "Edit card text" });
  await editor.fill("stale tenant-a mutation");
  await editor.press("Enter");
  await pageA.getByRole("button", { name: "Save" }).click();

  await expect(pageA.getByRole("heading", { name: "We couldn’t verify access" })).toBeVisible();
  expect(state.staleRequestCount).toBe(1);
  expect(state.documentLookupCount).toBe(lookupsBeforeSwitch + 1);
  expect(state.acceptedMutationCount).toBe(0);
  expect(JSON.stringify(state.documents["tenant-b"])).not.toContain("stale tenant-a mutation");

  await context.close();
});

test("cross-tab switch cancels an old tenant bundle before it can download", async ({ browser }) => {
  const state = createServerState();
  const context = await browser.newContext();
  await installControllableBundleZipWorker(context);
  await installSaasServer(context, state);
  const pageA = await context.newPage();
  const pageB = await context.newPage();
  let downloadCount = 0;
  pageA.on("download", () => {
    downloadCount += 1;
  });

  await Promise.all([openWorkspace(pageA), openWorkspace(pageB)]);
  await openSharePanel(pageA);
  await pageA.getByRole("button", { name: "Export bundle (.zip)" }).click();
  await expect.poll(() => pageA.evaluate(
    () => Boolean((window as Window & { __kjTenantBundleZipStarted?: boolean }).__kjTenantBundleZipStarted),
  )).toBe(true);

  await pageB.getByLabel("Current workspace: Tenant A").selectOption("tenant-b");
  await expect(pageB.getByLabel("Current workspace: Tenant B")).toBeVisible();

  const blockedHeading = pageA.getByRole("heading", { name: "We couldn’t verify access" });
  await expect(blockedHeading).toBeVisible();
  await expect.poll(() => pageA.evaluate(
    () => Boolean((window as Window & { __kjTenantBundleZipCancelled?: boolean }).__kjTenantBundleZipCancelled),
  )).toBe(true);
  await expect.poll(() => downloadCount).toBe(0);
  await expect(pageA.getByText("tenant-a confidential card", { exact: true })).toHaveCount(0);

  await context.close();
});

test("cross-tab switch discards a review pack that finishes reading for the old tenant", async ({ browser }) => {
  const state = createServerState();
  const context = await browser.newContext();
  await installControllableReviewPackRead(context);
  await installSaasServer(context, state);
  const pageA = await context.newPage();
  const pageB = await context.newPage();
  const reviewPack = new JSZip();
  reviewPack.file("document.json", "{}");
  reviewPack.file("view.json", "{}");
  const reviewPackBuffer = await reviewPack.generateAsync({ type: "nodebuffer" });

  await Promise.all([openWorkspace(pageA), openWorkspace(pageB)]);
  await openSharePanel(pageA);
  await pageA.locator('input[accept*=".zip"]').last().setInputFiles({
    name: "stale-review-pack.zip",
    mimeType: "application/zip",
    buffer: reviewPackBuffer,
  });
  await expect.poll(() => pageA.evaluate(
    () => Boolean((window as Window & { __kjTenantPackReadStarted?: boolean }).__kjTenantPackReadStarted),
  )).toBe(true);
  const lookupsBeforeSwitch = state.documentLookupCount;

  await pageB.getByLabel("Current workspace: Tenant A").selectOption("tenant-b");
  await expect(pageB.getByLabel("Current workspace: Tenant B")).toBeVisible();
  const blockedHeading = pageA.getByRole("heading", { name: "We couldn’t verify access" });
  await expect(blockedHeading).toBeVisible();

  await pageA.evaluate(() => {
    (window as Window & { __kjReleaseTenantPackRead?: () => void }).__kjReleaseTenantPackRead?.();
  });
  await expect.poll(() => pageA.evaluate(
    () => Boolean((window as Window & { __kjTenantPackReadFinished?: boolean }).__kjTenantPackReadFinished),
  )).toBe(true);
  await expect(blockedHeading).toBeVisible();
  await expect(pageA.getByText("tenant-a confidential card", { exact: true })).toHaveCount(0);
  expect(state.documentLookupCount).toBe(lookupsBeforeSwitch + 1);

  await context.close();
});

test("a 390px Japanese bfcache restoration blocks stale content and focuses the recovery state", async ({ browser }) => {
  const state = createServerState();
  const context = await browser.newContext({
    viewport: { width: 390, height: 720 },
  });
  await installSaasServer(context, state);
  const page = await context.newPage();
  await openWorkspace(page, "ja");
  await expect(page.getByRole("button", { name: "tenant-a confidential card" })).toBeVisible();

  await page.evaluate(() => {
    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: true }));
  });

  const blockedHeading = page.getByRole("heading", { name: "アクセスを確認できません" });
  await expect(blockedHeading).toBeVisible();
  await expect(blockedHeading).toBeFocused();
  await expect(page.getByText("tenant-a confidential card", { exact: true })).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

  await context.close();
});

test("cross-tab switch discards a delayed AI narrative proposal for the old tenant", async ({ browser }) => {
  const state = createServerState();
  const context = await browser.newContext();
  await installSaasServer(context, state);
  const pageA = await context.newPage();
  const pageB = await context.newPage();

  await Promise.all([openWorkspace(pageA), openWorkspace(pageB)]);
  await expect(pageA.getByRole("button", { name: "tenant-a confidential card" })).toBeVisible();

  await openAdvancedWorkMode(pageA);
  await selectWorkModeTab(pageA, "narrative");
  await expect(pageA.getByRole("tabpanel", { name: "Narrative" })).toBeVisible();

  let releaseDelayedNarrative: (() => Promise<void>) | undefined;
  await pageA.route("**/api/ai/generate-narrative", async (route) => {
    releaseDelayedNarrative = async () => {
      await fulfillJson(route, 200, {
        text: "tenant-a confidential narrative draft",
        basedOnReadingOrder: [],
      });
    };
  });

  await pageA.getByRole("button", { name: "Generate from Reading Order" }).click();
  await expect.poll(() => releaseDelayedNarrative).toBeDefined();

  await pageB.getByLabel("Current workspace: Tenant A").selectOption("tenant-b");
  await expect(pageB.getByLabel("Current workspace: Tenant B")).toBeVisible();
  await expect(pageB.getByRole("button", { name: "tenant-b confidential card" })).toBeVisible();

  const blockedHeading = pageA.getByRole("heading", { name: "We couldn’t verify access" });
  await expect(blockedHeading).toBeVisible();
  await expect(pageA.getByText("tenant-a confidential narrative draft", { exact: true })).toHaveCount(0);

  await releaseDelayedNarrative?.();
  await expect(blockedHeading).toBeVisible();
  await expect(pageA.getByText("tenant-a confidential narrative draft", { exact: true })).toHaveCount(0);
  await expect(pageB.getByText("tenant-a confidential narrative draft", { exact: true })).toHaveCount(0);

  await context.close();
});

test("authentication required shows sign-in button and retry is unavailable", async ({ browser }) => {
  const context = await browser.newContext();
  await context.route(/^https?:\/\/[^/]+\/api\//, async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname === "/api/session/bootstrap-policy") {
      await fulfillJson(route, 200, { tenantSessionMode: "tenant-session-required" });
      return;
    }
    await fulfillJson(route, 401, {
      detail: { code: "missing_token", message: "Authentication required" },
    });
  });

  const page = await context.newPage();
  await page.goto("/?locale=en");

  const blockedHeading = page.getByRole("heading", { name: "We couldn't verify access" });
  await expect(blockedHeading).toBeVisible();
  await expect(blockedHeading).toBeFocused();

  const signInButton = page.getByRole("button", { name: "Sign in" });
  await expect(signInButton).toBeVisible();

  const retryButton = page.getByRole("button", { name: "Retry" });
  await expect(retryButton).toHaveCount(0);

  await context.close();
});

test("stale session version after tenant switch surfaces 409 and blocks retry", async ({ browser }) => {
  const state = createServerState();
  const context = await browser.newContext();
  await installSaasServer(context, state);
  const page = await context.newPage();

  await openWorkspace(page);
  await expect(page.getByRole("button", { name: "tenant-a confidential card" })).toBeVisible();

  state.tenantSessionVersion = "stale-version";

  await page.getByRole("button", { name: "New card" }).click();
  const editor = page.getByRole("textbox", { name: "Edit card text" });
  await editor.fill("stale mutation after version change");
  await editor.press("Enter");
  await page.getByRole("button", { name: "Save" }).click();

  const blockedHeading = page.getByRole("heading", { name: "We couldn't verify access" });
  await expect(blockedHeading).toBeVisible();
  await expect(page.getByText("stale mutation after version change", { exact: true })).toHaveCount(0);

  await context.close();
});
