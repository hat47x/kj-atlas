import { useMemo } from "react";
import type { Card } from "../domain/types";
import { t } from "../i18n/translate";

type DomainStateSummaryProps = {
  cards: Card[];
  islandCount?: number;
  relationCount?: number;
};

type StateCounts = {
  total: number;
  byClaimType: Record<string, number>;
  unreviewed: number;
  withCritique: number;
  withCritiqueTags: number;
  withReview: number;
};

export function DomainStateSummary({ cards, islandCount = 0, relationCount = 0 }: DomainStateSummaryProps) {
  const counts: StateCounts = useMemo(() => {
    const byClaimType: Record<string, number> = { fact: 0, claim: 0, hypothesis: 0, unknown: 0 };
    let unreviewed = 0;
    let withCritique = 0;
    let withCritiqueTags = 0;
    let withReview = 0;

    for (const card of cards) {
      const ct = card.claimType ?? "unknown";
      byClaimType[ct] = (byClaimType[ct] ?? 0) + 1;

      if (card.textReviewed !== true) {
        unreviewed += 1;
      } else {
        withReview += 1;
      }
      if (typeof card.critique === "string" && card.critique.trim().length > 0) {
        withCritique += 1;
      }
      if ((card.critiqueTags?.length ?? 0) > 0) {
        withCritiqueTags += 1;
      }
    }

    return {
      total: cards.length,
      byClaimType,
      unreviewed,
      withCritique,
      withCritiqueTags,
      withReview,
    };
  }, [cards]);

  if (counts.total === 0) {
    return null;
  }

  const CLAIM_TYPE_LABELS: Record<string, string> = {
    fact: t("domain_state.fact"),
    claim: t("domain_state.claim"),
    hypothesis: t("domain_state.hypothesis"),
    unknown: t("domain_state.unknown"),
  };

  const itemStyle = {
    display: "flex",
    alignItems: "center",
    gap: 4,
    fontSize: 11,
    color: "#475569",
    whiteSpace: "nowrap",
  } as const;

  // First meaningful map criteria (PRODUCT-VALUE-01):
  // 3+ cards, 1+ island or 1+ relation or 1+ critique
  const hasEnoughCards = counts.total >= 3;
  const hasStructure = islandCount > 0 || relationCount > 0 || counts.withCritique > 0;
  const firstMapComplete = hasEnoughCards && hasStructure;

  return (
    <section
      aria-label={t("domain_state.title")}
      style={{
        display: "grid",
        gap: 6,
        padding: "8px 0",
        borderBottom: "1px solid #e2e8f0",
        marginBottom: 8,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>
          {t("domain_state.title")} ({counts.total})
        </div>
        {!firstMapComplete ? (
          <div style={{ fontSize: 10, color: "#64748b", fontStyle: "italic" }}>
            {!hasEnoughCards
              ? t("domain_state.map_progress_cards", { current: counts.total, target: 3 })
              : t("domain_state.map_progress_structure")}
          </div>
        ) : null}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {(["fact", "claim", "hypothesis"] as const).map((ct) =>
          counts.byClaimType[ct] > 0 ? (
            <span key={ct} style={itemStyle}>
              <span
                style={{
                  display: "inline-block",
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  backgroundColor:
                    ct === "fact" ? "#16a34a" : ct === "claim" ? "#2563eb" : "#9333ea",
                }}
              />
              {CLAIM_TYPE_LABELS[ct]}: {counts.byClaimType[ct]}
            </span>
          ) : null,
        )}
        {counts.unreviewed > 0 ? (
          <span style={itemStyle}>
            <span
              style={{
                display: "inline-block",
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: "#f59e0b",
              }}
            />
            {t("domain_state.unreviewed")}: {counts.unreviewed}
          </span>
        ) : null}
        {counts.withCritique > 0 ? (
          <span style={itemStyle}>
            <span
              style={{
                display: "inline-block",
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: "#f97316",
              }}
            />
            {t("domain_state.critique")}: {counts.withCritique}
          </span>
        ) : null}
      </div>
    </section>
  );
}
