import { readFile } from "node:fs/promises";
import { createHash, createVerify } from "node:crypto";
import path from "node:path";

function parseArgs(argv) {
  const options = { rootDir: process.cwd() };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--root") {
      options.rootDir = path.resolve(process.cwd(), argv[index + 1]);
      index += 1;
    } else if (value === "--public-key") {
      options.publicKeyPath = path.resolve(process.cwd(), argv[index + 1]);
      index += 1;
    } else if (value === "--key-id") {
      options.keyId = argv[index + 1];
      index += 1;
    }
  }
  return options;
}

function sha256Hex(content) {
  return createHash("sha256").update(content).digest("hex");
}

function assertManifestShape(manifest) {
  if (!manifest || typeof manifest !== "object") throw new Error("integrity.json must be an object");
  if (manifest.version !== "1") throw new Error("integrity.json version must be '1'");
  if (manifest.hashAlgorithm !== "sha256") throw new Error("integrity.json hashAlgorithm must be 'sha256'");
  if (!Array.isArray(manifest.files)) throw new Error("integrity.json files must be an array");
}

function verifySignature(manifest, publicKeyPem, expectedKeyId) {
  if (!manifest.signature || typeof manifest.signature !== "object") {
    throw new Error("integrity signature is missing");
  }
  if (manifest.signature.algorithm !== "rsa-sha256") {
    throw new Error(`Unsupported signature algorithm: ${String(manifest.signature.algorithm)}`);
  }
  if (expectedKeyId && manifest.signature.keyId !== expectedKeyId) {
    throw new Error(`Signing key mismatch: expected ${expectedKeyId}, got ${String(manifest.signature.keyId)}`);
  }
  const payload = JSON.stringify({
    version: manifest.version,
    hashAlgorithm: manifest.hashAlgorithm,
    files: manifest.files,
  });
  const verifier = createVerify("RSA-SHA256");
  verifier.update(payload);
  verifier.end();
  const ok = verifier.verify(publicKeyPem, Buffer.from(String(manifest.signature.value ?? ""), "base64"));
  if (!ok) {
    throw new Error("Signature verification failed");
  }
}

async function run() {
  const options = parseArgs(process.argv.slice(2));
  const integrityPath = path.resolve(options.rootDir, "integrity.json");
  const integrityRaw = await readFile(integrityPath, "utf-8");
  const manifest = JSON.parse(integrityRaw);
  assertManifestShape(manifest);

  for (const entry of manifest.files) {
    if (!entry || typeof entry !== "object" || typeof entry.path !== "string" || typeof entry.sha256 !== "string") {
      throw new Error("integrity.json has invalid file digest entry");
    }
    const content = await readFile(path.resolve(options.rootDir, entry.path));
    const digest = sha256Hex(content);
    if (digest !== entry.sha256) {
      throw new Error(`Hash mismatch: ${entry.path}`);
    }
  }

  if (options.publicKeyPath) {
    const publicKeyPem = await readFile(options.publicKeyPath, "utf-8");
    verifySignature(manifest, publicKeyPem, options.keyId);
  }

  console.log("Integrity verification passed");
}

run().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
