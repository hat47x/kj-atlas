import type { Locale } from "../i18n/translate";
import type { PublishVisibility } from "../domain/policy/publish_visibility";
import type { ViewMode } from "../domain/view/view_mode";
import { loadAdvancedUiEnabled, saveAdvancedUiEnabled } from "./advanced_ui";
import {
  initializeCurrentReviewerRef,
  saveCurrentReviewerRef,
} from "./current_reviewer";
import {
  loadEmptyCanvasHintCompleted,
  saveEmptyCanvasHintCompleted,
} from "./empty_canvas_hint";
import { loadRecentDocumentIds, pushRecentDocumentId } from "./recent";
import {
  buildTenantStoragePrefix,
  clearTenantScopedStorage,
  type TenantBrowserStorageScope,
} from "./tenant_scope";
import {
  loadViewLocaleForDocumentView,
  saveViewLocaleForDocumentView,
} from "./view_locale";
import { loadViewModeForDocument, saveViewModeForDocument } from "./view_mode";
import {
  loadViewVisibilityForDocument,
  saveViewVisibilityForDocument,
} from "./view_visibility";

export type AppBrowserStorage = Readonly<{
  scope?: TenantBrowserStorageScope;
  scopeIdentity: string;
  clearScope: () => number;
  loadAdvancedUiEnabled: () => boolean;
  saveAdvancedUiEnabled: (enabled: boolean) => void;
  initializeCurrentReviewerRef: () => string;
  saveCurrentReviewerRef: (value: string) => string;
  loadEmptyCanvasHintCompleted: () => boolean;
  saveEmptyCanvasHintCompleted: (completed: boolean) => void;
  loadRecentDocumentIds: () => string[];
  pushRecentDocumentId: (docId: string) => string[];
  loadViewLocaleForDocumentView: (docId: string, viewMode: ViewMode) => Locale | null;
  saveViewLocaleForDocumentView: (
    docId: string,
    viewMode: ViewMode,
    locale: string,
  ) => void;
  loadViewModeForDocument: (docId: string) => ViewMode | null;
  saveViewModeForDocument: (docId: string, mode: ViewMode) => void;
  loadViewVisibilityForDocument: (docId: string) => {
    viewVisibility: PublishVisibility;
    packVisibility: PublishVisibility;
  };
  saveViewVisibilityForDocument: (
    docId: string,
    visibility: {
      viewVisibility: PublishVisibility;
      packVisibility: PublishVisibility;
    },
  ) => void;
}>;

export function assertAppStorageScopeStable(
  initialScopeIdentity: string,
  currentScopeIdentity: string,
): void {
  if (initialScopeIdentity !== currentScopeIdentity) {
    throw new Error("App storage scope cannot change without a hard document replacement");
  }
}

export function createAppBrowserStorage(
  scope?: TenantBrowserStorageScope,
): AppBrowserStorage {
  const validatedScope = scope
    ? Object.freeze({
      deployment: scope.deployment,
      tenantId: scope.tenantId,
      principalId: scope.principalId,
    })
    : undefined;
  const scopeIdentity = validatedScope
    ? buildTenantStoragePrefix(validatedScope)
    : "legacy-single-tenant";

  return Object.freeze({
    scope: validatedScope,
    scopeIdentity,
    clearScope: () => validatedScope
      ? clearTenantScopedStorage(window.localStorage, validatedScope)
      : 0,
    loadAdvancedUiEnabled: () => loadAdvancedUiEnabled(validatedScope),
    saveAdvancedUiEnabled: (enabled: boolean) => saveAdvancedUiEnabled(enabled, validatedScope),
    initializeCurrentReviewerRef: () => initializeCurrentReviewerRef(validatedScope),
    saveCurrentReviewerRef: (value: string) => saveCurrentReviewerRef(value, validatedScope),
    loadEmptyCanvasHintCompleted: () => loadEmptyCanvasHintCompleted(validatedScope),
    saveEmptyCanvasHintCompleted: (completed: boolean) => saveEmptyCanvasHintCompleted(
      completed,
      validatedScope,
    ),
    loadRecentDocumentIds: () => loadRecentDocumentIds(validatedScope),
    pushRecentDocumentId: (docId: string) => pushRecentDocumentId(docId, validatedScope),
    loadViewLocaleForDocumentView: (docId: string, viewMode: ViewMode) => (
      loadViewLocaleForDocumentView(docId, viewMode, validatedScope)
    ),
    saveViewLocaleForDocumentView: (docId: string, viewMode: ViewMode, locale: string) => (
      saveViewLocaleForDocumentView(docId, viewMode, locale, validatedScope)
    ),
    loadViewModeForDocument: (docId: string) => loadViewModeForDocument(docId, validatedScope),
    saveViewModeForDocument: (docId: string, mode: ViewMode) => (
      saveViewModeForDocument(docId, mode, validatedScope)
    ),
    loadViewVisibilityForDocument: (docId: string) => (
      loadViewVisibilityForDocument(docId, validatedScope)
    ),
    saveViewVisibilityForDocument: (docId, visibility) => (
      saveViewVisibilityForDocument(docId, visibility, validatedScope)
    ),
  });
}
