import { initPerformanceRuntime } from './performance.js';
import { createBackgroundEngine } from './background.js';

export { createBackgroundEngine } from './background.js';
export { applyGlassSurface, removeGlassSurface } from './glass.js';
export { installAmbientLighting, updatePointerLight } from './lighting.js';
export { createParticleField } from './particles.js';
export { installTilt } from './tilt.js';
export { installCursorFollower } from './cursor.js';
export { getResolvedTheme, onThemeEffectChange, setEffectPalette } from './theme-effects.js';
export {
  canAnimate,
  createRafLoop,
  getRuntimeState,
  initPerformanceRuntime,
  onVisibilityChange,
} from './performance.js';

initPerformanceRuntime();

function resolveAtmospherePalette() {
  const path = window.location.pathname;
  if (path.endsWith('/finance.html') || path.endsWith('/excel-analysis.html')) {
    return { primary: '16, 185, 129', secondary: '34, 211, 238', accent: '5 150 105' };
  }
  if (path.endsWith('/operations.html')) {
    return { primary: '139, 92, 246', secondary: '34, 211, 238', accent: '109 40 217' };
  }
  if (path.endsWith('/reports.html')) {
    return { primary: '59, 130, 246', secondary: '34, 211, 238', accent: '30 58 138' };
  }
  return { primary: '99, 102, 241', secondary: '34, 211, 238', accent: '124 58 237' };
}

function initAtmosphere() {
  const engine = createBackgroundEngine(resolveAtmospherePalette());
  engine?.start();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAtmosphere, { once: true });
} else {
  initAtmosphere();
}
