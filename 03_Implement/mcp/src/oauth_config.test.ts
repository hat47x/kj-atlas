import { describe, expect, it } from "vitest";
import { HttpTransportConfigError, loadHttpTransportConfigFromEnv } from "./oauth_config.js";

const VALID_ENV = {
  KJ_ATLAS_MCP_RESOURCE_URL: "https://mcp.kj-atlas.example/",
  KJ_ATLAS_MCP_TRUSTED_ISSUER: "https://idp.example/",
  KJ_ATLAS_MCP_JWKS_URI: "https://idp.example/.well-known/jwks.json",
};

describe("loadHttpTransportConfigFromEnv", () => {
  it("loads a complete config with the safe host/port defaults", () => {
    const config = loadHttpTransportConfigFromEnv(VALID_ENV);
    expect(config).toEqual({
      host: "127.0.0.1",
      port: 8787,
      resource: "https://mcp.kj-atlas.example/",
      trustedIssuer: "https://idp.example/",
      jwksUri: "https://idp.example/.well-known/jwks.json",
      authorizationServers: ["https://idp.example/"],
    });
  });

  it("defaults authorization_servers to [trustedIssuer] when not set", () => {
    const config = loadHttpTransportConfigFromEnv(VALID_ENV);
    expect(config.authorizationServers).toEqual([config.trustedIssuer]);
  });

  it("splits KJ_ATLAS_MCP_AUTHORIZATION_SERVERS on commas and trims whitespace", () => {
    const config = loadHttpTransportConfigFromEnv({
      ...VALID_ENV,
      KJ_ATLAS_MCP_AUTHORIZATION_SERVERS: "https://idp-a.example/, https://idp-b.example/",
    });
    expect(config.authorizationServers).toEqual(["https://idp-a.example/", "https://idp-b.example/"]);
  });

  it.each(["KJ_ATLAS_MCP_RESOURCE_URL", "KJ_ATLAS_MCP_TRUSTED_ISSUER", "KJ_ATLAS_MCP_JWKS_URI"])(
    "throws HttpTransportConfigError when %s is missing (fails closed, no silent unauthenticated default)",
    (key) => {
      const env = { ...VALID_ENV, [key]: undefined };
      expect(() => loadHttpTransportConfigFromEnv(env)).toThrow(HttpTransportConfigError);
    },
  );

  it("rejects a non-numeric port", () => {
    expect(() => loadHttpTransportConfigFromEnv({ ...VALID_ENV, KJ_ATLAS_MCP_HTTP_PORT: "not-a-port" })).toThrow(
      HttpTransportConfigError,
    );
  });

  it("rejects an out-of-range port", () => {
    expect(() => loadHttpTransportConfigFromEnv({ ...VALID_ENV, KJ_ATLAS_MCP_HTTP_PORT: "70000" })).toThrow(
      HttpTransportConfigError,
    );
  });
});
