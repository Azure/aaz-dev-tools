import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/CLI': 'http://127.0.0.1:5000',
      '/AAZ': 'http://127.0.0.1:5000',
      '/Swagger': 'http://127.0.0.1:5000',
    }
  },
  build: {
    outDir: '../aaz_dev/ui',
  },
  plugins: [react()],
})
