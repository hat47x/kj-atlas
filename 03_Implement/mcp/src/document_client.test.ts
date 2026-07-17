import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DocumentFetchError,
  DocumentNotFoundError,
  fetchDocument,
  loadDocumentClientConfigFromEnv,
  validateMcpRuntimeProfile,
} from "./document_client.js";

function mockResponse(status: number, body: unknown): Response {
  return {
    status,
    ok: status >= 200 && status < 300,
    json: async () => body,
  } as Response;
}

describe("loadDocumentClientConfigFromEnv", () => {
  it("defaults to the direct-launch backend URL and no API key", () => {
    const config = loadDocumentClientConfigFromEnv({});
    expect(config).toEqual({ baseUrl: "http://127.0.0.1:8000", apiKey: undefined });
  });

  it("reads KJ_ATLAS_MCP_API_BASE_URL and KJ_ATLAS_API_KEY, stripping a trailing slash", () => {
    const config = loadDocumentClientConfigFromEnv({
      KJ_ATLAS_MCP_API_BASE_URL: "https://kj-atlas.example.internal/",
      KJ_ATLAS_API_KEY: "secret-key",
    });
    expect(config).toEqual({ baseUrl: "https://kj-atlas.example.internal", apiKey: "secret-key" });
  });

  it.each(["local-dev", "evaluation", "enterprise-production"])(
    "accepts the single-tenant runtime profile %s",
    (runtimeProfile) => {
      expect(validateMcpRuntimeProfile({ KJ_ATLAS_RUNTIME_PROFILE: ` ${runtimeProfile.toUpperCase()} ` })).toBe(
        runtimeProfile,
      );
    },
  );

  it("fails closed for the unfinished SaaS runtime profile", () => {
    expect(() =>
      loadDocumentClientConfigFromEnv({ KJ_ATLAS_RUNTIME_PROFILE: "saas-multitenant" }),
    ).toThrow("tenant-bound MCP credentials");
  });

  it("rejects unknown runtime profiles", () => {
    expect(() => loadDocumentClientConfigFromEnv({ KJ_ATLAS_RUNTIME_PROFILE: "production" })).toThrow(
      "Unsupported KJ_ATLAS_RUNTIME_PROFILE",
    );
  });
});

describe("fetchDocument", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("requests GET /docs/{id} against the configured base URL", async () => {
    const fetchSpy = vi.fn(async () => mockResponse(200, { id: "doc1", version: 1 }));
    vi.stubGlobal("fetch", fetchSpy);

    await fetchDocument({ baseUrl: "http://127.0.0.1:8000" }, "doc1");

    expect(fetchSpy).toHaveBeenCalledWith("http://127.0.0.1:8000/docs/doc1", { headers: {} });
  });

  it("sends X-API-Key when configured (the browser client never does; this is a separate process)", async () => {
    const fetchSpy = vi.fn(async () => mockResponse(200, { id: "doc1", version: 1 }));
    vi.stubGlobal("fetch", fetchSpy);

    await fetchDocument({ baseUrl: "http://127.0.0.1:8000", apiKey: "secret-key" }, "doc1");

    expect(fetchSpy).toHaveBeenCalledWith("http://127.0.0.1:8000/docs/doc1", {
      headers: { "X-API-Key": "secret-key" },
    });
  });

  it("URL-encodes the docId", async () => {
    const fetchSpy = vi.fn(async () => mockResponse(200, {}));
    vi.stubGlobal("fetch", fetchSpy);

    await fetchDocument({ baseUrl: "http://127.0.0.1:8000" }, "doc with space");

    expect(fetchSpy).toHaveBeenCalledWith("http://127.0.0.1:8000/docs/doc%20with%20space", { headers: {} });
  });

  it("throws DocumentNotFoundError on 404", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => mockResponse(404, {})));
    await expect(fetchDocument({ baseUrl: "http://127.0.0.1:8000" }, "missing")).rejects.toThrow(
      DocumentNotFoundError,
    );
  });

  it("throws DocumentFetchError on other non-ok statuses", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => mockResponse(500, {})));
    await expect(fetchDocument({ baseUrl: "http://127.0.0.1:8000" }, "doc1")).rejects.toThrow(DocumentFetchError);
  });

  it("returns the parsed document body on success", async () => {
    const body = { id: "doc1", version: 1, cards: [] };
    vi.stubGlobal("fetch", vi.fn(async () => mockResponse(200, body)));
    const result = await fetchDocument({ baseUrl: "http://127.0.0.1:8000" }, "doc1");
    expect(result).toEqual(body);
  });
});
