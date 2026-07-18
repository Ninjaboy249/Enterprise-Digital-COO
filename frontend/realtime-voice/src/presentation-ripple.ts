import * as THREE from 'three';
import gsap from 'gsap';
import './presentation-ripple.css';

const vertexShader = `
  varying vec2 vUv;
  void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }
`;

const fragmentShader = `
  uniform sampler2D uCurrent;
  uniform sampler2D uNext;
  uniform float uProgress;
  uniform float uAspect;
  varying vec2 vUv;
  void main(){
    vec2 p=vUv-0.5;
    p.x*=uAspect;
    float dist=length(p);
    float front=uProgress*1.25;
    float trail=dist-front;
    float wave=sin(trail*72.0)*exp(-abs(trail)*22.0);
    vec2 dir=normalize(p+vec2(0.0001));
    vec2 displaced=vUv+dir*wave*0.018;
    float blend=smoothstep(0.055,-0.025,trail);
    vec4 color=mix(texture2D(uCurrent,displaced),texture2D(uNext,displaced),blend);
    color.rgb+=abs(wave)*0.22;
    gl_FragColor=color;
  }
`;

type Slide = { title: string; kicker: string; image: string };

const slides: Slide[] = [
  { title: 'Enterprise Digital COO', kicker: 'AI command centre', image: '/static/assets/animated-footer-middle.png' },
  { title: 'Decisions at the speed of data', kicker: 'Executive intelligence', image: '/static/assets/edcoo-logo.svg' },
  { title: 'From signals to action', kicker: 'Nine-page guided story', image: '/static/assets/animated-footer-middle.png' },
];

const root = document.querySelector<HTMLElement>('[data-ripple-presentation]');

