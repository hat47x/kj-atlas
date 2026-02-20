import { describe, expect, test } from "vitest";
import { sanitizeMarkdownForDisplay } from "./markdown_sanitize";

describe("sanitizeMarkdownForDisplay", () => {
  test("removes raw html tags including scripts", () => {
    const source = "# title\n<script>alert('xss')</script><b>bold</b>";
    const sanitized = sanitizeMarkdownForDisplay(source);

    expect(sanitized).not.toContain("<script>");
    expect(sanitized).not.toContain("</script>");
    expect(sanitized).not.toContain("<b>");
    expect(sanitized).toContain("alert('xss')");
    expect(sanitized).toContain("bold");
  });
});
