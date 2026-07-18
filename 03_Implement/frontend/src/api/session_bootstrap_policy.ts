export type TenantSessionBootstrapMode =
  | "single-tenant"
  | "tenant-session-required";

export type TenantSessionBootstrapPolicyV1 = Readonly<{
  tenantSessionMode: TenantSessionBootstrapMode;
}>;

export class InvalidTenantSessionBootstrapPolicyError extends Error {
  constructor() {
    super("Invalid tenant session bootstrap policy");
    this.name = "InvalidTenantSessionBootstrapPolicyError";
  }
}

export function parseTenantSessionBootstrapPolicy(
  value: unknown,
): TenantSessionBootstrapPolicyV1 {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new InvalidTenantSessionBootstrapPolicyError();
  }
  const candidate = value as Record<string, unknown>;
  const keys = Object.keys(candidate);
  if (keys.length !== 1 || keys[0] !== "tenantSessionMode") {
    throw new InvalidTenantSessionBootstrapPolicyError();
  }
  if (
    candidate.tenantSessionMode !== "single-tenant"
    && candidate.tenantSessionMode !== "tenant-session-required"
  ) {
    throw new InvalidTenantSessionBootstrapPolicyError();
  }
  return { tenantSessionMode: candidate.tenantSessionMode };
}
