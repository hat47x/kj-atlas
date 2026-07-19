import { afterEach, describe, expect, it, vi } from "vitest";

import {
  ApiError,
  changeActiveTenant,
  getTenantSessionBootstrapPolicy,
  getTenantSessionContext,
  suggestMerges,
  suggestLayout,
} from "./client";
import type { DocumentV1 } from "../domain/types";
import { InvalidTenantSessionContextError } from "./session_context";
import { InvalidTenantSessionBootstrapPolicyError } from "./session_bootstrap_policy";

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Risk mitigation", x: 0, y: 0 },
      { id: "c2", text: "risk mitigation", x: 10, y: 0 },
    ],
    islands: [],
    edges: [],
  };
}

describe("tenant session bootstrap policy fetch boundary", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches a strict server policy without client runtime hints", async () => {
    const abortController = new AbortController();
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({
        tenantSessionMode: "tenant-session-required",
      }), { status: 200, headers: { "Content-Type": "application/json" } }),
    );

    await expect(getTenantSessionBootstrapPolicy({
      signal: abortController.signal,
    })).resolves.toEqual({ tenantSessionMode: "tenant-session-required" });
    expect(fetchMock).toHaveBeenCalledWith("/api/session/bootstrap-policy", {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      credentials: "same-origin",
      signal: abortController.signal,
    });
  });

  it("rejects unknown modes and response expansion", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ tenantSessionMode: "required" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({
          tenantSessionMode: "single-tenant",
          runtimeProfile: "local-dev",
        }), { status: 200, headers: { "Content-Type": "application/json" } }),
      );

    await expect(getTenantSessionBootstrapPolicy()).rejects.toBeInstanceOf(
      InvalidTenantSessionBootstrapPolicyError,
    );
    await expect(getTenantSessionBootstrapPolicy()).rejects.toBeInstanceOf(
      InvalidTenantSessionBootstrapPolicyError,
    );
  });

  it("rejects oversized and non-UTF-8 success responses", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(new Uint8Array((4 * 1024) + 1), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(new Uint8Array([0xff]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    await expect(getTenantSessionBootstrapPolicy()).rejects.toBeInstanceOf(
      InvalidTenantSessionBootstrapPolicyError,
    );
    await expect(getTenantSessionBootstrapPolicy()).rejects.toBeInstanceOf(
      InvalidTenantSessionBootstrapPolicyError,
    );
  });

  it("preserves a bounded backend failure contract", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({
        detail: {
          code: "runtime_policy_unavailable",
          message: "Runtime policy is unavailable.",
        },
      }), { status: 503, headers: { "Content-Type": "application/json" } }),
    );

    await expect(getTenantSessionBootstrapPolicy()).rejects.toMatchObject({
      status: 503,
      code: "runtime_policy_unavailable",
      message: "Runtime policy is unavailable.",
    });
  });
});

