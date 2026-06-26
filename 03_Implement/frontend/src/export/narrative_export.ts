import type { GroundingEntry } from "../domain/grounding";
import type { EvidenceLink } from "../domain/types";

export type NarrativeExportItem = {
  id: string;
  title?: string;
  text: string;
  createdAt?: string;
  reviewed: boolean;
  basedOnReadingOrder?: string[];
};

export type ReadingOrderSnippetMap = Record<string, string | undefined>;

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatCreatedAt(createdAt?: string): string {
  if (!createdAt || createdAt.trim().length === 0) {
    return "N/A";
  }

  return createdAt;
}

function buildReadingOrderMarkdown(ids: string[] = [], snippets: ReadingOrderSnippetMap): string {
  if (ids.length === 0) {
    return "_No based-on reading order entries._";
  }

  return ids
    .map((id, index) => {
      const snippet = snippets[id];
      return snippet && snippet.trim().length > 0
        ? `${index + 1}. ${id}: ${snippet.trim()}`
        : `${index + 1}. ${id}`;
    })
    .join("\n");
}

function buildReadingOrderHtml(ids: string[] = [], snippets: ReadingOrderSnippetMap): string {
  if (ids.length === 0) {
    return "<p><em>No based-on reading order entries.</em></p>";
  }

  const items = ids
    .map((id) => {
      const snippet = snippets[id];
      if (snippet && snippet.trim().length > 0) {
        return `<li><code>${escapeHtml(id)}</code>: ${escapeHtml(snippet.trim())}</li>`;
      }

      return `<li><code>${escapeHtml(id)}</code></li>`;
    })
    .join("\n");

  return `<ol>\n${items}\n</ol>`;
}

function buildEvidenceLinksMarkdown(links: EvidenceLink[], cardIds: Set<string>): string {
  const relevant = links.filter(
    (link) => cardIds.has(link.fromCardId) || cardIds.has(link.toCardId)
  );

  if (relevant.length === 0) {
    return "_No evidence links for the reading order entries._";
  }

  return relevant
    .map((link, index) => {
      const kind = link.type === "supports" ? "supports" : "contradicts";
      const noteSuffix = link.note ? ` — ${link.note}` : "";
      const stateSuffix = link.type === "contradicts" && link.contradictionState
        ? ` [${link.contradictionState}]` : "";
      return `${index + 1}. ${link.fromCardId} ${kind} ${link.toCardId}${stateSuffix}${noteSuffix}`;
    })
    .join("\n");
}

function buildEvidenceLinksHtml(links: EvidenceLink[], cardIds: Set<string>): string {
  const relevant = links.filter(
    (link) => cardIds.has(link.fromCardId) || cardIds.has(link.toCardId)
  );

  if (relevant.length === 0) {
    return "<p><em>No evidence links for the reading order entries.</em></p>";
  }

  const items = relevant
    .map((link) => {
      const kind = link.type === "supports" ? "supports" : "contradicts";
      const kindClass = link.type === "supports" ? "supports" : "contradicts";
      const noteSuffix = link.note ? ` — ${escapeHtml(link.note)}` : "";
      const stateSuffix = link.type === "contradicts" && link.contradictionState
        ? ` <span class="contradiction-state">[${escapeHtml(link.contradictionState)}]</span>` : "";
      return `<li><code>${escapeHtml(link.fromCardId)}</code> <span class="${kindClass}">${kind}</span> <code>${escapeHtml(link.toCardId)}</code>${stateSuffix}${noteSuffix}</li>`;
    })
    .join("\n");

  return `<ul class="evidence-links">\n${items}\n</ul>`;
}

