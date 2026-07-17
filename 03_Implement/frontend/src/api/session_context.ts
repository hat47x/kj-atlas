import {
  buildTenantStoragePrefix,
  type TenantBrowserStorageScope,
} from "../storage/tenant_scope";

export type TenantSessionSummaryV1 = Readonly<{
  id: string;
  displayName: string;
}>;

export const EFFECTIVE_CAPABILITIES = [
  "document.read",
  "document.write",
  "document.export",
  "document.share",
  "document.policy.manage",
  "membership.provision",
  "agent.register",
  "agent.revoke",
  "audit.read",
  "tenant.provision",
  "tenant.suspend",
] as const;

export type EffectiveCapability = (typeof EFFECTIVE_CAPABILITIES)[number];

const EFFECTIVE_CAPABILITY_SET = new Set<string>(EFFECTIVE_CAPABILITIES);

export type TenantSessionContextV1 = Readonly<{
  principalId: string;
  activeTenant: TenantSessionSummaryV1;
  availableTenants: readonly TenantSessionSummaryV1[];
  effectiveCapabilities: readonly EffectiveCapability[];
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

function hasExactKeys(value: Record<string, unknown>, expectedKeys: readonly string[]): boolean {
  const actualKeys = Object.keys(value);
  const expectedKeySet = new Set(expectedKeys);
  return actualKeys.length === expectedKeys.length
    && actualKeys.every((key) => expectedKeySet.has(key));
}

function effectiveCapability(value: unknown): EffectiveCapability {
  const capability = canonicalString(value);
  if (!EFFECTIVE_CAPABILITY_SET.has(capability)) {
    throw new InvalidTenantSessionContextError();
  }
  return capability as EffectiveCapability;
}

function parseTenantSummary(value: unknown): TenantSessionSummaryV1 {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new InvalidTenantSessionContextError();
  }
  const candidate = value as Record<string, unknown>;
  if (!hasExactKeys(candidate, ["displayName", "id"])) {
    throw new InvalidTenantSessionContextError();
  }
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
  if (!hasExactKeys(candidate, [
    "activeTenant",
    "availableTenants",
    "capabilityVersion",
    "effectiveCapabilities",
    "principalId",
  ])) {
    throw new InvalidTenantSessionContextError();
  }
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

  const effectiveCapabilities = [...new Set(
    candidate.effectiveCapabilities.map(effectiveCapability),
  )].sort();
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
