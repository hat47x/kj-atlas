export type SafeModeIndicatorTone = "safe" | "warning";

export type SafeModeIndicator = {
  label: string;
  detail: string;
  tone: SafeModeIndicatorTone;
};

export function getSafeModeIndicator(safeMode: boolean): SafeModeIndicator {
  if (safeMode) {
    return {
      label: "SafeMode: ON",
      detail: "Sensitive text is redacted in export/share contexts.",
      tone: "safe",
    };
  }

  return {
    label: "SafeMode: OFF",
    detail: "Raw text can be exported; verify before sharing.",
    tone: "warning",
  };
}

export function getSafeModeLockedContextLabel(): string {
  return "Locked redaction contexts: Share / Review Pack (cannot be disabled).";
}

export function getExportSafetyWarning(safeMode: boolean): string {
  if (safeMode) {
    return "SafeMode is ON. Exported summaries stay privacy-first by default.";
  }

  return "SafeMode is OFF. Exports may include raw text. Re-enable SafeMode before external sharing.";
}
