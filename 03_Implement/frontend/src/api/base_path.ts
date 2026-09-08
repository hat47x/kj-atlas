const DEFAULT_FRONTEND_API_BASE = "/api";
const CONTROL_CHARACTER_PATTERN = /[\u0000-\u001f\u007f]/;

/**
 * Resolve the public frontend API base as a same-origin absolute path.
 *
 * A network-path reference such as `//example.invalid` is not a path-only
 * configuration: browsers resolve it to another origin. Backslashes are also
 * rejected because URL parsers for HTTP(S) may treat them as slash-like
 * separators. Query/fragment components are outside the public base-path
 * contract and fall back to the safe default as well.
 *
 * The root path `/` is represented internally as an empty prefix so callers
 * can append `/docs`, `/ai/...`, etc. without producing `//docs`.
 */
export function resolveFrontendApiBase(rawValue: unknown): string {
  const value = typeof rawValue === "string" ? rawValue.trim() : "";

  if (value.length === 0) {
    return DEFAULT_FRONTEND_API_BASE;
  }

  if (
    !value.startsWith("/")
    || value.startsWith("//")
    || value.includes("\\")
    || value.includes("?")
    || value.includes("#")
    || CONTROL_CHARACTER_PATTERN.test(value)
  ) {
    return DEFAULT_FRONTEND_API_BASE;
  }

  const normalized = value.replace(/\/+$/, "");
  return normalized.length === 0 ? "" : normalized;
}
