import { useEffect } from "react";

type UseHotkeysOptions = {
  onClearSelection: () => void;
  onDeleteSelection: () => void;
  onNudge: (dx: number, dy: number) => void;
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

export function useHotkeys({
  onClearSelection,
  onDeleteSelection,
  onNudge,
  onReadingPathNext,
  onReadingPathPrev,
  onReadingPathToggleReviewedOnly,
  onReadingPathDisable,
}: UseHotkeysOptions) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (isEditableTarget(event.target) || event.defaultPrevented) {
        return;
      }

      if (event.metaKey || event.ctrlKey || event.altKey) {
        return;
      }

      if (event.key === "Escape" && onReadingPathDisable) {
        event.preventDefault();
        onReadingPathDisable();
        return;
      }

      if (event.key === "Escape") {
        event.preventDefault();
        onClearSelection();
        return;
      }

      if (event.key === "n" && onReadingPathNext) {
        event.preventDefault();
        onReadingPathNext();
        return;
      }

      if (event.key === "p" && onReadingPathPrev) {
        event.preventDefault();
        onReadingPathPrev();
        return;
      }

      if (event.key === "r" && onReadingPathToggleReviewedOnly) {
        event.preventDefault();
        onReadingPathToggleReviewedOnly();
        return;
      }

      if (event.key === "Delete" || event.key === "Backspace") {
        event.preventDefault();
        onDeleteSelection();
        return;
      }

      const step = event.shiftKey ? 10 : 1;
      if (event.key === "ArrowUp") {
        event.preventDefault();
        onNudge(0, -step);
        return;
      }

      if (event.key === "ArrowDown") {
        event.preventDefault();
        onNudge(0, step);
        return;
      }

      if (event.key === "ArrowLeft") {
        event.preventDefault();
        onNudge(-step, 0);
        return;
      }

      if (event.key === "ArrowRight") {
        event.preventDefault();
        onNudge(step, 0);
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
    onReadingPathDisable,
    onReadingPathNext,
    onReadingPathPrev,
    onReadingPathToggleReviewedOnly,
  ]);
}
