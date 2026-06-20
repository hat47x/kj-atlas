import { SafeModePolicy } from "../domain/policy/safe_mode";
import type { DiffResult } from "../domain/diff/doc_diff";
import type { DocumentV2 } from "../domain/types";
import { t } from "../i18n/translate";

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
  const reviewStateLabel = (reviewed: boolean | undefined) =>
    reviewed === undefined
      ? t("diff.panel.review_state_unknown")
      : t(reviewed ? "diff.panel.reviewed" : "diff.panel.unreviewed");

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
      <div style={{ fontWeight: 700, marginBottom: 8 }}>{t("diff.panel.title")}</div>
      <button type="button" onClick={onLoadComparisonDocument} style={{ marginBottom: 8 }}>
        {t("diff.panel.load_document")}
      </button>
      {comparisonFileName ? <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>{t("diff.panel.file", { fileName: comparisonFileName })}</div> : null}
      {hasComparisonDocument ? (
        <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
          {t("diff.panel.compare_stats", {
            cardCount: comparisonDocument?.cards.length ?? 0,
            islandCount: comparisonDocument?.islands.length ?? 0,
            relationSummaryCount: (comparisonDocument?.relationSummaries ?? []).length,
          })}
        </div>
      ) : (
        <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>
          {t("diff.panel.load_hint")}
        </div>
      )}
      {diffResult ? (
        <>
          <div style={{ fontSize: 12, color: "#0f172a", marginBottom: 8 }}>
            {t("diff.panel.summary.cards", { added: diffResult.cards.added.length, removed: diffResult.cards.removed.length, changedText: diffResult.cards.changedText.length })}
            <br />
            {t("diff.panel.summary.islands", { added: diffResult.islands.added.length, removed: diffResult.islands.removed.length, changedMembers: diffResult.islands.membershipChanged.length, changedSummary: diffResult.islands.summaryChanged.length })}
            <br />
            {t("diff.panel.summary.relations", { added: diffResult.relationSummaries.added.length, removed: diffResult.relationSummaries.removed.length, changedText: diffResult.relationSummaries.changedText.length, changedReviewed: diffResult.relationSummaries.changedReviewed.length, changedWarnings: diffResult.relationSummaries.warningsChanged.length })}
            <br />
            {t("diff.panel.summary.reading_order", { changed: diffResult.readingOrder.changed ? t("diff.panel.yes") : t("diff.panel.no") })}
          </div>

          <details>
            <summary>{t("diff.panel.section.cards")}</summary>
            <ul style={{ fontSize: 12, color: "#334155" }}>
              {diffResult.cards.added.map((id) => (
                <li key={`cards-added-${id}`}>{t("diff.panel.item.added")} {renderItemReference("card", id, currentCardIdSet.has(id), onJumpToItem)}</li>
              ))}
              {diffResult.cards.removed.map((id) => (
                <li key={`cards-removed-${id}`}>{t("diff.panel.item.removed")} {id}</li>
              ))}
              {diffResult.cards.changedText.map((entry) => (
                <li key={`cards-changed-${entry.id}`}>
                  {t("diff.panel.item.text_changed")} {renderItemReference("card", entry.id, currentCardIdSet.has(entry.id), onJumpToItem)}
                  <details>
                    <summary>
                      <span style={{ color: "#475569" }}>{t("diff.panel.label.a")}</span> {formatPreview(entry.aText, safeMode)} <span style={{ color: "#475569" }}>{t("diff.panel.label.b")}</span>{" "}
                      {formatPreview(entry.bText, safeMode)}
                    </summary>
                    <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>
                      <div>
                        <strong>{t("diff.panel.label.a_strong")}</strong>: {safeMode ? SafeModePolicy.redactText(entry.aText, true) : entry.aText}
                      </div>
                      <div>
                        <strong>{t("diff.panel.label.b_strong")}</strong>: {safeMode ? SafeModePolicy.redactText(entry.bText, true) : entry.bText}
                      </div>
                    </div>
                  </details>
                </li>
              ))}
            </ul>
          </details>

          <details>
            <summary>{t("diff.panel.section.islands")}</summary>
            <ul style={{ fontSize: 12, color: "#334155" }}>
              {diffResult.islands.added.map((id) => (
                <li key={`islands-added-${id}`}>{t("diff.panel.item.added")} {renderItemReference("island", id, currentIslandIdSet.has(id), onJumpToItem)}</li>
              ))}
              {diffResult.islands.removed.map((id) => (
                <li key={`islands-removed-${id}`}>{t("diff.panel.item.removed")} {id}</li>
              ))}
              {diffResult.islands.membershipChanged.map((entry) => (
                <li key={`islands-members-${entry.id}`}>
                  {t("diff.panel.item.membership_changed")} {renderItemReference("island", entry.id, currentIslandIdSet.has(entry.id), onJumpToItem)}
                  <ul style={{ margin: "4px 0 0", paddingLeft: 16 }}>
                    <li>
                      + {entry.addedCardIds.length === 0
                        ? t("diff.panel.none")
                        : entry.addedCardIds.map((cardId) => (
                            <span key={`island-membership-added-${entry.id}-${cardId}`} style={{ marginRight: 6 }}>
                              {renderItemReference("card", cardId, currentCardIdSet.has(cardId), onJumpToItem)}
                            </span>
                          ))}
                    </li>
                    <li>
                      - {entry.removedCardIds.length === 0
                        ? t("diff.panel.none")
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
                  {t("diff.panel.item.summary_changed")} {renderItemReference("island", entry.id, currentIslandIdSet.has(entry.id), onJumpToItem)}
                  <details>
                    <summary>
                      {t("diff.panel.label.a_strong")}[{reviewStateLabel(entry.aReviewed)}]: {formatPreview(entry.aSummary, safeMode)} / {t("diff.panel.label.b_strong")}[{reviewStateLabel(entry.bReviewed)}]: {formatPreview(entry.bSummary, safeMode)}
                    </summary>
                    <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>
                      <div>
                        <strong>{t("diff.panel.label.a_strong")}</strong> [{reviewStateLabel(entry.aReviewed)}]: {safeMode ? SafeModePolicy.redactText(entry.aSummary ?? "", true) : entry.aSummary ?? ""}
                      </div>
                      <div>
                        <strong>{t("diff.panel.label.b_strong")}</strong> [{reviewStateLabel(entry.bReviewed)}]: {safeMode ? SafeModePolicy.redactText(entry.bSummary ?? "", true) : entry.bSummary ?? ""}
                      </div>
                    </div>
                  </details>
                </li>
              ))}
            </ul>
          </details>

          <details>
            <summary>{t("diff.panel.section.relation_summaries")}</summary>
            <ul style={{ fontSize: 12, color: "#334155" }}>
              {diffResult.relationSummaries.added.map((id) => (
                <li key={`relations-added-${id}`}>{t("diff.panel.item.added")} {id}</li>
              ))}
              {diffResult.relationSummaries.removed.map((id) => (
                <li key={`relations-removed-${id}`}>{t("diff.panel.item.removed")} {id}</li>
              ))}
              {diffResult.relationSummaries.changedText.map((entry) => (
                <li key={`relations-text-${entry.id}`}>
                  {t("diff.panel.item.text_changed")} {entry.id}
                  <details>
                    <summary>
                      <span style={{ color: "#475569" }}>{t("diff.panel.label.a")}</span> {formatPreview(entry.aText, safeMode)} <span style={{ color: "#475569" }}>{t("diff.panel.label.b")}</span>{" "}
                      {formatPreview(entry.bText, safeMode)}
                    </summary>
                    <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>
                      <div>
                        <strong>{t("diff.panel.label.a_strong")}</strong>: {safeMode ? SafeModePolicy.redactText(entry.aText, true) : entry.aText}
                      </div>
                      <div>
                        <strong>{t("diff.panel.label.b_strong")}</strong>: {safeMode ? SafeModePolicy.redactText(entry.bText, true) : entry.bText}
                      </div>
                    </div>
                  </details>
                </li>
              ))}
              {diffResult.relationSummaries.changedReviewed.map((entry) => (
                <li key={`relations-reviewed-${entry.id}`}>
                  {t("diff.panel.item.reviewed_changed")} {entry.id} ({reviewStateLabel(entry.aReviewed)} → {reviewStateLabel(entry.bReviewed)})
                </li>
              ))}
              {diffResult.relationSummaries.warningsChanged.map((entry) => (
                <li key={`relations-warnings-${entry.id}`}>
                  {t("diff.panel.item.warnings_changed")} {entry.id} ({entry.aWarnings.join(" | ") || t("diff.panel.none")} → {entry.bWarnings.join(" | ") || t("diff.panel.none")})
                </li>
              ))}
            </ul>
          </details>

          <details>
            <summary>{t("diff.panel.section.reading_order")}</summary>
            <div style={{ fontSize: 12, color: "#334155" }}>
              {t("diff.panel.first_differing_index", { index: diffResult.readingOrder.firstDifferingIndex })}
              <details>
                <summary>{t("diff.panel.show_full_order_arrays")}</summary>
                <div>{t("diff.panel.label.a")} {diffResult.readingOrder.aOrder.join(" → ") || t("diff.panel.empty")}</div>
                <div>{t("diff.panel.label.b")} {diffResult.readingOrder.bOrder.join(" → ") || t("diff.panel.empty")}</div>
              </details>
            </div>
          </details>
        </>
      ) : null}
    </section>
  );
}
