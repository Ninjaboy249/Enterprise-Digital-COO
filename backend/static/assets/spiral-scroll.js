(function () {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let items = [];
  let ticking = false;

  function collect() {
    const root = document.getElementById('dashboard-main');
    if (!root) return;
    root.classList.add('spiral-scroll-stage');
    items = Array.from(root.children).filter(item => item.id !== 'ask-enterprise-coo');
    items.forEach(item => item.classList.add('spiral-scroll-item'));
    render();
  }

  function render() {
    ticking = false;
    if (reduceMotion.matches || window.innerWidth < 720) {
      items.forEach(item => item.style.removeProperty('--spiral-transform'));
      return;
    }
    const center = window.innerHeight / 2;
    items.forEach((item, index) => {
      const rect = item.getBoundingClientRect();
      const distance = Math.max(-1, Math.min(1, (rect.top + rect.height / 2 - center) / center));
      const angle = distance * 8;
      const x = Math.sin(distance * Math.PI) * 34;
      const z = -Math.abs(distance) * 95;
      const scale = 1 - Math.abs(distance) * .035;
      item.style.setProperty('--spiral-transform', `translate3d(${x}px,0,${z}px) rotateY(${angle}deg) rotateZ(${angle * .12}deg) scale(${scale})`);
      item.style.zIndex = String(100 - Math.round(Math.abs(distance) * 10) - index);
    });
  }

  function schedule() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(render);
  }

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  reduceMotion.addEventListener?.('change', schedule);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', collect);
  else collect();
}());
