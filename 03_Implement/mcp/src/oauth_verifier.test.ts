import { describe, expect, it } from "vitest";
import { SignJWT, exportJWK, generateKeyPair, createLocalJWKSet, type JWTVerifyGetKey } from "jose";
import { InvalidTokenError } from "@modelcontextprotocol/sdk/server/auth/errors.js";
import { createBearerTokenVerifier } from "./oauth_verifier.js";

const TRUSTED_ISSUER = "https://idp.example/";
const RESOURCE = "https://mcp.kj-atlas.example/";
const KID = "test-key-1";

type PrivateKey = Awaited<ReturnType<typeof generateKeyPair>>["privateKey"];

async function buildTrustedKeySet() {
  const { privateKey, publicKey } = await generateKeyPair("RS256");
  const publicJwk = await exportJWK(publicKey);
  publicJwk.kid = KID;
  publicJwk.alg = "RS256";
  const getKey: JWTVerifyGetKey = createLocalJWKSet({ keys: [publicJwk] });
  return { privateKey, getKey };
}

type SignOptions = {
  issuer?: string;
  audience?: string;
  expiresIn?: string;
  kid?: string;
};

async function signToken(
  privateKey: PrivateKey,
  claims: Record<string, unknown>,
  options: SignOptions = {},
): Promise<string> {
  return new SignJWT(claims)
    .setProtectedHeader({ alg: "RS256", kid: options.kid ?? KID })
    .setIssuer(options.issuer ?? TRUSTED_ISSUER)
    .setAudience(options.audience ?? RESOURCE)
    .setIssuedAt()
    .setExpirationTime(options.expiresIn ?? "5m")
    .sign(privateKey);
}

describe("createBearerTokenVerifier", () => {
  it("accepts a validly-signed token from the trusted issuer and returns AuthInfo", async () => {
    const { privateKey, getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);
    const token = await signToken(privateKey, { client_id: "client-1", scope: "read:context read:evidence" });

    const authInfo = await verifier.verifyAccessToken(token);

    expect(authInfo.clientId).toBe("client-1");
    expect(authInfo.scopes).toEqual(["read:context", "read:evidence"]);
    expect(authInfo.resource?.toString()).toBe(RESOURCE);
    expect(typeof authInfo.expiresAt).toBe("number");
    expect(authInfo.token).toBe(token);
  });

  it("falls back to azp, then sub, when client_id is absent", async () => {
    const { privateKey, getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);

    const azpToken = await signToken(privateKey, { azp: "authorized-party-1" });
    expect((await verifier.verifyAccessToken(azpToken)).clientId).toBe("authorized-party-1");

    const subToken = await signToken(privateKey, { sub: "subject-1" });
    expect((await verifier.verifyAccessToken(subToken)).clientId).toBe("subject-1");
  });

  it("defaults scopes to an empty array when the scope claim is absent", async () => {
    const { privateKey, getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);
    const token = await signToken(privateKey, { sub: "subject-1" });

    const authInfo = await verifier.verifyAccessToken(token);

    expect(authInfo.scopes).toEqual([]);
  });

  it("rejects (InvalidTokenError, not a generic Error) a token signed by an untrusted key", async () => {
    const { getKey } = await buildTrustedKeySet();
    const { privateKey: untrustedPrivateKey } = await generateKeyPair("RS256");
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);
    const token = await signToken(untrustedPrivateKey, { sub: "attacker" });

    await expect(verifier.verifyAccessToken(token)).rejects.toThrow(InvalidTokenError);
  });

  it("rejects a token issued by a different issuer, even if signed by a trusted key", async () => {
    const { privateKey, getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);
    const token = await signToken(privateKey, { sub: "subject-1" }, { issuer: "https://attacker.example/" });

    await expect(verifier.verifyAccessToken(token)).rejects.toThrow(InvalidTokenError);
  });

  it("rejects a token issued for a different audience/resource", async () => {
    const { privateKey, getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);
    const token = await signToken(privateKey, { sub: "subject-1" }, { audience: "https://other-service.example/" });

    await expect(verifier.verifyAccessToken(token)).rejects.toThrow(InvalidTokenError);
  });

  it("rejects an expired token", async () => {
    const { privateKey, getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);
    const token = await signToken(privateKey, { sub: "subject-1" }, { expiresIn: "-10s" });

    await expect(verifier.verifyAccessToken(token)).rejects.toThrow(InvalidTokenError);
  });

  it("rejects a token with no client_id, azp, or sub claim", async () => {
    const { privateKey, getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);
    const token = await signToken(privateKey, {});

    await expect(verifier.verifyAccessToken(token)).rejects.toThrow(InvalidTokenError);
  });

  it("rejects a malformed (non-JWT) token", async () => {
    const { getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);

    await expect(verifier.verifyAccessToken("not-a-jwt")).rejects.toThrow(InvalidTokenError);
  });

  it("never echoes score/rank/confidence/priority vocabulary from token claims into AuthInfo (CVI anti-scoring, defense in depth)", async () => {
    const { privateKey, getKey } = await buildTrustedKeySet();
    const verifier = createBearerTokenVerifier({ trustedIssuer: TRUSTED_ISSUER, resource: RESOURCE }, getKey);
    const token = await signToken(privateKey, { sub: "subject-1", score: 42, rank: 1, confidence: 0.9, priority: "high" });

    const authInfo = await verifier.verifyAccessToken(token);

    expect(JSON.stringify(authInfo)).not.toMatch(/score|rank|confidence|priority/i);
  });
});
