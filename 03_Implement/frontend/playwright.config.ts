import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  // UX-PERF-01: this spec measures Time-to-Interactive against the
  // *production build* (`vite build` + `vite preview`, see
  // playwright.prod-tti.config.ts / `npm run e2e:prod-tti`). Against this
  // config's `vite dev` server it would measure an unrelated, unbundled
  // module-loading pattern instead -- excluded here so the default
  // `npm run e2e` stays representative and fast.
  testIgnore: "ux_perf_01_time_to_interactive.spec.ts",
  timeout: 30_000,
  retries: 0,
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "on-first-retry",
  },
  webServer: {
    command: "node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4173",
    port: 4173,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