if (root) {
  const canvas = root.querySelector<HTMLCanvasElement>('canvas');
  const title = root.querySelector<HTMLElement>('[data-ripple-title]');
  const kicker = root.querySelector<HTMLElement>('[data-ripple-kicker]');
  const status = root.querySelector<HTMLElement>('[data-ripple-status]');

  if (canvas && title && kicker && status) {
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-.5, .5, .5, -.5, .01, 10);
    camera.position.z = 1;
    const loader = new THREE.TextureLoader();
    loader.setCrossOrigin('anonymous');
    const textures = slides.map(slide => {
      const texture = loader.load(slide.image);
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.minFilter = THREE.LinearFilter;
      texture.magFilter = THREE.LinearFilter;
      return texture;
    });
    const material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        uCurrent: { value: textures[0] },
        uNext: { value: textures[1] },
        uProgress: { value: 0 },
        uAspect: { value: 1 },
      },
    });
    const geometry = new THREE.PlaneGeometry(1, 1);
    scene.add(new THREE.Mesh(geometry, material));

    let current = 0;
    let changing = false;
    let autoTimer = 0;
    let running = false;

    const splitTitle = (value: string) => {
      title.innerHTML = '';
      Array.from(value).forEach(character => {
        const mask = document.createElement('span');
        mask.className = 'ripple-char-mask';
        const char = document.createElement('span');
        char.className = 'ripple-char';
        char.textContent = character === ' ' ? '\u00a0' : character;
        mask.appendChild(char);
        title.appendChild(mask);
      });
    };

    const showCopy = (index: number) => {
      splitTitle(slides[index].title);
      kicker.textContent = slides[index].kicker;
      status.textContent = `${String(index + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
      gsap.fromTo(title.querySelectorAll('.ripple-char'), { yPercent: 115 }, { yPercent: 0, duration: .7, stagger: .018, ease: 'power3.out' });
      gsap.fromTo([kicker, status], { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: .6, stagger: .08, ease: 'power2.out' });
    };

    const schedule = () => {
      clearTimeout(autoTimer);
      if (running) autoTimer = window.setTimeout(next, 4800);
    };

    const next = () => {
      if (changing) return;
      changing = true;
      const nextIndex = (current + 1) % slides.length;
      material.uniforms.uNext.value = textures[nextIndex];
      gsap.to([title, kicker, status], { opacity: 0, y: -18, duration: .25, ease: 'power2.in' });
      gsap.fromTo(material.uniforms.uProgress, { value: 0 }, {
        value: 1,
        duration: 1.15,
        ease: 'power2.inOut',
        onComplete: () => {
          current = nextIndex;
          material.uniforms.uCurrent.value = textures[current];
          material.uniforms.uProgress.value = 0;
          gsap.set([title, kicker, status], { opacity: 1, y: 0 });
          showCopy(current);
          changing = false;
          schedule();
        },
      });
    };

    const resize = () => {
      const width = root.clientWidth;
      const height = root.clientHeight;
      renderer.setSize(width, height, false);
      material.uniforms.uAspect.value = width / Math.max(height, 1);
    };
    resize();
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(root);
    const render = () => renderer.render(scene, camera);
    gsap.ticker.add(render);
    showCopy(0);

    const visibilityObserver = new IntersectionObserver(([entry]) => {
      running = entry.isIntersecting;
      if (running) schedule(); else clearTimeout(autoTimer);
    }, { threshold: .2 });
    visibilityObserver.observe(root);
    root.addEventListener('click', next);
    root.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); next(); }
    });

    window.addEventListener('pagehide', () => {
      clearTimeout(autoTimer);
      visibilityObserver.disconnect();
      resizeObserver.disconnect();
      gsap.ticker.remove(render);
      textures.forEach(texture => texture.dispose());
      geometry.dispose(); material.dispose(); renderer.dispose();
    }, { once: true });
  }
}

const deckSlides = Array.from(document.querySelectorAll<HTMLElement>('.slide-page'));
if (deckSlides.length) {
  const pagerLinks = Array.from(document.querySelectorAll<HTMLAnchorElement>('.pager a'));
  let activeSlide = Math.max(0, deckSlides.findIndex(slide => `#${slide.id}` === location.hash));
  let deckChanging = false;
  const controls = document.createElement('nav');
  controls.className = 'deck-nav';
  controls.setAttribute('aria-label', 'Presentation controls');
  controls.innerHTML = '<button type="button" data-deck-prev aria-label="Previous slide">←</button><span data-deck-count></span><button type="button" data-deck-next aria-label="Next slide">→</button>';
  document.body.appendChild(controls);
  const count = controls.querySelector<HTMLElement>('[data-deck-count]')!;

  const updateState = (index: number) => {
    deckSlides.forEach((slide, slideIndex) => {
      const active = slideIndex === index;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
    });
    pagerLinks.forEach((link, linkIndex) => {
      link.classList.toggle('is-active', linkIndex === index);
      if (linkIndex === index) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
    });
    count.textContent = `${String(index + 1).padStart(2, '0')} / ${String(deckSlides.length).padStart(2, '0')}`;
    history.replaceState(null, '', `#${deckSlides[index].id}`);
  };

  const showSlide = (requested: number, direction = 1) => {
    if (deckChanging) return;
    const nextIndex = (requested + deckSlides.length) % deckSlides.length;
    if (nextIndex === activeSlide) return;
    deckChanging = true;
    const outgoing = deckSlides[activeSlide];
    const incoming = deckSlides[nextIndex];
    incoming.classList.add('is-active');
    incoming.style.zIndex = '2';
    incoming.setAttribute('aria-hidden', 'false');
    gsap.set(incoming, { opacity: 1, clipPath: `circle(0% at ${direction > 0 ? '82%' : '18%'} 50%)` });
    gsap.to(outgoing, { opacity: 0, scale: .975, duration: .48, ease: 'power2.inOut' });
    gsap.to(incoming, {
      clipPath: `circle(150% at ${direction > 0 ? '82%' : '18%'} 50%)`, duration: .85, ease: 'power3.inOut',
      onComplete: () => {
        outgoing.classList.remove('is-active');
        gsap.set(outgoing, { opacity: 0, scale: 1, clearProps: 'zIndex' });
        incoming.style.zIndex = '';
        activeSlide = nextIndex;
        updateState(activeSlide);
        deckChanging = false;
      },
    });
    gsap.fromTo(incoming.querySelectorAll('.slide-copy > *, .shot, .stack-wrap, .ripple-stage'),
      { y: 34 * direction, opacity: 0 },
      { y: 0, opacity: 1, duration: .72, stagger: .055, delay: .18, ease: 'power3.out' });
  };

  updateState(activeSlide);
  controls.querySelector('[data-deck-prev]')?.addEventListener('click', () => showSlide(activeSlide - 1, -1));
  controls.querySelector('[data-deck-next]')?.addEventListener('click', () => showSlide(activeSlide + 1, 1));
  pagerLinks.forEach((link, index) => link.addEventListener('click', event => {
    event.preventDefault(); showSlide(index, index >= activeSlide ? 1 : -1);
  }));
  window.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'PageDown') showSlide(activeSlide + 1, 1);
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') showSlide(activeSlide - 1, -1);
  });
  let wheelLocked = false;
  window.addEventListener('wheel', event => {
    if (wheelLocked || Math.abs(event.deltaY) < 20) return;
    wheelLocked = true;
    const direction = event.deltaY > 0 ? 1 : -1;
    showSlide(activeSlide + direction, direction);
    window.setTimeout(() => { wheelLocked = false; }, 950);
  }, { passive: true });
  let touchX = 0;
  window.addEventListener('touchstart', event => { touchX = event.touches[0]?.clientX || 0; }, { passive: true });
  window.addEventListener('touchend', event => {
    const delta = (event.changedTouches[0]?.clientX || 0) - touchX;
    if (Math.abs(delta) > 45) showSlide(activeSlide + (delta < 0 ? 1 : -1), delta < 0 ? 1 : -1);
  }, { passive: true });
}
