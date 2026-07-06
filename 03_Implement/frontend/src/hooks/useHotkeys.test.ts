import { describe, expect, it } from "vitest";

import { resolveHotkeyAction } from "./useHotkeys";

describe("resolveHotkeyAction", () => {
  it("maps guarded selected-card H/U/R shortcuts", () => {
    expect(resolveHotkeyAction({ key: "h", canToggleSelectedCardHold: true })).toEqual({ kind: "toggle-card-hold" });
    expect(resolveHotkeyAction({ key: "U", canToggleSelectedCardCritique: true })).toEqual({ kind: "toggle-card-critique" });
    expect(resolveHotkeyAction({ key: "r", canToggleSelectedCardReviewed: true })).toEqual({ kind: "toggle-card-reviewed" });
  });

  it("does not fire single-key shortcuts while editing or using modifiers", () => {
    expect(resolveHotkeyAction({ key: "h", editableTarget: true, canToggleSelectedCardHold: true })).toBeNull();
    expect(resolveHotkeyAction({ key: "u", ctrlKey: true, canToggleSelectedCardCritique: true })).toBeNull();
    expect(resolveHotkeyAction({ key: "r", metaKey: true, canToggleSelectedCardReviewed: true })).toBeNull();
    expect(resolveHotkeyAction({ key: "h", shiftKey: true, canToggleSelectedCardHold: true })).toBeNull();
  });

  it("opens shortcut help with the guarded question mark key", () => {
    expect(resolveHotkeyAction({ key: "?", shiftKey: true })).toEqual({ kind: "open-shortcut-help" });
    expect(resolveHotkeyAction({ key: "/", shiftKey: true })).toEqual({ kind: "open-shortcut-help" });
    expect(resolveHotkeyAction({ key: "?", editableTarget: true })).toBeNull();
    expect(resolveHotkeyAction({ key: "?", ctrlKey: true })).toBeNull();
  });

  it("keeps reading navigation R ahead of selected-card review toggle", () => {
    expect(resolveHotkeyAction({
      key: "r",
      canReadingPathToggleReviewedOnly: true,
      canToggleSelectedCardReviewed: true,
    })).toEqual({ kind: "reading-toggle-reviewed-only" });
  });

  it("preserves existing selection and nudge keys", () => {
    expect(resolveHotkeyAction({ key: "Escape" })).toEqual({ kind: "clear-selection" });
    expect(resolveHotkeyAction({ key: "Delete" })).toEqual({ kind: "delete-selection" });
    expect(resolveHotkeyAction({ key: "ArrowRight" })).toEqual({ kind: "nudge", dx: 1, dy: 0 });
    expect(resolveHotkeyAction({ key: "ArrowRight", shiftKey: true })).toEqual({ kind: "nudge", dx: 10, dy: 0 });
  });
});
