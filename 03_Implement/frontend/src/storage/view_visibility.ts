import {
  DEFAULT_PACK_VISIBILITY,
  DEFAULT_VIEW_VISIBILITY,
  isPublishVisibility,
  type PublishVisibility,
} from "../domain/policy/publish_visibility";
import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const VIEW_VISIBILITY_STORAGE_KEY = "kj-atlas/view-visibility-by-doc";

type PersistedVisibilityByDoc = Record<string, {
  viewVisibility?: PublishVisibility;
  packVisibility?: PublishVisibility;
}>;

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function visibilityStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(VIEW_VISIBILITY_STORAGE_KEY, scope) : VIEW_VISIBILITY_STORAGE_KEY;
}

export function parsePersistedVisibilityByDoc(rawValue: string | null | undefined): PersistedVisibilityByDoc {
  if (!rawValue) {
    return {};
  }

  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return {};
    }

    const next: PersistedVisibilityByDoc = {};
    for (const [docId, value] of Object.entries(parsed as Record<string, unknown>)) {
      if (!docId || typeof value !== "object" || value === null || Array.isArray(value)) {
        continue;
      }

      const candidate = value as Record<string, unknown>;
      const viewVisibility = isPublishVisibility(candidate.viewVisibility) ? candidate.viewVisibility : undefined;
      const packVisibility = isPublishVisibility(candidate.packVisibility) ? candidate.packVisibility : undefined;

      if (viewVisibility || packVisibility) {
        next[docId] = {
          ...(viewVisibility ? { viewVisibility } : {}),
          ...(packVisibility ? { packVisibility } : {}),
        };
      }
    }

    return next;
  } catch {
    return {};
  }
}

export function loadViewVisibilityForDocument(
  docId: string,
  scope?: TenantBrowserStorageScope,
): { viewVisibility: PublishVisibility; packVisibility: PublishVisibility } {
  if (!docId || !isStorageAvailable()) {
    return { viewVisibility: DEFAULT_VIEW_VISIBILITY, packVisibility: DEFAULT_PACK_VISIBILITY };
  }

  const byDoc = parsePersistedVisibilityByDoc(window.localStorage.getItem(visibilityStorageKey(scope)));
  const current = byDoc[docId];
  return {
    viewVisibility: current?.viewVisibility ?? DEFAULT_VIEW_VISIBILITY,
    packVisibility: current?.packVisibility ?? DEFAULT_PACK_VISIBILITY,
  };
}

export function saveViewVisibilityForDocument(
  docId: string,
  visibility: { viewVisibility: PublishVisibility; packVisibility: PublishVisibility },
  scope?: TenantBrowserStorageScope,
): void {
  if (!docId || !isStorageAvailable()) {
    return;
  }

  const storageKey = visibilityStorageKey(scope);
  const byDoc = parsePersistedVisibilityByDoc(window.localStorage.getItem(storageKey));
  byDoc[docId] = visibility;
  try {
    window.localStorage.setItem(storageKey, JSON.stringify(byDoc));
  } catch {
    // Storage may be disabled or full. The in-memory visibility remains usable.
  }
}
