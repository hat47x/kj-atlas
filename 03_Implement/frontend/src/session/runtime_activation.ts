import { getTenantSessionBootstrapPolicy } from "../api/client";
import { parseTenantSessionBootstrapPolicy } from "../api/session_bootstrap_policy";

export type RuntimeEntryMode =
  | "single-tenant"
  | "tenant-session-required"
  | "invalid";

export type TenantSessionBootstrapPolicyLoader = (
  options: Readonly<{ signal?: AbortSignal }>,
) => Promise<unknown>;

export function resolveRuntimeEntryMode(runtimeProfile: unknown): RuntimeEntryMode {
  if (
    runtimeProfile === undefined
    || runtimeProfile === "local-dev"
    || runtimeProfile === "evaluation"
    || runtimeProfile === "enterprise-production"
  ) {
    return "single-tenant";
  }
  if (runtimeProfile === "saas-multitenant") {
    return "tenant-session-required";
  }
  return "invalid";
}

function isAbortFailure(error: unknown, signal: AbortSignal): boolean {
  return signal.aborted || Boolean(
    error
    && typeof error === "object"
    && "name" in error
    && error.name === "AbortError",
  );
}

export async function verifyTenantSessionRuntimePolicy(input: Readonly<{
  signal: AbortSignal;
  loadPolicy?: TenantSessionBootstrapPolicyLoader;
}>): Promise<boolean> {
  input.signal.throwIfAborted();
  try {
    const rawPolicy = await (input.loadPolicy ?? getTenantSessionBootstrapPolicy)({
      signal: input.signal,
    });
    input.signal.throwIfAborted();
    const policy = parseTenantSessionBootstrapPolicy(rawPolicy);
    return policy.tenantSessionMode === "tenant-session-required";
  } catch (error) {
    if (isAbortFailure(error, input.signal)) {
      throw error;
    }
    return false;
  }
}
