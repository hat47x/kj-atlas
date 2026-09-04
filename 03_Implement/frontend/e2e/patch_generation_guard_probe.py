from pathlib import Path

path = Path(__file__).with_name("tenant_session_multitab.spec.ts")
source = path.read_text(encoding="utf-8")

helper = r'''

async function installStaleTenantSessionResultProbe(page: Page) {
  await page.evaluate(() => {
    const staleErrorName = "StaleTenantSessionResultError";
    const descriptor = Object.getOwnPropertyDescriptor(Error.prototype, "name");
    if (!descriptor || descriptor.configurable !== true) {
      throw new Error("Error.prototype.name is not configurable");
    }
    const fallbackName = typeof descriptor.value === "string" ? descriptor.value : "Error";

    Object.defineProperty(Error.prototype, "name", {
      configurable: true,
      get() {
        return fallbackName;
      },
      set(value: unknown) {
        if (value === staleErrorName) {
          const probeWindow = window as Window & {
            __kjTenantGenerationGuardRejected?: number;
          };
          probeWindow.__kjTenantGenerationGuardRejected =
            (probeWindow.__kjTenantGenerationGuardRejected ?? 0) + 1;
        }
        Object.defineProperty(this, "name", {
          configurable: true,
          writable: true,
          value,
        });
      },
    });
  });
}

async function staleGenerationGuardRejectionCount(page: Page): Promise<number> {
  return page.evaluate(() => (
    (window as Window & { __kjTenantGenerationGuardRejected?: number })
      .__kjTenantGenerationGuardRejected ?? 0
  ));
}
'''

anchor = "\ntest.skip(\n"
if source.count(anchor) != 1:
    raise SystemExit("expected one test.skip anchor")
source = source.replace(anchor, helper + anchor, 1)

replacements = [
    (
        '''  await selectWorkModeTab(pageA, "narrative");
  await expect(pageA.getByRole("tabpanel", { name: "Narrative" })).toBeVisible();

  let releaseDelayedNarrative: (() => Promise<void>) | undefined;''',
        '''  await selectWorkModeTab(pageA, "narrative");
  await expect(pageA.getByRole("tabpanel", { name: "Narrative" })).toBeVisible();
  await installStaleTenantSessionResultProbe(pageA);

  let releaseDelayedNarrative: (() => Promise<void>) | undefined;''',
    ),
    (
        '''  await pageA.getByRole("button", { name: "Generate from Reading Order" }).click();
  await expect.poll(() => releaseDelayedNarrative).toBeDefined();

  await pageB.getByLabel("Current workspace: Tenant A").selectOption("tenant-b");''',
        '''  await pageA.getByRole("button", { name: "Generate from Reading Order" }).click();
  await expect.poll(() => releaseDelayedNarrative).toBeDefined();
  await expect.poll(() => staleGenerationGuardRejectionCount(pageA)).toBe(0);

  await pageB.getByLabel("Current workspace: Tenant A").selectOption("tenant-b");''',
    ),
    (
        '''  const blockedHeading = pageA.getByRole("heading", { name: "We couldn’t verify access" });
  await expect(blockedHeading).toBeVisible();
  await expect(pageA.getByText("tenant-a confidential narrative draft", { exact: true })).toHaveCount(0);

  await releaseDelayedNarrative?.();
  await expect(blockedHeading).toBeVisible();''',
        '''  const blockedHeading = pageA.getByRole("heading", { name: "We couldn’t verify access" });
  await expect(blockedHeading).toBeVisible();
  await expect(pageA.getByText("tenant-a confidential narrative draft", { exact: true })).toHaveCount(0);
  await expect.poll(() => staleGenerationGuardRejectionCount(pageA)).toBe(0);

  await releaseDelayedNarrative?.();
  await expect.poll(
    () => staleGenerationGuardRejectionCount(pageA),
    { message: "generation guard must reject the stale AI result" },
  ).toBe(1);
  await expect(blockedHeading).toBeVisible();''',
    ),
]

for old, new in replacements:
    if source.count(old) != 1:
        raise SystemExit(f"probe patch anchor drifted: {old.splitlines()[0]}")
    source = source.replace(old, new, 1)

path.write_text(source, encoding="utf-8")
