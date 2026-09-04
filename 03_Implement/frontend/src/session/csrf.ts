export const CSRF_COOKIE = "Kj-Atlas-Csrf";
export const CSRF_HEADER = "X-Kj-Atlas-Csrf";
const CSRF_TOKEN_PATTERN = /^[0-9a-f]{64}$/;

export function csrfTokenFromCookie(cookieSource: string): string | undefined {
  for (const part of cookieSource.split(";")) {
    const trimmed = part.trim();
    const separator = trimmed.indexOf("=");
    if (separator <= 0) {
      continue;
    }
    const name = trimmed.slice(0, separator);
    const value = trimmed.slice(separator + 1);
    if (name === CSRF_COOKIE && CSRF_TOKEN_PATTERN.test(value)) {
      return value;
    }
  }
  return undefined;
}

export function csrfHeader(): Record<string, string> {
  const cookieSource = typeof document === "undefined" ? "" : document.cookie;
  const token = csrfTokenFromCookie(cookieSource);
  return token ? { [CSRF_HEADER]: token } : {};
}
