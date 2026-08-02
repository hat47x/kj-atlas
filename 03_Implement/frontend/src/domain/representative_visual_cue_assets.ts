import {
  buildTenantStoragePrefix,
  type TenantBrowserStorageScope,
} from "../storage/tenant_scope";

export const HAND_DRAWN_CUE_ASSET_MAX_BYTES = 4 * 1024;
export const HAND_DRAWN_CUE_COORDINATE_MAX = 20;
const DATABASE_NAME = "kj-atlas-representative-visual-cues";
const DATABASE_VERSION = 1;
const STORE_NAME = "assets";
const SCOPE_DOCUMENT_INDEX = "scopeDocumentKey";
const LOCAL_SCOPE_KEY = "kj-atlas/local-scope/v1/";

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

type StoredCueAssetV1 = {
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

function scopeDocumentKey(scopeKey: string, documentId: string): string {
  return JSON.stringify([scopeKey, documentId]);
}

function openDatabase(): Promise<IDBDatabase> {
  if (typeof indexedDB === "undefined") {
    return Promise.reject(new Error("IndexedDB is unavailable"));
  }
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      const store = database.createObjectStore(STORE_NAME, { keyPath: "imageRef" });
      store.createIndex(SCOPE_DOCUMENT_INDEX, "scopeDocumentKey", { unique: false });
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
    const record: StoredCueAssetV1 = {
      imageRef,
      scopeKey,
      documentId,
      scopeDocumentKey: scopeDocumentKey(scopeKey, documentId),
      assetJson,
    };
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
    const request = transaction.objectStore(STORE_NAME).get(imageRef);
    const record = await new Promise<StoredCueAssetV1 | undefined>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result as StoredCueAssetV1 | undefined);
      request.onerror = () => reject(request.error ?? new Error("failed to read visual cue asset"));
    });
    await waitForTransaction(transaction);
    if (!record || record.scopeKey !== visualCueAssetScopeKey(scope)) {
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
    const request = store.get(imageRef);
    const record = await new Promise<StoredCueAssetV1 | undefined>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result as StoredCueAssetV1 | undefined);
      request.onerror = () => reject(request.error ?? new Error("failed to inspect visual cue asset"));
    });
    const canDelete = record?.scopeKey === visualCueAssetScopeKey(scope);
    if (canDelete) {
      store.delete(imageRef);
    }
    await waitForTransaction(transaction);
    return canDelete;
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
