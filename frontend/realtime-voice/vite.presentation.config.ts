import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  build: {
    outDir: resolve(__dirname, '../../backend/static/assets/presentation-ripple'),
    emptyOutDir: true,
    lib: {
      entry: resolve(__dirname, 'src/presentation-ripple.ts'),
      formats: ['es'],
      fileName: () => 'presentation-ripple.js',
    },
    cssCodeSplit: false,
    rollupOptions: { output: { assetFileNames: 'presentation-ripple.css' } },
  },
});
