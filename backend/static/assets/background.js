import { createParticleField } from './particles.js';

export function createBackgroundEngine(options = {}) {
  if (document.querySelector('.ambient-background')) return null;
  const canvas = document.createElement('canvas');
  canvas.className = 'ambient-background';
  canvas.setAttribute('aria-hidden', 'true');
  canvas.tabIndex = -1;
  (options.parent || document.body).prepend(canvas);
  const particles = createParticleField(canvas, options.particles);

  return {
    element: canvas,
    start: () => particles?.start(),
    stop: () => particles?.stop(),
    destroy() {
      particles?.destroy();
      canvas.remove();
    },
  };
}
