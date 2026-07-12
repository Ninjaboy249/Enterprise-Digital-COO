import { canAnimate } from './performance.js';

export function installTilt(elements, options = {}) {
  const targets = typeof elements === 'string' ? document.querySelectorAll(elements) : elements;
  const maxTilt = options.maxTilt ?? 4;
  const cleanups = [];

  Array.from(targets || []).forEach(element => {
    if (element.dataset.tiltReady === 'true') return;
    element.dataset.tiltReady = 'true';

    const onMove = event => {
      if (!canAnimate({ allowCoarsePointer: false })) return;
      const rect = element.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width;
      const y = (event.clientY - rect.top) / rect.height;
      element.style.setProperty('--tilt-x', `${(0.5 - y) * maxTilt}deg`);
      element.style.setProperty('--tilt-y', `${(x - 0.5) * maxTilt}deg`);
      element.style.setProperty('--pointer-x', `${x * 100}%`);
      element.style.setProperty('--pointer-y', `${y * 100}%`);
    };
    const reset = () => {
      element.style.setProperty('--tilt-x', '0deg');
      element.style.setProperty('--tilt-y', '0deg');
    };
    element.addEventListener('pointermove', onMove, { passive: true });
    element.addEventListener('pointerleave', reset, { passive: true });
    cleanups.push(() => {
      element.removeEventListener('pointermove', onMove);
      element.removeEventListener('pointerleave', reset);
      delete element.dataset.tiltReady;
      reset();
    });
  });

  return () => cleanups.forEach(cleanup => cleanup());
}
