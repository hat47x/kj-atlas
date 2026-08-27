import { defineConfig } from "@playwright/test";

// UX-PERF-01: measures Time-to-Interactive against the production build
// output (`vite build` -> `dist/`), served by `vite preview` -- not the dev
// server `playwright.config.ts` uses. Bundle size/parse cost only shows up
// in a real production build; `vite dev` serves unbundled ES modules and
// would make any main-chunk-size measurement meaningless.
//
// This config does not build `dist/` itself (Playwright's webServer only
// starts a server, it does not run a build step first). Run `npm run
// e2e:prod-tti`, which chains `vite build` then this config, or run
// `npm run build` yourself before `npx playwright test --config=playwright.prod-tti.config.ts`.
export default defineConfig({
  testDir: "./e2e",
  testMatch: "ux_perf_01_time_to_interactive.spec.ts",
  timeout: 30_000,
  retries: 0,
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:4175",
    trace: "on-first-retry",
  },
  webServer: {
    command: "node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 4175 --strictPort",
    port: 4175,
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
