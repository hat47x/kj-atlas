/**
 * Legacy island images are URL references embedded in DocumentV1.
 * SafeMode must not resolve them because rendering can disclose access metadata.
 */
export function shouldLoadLegacyIslandImage(safeMode: boolean, imageUrl: string | undefined): boolean {
  return !safeMode && typeof imageUrl === "string" && imageUrl.trim().length > 0;
}
