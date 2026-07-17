import {
  buildTenantStoragePrefix,
  type TenantBrowserStorageScope,
} from "../storage/tenant_scope";

export type TenantSessionSummaryV1 = Readonly<{
  id: string;
  displayName: string;
}>;

export type TenantSessionContextV1 = Readonly<{
  principalId: string;
  activeTenant: TenantSessionSummaryV1;
  availableTenants: readonly TenantSessionSummaryV1[];
  effectiveCapabilities: readonly string[];
  capabilityVersion: string;
}>;

export class InvalidTenantSessionContextError extends Error {
  constructor() {
    super("Invalid tenant session context");
    this.name = "InvalidTenantSessionContextError";
  }
}

const INVALID_CANONICAL_CHARACTER = /[\u0000-\u001f\u007f]/;

function canonicalString(value: unknown): string {
  if (
    typeof value !== "string"
    || value.length === 0
    || value.trim() !== value
    || INVALID_CANONICAL_CHARACTER.test(value)
  ) {
    throw new InvalidTenantSessionContextError();
  }
  return value;
}

function parseTenantSummary(value: unknown): TenantSessionSummaryV1 {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new InvalidTenantSessionContextError();
  }
  const candidate = value as Record<string, unknown>;
  return {
    id: canonicalString(candidate.id),
    displayName: canonicalString(candidate.displayName),
  };
}

export function parseTenantSessionContext(value: unknown): TenantSessionContextV1 {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new InvalidTenantSessionContextError();
  }
  const candidate = value as Record<string, unknown>;
  if (!Array.isArray(candidate.availableTenants) || !Array.isArray(candidate.effectiveCapabilities)) {
    throw new InvalidTenantSessionContextError();
  }

  const activeTenant = parseTenantSummary(candidate.activeTenant);
  const availableTenants = candidate.availableTenants.map(parseTenantSummary);
  const tenantById = new Map<string, TenantSessionSummaryV1>();
  for (const tenant of availableTenants) {
    if (tenantById.has(tenant.id)) {
      throw new InvalidTenantSessionContextError();
    }
    tenantById.set(tenant.id, tenant);
  }
  const allowlistedActiveTenant = tenantById.get(activeTenant.id);
  if (!allowlistedActiveTenant || allowlistedActiveTenant.displayName !== activeTenant.displayName) {
    throw new InvalidTenantSessionContextError();
  }

  const effectiveCapabilities = [...new Set(candidate.effectiveCapabilities.map(canonicalString))].sort();
  return {
    principalId: canonicalString(candidate.principalId),
    activeTenant,
    availableTenants,
    effectiveCapabilities,
    capabilityVersion: canonicalString(candidate.capabilityVersion),
  };
}

export function buildBrowserStorageScopeFromSession(
  sessionContext: TenantSessionContextV1,
  deployment: string,
): TenantBrowserStorageScope {
  const scope: TenantBrowserStorageScope = {
    deployment,
    tenantId: sessionContext.activeTenant.id,
    principalId: sessionContext.principalId,
  };
  buildTenantStoragePrefix(scope);
  return scope;
}
