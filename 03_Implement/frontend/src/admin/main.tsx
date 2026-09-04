import React from "react";
import ReactDOM from "react-dom/client";

import { ModelAllowlistAdminConsole } from "./ModelAllowlistAdminConsole";

const root = document.getElementById("admin-root");
if (!root) {
  throw new Error("Missing #admin-root");
}

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <ModelAllowlistAdminConsole />
  </React.StrictMode>,
);
