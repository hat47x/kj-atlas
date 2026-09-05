from __future__ import annotations

from pathlib import Path
import subprocess

SPEC = Path("03_Implement/frontend/e2e/tenant_session_multitab.spec.ts")
ISSUE = Path("01_Plans/issues/issue-QA-E2E-SAAS-01-tenant-session-coverage-gap.md")
DONE = Path("01_Plans/issues/done/issue-QA-E2E-SAAS-01-tenant-session-coverage-gap.md")
SCRIPT = Path(".github/scripts/lane_c_add_saas_tenant_storage_ui_e2e_once.py")

DOCS_ROUTE_ANCHOR = '''    if (url.pathname === "/api/ai/provider-status") {
      await fulfillJson(route, 200, { providerKind: "none" });
      return;
    }
    if (url.pathname === "/api/docs/doc_phase1_canvas") {
'''
DOCS_ROUTE_REPLACEMENT = '''    if (url.pathname === "/api/ai/provider-status") {
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
    if (url.pathname === "/api/docs/doc_phase1_canvas") {
'''

TEST_MARKER = 'test("tenant switch reloads recent documents and query presets from the new tenant scope"'
TEST_BLOCK = r'''

test("tenant switch reloads recent documents and query presets from the new tenant scope", async ({ browser }) => {
  const state = createServerState();
  const context = await browser.newContext();
  await context.addInitScript(() => {
    const seedMarker = "kj-atlas-e2e-tenant-storage-ui-seeded";
    if (window.sessionStorage.getItem(seedMarker) === "1") {
      return;
    }

    const principalId = "principal-1";
    const prefixFor = (tenantId: "tenant-a" | "tenant-b") => (
      `kj-atlas/tenant-scope/v1/${encodeURIComponent(window.location.origin)}/${encodeURIComponent(tenantId)}/${encodeURIComponent(principalId)}/`
    );
    const scopedKey = (tenantId: "tenant-a" | "tenant-b", baseKey: string) => (
      `${prefixFor(tenantId)}${encodeURIComponent(baseKey)}`
    );

    window.localStorage.setItem(
      scopedKey("tenant-a", "kj-atlas/recent-doc-ids"),
      JSON.stringify(["doc_tenant_a_recent"]),
    );
    window.localStorage.setItem(
      scopedKey("tenant-b", "kj-atlas/recent-doc-ids"),
      JSON.stringify(["doc_tenant_b_recent"]),
    );
    window.localStorage.setItem(
      scopedKey("tenant-a", "kj-atlas:ce3:patch-workspace-presets:v1"),
      JSON.stringify([{ id: "preset-tenant-a", name: "Tenant A preset", scope: "all", depth: 1, filters: ["alpha"] }]),
    );
    window.localStorage.setItem(
      scopedKey("tenant-b", "kj-atlas:ce3:patch-workspace-presets:v1"),
      JSON.stringify([{ id: "preset-tenant-b", name: "Tenant B preset", scope: "all", depth: 1, filters: ["beta"] }]),
    );
    window.sessionStorage.setItem(seedMarker, "1");
  });
  await installSaasServer(context, state);
  const page = await context.newPage();

  const openRecentDialog = async () => {
    await page.getByRole("menuitem", { name: "File", exact: true }).click();
    await page.getByRole("menuitem", { name: "Open recent document…" }).click();
    const dialog = page.locator('[data-ui-region="recent-documents-dialog"]');
    await expect(dialog).toBeVisible();
    return dialog;
  };

  const closeWorkMode = async () => {
    const workMode = page.locator('[data-ui-region="work-mode"]');
    if (!await workMode.isVisible().catch(() => false)) {
      return;
    }
    await page.keyboard.press("Escape");
    if (await workMode.isVisible().catch(() => false)) {
      await page.keyboard.press("Escape");
    }
    await expect(workMode).toBeHidden();
  };

  await openWorkspace(page);

  let dialog = await openRecentDialog();
  await expect(dialog.locator('option[value="doc_tenant_a_recent"]')).toHaveCount(1);
  await expect(dialog.locator('option[value="doc_tenant_b_recent"]')).toHaveCount(0);
  await dialog.getByRole("button", { name: "Close" }).click();

  await openAdvancedWorkMode(page);
  await selectWorkModeTab(page, "merge");
  const workspace = page.getByTestId("ce3-workspace-panel");
  await expect(workspace).toBeVisible();
  await expect(workspace.getByRole("button", { name: "Run Tenant A preset" })).toBeVisible();
  await expect(workspace.getByRole("button", { name: "Run Tenant B preset" })).toHaveCount(0);
  await closeWorkMode();

  await page.getByLabel("Current workspace: Tenant A").selectOption("tenant-b");
  await expect(page.getByLabel("Current workspace: Tenant B")).toBeVisible();
  await expect(page.getByRole("button", { name: "tenant-b confidential card" })).toBeVisible();

  dialog = await openRecentDialog();
  await expect(dialog.locator('option[value="doc_tenant_b_recent"]')).toHaveCount(1);
  await expect(dialog.locator('option[value="doc_tenant_a_recent"]')).toHaveCount(0);
  await dialog.getByRole("button", { name: "Close" }).click();

  await openAdvancedWorkMode(page);
  await selectWorkModeTab(page, "merge");
  await expect(workspace).toBeVisible();
  await expect(workspace.getByRole("button", { name: "Run Tenant B preset" })).toBeVisible();
  await expect(workspace.getByRole("button", { name: "Run Tenant A preset" })).toHaveCount(0);

  const tenantAStorageKeys = await page.evaluate(() => {
    const tenantPrefix = `kj-atlas/tenant-scope/v1/${encodeURIComponent(window.location.origin)}/${encodeURIComponent("tenant-a")}/${encodeURIComponent("principal-1")}/`;
    return Array.from({ length: window.localStorage.length }, (_, index) => window.localStorage.key(index))
      .filter((key): key is string => typeof key === "string" && key.startsWith(tenantPrefix));
  });
  expect(tenantAStorageKeys).toEqual([]);

  await context.close();
});
'''

