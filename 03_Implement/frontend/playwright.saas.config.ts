import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  testMatch: [
    "tenant_session_multitab.spec.ts",
    "tenant_session_round8_acceptance.spec.ts",
  ],
  timeout: 30_000,
  retries: 0,
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:4174",
    screenshot: "only-on-failure",
    trace: "on-first-retry",
  },
  webServer: {
    command: "node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4174",
    port: 4174,
    reuseExistingServer: false,
    timeout: 120_000,
    env: {
      ...process.env,
      KJ_ATLAS_RUNTIME_PROFILE: "saas-multitenant",
    },
  },
});