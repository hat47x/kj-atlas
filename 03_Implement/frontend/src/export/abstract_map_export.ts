import { buildIslandRelationExplanation } from "../domain/island_relation_explain";
import { getDerivedIslandEdges } from "../domain/island_edge_aggregate";
import { buildRelationSummarySourceSignature } from "../domain/relation_summary_ops";
import { isCanonicalCard, type DocumentV2, type EdgeType } from "../domain/types";

const GROUNDING_SNIPPET_LIMIT = 160;

export type AbstractMapExportViewState = {
  visibleIslandIds: Set<string>;
  abstractMapView: boolean;
  includeUnreviewedDrafts?: boolean;
};

export type AbstractMapExportIsland = {
  id: string;
  title: string;
  summaryText: string;
  summaryReviewed: boolean;
  shapeKind: string;
  memberCanonicalCardCount: number;
};

export type AbstractMapExportGroundingCard = {
  id: string;
  snippet: string;
};

export type AbstractMapExportRelation = {
  islandAId: string;
  islandBId: string;
  type: EdgeType;
  derived: boolean;
  summaryText?: string;
  summaryReviewed?: boolean;
  draftTemplateText?: string;
  warnings?: string[];
  groundingCardIds?: string[];
  groundingEdgeIds?: string[];
  groundingCards?: AbstractMapExportGroundingCard[];
};

export type AbstractMapExportRepresentative = {
  representativeCardId: string;
  representativeText: string;
  originalCardIds: string[];
};

export type AbstractMapExportModel = {
  generatedAt: string;
  islands: AbstractMapExportIsland[];
  relations: AbstractMapExportRelation[];
  representatives: AbstractMapExportRepresentative[];
};

type AbstractMapExportMarkdownOptions = {
  snapshotFilename?: string;
};

type AbstractMapExportHtmlOptions = {
  snapshotDataUrl?: string;
};

function normalizeTextSnippet(text: string): string {
  const normalized = text.replace(/\s+/g, " ").trim();
  if (normalized.length <= GROUNDING_SNIPPET_LIMIT) {
    return normalized;
  }

  return `${normalized.slice(0, GROUNDING_SNIPPET_LIMIT - 3)}...`;
}

