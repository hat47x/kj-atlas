import {
  normalizeFilters,
  type QueryPreset,
} from "../domain/patch/workspace/ce3_patch_workspace";
import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const PRESET_STORAGE_KEY = "kj-atlas:ce3:patch-workspace-presets:v1";

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function queryPresetStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(PRESET_STORAGE_KEY, scope) : PRESET_STORAGE_KEY;
}

export function loadQueryPresets(scope?: TenantBrowserStorageScope): QueryPreset[] {
  if (!isStorageAvailable()) {
    return [];
  }

  const raw = window.localStorage.getItem(queryPresetStorageKey(scope));
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .filter((item): item is QueryPreset => {
        return item && typeof item === "object"
          && typeof item.id === "string"
          && typeof item.name === "string"
          && (item.scope === "all" || item.scope === "selection" || item.scope === "island")
          && typeof item.depth === "number"
          && Array.isArray(item.filters)
          && item.filters.every((value: unknown) => typeof value === "string");
      })
      .map((item) => ({
        ...item,
        depth: Math.max(1, Math.floor(item.depth)),
        filters: normalizeFilters(item.filters.join(",")),
      }));
  } catch {
    return [];
  }
}

export function saveQueryPresets(
  presets: QueryPreset[],
  scope?: TenantBrowserStorageScope,
): void {
  if (!isStorageAvailable()) {
    return;
  }

  window.localStorage.setItem(queryPresetStorageKey(scope), JSON.stringify(presets));
}
