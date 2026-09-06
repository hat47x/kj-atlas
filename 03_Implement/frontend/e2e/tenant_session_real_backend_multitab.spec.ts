import { expect, test, type Page } from "@playwright/test";

const TENANT_SESSION_HEADER = "KJ-Atlas-Tenant-Session-Version";
const CSRF_COOKIE = "Kj-Atlas-Csrf";
const CSRF_HEADER = "X-Kj-Atlas-Csrf";

type TenantSummary = {
  id: string;
  displayName: string;
};

type TenantSessionContext = {
  principalId: string;
  activeTenant: TenantSummary;
  availableTenants: TenantSummary[];
  effectiveCapabilities: string[];
  capabilityVersion: string;
  tenantSessionVersion: string;
};

type BrowserJsonResponse = {
  status: number;
  body: unknown;
};

function buildProbeDocument(docId: string) {
  const now = "2026-09-06T00:00:00.000Z";
  return {
    version: 1,
    id: docId,
    title: "AC-13 stale mutation probe",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "probe-card",
        text: "This payload must never be committed from a stale tenant session.",
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

async function login(page: Page): Promise<TenantSessionContext> {
  await page.goto("/");

  const signIn = page.getByRole("button");
  await expect(signIn).toHaveCount(1);
  await expect(signIn).toBeVisible();

  const loginResponsePromise = page.waitForResponse((response) =>
    new URL(response.url()).pathname === "/session/login",
  );
  await signIn.click();
  const loginResponse = await loginResponsePromise;
  expect(loginResponse.headers()["x-kj-atlas-e2e-upstream"]).toBe("worker-1");

  await expect(page).toHaveURL(/localhost:9100\/oauth\/authorize/);
  await expect(page.getByRole("heading", { name: "Authorize Application" })).toBeVisible();

  const callbackResponsePromise = page.waitForResponse((response) =>
    new URL(response.url()).pathname === "/session/callback",
  );
  const authenticatedContextPromise = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/api/session/context" && response.status() === 200;
  });

  await page.getByRole("button", { name: "Approve" }).click();

  const callbackResponse = await callbackResponsePromise;
  expect(callbackResponse.status()).toBe(302);
  expect(callbackResponse.headers()["x-kj-atlas-e2e-upstream"]).toBe("worker-1");

  const sessionResponse = await authenticatedContextPromise;
  expect(sessionResponse.headers()["x-kj-atlas-e2e-upstream"]).toBe("worker-2");
  expect(sessionResponse.request().headers()["authorization"]).toBeUndefined();

  return await sessionResponse.json() as TenantSessionContext;
}

async function readSession(page: Page): Promise<TenantSessionContext> {
  const response = await page.evaluate(async () => {
    const result = await fetch("/api/session/context", {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      credentials: "same-origin",
    });
    return {
      status: result.status,
      body: await result.json(),
    };
  }) as BrowserJsonResponse;
  expect(response.status).toBe(200);
  return response.body as TenantSessionContext;
}

async function switchTenant(
  page: Page,
  tenantId: string,
  expectedTenantSessionVersion: string,
): Promise<BrowserJsonResponse> {
  return await page.evaluate(async ({ tenantId, expectedTenantSessionVersion, csrfCookie, csrfHeader }) => {
    const csrfToken = document.cookie
      .split(";")
      .map((part) => part.trim())
      .find((part) => part.startsWith(`${csrfCookie}=`))
      ?.slice(csrfCookie.length + 1);
    if (!csrfToken) {
      throw new Error("CSRF cookie is missing");
    }

    const result = await fetch("/api/session/active-tenant", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        [csrfHeader]: csrfToken,
      },
      body: JSON.stringify({ tenantId, expectedTenantSessionVersion }),
      cache: "no-store",
      credentials: "same-origin",
    });
    return {
      status: result.status,
      body: await result.json(),
    };
  }, {
    tenantId,
    expectedTenantSessionVersion,
    csrfCookie: CSRF_COOKIE,
    csrfHeader: CSRF_HEADER,
  }) as BrowserJsonResponse;
}

