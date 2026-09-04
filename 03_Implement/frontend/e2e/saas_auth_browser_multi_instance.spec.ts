import { expect, test } from "@playwright/test";

test("BFF login survives routing from worker 1 to worker 2 through shared PostgreSQL", async ({ page }) => {
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
  await expect(sessionResponse.json()).resolves.toMatchObject({
    principalId: "user-1",
    activeTenant: { id: "tenant-a" },
    capabilityVersion: "e2e-v1",
  });

  const authCookie = (await page.context().cookies()).find(
    (cookie) => cookie.name === "Kj-Atlas-Auth-Session",
  );
  expect(authCookie).toBeDefined();
  expect(authCookie?.httpOnly).toBe(true);
  expect(authCookie?.secure).toBe(true);

  const browserTokenState = await page.evaluate(() => ({
    localStorage: Object.entries(window.localStorage),
    sessionStorage: Object.entries(window.sessionStorage),
  }));
  expect(JSON.stringify(browserTokenState)).not.toContain("Bearer ");
  expect(JSON.stringify(browserTokenState)).not.toContain("access_token");
});
