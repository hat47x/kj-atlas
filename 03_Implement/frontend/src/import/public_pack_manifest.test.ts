import { describe, expect, it } from "vitest";

import { parsePublicPackManifest, validatePublicPackManifest } from "./public_pack_manifest";

describe("validatePublicPackManifest", () => {
  it("uses Public fallback visibility for legacy entries", () => {
    const result = validatePublicPackManifest({
      defaultPackId: "main",
      packs: [{ id: "main", documentPath: "main.document.json", viewPath: "main.view.json" }],
    });

    expect(result).toEqual({
      ok: true,
      manifest: {
        defaultPackId: "main",
        packs: [
          {
            id: "main",
            documentPath: "main.document.json",
            viewPath: "main.view.json",
            visibility: "Public",
          },
        ],
      },
    });
  });

  it("rejects invalid entries in strict validation", () => {
    const result = validatePublicPackManifest({
      packs: [
        { id: "ok", documentPath: "ok.document.json", visibility: "Restricted", enforceSafeMode: true, readOnly: true },
        { id: "invalid-visibility", documentPath: "invalid.document.json", visibility: "FriendsOnly" },
        { id: "bad", documentPath: 100 },
      ],
    });

    expect(result).toEqual({
      ok: false,
      errors: [
        {
          path: "packs[1].visibility",
          message: 'visibility must be "Public" | "Unlisted" | "Org" | "Restricted" when present.',
        },
        {
          path: "packs[2].documentPath",
          message: "documentPath must be a non-empty string.",
        },
      ],
    });
  });



  it.each(["", "public", null, 1, { value: "Org" }])("rejects non-enum visibility values: %p", (visibility) => {
    const result = validatePublicPackManifest({
      packs: [{ id: "invalid", documentPath: "invalid.document.json", visibility }],
    });

    expect(result).toEqual({
      ok: false,
      errors: [
        {
          path: "packs[0].visibility",
          message: 'visibility must be "Public" | "Unlisted" | "Org" | "Restricted" when present.',
        },
      ],
    });
  });

  it("accepts all supported visibility enum values", () => {
    const result = validatePublicPackManifest({
      packs: [
        { id: "public", documentPath: "public.document.json", visibility: "Public" },
        { id: "unlisted", documentPath: "unlisted.document.json", visibility: "Unlisted" },
        { id: "org", documentPath: "org.document.json", visibility: "Org" },
        { id: "restricted", documentPath: "restricted.document.json", visibility: "Restricted" },
      ],
    });

    expect(result).toEqual({
      ok: true,
      manifest: {
        packs: [
          { id: "public", documentPath: "public.document.json", visibility: "Public" },
          { id: "unlisted", documentPath: "unlisted.document.json", visibility: "Unlisted" },
          { id: "org", documentPath: "org.document.json", visibility: "Org" },
          { id: "restricted", documentPath: "restricted.document.json", visibility: "Restricted" },
        ],
      },
    });
  });

  it("rejects duplicate pack ids", () => {
    const result = validatePublicPackManifest({
      packs: [
        { id: "main", documentPath: "main.document.json", visibility: "Public" },
        { id: "main", documentPath: "secondary.document.json", visibility: "Org" },
      ],
    });

    expect(result).toEqual({
      ok: false,
      errors: [{ path: "packs[1].id", message: "duplicate id: main" }],
    });
  });

  it("rejects defaultPackId that is missing from packs", () => {
    const result = validatePublicPackManifest({
      defaultPackId: "missing",
      packs: [{ id: "main", documentPath: "main.document.json", visibility: "Public" }],
    });

    expect(result).toEqual({
      ok: false,
      errors: [{ path: "defaultPackId", message: "defaultPackId must reference an existing packs[].id." }],
    });
  });
});

describe("parsePublicPackManifest", () => {
  it("preserves visibility across serialize/parse reload", () => {
    const savedManifest = {
      defaultPackId: "org-main",
      packs: [{ id: "org-main", documentPath: "org-main.document.json", viewPath: "org-main.view.json", visibility: "Org" }],
    };

    const reloaded = parsePublicPackManifest(JSON.parse(JSON.stringify(savedManifest)));

    expect(reloaded).toEqual(savedManifest);
  });

  it("returns empty packs for strict-validation failures", () => {
    const manifest = parsePublicPackManifest({
      packs: [{ id: "invalid", documentPath: "invalid.document.json", visibility: "FriendsOnly" }],
    });

    expect(manifest).toEqual({ packs: [] });
  });

});
