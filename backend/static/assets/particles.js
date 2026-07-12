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
    linkColor: '99, 102, 241',
    linkDistance: 118,
    linkOpacity: 0.1,
    pointerParallax: 8,
    ...options,
  };
  let width = 0;
  let height = 0;
  let particles = [];
  let pointerX = 0;
  let pointerY = 0;
  let targetPointerX = 0;
  let targetPointerY = 0;

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
    pointerX += (targetPointerX - pointerX) * 0.035;
    pointerY += (targetPointerY - pointerY) * 0.035;
    particles.forEach((particle, index) => {
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

      for (let otherIndex = index + 1; otherIndex < particles.length; otherIndex += 1) {
        const other = particles[otherIndex];
        const dx = particle.x - other.x;
        const dy = particle.y - other.y;
        const distanceSquared = dx * dx + dy * dy;
        if (distanceSquared > settings.linkDistance * settings.linkDistance) continue;
        const distance = Math.sqrt(distanceSquared);
        context.beginPath();
        context.strokeStyle = `rgba(${settings.linkColor}, ${(1 - distance / settings.linkDistance) * settings.linkOpacity})`;
        context.lineWidth = 0.65;
        context.moveTo(
          particle.x + pointerX * particle.depth * settings.pointerParallax,
          particle.y + pointerY * particle.depth * settings.pointerParallax,
        );
        context.lineTo(
          other.x + pointerX * other.depth * settings.pointerParallax,
          other.y + pointerY * other.depth * settings.pointerParallax,
        );
        context.stroke();
      }
    });
  });

  const onPointerMove = event => {
    targetPointerX = event.clientX / Math.max(window.innerWidth, 1) - 0.5;
    targetPointerY = event.clientY / Math.max(window.innerHeight, 1) - 0.5;
  };

  const observer = new ResizeObserver(resize);
  observer.observe(canvas);
  window.addEventListener('pointermove', onPointerMove, { passive: true });
  resize();

  return {
    start: () => loop.start(),
    stop: () => loop.stop(),
    destroy() {
      loop.stop();
      observer.disconnect();
      window.removeEventListener('pointermove', onPointerMove);
      context.clearRect(0, 0, width, height);
    },
  };
}
