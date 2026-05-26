import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev: run FastAPI separately (e.g. uvicorn on 8000). See website/README.md.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
