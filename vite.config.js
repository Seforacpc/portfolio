import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  base: "/", // ⚠️ IMPORTANT → site à la racine

  plugins: [react()],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },

  server: {
    proxy: {
      "/api": "http://localhost:3001",
    },
  },

  build: {
    outDir: "dist",
    assetsDir: "assets",
  },
});
