import JSZip from "jszip";
import { VISUAL_CUE_BUNDLE_FILE_NAME } from "../domain/representative_visual_cue_assets";

const ALLOWED_EXTENSIONS = [".json", ".md", ".png"] as const;
const STRIPPABLE_ROOT_PREFIXES = ["kj-atlas-review-pack-"] as const;

export const ZIP_MAX_UNCOMPRESSED_BYTES = 20 * 1024 * 1024;
export const ZIP_MAX_FILE_COUNT = 200;
export const ZIP_MAX_FILE_UNCOMPRESSED_BYTES = 10 * 1024 * 1024;
export const ZIP_MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024;
export const ZIP_MAX_PNG_FILE_BYTES = 10 * 1024 * 1024;
export const ZIP_MAX_PNG_DIMENSION = 8000;
export const ZIP_MAX_COMPRESSION_RATIO = 120;

export class ZipImportError extends Error {
  readonly code: "Z001" | "Z002" | "Z003";

  constructor(code: "Z001" | "Z002" | "Z003", detail: string) {
    super(`${code}: ${detail}`);
    this.code = code;
    this.name = "ZipImportError";
  }
}

export type ZipImportResult = {
  entries: Map<string, Uint8Array | string>;
  skippedUnsupportedCount: number;
};

function hasAllowedExtension(path: string): boolean {
  const lowerPath = path.toLowerCase();
  return ALLOWED_EXTENSIONS.some((extension) => lowerPath.endsWith(extension));
}

