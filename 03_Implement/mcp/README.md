# kj-atlas-mcp

Read-only MCP server exposing kj-atlas `ContextBundle` projections, over
either stdio (EXT-CONN-01 subslice B) or streamable-HTTP + OAuth 2.1
resource-server auth (subslice C), `ADR-0054` stage 1.

Independent package: not part of any npm/yarn workspace, does not share a
lockfile or `node_modules` with `03_Implement/frontend`. It monorepo-imports
`../frontend/src/export/context_bundle_projection.ts` (and its own transitive
`domain/` dependencies) by relative path rather than copying it, so the
SafeMode redaction/anti-scoring logic stays a single source of truth across
both surfaces.

## What it exposes

Two read-only tools:

1. `get_context_projection({ docId, constraint, safeMode? })`, wrapping
   `buildContextProjection` from the frontend's projection core. `constraint` is
   one of `reviewed-only | evidence | contradiction | summary`. `safeMode`
   defaults to `true` (the safe default) when omitted.
2. `get_proposal_status({ docId })` — the CE4 proposal lifecycle for a
   document: whether each AI proposal is still proposal-only
   (`status=proposed`) or was decided by a human
   (`accepted | rejected | held`, with `decidedAt`). Lets a generative-AI
   verifier confirm that a proposal was never auto-applied and to trace the
   human decision, without mutating anything.

**Scope (DOGFOOD-05)**: unreviewed cards are never exposed on any constraint —
even `safeMode: false` reports `cards=0` for them (`SEC-CONTEXT-PROJECTION-01`
fail-closed). This path is for reviewing and structuring **already-reviewed**
content, not for initial exploration of unreviewed material. An AI co-worker
that needs to respect work-state on reviewed cards gets `holdState` metadata
(DOGFOOD-08); it cannot use this server to read unreviewed content.

No resources, no prompts, no write tools. Both tools carry
`readOnlyHint: true`; `tools/list` and the absence of a `resources` capability
in `initialize`'s response are locked by `src/context_projection_tool.test.ts`
against a fixed snapshot — see that file if a future change appears to add
capability.

## Non-goals

- No write/ingest/apply/publish/sampling/elicitation capability, on either
  transport. The CE-4 audit POST described below is the only outbound call this
  server makes, and it is a *read audit* (a report of an already-served
  projection), never a mutation of the document it projected.
