import { afterEach, describe, expect, test, vi } from "vitest";
import { BundleZipWorkerClient } from "./bundle_zip_client";

const payload = {
  files: [{ path: "a.txt", content: "a", mime: "text/plain" as const }],
};

describe("BundleZipWorkerClient", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  test("logs info only once when Worker runtime is unavailable", async () => {
    vi.stubGlobal("Worker", undefined);
    const info = vi.spyOn(console, "info").mockImplementation(() => {});
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new BundleZipWorkerClient();

    await client.buildZip(payload);
    await client.buildZip(payload);

    expect(info).toHaveBeenCalledTimes(1);
    expect(warn).not.toHaveBeenCalled();
  });

  test("warns when Worker exists but initialization fails", async () => {
    vi.stubGlobal(
      "Worker",
      class {
        constructor() {
          throw new Error("unavailable");
        }
      },
    );
    const info = vi.spyOn(console, "info").mockImplementation(() => {});
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new BundleZipWorkerClient();

    await client.buildZip(payload);

    expect(warn).toHaveBeenCalledOnce();
    expect(info).not.toHaveBeenCalled();
  });
});
