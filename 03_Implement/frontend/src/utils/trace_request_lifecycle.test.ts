import { describe, expect, it, vi } from "vitest";

import { runTraceRequest } from "./trace_request_lifecycle";


describe("trace request lifecycle", () => {
  it("returns a successful result and always settles", async () => {
    const onRejected = vi.fn();
    const onSettled = vi.fn();

    await expect(runTraceRequest({
      execute: async () => "trace markdown",
      onRejected,
      onSettled,
    })).resolves.toBe("trace markdown");

    expect(onRejected).not.toHaveBeenCalled();
    expect(onSettled).toHaveBeenCalledOnce();
  });

  it("normalizes rejection to null and settles controls for retry", async () => {
    const onRejected = vi.fn();
    const onSettled = vi.fn();

    await expect(runTraceRequest({
      execute: async () => {
        throw new Error("worker-internal-secret");
      },
      onRejected,
      onSettled,
    })).resolves.toBeNull();

    expect(onRejected).toHaveBeenCalledOnce();
    expect(onRejected).toHaveBeenCalledWith();
    expect(onSettled).toHaveBeenCalledOnce();
  });
});
