import { SafeModePolicy } from "../domain/policy/safe_mode";
import type { DiffResult } from "../domain/diff/doc_diff";
import type { DocumentV2 } from "../domain/types";

type DiffPanelProps = {
  comparisonFileName: string | null;
  comparisonDocument: DocumentV2 | null;
  diffResult: DiffResult | null;
  currentCardIdSet: Set<string>;
  currentIslandIdSet: Set<string>;
  onLoadComparisonDocument: () => void;
  onJumpToItem: (kind: "card" | "island", id: string) => void;
  safeMode: boolean;
};

function formatPreview(value: string | undefined, safeMode: boolean): string {
  if (safeMode && !SafeModePolicy.canExposeText("card.text", "diff", true)) {
    return SafeModePolicy.redactText(value ?? "", true);
  }
  const text = value ?? "";
  if (text.length <= 120) {
    return text;
  }

  return `${text.slice(0, 120)}…`;
}

function renderItemReference(
  kind: "card" | "island",
  id: string,
  canJump: boolean,
  onJumpToItem: DiffPanelProps["onJumpToItem"]
) {
  if (!canJump) {
    return <span>{id}</span>;
  }

  return (
    <button
      type="button"
      onClick={() => {
        onJumpToItem(kind, id);
      }}
      style={{
        fontSize: 12,
        border: "1px solid #cbd5e1",
        borderRadius: 6,
        background: "#ffffff",
        cursor: "pointer",
        padding: "2px 6px",
      }}
    >
      {id}
    </button>
  );
}