function buildGroundingMarkdown(entries: GroundingEntry[]): string {
  if (entries.length === 0) {
    return "_No grounding entries._";
  }

  return entries
    .map((entry, index) => {
      if (entry.kind === "missing") {
        return `${index + 1}. ${entry.anchor} Missing entry: ${entry.sourceId}`;
      }

      if (entry.kind === "card" && entry.card) {
        const canonicalLabel = entry.card.kind === "canonical" ? "canonical" : `source (canonicalId: ${entry.card.canonicalId})`;
        const claimLabel = entry.card.claimType && entry.card.claimType !== "unknown" ? ` [${entry.card.claimType}]` : "";
        const reviewLabel = entry.card.textReviewed === false ? " (unreviewed)" : entry.card.textReviewed === true ? " (reviewed)" : "";
        return `${index + 1}. ${entry.anchor} Card ${entry.card.id} [${canonicalLabel}]${claimLabel}${reviewLabel} — ${entry.card.text || "(empty)"}`;
      }

      const members = (entry.islandMembers ?? [])
        .map((member) => {
          const canonicalLabel =
            member.kind === "canonical" ? "canonical" : `source (canonicalId: ${member.canonicalId})`;
          const memberClaimLabel = member.claimType && member.claimType !== "unknown" ? ` [${member.claimType}]` : "";
          const memberReviewLabel = member.textReviewed === false ? " (unreviewed)" : member.textReviewed === true ? " (reviewed)" : "";
          return `   - ${member.id} [${canonicalLabel}]${memberClaimLabel}${memberReviewLabel} — ${member.text || "(empty)"}`;
        })
        .join("\n");
      const summary = entry.islandSummaryText
        ? `\n   - Summary${entry.islandSummaryReviewed ? "" : " (unreviewed)"}: ${entry.islandSummaryText}`
        : "";

      return `${index + 1}. ${entry.anchor} Island ${entry.islandTitle}\n${members || "   - (no member cards)"}${summary}`;
    })
    .join("\n");
}

function buildGroundingHtml(entries: GroundingEntry[]): string {
  if (entries.length === 0) {
    return "<p><em>No grounding entries.</em></p>";
  }

  return `<ol>${entries
    .map((entry) => {
      if (entry.kind === "missing") {
        return `<li><strong>${escapeHtml(entry.anchor)}</strong> Missing entry: <code>${escapeHtml(entry.sourceId)}</code></li>`;
      }

      if (entry.kind === "card" && entry.card) {
        const canonicalLabel =
          entry.card.kind === "canonical"
            ? "canonical"
            : `source (canonicalId: ${escapeHtml(entry.card.canonicalId ?? "")})`;
        const claimLabel = entry.card.claimType && entry.card.claimType !== "unknown" ? ` [${escapeHtml(entry.card.claimType)}]` : "";
        const reviewLabel = entry.card.textReviewed === false ? " (unreviewed)" : entry.card.textReviewed === true ? " (reviewed)" : "";
        return `<li><strong>${escapeHtml(entry.anchor)}</strong> Card <code>${escapeHtml(entry.card.id)}</code> [${canonicalLabel}]${claimLabel}${reviewLabel} — ${escapeHtml(entry.card.text || "(empty)")}</li>`;
      }

      const members = (entry.islandMembers ?? [])
        .map((member) => {
          const canonicalLabel =
            member.kind === "canonical"
              ? "canonical"
              : `source (canonicalId: ${escapeHtml(member.canonicalId ?? "")})`;
          const memberClaimLabel = member.claimType && member.claimType !== "unknown" ? ` [${escapeHtml(member.claimType)}]` : "";
          const memberReviewLabel = member.textReviewed === false ? " (unreviewed)" : member.textReviewed === true ? " (reviewed)" : "";
          return `<li><code>${escapeHtml(member.id)}</code> [${canonicalLabel}]${memberClaimLabel}${memberReviewLabel} — ${escapeHtml(member.text || "(empty)")}</li>`;
        })
        .join("");
      const summary = entry.islandSummaryText
        ? `<div>Summary${entry.islandSummaryReviewed ? "" : " (unreviewed)"}: ${escapeHtml(entry.islandSummaryText)}</div>`
        : "";

      return `<li><strong>${escapeHtml(entry.anchor)}</strong> Island ${escapeHtml(entry.islandTitle ?? entry.sourceId)}<ul>${members || "<li>(no member cards)</li>"}</ul>${summary}</li>`;
    })
    .join("")}</ol>`;
}

