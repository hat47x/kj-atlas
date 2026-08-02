import {
  buildTenantStoragePrefix,
  type TenantBrowserStorageScope,
} from "../storage/tenant_scope";
import type { DocumentV1 } from "./types";

export const HAND_DRAWN_CUE_ASSET_MAX_BYTES = 4 * 1024;
export const HAND_DRAWN_CUE_COORDINATE_MAX = 20;
export const HAND_DRAWN_CUE_BUNDLE_MAX_ASSETS = 400;
export const HAND_DRAWN_CUE_BUNDLE_MAX_BYTES = 2 * 1024 * 1024;
export const HAND_DRAWN_CUE_BUNDLE_FILE_NAME = "representative_visual_cue_assets.json";
const DATABASE_NAME = "kj-atlas-representative-visual-cues";
const DATABASE_VERSION = 2;
const LEGACY_STORE_NAME = "assets";
const STORE_NAME = "assets-v2";
const SCOPE_DOCUMENT_INDEX = "scopeDocumentKey";
const LOCAL_SCOPE_KEY = "kj-atlas/local-scope/v1/";
const VALID_IMAGE_REF = /^visual-cue:[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export type HandDrawnCuePointV1 = Readonly<{
  x: number;
  y: number;
}>;

export type HandDrawnCueAssetV1 = Readonly<{
  version: 1;
  kind: "hand_drawn";
  width: 20;
  height: 20;
  strokes: readonly (readonly HandDrawnCuePointV1[])[];
}>;

export type HandDrawnCueAssetBundleV1 = Readonly<{
  version: "1";
  documentId: string;
  assets: readonly Readonly<{
    imageRef: string;
    asset: HandDrawnCueAssetV1;
  }>[];
}>;

type StoredCueAssetV1 = {
  storageKey: string;
  imageRef: string;
  scopeKey: string;
  documentId: string;
  scopeDocumentKey: string;
  assetJson: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(value: Record<string, unknown>, expected: readonly string[]): boolean {
  const actual = Object.keys(value).sort();
  return actual.length === expected.length
    && actual.every((key, index) => key === [...expected].sort()[index]);
}

function isCoordinate(value: unknown): value is number {
  return Number.isInteger(value) && Number(value) >= 0 && Number(value) <= HAND_DRAWN_CUE_COORDINATE_MAX;
}

export function parseHandDrawnCueAsset(value: unknown): HandDrawnCueAssetV1 {
  if (
    !isRecord(value)
    || !hasExactKeys(value, ["height", "kind", "strokes", "version", "width"])
    || value.version !== 1
    || value.kind !== "hand_drawn"
    || value.width !== 20
    || value.height !== 20
    || !Array.isArray(value.strokes)
    || value.strokes.length === 0
    || value.strokes.length > 64
  ) {
    throw new Error("invalid hand-drawn visual cue asset");
  }

  let pointCount = 0;
  const strokes = value.strokes.map((stroke) => {
    if (!Array.isArray(stroke) || stroke.length === 0 || stroke.length > 256) {
      throw new Error("invalid hand-drawn visual cue stroke");
    }
    const points = stroke.map((point) => {
      if (
        !isRecord(point)
        || !hasExactKeys(point, ["x", "y"])
        || !isCoordinate(point.x)
        || !isCoordinate(point.y)
      ) {
        throw new Error("invalid hand-drawn visual cue point");
      }
      pointCount += 1;
      return { x: point.x, y: point.y };
    });
    return points;
  });

  if (pointCount > 512) {
    throw new Error("hand-drawn visual cue has too many points");
  }

  const asset: HandDrawnCueAssetV1 = {
    version: 1,
    kind: "hand_drawn",
    width: 20,
    height: 20,
    strokes,
  };
  if (new TextEncoder().encode(JSON.stringify(asset)).byteLength > HAND_DRAWN_CUE_ASSET_MAX_BYTES) {
    throw new Error("hand-drawn visual cue exceeds 4KB");
  }
  return asset;
}

export function serializeHandDrawnCueAsset(asset: HandDrawnCueAssetV1): string {
  return JSON.stringify(parseHandDrawnCueAsset(asset));
}

export function visualCueAssetScopeKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStoragePrefix(scope) : LOCAL_SCOPE_KEY;
}

function assetStorageKey(scopeKey: string, imageRef: string): string {
  return JSON.stringify([scopeKey, imageRef]);
}

function scopeDocumentKey(scopeKey: string, documentId: string): string {
  return JSON.stringify([scopeKey, documentId]);
}

function createStoredRecord(
  scopeKey: string,
  documentId: string,
  imageRef: string,
  assetJson: string,
): StoredCueAssetV1 {
  return {
    storageKey: assetStorageKey(scopeKey, imageRef),
    imageRef,
    scopeKey,
    documentId,
    scopeDocumentKey: scopeDocumentKey(scopeKey, documentId),
    assetJson,
  };
}

function openDatabase(): Promise<IDBDatabase> {
  if (typeof indexedDB === "undefined") {
    return Promise.reject(new Error("IndexedDB is unavailable"));
  }
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      const transaction = request.transaction;
      if (!transaction) {
        throw new Error("visual cue storage upgrade transaction is unavailable");
      }
      const store = database.objectStoreNames.contains(STORE_NAME)
        ? transaction.objectStore(STORE_NAME)
        : database.createObjectStore(STORE_NAME, { keyPath: "storageKey" });
      if (!store.indexNames.contains(SCOPE_DOCUMENT_INDEX)) {
        store.createIndex(SCOPE_DOCUMENT_INDEX, "scopeDocumentKey", { unique: false });
      }

      if (database.objectStoreNames.contains(LEGACY_STORE_NAME)) {
        const legacyStore = transaction.objectStore(LEGACY_STORE_NAME);
        const cursorRequest = legacyStore.openCursor();
        cursorRequest.onsuccess = () => {
          const cursor = cursorRequest.result;
          if (!cursor) {
            database.deleteObjectStore(LEGACY_STORE_NAME);
            return;
          }
          const legacy = cursor.value as Omit<StoredCueAssetV1, "storageKey">;
          store.put({
            ...legacy,
            storageKey: assetStorageKey(legacy.scopeKey, legacy.imageRef),
          } satisfies StoredCueAssetV1);
          cursor.continue();
        };
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("failed to open visual cue storage"));
    request.onblocked = () => reject(new Error("visual cue storage upgrade is blocked"));
  });
}

