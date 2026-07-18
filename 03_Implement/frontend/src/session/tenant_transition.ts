import {
  buildBrowserStorageScopeFromSession,
  parseTenantSessionContext,
} from "../api/session_context";
import {
  clearTenantScopedStorage,
  type TenantBrowserStorageScope,
} from "../storage/tenant_scope";

type TenantScopedStorage = Pick<Storage, "key" | "length" | "removeItem">;

export type TenantTransitionCleanup = () => void;

export type TenantSessionTransitionResult = Readonly<{
  nextScope: TenantBrowserStorageScope;
  clearedStorageEntries: number;
  cleanupFailureCount: number;
  storageClearFailed: boolean;
}>;

export function replaceCurrentDocument(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.location.replace(window.location.href);
}

export function executeTenantSessionTransition(input: {
  nextSessionContext: unknown;
  deployment: string;
  previousScope: TenantBrowserStorageScope;
  storage?: TenantScopedStorage;
  clearPreviousScope?: () => number;
  cleanupSteps: readonly TenantTransitionCleanup[];
  replaceDocument?: () => void;
}): TenantSessionTransitionResult {
  const nextSessionContext = parseTenantSessionContext(input.nextSessionContext);
  const nextScope = buildBrowserStorageScopeFromSession(
    nextSessionContext,
    input.deployment,
  );

  let cleanupFailureCount = 0;
  for (const cleanup of input.cleanupSteps) {
    try {
      cleanup();
    } catch {
      cleanupFailureCount += 1;
    }
  }

  let clearedStorageEntries = 0;
  let storageClearFailed = false;
  try {
    if (input.clearPreviousScope) {
      clearedStorageEntries = input.clearPreviousScope();
    } else if (input.storage) {
      clearedStorageEntries = clearTenantScopedStorage(input.storage, input.previousScope);
    } else {
      throw new Error("tenant storage cleanup unavailable");
    }
  } catch {
    storageClearFailed = true;
  }

  (input.replaceDocument ?? replaceCurrentDocument)();
  return {
    nextScope,
    clearedStorageEntries,
    cleanupFailureCount,
    storageClearFailed,
  };
}
