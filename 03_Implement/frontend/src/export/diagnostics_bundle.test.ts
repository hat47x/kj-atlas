import { describe, expect, it, vi } from "vitest";
import {
  buildDiagnosticsBundle,
  DIAG_BUNDLE_SCHEMA_VERSION,
  isDiagBundleShapeValid,
  serializeDiagnosticsBundle,
  type DiagBundleInput,
} from "./diagnostics_bundle";

// PRODUCT-OPS-02 / ADR-0053: diag-bundle.v1 safety properties. These lock the
// allowlist shape, unknown-key rejection, and the SafeMode invariant ("ON/OFF
// で出力項目・値の露出境界を変えない") BEFORE any UI wiring -- the panel is a
// thin caller over this pure core.

const BASE_INPUT: DiagBundleInput = {
  generatedAt: "2026-07-13T00:00:00.000Z",
  classificationCode: "SAVE-FAILURE",
  safeMode: false,
  providerType: "none",
};

describe("buildDiagnosticsBundle: minimal shape", () => {
  it("omits optional keys entirely (not just undefined-valued) when not supplied", () => {
    const bundle = buildDiagnosticsBundle(BASE_INPUT);

    expect(bundle.schemaVersion).toBe(DIAG_BUNDLE_SCHEMA_VERSION);
    expect(Object.keys(bundle).sort()).toEqual(["app", "client", "generatedAt", "incident", "runtime", "schemaVersion"]);
    expect(Object.keys(bundle.client).sort()).toEqual(["browserFamily", "osFamily"]);
    expect(Object.keys(bundle.incident).sort()).toEqual(["classificationCode"]);
    expect(isDiagBundleShapeValid(bundle)).toBe(true);
  });

  it("falls back app.revision to unknown when unsupplied or invalid", () => {
    expect(buildDiagnosticsBundle(BASE_INPUT).app.revision).toBe("unknown");
    expect(buildDiagnosticsBundle({ ...BASE_INPUT, appRevision: "" }).app.revision).toBe("unknown");
    expect(buildDiagnosticsBundle({ ...BASE_INPUT, appRevision: "not a valid revision!" }).app.revision).toBe("unknown");
    expect(buildDiagnosticsBundle({ ...BASE_INPUT, appRevision: "2026.07.13-abc123" }).app.revision).toBe("2026.07.13-abc123");
  });
});

describe("buildDiagnosticsBundle: full shape", () => {
  const fullInput: DiagBundleInput = {
    ...BASE_INPUT,
    httpStatus: 503,
    appRevision: "rev-abc123",
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    platform: "Win32",
    document: { version: 2, updatedAt: "2026-07-13T01:00:00.000Z", cardCount: 12, islandCount: 3, edgeCount: 5 },
    error: { errorCode: "A1_TIMEOUT", contractId: "hil-rs-a1.v1", occurredAt: "2026-07-13T00:59:00.000Z" },
  };

  it("includes every optional field when supplied, with exact allowed keys", () => {
    const bundle = buildDiagnosticsBundle(fullInput);

    expect(bundle.client).toEqual({ browserFamily: "chrome", browserMajor: 120, osFamily: "windows" });
    expect(bundle.incident).toEqual({ classificationCode: "SAVE-FAILURE", httpStatus: 503 });
    expect(bundle.document).toEqual({
      version: 2,
      updatedAt: "2026-07-13T01:00:00.000Z",
      counts: { cards: 12, islands: 3, edges: 5 },
    });
    expect(bundle.error).toEqual({ errorCode: "A1_TIMEOUT", contractId: "hil-rs-a1.v1", occurredAt: "2026-07-13T00:59:00.000Z" });
    expect(isDiagBundleShapeValid(bundle)).toBe(true);
  });

  it("does not leak extra properties smuggled onto nested input objects (no spread of caller input)", () => {
    const pollutedInput = {
      ...fullInput,
      document: { ...fullInput.document, cardText: "SECRET CARD BODY", documentId: "doc_should_not_leak" } as unknown,
      error: { ...fullInput.error, message: "raw stack trace should not leak", stack: "at foo()" } as unknown,
    } as DiagBundleInput;

    const bundle = buildDiagnosticsBundle(pollutedInput);

    expect(Object.keys(bundle.document!).sort()).toEqual(["counts", "updatedAt", "version"]);
    expect(Object.keys(bundle.error!).sort()).toEqual(["contractId", "errorCode", "occurredAt"]);
    expect(JSON.stringify(bundle)).not.toContain("SECRET");
    expect(JSON.stringify(bundle)).not.toContain("stack trace");
  });
});