describe("tenant session context fetch boundary", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches without client tenant hints and validates the response", async () => {
    const abortController = new AbortController();
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({
        principalId: "user-1",
        activeTenant: { id: "tenant-a", displayName: "Tenant A" },
        availableTenants: [{ id: "tenant-a", displayName: "Tenant A" }],
        effectiveCapabilities: ["document.write", "document.read"],
        capabilityVersion: "capability-v7",
        tenantSessionVersion: "session-v1",
      }), { status: 200, headers: { "Content-Type": "application/json" } }),
    );

    const context = await getTenantSessionContext({ signal: abortController.signal });

    expect(context.effectiveCapabilities).toEqual(["document.read", "document.write"]);
    expect(fetchMock).toHaveBeenCalledWith("/api/session/context", {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      credentials: "same-origin",
      signal: abortController.signal,
    });
  });

  it("preserves the backend status and stable error code", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({
        detail: {
          code: "capability_resolution_unavailable",
          message: "Tenant capabilities are unavailable.",
        },
      }), { status: 503, headers: { "Content-Type": "application/json" } }),
    );

    await expect(getTenantSessionContext()).rejects.toMatchObject({
      status: 503,
      code: "capability_resolution_unavailable",
      message: "Tenant capabilities are unavailable.",
    });
  });

  it("rejects invalid JSON and invalid session contracts", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response("not-json", { status: 200, headers: { "Content-Type": "text/plain" } }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ principalId: "user-1" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    await expect(getTenantSessionContext()).rejects.toBeInstanceOf(
      InvalidTenantSessionContextError,
    );
    await expect(getTenantSessionContext()).rejects.toBeInstanceOf(
      InvalidTenantSessionContextError,
    );
  });

  it("rejects an oversized session response before JSON contract use", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ padding: "x".repeat(64 * 1024) }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response("{}", {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Content-Length": String((64 * 1024) + 1),
          },
        }),
      );

    await expect(getTenantSessionContext()).rejects.toBeInstanceOf(
      InvalidTenantSessionContextError,
    );
    await expect(getTenantSessionContext()).rejects.toBeInstanceOf(
      InvalidTenantSessionContextError,
    );
  });

  it("cancels a chunked session response as soon as it exceeds the byte limit", async () => {
    let pullCount = 0;
    let cancelled = false;
    const chunks = [
      new Uint8Array(64 * 1024),
      new Uint8Array([0x20]),
      new TextEncoder().encode("must-not-be-read"),
    ];
    const body = new ReadableStream<Uint8Array>({
      pull(controller) {
        const chunk = chunks[pullCount];
        pullCount += 1;
        if (chunk) {
          controller.enqueue(chunk);
        } else {
          controller.close();
        }
      },
      cancel() {
        cancelled = true;
      },
    }, { highWaterMark: 0 });
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(body, {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await expect(getTenantSessionContext()).rejects.toBeInstanceOf(
      InvalidTenantSessionContextError,
    );
    expect(pullCount).toBe(2);
    expect(cancelled).toBe(true);
  });

  it("bounds oversized error responses and falls back to the HTTP status text", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(new Uint8Array((64 * 1024) + 1), {
        status: 503,
        statusText: "Service Unavailable",
        headers: { "Content-Type": "application/json" },
      }),
    );

    await expect(getTenantSessionContext()).rejects.toEqual(
      new ApiError(503, "Service Unavailable"),
    );
  });

  it("rejects a session response that is not valid UTF-8", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(new Uint8Array([0xff]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await expect(getTenantSessionContext()).rejects.toBeInstanceOf(
      InvalidTenantSessionContextError,
    );
  });

  it("changes only to a tenant from the verified current allowlist", async () => {
    const abortController = new AbortController();
    const currentSession = {
      principalId: "user-1",
      activeTenant: { id: "tenant-a", displayName: "Tenant A" },
      availableTenants: [
        { id: "tenant-a", displayName: "Tenant A" },
        { id: "tenant-b", displayName: "Tenant B" },
      ],
      effectiveCapabilities: ["document.read" as const],
      capabilityVersion: "capability-v7",
      tenantSessionVersion: "session-v1",
    };
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({
        ...currentSession,
        activeTenant: { id: "tenant-b", displayName: "Tenant B" },
        capabilityVersion: "capability-v8",
        tenantSessionVersion: "session-v2",
      }), { status: 200, headers: { "Content-Type": "application/json" } }),
    );

    const nextSession = await changeActiveTenant(
      currentSession,
      "tenant-b",
      { signal: abortController.signal },
    );

    expect(nextSession.activeTenant.id).toBe("tenant-b");
    expect(fetchMock).toHaveBeenCalledWith("/api/session/active-tenant", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        tenantId: "tenant-b",
        expectedTenantSessionVersion: "session-v1",
      }),
      cache: "no-store",
      credentials: "same-origin",
      signal: abortController.signal,
    });
  });

  it("rejects a free-input tenant before sending a request", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    const currentSession = {
      principalId: "user-1",
      activeTenant: { id: "tenant-a", displayName: "Tenant A" },
      availableTenants: [{ id: "tenant-a", displayName: "Tenant A" }],
      effectiveCapabilities: ["document.read" as const],
      capabilityVersion: "capability-v7",
      tenantSessionVersion: "session-v1",
    };

    await expect(
      changeActiveTenant(currentSession, "attacker-tenant"),
    ).rejects.toBeInstanceOf(InvalidTenantSessionContextError);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects a tenant-change response for another principal or tenant", async () => {
    const currentSession = {
      principalId: "user-1",
      activeTenant: { id: "tenant-a", displayName: "Tenant A" },
      availableTenants: [
        { id: "tenant-a", displayName: "Tenant A" },
        { id: "tenant-b", displayName: "Tenant B" },
      ],
      effectiveCapabilities: ["document.read" as const],
      capabilityVersion: "capability-v7",
      tenantSessionVersion: "session-v1",
    };
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({
          ...currentSession,
          principalId: "user-2",
          activeTenant: { id: "tenant-b", displayName: "Tenant B" },
          tenantSessionVersion: "session-v2",
        }), { status: 200 }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({
          ...currentSession,
          activeTenant: { id: "tenant-a", displayName: "Tenant A" },
          tenantSessionVersion: "session-v2",
        }), { status: 200 }),
      );

    await expect(
      changeActiveTenant(currentSession, "tenant-b"),
    ).rejects.toBeInstanceOf(InvalidTenantSessionContextError);
    await expect(
      changeActiveTenant(currentSession, "tenant-b"),
    ).rejects.toBeInstanceOf(InvalidTenantSessionContextError);
  });

  it("rejects a tenant-change response that keeps the old session version", async () => {
    const currentSession = {
      principalId: "user-1",
      activeTenant: { id: "tenant-a", displayName: "Tenant A" },
      availableTenants: [
        { id: "tenant-a", displayName: "Tenant A" },
        { id: "tenant-b", displayName: "Tenant B" },
      ],
      effectiveCapabilities: ["document.read" as const],
      capabilityVersion: "capability-v7",
      tenantSessionVersion: "session-v1",
    };
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({
        ...currentSession,
        activeTenant: { id: "tenant-b", displayName: "Tenant B" },
      }), { status: 200 }),
    );

    await expect(
      changeActiveTenant(currentSession, "tenant-b"),
    ).rejects.toBeInstanceOf(InvalidTenantSessionContextError);
  });

  it("preserves a stable active-tenant update failure", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({
        detail: {
          code: "active_tenant_update_unavailable",
          message: "Active tenant update is unavailable.",
        },
      }), { status: 503, statusText: "Service Unavailable" }),
    );
    const currentSession = {
      principalId: "user-1",
      activeTenant: { id: "tenant-a", displayName: "Tenant A" },
      availableTenants: [
        { id: "tenant-a", displayName: "Tenant A" },
        { id: "tenant-b", displayName: "Tenant B" },
      ],
      effectiveCapabilities: ["document.read" as const],
      capabilityVersion: "capability-v7",
      tenantSessionVersion: "session-v1",
    };

    await expect(changeActiveTenant(currentSession, "tenant-b")).rejects.toMatchObject({
      status: 503,
      code: "active_tenant_update_unavailable",
      message: "Active tenant update is unavailable.",
    });
  });
});

