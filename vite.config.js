import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {
      "/api/summarize": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
      },

      "/api/health": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },

      "/api/similarity": {
        target: "http://127.0.0.1:8002",
        changeOrigin: true,
      },

      "/api/quiz": {
        target: "http://127.0.0.1:8003",
        changeOrigin: true,
      },

      "/api/research": {
        target: "http://127.0.0.1:8004",
        changeOrigin: true,
      },
    },
  },
});
