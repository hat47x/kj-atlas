from __future__ import annotations

from pathlib import Path

PANEL = Path("03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx")
CLIENT_TEST = Path("03_Implement/frontend/src/api/client.test.ts")
DONE_MEMO = Path("01_Plans/issues/done/issue-FE-CONTRACT-REGRESSION-01-fresh-npm-suite-drift.md")


def replace_once(path: Path, before: str, after: str) -> None:
    body = path.read_text(encoding="utf-8")
    if body.count(before) != 1:
        raise SystemExit(f"exact replacement boundary is not unique: {path}: {before[:80]!r}")
    path.write_text(body.replace(before, after, 1), encoding="utf-8")


def patch_merge_method_display() -> None:
    replace_once(
        PANEL,
        'import { getActiveLocale, t } from "../i18n/translate";\n',
        'import { getActiveLocale, t } from "../i18n/translate";\n'
        'import { mergeMethodFieldLabel, mergeMethodLabel } from "./merge_method_label";\n',
    )
    replace_once(
        PANEL,
        '        const isApplied = isApplicableDecision && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");\n'
        '        return (\n',
        '        const isApplied = isApplicableDecision && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");\n'
        '        const mergeMethodLocale = getActiveLocale() === "ja" ? "ja" : "en";\n'
        '        return (\n',
    )
    replace_once(
        PANEL,
        '          </div>\n'
        '          {suggestion.rationale ? (\n'
        '            <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>{t("merge_suggestions.rationale")}: {suggestion.rationale}</div>\n'
        '          ) : null}\n',
        '          </div>\n'
        '          <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>\n'
        '            {mergeMethodFieldLabel(mergeMethodLocale)}: {mergeMethodLabel(suggestion.mergeMethod, mergeMethodLocale)}\n'
        '          </div>\n'
        '          {suggestion.rationale ? (\n'
        '            <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>{t("merge_suggestions.rationale")}: {suggestion.rationale}</div>\n'
        '          ) : null}\n',
    )


def patch_transport_guard() -> None:
    replace_once(
        CLIENT_TEST,
        'const APP_MODULE_PATH = "App.tsx";\nconst OAUTH_CALLBACK_MODULE_PATH = "session/oauth_callback.ts";\n',
        'const APP_MODULE_PATH = "App.tsx";\n'
        'const ADMIN_MODEL_ALLOWLIST_MODULE_PATH = "admin/model_allowlist_api.ts";\n'
        'const OAUTH_CALLBACK_MODULE_PATH = "session/oauth_callback.ts";\n',
    )
    replace_once(
        CLIENT_TEST,
        '  it("keeps every backend request inside the shared api client module", () => {\n',
        '  it("keeps every backend request inside an explicitly reviewed transport module", () => {\n',
    )
    replace_once(
        CLIENT_TEST,
        '    expect([...modulesWithFetch].sort()).toEqual([\n'
        '      APP_MODULE_PATH,\n'
        '      CLIENT_MODULE_PATH,\n'
        '      OAUTH_CALLBACK_MODULE_PATH,\n'
        '    ]);\n',
        '    expect([...modulesWithFetch].sort()).toEqual([\n'
        '      ADMIN_MODEL_ALLOWLIST_MODULE_PATH,\n'
        '      APP_MODULE_PATH,\n'
        '      CLIENT_MODULE_PATH,\n'
        '      OAUTH_CALLBACK_MODULE_PATH,\n'
        '    ].sort());\n',
    )
    replace_once(
        CLIENT_TEST,
        '    // OAuth code exchange targets the separately configured identity broker,\n'
        '    // before a tenant session exists. It must never address the application API.\n'
        '    for (const site of fetchCallSites(readFrontendModule(OAUTH_CALLBACK_MODULE_PATH))) {\n'
        '      const { url } = splitRequestArguments(site.args);\n'
        '      expect(url).toContain("brokerBase");\n'
        '      expect(url).not.toContain("API_BASE");\n'
        '    }\n'
        '  });\n',
        '    // OAuth code exchange targets the separately configured identity broker,\n'
        '    // before a tenant session exists. It must never address the application API.\n'
        '    for (const site of fetchCallSites(readFrontendModule(OAUTH_CALLBACK_MODULE_PATH))) {\n'
        '      const { url } = splitRequestArguments(site.args);\n'
        '      expect(url).toContain("brokerBase");\n'
        '      expect(url).not.toContain("API_BASE");\n'
        '    }\n'
        '\n'
        '    // The model allowlist console is a deliberately separate control-plane entry\n'
        '    // (admin.html). Its transport must stay confined to the reviewed admin\n'
        '    // provisioning namespace and same-origin credential boundary rather than\n'
        '    // silently becoming a second business-plane tenant-scoped client.\n'
        '    for (const site of fetchCallSites(readFrontendModule(ADMIN_MODEL_ALLOWLIST_MODULE_PATH))) {\n'
        '      const { url, init } = splitRequestArguments(site.args);\n'
        '      expect(url).toContain("${API_BASE}/admin/provision/models/tenants/");\n'
        '      expect(init).toContain(\'credentials: "same-origin"\');\n'
        '      expect(init).not.toContain("tenantSessionPreconditionHeaders");\n'
        '    }\n'
        '  });\n',
    )


