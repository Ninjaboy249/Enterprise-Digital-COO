import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: resolve(__dirname, '../../backend/static/assets/realtime-voice'),
    emptyOutDir: true,
    lib: {
      entry: resolve(__dirname, 'src/main.tsx'),
      formats: ['es'],
      fileName: () => 'realtime-voice.js',
    },
    cssCodeSplit: false,
    rollupOptions: { output: { assetFileNames: 'realtime-voice.css' } },
  },
});
