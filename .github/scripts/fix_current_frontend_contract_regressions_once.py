from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected exactly one replacement target, found {text.count(old)}")
    path.write_text(text.replace(old, new), encoding="utf-8")


panel = Path("03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx")
replace_once(
    panel,
    'import { getActiveLocale, t } from "../i18n/translate";\n',
    'import { getActiveLocale, t } from "../i18n/translate";\n'
    'import { mergeMethodFieldLabel, mergeMethodLabel } from "./merge_method_label";\n',
)
replace_once(
    panel,
    '        const isApplied = isApplicableDecision && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");\n'
    '        return (\n',
    '        const isApplied = isApplicableDecision && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");\n'
    '        const mergeMethodLocale = getActiveLocale() === "ja" ? "ja" : "en";\n'
    '        return (\n',
)
replace_once(
    panel,
    '          </div>\n'
    '          <ul style={{ margin: "0 0 8px", paddingLeft: 18 }}>\n',
    '          </div>\n'
    '          <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>\n'
    '            {mergeMethodFieldLabel(mergeMethodLocale)}: {mergeMethodLabel(suggestion.mergeMethod, mergeMethodLocale)}\n'
    '          </div>\n'
    '          <ul style={{ margin: "0 0 8px", paddingLeft: 18 }}>\n',
)

client_test = Path("03_Implement/frontend/src/api/client.test.ts")
replace_once(
    client_test,
    'const APP_MODULE_PATH = "App.tsx";\n'
    'const OAUTH_CALLBACK_MODULE_PATH = "session/oauth_callback.ts";\n',
    'const APP_MODULE_PATH = "App.tsx";\n'
    'const ADMIN_MODEL_ALLOWLIST_MODULE_PATH = "admin/model_allowlist_api.ts";\n'
    'const OAUTH_CALLBACK_MODULE_PATH = "session/oauth_callback.ts";\n',
)
replace_once(
    client_test,
    '  it("keeps every backend request inside the shared api client module", () => {\n',
    '  it("classifies every frontend fetch surface by its trust boundary", () => {\n',
)
replace_once(
    client_test,
    '    expect([...modulesWithFetch].sort()).toEqual([\n'
    '      APP_MODULE_PATH,\n'
    '      CLIENT_MODULE_PATH,\n'
    '      OAUTH_CALLBACK_MODULE_PATH,\n'
    '    ]);\n',
    '    expect([...modulesWithFetch].sort()).toEqual([\n'
    '      APP_MODULE_PATH,\n'
    '      ADMIN_MODEL_ALLOWLIST_MODULE_PATH,\n'
    '      CLIENT_MODULE_PATH,\n'
    '      OAUTH_CALLBACK_MODULE_PATH,\n'
    '    ]);\n',
)
replace_once(
    client_test,
    '    // OAuth code exchange targets the separately configured identity broker,\n'
    '    // before a tenant session exists. It must never address the application API.\n',
    '    // The model allowlist console is a separate control-plane surface. It does\n'
    '    // not carry the business-plane tenant-session version: tenant identity is\n'
    '    // explicit in the admin route and mutations use the control-plane CSRF/auth\n'
    '    // headers. Keep this exception narrow and mechanically bound to that route.\n'
    '    for (const site of fetchCallSites(readFrontendModule(ADMIN_MODEL_ALLOWLIST_MODULE_PATH))) {\n'
    '      const { url, init } = splitRequestArguments(site.args);\n'
    '      expect(url).toContain("API_BASE");\n'
    '      expect(url).toContain("/admin/provision/models/tenants/");\n'
    '      expect(url).toContain("/allowlist");\n'
    '      expect(init).toContain("controlPlaneHeaders");\n'
    '      expect(init).toContain(\'credentials: "same-origin"\');\n'
    '      expect(init).not.toContain("tenantSessionPreconditionHeaders");\n'
    '    }\n'
    '\n'
    '    // OAuth code exchange targets the separately configured identity broker,\n'
    '    // before a tenant session exists. It must never address the application API.\n',
)

print("patched MergeSuggestionsPanel.tsx and client.test.ts")
