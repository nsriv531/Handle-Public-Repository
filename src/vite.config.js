import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  publicDir: false,
  base: '/static/dist/',
  root: resolve(__dirname, 'app/static'),
  build: {
    manifest: true,
    outDir: 'dist',
    rollupOptions: {
      input: {
        app: resolve(__dirname, 'app/static/js/app.js'),
      }
    },
  },
  server: {
    port: 3000,
    hmr: {
      port: 8080
    }
  }
})
