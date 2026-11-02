/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Forward API calls to the Django dev server so the browser sees one origin
    // (no CORS setup needed). The Host header must stay as-is so it matches the
    // browser's Origin header, which Django's CSRF check compares against.
    // Use the object form: Vite's string shorthand turns on changeOrigin, which
    // rewrites Host and makes every POST fail with 403.
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: false },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