export function buildNarrativeMarkdown(
  item: NarrativeExportItem,
  snippets: ReadingOrderSnippetMap = {},
  groundingEntries: GroundingEntry[] = [],
  evidenceLinks: EvidenceLink[] = []
): string {
  const lines: string[] = [];

  if (item.reviewed) {
    lines.push("Status: Reviewed by human", "");
  } else {
    lines.push("# DRAFT (UNREVIEWED) — Please verify against the diagram.", "");
    lines.push("Status: Unreviewed draft", "");
  }

  if (item.title && item.title.trim().length > 0) {
    lines.push(`# ${item.title.trim()}`, "");
  }

  lines.push(`CreatedAt: ${formatCreatedAt(item.createdAt)}`, "");
  lines.push("## Narrative", "", item.text.trim().length > 0 ? item.text : "", "");
  lines.push("## BasedOnReadingOrder", "", buildReadingOrderMarkdown(item.basedOnReadingOrder ?? [], snippets));
  lines.push("", "## Grounding / Citations", "", buildGroundingMarkdown(groundingEntries));

  const readingOrderCardIds = new Set(item.basedOnReadingOrder ?? []);
  lines.push("", "## Evidence / Contradiction Links", "", buildEvidenceLinksMarkdown(evidenceLinks, readingOrderCardIds));

  return lines.join("\n");
}

export function buildNarrativeHtml(
  item: NarrativeExportItem,
  snippets: ReadingOrderSnippetMap = {},
  groundingEntries: GroundingEntry[] = [],
  evidenceLinks: EvidenceLink[] = []
): string {
  const title = item.title && item.title.trim().length > 0 ? item.title.trim() : "Narrative Export";
  const reviewBlock = item.reviewed
    ? '<div class="reviewed">Reviewed by human</div>'
    : '<div class="draft-banner">DRAFT (UNREVIEWED) — Please verify against the diagram.</div><div class="status">Status: Unreviewed draft</div>';

  const readingOrderCardIds = new Set(item.basedOnReadingOrder ?? []);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml(title)}</title>
  <style>
    body { font-family: sans-serif; margin: 24px; color: #0f172a; line-height: 1.5; }
    h1, h2 { margin-bottom: 8px; }
    .meta { color: #334155; margin-bottom: 16px; }
    .status { color: #7c2d12; font-weight: 600; margin-bottom: 16px; }
    .draft-banner { padding: 10px 12px; background: #fef2f2; border: 1px solid #ef4444; color: #991b1b; font-weight: 700; margin-bottom: 8px; }
    .reviewed { padding: 8px 0; color: #166534; font-weight: 700; margin-bottom: 16px; }
    .narrative { white-space: pre-wrap; }
    code { background: #f1f5f9; padding: 1px 4px; border-radius: 4px; }
    .evidence-links { list-style: none; padding: 0; margin: 0 0 16px; }
    .evidence-links li { padding: 4px 0; font-size: 14px; }
    .supports { color: #166534; font-weight: 600; }
    .contradicts { color: #b91c1c; font-weight: 600; }
  </style>
</head>
<body>
  ${reviewBlock}
  ${item.title && item.title.trim().length > 0 ? `<h1>${escapeHtml(item.title.trim())}</h1>` : ""}
  <div class="meta">CreatedAt: ${escapeHtml(formatCreatedAt(item.createdAt))}</div>
  <h2>Narrative</h2>
  <div class="narrative">${escapeHtml(item.text)}</div>
  <h2>BasedOnReadingOrder</h2>
  ${buildReadingOrderHtml(item.basedOnReadingOrder ?? [], snippets)}
  <h2>Grounding / Citations</h2>
  ${buildGroundingHtml(groundingEntries)}
  <h2>Evidence / Contradiction Links</h2>
  ${buildEvidenceLinksHtml(evidenceLinks, readingOrderCardIds)}
</body>
</html>`;
}

export function downloadTextFile(filename: string, mimeType: string, content: string): void {
  const blob = new Blob([content], { type: `${mimeType};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
