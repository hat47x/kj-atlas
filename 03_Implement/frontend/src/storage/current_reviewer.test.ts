import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  initializeCurrentReviewerRef,
  loadCurrentReviewerRef,
  sanitizeReviewerRef,
  saveCurrentReviewerRef,
} from "./current_reviewer";

type LocalStorageLike = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  clear: () => void;
};

function createMockStorage(): LocalStorageLike {
  const store = new Map<string, string>();
  return {
    getItem: (key) => store.get(key) ?? null,
    setItem: (key, value) => {
      store.set(key, value);
    },
    clear: () => {
      store.clear();
    },
  };
}

describe("current_reviewer storage", () => {
  beforeEach(() => {
    const storage = createMockStorage();
    Object.defineProperty(globalThis, "window", {
      value: { localStorage: storage },
      configurable: true,
      writable: true,
    });
    window.localStorage.clear();
    vi.restoreAllMocks();
  });

  it("sanitizes reviewerRef", () => {
    expect(sanitizeReviewerRef("  user:local:abc  ")).toBe("user:local:abc");
    expect(sanitizeReviewerRef(123)).toBe("");
  });

  it("initializes reviewerRef once and keeps it for reload", () => {
    const randomUuidSpy = vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-4000-8000-000000000001");

    const initialized = initializeCurrentReviewerRef();
    expect(initialized).toBe("user:local:00000000-0000-4000-8000-000000000001");
    expect(loadCurrentReviewerRef()).toBe("user:local:00000000-0000-4000-8000-000000000001");

    const second = initializeCurrentReviewerRef();
    expect(second).toBe("user:local:00000000-0000-4000-8000-000000000001");
    expect(randomUuidSpy).toHaveBeenCalledTimes(1);
  });

  it("saves explicit reviewerRef", () => {
    saveCurrentReviewerRef(" user:local:manual ");
    expect(loadCurrentReviewerRef()).toBe("user:local:manual");
  });
});
