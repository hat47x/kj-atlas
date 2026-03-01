import { describe, expect, it, vi } from "vitest";
import { installNetworkLeakMonitor, runLocaleConversionWithGuard, type GuardLogEvent } from "./locale_conversion_guard";

describe("locale conversion guard", () => {
  it("blocks safe-mode conversions and prevents fetch/xhr/worker leakage even when telemetry and audit are enabled", async () => {
    const monitor = installNetworkLeakMonitor();
    const logs: GuardLogEvent[] = [];

    const adapter = vi.fn(async () => {
      await globalThis.fetch("https://leak.invalid/fetch");
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "https://leak.invalid/xhr");
      // eslint-disable-next-line no-new
      new Worker("https://leak.invalid/worker.js");
      return "translated";
    });

    const telemetryDispatch = vi.fn(async () => {
      await globalThis.fetch("https://leak.invalid/telemetry");
    });
    const auditDispatch = vi.fn(async () => {
      await globalThis.fetch("https://leak.invalid/audit");
    });

    try {
      const result = await runLocaleConversionWithGuard({
        text: "機微情報: 顧客名 Alice",
        sourceLocale: "ja",
        targetLocale: "en",
        safeMode: true,
        telemetryEnabled: true,
        auditEnabled: true,
        adapter,
        telemetryDispatch,
        auditDispatch,
        logger: (event) => logs.push(event),
      });

      expect(result).toEqual({ status: "blocked", translatedText: "機微情報: 顧客名 Alice", reason: "safe_mode" });
      expect(adapter).not.toHaveBeenCalled();
      expect(telemetryDispatch).not.toHaveBeenCalled();
      expect(auditDispatch).not.toHaveBeenCalled();
      expect(monitor.attempts).toEqual([]);

      expect(logs).toHaveLength(1);
      expect(logs[0]?.code).toBe("translation.safe_mode_blocked");
      expect(logs[0]?.textDigest).toContain("[REDACTED]:");
      expect(JSON.stringify(logs)).not.toContain("Alice");
    } finally {
      monitor.restore();
    }
  });

  it("fails safe when telemetry dispatch violates policy", async () => {
    const adapter = vi.fn(async () => "translated");
    const telemetryDispatch = vi.fn(async () => {
      throw new Error("telemetry endpoint rejected");
    });
    const auditDispatch = vi.fn(async () => Promise.resolve());

    const result = await runLocaleConversionWithGuard({
      text: "個人情報 Bob",
      sourceLocale: "ja",
      targetLocale: "en",
      safeMode: false,
      telemetryEnabled: true,
      auditEnabled: true,
      adapter,
      telemetryDispatch,
      auditDispatch,
    });

    expect(result).toEqual({ status: "blocked", translatedText: "個人情報 Bob", reason: "fail_safe_dispatch" });
    expect(adapter).not.toHaveBeenCalled();
    expect(auditDispatch).not.toHaveBeenCalled();
  });

  it("keeps timeout logs and output redacted without leaking source text", async () => {
    const logs: GuardLogEvent[] = [];
    const sensitiveText = "顧客メール alice@example.com";
    const adapter = vi.fn(async ({ signal }: { signal: AbortSignal }) => {
      await new Promise<void>((resolve, reject) => {
        const timeoutId = setTimeout(resolve, 50);
        signal.addEventListener("abort", () => {
          clearTimeout(timeoutId);
          reject(new Error("aborted"));
        });
      });
      return "translated";
    });

    const result = await runLocaleConversionWithGuard({
      text: sensitiveText,
      sourceLocale: "ja",
      targetLocale: "en",
      safeMode: false,
      telemetryEnabled: false,
      auditEnabled: false,
      timeoutMs: 5,
      adapter,
      logger: (event) => logs.push(event),
    });

    expect(result.status).toBe("timeout");
    expect(result.translatedText).toContain("[REDACTED]");
    expect(result.translatedText).not.toContain("alice@example.com");
    expect(logs[0]?.code).toBe("translation.timeout");
    expect(logs[0]?.textDigest).toContain("[REDACTED]:");
    expect(JSON.stringify(logs)).not.toContain("alice@example.com");
  });

  it("keeps adapter error logs redacted and marks adapter_error status", async () => {
    const logs: GuardLogEvent[] = [];
    const adapter = vi.fn(async () => {
      throw new Error("adapter failure");
    });

    const result = await runLocaleConversionWithGuard({
      text: "社外秘: project-x",
      sourceLocale: "ja",
      targetLocale: "en",
      safeMode: false,
      telemetryEnabled: false,
      auditEnabled: false,
      adapter,
      logger: (event) => logs.push(event),
    });

    expect(result).toEqual({ status: "adapter_error", translatedText: "[REDACTED] (len:14)" });
    expect(logs[0]?.code).toBe("translation.adapter_error");
    expect(JSON.stringify(logs)).not.toContain("project-x");
  });

  it("allows normal conversion when safe mode is off and dispatches audit/telemetry with digest only", async () => {
    const telemetryDispatch = vi.fn(async () => Promise.resolve());
    const auditDispatch = vi.fn(async () => Promise.resolve());

    const result = await runLocaleConversionWithGuard({
      text: "利用者の入力テキスト",
      sourceLocale: "ja",
      targetLocale: "en",
      safeMode: false,
      telemetryEnabled: true,
      auditEnabled: true,
      adapter: async () => "translated-text",
      telemetryDispatch,
      auditDispatch,
    });

    expect(result).toEqual({ status: "success", translatedText: "translated-text" });
    expect(telemetryDispatch).toHaveBeenCalledTimes(2);
    expect(auditDispatch).toHaveBeenCalledTimes(2);

    const telemetryPayload = telemetryDispatch.mock.calls.at(0)?.at(0) as { textDigest: string } | undefined;
    expect(telemetryPayload?.textDigest).toContain("[REDACTED]:");
    expect(JSON.stringify(telemetryPayload)).not.toContain("利用者の入力テキスト");
  });
});