function normalizePair(a: string, b: string): [string, string] {
  return a <= b ? [a, b] : [b, a];
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function relationTypeLabel(type: EdgeType): string {
  return type === "negate" ? "NEGATE" : "RELATED";
}

function reviewLabel(reviewed?: boolean): string {
  return reviewed ? "reviewed" : "UNREVIEWED";
}

function buildGroundingCards(document: DocumentV2, cardIds: string[]): AbstractMapExportGroundingCard[] {
  const cardsById = new Map(document.cards.map((card) => [card.id, card]));
  return cardIds
    .map((cardId) => cardsById.get(cardId))
    .filter((card): card is NonNullable<typeof card> => Boolean(card))
    .map((card) => ({ id: card.id, snippet: normalizeTextSnippet(card.text) }));
}

function buildDraftTemplate(document: DocumentV2, relation: Pick<AbstractMapExportRelation, "islandAId" | "islandBId" | "type" | "derived" | "groundingCardIds" | "groundingEdgeIds">): string {
  const explanation = buildIslandRelationExplanation(document, {
    edgeId: relation.derived
      ? `derived:${relation.islandAId}:${relation.islandBId}:${relation.type}`
      : `persisted:${relation.islandAId}:${relation.islandBId}:${relation.type}`,
    fromIslandId: relation.islandAId,
    toIslandId: relation.islandBId,
    type: relation.type,
    isDerived: relation.derived,
    contributingEdgeIds: relation.groundingEdgeIds,
    contributingCardIds: relation.groundingCardIds,
  });

  return explanation.body;
}

function buildRelationRowBase(
  document: DocumentV2,
  relation: Omit<AbstractMapExportRelation, "draftTemplateText" | "groundingCards">
): AbstractMapExportRelation {
  const summaryText = relation.summaryText?.trim();
  const hasSummary = Boolean(summaryText && summaryText.length > 0);
  const draftTemplateText = hasSummary
    ? undefined
    : buildDraftTemplate(document, {
        islandAId: relation.islandAId,
        islandBId: relation.islandBId,
        type: relation.type,
        derived: relation.derived,
        groundingCardIds: relation.groundingCardIds,
        groundingEdgeIds: relation.groundingEdgeIds,
      });

  return {
    ...relation,
    summaryText: hasSummary ? summaryText : undefined,
    draftTemplateText,
    groundingCards: buildGroundingCards(document, relation.groundingCardIds ?? []),
  };
}

export function buildAbstractMapExport(doc: DocumentV2, viewState: AbstractMapExportViewState): AbstractMapExportModel {
  const visibleIslandIds = viewState.visibleIslandIds;
  const includeUnreviewedDrafts = viewState.includeUnreviewedDrafts ?? false;
  const visibleIslands = doc.islands
    .filter((island) => visibleIslandIds.has(island.id))
    .sort((a, b) => a.id.localeCompare(b.id));
  const cardsById = new Map(doc.cards.map((card) => [card.id, card]));

  const islands = visibleIslands.map((island) => {
    const memberCanonicalCardCount = island.cardIds.reduce((count, cardId) => {
      const card = cardsById.get(cardId);
      if (!card) {
        return count;
      }

      return isCanonicalCard(card) ? count + 1 : count;
    }, 0);

    const normalizedSummaryText = island.summaryText?.trim() ?? "";
    const isSummaryReviewed = island.summaryReviewed === true;
    const shouldIncludeSummary = normalizedSummaryText.length > 0 && (isSummaryReviewed || includeUnreviewedDrafts);

    return {
      id: island.id,
      title: island.title?.trim() || island.id,
      summaryText: shouldIncludeSummary ? normalizedSummaryText : normalizedSummaryText.length > 0 ? "UNREVIEWED hidden" : "(No summary)",
      summaryReviewed: isSummaryReviewed,
      shapeKind: island.shape?.kind ?? "rect",
      memberCanonicalCardCount,
    };
  });

  const relationRows: AbstractMapExportRelation[] = [];
  const relationSummariesBySignature = new Map((doc.relationSummaries ?? []).map((summary) => [summary.sourceSignature, summary]));

  for (const edge of doc.edges) {
    if (edge.fromKind !== "island" || edge.toKind !== "island") {
      continue;
    }

    if (!visibleIslandIds.has(edge.fromId) || !visibleIslandIds.has(edge.toId) || edge.fromId === edge.toId) {
      continue;
    }

    const [islandAId, islandBId] = normalizePair(edge.fromId, edge.toId);
    const summary = relationSummariesBySignature.get(`edge:${edge.id}`);

    relationRows.push(
      buildRelationRowBase(doc, {
        islandAId,
        islandBId,
        type: edge.type,
        derived: false,
        summaryText: summary?.reviewed === true || includeUnreviewedDrafts ? summary?.text : undefined,
        summaryReviewed: summary?.reviewed,
        warnings: summary?.warnings,
        groundingCardIds: summary?.groundingCardIds ?? [],
        groundingEdgeIds: summary?.groundingEdgeIds ?? [edge.id],
      })
    );
  }

  if (viewState.abstractMapView) {
    for (const derivedEdge of getDerivedIslandEdges(doc)) {
      // This outline's relation rows are island-pair rows (islandAId/islandBId);
      // island<->lone-wolf-card promotions (UX-SCALE-01 d) have no island on
      // one side and are out of scope for this text export's row format.
      if (derivedEdge.toKind !== "island") {
        continue;
      }
      if (!visibleIslandIds.has(derivedEdge.fromId) || !visibleIslandIds.has(derivedEdge.toId)) {
        continue;
      }

      const sourceSignature = buildRelationSummarySourceSignature({
        edgeId: derivedEdge.id,
        fromIslandId: derivedEdge.fromId,
        toIslandId: derivedEdge.toId,
        type: derivedEdge.type,
        isDerived: true,
        contributingEdgeIds: derivedEdge.contributingEdgeIds,
        contributingCardIds: derivedEdge.contributingCardIds,
      });
      const summary = relationSummariesBySignature.get(sourceSignature);

      relationRows.push(
        buildRelationRowBase(doc, {
          islandAId: derivedEdge.fromId,
          islandBId: derivedEdge.toId,
          type: derivedEdge.type,
          derived: true,
          summaryText: summary?.reviewed === true || includeUnreviewedDrafts ? summary?.text : undefined,
          summaryReviewed: summary?.reviewed,
          warnings: summary?.warnings,
          groundingCardIds: summary?.groundingCardIds ?? derivedEdge.contributingCardIds,
          groundingEdgeIds: summary?.groundingEdgeIds ?? derivedEdge.contributingEdgeIds,
        })
      );
    }
  }

  const relations = relationRows.sort((a, b) => {
    const pairCompare = `${a.islandAId}|${a.islandBId}`.localeCompare(`${b.islandAId}|${b.islandBId}`);
    if (pairCompare !== 0) {
      return pairCompare;
    }

    const typeCompare = a.type.localeCompare(b.type);
    if (typeCompare !== 0) {
      return typeCompare;
    }

    if (a.derived === b.derived) {
      return 0;
    }

    return a.derived ? 1 : -1;
  });

  const representatives = doc.cards
    .filter((card) => Array.isArray(card.repOf) && card.repOf.length > 0)
    .map((card) => ({
      representativeCardId: card.id,
      representativeText: normalizeTextSnippet(card.text),
      originalCardIds: card.repOf ?? [],
    }))
    .sort((a, b) => a.representativeCardId.localeCompare(b.representativeCardId));

  return {
    generatedAt: doc.updatedAt,
    islands,
    relations,
    representatives,
  };
}

export function exportAbstractMapMarkdown(model: AbstractMapExportModel, options: AbstractMapExportMarkdownOptions = {}): string {
  const lines: string[] = [];
  lines.push("# Abstract Map Export");
  lines.push("");
  if (options.snapshotFilename) {
    lines.push(`![Abstract Map Snapshot](${options.snapshotFilename})`);
    lines.push("");
  }
  lines.push(`GeneratedAt: ${model.generatedAt}`);
  lines.push("");
  lines.push("> Reviewed semantics: `reviewed` means human-reviewed text. `UNREVIEWED` means draft and must be verified.");
  lines.push("> Relation semantics: `derived` entries correspond to dashed/aggregated relations inferred from underlying links.");
  lines.push("");
  lines.push("## Islands");
  lines.push("");

  for (const island of model.islands) {
    lines.push(`### ${island.title} (${island.id})`);
    lines.push(`- Summary status: ${reviewLabel(island.summaryReviewed)}`);
    lines.push(`- Shape: ${island.shapeKind}`);
    lines.push(`- Canonical member cards: ${island.memberCanonicalCardCount}`);
    lines.push(`- Summary: ${island.summaryText}`);
    lines.push("");
  }

  lines.push("## Relations");
  lines.push("");

  const relationGroups = new Map<string, AbstractMapExportRelation[]>();
  for (const relation of model.relations) {
    const key = `${relation.islandAId}|${relation.islandBId}`;
    const bucket = relationGroups.get(key) ?? [];
    bucket.push(relation);
    relationGroups.set(key, bucket);
  }

  for (const [pair, groupedRelations] of relationGroups) {
    const [islandAId, islandBId] = pair.split("|");
    lines.push(`### ${islandAId} ↔ ${islandBId}`);
    lines.push("");

    for (const relation of groupedRelations) {
      lines.push(`- Type: ${relationTypeLabel(relation.type)} (${relation.derived ? "derived" : "persisted"})`);
      if (relation.summaryText) {
        lines.push(`  - Summary (${reviewLabel(relation.summaryReviewed)}): ${relation.summaryText}`);
      } else {
        lines.push("  - Summary (UNREVIEWED draft template):");
        lines.push(`    ${(relation.draftTemplateText ?? "").replace(/\n/g, "\n    ")}`);
      }

      if (relation.warnings && relation.warnings.length > 0) {
        lines.push("  - Warnings:");
        for (const warning of relation.warnings) {
          lines.push(`    - ${warning}`);
        }
      }

      lines.push(`  - Grounding edge IDs: ${(relation.groundingEdgeIds ?? []).join(", ") || "(none)"}`);
      lines.push("  - Grounding cards:");
      if (!relation.groundingCards || relation.groundingCards.length === 0) {
        lines.push("    - (none)");
      } else {
        for (const card of relation.groundingCards) {
          lines.push(`    - ${card.id}: ${card.snippet}`);
        }
      }
    }

    lines.push("");
  }

  lines.push("## Representative cards");
  lines.push("");
  if (model.representatives.length === 0) {
    lines.push("(none)");
    lines.push("");
  } else {
    for (const representative of model.representatives) {
      lines.push(`- ${representative.representativeCardId}: ${representative.representativeText}`);
      lines.push(`  - Rep count: ${representative.originalCardIds.length}`);
      lines.push(`  - Original card IDs: ${representative.originalCardIds.join(", ") || "(none)"}`);
    }
    lines.push("");
  }

  return lines.join("\n");
}

export function exportAbstractMapHTML(model: AbstractMapExportModel, options: AbstractMapExportHtmlOptions = {}): string {
  const relationGroups = new Map<string, AbstractMapExportRelation[]>();
  for (const relation of model.relations) {
    const key = `${relation.islandAId}|${relation.islandBId}`;
    const bucket = relationGroups.get(key) ?? [];
    bucket.push(relation);
    relationGroups.set(key, bucket);
  }

  const islandsHtml = model.islands
    .map(
      (island) => `<section class="block">
        <h3>${escapeHtml(island.title)} <code>${escapeHtml(island.id)}</code></h3>
        <ul>
          <li>Summary status: <strong>${escapeHtml(reviewLabel(island.summaryReviewed))}</strong></li>
          <li>Shape: ${escapeHtml(island.shapeKind)}</li>
          <li>Canonical member cards: ${island.memberCanonicalCardCount}</li>
        </ul>
        <p>${escapeHtml(island.summaryText)}</p>
      </section>`
    )
    .join("\n");

  const representativesHtml = model.representatives.length === 0
    ? "<p>(none)</p>"
    : `<ul>${model.representatives
        .map(
          (representative) => `<li><code>${escapeHtml(representative.representativeCardId)}</code>: ${escapeHtml(
            representative.representativeText
          )}<ul><li>Rep count: ${representative.originalCardIds.length}</li><li>Original card IDs: ${representative.originalCardIds
            .map((cardId) => `<code>${escapeHtml(cardId)}</code>`)
            .join(", ") || "(none)"}</li></ul></li>`
        )
        .join("")}</ul>`;

  const relationsHtml = Array.from(relationGroups.entries())
    .map(([pair, groupedRelations]) => {
      const [islandAId, islandBId] = pair.split("|");
      const relationRows = groupedRelations
        .map((relation) => {
          const summaryBlock = relation.summaryText
            ? `<div><strong>Summary (${escapeHtml(reviewLabel(relation.summaryReviewed))}):</strong> ${escapeHtml(relation.summaryText)}</div>`
            : `<div><strong>Summary (UNREVIEWED draft template):</strong><pre>${escapeHtml(relation.draftTemplateText ?? "")}</pre></div>`;

          const warningsBlock = relation.warnings && relation.warnings.length > 0
            ? `<div><strong>Warnings:</strong><ul>${relation.warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}</ul></div>`
            : "";

          const groundingItems = relation.groundingCards && relation.groundingCards.length > 0
            ? relation.groundingCards
                .map((card) => `<li><code>${escapeHtml(card.id)}</code>: ${escapeHtml(card.snippet)}</li>`)
                .join("")
            : "<li>(none)</li>";

          const groundingEdgeIds = relation.groundingEdgeIds && relation.groundingEdgeIds.length > 0
            ? relation.groundingEdgeIds.map((edgeId) => `<code>${escapeHtml(edgeId)}</code>`).join(", ")
            : "(none)";

          return `<li>
            <div><strong>Type:</strong> ${escapeHtml(relationTypeLabel(relation.type))} (${relation.derived ? "derived" : "persisted"})</div>
            ${summaryBlock}
            ${warningsBlock}
            <div><strong>Grounding edge IDs:</strong> ${groundingEdgeIds}</div>
            <div><strong>Grounding cards:</strong><ul>${groundingItems}</ul></div>
          </li>`;
        })
        .join("\n");

      return `<section class="block"><h3>${escapeHtml(islandAId)} ↔ ${escapeHtml(islandBId)}</h3><ul>${relationRows}</ul></section>`;
    })
    .join("\n");

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Abstract Map Export</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 20px; color: #0f172a; }
  .banner { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 10px; margin-bottom: 16px; }
  .block { border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-bottom: 10px; }
  code { background: #f8fafc; padding: 1px 4px; border-radius: 4px; }
  pre { white-space: pre-wrap; background: #f8fafc; padding: 8px; border-radius: 6px; }
</style>
</head>
<body>
  <h1>Abstract Map Export</h1>
  ${options.snapshotDataUrl ? `<div class="block"><img src="${escapeHtml(options.snapshotDataUrl)}" alt="Abstract Map Snapshot" style="max-width: 100%; height: auto; display: block;" /></div>` : ""}
  <div>GeneratedAt: ${escapeHtml(model.generatedAt)}</div>
  <div class="banner">
    <div><strong>Reviewed semantics:</strong> <code>reviewed</code> means human-reviewed text. <code>UNREVIEWED</code> means draft and must be verified.</div>
    <div><strong>Relation semantics:</strong> <code>derived</code> entries correspond to dashed/aggregated relations inferred from underlying links.</div>
  </div>
  <h2>Islands</h2>
  ${islandsHtml}
  <h2>Relations</h2>
  ${relationsHtml}
  <h2>Representative cards</h2>
  ${representativesHtml}
</body>
</html>`;
}
