// DOGFOOD-06: extract the client-side interpretation of a get_context_projection
// tool result into a pure, unit-testable function. The standalone verify_mcp.ts
// script uses this; the abnormal cases (isError / not_found) are asserted here
// so the DOGFOOD-03 fix (respect the server's isError contract instead of
// JSON.parsing the error text) is locked against regression.

export type ProjectionOutcome = "ok" | "not_found" | "error";

export type InterpretedResult = {
  outcome: ProjectionOutcome;
  /** Plain-text message when the tool reported an error (not a projection). */
  errorMessage: string | null;
  /** The projection JSON when outcome === "ok". */
  projection: unknown | null;
};

/**
 * Interpret the raw text content of a get_context_projection tool result.
 *
 * The MCP server contract (context_projection_tool.ts): on success it returns
 * { isError: false, content: [{ type: "text", text: <projection JSON> }] }; on
 * not_found / error it returns { isError: true, content: [{ type: "text",
 * text: <plain message> }] }. The client must NOT JSON.parse the error text.
 *
 * @param text      The tool result's text content (already extracted).
 * @param isError   The MCP result's isError flag.
 */
export function interpretProjectionResult(text: string, isError: boolean): InterpretedResult {
  if (isError === true) {
    const isNotFound =
      text.includes("DocumentNotFound") || text.includes("not found") || text.includes("404");
    return {
      outcome: isNotFound ? "not_found" : "error",
      errorMessage: text,
      projection: null,
    };
  }
  try {
    return { outcome: "ok", errorMessage: null, projection: JSON.parse(text) };
  } catch (error) {
    // A success-flagged result that is not valid JSON is a real client bug.
    const message = error instanceof Error ? error.message : String(error);
    return { outcome: "error", errorMessage: `invalid projection JSON: ${message}`, projection: null };
  }
}
