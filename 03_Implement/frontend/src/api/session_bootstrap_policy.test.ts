import { describe, expect, it } from "vitest";

import {
  InvalidTenantSessionBootstrapPolicyError,
  parseTenantSessionBootstrapPolicy,
} from "./session_bootstrap_policy";

describe("tenant session bootstrap policy", () => {
  it.each(["single-tenant", "tenant-session-required"])(
    "accepts the closed-world %s mode",
    (tenantSessionMode) => {
      expect(parseTenantSessionBootstrapPolicy({ tenantSessionMode })).toEqual({
        tenantSessionMode,
      });
    },
  );

  it.each([
    null,
    [],
    {},
    { tenantSessionMode: "required" },
    { tenantSessionMode: "single-tenant", runtimeProfile: "local-dev" },
  ])("rejects an invalid or expanded policy contract", (value) => {
    expect(() => parseTenantSessionBootstrapPolicy(value)).toThrow(
      InvalidTenantSessionBootstrapPolicyError,
    );
  });
});
