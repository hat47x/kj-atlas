import { describe, expect, it } from "vitest";

import {
  StaleTenantSessionResultError,
  TenantSessionGenerationGuard,
} from "./tenant_session_generation";

function deferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
} {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((resolvePromise) => {
    resolve = resolvePromise;
  });
  return { promise, resolve };
}

describe("TenantSessionGenerationGuard", () => {
  it("returns a result while the tenant generation remains current", async () => {
    const guard = new TenantSessionGenerationGuard();

    await expect(guard.run(async () => "current-result")).resolves.toBe("current-result");
  });

  it("rejects a delayed successful result after runtime invalidation", async () => {
    const guard = new TenantSessionGenerationGuard();
    const pending = deferred<string>();
    const result = guard.run(() => pending.promise);

    guard.invalidate();
    pending.resolve("stale-tenant-content");

    await expect(result).rejects.toBeInstanceOf(StaleTenantSessionResultError);
  });

  it("does not expose a stale result through a later generation", async () => {
    const guard = new TenantSessionGenerationGuard();
    const first = deferred<string>();
    const staleResult = guard.run(() => first.promise);

    guard.invalidate();
    await expect(guard.run(async () => "new-generation-result")).resolves.toBe(
      "new-generation-result",
    );
    first.resolve("old-generation-result");

    await expect(staleResult).rejects.toBeInstanceOf(StaleTenantSessionResultError);
  });
});
