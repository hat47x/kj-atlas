import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import { resolveRuntimeEntryMode } from "./session/runtime_activation";
import { TenantSessionBlockedView } from "./ui/TenantSessionBootstrapGate";
import { TenantSessionRuntimeGate } from "./ui/TenantSessionRuntimeGate";

document.documentElement.style.margin = "0";
document.documentElement.style.height = "100%";
document.body.style.margin = "0";
document.body.style.height = "100%";

const rootElement = document.getElementById("root")!;
rootElement.style.height = "100%";

const runtimeEntryMode = resolveRuntimeEntryMode(
  import.meta.env.KJ_ATLAS_RUNTIME_PROFILE,
);

function renderRuntimeEntry() {
  if (runtimeEntryMode === "tenant-session-required") {
    return (
      <TenantSessionRuntimeGate
        deployment={window.location.origin}
        renderApp={(result) => <App storageScope={result.storageScope} />}
      />
    );
  }
  if (runtimeEntryMode === "invalid") {
    return (
      <TenantSessionBlockedView
        reason="session_unavailable"
        onRetry={() => window.location.reload()}
      />
    );
  }
  return <App />;
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    {renderRuntimeEntry()}
  </React.StrictMode>
);