function waitForTransaction(transaction: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error ?? new Error("visual cue storage transaction failed"));
    transaction.onabort = () => reject(transaction.error ?? new Error("visual cue storage transaction aborted"));
  });
}

export async function saveHandDrawnCueAsset(
  documentId: string,
  asset: HandDrawnCueAssetV1,
  scope?: TenantBrowserStorageScope,
): Promise<string> {
  const assetJson = serializeHandDrawnCueAsset(asset);
  const scopeKey = visualCueAssetScopeKey(scope);
  const imageRef = `visual-cue:${crypto.randomUUID()}`;
  const database = await openDatabase();
  try {
    const transaction = database.transaction(STORE_NAME, "readwrite");
    const record = createStoredRecord(scopeKey, documentId, imageRef, assetJson);
    transaction.objectStore(STORE_NAME).add(record);
    await waitForTransaction(transaction);
    return imageRef;
  } finally {
    database.close();
  }
}

export async function loadHandDrawnCueAsset(
  imageRef: string,
  scope?: TenantBrowserStorageScope,
): Promise<HandDrawnCueAssetV1 | null> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(STORE_NAME, "readonly");
    const scopeKey = visualCueAssetScopeKey(scope);
    const request = transaction.objectStore(STORE_NAME).get(assetStorageKey(scopeKey, imageRef));
    const record = await new Promise<StoredCueAssetV1 | undefined>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result as StoredCueAssetV1 | undefined);
      request.onerror = () => reject(request.error ?? new Error("failed to read visual cue asset"));
    });
    await waitForTransaction(transaction);
    if (!record || record.scopeKey !== scopeKey) {
      return null;
    }
    return parseHandDrawnCueAsset(JSON.parse(record.assetJson));
  } finally {
    database.close();
  }
}

