import { createRafLoop, getRuntimeState } from './performance.js';

export function createParticleField(canvas, options = {}) {
  const context = canvas?.getContext('2d', { alpha: true });
  if (!context) return null;

  const settings = {
    density: 28000,
    maxParticles: 54,
    mobileMaxParticles: 24,
    speed: 0.018,
    color: '99, 102, 241',
    ...options,
  };
  let width = 0;
  let height = 0;
  let particles = [];

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    width = canvas.clientWidth || window.innerWidth;
    height = canvas.clientHeight || window.innerHeight;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    const state = getRuntimeState();
    const limit = state.coarsePointer ? settings.mobileMaxParticles : settings.maxParticles;
    const count = Math.min(limit, Math.max(10, Math.round(width * height / settings.density)));
    particles = Array.from({ length: count }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      depth: 0.35 + Math.random() * 0.65,
      drift: (Math.random() - 0.5) * settings.speed,
    }));
  }

  const loop = createRafLoop((time, delta) => {
    context.clearRect(0, 0, width, height);
    particles.forEach(particle => {
      particle.y -= delta * settings.speed * particle.depth;
      particle.x += delta * particle.drift;
      if (particle.y < -4) particle.y = height + 4;
      if (particle.x < -4) particle.x = width + 4;
      if (particle.x > width + 4) particle.x = -4;
      const pulse = 0.35 + Math.sin(time * 0.001 + particle.x) * 0.12;
      context.beginPath();
      context.fillStyle = `rgba(${settings.color}, ${pulse * particle.depth})`;
      context.arc(particle.x, particle.y, 0.6 + particle.depth, 0, Math.PI * 2);
      context.fill();
    });
  });

  const observer = new ResizeObserver(resize);
  observer.observe(canvas);
  resize();

  return {
    start: () => loop.start(),
    stop: () => loop.stop(),
    destroy() {
      loop.stop();
      observer.disconnect();
      context.clearRect(0, 0, width, height);
    },
  };
}