describe("suggestMerges contract validation", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("accepts a contract-valid candidate-group payload", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [
            {
              groupId: "heuristic-risk-c1-c2",
              targetCardId: "c1",
              candidateCardIds: ["c2"],
              scoreSummary: { min: 1, max: 1, avg: 1 },
              reasonCodes: ["heuristic:normalized-text"],
              snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
              cardIds: ["c1", "c2"],
              mergedTextDraft: "Risk mitigation",
              rationale: "heuristic:normalized-text",
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const result = await suggestMerges(createDocument(), "collect candidates");

    expect(result.suggestions).toHaveLength(1);
    expect(result.suggestions[0]?.snapshotVersion).toBe("CTR-2B-01-CANDIDATE-GROUP-V1");
  });

  it("preserves mock group order and targetCardId mapping under a fixed snapshotVersion", async () => {
    const responseBody = JSON.stringify({
      suggestions: [
        {
          groupId: "heuristic-risk-c1-c2",
          targetCardId: "c1",
          candidateCardIds: ["c2"],
          scoreSummary: { min: 1, max: 1, avg: 1 },
          reasonCodes: ["heuristic:normalized-text"],
          snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
          cardIds: ["c1", "c2"],
          mergedTextDraft: "Risk mitigation",
          rationale: "heuristic:normalized-text",
        },
        {
          groupId: "heuristic-timeline-c3-c4",
          targetCardId: "c3",
          candidateCardIds: ["c4"],
          scoreSummary: { min: 0.75, max: 0.75, avg: 0.75 },
          reasonCodes: ["heuristic:token-signature"],
          snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
          cardIds: ["c3", "c4"],
          mergedTextDraft: "Timeline review",
          rationale: "heuristic:token-signature",
        },
      ],
    });

    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(responseBody, { status: 200, headers: { "Content-Type": "application/json" } }))
      .mockResolvedValueOnce(new Response(responseBody, { status: 200, headers: { "Content-Type": "application/json" } }));

    const first = await suggestMerges(createDocument(), "collect candidates");
    const second = await suggestMerges(createDocument(), "collect candidates");

    expect(first).toEqual(second);
    expect(first.suggestions.map((suggestion) => suggestion.groupId)).toEqual([
      "heuristic-risk-c1-c2",
      "heuristic-timeline-c3-c4",
    ]);
    expect(first.suggestions.map((suggestion) => suggestion.targetCardId)).toEqual(["c1", "c3"]);
    expect(first.suggestions.every((suggestion) => suggestion.snapshotVersion === "CTR-2B-01-CANDIDATE-GROUP-V1")).toBe(true);
  });

  it("fails fast when snapshotVersion breaks the frozen contract", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [
            {
              groupId: "heuristic-risk-c1-c2",
              targetCardId: "c1",
              candidateCardIds: ["c2"],
              scoreSummary: { min: 1, max: 1, avg: 1 },
              reasonCodes: ["heuristic:normalized-text"],
              snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V2",
              cardIds: ["c1", "c2"],
              mergedTextDraft: "Risk mitigation",
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    await expect(suggestMerges(createDocument())).rejects.toMatchObject({
      name: "Error",
      message: "Invalid merge suggestions contract payload",
      status: 500,
    });
  });

  it("fails fast when required fields are missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [
            {
              groupId: "heuristic-risk-c1-c2",
              targetCardId: "c1",
              scoreSummary: { min: 1, max: 1, avg: 1 },
              reasonCodes: ["heuristic:normalized-text"],
              snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
              cardIds: ["c1", "c2"],
              mergedTextDraft: "Risk mitigation",
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    await expect(suggestMerges(createDocument())).rejects.toMatchObject({
      message: "Invalid merge suggestions contract payload",
      status: 500,
    });
  });
});

