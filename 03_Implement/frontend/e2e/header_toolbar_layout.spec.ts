import { expect, test, type Page } from "@playwright/test";

type Box = {
  bottom: number;
  height: number;
  right: number;
  text: string;
  width: number;
  x: number;
  y: number;
};

const checkedViewports = [
  { width: 1280, height: 720 },
  { width: 920, height: 720 },
] as const;

async function collectHeaderButtons(page: Page): Promise<Box[]> {
  return page.locator("header button").evaluateAll((nodes) =>
    nodes.map((node) => {
      const rect = node.getBoundingClientRect();
      return {
        text: (node.textContent ?? "").replace(/\s+/g, " ").trim(),
        x: rect.x,
        y: rect.y,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height,
      };
    })
  );
}

async function collectFixedPanels(page: Page): Promise<Box[]> {
  return page.locator("body *").evaluateAll((nodes) =>
    nodes
      .map((node) => {
        const rect = node.getBoundingClientRect();
        const style = getComputedStyle(node);
        return {
          text: (node.textContent ?? "").replace(/\s+/g, " ").trim(),
          x: rect.x,
          y: rect.y,
          right: rect.right,
          bottom: rect.bottom,
          width: rect.width,
          height: rect.height,
          position: style.position,
        };
      })
      .filter((entry) => entry.position === "fixed" && entry.width > 0 && entry.height > 0)
  );
}

for (const viewport of checkedViewports) {
  test(`header toolbar stays readable at ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("/");
    await page.waitForSelector("header");

    const headerBox = await page.locator("header").boundingBox();
    expect(headerBox).not.toBeNull();
    const headerBottom = headerBox!.y + headerBox!.height;

    const viewportMetrics = await page.evaluate(() => ({
      bodyMargin: getComputedStyle(document.body).margin,
      scrollWidth: document.documentElement.scrollWidth,
    }));
    expect(viewportMetrics.bodyMargin).toBe("0px");
    expect(viewportMetrics.scrollWidth).toBe(viewport.width);

    const buttons = await collectHeaderButtons(page);
    const offscreen = buttons.filter((entry) => entry.x < 0 || entry.right > viewport.width).map((entry) => entry.text);
    const verticalish = buttons.filter((entry) => entry.height > 44 || (entry.width > 0 && entry.height / entry.width > 1.2)).map((entry) => entry.text);
    expect(offscreen).toEqual([]);
    expect(verticalish).toEqual([]);

    await page.getByRole("button", { name: "View", exact: true }).click();
    const viewPanels = await collectFixedPanels(page);
    expect(viewPanels.length).toBeGreaterThan(0);
    expect(viewPanels.some((panel) => panel.y < headerBottom)).toBe(false);
    await page.getByRole("button", { name: "View", exact: true }).click();

    await page.locator("header button").nth(5).click();
    const sharePanels = await collectFixedPanels(page);
    expect(sharePanels.length).toBeGreaterThan(0);
    expect(sharePanels.some((panel) => panel.y < headerBottom)).toBe(false);
    expect(sharePanels.some((panel) => panel.bottom > viewport.height || panel.right > viewport.width)).toBe(false);
  });
}
