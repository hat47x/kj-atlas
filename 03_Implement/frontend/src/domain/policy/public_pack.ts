export function resolvePublicPackIdFromSearch(search: string): string | null {
  const query = new URLSearchParams(search);
  const raw = query.get("pack");
  if (!raw) {
    return null;
  }

  const trimmed = raw.trim();
  if (!trimmed) {
    return null;
  }

  return trimmed;
}

