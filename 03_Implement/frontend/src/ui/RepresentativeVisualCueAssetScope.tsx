import { createContext, useContext, type ReactNode } from "react";

import type { TenantBrowserStorageScope } from "../storage/tenant_scope";

const RepresentativeVisualCueAssetScopeContext = createContext<TenantBrowserStorageScope | undefined>(undefined);

export function RepresentativeVisualCueAssetScopeProvider({
  scope,
  children,
}: {
  scope?: TenantBrowserStorageScope;
  children: ReactNode;
}) {
  return (
    <RepresentativeVisualCueAssetScopeContext.Provider value={scope}>
      {children}
    </RepresentativeVisualCueAssetScopeContext.Provider>
  );
}

export function useRepresentativeVisualCueAssetScope(): TenantBrowserStorageScope | undefined {
  return useContext(RepresentativeVisualCueAssetScopeContext);
}