export async function deleteHandDrawnCueAsset(
  imageRef: string,
  scope?: TenantBrowserStorageScope,
): Promise<boolean> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(STORE_NAME, "readwrite");
    const store = transaction.objectStore(STORE_NAME);
    const scopeKey = visualCueAssetScopeKey(scope);
    const request = store.get(assetStorageKey(scopeKey, imageRef));
    const record = await new Promise<StoredCueAssetV1 | undefined>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result as StoredCueAssetV1 | undefined);
      request.onerror = () => reject(request.error ?? new Error("failed to inspect visual cue asset"));
    });
    const canDelete = record?.scopeKey === scopeKey;
    if (canDelete) {
      store.delete(assetStorageKey(scopeKey, imageRef));
    }
    await waitForTransaction(transaction);
    return canDelete;
  } finally {
    database.close();
  }
}

export function collectHandDrawnCueImageRefs(document: DocumentV1): string[] {
  return [...new Set(
    document.islands.flatMap((island) => {
      const cue = island.representativeCue;
      return cue?.kind === "hand_drawn" && cue.imageRef ? [cue.imageRef] : [];
    }),
  )].sort();
}

export function stripHandDrawnVisualCues(document: DocumentV1): DocumentV1 {
  if (!document.islands.some((island) => island.representativeCue?.kind === "hand_drawn")) {
    return document;
  }
  return {
    ...document,
    islands: document.islands.map((island) => {
      if (island.representativeCue?.kind !== "hand_drawn") {
        return island;
      }
      const { representativeCue: _representativeCue, ...rest } = island;
      return rest;
    }),
  };
}

export function parseHandDrawnCueAssetBundle(
  value: unknown,
  document: DocumentV1,
): HandDrawnCueAssetBundleV1 {
  if (
    !isRecord(value)
    || !hasExactKeys(value, ["assets", "documentId", "version"])
    || value.version !== "1"
    || value.documentId !== document.id
    || !Array.isArray(value.assets)
    || value.assets.length === 0
    || value.assets.length > HAND_DRAWN_CUE_BUNDLE_MAX_ASSETS
  ) {
    throw new Error("invalid hand-drawn visual cue asset bundle");
  }

  const seen = new Set<string>();
  const assets = value.assets.map((entry) => {
    if (
      !isRecord(entry)
      || !hasExactKeys(entry, ["asset", "imageRef"])
      || typeof entry.imageRef !== "string"
      || !VALID_IMAGE_REF.test(entry.imageRef)
      || seen.has(entry.imageRef)
    ) {
      throw new Error("invalid hand-drawn visual cue asset bundle entry");
    }
    seen.add(entry.imageRef);
    return {
      imageRef: entry.imageRef,
      asset: parseHandDrawnCueAsset(entry.asset),
    };
  });

  const expectedRefs = collectHandDrawnCueImageRefs(document);
  const actualRefs = [...seen].sort();
  if (
    expectedRefs.length !== actualRefs.length
    || expectedRefs.some((imageRef, index) => imageRef !== actualRefs[index])
  ) {
    throw new Error("hand-drawn visual cue asset bundle does not match document references");
  }

  const bundle: HandDrawnCueAssetBundleV1 = {
    version: "1",
    documentId: document.id,
    assets: assets.sort((left, right) => left.imageRef.localeCompare(right.imageRef)),
  };
  if (new TextEncoder().encode(JSON.stringify(bundle)).byteLength > HAND_DRAWN_CUE_BUNDLE_MAX_BYTES) {
    throw new Error("hand-drawn visual cue asset bundle exceeds 2MB");
  }
  return bundle;
}

