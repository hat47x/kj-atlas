import { afterEach, describe, expect, it, vi } from "vitest";

import { handleOAuthCallback } from "./oauth_callback";
import { clearTokens, getAccessToken } from "./token_store";

function storageWithOAuthState(): Storage {
  const values = new Map([
    ["kj_atlas_oauth_state", "expected-state"],
    ["kj_atlas_pkce_verifier", "verifier"],
  ]);
  return {
    get length() { return values.size; },
    clear: () => values.clear(),
    getItem: (key) => values.get(key) ?? null,
    key: (index) => [...values.keys()][index] ?? null,
    removeItem: (key) => { values.delete(key); },
    setItem: (key, value) => { values.set(key, value); },
  };
}

describe("handleOAuthCallback", () => {
  afterEach(() => {
    clearTokens();
    vi.unstubAllGlobals();
  });

  it("rejects the whole response when a refresh token is exposed", async () => {
    vi.stubGlobal("sessionStorage", storageWithOAuthState());
    const replaceState = vi.fn();
    vi.stubGlobal("window", {
      location: {
        search: "?code=code-1&state=expected-state",
        origin: "https://app.example",
        pathname: "/oauth/callback",
      },
      history: { replaceState },
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: "short-lived-token",
        refresh_token: "long-lived-secret",
      }),
    }));

    await expect(handleOAuthCallback()).resolves.toEqual({
      handled: true,
      error: "oauth_refresh_token_not_allowed",
    });
    expect(getAccessToken()).toBeNull();
    expect(replaceState).toHaveBeenCalledWith(
      null,
      "",
      "https://app.example/oauth/callback",
    );
  });
});
