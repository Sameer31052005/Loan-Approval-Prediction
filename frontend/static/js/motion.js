(() => {
  const story = document.querySelector('.scroll-story');
  if (!story) return;
  const stage = story.querySelector('.story-stage');
  const scenes = [...story.querySelectorAll('.story-scene')];
  const dots = [...story.querySelectorAll('[data-slide]')];
  const next = document.querySelector('#next-scene');
  const progressBar = story.querySelector('.story-progress > span');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const narrow = matchMedia('(max-width: 620px)');
  let active = 0, scheduled = false;
  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
  function render() {
    scheduled = false;
    if (reduced.matches) return;
    const rect = story.getBoundingClientRect();
    const travel = story.offsetHeight - stage.offsetHeight;
    const top = narrow.matches ? 6 : 12;
    const progress = clamp((top - rect.top) / Math.max(travel, 1), 0, 1);
    // Leave a short reading plateau at each end of the scroll sequence.
    const position = clamp((progress - .08) / .84, 0, 1) * (scenes.length - 1);
    active = Math.round(position);
    scenes.forEach((scene, index) => {
      const distance = index - position;
      const magnitude = Math.abs(distance);
      const visible = magnitude < 1;
      scene.style.visibility = visible ? 'visible' : 'hidden';
      scene.style.opacity = String(clamp(1 - magnitude * 1.4, 0, 1));
      scene.style.transform = reduced.matches ? 'none' :
        'translate3d(0,' + (distance * (narrow.matches ? 65 : 95)) + 'px,' + (-magnitude * 220) +
        'px) rotateX(' + (-distance * (narrow.matches ? 7 : 13)) + 'deg) scale(' + (1 - magnitude * .08) + ')';
      scene.inert = index !== active;
      scene.setAttribute('aria-hidden', String(index !== active));
      scene.style.pointerEvents = index === active ? 'auto' : 'none';
    });
    dots.forEach((dot, i) => dot.setAttribute('aria-pressed', String(i === active)));
    next.textContent = active === scenes.length - 1 ? 'Start assessment ↗' : 'Next scene ↗';
    progressBar.style.transform = 'scaleX(' + progress + ')';
  }
  function schedule() {
    if (!scheduled) { scheduled = true; requestAnimationFrame(render); }
  }
  function goTo(index) {
    if (index >= scenes.length) {
      document.querySelector('#workspace').scrollIntoView({behavior: reduced.matches ? 'auto' : 'smooth'});
      return;
    }
    if (reduced.matches) { scenes[index].scrollIntoView({behavior:'auto'}); return; }
    const travel = story.offsetHeight - stage.offsetHeight;
    const fraction = .08 + index / (scenes.length - 1) * .84;
    window.scrollTo({top: window.scrollY + story.getBoundingClientRect().top - (narrow.matches ? 6 : 12) + travel * fraction, behavior:'smooth'});
  }
  function configure() {
    document.documentElement.classList.toggle('motion-enabled', !reduced.matches);
    if (reduced.matches) {
      scenes.forEach(scene => {scene.removeAttribute('style');scene.inert=false;scene.removeAttribute('aria-hidden');});
    } else schedule();
  }
  dots.forEach(dot => dot.addEventListener('click', () => goTo(Number(dot.dataset.slide))));
  next.addEventListener('click', () => goTo(active + 1));
  window.addEventListener('scroll', schedule, {passive:true});
  window.addEventListener('resize', schedule, {passive:true});
  reduced.addEventListener('change', configure);
  configure();
})();

