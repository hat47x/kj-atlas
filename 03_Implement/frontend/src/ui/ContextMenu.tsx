import { useEffect, useRef, type KeyboardEvent as ReactKeyboardEvent } from "react";

export type ContextMenuItem =
  | { kind: "separator" }
  | { kind: "action"; label: string; onSelect: () => void; disabled?: boolean };

type ContextMenuProps = {
  x: number;
  y: number;
  items: ContextMenuItem[];
  ariaLabel: string;
  returnFocusTo: HTMLElement | null;
  onClose: () => void;
};

const MENU_MIN_WIDTH = 190;
const MENU_ITEM_HEIGHT = 32;
const MENU_PADDING = 8;

function clampToViewport(x: number, y: number, itemCount: number): { left: number; top: number } {
  if (typeof window === "undefined") {
    return { left: x, top: y };
  }

  const estimatedHeight = itemCount * MENU_ITEM_HEIGHT + MENU_PADDING;
  const left = Math.max(4, Math.min(x, window.innerWidth - MENU_MIN_WIDTH - 4));
  const top = Math.max(4, Math.min(y, window.innerHeight - estimatedHeight - 4));
  return { left, top };
}

export function ContextMenu({ x, y, items, ariaLabel, returnFocusTo, onClose }: ContextMenuProps) {
  const ref = useRef<HTMLDivElement>(null);
  const itemRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const enabledItems = () => itemRefs.current.filter((item): item is HTMLButtonElement => Boolean(item && !item.disabled));

  const restorePreviousFocus = () => {
    if (returnFocusTo?.isConnected) returnFocusTo.focus();
  };

  useEffect(() => {
    enabledItems()[0]?.focus();

    const handlePointerDown = (event: PointerEvent) => {
      if (ref.current && event.target instanceof Node && !ref.current.contains(event.target)) {
        onClose();
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        onClose();
        restorePreviousFocus();
      }
    };

    window.addEventListener("pointerdown", handlePointerDown, true);
    window.addEventListener("keydown", handleKeyDown, true);
    return () => {
      window.removeEventListener("pointerdown", handlePointerDown, true);
      window.removeEventListener("keydown", handleKeyDown, true);
    };
  }, [onClose, returnFocusTo]);

  const { left, top } = clampToViewport(x, y, items.length);

  const handleMenuKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>) => {
    const enabled = enabledItems();
    if (enabled.length === 0) return;
    const currentIndex = enabled.indexOf(document.activeElement as HTMLButtonElement);
    let nextIndex: number | null = null;
    if (event.key === "ArrowDown") nextIndex = currentIndex < 0 ? 0 : (currentIndex + 1) % enabled.length;
    if (event.key === "ArrowUp") nextIndex = currentIndex < 0 ? enabled.length - 1 : (currentIndex - 1 + enabled.length) % enabled.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = enabled.length - 1;
    if (nextIndex === null) return;
    event.preventDefault();
    event.stopPropagation();
    enabled[nextIndex]?.focus();
  };

  return (
    <div
      ref={ref}
      role="menu"
      aria-label={ariaLabel}
      onKeyDown={handleMenuKeyDown}
      onContextMenu={(event) => event.preventDefault()}
      style={{
        position: "fixed",
        top,
        left,
        minWidth: MENU_MIN_WIDTH,
        backgroundColor: "#ffffff",
        border: "1px solid #cbd5e1",
        borderRadius: 8,
        boxShadow: "0 8px 24px rgba(15, 23, 42, 0.18)",
        padding: 4,
        zIndex: 1000,
      }}
    >
      {items.map((item, index) =>
        item.kind === "separator" ? (
          <div
            key={`separator-${index}`}
            style={{ height: 1, backgroundColor: "#e2e8f0", margin: "4px 6px" }}
          />
        ) : (
          <button
            key={`item-${index}`}
            ref={(element) => {
              itemRefs.current[index] = element;
            }}
            type="button"
            role="menuitem"
            tabIndex={-1}
            disabled={item.disabled}
            onClick={() => {
              if (item.disabled) {
                return;
              }
              item.onSelect();
              onClose();
            }}
            style={{
              display: "block",
              width: "100%",
              textAlign: "left",
              border: "none",
              backgroundColor: "transparent",
              color: item.disabled ? "#94a3b8" : "#0f172a",
              borderRadius: 6,
              padding: "6px 10px",
              fontSize: 13,
              lineHeight: 1.4,
              cursor: item.disabled ? "not-allowed" : "pointer",
            }}
          >
            {item.label}
          </button>
        )
      )}
    </div>
  );
}
