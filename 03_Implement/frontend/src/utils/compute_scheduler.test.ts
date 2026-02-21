import { describe, expect, it, vi } from "vitest";
import { createCancelableTaskRunner } from "./compute_scheduler";

describe("createCancelableTaskRunner", () => {
  it("yields back to main thread between chunks", async () => {
    const runner = createCancelableTaskRunner();
    const steps: string[] = [];

    const result = await runner.run(async (ctx) => {
      steps.push("start");
      await ctx.yieldToMainThread();
      steps.push("after-yield");
      return 42;
    });

    expect(result).toEqual({ status: "completed", result: 42 });
    expect(steps).toEqual(["start", "after-yield"]);
  });

  it("returns cancelled state", async () => {
    const runner = createCancelableTaskRunner();

    const runPromise = runner.run(async (ctx) => {
      await ctx.yieldToMainThread();
      return "done";
    });

    runner.cancel();
    await expect(runPromise).resolves.toEqual({ status: "cancelled" });
  });

  it("emits deterministic progress updates", async () => {
    const runner = createCancelableTaskRunner();
    const spy = vi.fn();
    runner.onProgress(spy);

    await runner.run(async (ctx) => {
      ctx.reportProgress({ message: "Step 1", completed: 1, total: 2 });
      ctx.reportProgress({ message: "Step 2", completed: 2, total: 2 });
      return true;
    });

    expect(spy).toHaveBeenCalledTimes(2);
    expect(spy).toHaveBeenNthCalledWith(1, { message: "Step 1", completed: 1, total: 2 });
    expect(spy).toHaveBeenNthCalledWith(2, { message: "Step 2", completed: 2, total: 2 });
  });
});
