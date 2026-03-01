import { describe, expect, it } from "vitest";

import { resolveLocaleFromSearch, resolveViewLocale } from "./view_locale_resolution";

describe("view locale resolution", () => {
  it("prioritizes URL locale over metadata and local storage", () => {
    const resolved = resolveViewLocale({
      search: "?locale=en",
      metadataLocale: "ja",
      persistedLocale: "ja",
      isReadOnly: false,
    });

    expect(resolved).toEqual({ locale: "en", source: "url", shouldPersist: false });
  });

  it("uses view metadata locale when URL parameter is absent", () => {
    const resolved = resolveViewLocale({
      search: "",
      metadataLocale: "en",
      persistedLocale: "ja",
      isReadOnly: false,
    });

    expect(resolved).toEqual({ locale: "en", source: "view-metadata", shouldPersist: true });
  });

  it("falls back to local storage locale when metadata locale is missing", () => {
    const resolved = resolveViewLocale({
      search: "",
      metadataLocale: undefined,
      persistedLocale: "en",
      isReadOnly: false,
    });

    expect(resolved).toEqual({ locale: "en", source: "local-storage", shouldPersist: true });
  });

  it("falls back to default locale when metadata/local storage are invalid", () => {
    const resolved = resolveViewLocale({
      search: "",
      metadataLocale: "fr",
      persistedLocale: "de",
      isReadOnly: false,
    });

    expect(resolved).toEqual({ locale: "ja", source: "default", shouldPersist: true });
  });

  it("does not persist in read-only mode even without URL locale", () => {
    const resolved = resolveViewLocale({
      search: "",
      metadataLocale: "en",
      persistedLocale: "ja",
      isReadOnly: true,
    });

    expect(resolved).toEqual({ locale: "en", source: "view-metadata", shouldPersist: false });
  });

  it("restores per-view locale across switch and reload", () => {
    const persistedByView = {
      explore: "en",
      review: "ja",
    } as const;

    const explore = resolveViewLocale({
      search: "",
      metadataLocale: undefined,
      persistedLocale: persistedByView.explore,
      isReadOnly: false,
    });
    const review = resolveViewLocale({
      search: "",
      metadataLocale: undefined,
      persistedLocale: persistedByView.review,
      isReadOnly: false,
    });
    const reloadedExplore = resolveViewLocale({
      search: "",
      metadataLocale: undefined,
      persistedLocale: persistedByView.explore,
      isReadOnly: false,
    });

    expect(explore.locale).toBe("en");
    expect(review.locale).toBe("ja");
    expect(reloadedExplore.locale).toBe("en");
  });

  it("accepts locale query aliases", () => {
    expect(resolveLocaleFromSearch("?lang=en")).toBe("en");
    expect(resolveLocaleFromSearch("?uiLocale=ja")).toBe("ja");
  });
});
