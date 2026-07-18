import {
  ApiError,
  getTenantSessionContext,
} from "../api/client";
import {
  InvalidTenantSessionContextError,
  buildBrowserStorageScopeFromSession,
  parseTenantSessionContext,
  type TenantSessionContextV1,
} from "../api/session_context";
import type { TenantBrowserStorageScope } from "../storage/tenant_scope";

export type TenantSessionBlockReason =
  | "authentication_required"
  | "access_denied"
  | "session_unavailable"
  | "invalid_session_response"
  | "invalid_deployment";

export type TenantSessionBootstrapResult =
  | Readonly<{
    status: "ready";
    sessionContext: TenantSessionContextV1;
    storageScope: TenantBrowserStorageScope;
  }>
  | Readonly<{
    status: "blocked";
    reason: TenantSessionBlockReason;
  }>;

export type TenantSessionContextLoader = (
  options: Readonly<{ signal?: AbortSignal }>,
) => Promise<unknown>;

function isAbortFailure(error: unknown, signal: AbortSignal): boolean {
  if (signal.aborted) {
    return true;
  }
  return Boolean(
    error
    && typeof error === "object"
    && "name" in error
    && error.name === "AbortError",
  );
}

function blockReasonFor(error: unknown): TenantSessionBlockReason {
  if (error instanceof InvalidTenantSessionContextError) {
    return "invalid_session_response";
  }
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "authentication_required";
    }
    if (error.status === 403) {
      return "access_denied";
    }
  }
  return "session_unavailable";
}

export async function bootstrapTenantSession(input: Readonly<{
  deployment: string;
  signal: AbortSignal;
  loadSessionContext?: TenantSessionContextLoader;
}>): Promise<TenantSessionBootstrapResult> {
  input.signal.throwIfAborted();

  let sessionContext: TenantSessionContextV1;
  try {
    const response = await (
      input.loadSessionContext ?? getTenantSessionContext
    )({ signal: input.signal });
    input.signal.throwIfAborted();
    sessionContext = parseTenantSessionContext(response);
  } catch (error) {
    if (isAbortFailure(error, input.signal)) {
      throw error;
    }
    return { status: "blocked", reason: blockReasonFor(error) };
  }

  try {
    return {
      status: "ready",
      sessionContext,
      storageScope: buildBrowserStorageScopeFromSession(
        sessionContext,
        input.deployment,
      ),
    };
  } catch {
    return { status: "blocked", reason: "invalid_deployment" };
  }
}