async function tenantScopedJsonRequest(
  page: Page,
  method: "GET" | "PUT",
  path: string,
  tenantSessionVersion: string,
  body?: unknown,
): Promise<BrowserJsonResponse> {
  return await page.evaluate(async ({ method, path, tenantSessionVersion, body, sessionHeader, csrfCookie, csrfHeader }) => {
    const csrfToken = document.cookie
      .split(";")
      .map((part) => part.trim())
      .find((part) => part.startsWith(`${csrfCookie}=`))
      ?.slice(csrfCookie.length + 1);
    if (!csrfToken) {
      throw new Error("CSRF cookie is missing");
    }

    const headers: Record<string, string> = {
      Accept: "application/json",
      [sessionHeader]: tenantSessionVersion,
      [csrfHeader]: csrfToken,
    };
    if (body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    const result = await fetch(path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      cache: "no-store",
      credentials: "same-origin",
    });
    const text = await result.text();
    let responseBody: unknown = null;
    if (text) {
      try {
        responseBody = JSON.parse(text) as unknown;
      } catch {
        responseBody = text;
      }
    }
    return { status: result.status, body: responseBody };
  }, {
    method,
    path,
    tenantSessionVersion,
    body,
    sessionHeader: TENANT_SESSION_HEADER,
    csrfCookie: CSRF_COOKIE,
    csrfHeader: CSRF_HEADER,
  }) as BrowserJsonResponse;
}

test("stale tenant session requests from a second tab fail before lookup or commit on the real backend", async ({ page }) => {
  const initialA = await login(page);
  expect(initialA.principalId).toBe("user-1");
  expect(initialA.activeTenant.id).toBe("tenant-a");
  expect(initialA.availableTenants.length).toBeGreaterThanOrEqual(2);

  const targetTenant = initialA.availableTenants.find(
    (tenant) => tenant.id !== initialA.activeTenant.id,
  );
  expect(targetTenant).toBeDefined();
  if (!targetTenant) {
    throw new Error("real SaaS E2E fixture must expose at least two tenant memberships");
  }

  const tabB = await page.context().newPage();
  await tabB.goto("/");
  const initialB = await readSession(tabB);
  expect(initialB.principalId).toBe(initialA.principalId);
  expect(initialB.activeTenant.id).toBe(initialA.activeTenant.id);
  expect(initialB.tenantSessionVersion).toBe(initialA.tenantSessionVersion);

  const staleVersion = initialB.tenantSessionVersion;
  const switchedResponse = await switchTenant(
    page,
    targetTenant.id,
    initialA.tenantSessionVersion,
  );
  expect(switchedResponse.status).toBe(200);
  const switched = switchedResponse.body as TenantSessionContext;
  expect(switched.activeTenant.id).toBe(targetTenant.id);
  expect(switched.tenantSessionVersion).not.toBe(staleVersion);

  const missingDocId = "ac13-missing-doc-probe";
  const staleLookup = await tenantScopedJsonRequest(
    tabB,
    "GET",
    `/api/docs/${missingDocId}`,
    staleVersion,
  );
  expect(staleLookup.status).toBe(409);
  expect(staleLookup.body).toMatchObject({
    detail: { code: "tenant_session_changed" },
  });

  const mutationDocId = "ac13-stale-put-probe";
  const staleMutation = await tenantScopedJsonRequest(
    tabB,
    "PUT",
    `/api/docs/${mutationDocId}`,
    staleVersion,
    buildProbeDocument(mutationDocId),
  );
  expect(staleMutation.status).toBe(409);
  expect(staleMutation.body).toMatchObject({
    detail: { code: "tenant_session_changed" },
  });

  const mutationProbeAfterRejection = await tenantScopedJsonRequest(
    page,
    "GET",
    `/api/docs/${mutationDocId}`,
    switched.tenantSessionVersion,
  );
  expect(mutationProbeAfterRejection.status).toBe(404);

  const staleRollback = await switchTenant(
    tabB,
    initialA.activeTenant.id,
    staleVersion,
  );
  expect(staleRollback.status).toBe(409);
  expect(staleRollback.body).toMatchObject({
    detail: { code: "tenant_session_changed" },
  });

  const finalSession = await readSession(page);
  expect(finalSession.activeTenant.id).toBe(targetTenant.id);
  expect(finalSession.tenantSessionVersion).toBe(switched.tenantSessionVersion);
});