COMPLETION_SECTION = '''## 2026-09-05: tenant-scoped UI残差の完了

上記で確定したbrowser lifecycle gapに対し、`tenant_session_multitab.spec.ts`へ実ブラウザscenarioを追加した。単一の認証済みsessionでtenant Aからtenant Bへ切り替える既存のproduct経路を使い、両tenantのscoped localStorageへ異なるrecent documentとQueryPresetを事前投入して、実UIが正しいscopeだけを読むことを確認する。

- [x] tenant Aでは「最近使った文書」ダイアログに`doc_tenant_a_recent`だけが現れ、tenant Bのrecent項目を表示しない。
- [x] tenant AではQueryPreset panelに`Tenant A preset`だけが現れ、tenant Bのpresetを表示しない。
- [x] tenant A→B切替後のhard reloadで、recent dialogは`doc_tenant_b_recent`を表示し、tenant Aのrecent項目を表示しない。
- [x] 同じ切替後にQueryPreset panelは`Tenant B preset`を表示し、tenant Aのpresetを表示しない。
- [x] transition後、旧tenant Aの`kj-atlas/tenant-scope/v1/...` localStorage keyが残っていないことも同じbrowser scenarioで確認する。

初期seedは`sessionStorage` markerで一度だけ投入する。tenant切替のhard reload時には再seedしないため、`executeTenantSessionTransition()`が旧scopeを消去してから新scopeでAppを再bootstrapする実際の契約を迂回しない。`/api/docs`だけは既存`ServerState`に現在tenantの一覧応答を追加し、recent dialogのserver-side canvas listも決定的に保つ。

このscenarioはmock APIを用いるbrowser lifecycle層の証拠であり、実Broker / PostgreSQL / 複数backend workerの認証縦断証拠は引き続きDoneの`AUTH-ONE-TIME-JWT-01`を正本とする。AI generation guardの機構固有証拠もDoneの`SAAS-TENANT-E2E-01`を正本とし、責務を重複させない。

本Issueが2026-09-05再棚卸しで確定した唯一のbrowser側残差を閉じたため、Issueを`Done`とする。

'''


def replace_once(body: str, old: str, new: str, label: str) -> str:
    if body.count(old) != 1:
        raise SystemExit(f"{label} anchor count={body.count(old)}")
    return body.replace(old, new, 1)


def update_exact_references(old: Path, new: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "grep", "-Il", "-F", old.as_posix(), "--", f":!{SCRIPT.as_posix()}", f":!{new.as_posix()}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        raise SystemExit(completed.stderr.strip() or "git grep failed")
    updated: list[str] = []
    for filename in [line for line in completed.stdout.splitlines() if line]:
        path = Path(filename)
        body = path.read_text(encoding="utf-8")
        replaced = body.replace(old.as_posix(), new.as_posix())
        if replaced == body:
            raise SystemExit(f"reference replacement missed: {filename}")
        path.write_text(replaced, encoding="utf-8")
        updated.append(filename)
    return updated


def main() -> None:
    spec = SPEC.read_text(encoding="utf-8")
    if TEST_MARKER in spec:
        raise SystemExit("tenant storage UI E2E already exists")
    spec = replace_once(spec, DOCS_ROUTE_ANCHOR, DOCS_ROUTE_REPLACEMENT, "docs route")
    SPEC.write_text(spec.rstrip() + TEST_BLOCK + "\n", encoding="utf-8")

    if DONE.exists():
        raise SystemExit(f"done issue already exists: {DONE}")
    issue = ISSUE.read_text(encoding="utf-8")
    issue = replace_once(issue, "- Status: Draft", "- Status: Done", "issue status")
    issue = replace_once(issue, "## 補足\n", COMPLETION_SECTION + "## 補足\n", "completion section")
    ISSUE.write_text(issue, encoding="utf-8")
    subprocess.run(["git", "mv", ISSUE.as_posix(), DONE.as_posix()], check=True)

    refs = update_exact_references(ISSUE, DONE)
    print(f"updated issue references={len(refs)}")
    for ref in refs:
        print(f"  - {ref}")


if __name__ == "__main__":
    main()