export function normalizeZipPath(path: string, shouldStripCommonRoot: boolean): string | null {
  const hasWindowsDrivePrefix = /^[a-zA-Z]:[\\/]/.test(path);
  const hasUncPrefix = /^\\\\/.test(path);
  const hasPosixAbsolutePrefix = /^\//.test(path);
  if (hasWindowsDrivePrefix || hasUncPrefix || hasPosixAbsolutePrefix) {
    throw new ZipImportError("Z002", `Absolute paths are not allowed: ${path}`);
  }

  const normalized = path.replace(/\\/g, "/").replace(/^\/+/, "").replace(/^(\.\/)+/, "");
  if (normalized.includes("\u0000")) {
    throw new ZipImportError("Z002", `NUL byte in path is not allowed: ${path}`);
  }
  const rawSegments = normalized.split("/").filter((segment) => segment.length > 0 && segment !== ".");
  if (rawSegments.length === 0) {
    return null;
  }
  if (rawSegments.some((segment) => segment === "..")) {
    throw new ZipImportError("Z002", `Path traversal is not allowed: ${path}`);
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

  return STRIPPABLE_ROOT_PREFIXES.some((prefix) => candidate.startsWith(prefix)) ? candidate : null;
}

function ensureWithinMaxSize(size: number, maxSize: number, detail: string): void {
  if (size > maxSize) {
    throw new ZipImportError("Z001", detail);
  }
}

function decodePngDimensions(content: Uint8Array): { width: number; height: number } {
  const PNG_SIGNATURE = [137, 80, 78, 71, 13, 10, 26, 10];
  if (content.byteLength < 24) {
    throw new ZipImportError("Z003", "Invalid PNG format");
  }

  for (let index = 0; index < PNG_SIGNATURE.length; index += 1) {
    if (content[index] !== PNG_SIGNATURE[index]) {
      throw new ZipImportError("Z003", "Invalid PNG signature");
    }
  }

  const dataView = new DataView(content.buffer, content.byteOffset, content.byteLength);
  const chunkType = String.fromCharCode(content[12], content[13], content[14], content[15]);
  if (chunkType !== "IHDR") {
    throw new ZipImportError("Z003", "PNG missing IHDR header");
  }
  const width = dataView.getUint32(16);
  const height = dataView.getUint32(20);
  return { width, height };
}

function readEntryUncompressedSize(entry: JSZip.JSZipObject): number | null {
  const maybeCompressedObject = entry as JSZip.JSZipObject & { _data?: { uncompressedSize?: number } };
  const uncompressedSize = maybeCompressedObject._data?.uncompressedSize;
  return typeof uncompressedSize === "number" && Number.isFinite(uncompressedSize) ? uncompressedSize : null;
}

function readEntryCompressedSize(entry: JSZip.JSZipObject): number | null {
  const maybeCompressedObject = entry as JSZip.JSZipObject & { _data?: { compressedSize?: number } };
  const compressedSize = maybeCompressedObject._data?.compressedSize;
  return typeof compressedSize === "number" && Number.isFinite(compressedSize) ? compressedSize : null;
}

export async function readZipFiles(file: File): Promise<ZipImportResult> {
  const zip = await JSZip.loadAsync(await file.arrayBuffer());
  const result = new Map<string, Uint8Array | string>();
  let totalSize = 0;
  let skippedUnsupportedCount = 0;
  const archivePaths = Object.values(zip.files).filter((entry) => !entry.dir).map((entry) => entry.name);
  ensureWithinMaxSize(archivePaths.length, ZIP_MAX_FILE_COUNT, `Archive contains too many files (${archivePaths.length}/${ZIP_MAX_FILE_COUNT})`);
  const commonRootFolder = findCommonRootFolder(archivePaths);

  for (const entry of Object.values(zip.files)) {
    if (entry.dir) {
      continue;
    }

    const rawEntryName = ((entry as JSZip.JSZipObject & { unsafeOriginalName?: string }).unsafeOriginalName ?? entry.name);
    const normalizedPath = normalizeZipPath(rawEntryName, Boolean(commonRootFolder));
    if (!normalizedPath) {
      continue;
    }
    if (!hasAllowedExtension(normalizedPath)) {
      skippedUnsupportedCount += 1;
      continue;
    }

    const lowerPath = normalizedPath.toLowerCase();
    const estimatedSize = readEntryUncompressedSize(entry);
    const compressedSize = readEntryCompressedSize(entry);
    if (estimatedSize !== null && compressedSize !== null && compressedSize > 0) {
      const compressionRatio = estimatedSize / compressedSize;
      ensureWithinMaxSize(compressionRatio, ZIP_MAX_COMPRESSION_RATIO, `${normalizedPath} exceeds compression ratio limit`);
    }
    if (estimatedSize !== null) {
      ensureWithinMaxSize(estimatedSize, ZIP_MAX_FILE_UNCOMPRESSED_BYTES, `${normalizedPath} exceeds per-file size limit`);
      if (lowerPath.endsWith(".png")) {
        ensureWithinMaxSize(estimatedSize, ZIP_MAX_PNG_FILE_BYTES, `${normalizedPath} exceeds png size limit`);
      }
      if (lowerPath.endsWith(".json") || lowerPath.endsWith(".md")) {
        ensureWithinMaxSize(estimatedSize, ZIP_MAX_TEXT_FILE_BYTES, `${normalizedPath} exceeds text size limit`);
      }
      ensureWithinMaxSize(totalSize + estimatedSize, ZIP_MAX_UNCOMPRESSED_BYTES, "Zip too large / exceeds total uncompressed limit");
    }

    const isTextFile = lowerPath.endsWith(".json") || lowerPath.endsWith(".md");
    if (isTextFile) {
      const content = await entry.async("string");
      const textSize = new TextEncoder().encode(content).byteLength;
      ensureWithinMaxSize(textSize, ZIP_MAX_TEXT_FILE_BYTES, `${normalizedPath} exceeds text size limit`);
      ensureWithinMaxSize(textSize, ZIP_MAX_FILE_UNCOMPRESSED_BYTES, `${normalizedPath} exceeds per-file size limit`);
      totalSize += textSize;
      ensureWithinMaxSize(totalSize, ZIP_MAX_UNCOMPRESSED_BYTES, "Zip too large / exceeds total uncompressed limit");
      result.set(normalizedPath, content);
      continue;
    }

    const content = await entry.async("uint8array");
    ensureWithinMaxSize(content.byteLength, ZIP_MAX_FILE_UNCOMPRESSED_BYTES, `${normalizedPath} exceeds per-file size limit`);
    ensureWithinMaxSize(content.byteLength, ZIP_MAX_PNG_FILE_BYTES, `${normalizedPath} exceeds png size limit`);
    const { width, height } = decodePngDimensions(content);
    if (width > ZIP_MAX_PNG_DIMENSION || height > ZIP_MAX_PNG_DIMENSION) {
      throw new ZipImportError("Z003", `${normalizedPath} dimensions ${width}x${height} exceed ${ZIP_MAX_PNG_DIMENSION}x${ZIP_MAX_PNG_DIMENSION}`);
    }
    totalSize += content.byteLength;
    ensureWithinMaxSize(totalSize, ZIP_MAX_UNCOMPRESSED_BYTES, "Zip too large / exceeds total uncompressed limit");
    result.set(normalizedPath, content);
  }

  return { entries: result, skippedUnsupportedCount };
}

export type ReviewPackPaths = {
  documentPath: string | null;
  viewPath: string | null;
  snapshotPath: string | null;
  diagnosticsPath: string | null;
  outlinePath: string | null;
  integrityPath: string | null;
  visualCueAssetsPath: string | null;
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
  const integrityPath = findFilePath(paths, "integrity.json");
  const visualCueAssetsPath = findFilePath(paths, VISUAL_CUE_BUNDLE_FILE_NAME);

  const knownPathSet = new Set([
    documentPath,
    viewPath,
    snapshotPath,
    diagnosticsPath,
    outlinePath,
    integrityPath,
    visualCueAssetsPath,
  ].filter(Boolean));

  return {
    documentPath,
    viewPath,
    snapshotPath,
    diagnosticsPath,
    outlinePath,
    integrityPath,
    visualCueAssetsPath,
    ignoredFileCount: paths.filter((path) => !knownPathSet.has(path)).length,
  };
}
