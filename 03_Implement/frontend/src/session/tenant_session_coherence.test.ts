import { describe, expect, it, vi } from "vitest";

import {
  installTenantSessionCoherenceBoundary,
  type TenantSessionInvalidationReason,
} from "./tenant_session_coherence";

class FakeEventTarget {
  private readonly listeners = new Map<string, Set<EventListener>>();

  addEventListener(type: string, listener: EventListener): void {
    const listeners = this.listeners.get(type) ?? new Set<EventListener>();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }

  removeEventListener(type: string, listener: EventListener): void {
    this.listeners.get(type)?.delete(listener);
  }

  dispatch(type: string, event: Event = new Event(type)): void {
    for (const listener of [...(this.listeners.get(type) ?? [])]) {
      listener(event);
    }
  }
}

class FakeVisibilityTarget extends FakeEventTarget {
  visibilityState = "visible";
}

class FakeChannel extends FakeEventTarget {
  readonly messages: null[] = [];
  close = vi.fn();

  postMessage(message: null): void {
    this.messages.push(message);
  }
}

function setup(overrides: Readonly<{
  hiddenRevalidationMs?: number;
  now?: () => number;
  createChannel?: (name: string) => FakeChannel | undefined;
}> = {}) {
  const windowTarget = new FakeEventTarget();
  const documentTarget = new FakeVisibilityTarget();
  const channel = new FakeChannel();
  const invalidations: TenantSessionInvalidationReason[] = [];
  let channelName = "";
  const boundary = installTenantSessionCoherenceBoundary({
    onInvalidate: (reason) => invalidations.push(reason),
    windowTarget,
    documentTarget,
    createChannel: overrides.createChannel ?? ((name) => {
      channelName = name;
      return channel;
    }),
    hiddenRevalidationMs: overrides.hiddenRevalidationMs,
    now: overrides.now,
  });
  return {
    boundary,
    channel,
    channelName: () => channelName,
    documentTarget,
    invalidations,
    windowTarget,
  };
}

describe("tenant session coherence boundary", () => {
  it("publishes a fixed data-free notification", () => {
    const fixture = setup();

    expect(fixture.boundary.publishSessionChanged()).toBe(true);
    expect(fixture.channel.messages).toEqual([null]);
    expect(fixture.channelName()).toBe("kj-atlas-tenant-session-v1");
    expect(fixture.channelName()).not.toContain("tenant-a");
    expect(fixture.channelName()).not.toContain("user-1");
    expect(fixture.channelName()).not.toContain("opaque-version-777");
  });

  it("invalidates once for any same-origin channel message and then detaches", () => {
    const fixture = setup();

    fixture.channel.dispatch("message");
    fixture.windowTarget.dispatch("online");

    expect(fixture.invalidations).toEqual(["cross-tab"]);
    expect(fixture.channel.close).toHaveBeenCalledOnce();
    expect(fixture.boundary.publishSessionChanged()).toBe(false);
  });

  it("invalidates only a persisted pageshow restoration", () => {
    const fixture = setup();
    const normalPageShow = new Event("pageshow");
    Object.defineProperty(normalPageShow, "persisted", { value: false });
    fixture.windowTarget.dispatch("pageshow", normalPageShow);

    const restoredPageShow = new Event("pageshow");
    Object.defineProperty(restoredPageShow, "persisted", { value: true });
    fixture.windowTarget.dispatch("pageshow", restoredPageShow);

    expect(fixture.invalidations).toEqual(["bfcache"]);
  });

  it("invalidates after a bounded hidden interval but not a short pause", () => {
    let currentTime = 1_000;
    const fixture = setup({
      hiddenRevalidationMs: 300_000,
      now: () => currentTime,
    });

    fixture.documentTarget.visibilityState = "hidden";
    fixture.documentTarget.dispatch("visibilitychange");
    currentTime += 299_999;
    fixture.documentTarget.visibilityState = "visible";
    fixture.documentTarget.dispatch("visibilitychange");
    expect(fixture.invalidations).toEqual([]);

    fixture.documentTarget.visibilityState = "hidden";
    fixture.documentTarget.dispatch("visibilitychange");
    currentTime += 300_000;
    fixture.documentTarget.visibilityState = "visible";
    fixture.documentTarget.dispatch("visibilitychange");
    expect(fixture.invalidations).toEqual(["resume"]);
  });

  it("invalidates on network restoration without relying on channel support", () => {
    const fixture = setup({ createChannel: () => undefined });

    expect(fixture.boundary.publishSessionChanged()).toBe(false);
    fixture.windowTarget.dispatch("online");

    expect(fixture.invalidations).toEqual(["online"]);
  });

  it("rejects an invalid resume threshold before installing listeners", () => {
    expect(() => setup({ hiddenRevalidationMs: -1 })).toThrow(TypeError);
    expect(() => setup({ hiddenRevalidationMs: Number.NaN })).toThrow(TypeError);
  });
});
