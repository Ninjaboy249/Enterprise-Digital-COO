export function applyGlassSurface(elements, variant = 'default') {
  const targets = typeof elements === 'string' ? document.querySelectorAll(elements) : elements;
  Array.from(targets || []).forEach(element => {
    element.classList.add('premium-glass', `premium-glass--${variant}`);
  });
}

export function removeGlassSurface(elements) {
  const targets = typeof elements === 'string' ? document.querySelectorAll(elements) : elements;
  Array.from(targets || []).forEach(element => {
    [...element.classList]
      .filter(className => className === 'premium-glass' || className.startsWith('premium-glass--'))
      .forEach(className => element.classList.remove(className));
  });
}