def write_done_memo() -> None:
    if DONE_MEMO.exists():
        raise SystemExit(f"done memo already exists: {DONE_MEMO}")
    DONE_MEMO.write_text(
        """# Issue: FE-CONTRACT-REGRESSION-01 fresh npm suiteで露出したfrontend transport/mergeMethod契約ドリフト

- Type: QA
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/api/client.test.ts`, `03_Implement/frontend/src/admin/model_allowlist_api.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`
- Related ADR/Spec: N/A
- Expected verification level: frontend unit + build + planning checks

## 課題

2026-09-05、`DX-CI-PNPM-01` / `DX-ENV-01` のstale性をfresh checkout + `npm ci` で検証したところ、pnpm混在とは無関係なfrontend full unit suiteの失敗を3件検出した。

1. `src/api/client.test.ts` の静的transport inventoryが、PR #2898で意図的に導入された独立control-plane consoleの `admin/model_allowlist_api.ts` を未分類のbackend fetchとして拒否した。
2. `MergeSuggestionsPanel.merge_method.test.ts` の2件が、`mergeMethod` の日本語/英語表示消失を検出した。`merge_method_label.ts` と固定テストは残っていたが、panel側のimport・locale解決・表示行が失われていた。

## 判断

### Admin transport

PR #2898は `admin.html` を主キャンバスから分離し、business-plane credentialへcontrol-plane権限を広げない独立consoleとして実装している。そのためadmin requestを `api/client.ts` へ無条件に吸収するのではなく、静的inventoryへ **明示的なreviewed transport** として登録する。

同時に、admin transportのfetchが以下を満たすことを静的に固定する。

- `${API_BASE}/admin/provision/models/tenants/...` 名前空間に限定される。
- `credentials: \"same-origin\"` を維持する。
- business-planeの `tenantSessionPreconditionHeaders` を暗黙に流用しない。

### mergeMethod表示

`mergeMethod` はbackend contract・frontend parser・label helper・既存regression testで保持されている。表示assertionを削るのではなく、`0f693a...` で固定されていた方式表示を現行partial-accept UIへ復元する。

## Acceptance

- [x] admin control-plane transportがstatic fetch inventoryで未分類にならず、admin provisioning namespace / same-origin境界を検証される。
- [x] `MergeSuggestionsPanel` が `near_duplicate` / `kernel_fusion` をrationaleとは別フィールドとして日本語・英語で再表示する。
- [x] fresh `npm ci` 後のfrontend full unit suiteがpassする。
- [x] frontend production buildがpassする。
- [x] planning lifecycle / docs / triage / stale reintroduction / diff checksがpassする。

## 境界

- admin consoleをbusiness-planeのtenant-session clientへ統合しない。
- `mergeMethod` のbackend/API/schema値は変更しない。
- `DX-CI-TEST-01` のrepo外fixture依存問題は別Issueとしてactiveのまま扱う。
- pnpm/npmローカル混在の整理は、本回帰修復の成功後に別PRで再検証して閉じる。
""",
        encoding="utf-8",
    )


def main() -> None:
    patch_merge_method_display()
    patch_transport_guard()
    write_done_memo()


if __name__ == "__main__":
    main()
