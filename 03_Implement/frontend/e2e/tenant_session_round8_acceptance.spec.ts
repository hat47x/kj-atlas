import { expect, test, type BrowserContext, type Locator, type Page, type Route } from "@playwright/test";

const TENANT_SESSION_HEADER = "kj-atlas-tenant-session-version";
const START_PANEL = '[data-panel="start-document-entry"]';
const SANITY_CEILING_MS = 45_000;

type TenantId = "tenant-a" | "tenant-b";
type Locale = "en" | "ja";

type ServerState = {
  activeTenantId: TenantId;
  tenantSessionVersion: string;
  documents: Record<TenantId, ReturnType<typeof buildDocument>>;
};

function buildDocument(tenantId: TenantId) {
  const now = "2026-09-06T00:00:00.000Z";
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: `${tenantId} Round 8 fixture`,
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
        await fulfillJson(route, 409, {
          detail: { code: "tenant_session_changed", message: "Session context changed" },
        });
        return;
      }
      if (payload.tenantId !== "tenant-a" && payload.tenantId !== "tenant-b") {
        await fulfillJson(route, 404, { detail: { code: "tenant_not_available" } });
        return;
      }
      state.activeTenantId = payload.tenantId;
      state.tenantSessionVersion = state.tenantSessionVersion === "session-v1" ? "session-v2" : "session-v3";
      await fulfillJson(route, 200, sessionContext(state), { "Cache-Control": "no-store" });
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
    if (url.pathname === "/api/docs" && request.method() === "GET") {
      const doc = state.documents[state.activeTenantId];
      await fulfillJson(route, 200, [{
        id: doc.id,
        title: doc.title,
        created_by: "principal-1",
        lifecycle_state: "active",
        updated_at: doc.updatedAt,
      }]);
      return;
    }
    if (url.pathname === "/api/docs/doc_phase1_canvas" && request.method() === "GET") {
      if (request.headers()[TENANT_SESSION_HEADER] !== state.tenantSessionVersion) {
        await fulfillJson(route, 409, {
          detail: { code: "tenant_session_changed", message: "Session context changed" },
        });
        return;
      }
      await fulfillJson(route, 200, state.documents[state.activeTenantId], {
        ETag: `"${state.activeTenantId}-round8"`,
      });
      return;
    }

    await fulfillJson(route, 404, { detail: { code: "not_found" } });
  });
}

async function seedTenantCaches(context: BrowserContext) {
  await context.addInitScript(() => {
    const principalId = "principal-1";
    const prefixFor = (tenantId: "tenant-a" | "tenant-b") => (
      `kj-atlas/tenant-scope/v1/${encodeURIComponent(window.location.origin)}/${encodeURIComponent(tenantId)}/${encodeURIComponent(principalId)}/`
    );
    const scopedKey = (tenantId: "tenant-a" | "tenant-b", baseKey: string) => (
      `${prefixFor(tenantId)}${encodeURIComponent(baseKey)}`
    );

    window.localStorage.setItem(
      scopedKey("tenant-a", "kj-atlas/recent-doc-ids"),
      JSON.stringify(["doc_tenant_a_round8"]),
    );
    window.localStorage.setItem(
      scopedKey("tenant-b", "kj-atlas/recent-doc-ids"),
      JSON.stringify(["doc_tenant_b_round8"]),
    );
  });
}

function tenantSwitcher(page: Page): Locator {
  return page.locator("select").filter({
    has: page.locator('option[value="tenant-b"]'),
  }).first();
}

async function reachByTab(page: Page, target: Locator): Promise<number> {
  await page.evaluate(() => {
    const active = document.activeElement;
    if (active instanceof HTMLElement) {
      active.blur();
    }
    document.body.tabIndex = -1;
    document.body.focus();
    document.body.removeAttribute("tabindex");
  });

  for (let presses = 1; presses <= 60; presses += 1) {
    await page.keyboard.press("Tab");
    if (await target.evaluate((element) => document.activeElement === element)) {
      return presses;
    }
  }
  throw new Error("Tenant switcher was not reachable by keyboard Tab navigation within 60 presses");
}

async function tenantScopedKeys(page: Page, tenantId: TenantId): Promise<string[]> {
  return page.evaluate(({ targetTenantId }) => {
    const prefix = `kj-atlas/tenant-scope/v1/${encodeURIComponent(window.location.origin)}/${encodeURIComponent(targetTenantId)}/${encodeURIComponent("principal-1")}/`;
    return Array.from({ length: window.localStorage.length }, (_, index) => window.localStorage.key(index))
      .filter((key): key is string => typeof key === "string" && key.startsWith(prefix));
  }, { targetTenantId: tenantId });
}

