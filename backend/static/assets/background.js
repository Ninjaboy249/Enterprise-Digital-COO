import { createParticleField } from './particles.js';
import { canAnimate, onVisibilityChange } from './performance.js';

export function createBackgroundEngine(options = {}) {
  if (document.querySelector('.ambient-atmosphere')) return null;
  const layer = document.createElement('div');
  layer.className = 'ambient-atmosphere';
  layer.setAttribute('aria-hidden', 'true');
  layer.style.setProperty('--atmosphere-primary', (options.primary || '99 102 241').replaceAll(',', ' '));
  layer.style.setProperty('--atmosphere-secondary', (options.secondary || '34 211 238').replaceAll(',', ' '));
  layer.style.setProperty('--atmosphere-accent', options.accent || '124 58 237');
  const canvas = document.createElement('canvas');
  canvas.className = 'ambient-background';
  canvas.setAttribute('aria-hidden', 'true');
  canvas.tabIndex = -1;
  const light = document.createElement('span');
  light.className = 'ambient-atmosphere__light';
  const beam = document.createElement('span');
  beam.className = 'ambient-atmosphere__beam';
  layer.append(canvas, light, beam);
  (options.parent || document.body).prepend(layer);
  document.querySelectorAll('body > header, body > main, body > footer, body > .min-h-screen, body > .max-w-7xl, #dashboard-main, .deck-shell')
    .forEach(element => element.classList.add('atmosphere-content'));
  const particles = createParticleField(canvas, {
    color: options.primary || '99, 102, 241',
    linkColor: options.secondary || '34, 211, 238',
    ...options.particles,
  });

  let pointerFrame = 0;
  const onPointerMove = event => {
    if (pointerFrame || !canAnimate({ allowCoarsePointer: false })) return;
    pointerFrame = requestAnimationFrame(() => {
      layer.style.setProperty('--atmosphere-x', `${event.clientX / window.innerWidth * 100}%`);
      layer.style.setProperty('--atmosphere-y', `${event.clientY / window.innerHeight * 100}%`);
      pointerFrame = 0;
    });
  };
  window.addEventListener('pointermove', onPointerMove, { passive: true });
  const unsubscribeVisibility = onVisibilityChange(visible => {
    if (visible && canAnimate()) particles?.start();
    else particles?.stop();
  });

  return {
    element: canvas,
    start: () => particles?.start(),
    stop: () => particles?.stop(),
    destroy() {
      particles?.destroy();
      unsubscribeVisibility();
      cancelAnimationFrame(pointerFrame);
      window.removeEventListener('pointermove', onPointerMove);
      layer.remove();
    },
  };
}
