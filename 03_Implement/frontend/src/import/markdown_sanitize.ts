export function sanitizeMarkdownForDisplay(markdown: string): string {
  return markdown.replace(/<[^>]+>/g, "");
}
