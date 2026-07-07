import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent } from "react";

import { t } from "../i18n/translate";

export type PaletteCommandCategory = "hold" | "create" | "nav" | "history" | "safety";

export type PaletteCommand = {
  id: string;
  label: string;
  category: PaletteCommandCategory;
  shortcutHint?: string;
  run: () => void;
};

type CommandPaletteProps = {
  commands: PaletteCommand[];
  /** Escape/backdrop dismissal (cancel path): caller restores focus to the pre-open trigger. */
  onClose: () => void;
  /** Enter/click execution: caller closes WITHOUT forcing focus (the command's own side effects decide). */
  onRunCommand: (command: PaletteCommand) => void;
};

// UX-CMDK-01 (ADR-0048 D2, collapse-layer 5): a dialog-style palette that
// delegates every action to an existing handler. No new business logic lives
// here — only search, keyboard navigation, and the dialog contract.
const CATEGORY_GLYPH: Record<PaletteCommandCategory, string> = {
  hold: "●",
  create: "＋",
  nav: "▤",
  history: "↺",
  safety: "◆",
};

export function CommandPalette({ commands, onClose, onRunCommand }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const listboxId = "command-palette-listbox";

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Retention-first ordering (ADR-0048 D2 CB-2): "hold" category commands are
  // pinned above the rest. Array.prototype.sort is stable, so relative order
  // within each group is preserved.
  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const matches =
      normalizedQuery.length === 0
        ? commands
        : commands.filter((command) => command.label.toLowerCase().includes(normalizedQuery));

    return [...matches].sort((a, b) => {
      const aWeight = a.category === "hold" ? 0 : 1;
      const bWeight = b.category === "hold" ? 0 : 1;
      return aWeight - bWeight;
    });
  }, [commands, query]);

  useEffect(() => {
    setActiveIndex((previous) => {
      if (filtered.length === 0) {
        return 0;
      }
      return Math.min(previous, filtered.length - 1);
    });
  }, [filtered]);

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      onClose();
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((previous) => Math.min(previous + 1, Math.max(filtered.length - 1, 0)));
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((previous) => Math.max(previous - 1, 0));
      return;
    }

    if (event.key === "Enter") {
      event.preventDefault();
      const command = filtered[activeIndex];
      if (command) {
        onRunCommand(command);
      }
    }
  };

  const activeOptionId = filtered[activeIndex] ? `command-palette-option-${filtered[activeIndex].id}` : undefined;

  return (
    <div
      data-ui-region="command-palette-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        paddingTop: "12vh",
        backgroundColor: "rgba(15, 23, 42, 0.35)",
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t("command_palette.title")}
        onKeyDown={handleKeyDown}
        style={{
          width: "min(560px, 92vw)",
          maxHeight: "60vh",
          display: "flex",
          flexDirection: "column",
          backgroundColor: "#ffffff",
          borderRadius: 12,
          boxShadow: "0 16px 40px rgba(15, 23, 42, 0.35)",
          overflow: "hidden",
        }}
      >
        <input
          ref={inputRef}
          data-command-palette-input="true"
          type="text"
          role="combobox"
          aria-expanded="true"
          aria-controls={listboxId}
          aria-activedescendant={activeOptionId}
          autoComplete="off"
          spellCheck={false}
          placeholder={t("command_palette.placeholder")}
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setActiveIndex(0);
          }}
          style={{
            height: 44,
            fontSize: 13,
            padding: "0 14px",
            border: "none",
            borderBottom: "1px solid #e2e8f0",
            outline: "none",
            boxSizing: "border-box",
          }}
        />
        <div id={listboxId} role="listbox" aria-label={t("command_palette.title")} style={{ overflowY: "auto" }}>
          {filtered.length === 0 ? (
            <div style={{ padding: "12px 14px", fontSize: 12, color: "#64748b" }}>
              {t("command_palette.no_results")}
            </div>
          ) : (
            filtered.map((command, index) => {
              const isActive = index === activeIndex;
              return (
                <div
                  key={command.id}
                  id={`command-palette-option-${command.id}`}
                  role="option"
                  aria-selected={isActive}
                  onMouseEnter={() => setActiveIndex(index)}
                  onClick={() => onRunCommand(command)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    minHeight: 36,
                    padding: "0 14px",
                    fontSize: 13,
                    color: "#0f172a",
                    backgroundColor: isActive ? "#eff6ff" : "transparent",
                    cursor: "pointer",
                  }}
                >
                  <span aria-hidden="true" style={{ width: 16, textAlign: "center", color: "#94a3b8", fontSize: 12 }}>
                    {CATEGORY_GLYPH[command.category]}
                  </span>
                  <span style={{ flex: 1 }}>{command.label}</span>
                  {command.shortcutHint ? (
                    <span style={{ fontSize: 11, color: "#94a3b8", fontFamily: "monospace" }}>
                      {command.shortcutHint}
                    </span>
                  ) : null}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
