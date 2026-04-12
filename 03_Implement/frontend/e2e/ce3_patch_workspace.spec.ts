import { expect, test } from "@playwright/test";

test("CE3 patch workspace supports candidate comparison, preset replay, and rollback recovery", async ({ page }) => {
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    const now = new Date().toISOString();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        version: 2,
        id: "doc_phase1_canvas",
        createdAt: now,
        updatedAt: now,
        transform: { panX: 0, panY: 0, zoom: 1 },
        cards: [],
        edges: [],
        islands: [],
      }),
    });
  });
  await page.route("**/ai/suggest-merges", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        suggestions: [
          {
            groupId: "group-alpha",
            targetCardId: "c1",
            candidateCardIds: ["c2", "c3"],
            scoreSummary: { min: 0.88, max: 0.99, avg: 0.93 },
            reasonCodes: ["heuristic:normalized-text"],
            snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
            cardIds: ["c1", "c2", "c3"],
            mergedTextDraft: "alpha",
            rationale: "deterministic fixture",
          },
          {
            groupId: "group-beta",
            targetCardId: "c4",
            candidateCardIds: [],
            scoreSummary: { min: 0.95, max: 0.95, avg: 0.95 },
            reasonCodes: ["heuristic:token-signature"],
            snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
            cardIds: ["c4"],
            mergedTextDraft: "beta",
            rationale: "deterministic fixture",
          },
          {
            groupId: "group-gamma",
            targetCardId: "c5",
            candidateCardIds: [],
            scoreSummary: { min: 0.91, max: 0.91, avg: 0.91 },
            reasonCodes: ["heuristic:token-signature"],
            snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
            cardIds: ["c5"],
            mergedTextDraft: "gamma",
            rationale: "deterministic fixture",
          },
        ],
      }),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: /^Load document\.json$|^document\.json を読み込む$/ }).click();
  const fileChooser = await fileChooserPromise;

  const now = new Date().toISOString();
  const doc = {
    version: 2,
    id: "doc_e2e_ce3_workspace",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "alpha", x: 100, y: 100 },
      { id: "c2", text: "Alpha", x: 130, y: 120 },
      { id: "c3", text: "alpha ", x: 160, y: 140 },
      { id: "c4", text: "beta", x: 500, y: 100 },
      { id: "c5", text: "gamma", x: 560, y: 120 },
    ],
    edges: [],
    islands: [],
  };

  await fileChooser.setFiles({
    name: "ce3-workspace-doc.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(doc), "utf-8"),
  });

  await page.getByRole("button", { name: /Replace current document|現在の document を置換/ }).click();
  await expect(page.getByText("Replaced current document")).toBeVisible();

  await page.getByRole("button", { name: /Collect candidates/i }).click();

  const workspace = page.getByTestId("ce3-workspace-panel");
  await expect(workspace).toBeVisible();
  await expect(page.getByTestId("ce3-candidate-select")).toBeEnabled();
  await expect(page.getByTestId("ce3-candidate-count")).toContainText("(3)");
  await expect(page.getByTestId("ce3-diff-preview")).toContainText("Patch diff preview");
  await expect(page.getByTestId("ce3-diff-preview")).toContainText("Token delta:");
  const optionLocator = page.locator('[data-testid="ce3-candidate-select"] option');
  await expect(optionLocator).toHaveCount(3);
  const alphaCandidateId = await optionLocator.nth(0).getAttribute("value");
  const betaCandidateId = await optionLocator.nth(1).getAttribute("value");
  const gammaCandidateId = await optionLocator.nth(2).getAttribute("value");
  expect(alphaCandidateId).not.toBeNull();
  expect(betaCandidateId).not.toBeNull();
  expect(gammaCandidateId).not.toBeNull();

  await page.getByTestId("ce3-adopt").click();
  await expect(page.getByTestId("ce3-decision-state")).toContainText("adopt");
  await expect(page.getByTestId(`ce3-candidate-state-${alphaCandidateId}`)).toContainText("adopt");

  await page.getByTestId("ce3-candidate-select").selectOption(betaCandidateId ?? "");
  await page.getByTestId("ce3-reject").click();
  await expect(page.getByTestId(`ce3-candidate-state-${betaCandidateId}`)).toContainText("reject");
  await expect(page.getByTestId(`ce3-candidate-state-${alphaCandidateId}`)).toContainText("adopt");
  await expect(page.getByTestId(`ce3-candidate-state-${gammaCandidateId}`)).toContainText("hold");
  await expect(page.getByTestId("ce3-audit-log-size")).toContainText("2");

  await page.getByTestId("ce3-rollback").click();
  await expect(page.getByTestId("ce3-decision-state")).toContainText("hold");
  await expect(page.getByTestId(`ce3-candidate-state-${betaCandidateId}`)).toContainText("hold");
  await expect(page.getByTestId(`ce3-candidate-state-${alphaCandidateId}`)).toContainText("adopt");
  await expect(page.getByTestId(`ce3-candidate-audit-${betaCandidateId ?? ""}`)).toContainText("rollback");
  await expect(page.getByTestId(`ce3-candidate-audit-${alphaCandidateId ?? ""}`)).not.toContainText("rollback");
  await expect(page.getByTestId("ce3-audit-log-size")).toContainText("3");

  await page.getByTestId("ce3-preset-name").fill("Local CE3 Preset");
  await page.getByTestId("ce3-preset-scope").selectOption("selection");
  await page.getByTestId("ce3-preset-depth").fill("2");
  await page.getByTestId("ce3-preset-filters").fill(" risk, merge ");
  await page.getByTestId("ce3-save-preset").click();

  await page.getByRole("button", { name: "Run current preset" }).click();
  await expect(page.getByTestId("ce3-normalized-query")).toContainText("\"scope\":\"selection\"");
  await expect(page.getByTestId("ce3-normalized-query")).toContainText("\"depth\":2");
  await expect(page.getByTestId("ce3-normalized-query")).toContainText("\"filters\":[\"merge\",\"risk\"]");

  await page.getByRole("button", { name: /Run Local CE3 Preset/ }).click();
  await expect(page.getByTestId("ce3-normalized-query")).toContainText("\"scope\":\"selection\"");
  await expect(page.getByTestId("ce3-failure")).toHaveCount(0);

  await page.reload();
  await page.getByRole("button", { name: /Collect candidates/i }).click();
  await page.getByRole("button", { name: /Run Local CE3 Preset/ }).click();
  await expect(page.getByTestId("ce3-normalized-query")).toContainText("\"filters\":[\"merge\",\"risk\"]");
});
