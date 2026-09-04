import { defineConfig } from "vitest/config";

export default defineConfig({
  envPrefix: "KJ_ATLAS_",
  build: {
    rollupOptions: {
      input: {
        app: "index.html",
        admin: "admin.html",
      },
    },
  },
  server: {
    proxy: {
      "/api": {
        // Use 127.0.0.1 (not localhost) so the dev proxy matches the documented
        // backend bind (uvicorn --host 127.0.0.1) and avoids IPv6 (::1) resolution
        // failures on hosts where localhost resolves to ::1 first (e.g. Windows).
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/session": {
        // Keep the BFF surface outside /api. OAuth redirect/cookie contracts use
        // /session/* as-is, so this proxy must not rewrite the path.
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