- **Resource server only.** This process never issues tokens, registers
  clients, or runs an authorization/consent endpoint -- it validates bearer
  tokens issued by an already-trusted external IdP (`ADR-0054`, consistent
  with `ADR-0020`'s "never run a production IdP/AS" stance). There is no
  code path for token issuance in this package.

## Running

```bash
npm install
npm run typecheck
npm test
npm start   # runs src/index.ts (transport selected by KJ_ATLAS_MCP_TRANSPORT)

# Client-based verification (generative-AI path; requires running backend).
# Run via tsx (npm run verify) — the script imports a .ts module and uses TS
# `as` syntax, which plain Node 20 rejects:
KJ_ATLAS_MCP_API_BASE_URL=http://127.0.0.1:8000 npm run verify -- [docId] [constraint]
```

### Connecting a generative-AI MCP client (config example)

To let a generative-AI agent (Claude Desktop, IDE MCP client, etc.) use this
server over stdio, add it to the client's MCP server config. The backend must
be running first (`uvicorn kj_atlas_api.main:app --port 8000`).

```jsonc
{
  "mcpServers": {
    "kj-atlas": {
      "command": "npx",
      "args": ["tsx", "src/index.ts"],
      "cwd": "/absolute/path/to/kj-atlas/03_Implement/mcp",
      "env": {
        "KJ_ATLAS_MCP_API_BASE_URL": "http://127.0.0.1:8000",
        "KJ_ATLAS_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Notes for AI agents using this path:
- One tool, `get_context_projection({ docId, constraint, safeMode })` — read-only.
- **Unreviewed cards are never exposed on any constraint** (fail-closed, see
  Scope above). Use it for already-reviewed content; `holdState` metadata tells
  you which cards are held/pending/shelved (DOGFOOD-08).
- The projection also carries structural state a generative-AI can verify:
  `voids` (kind/refs/resolved — KJ-VOIDS-01) and `narrativeChecks`
  (A/B direction + counts — KJ-AB-CROSS-CHECK-01). Both are SafeMode-safe
  (no card text, no issue messages).
- For the HTTP + OAuth 2.1 resource-server transport, set `KJ_ATLAS_MCP_TRANSPORT=http`
  and the required OAuth env vars (see Transport selection below); tokens must be
  issued by the configured trusted issuer and carry the `read:context` scope.

### Generative-AI verification runbook

A generative-AI agent can verify that the served app behaves correctly by
calling `get_context_projection` and asserting the expected contract. The
standalone client `scripts/verify_mcp.ts` (run via `npm run verify`) performs
exactly this; the scenarios below are what it checks.

| Scenario | Call | Expected (assert) |
| --- | --- | --- |
| SafeMode fail-closed | `get_context_projection({ docId, constraint: "reviewed-only", safeMode: true })` on a doc with unreviewed cards | `cards[].redacted === true`; `counts.unreviewed > 0`; unreviewed text is absent |
| holdState projection | same call on a doc with held/shelved cards | `cards[].holdState` is `held` / `shelved` / `pending` (DOGFOOD-08) |
| Anti-scoring | serialize the projection | no `score` / `rank` / `confidence` / `priority` tokens |
| not_found | `get_context_projection({ docId: "<missing>", ... })` | `isError: true` with a plain message — the transport is alive, the doc is not retrievable (DOGFOOD-03/06) |
| void state | same call on a doc that has stored voids | `voids` lists each void's kind/refs/resolved (KJ-VOIDS-01) |
| narrative A/B | same call on a doc with narrative checks | `narrativeChecks[].issueDirections` and `counts` are present — and `verify_mcp.ts` **asserts the per-check counts** (`bMissingInA`/`aMissingInB`) so a generative-AI verifier can rely on the A/B totals, not just the directions (KJ-AB-CROSS-CHECK-01) |
| lifecycle | same call on a doc | `documentMetadata.lifecycle_state` (`active` / `archived`) and `created_by` are present (ADR-0073 / 第2反復) |
| archived read-only | same call on an archived doc | `documentMetadata.lifecycle_state === "archived"`; the server enforces review-only (`PUT /docs/{id}` → **423 Locked**, code `document_archived`, even with a current ETag — ADR-0073 D2=A). A generative-AI can cross-check the write contract directly over the HTTP API or via `verify_api_write.sh` (checks 12–14) |
| bundle determinism | call twice with identical inputs | identical `bundleHash` |

Interpretation rule: an `isError` outcome with `not_found`/`error` is a **valid
signal** (the target document does not exist), not an MCP-path failure — the
transport worked, the request reached the server, and the failure was classified.

In addition to the local `mcp-context-read.v1` entry above, every **successful**
read is reported to the backend's `POST /docs/{id}/context-audit` (CE-4)
endpoint with `channel="mcp"` (`operation=query`, `command=context-query`,
`equivalenceKey=queryCanonicalHash`, `bundleHash=projection.bundleHash`,
`safeMode`, `dryRun=true`, `sideEffect=none`) via `src/audit_log.ts`
`emitContextAuditEvent`. This closes the former channel-enum gap: an
MCP-originated read is traceable in the same backend audit trail as
api/cli/gui callers. The emit is **best-effort** — the synchronous local entry
is the read's correlation, and a CE-4 POST failure never turns a successful
read into an error (it logs a structured warning to stderr). A generative-AI
verifier that needs to assert the backend saw the read can cross-check the
deployment's audit sink directly; `verify_mcp.ts` itself validates the read
path, not the sink delivery.

To verify the whole chain (MCP read → CE-4 `channel="mcp"` event → backend →
configured HTTP audit sink) in one self-contained run, use the dogfood E2E:

```bash
cd 03_Implement/backend
.venv/bin/python scripts/verify_mcp_ce4_audit_e2e.py   # expect "Result: 9 passed, 0 failed"
```

It starts a local audit sink, a migrated backend with
`KJ_ATLAS_AUDIT_TRANSPORT=http` (plus `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE=1`,
because MCP reads are safeMode=true and the dispatcher drops safe-mode events
otherwise), runs `verify_mcp.ts` against it, and asserts the sink received the
`channel="mcp"`/`operation=query` event for the read document.

### Transport selection

| Variable | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_MCP_TRANSPORT` | `stdio` | `stdio` or `http`. |

### stdio transport (subslice B)

| Variable | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_RUNTIME_PROFILE` | `local-dev` | `local-dev`, `evaluation`, `enterprise-production`を受理する。`saas-multitenant`はtenant-bound MCP credentialが未実装のため起動拒否する。 |
| `KJ_ATLAS_MCP_API_BASE_URL` | `http://127.0.0.1:8000` | Backend base URL this process fetches `GET /docs/{id}` from. Not the frontend's browser-relative `KJ_ATLAS_FRONTEND_API_BASE` -- this process runs outside the frontend's nginx proxy and needs an absolute URL. |
| `KJ_ATLAS_API_KEY` | unset | Sent as `X-API-Key` when the backend requires it. The browser client relies on same-origin proxying instead; this standalone process must send it itself. |

stdout is reserved exclusively for the MCP JSON-RPC stream once connected --
never write anything else to it. All diagnostics go to stderr. This applies
regardless of transport, for consistency with the stdio deployment.

### HTTP transport + OAuth 2.1 resource server (subslice C)

When `KJ_ATLAS_MCP_TRANSPORT=http`, this process opens a public listen port.
`KJ_ATLAS_API_KEY`/`KJ_ATLAS_MCP_API_BASE_URL` above still apply (the backend
fetch is transport-independent); the following are required in addition, with
no permissive default -- any missing value fails closed at startup rather
than falling back to an unauthenticated or wildcard-trusting mode:

| Variable | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_MCP_HTTP_HOST` | `127.0.0.1` | Listen host. |
| `KJ_ATLAS_MCP_HTTP_PORT` | `8787` | Listen port. |
| `KJ_ATLAS_MCP_RESOURCE_URL` | *(required)* | This server's own resource identifier (RFC 8707). Must equal the `aud` claim tokens are issued for. |
| `KJ_ATLAS_MCP_TRUSTED_ISSUER` | *(required)* | Exact issuer string tokens must present in `iss`. Matched exactly, no prefix/wildcard matching. |
| `KJ_ATLAS_MCP_JWKS_URI` | *(required)* | JWKS endpoint of the trusted issuer, used to verify token signatures. |
| `KJ_ATLAS_MCP_AUTHORIZATION_SERVERS` | `[KJ_ATLAS_MCP_TRUSTED_ISSUER]` | Comma-separated list advertised in `/.well-known/oauth-protected-resource` (RFC 9728). Purely informational to clients -- not itself trusted for anything. |

Behavior:

- `POST/GET/DELETE /mcp` require a valid bearer token (`Authorization: Bearer
  <token>`) with the `read:context` scope; missing/invalid/expired/wrong-issuer/
  wrong-audience tokens get 401, while a valid token without the required scope
  gets 403 `insufficient_scope`. Both responses carry a `WWW-Authenticate`
  challenge via the SDK's `requireBearerAuth`.
- `GET /.well-known/oauth-protected-resource` is intentionally unauthenticated
  (RFC 9728 requires this) and returns only non-secret discovery metadata.
- All routes (including the metadata endpoint) share a 60 requests/minute/IP
  rate limit.
- The transport is stateless (`sessionIdGenerator: undefined`); there is no
  per-client session state to fix or exhaust. Stateless mode requires a FRESH
  server + transport per request (SDK requirement), which this server does —
  a remote client can complete a full MCP session over HTTP (initialize ->
  tools/list -> tools/call), verified by `http_server.test.ts`.
- See `THREAT_MODEL.md` §6-1 for the full threat analysis of this surface.
