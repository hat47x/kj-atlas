import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { t } from "../i18n/translate";

// UX-NAV-02 (resolves ADR-0052 C-5): role=tablist container for the work-mode
// surface's 5 co-equal panes. Manual activation (WAI-ARIA APG "tabs, manual
// activation"): arrow keys move a roving tabIndex focus target across tab
// buttons WITHOUT switching the active panel; native <button> onClick (which
// also fires for a keyboard Enter/Space on the focused button) is what
// actually activates a tab. This keeps the activation logic to a single
// onClick handler instead of intercepting Enter/Space separately.
//
// Non-active tabpanels are `hidden`, not unmounted: switching tabs must not
// lose in-progress input, candidates, or async results, and must not start
// new side effects for a panel the user isn't looking at (a hidden subtree
// simply stays mounted with its existing React state untouched).
//
// Staged Escape: pressing Escape while focus is inside a tabpanel's content
// moves focus OUT to that tab's button (stopping propagation) rather than
// closing the surrounding work-mode overlay. A second Escape, now with focus
// on the tab button (inside the tablist, which has no Escape handler of its
// own), bubbles up uncaught to WorkModePanel's existing handler, which closes
// the overlay and restores focus to the launch trigger.

export type WorkModeTabDef = {
  id: string;
  label: string;
  content: ReactNode;
};

/** External cross-navigation request (e.g. SidePanel's "Review reproposal"
 * link into the AI-suggestion tab): switch to `tabId` and focus
 * `focusSelector` (if given) once `nonce` becomes non-zero. `nonce: 0` is the
 * caller's "never requested yet" sentinel and is always a no-op -- callers
 * are expected to hold a counter starting at 0 and increment it per request
 * (never reset it back to 0). The switch and the deferred focus are handled
 * by the SAME effect below -- splitting them across this component's
 * tab-switch and the caller's own focus effect would race two
 * independently-scheduled updates with no ordering guarantee between them. */
export type WorkModeTabActivateRequest = {
  tabId: string;
  nonce: number;
  focusSelector?: string;
};

type WorkModeTabsProps = {
  tabs: WorkModeTabDef[];
  activateRequest?: WorkModeTabActivateRequest | null;
};

export function WorkModeTabs({ tabs, activateRequest }: WorkModeTabsProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [rovingIndex, setRovingIndex] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const tabsRef = useRef(tabs);
  tabsRef.current = tabs;

  useEffect(() => {
    tabRefs.current[rovingIndex]?.scrollIntoView({ inline: "nearest", block: "nearest" });
  }, [rovingIndex]);

  // Depend on activateRequest's PRIMITIVE fields, not the object itself (a
  // fresh literal every App render) -- otherwise this would re-fire on every
  // unrelated re-render and repeatedly steal focus back into this tab. Guard
  // on the VALUE `nonce === 0` (caller's "never requested yet" convention),
  // not a ref that remembers the last-handled nonce: React 18 StrictMode
  // double-invokes every effect (run -> cleanup -> run again) on mount, and a
  // ref-based dedup would let the cleanup cancel the first run's scheduled
  // focus call while blocking the second run from scheduling a replacement,
  // so the focus call would silently never fire. A plain value check makes
  // both StrictMode invocations agree and is naturally idempotent.
  const nonce = activateRequest?.nonce;
  const tabId = activateRequest?.tabId;
  const focusSelector = activateRequest?.focusSelector;

  useEffect(() => {
    if (tabId === undefined || !nonce) return;
    const index = tabsRef.current.findIndex((tab) => tab.id === tabId);
    if (index === -1) return;
    setActiveIndex(index);
    setRovingIndex(index);

    if (!focusSelector) return;
    // A macrotask (setTimeout), not requestAnimationFrame: this switch races
    // WorkModePanel's own open-time initial-focus effect, and empirically an
    // rAF callback can still run before that effect's (StrictMode-doubled)
    // second invocation finishes claiming focus within the same frame,
    // letting it win and undo this call. setTimeout(0) defers past that
    // whole synchronous effect-flush window instead of racing it.
    const timeoutId = window.setTimeout(() => {
      const target = window.document.querySelector<HTMLElement>(focusSelector);
      target?.focus();
      target?.scrollIntoView({ block: "start" });
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [tabId, nonce, focusSelector]);

  const focusTabAt = (index: number) => {
    setRovingIndex(index);
    tabRefs.current[index]?.focus();
  };

  const handleTablistKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    const count = tabs.length;
    if (count === 0) return;

    if (event.key === "ArrowRight") {
      event.preventDefault();
      focusTabAt((rovingIndex + 1) % count);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      focusTabAt((rovingIndex - 1 + count) % count);
    } else if (event.key === "Home") {
      event.preventDefault();
      focusTabAt(0);
    } else if (event.key === "End") {
      event.preventDefault();
      focusTabAt(count - 1);
    }
  };

  const handleTabPanelKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== "Escape") return;
    event.preventDefault();
    // Must not bubble to WorkModePanel's own Escape handler on the first
    // press -- that would close the whole overlay instead of just backing
    // out of the panel content to the tab strip.
    event.stopPropagation();
    setRovingIndex(activeIndex);
    tabRefs.current[activeIndex]?.focus();
  };

  return (
    <div style={{ display: "grid", gap: 0, minHeight: 0 }}>
      <div
        role="tablist"
        aria-label={t("work_mode.tabs.label")}
        aria-orientation="horizontal"
        onKeyDown={handleTablistKeyDown}
        style={{
          display: "flex",
          gap: 4,
          overflowX: "auto",
          borderBottom: "1px solid #e2e8f0",
        }}
      >
        {tabs.map((tab, index) => {
          const isActive = index === activeIndex;
          return (
            <button
              key={tab.id}
              ref={(node) => {
                tabRefs.current[index] = node;
              }}
              type="button"
              role="tab"
              id={`work-mode-tab-${tab.id}`}
              aria-selected={isActive}
              aria-controls={`work-mode-panel-${tab.id}`}
              tabIndex={index === rovingIndex ? 0 : -1}
              data-work-mode-initial-focus={isActive ? "true" : undefined}
              onClick={() => {
                setActiveIndex(index);
                setRovingIndex(index);
              }}
              style={{
                border: "none",
                borderBottom: isActive ? "2px solid #2563eb" : "2px solid transparent",
                backgroundColor: "transparent",
                color: isActive ? "#0f172a" : "#475569",
                fontWeight: isActive ? 700 : 600,
                fontSize: 13,
                padding: "8px 12px",
                cursor: "pointer",
                whiteSpace: "nowrap",
                flexShrink: 0,
              }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
      {tabs.map((tab, index) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`work-mode-panel-${tab.id}`}
          aria-labelledby={`work-mode-tab-${tab.id}`}
          tabIndex={0}
          hidden={index !== activeIndex}
          onKeyDown={handleTabPanelKeyDown}
          style={{ paddingTop: 12 }}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
