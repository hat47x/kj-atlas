import { useRef, useState } from "react";

import { ContextMenu, type ContextMenuItem } from "./ContextMenu";

type MenuButtonProps = {
  label: string;
  items: ContextMenuItem[];
  disabled?: boolean;
  title?: string;
};

/**
 * A header dropdown trigger. Reuses ContextMenu for the popup so the menu look,
 * outside-click dismissal, and Escape handling stay consistent with the
 * canvas right-click menu.
 */
export function MenuButton({ label, items, disabled = false, title }: MenuButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [menuPosition, setMenuPosition] = useState<{ x: number; y: number } | null>(null);

  const isOpen = menuPosition !== null;

  const toggleMenu = () => {
    if (isOpen) {
      setMenuPosition(null);
      return;
    }
    const button = buttonRef.current;
    if (!button) {
      return;
    }
    const rect = button.getBoundingClientRect();
    setMenuPosition({ x: rect.left, y: rect.bottom + 4 });
  };

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        disabled={disabled}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        title={title}
        onClick={toggleMenu}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 4,
          border: "1px solid #cbd5e1",
          backgroundColor: isOpen ? "#e0e7ff" : "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: disabled ? "not-allowed" : "pointer",
        }}
      >
        <span>{label}</span>
        <span aria-hidden="true" style={{ fontSize: 10, opacity: 0.7 }}>
          {"▾"}
        </span>
      </button>
      {isOpen && menuPosition ? (
        <ContextMenu
          x={menuPosition.x}
          y={menuPosition.y}
          items={items}
          onClose={() => setMenuPosition(null)}
        />
      ) : null}
    </>
  );
}
