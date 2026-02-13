export type NarrativeExportItem = {
  id: string;
  title?: string;
  text: string;
  createdAt?: string;
  reviewed: boolean;
  basedOnReadingOrder: string[];
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

function buildReadingOrderMarkdown(ids: string[], snippets: ReadingOrderSnippetMap): string {
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

function buildReadingOrderHtml(ids: string[], snippets: ReadingOrderSnippetMap): string {
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

export function buildNarrativeMarkdown(item: NarrativeExportItem, snippets: ReadingOrderSnippetMap = {}): string {
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
  lines.push("## BasedOnReadingOrder", "", buildReadingOrderMarkdown(item.basedOnReadingOrder, snippets));

  return lines.join("\n");
}

export function buildNarrativeHtml(item: NarrativeExportItem, snippets: ReadingOrderSnippetMap = {}): string {
  const title = item.title && item.title.trim().length > 0 ? item.title.trim() : "Narrative Export";
  const reviewBlock = item.reviewed
    ? '<div class="reviewed">Reviewed by human</div>'
    : '<div class="draft-banner">DRAFT (UNREVIEWED) — Please verify against the diagram.</div><div class="status">Status: Unreviewed draft</div>';

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
  </style>
</head>
<body>
  ${reviewBlock}
  ${item.title && item.title.trim().length > 0 ? `<h1>${escapeHtml(item.title.trim())}</h1>` : ""}
  <div class="meta">CreatedAt: ${escapeHtml(formatCreatedAt(item.createdAt))}</div>
  <h2>Narrative</h2>
  <div class="narrative">${escapeHtml(item.text)}</div>
  <h2>BasedOnReadingOrder</h2>
  ${buildReadingOrderHtml(item.basedOnReadingOrder, snippets)}
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
