import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
  proxy: {
    '/chat': 'http://localhost:8000',
    '/notes': 'http://localhost:8000',
    '/learning-plan': 'http://localhost:8000',
    '/integrations': 'http://localhost:8000'
  },
},
});