export async function buildHandDrawnCueAssetBundle(
  document: DocumentV1,
  scope?: TenantBrowserStorageScope,
): Promise<HandDrawnCueAssetBundleV1> {
  const imageRefs = collectHandDrawnCueImageRefs(document);
  if (imageRefs.length === 0 || imageRefs.length > HAND_DRAWN_CUE_BUNDLE_MAX_ASSETS) {
    throw new Error("document has no exportable hand-drawn visual cue assets");
  }
  const assets = [];
  for (const imageRef of imageRefs) {
    const asset = await loadHandDrawnCueAsset(imageRef, scope);
    if (!asset) {
      throw new Error(`hand-drawn visual cue asset is unavailable (${imageRef})`);
    }
    assets.push({ imageRef, asset });
  }
  return parseHandDrawnCueAssetBundle({
    version: "1",
    documentId: document.id,
    assets,
  }, document);
}

export async function restoreHandDrawnCueAssetBundle(
  document: DocumentV1,
  value: unknown,
  scope?: TenantBrowserStorageScope,
): Promise<number> {
  const bundle = parseHandDrawnCueAssetBundle(value, document);
  const scopeKey = visualCueAssetScopeKey(scope);
  const database = await openDatabase();
  try {
    const transaction = database.transaction(STORE_NAME, "readwrite");
    const store = transaction.objectStore(STORE_NAME);
    await new Promise<void>((resolve, reject) => {
      let remaining = bundle.assets.length;
      let settled = false;
      for (const entry of bundle.assets) {
        const storageKey = assetStorageKey(scopeKey, entry.imageRef);
        const request = store.get(storageKey);
        request.onerror = () => {
          if (!settled) {
            settled = true;
            transaction.abort();
            reject(request.error ?? new Error("failed to inspect imported visual cue asset"));
          }
        };
        request.onsuccess = () => {
          if (settled) {
            return;
          }
          const existing = request.result as StoredCueAssetV1 | undefined;
          if (existing && existing.documentId !== document.id) {
            settled = true;
            transaction.abort();
            reject(new Error("visual cue imageRef is already owned by another document"));
            return;
          }
          store.put(createStoredRecord(
            scopeKey,
            document.id,
            entry.imageRef,
            serializeHandDrawnCueAsset(entry.asset),
          ));
          remaining -= 1;
          if (remaining === 0) {
            settled = true;
            resolve();
          }
        };
      }
    });
    await waitForTransaction(transaction);
    return bundle.assets.length;
  } finally {
    database.close();
  }
}

export async function deleteUnreferencedHandDrawnCueAssets(
  documentId: string,
  retainedImageRefs: ReadonlySet<string>,
  scope?: TenantBrowserStorageScope,
): Promise<number> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(STORE_NAME, "readwrite");
    const store = transaction.objectStore(STORE_NAME);
    const index = store.index(SCOPE_DOCUMENT_INDEX);
    const request = index.openCursor(
      IDBKeyRange.only(scopeDocumentKey(visualCueAssetScopeKey(scope), documentId)),
    );
    let deleted = 0;
    await new Promise<void>((resolve, reject) => {
      request.onsuccess = () => {
        const cursor = request.result;
        if (!cursor) {
          resolve();
          return;
        }
        const record = cursor.value as StoredCueAssetV1;
        if (!retainedImageRefs.has(record.imageRef)) {
          cursor.delete();
          deleted += 1;
        }
        cursor.continue();
      };
      request.onerror = () => reject(request.error ?? new Error("failed to enumerate visual cue assets"));
    });
    await waitForTransaction(transaction);
    return deleted;
  } finally {
    database.close();
  }
}
