import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api": {
        target: "http://backend:5000",
        changeOrigin: true,
      },
    },
    sourcemap: true,  // Włącz source maps tylko w dev
  },
  build: {
    sourcemap: false,  // WYŁĄCZ source maps na produkcji
    minify: "terser",
    terserOptions: {
      compress: {
        drop_console: true,  // Usuń console.log w prod
      },
    },
  },
});