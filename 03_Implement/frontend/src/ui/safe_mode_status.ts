import { t } from "../i18n/translate";

export type SafeModeIndicatorTone = "safe" | "warning";

export type SafeModeIndicator = {
  label: string;
  detail: string;
  tone: SafeModeIndicatorTone;
};

export function getSafeModeIndicator(safeMode: boolean): SafeModeIndicator {
  if (safeMode) {
    return {
      label: t("safe_mode.indicator.on.label"),
      detail: t("safe_mode.indicator.on.detail"),
      tone: "safe",
    };
  }

  return {
    label: t("safe_mode.indicator.off.label"),
    detail: t("safe_mode.indicator.off.detail"),
    tone: "warning",
  };
}

export function getSafeModeLockedContextLabel(): string {
  return t("safe_mode.locked_contexts");
}

export function getExportSafetyWarning(safeMode: boolean): string {
  if (safeMode) {
    return t("safe_mode.export_warning.on");
  }

  return t("safe_mode.export_warning.off");
}
