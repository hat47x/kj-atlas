import { describe, expect, it } from "vitest";

import { parsePublicPackManifest } from "./public_pack_manifest";

describe("parsePublicPackManifest", () => {
  it("uses Public fallback visibility for legacy entries", () => {
    const manifest = parsePublicPackManifest({
      defaultPackId: "main",
      packs: [{ id: "main", documentPath: "main.document.json", viewPath: "main.view.json" }],
    });

    expect(manifest.defaultPackId).toBe("main");
    expect(manifest.packs).toEqual([
      {
        id: "main",
        documentPath: "main.document.json",
        viewPath: "main.view.json",
        visibility: "Public",
      },
    ]);
  });

  it("drops invalid entries and preserves valid visibility", () => {
    const manifest = parsePublicPackManifest({
      packs: [
        { id: "ok", documentPath: "ok.document.json", visibility: "Restricted", enforceSafeMode: true, readOnly: true },
        { id: "invalid-visibility", documentPath: "invalid.document.json", visibility: "FriendsOnly" },
        { id: "bad", documentPath: 100 },
      ],
    });

    expect(manifest.packs).toEqual([
      {
        id: "ok",
        documentPath: "ok.document.json",
        visibility: "Restricted",
        enforceSafeMode: true,
        readOnly: true,
      },
    ]);
  });
});
