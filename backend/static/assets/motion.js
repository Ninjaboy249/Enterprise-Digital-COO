import { initPerformanceRuntime } from './performance.js';

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