const round8Cases: Array<{ locale: Locale; width: number; height: number }> = [
  { locale: "en", width: 390, height: 844 },
  { locale: "en", width: 768, height: 900 },
  { locale: "en", width: 1440, height: 900 },
  { locale: "ja", width: 390, height: 844 },
  { locale: "ja", width: 768, height: 900 },
  { locale: "ja", width: 1440, height: 900 },
];

test.skip(
  process.env.KJ_ATLAS_E2E_SAAS !== "1",
  "Runs only with playwright.saas.config.ts and the SaaS runtime profile.",
);

test("Round 8 R8-E/F validates SaaS tenant UI across viewport, locale, keyboard/focus, DOM/cache disposal, and startup operability", async ({ browser }, testInfo) => {
  test.slow();
  const evidence: Array<Record<string, unknown>> = [];

  for (const scenario of round8Cases) {
    const state = createServerState();
    const context = await browser.newContext({
      viewport: { width: scenario.width, height: scenario.height },
    });
    try {
      await seedTenantCaches(context);
      await installSaasServer(context, state);
      const page = await context.newPage();

      await page.goto(`/?locale=${scenario.locale}`);
      const startPanel = page.locator(START_PANEL);
      await expect(startPanel).toBeVisible();
      const closeButton = startPanel.getByRole("button", {
        name: scenario.locale === "en" ? "Close start panel" : "開始パネルを閉じる",
      });
      await expect(closeButton).toBeEnabled({ timeout: SANITY_CEILING_MS });
      const bootstrapReadyMs = await page.evaluate(() => performance.now());
      expect(bootstrapReadyMs).toBeGreaterThan(0);
      expect(bootstrapReadyMs).toBeLessThan(SANITY_CEILING_MS);

      await closeButton.click();
      await expect(startPanel).toBeHidden();
      await expect(page.getByRole("button", { name: "tenant-a confidential card" })).toBeVisible();

      const switcher = tenantSwitcher(page);
      await expect(switcher).toBeVisible();
      await expect(switcher).toBeEnabled();
      const workspaceReadyMs = await page.evaluate(() => performance.now());
      expect(workspaceReadyMs).toBeGreaterThanOrEqual(bootstrapReadyMs);
      expect(workspaceReadyMs).toBeLessThan(SANITY_CEILING_MS);

      expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

      const tabPresses = await reachByTab(page, switcher);
      await expect(switcher).toBeFocused();
      expect(await switcher.evaluate((element) => element.matches(":focus-visible"))).toBe(true);

      // Use the native select from the keyboard so R8-F proves the tenant switch
      // is not merely mouse/selectOption-operable.
      await page.keyboard.press("ArrowDown");
      await expect(switcher).toHaveValue("tenant-b");
      await expect(page.getByRole("button", { name: "tenant-b confidential card" })).toBeVisible();
      await expect(page.getByText("tenant-a confidential card", { exact: true })).toHaveCount(0);

      const tenantAKeys = await tenantScopedKeys(page, "tenant-a");
      const tenantBKeys = await tenantScopedKeys(page, "tenant-b");
      expect(tenantAKeys).toEqual([]);
      expect(tenantBKeys.some((key) => key.includes(encodeURIComponent("kj-atlas/recent-doc-ids")))).toBe(true);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

      const screenshot = await page.screenshot({ fullPage: true });
      await testInfo.attach(`round8-${scenario.locale}-${scenario.width}px.png`, {
        contentType: "image/png",
        body: screenshot,
      });

      evidence.push({
        locale: scenario.locale,
        viewport: `${scenario.width}x${scenario.height}`,
        bootstrapReadyMs: Number(bootstrapReadyMs.toFixed(1)),
        workspaceReadyMs: Number(workspaceReadyMs.toFixed(1)),
        tabPressesToTenantSwitcher: tabPresses,
        oldTenantDomDiscarded: true,
        oldTenantScopedCacheDiscarded: true,
        horizontalOverflow: false,
      });
    } finally {
      await context.close();
    }
  }

  console.info(`SAAS-TENANT-01 AC-12 Round 8 evidence: ${JSON.stringify(evidence)}`);
  await testInfo.attach("saas-tenant-ac12-round8-evidence.json", {
    contentType: "application/json",
    body: Buffer.from(JSON.stringify({
      operationallyReadySignal: "SaaS start panel is dismissible and active-tenant document + tenant switcher are operable",
      sanityCeilingMs: SANITY_CEILING_MS,
      cases: evidence,
    }, null, 2)),
  });
});
