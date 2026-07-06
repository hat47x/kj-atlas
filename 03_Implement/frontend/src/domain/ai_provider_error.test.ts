import { describe, expect, it } from "vitest";

import { ApiError } from "../api/client";
import { classifyAiProviderError } from "./ai_provider_error";

// PROV-ERROR-01 (ADR-0050 D2): classification must use the structured
// code/disabledReason fields, not a regex over the error message text.

describe("classifyAiProviderError", () => {
  it("classifies a disabled provider (provider=none) even with an unrelated message", () => {
    const error = new ApiError(503, "some unrelated text", {
      code: "provider_unavailable",
      disabledReason: "provider_disabled_or_none_default",
    });
    expect(classifyAiProviderError(error)).toBe("disabled");
  });

  it("classifies provider_timeout", () => {
    const error = new ApiError(504, "local request timed out", { code: "provider_timeout" });
    expect(classifyAiProviderError(error)).toBe("timeout");
  });

  it("classifies provider_validation", () => {
    const error = new ApiError(422, "local response missing text field", { code: "provider_validation" });
    expect(classifyAiProviderError(error)).toBe("validation");
  });

  it("classifies provider_unavailable (configured but unreachable) distinctly from disabled", () => {
    const error = new ApiError(503, "local request failed: Connection refused", { code: "provider_unavailable" });
    expect(classifyAiProviderError(error)).toBe("unavailable");
  });

  it("does not misclassify a raw exception message that happens to contain 'disabled'", () => {
    // Regression guard for the old regex bug: a plain message must NOT be
    // enough to trigger "disabled" without the structured disabledReason.
    const error = new ApiError(503, "provider seems disabled or unreachable", { code: "provider_unavailable" });
    expect(classifyAiProviderError(error)).toBe("unavailable");
  });

  it("falls back to unknown for non-ApiError values", () => {
    expect(classifyAiProviderError(new Error("network down"))).toBe("unknown");
    expect(classifyAiProviderError("not an error")).toBe("unknown");
  });

  it("falls back to unknown for an ApiError with no provider code", () => {
    const error = new ApiError(400, "bad request");
    expect(classifyAiProviderError(error)).toBe("unknown");
  });
});
