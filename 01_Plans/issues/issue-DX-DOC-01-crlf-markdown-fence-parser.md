# Issue: DX-DOC-01 Markdown JSON Fence Test Must Accept CRLF

- Type: Bug / Test portability
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: Full frontend test run on Windows
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/import/external_agent_workflow_doc.test.ts`
- Expected verification level: unit test

## Problem

The test that extracts the public `agent-response.v1` JSON example required a line-feed-only fence opening. A Windows checkout stores the Markdown with CRLF, so the test found zero JSON blocks even though the document contained the expected example.

## Resolution

The extractor now accepts both LF and CRLF line endings. The implementation and public document contract are unchanged.

## Verification

- Full frontend Vitest run passes, including `external_agent_workflow_doc.test.ts`.

## ADR Impact

No ADR is needed. This is a test portability correction.
