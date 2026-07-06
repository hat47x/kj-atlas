import { useEffect, useRef, type KeyboardEvent } from "react";

import { t } from "../i18n/translate";

type ShortcutHelpDialogProps = {
  onClose: () => void;
};

type ShortcutHelpEntry = {
  keys: string[];
  label: string;
};

const focusableSelector = [
  "button:not([disabled])",
  "a[href]",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(", ");

const dialogStyle = {
  position: "fixed",
  inset: 0,
  zIndex: 900,
  backgroundColor: "rgba(15, 23, 42, 0.32)",
  display: "grid",
  placeItems: "center",
  padding: 16,
} as const;

const panelStyle = {
  width: "min(720px, calc(100vw - 32px))",
  maxHeight: "min(680px, calc(100vh - 32px))",
  overflowY: "auto",
  border: "1px solid #cbd5e1",
  borderRadius: 8,
  backgroundColor: "#ffffff",
  boxShadow: "0 18px 50px rgba(15, 23, 42, 0.24)",
  padding: 16,
  display: "grid",
  gap: 14,
} as const;

const sectionStyle = {
  display: "grid",
  gap: 6,
} as const;

const rowStyle = {
  display: "grid",
  gridTemplateColumns: "minmax(116px, max-content) 1fr",
  gap: 10,
  alignItems: "center",
  fontSize: 12,
  color: "#334155",
  lineHeight: 1.45,
} as const;

const keyGroupStyle = {
  display: "flex",
  alignItems: "center",
  flexWrap: "wrap",
  gap: 4,
} as const;

const keyStyle = {
  minWidth: 22,
  border: "1px solid #cbd5e1",
  borderRadius: 4,
  backgroundColor: "#f8fafc",
  color: "#0f172a",
  fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
  fontSize: 11,
  fontWeight: 700,
  lineHeight: "18px",
  textAlign: "center",
  padding: "0 5px",
} as const;

function getFocusableElements(root: HTMLElement): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(focusableSelector)).filter(
    (element) => !element.hasAttribute("disabled") && element.getAttribute("aria-hidden") !== "true",
  );
}

function getPrimaryModifierLabel(): string {
  const platform = window.navigator.platform.toLowerCase();
  return platform.includes("mac") ? "Cmd" : "Ctrl";
}

function keys(...values: string[]): string[] {
  return values;
}

function renderKeys(values: string[]) {
  return (
    <span style={keyGroupStyle}>
      {values.map((value, index) => (
        <span key={`${value}-${index}`} style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
          {index > 0 ? <span aria-hidden="true" style={{ color: "#64748b" }}>+</span> : null}
          <kbd style={keyStyle}>{value}</kbd>
        </span>
      ))}
    </span>
  );
}

function ShortcutSection({ title, entries }: { title: string; entries: ShortcutHelpEntry[] }) {
  return (
    <section style={sectionStyle}>
      <h3 style={{ margin: 0, color: "#0f172a", fontSize: 13, fontWeight: 800 }}>{title}</h3>
      <div style={{ display: "grid", gap: 5 }}>
        {entries.map((entry) => (
          <div key={`${entry.keys.join("+")}-${entry.label}`} style={rowStyle}>
            {renderKeys(entry.keys)}
            <span>{entry.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function ShortcutHelpDialog({ onClose }: ShortcutHelpDialogProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const primaryModifier = getPrimaryModifierLabel();
  const viewEntries: ShortcutHelpEntry[] = [
    { keys: keys(primaryModifier, "1"), label: t("shortcut_help.view.explore") },
    { keys: keys(primaryModifier, "2"), label: t("shortcut_help.view.review") },
    { keys: keys(primaryModifier, "3"), label: t("shortcut_help.view.summary") },
    { keys: keys("Alt", "Shift", "1/2/3"), label: t("shortcut_help.view.structure") },
  ];
  const cardEntries: ShortcutHelpEntry[] = [
    { keys: keys("H"), label: t("shortcut_help.card.hold") },
    { keys: keys("U"), label: t("shortcut_help.card.critique") },
    { keys: keys("R"), label: t("shortcut_help.card.reviewed") },
    { keys: keys("Delete / Backspace"), label: t("shortcut_help.card.delete") },
    { keys: keys("Arrow"), label: t("shortcut_help.card.nudge") },
    { keys: keys("Shift", "Arrow"), label: t("shortcut_help.card.nudge_large") },
  ];
  const readingEntries: ShortcutHelpEntry[] = [
    { keys: keys("N"), label: t("shortcut_help.reading.next") },
    { keys: keys("P"), label: t("shortcut_help.reading.prev") },
    { keys: keys("R"), label: t("shortcut_help.reading.reviewed_only") },
    { keys: keys("Esc"), label: t("shortcut_help.reading.disable") },
  ];
  const systemEntries: ShortcutHelpEntry[] = [
    { keys: keys("?"), label: t("shortcut_help.system.open") },
    { keys: keys("Esc"), label: t("shortcut_help.system.close") },
  ];

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const [firstFocusable] = panelRef.current ? getFocusableElements(panelRef.current) : [];
      (firstFocusable ?? panelRef.current)?.focus();
    });

    return () => window.cancelAnimationFrame(frame);
  }, []);

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      onClose();
      return;
    }

    if (event.key !== "Tab" || !panelRef.current) {
      return;
    }

    const focusableElements = getFocusableElements(panelRef.current);
    if (focusableElements.length === 0) {
      event.preventDefault();
      panelRef.current.focus();
      return;
    }

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    if (event.shiftKey && window.document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
      return;
    }

    if (!event.shiftKey && window.document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  };

  return (
    <div data-ui-region="shortcut-help-backdrop" style={dialogStyle}>
      <div
        ref={panelRef}
        data-ui-region="shortcut-help"
        role="dialog"
        aria-modal="true"
        aria-label={t("shortcut_help.title")}
        tabIndex={-1}
        onKeyDown={handleKeyDown}
        style={panelStyle}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start" }}>
          <div style={{ display: "grid", gap: 4 }}>
            <h2 style={{ margin: 0, color: "#0f172a", fontSize: 16, fontWeight: 800 }}>
              {t("shortcut_help.title")}
            </h2>
            <p style={{ margin: 0, color: "#475569", fontSize: 12, lineHeight: 1.45 }}>
              {t("shortcut_help.intro")}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label={t("shortcut_help.close")}
            style={{
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              backgroundColor: "#ffffff",
              color: "#0f172a",
              padding: "4px 10px",
              fontSize: 12,
              fontWeight: 700,
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            {t("shortcut_help.close")}
          </button>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 14 }}>
          <ShortcutSection title={t("shortcut_help.section.view")} entries={viewEntries} />
          <ShortcutSection title={t("shortcut_help.section.card")} entries={cardEntries} />
          <ShortcutSection title={t("shortcut_help.section.reading")} entries={readingEntries} />
          <ShortcutSection title={t("shortcut_help.section.system")} entries={systemEntries} />
        </div>
        <div style={{ display: "grid", gap: 4, borderTop: "1px solid #e2e8f0", paddingTop: 10, color: "#475569", fontSize: 12, lineHeight: 1.45 }}>
          <p style={{ margin: 0 }}>{t("shortcut_help.note.platform")}</p>
          <p style={{ margin: 0 }}>{t("shortcut_help.note.editing")}</p>
        </div>
      </div>
    </div>
  );
}
