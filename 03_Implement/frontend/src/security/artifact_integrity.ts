export type IntegrityFileDigest = {
  path: string;
  sha256: string;
};

export type ArtifactIntegrityManifestV1 = {
  version: "1";
  hashAlgorithm: "sha256";
  generatedAt: string;
  files: IntegrityFileDigest[];
};

const HEX_ALPHABET = /^[0-9a-f]{64}$/;

function toArrayBuffer(content: string | Uint8Array): ArrayBuffer {
  if (typeof content === "string") {
    return new TextEncoder().encode(content).buffer;
  }
  const view = content.byteOffset === 0 && content.byteLength === content.buffer.byteLength
    ? content
    : content.slice(0);
  return view.buffer as ArrayBuffer;
}

function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

async function digestSha256(content: string | Uint8Array): Promise<string> {
  const hashBuffer = await crypto.subtle.digest("SHA-256", toArrayBuffer(content));
  return bytesToHex(new Uint8Array(hashBuffer));
}

function normalizePath(path: string): string {
  return path.replace(/^\.\//, "").replace(/\\/g, "/");
}

export async function buildIntegrityManifest(
  files: Array<{ path: string; content: string | Uint8Array }>,
  generatedAt: string,
): Promise<ArtifactIntegrityManifestV1> {
  const digests: IntegrityFileDigest[] = [];
  for (const file of files) {
    const normalizedPath = normalizePath(file.path);
    if (normalizedPath.endsWith("/integrity.json") || normalizedPath === "integrity.json") {
      continue;
    }
    digests.push({
      path: normalizedPath,
      sha256: await digestSha256(file.content),
    });
  }

  digests.sort((left, right) => left.path.localeCompare(right.path));
  return {
    version: "1",
    hashAlgorithm: "sha256",
    generatedAt,
    files: digests,
  };
}

export function parseIntegrityManifest(input: unknown): { ok: true; manifest: ArtifactIntegrityManifestV1 } | { ok: false; error: string } {
  if (!input || typeof input !== "object") {
    return { ok: false, error: "integrity.json must be a JSON object" };
  }
  const value = input as Record<string, unknown>;
  if (value.version !== "1") {
    return { ok: false, error: "integrity.json version must be \"1\"" };
  }
  if (value.hashAlgorithm !== "sha256") {
    return { ok: false, error: "integrity.json hashAlgorithm must be \"sha256\"" };
  }
  if (typeof value.generatedAt !== "string" || value.generatedAt.length === 0) {
    return { ok: false, error: "integrity.json generatedAt must be a non-empty string" };
  }
  if (!Array.isArray(value.files)) {
    return { ok: false, error: "integrity.json files must be an array" };
  }

  const files: IntegrityFileDigest[] = [];
  for (const entry of value.files) {
    if (!entry || typeof entry !== "object") {
      return { ok: false, error: "integrity.json files entries must be objects" };
    }
    const digest = entry as Record<string, unknown>;
    if (typeof digest.path !== "string" || digest.path.length === 0) {
      return { ok: false, error: "integrity.json files[].path must be a non-empty string" };
    }
    if (typeof digest.sha256 !== "string" || !HEX_ALPHABET.test(digest.sha256)) {
      return { ok: false, error: `integrity.json files[].sha256 is invalid (${String(digest.path)})` };
    }
    files.push({ path: normalizePath(digest.path), sha256: digest.sha256.toLowerCase() });
  }

  return {
    ok: true,
    manifest: {
      version: "1",
      hashAlgorithm: "sha256",
      generatedAt: value.generatedAt,
      files,
    },
  };
}

export async function verifyIntegrityManifest(
  manifest: ArtifactIntegrityManifestV1,
  files: Map<string, string | Uint8Array>,
): Promise<{ ok: true } | { ok: false; error: string }> {
  for (const digest of manifest.files) {
    const direct = files.get(digest.path);
    const fallback = files.get(`./${digest.path}`);
    const content = direct ?? fallback;
    if (content === undefined) {
      return { ok: false, error: `Missing file listed in integrity.json: ${digest.path}` };
    }
    const actual = await digestSha256(content);
    if (actual !== digest.sha256) {
      return { ok: false, error: `Hash mismatch detected for ${digest.path}` };
    }
  }
  return { ok: true };
}
