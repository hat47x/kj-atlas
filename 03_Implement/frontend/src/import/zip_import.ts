import JSZip from "jszip";

const ALLOWED_EXTENSIONS = [".json", ".md", ".png"] as const;
const STRIPPABLE_ROOT_PREFIXES = ["kj-atlas-review-pack-"] as const;

export const ZIP_MAX_UNCOMPRESSED_BYTES = 20 * 1024 * 1024;

function hasAllowedExtension(path: string): boolean {
  const lowerPath = path.toLowerCase();
  return ALLOWED_EXTENSIONS.some((extension) => lowerPath.endsWith(extension));
}

function normalizeZipPath(path: string, shouldStripCommonRoot: boolean): string | null {
  const normalized = path.replace(/\\/g, "/").replace(/^\/+/, "");
  const rawSegments = normalized.split("/").filter((segment) => segment.length > 0 && segment !== ".");
  if (rawSegments.length === 0 || rawSegments.some((segment) => segment === "..")) {
    return null;
  }

  const segments = shouldStripCommonRoot && rawSegments.length > 1 ? rawSegments.slice(1) : rawSegments;
  return segments.join("/");
}

function findCommonRootFolder(paths: string[]): string | null {
  const firstSegments = paths
    .map((path) => path.replace(/\\/g, "/").replace(/^\/+/, "").split("/").filter(Boolean))
    .filter((segments) => segments.length > 0)
    .map((segments) => segments[0]);

  if (firstSegments.length === 0) {
    return null;
  }

  const candidate = firstSegments[0];
  if (!candidate || !firstSegments.every((segment) => segment === candidate)) {
    return null;
  }

  const byPrefix = STRIPPABLE_ROOT_PREFIXES.some((prefix) => candidate.startsWith(prefix));
  if (byPrefix) {
    return candidate;
  }

  return firstSegments.length > 1 ? candidate : null;
}

export async function readZipFiles(file: File): Promise<Map<string, Uint8Array | string>> {
  const zip = await JSZip.loadAsync(await file.arrayBuffer());
  const result = new Map<string, Uint8Array | string>();
  let totalSize = 0;
  const archivePaths = Object.values(zip.files).filter((entry) => !entry.dir).map((entry) => entry.name);
  const commonRootFolder = findCommonRootFolder(archivePaths);

  for (const entry of Object.values(zip.files)) {
    if (entry.dir) {
      continue;
    }

    const normalizedPath = normalizeZipPath(entry.name, Boolean(commonRootFolder));
    if (!normalizedPath) {
      continue;
    }
    if (!hasAllowedExtension(normalizedPath)) {
      continue;
    }

    const lowerPath = normalizedPath.toLowerCase();
    const isTextFile = lowerPath.endsWith(".json") || lowerPath.endsWith(".md");
    if (isTextFile) {
      const content = await entry.async("string");
      totalSize += new TextEncoder().encode(content).byteLength;
      if (totalSize > ZIP_MAX_UNCOMPRESSED_BYTES) {
        throw new Error("Zip too large / exceeds limit");
      }
      result.set(normalizedPath, content);
      continue;
    }

    const content = await entry.async("uint8array");
    totalSize += content.byteLength;
    if (totalSize > ZIP_MAX_UNCOMPRESSED_BYTES) {
      throw new Error("Zip too large / exceeds limit");
    }
    result.set(normalizedPath, content);
  }

  return result;
}

export type ReviewPackPaths = {
  documentPath: string | null;
  viewPath: string | null;
  snapshotPath: string | null;
  diagnosticsPath: string | null;
  outlinePath: string | null;
  ignoredFileCount: number;
};

function findFilePath(paths: string[], fileName: string): string | null {
  const normalizedTarget = fileName.toLowerCase();
  for (const path of paths) {
    const normalizedPath = path.toLowerCase();
    if (normalizedPath === normalizedTarget || normalizedPath.endsWith(`/${normalizedTarget}`)) {
      return path;
    }
  }
  return null;
}

export function detectReviewPackFiles(entries: Map<string, Uint8Array | string>): ReviewPackPaths {
  const paths = Array.from(entries.keys());
  const documentPath = findFilePath(paths, "document.json");
  const viewPath = findFilePath(paths, "view.json");
  const snapshotPath = findFilePath(paths, "snapshot.png");
  const diagnosticsPath = findFilePath(paths, "diagnostics.md");
  const outlinePath = findFilePath(paths, "outline.md");

  const knownPathSet = new Set([documentPath, viewPath, snapshotPath, diagnosticsPath, outlinePath].filter(Boolean));

  return {
    documentPath,
    viewPath,
    snapshotPath,
    diagnosticsPath,
    outlinePath,
    ignoredFileCount: paths.filter((path) => !knownPathSet.has(path)).length,
  };
}
