/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import topLevelAwait from "vite-plugin-top-level-await";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), topLevelAwait()],
  test: {
    globals: true,
    environment: "happy-dom",
    setupFiles: ["./src/test-setup.ts"],
    css: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/**",
        "src/test-setup.ts",
        "src/**/*.test.{ts,tsx}",
        "src/**/__tests__/**",
        "dist/**",
        "build/**",
      ],
    },
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      "/CLI": "http://127.0.0.1:5000",
      "/AAZ": "http://127.0.0.1:5000",
      "/Swagger": "http://127.0.0.1:5000",
      "/assets/typespec": "http://127.0.0.1:5000",
    },
  },
  build: {
    outDir: "dist",
  },
});
