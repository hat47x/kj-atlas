import type { DocumentV1 } from "../domain/types";
import type { MergeItem } from "../diff/merge_items";
import type { MergeItemEvaluation } from "../diff/merge_dependencies";
import { t } from "../i18n/translate";

type ReviewDiffPanelProps = {
  comparisonFileName: string | null;
  comparisonDocument: DocumentV1 | null;
  mergeItems: MergeItem[];
  evaluations: MergeItemEvaluation[];
  selectedItemIds: Set<string>;
  autoIncludePrerequisites: boolean;
  onLoadComparisonDocument: () => void;
  onToggleAutoIncludePrerequisites: (enabled: boolean) => void;
  onItemCheckedChange: (itemId: string, checked: boolean) => void;
  onGroupCheckedChange: (group: string, checked: boolean) => void;
  onApplySelected: () => void;
  onUndoLastMerge: () => void;
  canApply: boolean;
  isComputingDiff: boolean;
  onCancelDiff: () => void;
  computeProgressMessage: string | null;
  computeProgressPercent: number;
  isFallbackMode: boolean;
};

const statusStyleByCode = {
  ok: { color: "#166534", border: "#86efac", labelKey: "review.panel.status.ok" },
  missing_prerequisites: { color: "#92400e", border: "#fcd34d", labelKey: "review.panel.status.missing_prerequisites" },
  conflict: { color: "#991b1b", border: "#fca5a5", labelKey: "review.panel.status.conflict" },
};

function groupOf(kind: MergeItem["kind"]): string {
  return kind.split(".")[0] ?? kind;
}

export function ReviewDiffPanel({ comparisonFileName, comparisonDocument, mergeItems, evaluations, selectedItemIds, autoIncludePrerequisites, onLoadComparisonDocument, onToggleAutoIncludePrerequisites, onItemCheckedChange, onGroupCheckedChange, onApplySelected, onUndoLastMerge, canApply, isComputingDiff, onCancelDiff, computeProgressMessage, computeProgressPercent, isFallbackMode }: ReviewDiffPanelProps) {
  const evaluationById = new Map(evaluations.map((entry) => [entry.item.id, entry]));
  const groups = [...new Set(mergeItems.map((item) => groupOf(item.kind)))];

  return (
    <section style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 12, marginBottom: 12, backgroundColor: "#ffffff" }}>
      <div style={{ fontWeight: 700, marginBottom: 8 }}>{t("review.panel.title")}</div>
      <button type="button" onClick={onLoadComparisonDocument} style={{ marginBottom: 8 }}>
        {t("review.panel.load_document")}
      </button>
      {comparisonFileName ? <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>{t("review.panel.file", { fileName: comparisonFileName })}</div> : null}
      {comparisonDocument ? <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>{t("review.panel.items", { count: mergeItems.length })}{isComputingDiff ? ` · ${t("review.panel.working")}` : ""}{isFallbackMode ? ` · ${t("review.panel.fallback_mode")}` : ""}</div> : null}
      {isFallbackMode ? <span style={{ fontSize: 11, border: "1px solid #f59e0b", color: "#92400e", borderRadius: 999, padding: "1px 6px", marginRight: 8 }}>{t("review.panel.fallback_mode")}</span> : null}
      {isComputingDiff ? <button type="button" onClick={onCancelDiff}>{t("review.panel.cancel")}</button> : null}
      {isComputingDiff && computeProgressMessage ? <div style={{ fontSize: 12 }}>{computeProgressMessage}</div> : null}
      {isComputingDiff ? <div style={{ marginTop: 4, height: 6, borderRadius: 999, background: "#e2e8f0", overflow: "hidden" }}><div style={{ width: `${Math.max(0, Math.min(100, computeProgressPercent))}%`, height: "100%", background: "#2563eb" }} /></div> : null}

      <label style={{ display: "block", fontSize: 12, marginBottom: 8 }}>
        <input type="checkbox" checked={autoIncludePrerequisites} onChange={(event) => onToggleAutoIncludePrerequisites(event.target.checked)} /> {t("review.panel.auto_include_prerequisites")}
      </label>

      {groups.map((group) => {
        const inGroup = mergeItems.filter((item) => groupOf(item.kind) === group);
        return (
          <details key={group} open>
            <summary>
              {group} ({inGroup.length}){" "}
              <button type="button" onClick={() => onGroupCheckedChange(group, true)} style={{ marginLeft: 8 }}>
                {t("review.panel.select_all")}
              </button>
              <button type="button" onClick={() => onGroupCheckedChange(group, false)} style={{ marginLeft: 4 }}>
                {t("review.panel.select_none")}
              </button>
            </summary>
            <ul style={{ listStyle: "none", paddingLeft: 0, marginTop: 6 }}>
              {inGroup.map((item) => {
                const evaluation = evaluationById.get(item.id);
                const status = statusStyleByCode[evaluation?.status ?? "ok"];
                return (
                  <li key={item.id} style={{ fontSize: 12, marginBottom: 6, border: "1px solid #e2e8f0", borderRadius: 6, padding: 6 }}>
                    <label>
                      <input type="checkbox" checked={selectedItemIds.has(item.id)} onChange={(event) => onItemCheckedChange(item.id, event.target.checked)} /> {item.kind} {item.entityRef.id}
                      {item.field ? `.${item.field}` : ""}
                    </label>
                    <span style={{ marginLeft: 8, border: `1px solid ${status.border}`, color: status.color, borderRadius: 999, padding: "1px 6px" }}>{t(status.labelKey)}</span>
                    {evaluation && evaluation.missingPrerequisites.length > 0 ? (
                      <details style={{ marginTop: 4 }}>
                        <summary>{t("review.panel.explain_blocked")}</summary>
                        <div>{t("review.panel.missing", { value: evaluation.missingPrerequisites.map((entry) => `${entry.kind}:${entry.id}`).join(", ") })}</div>
                      </details>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </details>
        );
      })}

      <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 8 }}>
        <button type="button" onClick={onApplySelected} disabled={!canApply}>{t("review.panel.apply_selected")}</button>
        <button type="button" onClick={onUndoLastMerge}>{t("review.panel.revert_last")}</button>
      </div>
    </section>
  );
}
