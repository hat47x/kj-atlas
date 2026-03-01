import type { ViewMode } from "../domain/view/view_mode";

type ViewLocalePersistenceScope = {
  docId: string;
  viewMode: ViewMode;
  allowPersistence: boolean;
};

export type { ViewLocalePersistenceScope };

export function createViewLocalePersistenceScope(initialScope: ViewLocalePersistenceScope) {
  let scope = initialScope;

  return {
    getScope(): ViewLocalePersistenceScope {
      return scope;
    },
    updateScope(nextScope: ViewLocalePersistenceScope): void {
      scope = nextScope;
    },
  };
}
