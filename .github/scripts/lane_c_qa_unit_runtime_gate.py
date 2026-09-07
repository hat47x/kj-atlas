from pathlib import Path

ISSUE = Path("01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md")
TEST = Path("03_Implement/frontend/src/ui/TenantSessionRuntimeGate.test.ts")
MARKER = "## 2026-09-07 Open化同期 / 第2バッチ再開"

issue = ISSUE.read_text(encoding="utf-8")
if issue.count("- Status: Draft\n") != 1:
    raise SystemExit("expected exactly one Draft status in QA-UNIT-01")
if MARKER in issue:
    raise SystemExit("QA-UNIT-01 second-batch checkpoint already exists")

old_scope = "- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`（Phase 1〜6の計画文書更新）。2026-07-18の実行計画節以降は、初回実行バッチとして`03_Implement/frontend/src/domain/view/hierarchy_level.ts`・同`.test.ts`・`App.tsx`（QA-MONKEY-13再発検知テストの追加とその可読化リファクタ）も対象に含む。\n"
new_scope = "- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`、初回実行バッチの`03_Implement/frontend/src/domain/view/hierarchy_level.ts`・同`.test.ts`・`App.tsx`、および2026-09-07第2バッチの`03_Implement/frontend/src/ui/TenantSessionRuntimeGate.test.ts`・`03_Implement/frontend/package.json`・`package-lock.json`。\n"
old_out = "- Out of Scope: CI設定変更。実装コード変更・テストコード追加は、2026-07-18の実行計画節が承認した初回実行バッチの範囲でのみ許可する（それ以外の無制限な実装変更は引き続き対象外）。\n"
new_out = "- Out of Scope: CI設定変更、Vitest全体の`node`環境変更、テスト都合の製品挙動変更。第2バッチでは対象test fileだけにDOM環境を与え、`TenantSessionRuntimeGate.tsx`本体は変更しない。\n"
if old_scope not in issue or old_out not in issue:
    raise SystemExit("QA-UNIT-01 scope baseline drifted")
issue = issue.replace("- Status: Draft\n", "- Status: Open\n", 1)
issue = issue.replace(old_scope, new_scope, 1).replace(old_out, new_out, 1)
checkpoint = r'''
## 2026-09-07 Open化同期 / 第2バッチ再開

2026-07-16〜18にPending-1/2とB-UNIT-03は解消済みで、初回バッチも2026-07-18に実装・検証済みである一方、headerだけが`Status: Draft`に残っていたため、歴史節のDraft/Hold判定を改変せず現在状態を`Open`へ同期する。

2026-07-19の第2バッチで停止した理由は、`TenantSessionRuntimeGate`の中心的な状態遷移がReactのcommit/effectを必要とするのに、既存unit suiteがglobal `environment: "node"`＋SSR中心で、実componentを再レンダリングする局所harnessを持たなかったことだった。今回、この停止条件を次の最小境界で解除する。

- globalのVitest `environment: "node"` は変更しない。
- `TenantSessionRuntimeGate.test.ts`だけをVitestのfile-local environmentで`happy-dom`へ切り替える。
- Testing Library等の追加抽象層は導入せず、React 18の`createRoot`＋`act`で実componentをmountする。
- 製品側`TenantSessionRuntimeGate.tsx`をテスト都合で純関数化・分岐抽出しない。
- `policyVerified=false`のblocked表示、`true`の`TenantSessionBootstrapGate` hand-off、Retryによるpolicy再検証を実effect/state遷移として固定する。

### 判定境界

この変更は、2026-07-19に明記した**特定のtest-harness blockerを解消し、第2バッチの欠陥検知能力を増やすもの**である。QA-UNIT-01全体をDoneとはしない。今後も欠陥クラス基準で追加候補を選び、DOM環境を全testへ拡張することや、coverage率そのものを目的化することはしない。

依存追加はNode 20（repository `.nvmrc`）でengine-strict installが成立する版に固定し、対象test、frontend全suite、typecheck、planning/docs guardsが同一runでgreenになった場合だけmainline候補とする。
'''
ISSUE.write_text(issue.rstrip() + "\n\n" + checkpoint.strip() + "\n", encoding="utf-8")

