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

One tool, `get_context_projection({ docId, constraint, safeMode? })`, wrapping
`buildContextProjection` from the frontend's projection core. `constraint` is
one of `reviewed-only | evidence | contradiction | summary`. `safeMode`
defaults to `true` (the safe default) when omitted.

No resources, no prompts, no other tools. `tools/list` and the absence of a
`resources` capability in `initialize`'s response are locked by
`src/context_projection_tool.test.ts` against a fixed snapshot — see that
file if a future change appears to add capability.

## Non-goals

- No write/ingest/apply/publish/sampling/elicitation capability, on either
  transport.
- **Resource server only.** This process never issues tokens, registers
  clients, or runs an authorization/consent endpoint -- it validates bearer
  tokens issued by an already-trusted external IdP (`ADR-0054`, consistent
  with `ADR-0020`'s "never run a production IdP/AS" stance). There is no
  code path for token issuance in this package.
- No backend contract change: reads are audited locally (structured JSON on
  stderr, `src/audit_log.ts`) rather than via the backend's
  `POST /docs/{id}/context-audit` (CE-4) endpoint, whose `channel` enum has no
  slot for an MCP-originated read yet. Wiring that in is a separate,
  shared-contract change deferred to a dedicated backend issue.

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
  <token>`); missing/invalid/expired/wrong-issuer/wrong-audience tokens get a
  401 with a `WWW-Authenticate: Bearer ... resource_metadata=...` header, via
  the SDK's `requireBearerAuth`.
- `GET /.well-known/oauth-protected-resource` is intentionally unauthenticated
  (RFC 9728 requires this) and returns only non-secret discovery metadata.
- All routes (including the metadata endpoint) share a 60 requests/minute/IP
  rate limit.
- The transport is stateless (`sessionIdGenerator: undefined`); there is no
  per-client session state to fix or exhaust.
- See `THREAT_MODEL.md` §6-1 for the full threat analysis of this surface.
