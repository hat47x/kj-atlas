export type TenantSessionInvalidationReason =
  | "cross-tab"
  | "bfcache"
  | "online"
  | "resume";

type EventTargetLike = Readonly<{
  addEventListener: (type: string, listener: EventListener) => void;
  removeEventListener: (type: string, listener: EventListener) => void;
}>;

type VisibilityTargetLike = EventTargetLike & Readonly<{
  visibilityState: string;
}>;

type BroadcastChannelLike = Readonly<{
  addEventListener: (type: "message", listener: EventListener) => void;
  removeEventListener: (type: "message", listener: EventListener) => void;
  postMessage: (message: null) => void;
  close: () => void;
}>;

export type TenantSessionCoherenceBoundary = Readonly<{
  publishSessionChanged: () => boolean;
  dispose: () => void;
}>;

const CHANNEL_NAME = "kj-atlas-tenant-session-v1";
const DEFAULT_HIDDEN_REVALIDATION_MS = 5 * 60 * 1000;

function defaultChannelFactory(name: string): BroadcastChannelLike | undefined {
  if (typeof BroadcastChannel !== "function") {
    return undefined;
  }
  return new BroadcastChannel(name) as unknown as BroadcastChannelLike;
}

/**
 * Invalidates a mounted tenant scope when shared browser-session context may
 * have changed. Cross-tab messages deliberately contain no principal, tenant,
 * capability, content, or raw session-version data. The server precondition
 * remains authoritative when notification delivery is unavailable.
 */
export function installTenantSessionCoherenceBoundary(input: Readonly<{
  onInvalidate: (reason: TenantSessionInvalidationReason) => void;
  hiddenRevalidationMs?: number;
  now?: () => number;
  windowTarget?: EventTargetLike;
  documentTarget?: VisibilityTargetLike;
  createChannel?: (name: string) => BroadcastChannelLike | undefined;
}>): TenantSessionCoherenceBoundary {
  const hiddenRevalidationMs = input.hiddenRevalidationMs
    ?? DEFAULT_HIDDEN_REVALIDATION_MS;
  if (!Number.isFinite(hiddenRevalidationMs) || hiddenRevalidationMs < 0) {
    throw new TypeError("Invalid tenant session resume threshold");
  }

  const now = input.now ?? Date.now;
  const windowTarget = input.windowTarget
    ?? (window as unknown as EventTargetLike);
  const documentTarget = input.documentTarget
    ?? (document as unknown as VisibilityTargetLike);
  let channel: BroadcastChannelLike | undefined;
  try {
    channel = (input.createChannel ?? defaultChannelFactory)(CHANNEL_NAME);
  } catch {
    channel = undefined;
  }

  let hiddenAt: number | undefined;
  let invalidated = false;
  let disposed = false;

  const dispose = () => {
    if (disposed) {
      return;
    }
    disposed = true;
    windowTarget.removeEventListener("pageshow", onPageShow);
    windowTarget.removeEventListener("online", onOnline);
    documentTarget.removeEventListener("visibilitychange", onVisibilityChange);
    channel?.removeEventListener("message", onChannelMessage);
    try {
      channel?.close();
    } catch {
      // Context invalidation must not depend on notification cleanup success.
    }
  };

  const invalidate = (reason: TenantSessionInvalidationReason) => {
    if (disposed || invalidated) {
      return;
    }
    invalidated = true;
    dispose();
    input.onInvalidate(reason);
  };

  function onChannelMessage(): void {
    invalidate("cross-tab");
  }

  function onPageShow(event: Event): void {
    if ((event as PageTransitionEvent).persisted === true) {
      invalidate("bfcache");
    }
  }

  function onOnline(): void {
    invalidate("online");
  }

  function onVisibilityChange(): void {
    if (documentTarget.visibilityState === "hidden") {
      hiddenAt = now();
      return;
    }
    if (
      documentTarget.visibilityState === "visible"
      && hiddenAt !== undefined
      && now() - hiddenAt >= hiddenRevalidationMs
    ) {
      invalidate("resume");
    }
    hiddenAt = undefined;
  }

  windowTarget.addEventListener("pageshow", onPageShow);
  windowTarget.addEventListener("online", onOnline);
  documentTarget.addEventListener("visibilitychange", onVisibilityChange);
  channel?.addEventListener("message", onChannelMessage);

  return {
    publishSessionChanged: () => {
      if (disposed || !channel) {
        return false;
      }
      try {
        channel.postMessage(null);
        return true;
      } catch {
        return false;
      }
    },
    dispose,
  };
}
