import { expect, test } from "@playwright/test";

const REV_1 = "1".repeat(64);
const REV_2 = "2".repeat(64);
const REV_3 = "3".repeat(64);

test("allowlist conflict reloads current state without automatic retry", async ({ page }) => {
  let getCount = 0;
  let putCount = 0;
  const putBodies: Array<{ modelIds: string[]; expectedRevision: string }> = [];

  await page.route("**/api/admin/provision/models/tenants/tenant-a/allowlist", async (route) => {
    const request = route.request();
    if (request.method() === "GET") {
      getCount += 1;
      const current = getCount === 1
        ? { tenantId: "tenant-a", modelIds: ["model-a", "model-c"], revision: REV_1 }
        : { tenantId: "tenant-a", modelIds: ["model-a", "model-d"], revision: REV_2 };
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(current),
      });
      return;
    }

    if (request.method() === "PUT") {
      putCount += 1;
      putBodies.push(JSON.parse(request.postData() ?? "{}") as {
        modelIds: string[];
        expectedRevision: string;
      });
      if (putCount === 1) {
        await route.fulfill({
          status: 409,
          contentType: "application/json",
          body: JSON.stringify({
            detail: {
              code: "model_allowlist_conflict",
              message: "The tenant model allowlist changed after it was read.",
              currentRevision: REV_2,
            },
          }),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          tenantId: "tenant-a",
          modelIds: ["model-a", "model-b"],
          revision: REV_3,
        }),
      });
      return;
    }

    await route.abort();
  });

  await page.goto("/admin.html");
  await page.getByTestId("tenant-id").fill("tenant-a");
  await page.getByTestId("load-current").click();
  await expect(page.getByTestId("baseline-revision")).toHaveText(REV_1);

  await page.getByTestId("model-ids").fill("model-a\nmodel-b");
  await page.getByTestId("save-allowlist").click();

  await expect(page.getByTestId("conflict-panel")).toBeVisible();
  await expect(page.getByTestId("current-revision")).toHaveText(REV_2);
  await expect(page.getByTestId("only-in-draft")).toContainText("model-b");
  await expect(page.getByTestId("only-on-server")).toContainText("model-d");
  await expect(page.getByTestId("save-allowlist")).toBeDisabled();
  expect(putCount).toBe(1);
  expect(getCount).toBe(2);
  expect(putBodies[0]).toEqual({
    modelIds: ["model-a", "model-b"],
    expectedRevision: REV_1,
  });

  await page.getByTestId("continue-draft").click();
  await expect(page.getByTestId("conflict-panel")).toHaveCount(0);
  await expect(page.getByTestId("baseline-revision")).toHaveText(REV_2);
  expect(putCount).toBe(1);

  await page.getByTestId("save-allowlist").click();
  await expect(page.getByTestId("status-message")).toContainText("保存しました");
  expect(putCount).toBe(2);
  expect(putBodies[1]).toEqual({
    modelIds: ["model-a", "model-b"],
    expectedRevision: REV_2,
  });
});
