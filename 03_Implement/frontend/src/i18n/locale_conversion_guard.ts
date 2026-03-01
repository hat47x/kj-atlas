import { SafeModePolicy } from "../domain/policy/safe_mode";

export type NetworkChannel = "fetch" | "xhr" | "worker";

export type TranslationAdapter = (input: {
  text: string;
  sourceLocale: string;
  targetLocale: string;
  signal: AbortSignal;
}) => Promise<string>;

export type GuardLogEvent = {
  level: "info" | "warn" | "error";
  code:
    | "translation.safe_mode_blocked"
    | "translation.timeout"
    | "translation.adapter_error"
    | "translation.audit_failed"
    | "translation.telemetry_failed";
  textDigest: string;
  sourceLocale: string;
  targetLocale: string;
  detail?: string;
};

export type GuardDispatch = (payload: {
  event: "translation_attempt" | "translation_completed" | "translation_failed";
  safeMode: boolean;
  sourceLocale: string;
  targetLocale: string;
  textDigest: string;
}) => Promise<void>;

export type LocaleConversionGuardInput = {
  text: string;
  sourceLocale: string;
  targetLocale: string;
  safeMode: boolean;
  telemetryEnabled: boolean;
  auditEnabled: boolean;
  timeoutMs?: number;
  adapter: TranslationAdapter;
  telemetryDispatch?: GuardDispatch;
  auditDispatch?: GuardDispatch;
  logger?: (event: GuardLogEvent) => void;
};

export type LocaleConversionGuardResult =
  | { status: "blocked"; translatedText: string; reason: "safe_mode" | "fail_safe_dispatch" }
  | { status: "success"; translatedText: string }
  | { status: "timeout"; translatedText: string }
  | { status: "adapter_error"; translatedText: string };

export async function runLocaleConversionWithGuard(input: LocaleConversionGuardInput): Promise<LocaleConversionGuardResult> {
  const textDigest = SafeModePolicy.summarizeForSafeMode(input.text);

  if (input.safeMode) {
    input.logger?.({
      level: "warn",
      code: "translation.safe_mode_blocked",
      textDigest,
      sourceLocale: input.sourceLocale,
      targetLocale: input.targetLocale,
      detail: "external translation is blocked while safe mode is enabled",
    });
    return { status: "blocked", translatedText: input.text, reason: "safe_mode" };
  }

  const timeoutMs = Math.max(1, input.timeoutMs ?? 3_000);
  const timeoutController = new AbortController();
  const timeoutId = setTimeout(() => {
    timeoutController.abort();
  }, timeoutMs);

  const dispatchPayload = {
    safeMode: input.safeMode,
    sourceLocale: input.sourceLocale,
    targetLocale: input.targetLocale,
    textDigest,
  };

  if (input.telemetryEnabled) {
    try {
      await input.telemetryDispatch?.({ event: "translation_attempt", ...dispatchPayload });
    } catch {
      input.logger?.({
        level: "warn",
        code: "translation.telemetry_failed",
        textDigest,
        sourceLocale: input.sourceLocale,
        targetLocale: input.targetLocale,
      });
      return { status: "blocked", translatedText: input.text, reason: "fail_safe_dispatch" };
    }
  }

  if (input.auditEnabled) {
    try {
      await input.auditDispatch?.({ event: "translation_attempt", ...dispatchPayload });
    } catch {
      input.logger?.({
        level: "warn",
        code: "translation.audit_failed",
        textDigest,
        sourceLocale: input.sourceLocale,
        targetLocale: input.targetLocale,
      });
      return { status: "blocked", translatedText: input.text, reason: "fail_safe_dispatch" };
    }
  }

  try {
    const translatedText = await input.adapter({
      text: input.text,
      sourceLocale: input.sourceLocale,
      targetLocale: input.targetLocale,
      signal: timeoutController.signal,
    });

    if (input.telemetryEnabled) {
      await input.telemetryDispatch?.({ event: "translation_completed", ...dispatchPayload });
    }
    if (input.auditEnabled) {
      await input.auditDispatch?.({ event: "translation_completed", ...dispatchPayload });
    }

    return { status: "success", translatedText };
  } catch (error) {
    const isTimeout = timeoutController.signal.aborted;
    input.logger?.({
      level: "error",
      code: isTimeout ? "translation.timeout" : "translation.adapter_error",
      textDigest,
      sourceLocale: input.sourceLocale,
      targetLocale: input.targetLocale,
      detail: isTimeout ? "adapter timeout" : "adapter rejected",
    });

    if (input.telemetryEnabled) {
      await input.telemetryDispatch?.({ event: "translation_failed", ...dispatchPayload });
    }
    if (input.auditEnabled) {
      await input.auditDispatch?.({ event: "translation_failed", ...dispatchPayload });
    }

    return { status: isTimeout ? "timeout" : "adapter_error", translatedText: SafeModePolicy.redactText(input.text, true) };
  } finally {
    clearTimeout(timeoutId);
  }
}

export type NetworkLeakAttempt = {
  channel: NetworkChannel;
  destination: string;
};

export type NetworkLeakMonitor = {
  attempts: NetworkLeakAttempt[];
  restore: () => void;
};

export function installNetworkLeakMonitor(): NetworkLeakMonitor {
  const attempts: NetworkLeakAttempt[] = [];

  const originalFetch = globalThis.fetch;
  const originalXhr = (globalThis as { XMLHttpRequest?: unknown }).XMLHttpRequest;
  const originalWorker = (globalThis as { Worker?: unknown }).Worker;

  globalThis.fetch = (async (input: RequestInfo | URL) => {
    const destination = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
    attempts.push({ channel: "fetch", destination });
    throw new Error("network blocked by leak monitor");
  }) as typeof globalThis.fetch;

  class GuardedXMLHttpRequest {
    open(_method: string, url: string | URL): void {
      attempts.push({ channel: "xhr", destination: String(url) });
      throw new Error("network blocked by leak monitor");
    }
  }

  class GuardedWorker {
    constructor(scriptURL: string | URL) {
      attempts.push({ channel: "worker", destination: String(scriptURL) });
      throw new Error("worker creation blocked by leak monitor");
    }
  }

  (globalThis as { XMLHttpRequest?: unknown }).XMLHttpRequest = GuardedXMLHttpRequest;
  (globalThis as { Worker?: unknown }).Worker = GuardedWorker;

  return {
    attempts,
    restore: () => {
      globalThis.fetch = originalFetch;
      (globalThis as { XMLHttpRequest?: unknown }).XMLHttpRequest = originalXhr;
      (globalThis as { Worker?: unknown }).Worker = originalWorker;
    },
  };
}
