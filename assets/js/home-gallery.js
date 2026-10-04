(() => {
  const gallery = document.querySelector("#profile-gallery");
  const profile = document.querySelector(".quarto-about-trestles .about-entity");
  const title = profile?.querySelector("#title-block-header");
  if (!gallery || !profile || !title) return;

  title.insertAdjacentElement("afterend", gallery);

  const track = gallery.querySelector(".profile-gallery-track");
  const slides = [...gallery.querySelectorAll(".profile-gallery-slide")];
  const status = gallery.querySelector("[data-gallery-status]");
  const pauseButton = gallery.querySelector("[data-gallery-toggle]");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let active = 0;
  let timer;
  let paused = reducedMotion.matches;

  function render() {
    track.style.transform = `translateX(-${active * 100}%)`;
    slides.forEach((slide, index) => {
      slide.setAttribute("aria-hidden", String(index !== active));
      const video = slide.querySelector("video");
      if (!video) return;
      if (index === active && !paused && !reducedMotion.matches) {
        video.play().catch(() => {});
      } else {
        video.pause();
      }
    });
    status.textContent = `${active + 1} / ${slides.length}`;
  }

  function stop() {
    window.clearInterval(timer);
    timer = undefined;
  }

  function start() {
    stop();
    if (paused || document.hidden || reducedMotion.matches) return;
    timer = window.setInterval(() => {
      active = (active + 1) % slides.length;
      render();
    }, 6500);
    render();
  }

  gallery.querySelector("[data-gallery-previous]").addEventListener("click", () => {
    active = (active - 1 + slides.length) % slides.length;
    render();
    if (!paused) start();
  });

  gallery.querySelector("[data-gallery-next]").addEventListener("click", () => {
    active = (active + 1) % slides.length;
    render();
    if (!paused) start();
  });

  pauseButton.addEventListener("click", () => {
    paused = !paused;
    pauseButton.textContent = paused ? "Play" : "Pause";
    pauseButton.setAttribute("aria-pressed", String(paused));
    if (paused) {
      stop();
      render();
    } else {
      start();
    }
  });

  gallery.addEventListener("pointerenter", stop);
  gallery.addEventListener("pointerleave", start);
  gallery.addEventListener("focusin", stop);
  gallery.addEventListener("focusout", (event) => {
    if (!gallery.contains(event.relatedTarget)) start();
  });
  document.addEventListener("visibilitychange", start);
  reducedMotion.addEventListener("change", (event) => {
    if (event.matches) paused = true;
    pauseButton.textContent = paused ? "Play" : "Pause";
    pauseButton.setAttribute("aria-pressed", String(paused));
    start();
  });

  render();
  start();
})();
