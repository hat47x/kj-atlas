import { describe, expect, it } from "vitest";

import { createViewLocalePersistenceScope } from "./view_locale_scope";

describe("createViewLocalePersistenceScope", () => {
  it("tracks the latest doc/view scope for locale persistence", () => {
    const scope = createViewLocalePersistenceScope({ docId: "doc-a", viewMode: "explore" });

    expect(scope.getScope()).toEqual({ docId: "doc-a", viewMode: "explore" });

    scope.updateScope({ docId: "doc-a", viewMode: "review" });
    expect(scope.getScope()).toEqual({ docId: "doc-a", viewMode: "review" });

    scope.updateScope({ docId: "doc-b", viewMode: "summary" });
    expect(scope.getScope()).toEqual({ docId: "doc-b", viewMode: "summary" });
  });
});
