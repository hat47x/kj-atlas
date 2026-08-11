import { afterEach, describe, expect, it, vi } from "vitest";

import {
  authorizationHeader,
  clearTokens,
  getAccessToken,
  isAuthenticated,
  storeTokens,
} from "./token_store";

describe("token_store", () => {
  afterEach(() => {
    clearTokens();
    vi.unstubAllGlobals();
  });

  it("keeps the access token in memory without touching browser storage", () => {
    const sessionStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    };
    vi.stubGlobal("sessionStorage", sessionStorage);

    storeTokens({ accessToken: "short-lived-token" });

    expect(getAccessToken()).toBe("short-lived-token");
    expect(isAuthenticated()).toBe(true);
    expect(authorizationHeader()).toEqual({
      "X-Kj-Atlas-Authorization": "Bearer short-lived-token",
    });
    expect(sessionStorage.getItem).not.toHaveBeenCalled();
    expect(sessionStorage.setItem).not.toHaveBeenCalled();
    expect(sessionStorage.removeItem).not.toHaveBeenCalled();
  });

  it("clears the in-memory token on logout", () => {
    storeTokens({ accessToken: "short-lived-token" });

    clearTokens();

    expect(getAccessToken()).toBeNull();
    expect(isAuthenticated()).toBe(false);
    expect(authorizationHeader()).toEqual({});
  });
});
