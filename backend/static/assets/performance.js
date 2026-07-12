const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
const coarsePointerQuery = window.matchMedia('(pointer: coarse)');

const runtimeState = {
  reducedMotion: reducedMotionQuery.matches,
  coarsePointer: coarsePointerQuery.matches,
  visible: !document.hidden,
};

const visibilitySubscribers = new Set();

function syncRootState() {
  const root = document.documentElement;
  root.classList.toggle('motion-reduced', runtimeState.reducedMotion);
  root.classList.toggle('pointer-coarse', runtimeState.coarsePointer);
  root.classList.toggle('page-hidden', !runtimeState.visible);
}

function notifyVisibility() {
  visibilitySubscribers.forEach(callback => callback(runtimeState.visible));
}

export function getRuntimeState() {
  return { ...runtimeState };
}

export function canAnimate({ allowCoarsePointer = true } = {}) {
  return runtimeState.visible && !runtimeState.reducedMotion &&
    (allowCoarsePointer || !runtimeState.coarsePointer);
}

export function onVisibilityChange(callback) {
  visibilitySubscribers.add(callback);
  return () => visibilitySubscribers.delete(callback);
}

export function createRafLoop(render, options = {}) {
  const { allowCoarsePointer = true } = options;
  let frameId = 0;
  let running = false;
  let previousTime = 0;

  const frame = time => {
    if (!running) return;
    if (canAnimate({ allowCoarsePointer })) {
      render(time, previousTime ? Math.min(time - previousTime, 50) : 0);
      previousTime = time;
    }
    frameId = requestAnimationFrame(frame);
  };

  return {
    start() {
      if (running || runtimeState.reducedMotion) return;
      running = true;
      frameId = requestAnimationFrame(frame);
    },
    stop() {
      running = false;
      previousTime = 0;
      cancelAnimationFrame(frameId);
    },
    get running() {
      return running;
    },
  };
}

export function initPerformanceRuntime() {
  if (document.documentElement.dataset.motionRuntime === 'ready') return;
  document.documentElement.dataset.motionRuntime = 'ready';
  document.documentElement.classList.add('motion-runtime');
  syncRootState();

  reducedMotionQuery.addEventListener('change', event => {
    runtimeState.reducedMotion = event.matches;
    syncRootState();
  });
  coarsePointerQuery.addEventListener('change', event => {
    runtimeState.coarsePointer = event.matches;
    syncRootState();
  });
  document.addEventListener('visibilitychange', () => {
    runtimeState.visible = !document.hidden;
    syncRootState();
    notifyVisibility();
  });
}
