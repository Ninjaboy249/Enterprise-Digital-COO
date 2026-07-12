export function installAmbientLighting(container, options = {}) {
  if (!container || container.querySelector(':scope > .ambient-light-layer')) return null;
  const layer = document.createElement('div');
  layer.className = 'ambient-light-layer';
  layer.setAttribute('aria-hidden', 'true');
  layer.style.setProperty('--light-primary', options.primary || '124 58 237');
  layer.style.setProperty('--light-secondary', options.secondary || '34 211 238');
  container.prepend(layer);
  return layer;
}

export function updatePointerLight(element, clientX, clientY) {
  if (!element) return;
  const rect = element.getBoundingClientRect();
  element.style.setProperty('--light-x', `${clientX - rect.left}px`);
  element.style.setProperty('--light-y', `${clientY - rect.top}px`);
}
