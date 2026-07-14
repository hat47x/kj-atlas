import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent as ReactKeyboardEvent } from "react";
import { t } from "../i18n/translate";

export type MenuItemDef = {
  id: string;
  label: string;
  shortcutHint?: string;
  disabled?: boolean;
  /** Present only for checkable items (role="menuitemcheckbox"). */
  checked?: boolean;
  run: () => void;
};

export type MenuRowDef = { kind: "header"; label: string } | { kind: "item"; item: MenuItemDef };

export type MenuCategoryDef = {
  id: string;
  label: string;
  rows: MenuRowDef[];
};

type MenuBarProps = {
  categories: MenuCategoryDef[];
};

const COLLAPSE_WIDTH_PX = 768;

function flattenRows(categories: MenuCategoryDef[]): MenuRowDef[] {
  const rows: MenuRowDef[] = [];
  categories.forEach((category) => {
    rows.push({ kind: "header", label: category.label });
    rows.push(...category.rows);
  });
  return rows;
}

function isEnabledItemRow(row: MenuRowDef | undefined): row is { kind: "item"; item: MenuItemDef } {
  return Boolean(row) && row!.kind === "item" && !row!.item.disabled;
}

// UX-MENU-01 (ADR-0048 D2, collapse-layer 3): a persistent menu bar that is
// the permanent, categorized address for classifiable commands. Every item
// delegates to an EXISTING handler passed in by the caller (App.tsx) — no
// new business logic lives here. Implements the WAI-ARIA menubar keyboard
// pattern (arrow cycling, Home/End, Escape-close-with-focus-return) since
// neither ContextMenu.tsx nor CommandPalette.tsx already provided it.
export function MenuBar({ categories }: MenuBarProps) {
  const [openId, setOpenId] = useState<string | null>(null);
  const [activeRowIndex, setActiveRowIndex] = useState(0);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);
  const topButtonRefs = useRef<Map<string, HTMLButtonElement>>(new Map());
  const rowRefs = useRef<Map<number, HTMLButtonElement>>(new Map());
  const wasCollapsedRef = useRef(isCollapsed);

  useEffect(() => {
    const updateCollapsed = () => {
      setIsCollapsed(window.innerWidth < COLLAPSE_WIDTH_PX);
    };
    updateCollapsed();
    window.addEventListener("resize", updateCollapsed);
    return () => window.removeEventListener("resize", updateCollapsed);
  }, []);

  useEffect(() => {
    if (!openId) {
      return;
    }

    const handlePointerDown = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpenId(null);
      }
    };
    window.addEventListener("mousedown", handlePointerDown);
    return () => window.removeEventListener("mousedown", handlePointerDown);
  }, [openId]);

  const topEntries: Array<{ id: string; label: string }> = isCollapsed
    ? [{ id: "__collapsed__", label: t("menu_bar.collapsed_trigger") }]
    : categories.map((category) => ({ id: category.id, label: category.label }));

  // If crossing the collapse breakpoint unmounts the top-level button that
  // currently holds focus (e.g. "File" mid-resize), the browser drops focus
  // to <body> with nothing to catch it. Redirect to whatever top entry
  // replaced it.
  useEffect(() => {
    if (wasCollapsedRef.current === isCollapsed) {
      return;
    }
    wasCollapsedRef.current = isCollapsed;
    if (typeof document !== "undefined" && (document.activeElement === document.body || document.activeElement === null)) {
      const firstId = topEntries[0]?.id;
      if (firstId) {
        topButtonRefs.current.get(firstId)?.focus();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isCollapsed]);

  // Only focus a row if it's actually enabled; otherwise fall back to the
  // menu container itself so Escape/arrow keys keep reaching
  // handleMenuKeyDown instead of getting stranded on the top button (which
  // would silently route keys to handleTopKeyDown, unable to navigate the
  // visibly-open menu). This also covers the case where every row in a
  // category is disabled (e.g. Edit's items while isReadOnly).
  useEffect(() => {
    if (openId === null) {
      return;
    }
    const activeButton = rowRefs.current.get(activeRowIndex);
    if (activeButton && !activeButton.disabled) {
      activeButton.focus();
    } else {
      menuRef.current?.focus();
    }
  }, [openId, activeRowIndex]);

  const rowsForId = (id: string | null): MenuRowDef[] => {
    if (id === null) {
      return [];
    }
    if (isCollapsed) {
      return flattenRows(categories);
    }
    return categories.find((category) => category.id === id)?.rows ?? [];
  };

  const openRows: MenuRowDef[] = rowsForId(openId);

  const closeAndReturnFocus = (idToFocus: string | null) => {
    setOpenId(null);
    if (idToFocus) {
      topButtonRefs.current.get(idToFocus)?.focus();
    }
  };

  const firstEnabledRowIndexIn = (rows: MenuRowDef[]): number => rows.findIndex((row) => isEnabledItemRow(row));
  const lastEnabledRowIndexIn = (rows: MenuRowDef[]): number => {
    for (let index = rows.length - 1; index >= 0; index -= 1) {
      if (isEnabledItemRow(rows[index])) {
        return index;
      }
    }
    return -1;
  };
  const firstEnabledRowIndex = (): number => firstEnabledRowIndexIn(openRows);
  const lastEnabledRowIndex = (): number => lastEnabledRowIndexIn(openRows);

  // Opening a category ALWAYS drills into its first enabled item (matches
  // click-to-open behavior whether triggered by click, ArrowDown/Enter/Space,
  // or ArrowRight/Left/Home/End rollover while a menu is already open).
  const openMenu = (id: string) => {
    setOpenId(id);
    setActiveRowIndex(Math.max(firstEnabledRowIndexIn(rowsForId(id)), 0));
  };

  const moveTopFocus = (fromId: string, direction: 1 | -1) => {
    const ids = topEntries.map((entry) => entry.id);
    const currentIndex = ids.indexOf(fromId);
    const nextIndex = (currentIndex + direction + ids.length) % ids.length;
    const nextId = ids[nextIndex];
    if (openId) {
      // A menu is already open: roll over and drill into the sibling
      // category's first item (openMenu's effect moves focus there).
      openMenu(nextId);
    } else {
      // No menu open yet: plain roving-tabindex focus move, nothing opens.
      topButtonRefs.current.get(nextId)?.focus();
    }
    return nextId;
  };

  const handleTopKeyDown = (event: ReactKeyboardEvent<HTMLButtonElement>, id: string) => {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      moveTopFocus(id, 1);
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      moveTopFocus(id, -1);
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      const firstId = topEntries[0]?.id;
      if (firstId) {
        topButtonRefs.current.get(firstId)?.focus();
        if (openId) {
          openMenu(firstId);
        }
      }
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      const lastId = topEntries[topEntries.length - 1]?.id;
      if (lastId) {
        topButtonRefs.current.get(lastId)?.focus();
        if (openId) {
          openMenu(lastId);
        }
      }
      return;
    }
    if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openMenu(id);
      return;
    }
    if (event.key === "Escape" && openId) {
      event.preventDefault();
      closeAndReturnFocus(id);
    }
  };

  const runRow = (row: MenuRowDef, triggerIdForFocus: string | null) => {
    if (row.kind !== "item" || row.item.disabled) {
      return;
    }
    // Focus the trigger BEFORE the row unmounts (same synchronous-focus-
    // before-unmount pattern as handleCloseCanvasLegend/closeCommandPalette)
    // so a run() that doesn't itself grab focus (a toggle, an export) never
    // drops focus to <body>. A run() that DOES open another panel/dialog
    // (e.g. the shortcut cheatsheet) still wins: it reads the NOW-current
    // activeElement (this trigger button) or grabs its own focus in a later
    // effect, either way superseding this.
    if (triggerIdForFocus) {
      topButtonRefs.current.get(triggerIdForFocus)?.focus();
    }
    setOpenId(null);
    row.item.run();
  };

  const handleMenuKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeAndReturnFocus(isCollapsed ? "__collapsed__" : openId);
      return;
    }
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveRowIndex((previous) => {
        for (let index = previous + 1; index < openRows.length; index += 1) {
          if (isEnabledItemRow(openRows[index])) {
            return index;
          }
        }
        return firstEnabledRowIndex();
      });
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveRowIndex((previous) => {
        for (let index = previous - 1; index >= 0; index -= 1) {
          if (isEnabledItemRow(openRows[index])) {
            return index;
          }
        }
        return lastEnabledRowIndex();
      });
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      setActiveRowIndex(Math.max(firstEnabledRowIndex(), 0));
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      setActiveRowIndex(Math.max(lastEnabledRowIndex(), 0));
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      const row = openRows[activeRowIndex];
      if (row) {
        runRow(row, openId);
      }
      return;
    }
    if (!isCollapsed && (event.key === "ArrowRight" || event.key === "ArrowLeft")) {
      event.preventDefault();
      if (openId) {
        moveTopFocus(openId, event.key === "ArrowRight" ? 1 : -1);
      }
    }
  };

  return (
    <div
      ref={containerRef}
      data-ui-region="menu-bar"
      role="menubar"
      aria-label={t("menu_bar.aria_label")}
      style={{ position: "relative", display: "flex", alignItems: "center", gap: 2, flexWrap: "nowrap" }}
    >
      {topEntries.map((entry) => {
        const isOpen = isCollapsed ? openId !== null : openId === entry.id;
        return (
          <button
            key={entry.id}
            ref={(element) => {
              if (element) {
                topButtonRefs.current.set(entry.id, element);
              } else {
                topButtonRefs.current.delete(entry.id);
              }
            }}
            type="button"
            role="menuitem"
            aria-haspopup="menu"
            aria-expanded={isOpen}
            data-ui-menu-category={entry.id}
            onClick={() => {
              setOpenId((previous) => {
                const next = (isCollapsed ? previous !== null : previous === entry.id) ? null : entry.id;
                if (next) {
                  setActiveRowIndex(Math.max(firstEnabledRowIndexIn(rowsForId(next)), 0));
                }
                return next;
              });
            }}
            onKeyDown={(event) => handleTopKeyDown(event, entry.id)}
            style={{
              border: "1px solid transparent",
              backgroundColor: isOpen ? "#e0e7ff" : "transparent",
              color: "#0f172a",
              borderRadius: 6,
              padding: "6px 10px",
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {entry.label}
          </button>
        );
      })}
      {openId ? (
        <div
          ref={menuRef}
          role="menu"
          aria-label={isCollapsed ? t("menu_bar.aria_label") : categories.find((category) => category.id === openId)?.label}
          tabIndex={-1}
          onKeyDown={handleMenuKeyDown}
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            zIndex: 60,
            marginTop: 4,
            minWidth: 220,
            maxHeight: "70vh",
            overflowY: "auto",
            backgroundColor: "#ffffff",
            border: "1px solid #cbd5e1",
            borderRadius: 8,
            boxShadow: "0 8px 24px rgba(15, 23, 42, 0.18)",
            padding: 4,
          }}
        >
          {openRows.map((row, index) => {
            if (row.kind === "header") {
              return (
                <div
                  key={`header-${row.label}-${index}`}
                  role="presentation"
                  style={{
                    padding: "6px 8px 2px",
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#64748b",
                    textTransform: "uppercase",
                    letterSpacing: 0.4,
                  }}
                >
                  {row.label}
                </div>
              );
            }

            const { item } = row;
            const isActive = index === activeRowIndex;
            const isCheckable = item.checked !== undefined;
            return (
              <button
                key={item.id}
                ref={(element) => {
                  if (element) {
                    rowRefs.current.set(index, element);
                  } else {
                    rowRefs.current.delete(index);
                  }
                }}
                type="button"
                role={isCheckable ? "menuitemcheckbox" : "menuitem"}
                aria-checked={isCheckable ? item.checked : undefined}
                aria-disabled={item.disabled ? "true" : undefined}
                tabIndex={isActive ? 0 : -1}
                disabled={item.disabled}
                onMouseEnter={() => {
                  if (!item.disabled) {
                    setActiveRowIndex(index);
                  }
                }}
                onClick={() => runRow(row, openId)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  width: "100%",
                  minHeight: 32,
                  padding: "0 8px",
                  border: "none",
                  borderRadius: 6,
                  fontSize: 13,
                  textAlign: "left",
                  color: item.disabled ? "#94a3b8" : "#0f172a",
                  backgroundColor: isActive && !item.disabled ? "#eff6ff" : "transparent",
                  cursor: item.disabled ? "not-allowed" : "pointer",
                }}
              >
                <span aria-hidden="true" style={{ width: 14, fontSize: 12, color: "#1d4ed8" }}>
                  {isCheckable && item.checked ? "✓" : ""}
                </span>
                <span style={{ flex: 1 }}>{item.label}</span>
                {item.shortcutHint ? (
                  <span style={{ fontSize: 11, color: "#94a3b8", fontFamily: "monospace" }}>{item.shortcutHint}</span>
                ) : null}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
