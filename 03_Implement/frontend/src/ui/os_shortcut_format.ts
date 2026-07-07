/**
 * ADR-0048 D2: OS-specific shortcut display (Mac=⌘-prefixed / Windows,Linux=Ctrl+).
 * Shared by the command palette (UX-CMDK-01) and the shortcut cheatsheet
 * (UX-SHORTCUT-01) so the two surfaces never drift.
 */
export function isMacPlatform(): boolean {
  if (typeof navigator === "undefined") {
    return false;
  }
  const platform = navigator.platform ?? "";
  const userAgent = navigator.userAgent ?? "";
  return /Mac|iPhone|iPod|iPad/.test(platform || userAgent);
}

/**
 * Every formatter accepts an optional `useMacNotation` override so the
 * cheatsheet's manual OS switch (Round 5 redline) can preview the other
 * platform's notation without touching the real platform detection.
 */
function resolveMac(useMacNotation?: boolean): boolean {
  return useMacNotation ?? isMacPlatform();
}

/** Formats a single letter/digit bound to the primary modifier (Cmd/Ctrl). */
export function formatModShortcut(key: string, useMacNotation?: boolean): string {
  return resolveMac(useMacNotation) ? `⌘${key}` : `Ctrl+${key}`;
}

/** Formats a key bound to the primary modifier + Shift (e.g. Redo alt form). */
export function formatModShiftShortcut(key: string, useMacNotation?: boolean): string {
  return resolveMac(useMacNotation) ? `⇧⌘${key}` : `Ctrl+Shift+${key}`;
}

/** Formats a key bound to Alt+Shift (e.g. hierarchy-level switching). */
export function formatAltShiftShortcut(key: string, useMacNotation?: boolean): string {
  return resolveMac(useMacNotation) ? `⌥⇧${key}` : `Alt+Shift+${key}`;
}