export function DiffPanel({
  comparisonFileName,
  comparisonDocument,
  diffResult,
  currentCardIdSet,
  currentIslandIdSet,
  onLoadComparisonDocument,
  onJumpToItem,
  safeMode,
}: DiffPanelProps) {
  const hasComparisonDocument = Boolean(comparisonDocument);

  return (
    <section
      style={{
        border: "1px solid #e2e8f0",
        borderRadius: 8,
        padding: 12,
        marginBottom: 12,
        backgroundColor: "#ffffff",
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: 8 }}>Diff</div>
      <button type="button" onClick={onLoadComparisonDocument} style={{ marginBottom: 8 }}>
        Load comparison document (JSON)
      </button>
      {comparisonFileName ? <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>File: {comparisonFileName}</div> : null}
      {hasComparisonDocument ? (
        <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
          Compare target stats: {comparisonDocument?.cards.length ?? 0} cards / {comparisonDocument?.islands.length ?? 0} islands /{" "}
          {(comparisonDocument?.relationSummaries ?? []).length} relation summaries
        </div>
      ) : (
        <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>
          Load a second document (or snapshot JSON containing a document) to compare against the current doc.
        </div>
      )}
      {diffResult ? (
        <>
          <div style={{ fontSize: 12, color: "#0f172a", marginBottom: 8 }}>
            Cards: +{diffResult.cards.added.length} / -{diffResult.cards.removed.length} / Δtext {diffResult.cards.changedText.length}
            <br />
            Islands: +{diffResult.islands.added.length} / -{diffResult.islands.removed.length} / Δmembers{" "}
            {diffResult.islands.membershipChanged.length} / Δsummary {diffResult.islands.summaryChanged.length}
            <br />
            Relation summaries: +{diffResult.relationSummaries.added.length} / -{diffResult.relationSummaries.removed.length} / Δtext{" "}
            {diffResult.relationSummaries.changedText.length} / Δreviewed {diffResult.relationSummaries.changedReviewed.length} / Δwarnings{" "}
            {diffResult.relationSummaries.warningsChanged.length}
            <br />
            Reading order changed: {diffResult.readingOrder.changed ? "yes" : "no"}
          </div>

          <details>
            <summary>Cards</summary>
            <ul style={{ fontSize: 12, color: "#334155" }}>
              {diffResult.cards.added.map((id) => (
                <li key={`cards-added-${id}`}>added: {renderItemReference("card", id, currentCardIdSet.has(id), onJumpToItem)}</li>
              ))}
              {diffResult.cards.removed.map((id) => (
                <li key={`cards-removed-${id}`}>removed: {id}</li>
              ))}
              {diffResult.cards.changedText.map((entry) => (
                <li key={`cards-changed-${entry.id}`}>
                  text changed: {renderItemReference("card", entry.id, currentCardIdSet.has(entry.id), onJumpToItem)}
                  <details>
                    <summary>
                      <span style={{ color: "#475569" }}>A:</span> {formatPreview(entry.aText, safeMode)} <span style={{ color: "#475569" }}>B:</span>{" "}
                      {formatPreview(entry.bText, safeMode)}
                    </summary>
                    <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>
                      <div>
                        <strong>A</strong>: {safeMode ? SafeModePolicy.redactText(entry.aText, true) : entry.aText}
                      </div>
                      <div>
                        <strong>B</strong>: {safeMode ? SafeModePolicy.redactText(entry.bText, true) : entry.bText}
                      </div>
                    </div>
                  </details>
                </li>
              ))}
            </ul>
          </details>

          <details>
            <summary>Islands</summary>
            <ul style={{ fontSize: 12, color: "#334155" }}>
              {diffResult.islands.added.map((id) => (
                <li key={`islands-added-${id}`}>added: {renderItemReference("island", id, currentIslandIdSet.has(id), onJumpToItem)}</li>
              ))}
              {diffResult.islands.removed.map((id) => (
                <li key={`islands-removed-${id}`}>removed: {id}</li>
              ))}
              {diffResult.islands.membershipChanged.map((entry) => (
                <li key={`islands-members-${entry.id}`}>
                  membership changed: {renderItemReference("island", entry.id, currentIslandIdSet.has(entry.id), onJumpToItem)}
                  <ul style={{ margin: "4px 0 0", paddingLeft: 16 }}>
                    <li>
                      + {entry.addedCardIds.length === 0
                        ? "none"
                        : entry.addedCardIds.map((cardId) => (
                            <span key={`island-membership-added-${entry.id}-${cardId}`} style={{ marginRight: 6 }}>
                              {renderItemReference("card", cardId, currentCardIdSet.has(cardId), onJumpToItem)}
                            </span>
                          ))}
                    </li>
                    <li>
                      - {entry.removedCardIds.length === 0
                        ? "none"
                        : entry.removedCardIds.map((cardId) => (
                            <span key={`island-membership-removed-${entry.id}-${cardId}`} style={{ marginRight: 6 }}>
                              {renderItemReference("card", cardId, currentCardIdSet.has(cardId), onJumpToItem)}
                            </span>
                          ))}
                    </li>
                  </ul>
                </li>
              ))}
              {diffResult.islands.summaryChanged.map((entry) => (
                <li key={`islands-summary-${entry.id}`}>
                  summary changed: {renderItemReference("island", entry.id, currentIslandIdSet.has(entry.id), onJumpToItem)}
                  <details>
                    <summary>
                      A[{String(entry.aReviewed)}]: {formatPreview(entry.aSummary, safeMode)} / B[{String(entry.bReviewed)}]: {formatPreview(entry.bSummary, safeMode)}
                    </summary>
                    <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>
                      <div>
                        <strong>A</strong> [{String(entry.aReviewed)}]: {safeMode ? SafeModePolicy.redactText(entry.aSummary ?? "", true) : entry.aSummary ?? ""}
                      </div>
                      <div>
                        <strong>B</strong> [{String(entry.bReviewed)}]: {safeMode ? SafeModePolicy.redactText(entry.bSummary ?? "", true) : entry.bSummary ?? ""}
                      </div>
                    </div>
                  </details>
                </li>
              ))}
            </ul>
          </details>

          <details>
            <summary>Relation summaries</summary>
            <ul style={{ fontSize: 12, color: "#334155" }}>
              {diffResult.relationSummaries.added.map((id) => (
                <li key={`relations-added-${id}`}>added: {id}</li>
              ))}
              {diffResult.relationSummaries.removed.map((id) => (
                <li key={`relations-removed-${id}`}>removed: {id}</li>
              ))}
              {diffResult.relationSummaries.changedText.map((entry) => (
                <li key={`relations-text-${entry.id}`}>
                  text changed: {entry.id}
                  <details>
                    <summary>
                      <span style={{ color: "#475569" }}>A:</span> {formatPreview(entry.aText, safeMode)} <span style={{ color: "#475569" }}>B:</span>{" "}
                      {formatPreview(entry.bText, safeMode)}
                    </summary>
                    <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>
                      <div>
                        <strong>A</strong>: {safeMode ? SafeModePolicy.redactText(entry.aText, true) : entry.aText}
                      </div>
                      <div>
                        <strong>B</strong>: {safeMode ? SafeModePolicy.redactText(entry.bText, true) : entry.bText}
                      </div>
                    </div>
                  </details>
                </li>
              ))}
              {diffResult.relationSummaries.changedReviewed.map((entry) => (
                <li key={`relations-reviewed-${entry.id}`}>
                  reviewed changed: {entry.id} ({String(entry.aReviewed)} → {String(entry.bReviewed)})
                </li>
              ))}
              {diffResult.relationSummaries.warningsChanged.map((entry) => (
                <li key={`relations-warnings-${entry.id}`}>
                  warnings changed: {entry.id} ({entry.aWarnings.join(" | ") || "none"} → {entry.bWarnings.join(" | ") || "none"})
                </li>
              ))}
            </ul>
          </details>

          <details>
            <summary>Reading order</summary>
            <div style={{ fontSize: 12, color: "#334155" }}>
              First differing index: {diffResult.readingOrder.firstDifferingIndex}
              <details>
                <summary>Show full order arrays</summary>
                <div>A: {diffResult.readingOrder.aOrder.join(" → ") || "(empty)"}</div>
                <div>B: {diffResult.readingOrder.bOrder.join(" → ") || "(empty)"}</div>
              </details>
            </div>
          </details>
        </>
      ) : null}
    </section>
  );
}
