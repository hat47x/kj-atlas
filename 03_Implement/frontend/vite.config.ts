import { defineConfig } from "vitest/config";

export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
