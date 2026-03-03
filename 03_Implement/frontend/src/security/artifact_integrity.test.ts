import { generateKeyPairSync, createHash, createSign } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { parseIntegrityManifest, verifyIntegrityManifest } from "./artifact_integrity";

function sha256Hex(content: string): string {
  return createHash("sha256").update(content).digest("hex");
}

describe("artifact integrity", () => {
  it("passes normal hash verification", async () => {
    const files = new Map<string, string | Uint8Array>([
      ["document.json", '{"id":"doc"}\n'],
      ["view.json", '{"version":"1"}\n'],
    ]);
    const manifest = {
      version: "1",
      hashAlgorithm: "sha256",
      generatedAt: "2026-01-01T00:00:00.000Z",
      files: [
        { path: "document.json", sha256: sha256Hex('{"id":"doc"}\n') },
        { path: "view.json", sha256: sha256Hex('{"version":"1"}\n') },
      ],
    } as const;

    const parsed = parseIntegrityManifest(manifest);
    expect(parsed.ok).toBe(true);
    if (!parsed.ok) return;
    await expect(verifyIntegrityManifest(parsed.manifest, files)).resolves.toEqual({ ok: true });
  });

  it("detects tampered artifact via hash mismatch", async () => {
    const manifest = {
      version: "1",
      hashAlgorithm: "sha256",
      generatedAt: "2026-01-01T00:00:00.000Z",
      files: [{ path: "document.json", sha256: sha256Hex('{"id":"doc"}\n') }],
    };
    const parsed = parseIntegrityManifest(manifest);
    if (!parsed.ok) throw new Error(parsed.error);

    const verification = await verifyIntegrityManifest(parsed.manifest, new Map([["document.json", '{"id":"tampered"}\n']]));
    expect(verification.ok).toBe(false);
  });

  it("fails on signing key mismatch in verifier script", () => {
    const tmpRoot = mkdtempSync(path.join(tmpdir(), "kj-atlas-integrity-"));
    try {
      const dataPath = path.join(tmpRoot, "document.json");
      writeFileSync(dataPath, '{"id":"doc"}\n', "utf-8");

      const signing = generateKeyPairSync("rsa", { modulusLength: 2048 });
      const wrong = generateKeyPairSync("rsa", { modulusLength: 2048 });
      const payloadBase = {
        version: "1",
        hashAlgorithm: "sha256",
        files: [{ path: "document.json", sha256: sha256Hex(readFileSync(dataPath, "utf-8")) }],
      };
      const signer = createSign("RSA-SHA256");
      signer.update(JSON.stringify(payloadBase));
      signer.end();
      const signature = signer.sign(signing.privateKey).toString("base64");
      writeFileSync(
        path.join(tmpRoot, "integrity.json"),
        `${JSON.stringify({ ...payloadBase, generatedAt: "2026-01-01T00:00:00.000Z", signature: { keyId: "ops-2026q1", algorithm: "rsa-sha256", value: signature } }, null, 2)}\n`,
        "utf-8",
      );
      const wrongPublicPath = path.join(tmpRoot, "wrong-public.pem");
      writeFileSync(wrongPublicPath, wrong.publicKey.export({ type: "spki", format: "pem" }), "utf-8");

      expect(() =>
        execFileSync(
          "node",
          ["./scripts/verify_artifact_integrity.mjs", "--root", tmpRoot, "--public-key", wrongPublicPath, "--key-id", "ops-2026q1"],
          { cwd: path.resolve(path.dirname(new URL(import.meta.url).pathname), "..", ".."), stdio: "pipe" },
        ),
      ).toThrow();
    } finally {
      rmSync(tmpRoot, { recursive: true, force: true });
    }
  });
});
