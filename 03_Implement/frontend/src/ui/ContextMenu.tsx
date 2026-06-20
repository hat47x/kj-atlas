import { useEffect, useRef } from "react";

export type ContextMenuItem =
  | { kind: "separator" }
  | { kind: "action"; label: string; onSelect: () => void; disabled?: boolean };

type ContextMenuProps = {
  x: number;
  y: number;
  items: ContextMenuItem[];
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

export function ContextMenu({ x, y, items, onClose }: ContextMenuProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handlePointerDown = (event: PointerEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        onClose();
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("pointerdown", handlePointerDown, true);
    window.addEventListener("keydown", handleKeyDown, true);
    return () => {
      window.removeEventListener("pointerdown", handlePointerDown, true);
      window.removeEventListener("keydown", handleKeyDown, true);
    };
  }, [onClose]);

  const { left, top } = clampToViewport(x, y, items.length);

  return (
    <div
      ref={ref}
      role="menu"
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
            type="button"
            role="menuitem"
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