describe("buildDiagnosticsBundle: SafeMode invariant", () => {
  it("changes only runtime.safeMode between ON and OFF, nothing else", () => {
    const input: DiagBundleInput = {
      ...BASE_INPUT,
      httpStatus: 401,
      appRevision: "rev-xyz",
      userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15",
      platform: "MacIntel",
      document: { version: 2, cardCount: 1, islandCount: 0, edgeCount: 0 },
    };

    const off = buildDiagnosticsBundle({ ...input, safeMode: false });
    const on = buildDiagnosticsBundle({ ...input, safeMode: true });

    expect(off.runtime.safeMode).toBe(false);
    expect(on.runtime.safeMode).toBe(true);
    // Every other field must be byte-identical regardless of SafeMode.
    const stripSafeMode = (bundle: ReturnType<typeof buildDiagnosticsBundle>) => {
      const { runtime, ...rest } = bundle;
      const { safeMode: _safeMode, ...restRuntime } = runtime;
      return { ...rest, runtime: restRuntime };
    };
    expect(stripSafeMode(off)).toEqual(stripSafeMode(on));
  });
});

describe("isDiagBundleShapeValid: unknown-key rejection", () => {
  it("rejects an extra top-level key", () => {
    const bundle: Record<string, unknown> = { ...buildDiagnosticsBundle(BASE_INPUT), extra: "nope" };
    expect(isDiagBundleShapeValid(bundle)).toBe(false);
  });

  it("rejects an extra key in app/client/incident/runtime/document/error", () => {
    const base = buildDiagnosticsBundle({
      ...BASE_INPUT,
      document: { version: 2, cardCount: 0, islandCount: 0, edgeCount: 0 },
      error: { errorCode: "X", contractId: "Y", occurredAt: "2026-07-13T00:00:00.000Z" },
    });

    expect(isDiagBundleShapeValid({ ...base, app: { ...base.app, extra: 1 } })).toBe(false);
    expect(isDiagBundleShapeValid({ ...base, client: { ...base.client, extra: 1 } })).toBe(false);
    expect(isDiagBundleShapeValid({ ...base, incident: { ...base.incident, extra: 1 } })).toBe(false);
    expect(isDiagBundleShapeValid({ ...base, runtime: { ...base.runtime, extra: 1 } })).toBe(false);
    expect(isDiagBundleShapeValid({ ...base, document: { ...base.document, extra: 1 } })).toBe(false);
    expect(
      isDiagBundleShapeValid({ ...base, document: { ...base.document, counts: { ...base.document!.counts, extra: 1 } } }),
    ).toBe(false);
    expect(isDiagBundleShapeValid({ ...base, error: { ...base.error, message: "should not exist" } })).toBe(false);
  });

  it("rejects an unknown classificationCode or providerType", () => {
    const base = buildDiagnosticsBundle(BASE_INPUT);
    expect(isDiagBundleShapeValid({ ...base, incident: { classificationCode: "NOT-A-CODE" } })).toBe(false);
    expect(isDiagBundleShapeValid({ ...base, runtime: { ...base.runtime, providerType: "openai" } })).toBe(false);
  });

  it("accepts a fully valid bundle produced by the builder", () => {
    const bundle = buildDiagnosticsBundle({
      ...BASE_INPUT,
      httpStatus: 200,
      document: { version: 2, updatedAt: "2026-07-13T00:00:00.000Z", cardCount: 1, islandCount: 1, edgeCount: 1 },
      error: { errorCode: "X", contractId: "Y", occurredAt: "2026-07-13T00:00:00.000Z" },
    });
    expect(isDiagBundleShapeValid(bundle)).toBe(true);
  });
});

