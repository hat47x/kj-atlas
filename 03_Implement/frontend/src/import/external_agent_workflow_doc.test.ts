import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { parseAgentResponse } from "./agent_response_import";

// EXT-AGENT-03 (spec §7): the public-facing doc's agent-response.v1 example
// must stay valid as the schema evolves -- extracted directly from the
// Markdown source (not a hand-synced copy) so drift is impossible to miss.
// Walks upward from __dirname to find the repo root (the directory
// containing 04_Documentation) rather than assuming a fixed nesting depth,
// since some checkout/mirror setups flatten 03_Implement/frontend.
function findRepoRoot(startDir: string): string {
  let dir = startDir;
  for (let i = 0; i < 10; i += 1) {
    if (fs.existsSync(path.join(dir, "04_Documentation"))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  throw new Error(`Could not find repo root (04_Documentation) walking up from ${startDir}`);
}

const docPath = path.join(findRepoRoot(__dirname), "04_Documentation", "external_agent_workflow.md");

function extractJsonFencedBlocks(markdown: string): string[] {
  const pattern = /```json\r?\n([\s\S]*?)```/g;
  return Array.from(markdown.matchAll(pattern), (match) => match[1]);
}

describe("external_agent_workflow.md response example", () => {
  it("contains exactly one ```json fenced block", () => {
    const markdown = fs.readFileSync(docPath, "utf8");
    expect(extractJsonFencedBlocks(markdown)).toHaveLength(1);
  });

  it("is a valid agent-response.v1 payload (lenient mode)", () => {
    const markdown = fs.readFileSync(docPath, "utf8");
    const [example] = extractJsonFencedBlocks(markdown);
    const result = parseAgentResponse(example, "lenient");
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.warnings).toHaveLength(0);
    expect(result.response.proposals.length).toBeGreaterThan(0);
  });

  it("is also valid under strict mode (no forbidden fields, no missing rationale)", () => {
    const markdown = fs.readFileSync(docPath, "utf8");
    const [example] = extractJsonFencedBlocks(markdown);
    const result = parseAgentResponse(example, "strict");
    expect(result.ok).toBe(true);
  });
});
