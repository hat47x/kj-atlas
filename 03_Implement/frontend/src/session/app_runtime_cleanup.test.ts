import { describe, expect, it, vi } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { cleanupAppRuntimeResources } from "./app_runtime_cleanup";

describe("App runtime cleanup", () => {
  it("aborts requests before cancelling tasks and disposing workers", () => {
    const order: string[] = [];

    const result = cleanupAppRuntimeResources({
      abortControllers: [
        { abort: () => order.push("abort-diff") },
        { abort: () => order.push("abort-diagnostics") },
        { abort: () => order.push("abort-bundle") },
      ],
      cancelableTasks: [
        { cancel: () => order.push("cancel-bundle-runner") },
      ],
      disposableWorkers: [
        { dispose: () => order.push("dispose-diff-worker") },
        { dispose: () => order.push("dispose-diagnostics-worker") },
      ],
    });

    expect(order).toEqual([
      "abort-diff",
      "abort-diagnostics",
      "abort-bundle",
      "cancel-bundle-runner",
      "dispose-diff-worker",
      "dispose-diagnostics-worker",
    ]);
    expect(result).toEqual({ attemptedSteps: 6, failureCount: 0 });
  });

  it("continues hard-replacement cleanup when an individual resource fails", () => {
    const abortAfterFailure = vi.fn();
    const disposeAfterFailure = vi.fn();

    const result = cleanupAppRuntimeResources({
      abortControllers: [
        { abort: () => { throw new Error("controller failed"); } },
        { abort: abortAfterFailure },
        null,
      ],
      cancelableTasks: [undefined],
      disposableWorkers: [
        { dispose: disposeAfterFailure },
      ],
    });

    expect(abortAfterFailure).toHaveBeenCalledOnce();
    expect(disposeAfterFailure).toHaveBeenCalledOnce();
    expect(result).toEqual({ attemptedSteps: 3, failureCount: 1 });
  });

  it("accepts an App with no active resources", () => {
    expect(cleanupAppRuntimeResources({
      abortControllers: [null, undefined],
      cancelableTasks: [],
      disposableWorkers: [null],
    })).toEqual({ attemptedSteps: 0, failureCount: 0 });
  });

  it("remains wired to the App unmount boundary", () => {
    const appSource = readFileSync(resolve(__dirname, "..", "App.tsx"), "utf8");

    expect(appSource).toContain("diffAbortRef");
    expect(appSource).toContain("diagnosticsAbortRef");
    expect(appSource).toContain("bundleAbortRef");
  });
});
