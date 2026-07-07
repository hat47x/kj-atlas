import { useState } from "react";
import type { KeyboardEvent } from "react";

import { t } from "../i18n/translate";
import { formatAltShiftShortcut, formatModShiftShortcut, formatModShortcut, isMacPlatform } from "./os_shortcut_format";

type ShortcutCheatsheetProps = {
  onClose: () => void;
};

const kbdStyle = {
  display: "inline-block",
  fontFamily: "monospace",
  fontSize: 11,
  borderRadius: 5,
  padding: "2px 8px",
  backgroundColor: "#f1f5f9",
  border: "1px solid #cbd5e1",
  color: "#0f172a",
  whiteSpace: "nowrap",
} as const;

const groupTitleStyle = {
  fontSize: 11,
  fontWeight: 700,
  color: "#475569",
  marginBottom: 6,
} as const;

const rowStyle = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12,
  fontSize: 13,
  color: "#0f172a",
  padding: "4px 0",
} as const;

function Kbd({ children }: { children: string }) {
  return <kbd style={kbdStyle}>{children}</kbd>;
}

function Row({ label, shortcuts }: { label: string; shortcuts: string[] }) {
  return (
    <div style={rowStyle}>
      <span>{label}</span>
      <span style={{ display: "flex", gap: 6 }}>
        {shortcuts.map((shortcut) => (
          <Kbd key={shortcut}>{shortcut}</Kbd>
        ))}
      </span>
    </div>
  );
}

// UX-SHORTCUT-01 AC-4 (ADR-0048 D2, Round 5 redline): only lists shortcuts
// that actually exist in the app today. A manual Mac/Windows·Linux switch
// (defaulting to auto-detection) previews the other platform's notation.
export function ShortcutCheatsheet({ onClose }: ShortcutCheatsheetProps) {
  const [useMacNotation, setUseMacNotation] = useState(isMacPlatform());

  const handleKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      onClose();
    }
  };

  const mod = (key: string) => formatModShortcut(key, useMacNotation);
  const modShift = (key: string) => formatModShiftShortcut(key, useMacNotation);
  const altShift = (key: string) => formatAltShiftShortcut(key, useMacNotation);

  return (
    <div
      data-ui-region="shortcut-cheatsheet-backdrop"
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
        paddingTop: "8vh",
        backgroundColor: "rgba(15, 23, 42, 0.35)",
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t("shortcut_cheatsheet.title")}
        onKeyDown={handleKeyDown}
        style={{
          width: "min(520px, 92vw)",
          maxHeight: "78vh",
          display: "flex",
          flexDirection: "column",
          backgroundColor: "#ffffff",
          borderRadius: 12,
          boxShadow: "0 16px 40px rgba(15, 23, 42, 0.35)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "12px 16px",
            borderBottom: "1px solid #e2e8f0",
          }}
        >
          <span style={{ fontSize: 14, fontWeight: 700, color: "#0f172a" }}>{t("shortcut_cheatsheet.title")}</span>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ display: "inline-flex", border: "1px solid #cbd5e1", borderRadius: 6, overflow: "hidden" }}>
              <button
                type="button"
                onClick={() => setUseMacNotation(true)}
                aria-pressed={useMacNotation}
                style={{
                  border: "none",
                  padding: "3px 8px",
                  fontSize: 11,
                  cursor: "pointer",
                  backgroundColor: useMacNotation ? "#e0e7ff" : "#ffffff",
                }}
              >
                {t("shortcut_cheatsheet.os.mac")}
              </button>
              <button
                type="button"
                onClick={() => setUseMacNotation(false)}
                aria-pressed={!useMacNotation}
                style={{
                  border: "none",
                  padding: "3px 8px",
                  fontSize: 11,
                  cursor: "pointer",
                  backgroundColor: !useMacNotation ? "#e0e7ff" : "#ffffff",
                }}
              >
                {t("shortcut_cheatsheet.os.other")}
              </button>
            </div>
            <button
              type="button"
              autoFocus
              onClick={onClose}
              aria-label={t("shortcut_cheatsheet.close")}
              style={{
                border: "1px solid #cbd5e1",
                borderRadius: 4,
                backgroundColor: "#ffffff",
                color: "#475569",
                fontSize: 11,
                fontWeight: 600,
                padding: "2px 7px",
                cursor: "pointer",
              }}
            >
              ✕
            </button>
          </div>
        </div>
        <div style={{ overflowY: "auto", padding: "8px 16px 16px" }}>
          <div style={groupTitleStyle}>{t("shortcut_cheatsheet.group.hold")}</div>
          <Row label={t("command_palette.command.toggle_hold")} shortcuts={["H"]} />
          <Row label={t("shortcut_cheatsheet.critique_quick_flag")} shortcuts={["U"]} />
          <Row label={t("shortcut_cheatsheet.toggle_reviewed")} shortcuts={["R"]} />
          <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>
            {t("shortcut_cheatsheet.disabled_while_editing")}
          </div>

          <div style={{ ...groupTitleStyle, marginTop: 14 }}>{t("shortcut_cheatsheet.group.selection")}</div>
          <Row label={t("shortcut_cheatsheet.delete_selection")} shortcuts={["Delete"]} />
          <Row label={t("shortcut_cheatsheet.nudge_selection")} shortcuts={["↑", "↓", "←", "→"]} />
          <Row label={t("shortcut_cheatsheet.clear_selection_or_close")} shortcuts={["Esc"]} />

          <div style={{ ...groupTitleStyle, marginTop: 14 }}>{t("shortcut_cheatsheet.group.history")}</div>
          <Row label={t("app.toolbar.undo")} shortcuts={[mod("Z")]} />
          <Row label={t("app.toolbar.redo")} shortcuts={[mod("Y"), modShift("Z")]} />

          <div style={{ ...groupTitleStyle, marginTop: 14 }}>{t("shortcut_cheatsheet.group.organize")}</div>
          <Row label={t("app.toolbar.create_island")} shortcuts={[mod("G")]} />

          <div style={{ ...groupTitleStyle, marginTop: 14 }}>{t("shortcut_cheatsheet.group.nav")}</div>
          <Row label={t("command_palette.title")} shortcuts={[mod("K")]} />
          <Row label={t("shortcut_cheatsheet.view_mode")} shortcuts={[mod("1"), mod("2"), mod("3")]} />
          <Row label={t("shortcut_cheatsheet.hierarchy_level")} shortcuts={[altShift("1"), altShift("2")]} />
          <Row label={t("shortcut_cheatsheet.title")} shortcuts={["?"]} />

          <div style={{ ...groupTitleStyle, marginTop: 14 }}>{t("shortcut_cheatsheet.group.reading_path")}</div>
          <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>
            {t("shortcut_cheatsheet.reading_path_scope")}
          </div>
          <Row label={t("shortcut_cheatsheet.reading_path_next")} shortcuts={["N"]} />
          <Row label={t("shortcut_cheatsheet.reading_path_prev")} shortcuts={["P"]} />
          <Row label={t("shortcut_cheatsheet.reading_path_reviewed_only")} shortcuts={["R"]} />
        </div>
      </div>
    </div>
  );
}
