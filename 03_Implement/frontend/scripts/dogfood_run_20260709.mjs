// VALUE-DOGFOOD-01: a genuine, backend-present dogfood run against the real
// docker-compose stack (db+api+web at http://127.0.0.1:8080), not a mocked
// e2e fixture. Drives the ADR-0042 5-step path with real material (this
// session's own EXT-AGENT-02 open questions) and narrates observations to
// stdout for the dogfood log. This is a one-off exploratory script, not a
// test -- kept for reproducibility, not wired into CI.
import { chromium } from "@playwright/test";

const BASE_URL = process.env.KJ_ATLAS_DOGFOOD_URL ?? "http://127.0.0.1:8080/?locale=ja";

function log(step, message) {
  console.log(`\n[${step}] ${message}`);
}

async function run() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
  page.on("console", (msg) => {
    if (msg.type() === "error") console.log(`  [browser console error] ${msg.text()}`);
  });
  page.on("pageerror", (err) => console.log(`  [browser page error] ${err.message}`));
  page.on("response", (response) => {
    if (response.status() >= 400) console.log(`  [network ${response.status()}] ${response.url()}`);
  });

  // Canvas cards expose role="option" in the accessibility tree, but so do
  // native <select><option> elements elsewhere on the page (e.g. the
  // domain-state-filter select) -- scope to the primary-flow canvas region
  // to avoid picking up the wrong "option".
  const cards = page.locator('[data-ui-region="primary-flow"]').getByRole("option");

  log("setup", `navigating to ${BASE_URL}`);
  await page.goto(BASE_URL);
  await page.waitForTimeout(500);

  // Step 1: place cards from real material (own notes) into a fresh document.
  log("step1", "creating a new document from the start panel");
  const newDocButton = page.getByRole("button", { name: /新しい文書を作成|Create new document/ });
  await newDocButton.click();
  await page.waitForTimeout(300);

  const safeModeText = await page.locator('text=セーフモード').first().textContent().catch(() => null);
  log("step1", `SafeMode indicator on fresh document: "${safeModeText}"`);

  const cardTexts = [
    "EXT-AGENT-02の応答取込先、island_titleとcritiqueには既存の複数候補UIが無かった",
    "PatchWorkspacePanelのCandidateItemにPatchV1を運ぶフィールドが無く、実適用パイプラインと分離している",
    "context-auditはCE1/CE4専用のequivalenceKey/bundleHash契約で、外部応答インポートには合わない",
    "この3点は「設計として決着している」のか、それとも「まだ誰も気づいていないだけ」なのか、今の時点では判断できない",
  ];

  for (const [index, text] of cardTexts.entries()) {
    log("step1", `adding card ${index + 1}/${cardTexts.length}`);
    const countBefore = await cards.count();
    await page.getByRole("button", { name: /新規カード|New card/ }).click();
    await page.waitForFunction(
      (expected) => document.querySelectorAll('[data-ui-region="primary-flow"] [role="option"]').length >= expected,
      countBefore + 1,
    );
    // NOTE (real finding, from reading App.tsx's createCardAtPosition): a
    // newly created card auto-enters edit mode in the SAME state update that
    // adds it (setEditingCardId(newCardId) right after the card is appended)
    // -- no dblclick is needed, and doing one anyway is a race: if the click
    // lands outside the live textarea it blurs (commits the untouched
    // default text as a no-op) then a second click's dblclick-to-edit
    // handler reopens edit mode, which is an extra, unnecessary state hop.
    // Go straight to the textarea.
    const newCard = cards.last();
    // NOTE (real finding): selecting/editing a card ALSO surfaces the
    // SidePanel's KA-method (inner-voice/value) and critique-comment
    // textareas at the same time -- a page-wide "textarea:visible" locator
    // is ambiguous (4 matches). Scope to the card's OWN edit textarea.
    const editTextarea = newCard.locator("textarea");
    await editTextarea.waitFor({ state: "visible", timeout: 5000 });
    await editTextarea.fill(text);
    // Escape CANCELS the edit (reverts to the original text) -- Enter
    // commits it. Confirmed by reading CardView.tsx's textarea onKeyDown.
    await editTextarea.press("Enter");
    // Wait for the edit textarea to fully unmount (editingCardId cleared)
    // before moving on, so the next card-creation click can't land while
    // this card's edit state is still open.
    await editTextarea.waitFor({ state: "detached", timeout: 5000 }).catch(() => {});
    // Poll for the real committed text instead of trusting a fixed delay --
    // a fixed waitForTimeout raced against React's re-render in earlier runs
    // and produced false "empty" reads.
    await page.waitForFunction(
      ({ expectedText, index: cardIndex }) => {
        const el = document.querySelectorAll('[data-ui-region="primary-flow"] [role="option"]')[cardIndex];
        return Boolean(el && el.textContent && el.textContent.includes(expectedText.slice(0, 10)));
      },
      { expectedText: text, index: index },
      { timeout: 5000 },
    ).catch(() => {});
    const committedText = await newCard.textContent();
    log("step1", `card ${index} text immediately after commit: "${committedText?.slice(0, 40)}"`);

    // REAL FINDING (resolved after 6 runs; root cause confirmed by reading
    // the saved document out of postgres): what looked like "alternating
    // cards losing their just-typed text" is NOT data loss. The text is
    // committed to the document model every time -- but new cards cascade
    // at (+40,+40) from their anchor, the cascade overlaps their LABEL
    // rects, and CanvasShell's label culling (labelCullingResult ->
    // showLabelText=false) then hides the TEXT of whichever cards lose the
    // overlap contest (alternating winners). To the user it looks exactly
    // like their text vanished. The retry below is kept as a probe: it
    // "fails" too, because handleCommitCardText sees nextText ===
    // targetCard.text (the model already has the text!) and no-ops.
    // Corner-targeted dblclick because the cascade also covers each card's
    // CENTER, making center clicks fail with "intercepts pointer events".
    for (let attempt = 0; attempt < 2; attempt++) {
      const current = await newCard.textContent();
      if (current && current.includes(text.slice(0, 10))) {
        break;
      }
      log("step1", `card ${index} commit did not stick (attempt ${attempt + 1}), retrying via corner dblclick`);
      await newCard.dblclick({ position: { x: 12, y: 12 } });
      const retryTextarea = newCard.locator("textarea");
      await retryTextarea.waitFor({ state: "visible", timeout: 5000 });
      await retryTextarea.fill(text);
      await retryTextarea.press("Enter");
      await retryTextarea.waitFor({ state: "detached", timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(400);
    }

    // Settle pause before the next card's creation click, roughly matching
    // human pacing between card entries.
    await page.waitForTimeout(800);
  }

  const cardCountAfterPlacement = await cards.count();
  log("step1", `card count after placement: ${cardCountAfterPlacement} (expected ${cardTexts.length})`);
  const actualTexts = await cards.allTextContents();
  for (const [index, text] of actualTexts.entries()) {
    log("step1", `card ${index} actual text: "${text.slice(0, 60)}"`);
  }

  // Repair pass, kept as a diagnostic probe. With the label-culling root
  // cause (see the creation loop above) this pass always reports
  // "text after repair: empty" for culled cards: the model already holds
  // the correct text, so re-committing the identical text is a no-op and
  // the label stays culled. That behavior -- a user retyping "lost" text
  // and seeing no effect at all -- is itself a key friction observation
  // for the dogfood log (filed as QA-MONKEY-10).
  for (const [index, text] of cardTexts.entries()) {
    const currentText = await cards.nth(index).textContent();
    if (currentText && currentText.includes(text.slice(0, 10))) {
      continue;
    }
    log("step1", `repairing card ${index}: lost text, re-editing`);
    const target = cards.nth(index);
    // Corner-targeted dblclick: cascade placement means the card's center is
    // covered by its successor (see the finding in the creation loop above).
    // NOT force:true -- a forced click dispatches to whatever element the
    // browser hit-tests at that point, i.e. the OVERLAPPING card, which is
    // exactly the wrong target.
    await target.dblclick({ position: { x: 12, y: 12 } });
    const repairTextarea = target.locator("textarea");
    await repairTextarea.waitFor({ state: "visible", timeout: 5000 });
    await repairTextarea.fill(text);
    await repairTextarea.press("Enter");
    await repairTextarea.waitFor({ state: "detached", timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(300);
    const repairedText = await cards.nth(index).textContent();
    log("step1", `card ${index} text after repair: "${repairedText?.slice(0, 40)}"`);
  }

  // Step 2: register hold/critique/insufficient-evidence as "work state", not failure.
  log("step2", "selecting the last (most uncertain) card and marking it as held + critiqued");
  const uncertainCard = cards.filter({ hasText: "まだ誰も気づいていないだけ" });
  await uncertainCard.click();
  await page.waitForTimeout(200);

  const holdButtonVisible = await page.getByRole("button", { name: /保留|Hold/ }).first().isVisible().catch(() => false);
  log("step2", `a "hold" affordance is visible for the selected card without enabling Advanced: ${holdButtonVisible}`);
  if (holdButtonVisible) {
    await page.getByRole("button", { name: /保留|Hold/ }).first().click();
    await page.waitForTimeout(200);
  }

  // Step 3: build a cluster/relation, round-trip overview <-> detail.
  // Clear any lingering selection/overlay state from step 2 first -- a
  // still-selected card can render an inline quick-action overlay that
  // intercepts pointer events on the card underneath it.
  log("step3", "clicking empty canvas background to clear step2's selection state");
  await page.locator('[data-ui-region="primary-flow"]').click({ position: { x: 20, y: 20 } }).catch(() => {});
  await page.waitForTimeout(200);

  log("step3", "selecting the two related cards and bundling into an island");
  // Corner-targeted clicks -- same cascade-overlap finding as in step 1.
  await cards.nth(0).click({ position: { x: 12, y: 12 } });
  await cards.nth(1).click({ modifiers: ["Shift"], position: { x: 12, y: 12 } });
  const createIslandButton = page.getByRole("button", { name: /島を作成|Create Island/ });
  const canCreateIsland = await createIslandButton.isEnabled().catch(() => false);
  log("step3", `"create island" enabled with 2 cards selected: ${canCreateIsland}`);
  if (canCreateIsland) {
    await createIslandButton.click();
    await page.waitForTimeout(300);
  }

  log("step3", "checking minimap / view-mode round trip (overview <-> detail)");
  const summaryPill = page.getByRole("button", { name: /要約|Summary/ }).first();
  if (await summaryPill.isVisible().catch(() => false)) {
    await summaryPill.click();
    await page.waitForTimeout(200);
    const explorePill = page.getByRole("button", { name: /探索|Explore/ }).first();
    await explorePill.click();
    await page.waitForTimeout(200);
    log("step3", "round-tripped 要約(summary) -> 探索(explore) without error");
  } else {
    log("step3", "could not find summary/explore view-mode pills by expected label");
  }

  // Step 4: run pre-share confirmation and produce one artifact -- against the REAL backend.
  log("step4", "saving the document to the real backend");
  const saveButton = page.getByRole("button", { name: /保存|Save/ }).first();
  const canSave = await saveButton.isEnabled().catch(() => false);
  log("step4", `save button enabled: ${canSave}`);
  if (canSave) {
    await saveButton.click();
    await page.waitForTimeout(500);
    const statusAfterSave = await page.getByTestId("status-message").textContent().catch(() => null);
    log("step4", `status message after save: "${statusAfterSave}"`);
  }

  log("step4", "reloading the page to verify real persistence (not a mocked fixture)");
  await page.reload();
  await page.waitForTimeout(800);
  const startPanelVisibleAfterReload = await page.locator('[data-panel="start-document-entry"]').isVisible().catch(() => true);
  log("step4", `start panel visible after reload (true would mean the doc did NOT auto-resume): ${startPanelVisibleAfterReload}`);
  if (startPanelVisibleAfterReload) {
    const recentButton = page.getByRole("button", { name: /最近使ったドキュメント|Recent documents/ }).first();
    log("step4", `a "recent documents" affordance exists on the start panel: ${await recentButton.isVisible().catch(() => false)}`);
  }
  const cardCountAfterReload = await cards.count();
  // NOTE: this count is NOT canvas cards after a reload -- the start panel's
  // document list also renders role="option" entries (one per document in
  // the DB), so a non-zero value here with the start panel visible means
  // the saved document shows up in the pick list, i.e. real persistence
  // round-tripped. Confirmed against postgres: 3 documents exist, count=3.
  log("step4", `role=option count after reload (start panel document list): ${cardCountAfterReload}`);

  await browser.close();
  log("done", "run complete");
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
