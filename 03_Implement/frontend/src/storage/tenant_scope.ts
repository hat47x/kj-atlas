export type TenantBrowserStorageScope = Readonly<{
  deployment: string;
  tenantId: string;
  principalId: string;
}>;

type StorageKeyIndex = Pick<Storage, "key" | "length" | "removeItem">;

const TENANT_SCOPE_PREFIX = "kj-atlas/tenant-scope/v1";
const INVALID_SCOPE_CHARACTER = /[\u0000-\u001f\u007f]/;

function encodeRequiredPart(name: string, value: string): string {
  if (!value || value.trim() !== value || INVALID_SCOPE_CHARACTER.test(value)) {
    throw new Error(`${name} must be a non-empty canonical storage scope value`);
  }
  return encodeURIComponent(value);
}

export function buildTenantStoragePrefix(scope: TenantBrowserStorageScope): string {
  const deployment = encodeRequiredPart("deployment", scope.deployment);
  const tenantId = encodeRequiredPart("tenantId", scope.tenantId);
  const principalId = encodeRequiredPart("principalId", scope.principalId);
  return `${TENANT_SCOPE_PREFIX}/${deployment}/${tenantId}/${principalId}/`;
}

export function buildTenantStorageKey(
  baseKey: string,
  scope: TenantBrowserStorageScope,
): string {
  return `${buildTenantStoragePrefix(scope)}${encodeRequiredPart("baseKey", baseKey)}`;
}

export function clearTenantScopedStorage(
  storage: StorageKeyIndex,
  scope: TenantBrowserStorageScope,
): number {
  const prefix = buildTenantStoragePrefix(scope);
  const keysToRemove: string[] = [];

  for (let index = 0; index < storage.length; index += 1) {
    const key = storage.key(index);
    if (key?.startsWith(prefix)) {
      keysToRemove.push(key);
    }
  }

  for (const key of keysToRemove) {
    storage.removeItem(key);
  }
  return keysToRemove.length;
}
