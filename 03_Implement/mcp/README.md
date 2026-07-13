# kj-atlas-mcp

Read-only stdio MCP server exposing kj-atlas `ContextBundle` projections
(EXT-CONN-01 subslice B, `ADR-0054` stage 1).

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

## Non-goals (this subslice)

- No write/ingest/apply/publish/sampling/elicitation capability.
- No HTTP or OAuth transport (stdio only). No listen port is opened.
- No backend contract change: reads are audited locally (structured JSON on
  stderr, `src/audit_log.ts`) rather than via the backend's
  `POST /docs/{id}/context-audit` (CE-4) endpoint, whose `channel` enum has no
  slot for an MCP-originated read yet. Wiring that in is a separate,
  shared-contract change deferred to subslice C or a dedicated backend issue.

## Running

```bash
npm install
npm run typecheck
npm test
npm start   # runs src/index.ts over stdio via tsx
```

Environment variables (both optional):

| Variable | Default | Purpose |
| --- | --- | --- |
| `KJ_ATLAS_MCP_API_BASE_URL` | `http://127.0.0.1:8000` | Backend base URL this process fetches `GET /docs/{id}` from. Not the frontend's browser-relative `KJ_ATLAS_FRONTEND_API_BASE` -- this process runs outside the frontend's nginx proxy and needs an absolute URL. |
| `KJ_ATLAS_API_KEY` | unset | Sent as `X-API-Key` when the backend requires it. The browser client relies on same-origin proxying instead; this standalone process must send it itself. |

stdout is reserved exclusively for the MCP JSON-RPC stream once connected --
never write anything else to it. All diagnostics go to stderr.
