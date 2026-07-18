import type { ChangeEvent } from "react";

import {
  parseTenantSessionContext,
  type TenantSessionContextV1,
} from "../api/session_context";
import { t } from "../i18n/translate";

type TenantSessionControlProps = Readonly<{
  sessionContext: TenantSessionContextV1;
  isChanging?: boolean;
  onRequestTenantChange: (tenantId: string) => void;
}>;

export function resolveAllowedTenantSelection(
  sessionContext: unknown,
  requestedTenantId: string,
): string | null {
  try {
    const verifiedSession = parseTenantSessionContext(sessionContext);
    const selectedTenant = verifiedSession.availableTenants.find(
      (tenant) => tenant.id === requestedTenantId,
    );
    if (!selectedTenant || selectedTenant.id === verifiedSession.activeTenant.id) {
      return null;
    }
    return selectedTenant.id;
  } catch {
    return null;
  }
}

const controlStyle = {
  minWidth: 0,
  display: "flex",
  alignItems: "center",
  gap: 8,
  color: "#334155",
  fontSize: 13,
} as const;

const nameStyle = {
  maxWidth: 220,
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
  color: "#0f172a",
  fontWeight: 600,
} as const;

export function TenantSessionControl({
  sessionContext,
  isChanging = false,
  onRequestTenantChange,
}: TenantSessionControlProps) {
  const verifiedSession = parseTenantSessionContext(sessionContext);
  const activeTenant = verifiedSession.activeTenant;
  const accessibleName = t("tenant_session.control.active_aria", {
    name: activeTenant.displayName,
  });

  if (verifiedSession.availableTenants.length === 1) {
    return (
      <div style={controlStyle} aria-label={accessibleName} data-tenant-control="label">
        <span>{t("tenant_session.control.scope_label")}</span>
        <span style={nameStyle} title={activeTenant.displayName}>
          {activeTenant.displayName}
        </span>
      </div>
    );
  }

  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const selectedTenantId = resolveAllowedTenantSelection(
      verifiedSession,
      event.currentTarget.value,
    );
    if (selectedTenantId) {
      onRequestTenantChange(selectedTenantId);
    }
  };

  return (
    <label style={controlStyle} data-tenant-control="switcher">
      <span>{t("tenant_session.control.scope_label")}</span>
      <select
        value={activeTenant.id}
        onChange={handleChange}
        disabled={isChanging}
        aria-label={accessibleName}
        aria-busy={isChanging}
        style={{
          minWidth: 0,
          maxWidth: 240,
          border: "1px solid #cbd5e1",
          borderRadius: 7,
          padding: "5px 28px 5px 8px",
          background: "#ffffff",
          color: "#0f172a",
          font: "inherit",
        }}
      >
        {verifiedSession.availableTenants.map((tenant) => (
          <option key={tenant.id} value={tenant.id}>
            {tenant.displayName}
          </option>
        ))}
      </select>
      {isChanging ? (
        <span role="status" aria-live="polite">
          {t("tenant_session.control.changing")}
        </span>
      ) : null}
    </label>
  );
}
