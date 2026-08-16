import { useEffect, type ChangeEvent } from "react";
import type {
  AvailableModelItem,
  AvailableModelUnavailableReason,
} from "../api/client";
import { t } from "../i18n/translate";

// AI-MODEL-GOVERNANCE-01 (R2): a per-operation model selector.
//
// Presentational: the caller (App) owns the data fetch through the guarded
// tenant-session wrapper and passes the tenant's allowed ACTIVE models here.
// Offers an "auto" (platform default) option plus each allowed model. "" means
// auto — the backend falls back to the resolved default. When no models are
// listed, keep a disabled status visible so an operator-side allowlist mistake
// is distinguishable from a feature that does not support model selection.
type ModelSelectorProps = {
  label: string;
  value: string;
  onChange: (model: string) => void;
  disabled?: boolean;
  dataUiRegion?: string;
  /** Tenant-allowed active models; null = still loading. */
  models: AvailableModelItem[] | null;
  unavailableReason?: AvailableModelUnavailableReason | null;
};

const selectStyle = {
  border: "1px solid #cbd5e1",
  borderRadius: 6,
  backgroundColor: "#ffffff",
  color: "#0f172a",
  padding: "4px 8px",
  fontSize: 12,
  cursor: "pointer",
  maxWidth: 220,
} as const;

export function reconcileModelSelection(value: string, models: AvailableModelItem[] | null): string {
  if (models === null || value === "" || models.some((model) => model.id === value)) {
    return value;
  }
  return "";
}

const unavailableReasonTranslationKeys: Record<AvailableModelUnavailableReason, string> = {
  no_active_models: "model_selector.reason.no_active_models",
  provider_unavailable: "model_selector.reason.provider_unavailable",
  tenant_policy_excludes_all: "model_selector.reason.tenant_policy_excludes_all",
  no_user_selectable_models: "model_selector.reason.no_user_selectable_models",
};

export function ModelSelector({
  label,
  value,
  onChange,
  disabled,
  dataUiRegion,
  models,
  unavailableReason,
}: ModelSelectorProps) {
  useEffect(() => {
    const reconciled = reconcileModelSelection(value, models);
    if (reconciled !== value) {
      onChange(reconciled);
    }
  }, [models, onChange, value]);

  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    onChange(event.target.value);
  };

  if (models === null) {
    return (
      <label style={{ display: "grid", gap: 4 }} data-ui-region={dataUiRegion}>
        <span style={{ fontSize: 11, fontWeight: 600, color: "#334155" }}>{label}</span>
        <select style={{ ...selectStyle, opacity: 0.5 }} disabled value="">
          <option value="">{t("model_selector.auto")}</option>
        </select>
      </label>
    );
  }

  if (models.length === 0) {
    const reasonKey = unavailableReason
      ? unavailableReasonTranslationKeys[unavailableReason]
      : "model_selector.none_available_help";
    return (
      <label style={{ display: "grid", gap: 4 }} data-ui-region={dataUiRegion}>
        <span style={{ fontSize: 11, fontWeight: 600, color: "#334155" }}>{label}</span>
        <select
          style={{ ...selectStyle, opacity: 0.65, cursor: "not-allowed" }}
          disabled
          value=""
          aria-label={label}
        >
          <option value="">{t("model_selector.none_available")}</option>
        </select>
        <span role="status" style={{ maxWidth: 340, fontSize: 11, lineHeight: 1.4, color: "#64748b" }}>
          {t(reasonKey)}
        </span>
      </label>
    );
  }

  return (
    <label style={{ display: "grid", gap: 4 }} data-ui-region={dataUiRegion}>
      <span style={{ fontSize: 11, fontWeight: 600, color: "#334155" }}>{label}</span>
      <select style={selectStyle} value={value} onChange={handleChange} disabled={disabled} aria-label={label}>
        <option value="">{t("model_selector.auto")}</option>
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.displayName}
          </option>
        ))}
      </select>
    </label>
  );
}