TEST.write_text(r'''// @vitest-environment happy-dom

import React, { act } from "react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRoot, type Root } from "react-dom/client";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import { TenantSessionRuntimeGate } from "./TenantSessionRuntimeGate";

const roots: Root[] = [];
const actGlobal = globalThis as typeof globalThis & {
  IS_REACT_ACT_ENVIRONMENT?: boolean;
};
actGlobal.IS_REACT_ACT_ENVIRONMENT = true;

async function flushReactWork(): Promise<void> {
  await Promise.resolve();
  await Promise.resolve();
}

async function mountRuntimeGate(
  props: Parameters<typeof TenantSessionRuntimeGate>[0],
): Promise<HTMLElement> {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  roots.push(root);
  await act(async () => {
    root.render(React.createElement(TenantSessionRuntimeGate, props));
    await flushReactWork();
  });
  return container;
}

afterEach(async () => {
  while (roots.length > 0) {
    const root = roots.pop();
    if (root) {
      await act(async () => root.unmount());
    }
  }
  document.body.replaceChildren();
  vi.restoreAllMocks();
});

afterAll(() => {
  delete actGlobal.IS_REACT_ACT_ENVIRONMENT;
});

describe("tenant session runtime gate", () => {
  it("starts with no tenant App content mounted while policy verification is pending", async () => {
    const renderApp = vi.fn();
    const container = await mountRuntimeGate({
      deployment: "https://atlas.example.test",
      loadPolicy: async () => new Promise(() => undefined),
      renderApp,
    });

    expect(container.querySelector('[role="status"]')).not.toBeNull();
    expect(container.querySelector('[aria-busy="true"]')).not.toBeNull();
    expect(renderApp).not.toHaveBeenCalled();
  });

  it("blocks when runtime policy does not require a tenant session", async () => {
    const renderApp = vi.fn();
    const container = await mountRuntimeGate({
      deployment: "https://atlas.example.test",
      loadPolicy: async () => ({ tenantSessionMode: "single-tenant" }),
      renderApp,
    });

    expect(container.querySelector('[role="alert"]')).not.toBeNull();
    expect(container.querySelector("button")).not.toBeNull();
    expect(renderApp).not.toHaveBeenCalled();
  });

  it("hands verified runtime policy to tenant session bootstrap and mounts scoped App", async () => {
    const renderApp = vi.fn(() => React.createElement(
      "div",
      { "data-testid": "tenant-app" },
      "ready",
    ));
    const loadSessionContext = vi.fn(async () => ({
      principalId: "user-1",
      activeTenant: { id: "tenant-1", displayName: "Tenant One" },
      availableTenants: [{ id: "tenant-1", displayName: "Tenant One" }],
      effectiveCapabilities: ["document.read"],
      capabilityVersion: "v1",
      tenantSessionVersion: "v1",
    }));
    const container = await mountRuntimeGate({
      deployment: "https://atlas.example.test",
      loadPolicy: async () => ({ tenantSessionMode: "tenant-session-required" }),
      loadSessionContext,
      renderApp,
    });

    expect(loadSessionContext).toHaveBeenCalledTimes(1);
    expect(renderApp).toHaveBeenCalledTimes(1);
    expect(container.querySelector('[data-testid="tenant-app"]')?.textContent).toBe("ready");
  });

  it("retries runtime policy verification and can recover from blocked to ready", async () => {
    const loadPolicy = vi.fn()
      .mockResolvedValueOnce({ tenantSessionMode: "single-tenant" })
      .mockResolvedValueOnce({ tenantSessionMode: "tenant-session-required" });
    const loadSessionContext = vi.fn(async () => ({
      principalId: "user-1",
      activeTenant: { id: "tenant-1", displayName: "Tenant One" },
      availableTenants: [{ id: "tenant-1", displayName: "Tenant One" }],
      effectiveCapabilities: ["document.read"],
      capabilityVersion: "v1",
      tenantSessionVersion: "v1",
    }));
    const renderApp = vi.fn(() => React.createElement("div", null, "ready after retry"));
    const container = await mountRuntimeGate({
      deployment: "https://atlas.example.test",
      loadPolicy,
      loadSessionContext,
      renderApp,
    });

    const retry = container.querySelector("button");
    expect(retry).not.toBeNull();
    await act(async () => {
      retry?.click();
      await flushReactWork();
    });

    expect(loadPolicy).toHaveBeenCalledTimes(2);
    expect(loadSessionContext).toHaveBeenCalledTimes(1);
    expect(renderApp).toHaveBeenCalledTimes(1);
    expect(container.textContent).toContain("ready after retry");
  });

  it("remains wired to the production entry point and scoped App", () => {
    const mainSource = readFileSync(resolve(__dirname, "..", "main.tsx"), "utf8");

    expect(mainSource).toContain("resolveRuntimeEntryMode");
    expect(mainSource).toContain('runtimeEntryMode === "tenant-session-required"');
    expect(mainSource).toContain("<TenantSessionRuntimeGate");
    expect(mainSource).toContain("storageScope={result.storageScope}");
    expect(mainSource).toContain("tenantSessionContext={result.sessionContext}");
    expect(mainSource).toContain('runtimeEntryMode === "invalid"');
  });
});
''', encoding="utf-8")

print("staged QA-UNIT-01 Open sync and TenantSessionRuntimeGate state-transition tests")
