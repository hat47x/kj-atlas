/**
 * ADR-0048 D2: OS-specific shortcut display (Mac=⌘-prefixed / Windows,Linux=Ctrl+).
 * Shared by the command palette (UX-CMDK-01) and, later, the shortcut
 * cheatsheet (UX-SHORTCUT-01) so the two surfaces never drift.
 */
export function isMacPlatform(): boolean {
  if (typeof navigator === "undefined") {
    return false;
  }
  const platform = navigator.platform ?? "";
  const userAgent = navigator.userAgent ?? "";
  return /Mac|iPhone|iPod|iPad/.test(platform || userAgent);
}

/** Formats a single letter/digit bound to the primary modifier (Cmd/Ctrl). */
export function formatModShortcut(key: string): string {
  return isMacPlatform() ? `⌘${key}` : `Ctrl+${key}`;
}