describe("client normalization", () => {
  const cases: Array<[string, string, { browserFamily: string; browserMajor?: number; osFamily: string }]> = [
    [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Win32",
      { browserFamily: "chrome", browserMajor: 120, osFamily: "windows" },
    ],
    [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
      "Win32",
      { browserFamily: "firefox", browserMajor: 121, osFamily: "windows" },
    ],
    [
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15",
      "MacIntel",
      { browserFamily: "safari", browserMajor: 17, osFamily: "macos" },
    ],
    [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
      "Win32",
      { browserFamily: "edge", browserMajor: 120, osFamily: "windows" },
    ],
    [
      "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
      "Linux armv8l",
      { browserFamily: "chrome", browserMajor: 120, osFamily: "android" },
    ],
    [
      "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
      "iPhone",
      { browserFamily: "safari", browserMajor: 17, osFamily: "ios" },
    ],
    [
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Linux x86_64",
      { browserFamily: "chrome", browserMajor: 120, osFamily: "linux" },
    ],
    ["some-unrecognized-agent-string", "unrecognized-platform", { browserFamily: "other", osFamily: "other" }],
  ];

  it.each(cases)("normalizes UA=%s platform=%s", (userAgent, platform, expected) => {
    const bundle = buildDiagnosticsBundle({ ...BASE_INPUT, userAgent, platform });
    expect(bundle.client.browserFamily).toBe(expected.browserFamily);
    expect(bundle.client.browserMajor).toBe(expected.browserMajor);
    expect(bundle.client.osFamily).toBe(expected.osFamily);
  });

  it("never stores the raw userAgent or platform string anywhere in the output", () => {
    const distinctiveUa = "Mozilla/5.0 UNIQUE-MARKER-STRING-0042 Chrome/120.0.0.0";
    const bundle = buildDiagnosticsBundle({ ...BASE_INPUT, userAgent: distinctiveUa, platform: "UNIQUE-PLATFORM-MARKER" });
    const serialized = serializeDiagnosticsBundle(bundle);
    expect(serialized).not.toContain("UNIQUE-MARKER-STRING-0042");
    expect(serialized).not.toContain("UNIQUE-PLATFORM-MARKER");
  });
});

describe("no side effects", () => {
  it("performs zero network calls and zero storage writes while building and serializing", () => {
    const fetchSpy = vi.fn();
    const setItemSpy = vi.fn();
    const sessionSetItemSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    vi.stubGlobal("localStorage", { setItem: setItemSpy, getItem: vi.fn(), removeItem: vi.fn() });
    vi.stubGlobal("sessionStorage", { setItem: sessionSetItemSpy, getItem: vi.fn(), removeItem: vi.fn() });

    try {
      const bundle = buildDiagnosticsBundle({
        ...BASE_INPUT,
        document: { version: 2, cardCount: 1, islandCount: 1, edgeCount: 1 },
        error: { errorCode: "X", contractId: "Y", occurredAt: "2026-07-13T00:00:00.000Z" },
      });
      serializeDiagnosticsBundle(bundle);

      expect(fetchSpy).not.toHaveBeenCalled();
      expect(setItemSpy).not.toHaveBeenCalled();
      expect(sessionSetItemSpy).not.toHaveBeenCalled();
    } finally {
      vi.unstubAllGlobals();
    }
  });
});

describe("serializeDiagnosticsBundle", () => {
  it("is deterministic for identical input", () => {
    const input: DiagBundleInput = { ...BASE_INPUT, document: { version: 2, cardCount: 2, islandCount: 1, edgeCount: 1 } };
    const first = serializeDiagnosticsBundle(buildDiagnosticsBundle(input));
    const second = serializeDiagnosticsBundle(buildDiagnosticsBundle(input));
    expect(first).toBe(second);
  });

  it("round-trips through JSON.parse without gaining or losing keys", () => {
    const bundle = buildDiagnosticsBundle({
      ...BASE_INPUT,
      httpStatus: 500,
      document: { version: 2, updatedAt: "2026-07-13T00:00:00.000Z", cardCount: 1, islandCount: 1, edgeCount: 1 },
      error: { errorCode: "X", contractId: "Y", occurredAt: "2026-07-13T00:00:00.000Z" },
    });
    const roundTripped = JSON.parse(serializeDiagnosticsBundle(bundle));
    expect(roundTripped).toEqual(bundle);
    expect(isDiagBundleShapeValid(roundTripped)).toBe(true);
  });
});
