export function getResolvedTheme() {
  const selected = document.documentElement.dataset.theme || 'auto';
  if (selected !== 'auto') return selected;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function onThemeEffectChange(callback) {
  const colorQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const observer = new MutationObserver(() => callback(getResolvedTheme()));
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  const onColorChange = () => callback(getResolvedTheme());
  colorQuery.addEventListener('change', onColorChange);
  callback(getResolvedTheme());

  return () => {
    observer.disconnect();
    colorQuery.removeEventListener('change', onColorChange);
  };
}

export function setEffectPalette(element, palette) {
  if (!element || !palette) return;
  Object.entries(palette).forEach(([name, value]) => {
    element.style.setProperty(`--effect-${name}`, value);
  });
}
