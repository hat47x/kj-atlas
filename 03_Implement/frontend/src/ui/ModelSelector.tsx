import type { ChangeEvent } from "react";
import type { AvailableModelItem } from "../api/client";
import { t } from "../i18n/translate";

// AI-MODEL-GOVERNANCE-01 (R2): a per-operation model selector.
//
// Presentational: the caller (App) owns the data fetch through the guarded
// tenant-session wrapper and passes the tenant's allowed ACTIVE models here.
// Offers an "auto" (platform default) option plus each allowed model. "" means
// auto — the backend falls back to the resolved default. When no models are
// listed (or they are still loading) the selector collapses to nothing/disabled
// so the operation is never blocked by model listing.
type ModelSelectorProps = {
  label: string;
  value: string;
  onChange: (model: string) => void;
  disabled?: boolean;
  dataUiRegion?: string;
  /** Tenant-allowed active models; null = still loading. */
  models: AvailableModelItem[] | null;
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

export function ModelSelector({ label, value, onChange, disabled, dataUiRegion, models }: ModelSelectorProps) {
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
    return null;
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
