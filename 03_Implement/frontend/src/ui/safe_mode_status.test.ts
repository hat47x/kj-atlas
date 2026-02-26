import { describe, expect, it } from "vitest";
import { getExportSafetyWarning, getSafeModeIndicator, getSafeModeLockedContextLabel } from "./safe_mode_status";

describe("safe_mode_status", () => {
  it("returns safe indicator details when safe mode is on", () => {
    expect(getSafeModeIndicator(true)).toEqual({
      label: "SafeMode: ON",
      detail: "Sensitive text is redacted in export/share contexts.",
      tone: "safe",
    });
    expect(getExportSafetyWarning(true)).toBe("SafeMode is ON. Exported summaries stay privacy-first by default.");
  });

  it("returns warning indicator details when safe mode is off", () => {
    expect(getSafeModeIndicator(false)).toEqual({
      label: "SafeMode: OFF",
      detail: "Raw text can be exported; verify before sharing.",
      tone: "warning",
    });
    expect(getExportSafetyWarning(false)).toBe("SafeMode is OFF. Exports may include raw text. Re-enable SafeMode before external sharing.");
  });

  it("shows locked redaction contexts copy", () => {
    expect(getSafeModeLockedContextLabel()).toBe("Locked redaction contexts: Share / Review Pack (cannot be disabled).");
  });
});
