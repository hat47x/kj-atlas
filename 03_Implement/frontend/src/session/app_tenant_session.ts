import {
  InvalidTenantSessionContextError,
  buildBrowserStorageScopeFromSession,
  parseTenantSessionContext,
  type TenantSessionContextV1,
} from "../api/session_context";
import type { TenantBrowserStorageScope } from "../storage/tenant_scope";

function scopesMatch(
  actual: TenantBrowserStorageScope,
  expected: TenantBrowserStorageScope,
): boolean {
  return actual.deployment === expected.deployment
    && actual.principalId === expected.principalId
    && actual.tenantId === expected.tenantId;
}

export function resolveAppTenantSession(input: Readonly<{
  sessionContext?: unknown;
  storageScope?: TenantBrowserStorageScope;
}>): TenantSessionContextV1 | undefined {
  if (input.sessionContext === undefined) {
    return undefined;
  }
  if (!input.storageScope) {
    throw new InvalidTenantSessionContextError();
  }

  const sessionContext = parseTenantSessionContext(input.sessionContext);
  const expectedScope = buildBrowserStorageScopeFromSession(
    sessionContext,
    input.storageScope.deployment,
  );
  if (!scopesMatch(input.storageScope, expectedScope)) {
    throw new InvalidTenantSessionContextError();
  }
  return sessionContext;
}