describe("PROV-ERROR-01: structured provider error propagation", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("carries code and disabledReason from a ProviderDisabledError contract (detail as object)", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: {
            code: "provider_unavailable",
            message: "AI is disabled. Set KJ_ATLAS_LLM_PROVIDER to local or large-scale.",
            provider: "none",
            disabled_reason: "provider_disabled_or_none_default",
          },
        }),
        { status: 503, headers: { "Content-Type": "application/json" } }
      )
    );

    const error = await suggestLayout(createDocument()).catch((caught) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(503);
    expect((error as ApiError).code).toBe("provider_unavailable");
    expect((error as ApiError).disabledReason).toBe("provider_disabled_or_none_default");
    expect((error as ApiError).message).toBe("AI is disabled. Set KJ_ATLAS_LLM_PROVIDER to local or large-scale.");
  });

  it("carries code without disabledReason for a configured-but-unreachable provider", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: {
            code: "provider_timeout",
            message: "local request timed out with status 504",
            provider: "local",
          },
        }),
        { status: 504, headers: { "Content-Type": "application/json" } }
      )
    );

    const error = await suggestLayout(createDocument()).catch((caught) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).code).toBe("provider_timeout");
    expect((error as ApiError).disabledReason).toBeUndefined();
  });

  it("still supports a plain string detail (non-provider routes)", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "narrativeText must not be empty" }), {
        status: 422,
        headers: { "Content-Type": "application/json" },
      })
    );

    const error = await suggestLayout(createDocument()).catch((caught) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).message).toBe("narrativeText must not be empty");
    expect((error as ApiError).code).toBeUndefined();
  });
});
