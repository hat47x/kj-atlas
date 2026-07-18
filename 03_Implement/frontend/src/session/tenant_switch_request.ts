import { changeActiveTenant } from "../api/client";
import {
  InvalidTenantSessionContextError,
  buildBrowserStorageScopeFromSession,
  parseTenantSessionContext,
  type TenantSessionContextV1,
} from "../api/session_context";
import type { TenantBrowserStorageScope } from "../storage/tenant_scope";
import {
  executeTenantSessionTransition,
  type TenantSessionTransitionResult,
  type TenantTransitionCleanup,
} from "./tenant_transition";

type TenantScopedStorage = Pick<Storage, "key" | "length" | "removeItem">;

export type TenantSwitchUnsavedDecision = "save" | "discard" | "cancel";

export type TenantSwitchRequestResult =
  | Readonly<{ status: "unchanged" }>
  | Readonly<{ status: "cancelled" }>
  | Readonly<{ status: "save-failed" }>
  | Readonly<{
    status: "transitioned";
    transition: TenantSessionTransitionResult;
  }>;

export type ActiveTenantChanger = (
  currentSessionContext: TenantSessionContextV1,
  requestedTenantId: string,
  options: Readonly<{ signal?: AbortSignal }>,
) => Promise<unknown>;

function scopesMatch(
  actual: TenantBrowserStorageScope,
  expected: TenantBrowserStorageScope,
): boolean {
  return actual.deployment === expected.deployment
    && actual.principalId === expected.principalId
    && actual.tenantId === expected.tenantId;
}

function selectedTenantId(
  currentSessionContext: TenantSessionContextV1,
  requestedTenantId: string,
): string | null {
  if (requestedTenantId === currentSessionContext.activeTenant.id) {
    return null;
  }
  const selectedTenant = currentSessionContext.availableTenants.find(
    (tenant) => tenant.id === requestedTenantId,
  );
  if (!selectedTenant) {
    throw new InvalidTenantSessionContextError();
  }
  return selectedTenant.id;
}

export async function requestTenantSessionTransition(input: Readonly<{
  currentSessionContext: unknown;
  requestedTenantId: string;
  deployment: string;
  previousScope: TenantBrowserStorageScope;
  storage: TenantScopedStorage;
  cleanupSteps: readonly TenantTransitionCleanup[];
  hasUnsavedChanges: boolean;
  requestUnsavedDecision?: () => Promise<unknown>;
  saveUnsavedChanges?: () => Promise<boolean>;
  changeTenant?: ActiveTenantChanger;
  signal: AbortSignal;
  replaceDocument?: () => void;
}>): Promise<TenantSwitchRequestResult> {
  input.signal.throwIfAborted();
  const currentSession = parseTenantSessionContext(input.currentSessionContext);
  const requestedTenantId = selectedTenantId(
    currentSession,
    input.requestedTenantId,
  );
  if (requestedTenantId === null) {
    return { status: "unchanged" };
  }

  const expectedPreviousScope = buildBrowserStorageScopeFromSession(
    currentSession,
    input.deployment,
  );
  if (!scopesMatch(input.previousScope, expectedPreviousScope)) {
    throw new InvalidTenantSessionContextError();
  }

  if (input.hasUnsavedChanges) {
    if (!input.requestUnsavedDecision) {
      throw new InvalidTenantSessionContextError();
    }
    const decision = await input.requestUnsavedDecision();
    input.signal.throwIfAborted();
    if (decision === "cancel") {
      return { status: "cancelled" };
    }
    if (decision === "save") {
      if (!input.saveUnsavedChanges) {
        throw new InvalidTenantSessionContextError();
      }
      if (!await input.saveUnsavedChanges()) {
        return { status: "save-failed" };
      }
      input.signal.throwIfAborted();
    } else if (decision !== "discard") {
      throw new InvalidTenantSessionContextError();
    }
  }

  const nextSessionResponse = await (input.changeTenant ?? changeActiveTenant)(
    currentSession,
    requestedTenantId,
    { signal: input.signal },
  );
  const nextSession = parseTenantSessionContext(nextSessionResponse);
  if (
    nextSession.principalId !== currentSession.principalId
    || nextSession.activeTenant.id !== requestedTenantId
  ) {
    throw new InvalidTenantSessionContextError();
  }

  // Once the server-confirmed session has changed, replacement must proceed
  // even if the initiating component was aborted. Keeping the old tenant DOM
  // after a verified session change would be the less safe outcome.
  return {
    status: "transitioned",
    transition: executeTenantSessionTransition({
      nextSessionContext: nextSession,
      deployment: input.deployment,
      previousScope: input.previousScope,
      storage: input.storage,
      cleanupSteps: input.cleanupSteps,
      replaceDocument: input.replaceDocument,
    }),
  };
}
