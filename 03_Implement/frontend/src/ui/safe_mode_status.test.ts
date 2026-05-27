import { afterEach, describe, expect, it } from "vitest";
import { setActiveLocale } from "../i18n/translate";
import { getExportSafetyWarning, getSafeModeIndicator, getSafeModeLockedContextLabel } from "./safe_mode_status";

afterEach(() => {
  setActiveLocale("ja");
});

describe("safe_mode_status", () => {
  it("returns safe indicator details in Japanese by default", () => {
    expect(getSafeModeIndicator(true)).toEqual({
      label: "セーフモード: ON",
      detail: "書き出しや共有の場面では機微テキストをマスクします。",
      tone: "safe",
    });
    expect(getExportSafetyWarning(true)).toBe("セーフモードが ON です。書き出した要約は既定でプライバシー優先になります。");
  });

  it("returns warning indicator details in English when locale switched", () => {
    setActiveLocale("en");

    expect(getSafeModeIndicator(false)).toEqual({
      label: "SafeMode: OFF",
      detail: "Raw text can be exported; verify before sharing.",
      tone: "warning",
    });
    expect(getExportSafetyWarning(false)).toBe("SafeMode is OFF. Exports may include raw text. Re-enable SafeMode before external sharing.");
  });

  it("shows locked redaction contexts copy in English", () => {
    setActiveLocale("en");
    expect(getSafeModeLockedContextLabel()).toBe("Locked redaction contexts: Share / Review Pack (cannot be disabled).");
  });
});
