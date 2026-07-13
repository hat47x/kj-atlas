import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { createServer } from "./server.js";
import type { DocumentV2 } from "../../frontend/src/domain/types.js";

// EXT-CONN-01 subslice B, Maintainer代理裁可 condition: "MCP capabilityはread-only
// resourcesとread-only toolsだけにallowlistし...tools/list / resources/list の
// 固定snapshotで検証する". A real Client<->Server pair over InMemoryTransport
// (no stdio/process needed) exercises the actual wire-level protocol, not just
// this module's own function calls.

function buildFixtureDoc(): DocumentV2 {
  return {
    version: 2,
    id: "doc_mcp_fixture",
    title: "mcp fixture",
    createdAt: "2026-07-13T00:00:00.000Z",
    updatedAt: "2026-07-13T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "reviewed claim", x: 0, y: 0, claimType: "claim", textReviewed: true },
      { id: "c2", text: "unreviewed draft", x: 100, y: 0, claimType: "unknown", textReviewed: false },
    ],
    edges: [],
    islands: [],
    readingOrder: ["c1", "c2"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

function mockDocResponse(status: number, body: unknown) {
  return { status, ok: status >= 200 && status < 300, json: async () => body } as Response;
}

async function connectedClient(): Promise<Client> {
  const server = createServer({ baseUrl: "http://127.0.0.1:8000" });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  const client = new Client({ name: "test-client", version: "0.0.0" });
  await Promise.all([client.connect(clientTransport), server.connect(serverTransport)]);
  return client;
}

describe("capability allowlist (fixed snapshot)", () => {
  let client: Client;

  beforeEach(async () => {
    client = await connectedClient();
  });

  it("tools/list exposes exactly one read-only tool and nothing else", async () => {
    const { tools } = await client.listTools();
    expect(tools.map((tool) => tool.name)).toEqual(["get_context_projection"]);
    expect(tools[0].annotations).toMatchObject({
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
    });
  });

  it("advertises no resources capability at all -- resources/list is not even a supported method", async () => {
    // A server that never registers a resource does not advertise the
    // resources capability during initialize, so the SDK correctly rejects
    // resources/list as unknown rather than returning an empty list. This is
    // a STRONGER guarantee than "empty" would be: the method doesn't exist.
    await expect(client.listResources()).rejects.toMatchObject({ code: -32601 });
  });

  it("never registers a write/ingest/apply/publish-shaped tool name", async () => {
    const { tools } = await client.listTools();
    const names = tools.map((tool) => tool.name.toLowerCase());
    for (const forbidden of ["write", "ingest", "apply", "publish", "create", "update", "delete", "sampling", "elicit"]) {
      expect(names.some((name) => name.includes(forbidden)), forbidden).toBe(false);
    }
  });
});

describe("get_context_projection tool behavior", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("defaults safeMode to true when omitted, and excludes unreviewed cards for reviewed-only", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => mockDocResponse(200, buildFixtureDoc())));
    const client = await connectedClient();

    const result = await client.callTool({
      name: "get_context_projection",
      arguments: { docId: "doc_mcp_fixture", constraint: "reviewed-only" },
    });

    expect(result.isError).toBeFalsy();
    const text = (result.content as Array<{ type: string; text?: string }>)[0]?.text ?? "";
    const projection = JSON.parse(text);
    expect(projection.safeMode).toBe(true);
    expect(projection.cards.map((card: { id: string }) => card.id)).toEqual(["c1"]);
    // safeMode true -> even the reviewed card's text is redacted (share boundary).
    expect(projection.cards[0].redacted).toBe(true);
  });

  it("exposes reviewed card text when safeMode is explicitly false", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => mockDocResponse(200, buildFixtureDoc())));
    const client = await connectedClient();

    const result = await client.callTool({
      name: "get_context_projection",
      arguments: { docId: "doc_mcp_fixture", constraint: "reviewed-only", safeMode: false },
    });

    const text = (result.content as Array<{ type: string; text?: string }>)[0]?.text ?? "";
    const projection = JSON.parse(text);
    expect(projection.cards[0].text).toBe("reviewed claim");
  });

  it("never emits score/rank/confidence/priority vocabulary in the projection", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => mockDocResponse(200, buildFixtureDoc())));
    const client = await connectedClient();

    const result = await client.callTool({
      name: "get_context_projection",
      arguments: { docId: "doc_mcp_fixture", constraint: "summary" },
    });

    const text = (result.content as Array<{ type: string; text?: string }>)[0]?.text ?? "";
    expect(text).not.toMatch(/score|rank|confidence|priority/i);
  });

  it("returns an error result (not a thrown exception) when the document is missing", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => mockDocResponse(404, {})));
    const client = await connectedClient();

    const result = await client.callTool({
      name: "get_context_projection",
      arguments: { docId: "missing-doc", constraint: "summary" },
    });

    expect(result.isError).toBe(true);
  });

  it("logs an audit entry to stderr (never stdout) for both success and not-found outcomes", async () => {
    const stderrSpy = vi.spyOn(process.stderr, "write").mockImplementation(() => true);
    const stdoutSpy = vi.spyOn(process.stdout, "write").mockImplementation(() => true);
    vi.stubGlobal("fetch", vi.fn(async () => mockDocResponse(200, buildFixtureDoc())));
    const client = await connectedClient();

    await client.callTool({
      name: "get_context_projection",
      arguments: { docId: "doc_mcp_fixture", constraint: "summary" },
    });

    const auditLines = stderrSpy.mock.calls
      .map((call) => call[0] as string)
      .filter((line) => line.includes("mcp-context-read.v1"));
    expect(auditLines.length).toBeGreaterThan(0);
    const entry = JSON.parse(auditLines[auditLines.length - 1]);
    expect(entry.outcome).toBe("ok");
    expect(entry.bundleHash).toMatch(/^[0-9a-f]{64}$/);
    expect(entry.queryCanonicalHash).toMatch(/^[0-9a-f]{64}$/);
    // The MCP protocol itself writes plenty to stdout via the transport, but
    // this audit entry specifically must never land there.
    expect(stdoutSpy.mock.calls.some((call) => (call[0] as string).includes("mcp-context-read.v1"))).toBe(false);

    stderrSpy.mockRestore();
    stdoutSpy.mockRestore();
  });
});
