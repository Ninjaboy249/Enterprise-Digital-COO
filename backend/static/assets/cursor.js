import { canAnimate, getRuntimeState } from './performance.js';

export function installCursorFollower(options = {}) {
  const state = getRuntimeState();
  if (state.coarsePointer || state.reducedMotion || document.querySelector('.premium-cursor')) return null;
  const cursor = document.createElement('div');
  cursor.className = 'premium-cursor';
  cursor.setAttribute('aria-hidden', 'true');
  document.body.appendChild(cursor);
  let frameId = 0;
  let x = -100;
  let y = -100;

  const render = () => {
    frameId = 0;
    if (canAnimate({ allowCoarsePointer: false })) {
      cursor.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    }
  };
  const onMove = event => {
    x = event.clientX;
    y = event.clientY;
    if (!frameId) frameId = requestAnimationFrame(render);
  };
  const onOver = event => {
    cursor.classList.toggle('is-interactive', Boolean(event.target.closest(options.interactive || 'a,button,input,textarea,select')));
  };
  document.addEventListener('pointermove', onMove, { passive: true });
  document.addEventListener('pointerover', onOver, { passive: true });

  return () => {
    cancelAnimationFrame(frameId);
    document.removeEventListener('pointermove', onMove);
    document.removeEventListener('pointerover', onOver);
    cursor.remove();
  };
}
