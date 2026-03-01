import { describe, expect, it } from "vitest";

import { createViewLocalePersistenceScope } from "./view_locale_scope";

describe("createViewLocalePersistenceScope", () => {
  it("tracks the latest doc/view scope for locale persistence", () => {
    const scope = createViewLocalePersistenceScope({ docId: "doc-a", viewMode: "explore", allowPersistence: true });

    expect(scope.getScope()).toEqual({ docId: "doc-a", viewMode: "explore", allowPersistence: true });

    scope.updateScope({ docId: "doc-a", viewMode: "review", allowPersistence: false });
    expect(scope.getScope()).toEqual({ docId: "doc-a", viewMode: "review", allowPersistence: false });

    scope.updateScope({ docId: "doc-b", viewMode: "summary", allowPersistence: true });
    expect(scope.getScope()).toEqual({ docId: "doc-b", viewMode: "summary", allowPersistence: true });
  });
});
