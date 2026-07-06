import { useEffect } from "react";

export type HotkeyAction =
  | { kind: "clear-selection" }
  | { kind: "delete-selection" }
  | { kind: "nudge"; dx: number; dy: number }
  | { kind: "reading-disable" }
  | { kind: "reading-next" }
  | { kind: "reading-prev" }
  | { kind: "reading-toggle-reviewed-only" }
  | { kind: "toggle-card-critique" }
  | { kind: "toggle-card-hold" }
  | { kind: "toggle-card-reviewed" };

export type HotkeyResolverInput = {
  altKey?: boolean;
  canReadingPathDisable?: boolean;
  canReadingPathNext?: boolean;
  canReadingPathPrev?: boolean;
  canReadingPathToggleReviewedOnly?: boolean;
  canToggleSelectedCardCritique?: boolean;
  canToggleSelectedCardHold?: boolean;
  canToggleSelectedCardReviewed?: boolean;
  ctrlKey?: boolean;
  defaultPrevented?: boolean;
  editableTarget?: boolean;
  key: string;
  metaKey?: boolean;
  shiftKey?: boolean;
};

type UseHotkeysOptions = {
  onClearSelection: () => void;
  onDeleteSelection: () => void;
  onNudge: (dx: number, dy: number) => void;
  onToggleSelectedCardCritique?: () => void;
  onToggleSelectedCardHold?: () => void;
  onToggleSelectedCardReviewed?: () => void;
  onReadingPathNext?: () => void;
  onReadingPathPrev?: () => void;
  onReadingPathToggleReviewedOnly?: () => void;
  onReadingPathDisable?: () => void;
};

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) {
    return false;
  }

  const tagName = target.tagName.toLowerCase();
  if (tagName === "input" || tagName === "textarea" || tagName === "select") {
    return true;
  }

  return target.isContentEditable;
}

export function resolveHotkeyAction(input: HotkeyResolverInput): HotkeyAction | null {
  if (input.editableTarget || input.defaultPrevented) {
    return null;
  }

  if (input.metaKey || input.ctrlKey || input.altKey) {
    return null;
  }

  const lowerKey = input.key.toLowerCase();
  const usesShift = input.shiftKey === true;

  if (input.key === "Escape" && input.canReadingPathDisable) {
    return { kind: "reading-disable" };
  }

  if (input.key === "Escape") {
    return { kind: "clear-selection" };
  }

  if (!usesShift && lowerKey === "h" && input.canToggleSelectedCardHold) {
    return { kind: "toggle-card-hold" };
  }

  if (!usesShift && lowerKey === "u" && input.canToggleSelectedCardCritique) {
    return { kind: "toggle-card-critique" };
  }

  if (
    !usesShift
    && lowerKey === "r"
    && input.canToggleSelectedCardReviewed
    && !input.canReadingPathToggleReviewedOnly
  ) {
    return { kind: "toggle-card-reviewed" };
  }

  if (!usesShift && lowerKey === "n" && input.canReadingPathNext) {
    return { kind: "reading-next" };
  }

  if (!usesShift && lowerKey === "p" && input.canReadingPathPrev) {
    return { kind: "reading-prev" };
  }

  if (!usesShift && lowerKey === "r" && input.canReadingPathToggleReviewedOnly) {
    return { kind: "reading-toggle-reviewed-only" };
  }

  if (input.key === "Delete" || input.key === "Backspace") {
    return { kind: "delete-selection" };
  }

  const step = usesShift ? 10 : 1;
  if (input.key === "ArrowUp") {
    return { kind: "nudge", dx: 0, dy: -step };
  }

  if (input.key === "ArrowDown") {
    return { kind: "nudge", dx: 0, dy: step };
  }

  if (input.key === "ArrowLeft") {
    return { kind: "nudge", dx: -step, dy: 0 };
  }

  if (input.key === "ArrowRight") {
    return { kind: "nudge", dx: step, dy: 0 };
  }

  return null;
}

export function useHotkeys({
  onClearSelection,
  onDeleteSelection,
  onNudge,
  onToggleSelectedCardCritique,
  onToggleSelectedCardHold,
  onToggleSelectedCardReviewed,
  onReadingPathNext,
  onReadingPathPrev,
  onReadingPathToggleReviewedOnly,
  onReadingPathDisable,
}: UseHotkeysOptions) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const action = resolveHotkeyAction({
        altKey: event.altKey,
        canReadingPathDisable: Boolean(onReadingPathDisable),
        canReadingPathNext: Boolean(onReadingPathNext),
        canReadingPathPrev: Boolean(onReadingPathPrev),
        canReadingPathToggleReviewedOnly: Boolean(onReadingPathToggleReviewedOnly),
        canToggleSelectedCardCritique: Boolean(onToggleSelectedCardCritique),
        canToggleSelectedCardHold: Boolean(onToggleSelectedCardHold),
        canToggleSelectedCardReviewed: Boolean(onToggleSelectedCardReviewed),
        ctrlKey: event.ctrlKey,
        defaultPrevented: event.defaultPrevented,
        editableTarget: isEditableTarget(event.target),
        key: event.key,
        metaKey: event.metaKey,
        shiftKey: event.shiftKey,
      });

      if (!action) {
        return;
      }

      event.preventDefault();
      switch (action.kind) {
        case "clear-selection":
          onClearSelection();
          return;
        case "delete-selection":
          onDeleteSelection();
          return;
        case "nudge":
          onNudge(action.dx, action.dy);
          return;
        case "reading-disable":
          onReadingPathDisable?.();
          return;
        case "reading-next":
          onReadingPathNext?.();
          return;
        case "reading-prev":
          onReadingPathPrev?.();
          return;
        case "reading-toggle-reviewed-only":
          onReadingPathToggleReviewedOnly?.();
          return;
        case "toggle-card-critique":
          onToggleSelectedCardCritique?.();
          return;
        case "toggle-card-hold":
          onToggleSelectedCardHold?.();
          return;
        case "toggle-card-reviewed":
          onToggleSelectedCardReviewed?.();
          return;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [
    onClearSelection,
    onDeleteSelection,
    onNudge,
    onToggleSelectedCardCritique,
    onToggleSelectedCardHold,
    onToggleSelectedCardReviewed,
    onReadingPathDisable,
    onReadingPathNext,
    onReadingPathPrev,
    onReadingPathToggleReviewedOnly,
  ]);
}
