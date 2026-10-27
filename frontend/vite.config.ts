import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // In sviluppo (`npm run dev`) le chiamate /api vanno al backend in Docker
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
