document.documentElement.classList.add("js");

const nav = document.getElementById("site-nav");
const toggle = document.getElementById("nav-toggle");
const year = document.getElementById("year");
const copyButton = document.getElementById("copy-id");
const marketId = document.getElementById("market-id");
const copyStatus = document.getElementById("copy-status");
const dialog = document.getElementById("meme-dialog");
let lastArtworkLink = null;
let copyTimer;

if (year) year.textContent = String(new Date().getFullYear());

function closeMenu(returnFocus = false) {
  if (!nav || !toggle) return;
  nav.classList.remove("open");
  toggle.setAttribute("aria-expanded", "false");
  toggle.setAttribute("aria-label", "Open menu");
  if (returnFocus) toggle.focus();
}

if (toggle && nav) {
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  });
  nav
    .querySelectorAll("a")
    .forEach((link) => link.addEventListener("click", () => closeMenu()));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.classList.contains("open"))
      closeMenu(true);
  });
  document.addEventListener("click", (event) => {
    if (!nav.contains(event.target) && !toggle.contains(event.target))
      closeMenu();
  });
  window
    .matchMedia("(min-width: 1001px)")
    .addEventListener("change", (event) => {
      if (event.matches) closeMenu();
    });
}

if (copyButton && marketId && copyStatus) {
  copyButton.addEventListener("click", async () => {
    window.clearTimeout(copyTimer);
    try {
      if (!navigator.clipboard?.writeText)
        throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(marketId.textContent.trim());
      copyButton.textContent = "Copied ✓";
      copyStatus.textContent = "Official market ID copied.";
    } catch {
      const range = document.createRange();
      range.selectNodeContents(marketId);
      marketId.focus();
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      copyStatus.textContent =
        "Market ID selected. Use your device’s Copy action.";
    }
    copyTimer = window.setTimeout(() => {
      copyButton.textContent = "Copy market ID ⧉";
    }, 2200);
  });
}

if (dialog && typeof dialog.showModal === "function") {
  const image = document.getElementById("dialog-image");
  const title = document.getElementById("dialog-title");
  const caption = document.getElementById("dialog-caption");
  const download = document.getElementById("dialog-download");
  document.querySelectorAll(".meme-open").forEach((link) => {
    link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)
        return;
      event.preventDefault();
      lastArtworkLink = link;
      image.src = link.href;
      image.alt = link.querySelector("img").alt;
      title.textContent = link.dataset.title;
      caption.textContent = link.dataset.caption;
      download.href = link.href;
      download.download = `zyclops-${link.dataset.title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}.jpg`;
      dialog.showModal();
      document.body.classList.add("modal-open");
    });
  });
  dialog
    .querySelector(".dialog-close")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    const bounds = dialog.getBoundingClientRect();
    if (
      event.target === dialog &&
      (event.clientX < bounds.left ||
        event.clientX > bounds.right ||
        event.clientY < bounds.top ||
        event.clientY > bounds.bottom)
    )
      dialog.close();
  });
  dialog.addEventListener("close", () => {
    document.body.classList.remove("modal-open");
    lastArtworkLink?.focus({ preventScroll: true });
  });
}

// Motion is progressive: the page stays readable without JavaScript.
const root = document.documentElement;
const motionButton = document.getElementById("motion-toggle");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
const videos = [...document.querySelectorAll(".sticker-video")];
const visibleVideos = new Set();
const manuallyPaused = new Set();
let motionPreference = null;
try {
  motionPreference = localStorage.getItem("zyclops-motion");
} catch {
  /* Storage can be disabled. */
}
let motionEnabled =
  motionPreference === "on" ||
  (motionPreference !== "off" && !reducedMotion.matches);
let revealObserver;

function refreshVideoButton(video) {
  const button = video.parentElement.querySelector(".sticker-play");
  const playing = !video.paused && !video.ended;
  button.setAttribute(
    "aria-label",
    `${playing ? "Pause" : "Play"} ${video.dataset.name} animation`,
  );
  button.firstElementChild.textContent = playing ? "Ⅱ" : "▶";
}
function loadVideo(video) {
  const source = video.querySelector("source");
  if (!source.hasAttribute("src")) {
    source.src = source.dataset.src;
    video.load();
  }
}
function playVideo(video) {
  loadVideo(video);
  video.play().catch(() => refreshVideoButton(video));
}
function syncVideos() {
  videos.forEach((video) => {
    if (
      motionEnabled &&
      !document.hidden &&
      visibleVideos.has(video) &&
      !manuallyPaused.has(video)
    )
      playVideo(video);
    else video.pause();
  });
}
function revealEverything() {
  document
    .querySelectorAll(".reveal-pending")
    .forEach((el) => el.classList.remove("reveal-pending"));
  revealObserver?.disconnect();
}
function applyMotion() {
  root.dataset.motion = motionEnabled ? "on" : "off";
  root.classList.toggle("page-visible", !document.hidden);
  if (motionButton) {
    motionButton.hidden = false;
    motionButton.setAttribute(
      "aria-label",
      motionEnabled ? "Pause animations" : "Enable animations",
    );
    motionButton.title = motionEnabled
      ? "Pause animations"
      : "Enable animations";
    motionButton.querySelector(".motion-label").textContent = motionEnabled
      ? "Motion on"
      : "Motion off";
  }
  if (!motionEnabled) revealEverything();
  syncVideos();
  document.dispatchEvent(new Event("zyclops:motionchange"));
}
motionButton?.addEventListener("click", () => {
  motionEnabled = !motionEnabled;
  motionPreference = motionEnabled ? "on" : "off";
  try {
    localStorage.setItem("zyclops-motion", motionPreference);
  } catch {
    /* Keep the current-session choice. */
  }
  applyMotion();
});
reducedMotion.addEventListener("change", () => {
  motionPreference = null;
  try {
    localStorage.removeItem("zyclops-motion");
  } catch {
    /* OS preference still applies. */
  }
  motionEnabled = !reducedMotion.matches;
  applyMotion();
});
document.addEventListener("visibilitychange", () => {
  root.classList.toggle("page-visible", !document.hidden);
  syncVideos();
});

videos.forEach((video) => {
  video.muted = true;
  const button = video.parentElement.querySelector(".sticker-play");
  button.hidden = false;
  video.addEventListener("play", () => refreshVideoButton(video));
  video.addEventListener("pause", () => refreshVideoButton(video));
  video.addEventListener("error", () => refreshVideoButton(video));
  button.addEventListener("click", () => {
    if (video.paused) {
      manuallyPaused.delete(video);
      playVideo(video);
    } else {
      manuallyPaused.add(video);
      video.pause();
    }
  });
});
if ("IntersectionObserver" in window) {
  const videoObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) visibleVideos.add(entry.target);
        else visibleVideos.delete(entry.target);
      });
      syncVideos();
    },
    { threshold: 0.15 },
  );
  videos.forEach((video) => videoObserver.observe(video));

  const hero = document.querySelector(".hero");
  const heroObserver = new IntersectionObserver((entries) => {
    root.classList.toggle("hero-visible", entries[0].isIntersecting);
  });
  if (hero) heroObserver.observe(hero);

  if (motionEnabled) {
    revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.remove("reveal-pending");
          revealObserver.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -36px 0px", threshold: 0.02 },
    );
    document
      .querySelectorAll(
        ".section-meta, .dossier-heading, .archive-scene, .character-notes > *, .buy-intro, .buy-steps > li, .market-card, .section-heading-row, .meme-card, .vault-card, .sticker-pack, .animated-heading, .animated-card, .vision-copy, .vision-instrument, .community-inner > *",
      )
      .forEach((el, index) => {
        el.classList.add("reveal");
        el.style.setProperty("--reveal-delay", `${(index % 3) * 55}ms`);
        if (el.getBoundingClientRect().top > window.innerHeight) {
          el.classList.add("reveal-pending");
          revealObserver.observe(el);
        }
      });
    // Keyboard navigation must never focus invisible content.
    document.addEventListener("focusin", (event) => {
      const pending = event.target.closest(".reveal-pending");
      if (pending) {
        pending.classList.remove("reveal-pending");
        revealObserver.unobserve(pending);
      }
    });
  }
}

// Pointer highlights and a small artwork tilt are reserved for a mouse.
const resetArtworkPointers = [];
document.querySelectorAll(".meme-open, .sticker-stage").forEach((card) => {
  let pointerFrame;
  const resetPointer = () => {
    cancelAnimationFrame(pointerFrame);
    card.classList.remove("pointer-active");
    card.style.removeProperty("--tilt-x");
    card.style.removeProperty("--tilt-y");
  };
  resetArtworkPointers.push(resetPointer);
  card.addEventListener("pointermove", (event) => {
    if (!motionEnabled || !finePointer.matches) return;
    cancelAnimationFrame(pointerFrame);
    pointerFrame = requestAnimationFrame(() => {
      const box = card.getBoundingClientRect();
      card.style.setProperty("--pointer-x", `${event.clientX - box.left}px`);
      card.style.setProperty("--pointer-y", `${event.clientY - box.top}px`);
      if (card.matches(".meme-open")) {
        // Use the stationary parent so the tilt cannot chase its own bounds.
        const parent = card.parentElement.getBoundingClientRect();
        const x = Math.max(
          -1,
          Math.min(1, ((event.clientX - parent.left) / parent.width - 0.5) * 2),
        );
        const y = Math.max(
          -1,
          Math.min(
            1,
            ((event.clientY - parent.top) / card.offsetHeight - 0.5) * 2,
          ),
        );
        card.style.setProperty("--tilt-x", `${-y * 3.2}deg`);
        card.style.setProperty("--tilt-y", `${x * 3.2}deg`);
      }
      card.classList.add("pointer-active");
    });
  });
  card.addEventListener("pointerleave", resetPointer);
  card.addEventListener("click", resetPointer);
});
finePointer.addEventListener("change", () => {
  if (!finePointer.matches) resetArtworkPointers.forEach((reset) => reset());
});

// Ambient loops run only while their own section is on screen.
const ambientSections = [...document.querySelectorAll("[data-ambient]")];
if ("IntersectionObserver" in window) {
  const ambientObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) =>
        entry.target.classList.toggle("is-inview", entry.isIntersecting),
      );
    },
    { threshold: 0.04 },
  );
  ambientSections.forEach((section) => ambientObserver.observe(section));
}

const heroArt = document.querySelector(".hero-art");
const heroSection = document.querySelector(".hero");
const archiveScene = document.querySelector(".archive-scene");
const siteHeader = document.querySelector(".site-header");
const mainSections = [...document.querySelectorAll("main > section[id]")];
const navigationLinks = [
  ...document.querySelectorAll('.site-nav a[href^="#"]'),
];
let scrollFrame = 0;
function updateScrollScene() {
  scrollFrame = 0;
  const span = document.documentElement.scrollHeight - innerHeight;
  root.style.setProperty(
    "--reading-progress",
    String(span > 0 ? Math.min(1, Math.max(0, scrollY / span)) : 0),
  );
  siteHeader?.classList.toggle("has-scrolled", scrollY > 24);
  let current = "";
  mainSections.forEach((section) => {
    if (section.getBoundingClientRect().top <= 160) current = section.id;
  });
  if (current === "vision") current = "lore";
  const stickers = document.getElementById("stickers");
  if (current === "memes" && stickers?.getBoundingClientRect().top <= 160)
    current = "stickers";
  navigationLinks.forEach((link) => {
    if (link.hash === `#${current}`)
      link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  });
  if (!motionEnabled) return;
  if (heroArt && heroSection && finePointer.matches) {
    const box = heroSection.getBoundingClientRect();
    if (box.bottom > 0)
      heroArt.style.setProperty(
        "--hero-scroll",
        `${Math.min(28, Math.max(0, -box.top * 0.045))}px`,
      );
  }
  if (archiveScene) {
    const box = archiveScene.getBoundingClientRect();
    if (box.bottom > 0 && box.top < innerHeight) {
      const travel =
        (innerHeight / 2 - (box.top + box.height / 2)) / innerHeight;
      archiveScene.style.setProperty(
        "--archive-shift",
        `${Math.max(-17, Math.min(17, travel * 30))}px`,
      );
    }
  }
}
function requestScrollUpdate() {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScrollScene);
}
window.addEventListener("scroll", requestScrollUpdate, { passive: true });
window.addEventListener("resize", requestScrollUpdate, { passive: true });
window.addEventListener("load", requestScrollUpdate, { once: true });
if ("ResizeObserver" in window)
  new ResizeObserver(requestScrollUpdate).observe(document.body);

let heroPointerFrame = 0;
heroSection?.addEventListener("pointermove", (event) => {
  if (!motionEnabled || !finePointer.matches || !heroArt) return;
  cancelAnimationFrame(heroPointerFrame);
  heroPointerFrame = requestAnimationFrame(() => {
    const box = heroSection.getBoundingClientRect();
    heroArt.style.setProperty(
      "--hero-pan-x",
      `${((event.clientX - box.left - box.width / 2) / box.width) * 14}px`,
    );
    heroArt.style.setProperty(
      "--hero-pan-y",
      `${((event.clientY - box.top - box.height / 2) / box.height) * 10}px`,
    );
  });
});
function resetHeroPointer() {
  cancelAnimationFrame(heroPointerFrame);
  heroArt?.style.setProperty("--hero-pan-x", "0px");
  heroArt?.style.setProperty("--hero-pan-y", "0px");
}
heroSection?.addEventListener("pointerleave", resetHeroPointer);

// A self-contained character joke: this does not access a camera or a wallet.
const visionLab = document.getElementById("vision");
const instrument = document.querySelector(".vision-instrument");
const visionTest = document.getElementById("vision-test");
const visionBlink = document.getElementById("vision-blink");
const visionVerdict = document.getElementById("vision-verdict");
const lensNote = document.getElementById("lens-note");
const rayGroup = document.querySelector(".iris-rays");
let gazeFrame = 0;
let testTimer;
let blinkTimer;
let testBusy = false;
let verdictIndex = 0;
const verdicts = [
  "Vision: questionable. Confidence: absolute.",
  "One eye. Zero useful observations.",
  "He saw the assignment. He ignored it.",
  "Results classified. Mostly out of embarrassment.",
  "Still looking for Zatoshi. Still looking.",
];
if (rayGroup) {
  const lines = document.createDocumentFragment();
  for (let i = 0; i < 72; i++) {
    const angle = (i * Math.PI * 2) / 72;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    const inner = i % 3 === 0 ? 40 : 49;
    line.setAttribute("x1", String(300 + Math.cos(angle) * inner));
    line.setAttribute("y1", String(200 + Math.sin(angle) * inner));
    line.setAttribute("x2", String(300 + Math.cos(angle) * 82));
    line.setAttribute("y2", String(200 + Math.sin(angle) * 82));
    line.setAttribute("stroke-width", i % 3 === 0 ? "1.5" : ".7");
    lines.append(line);
  }
  rayGroup.append(lines);
}
function resetGaze() {
  cancelAnimationFrame(gazeFrame);
  instrument?.style.setProperty("--gaze-x", "0px");
  instrument?.style.setProperty("--gaze-y", "0px");
}
visionLab?.addEventListener("pointermove", (event) => {
  if (!motionEnabled || !finePointer.matches || !instrument) return;
  cancelAnimationFrame(gazeFrame);
  gazeFrame = requestAnimationFrame(() => {
    const box = instrument.getBoundingClientRect();
    const x = Math.max(
      -1,
      Math.min(1, (event.clientX - box.left - box.width / 2) / (box.width / 2)),
    );
    const y = Math.max(
      -1,
      Math.min(
        1,
        (event.clientY - box.top - box.height / 2) / (box.height / 2),
      ),
    );
    instrument.style.setProperty("--gaze-x", `${x * 22}px`);
    instrument.style.setProperty("--gaze-y", `${y * 13}px`);
  });
});
visionLab?.addEventListener("pointerleave", resetGaze);
function finishVisionTest() {
  clearTimeout(testTimer);
  if (!testBusy) return;
  testBusy = false;
  instrument.classList.remove("is-testing");
  visionVerdict.textContent = verdicts[verdictIndex % verdicts.length];
  verdictIndex++;
  lensNote.textContent = "RESULT: BEAUTIFULLY INCONCLUSIVE";
  visionTest.disabled = false;
  visionBlink.disabled = false;
  visionTest.textContent = "Test again ↗";
}
if (visionTest && visionBlink && instrument && visionVerdict && lensNote) {
  visionTest.hidden = false;
  visionBlink.hidden = false;
  visionTest.addEventListener("click", () => {
    if (testBusy) return;
    testBusy = true;
    visionTest.disabled = true;
    visionBlink.disabled = true;
    visionTest.textContent = "Looking…";
    visionVerdict.textContent = "Focusing. This may be optimistic.";
    lensNote.textContent = "ONE MOMENT. HE IS CONCENTRATING.";
    resetGaze();
    if (motionEnabled && !reducedMotion.matches) {
      instrument.classList.add("is-testing");
      testTimer = setTimeout(finishVisionTest, 1300);
    } else finishVisionTest();
  });
  visionBlink.addEventListener("click", () => {
    clearTimeout(blinkTimer);
    visionVerdict.textContent = "That was his version of a wink.";
    lensNote.textContent = "WINK ATTEMPT: TECHNICALLY A BLINK";
    if (!motionEnabled || reducedMotion.matches) return;
    instrument.classList.remove("is-blinking");
    // Restart the brief, user-triggered blink, including repeated taps.
    void instrument.getBoundingClientRect();
    instrument.classList.add("is-blinking");
    blinkTimer = setTimeout(
      () => instrument.classList.remove("is-blinking"),
      400,
    );
  });
}
function syncImmersiveMotion() {
  if (!motionEnabled || document.hidden) {
    resetHeroPointer();
    resetGaze();
    resetArtworkPointers.forEach((reset) => reset());
    clearTimeout(blinkTimer);
    instrument?.classList.remove("is-blinking");
    finishVisionTest();
  }
  requestScrollUpdate();
}
document.addEventListener("zyclops:motionchange", syncImmersiveMotion);
document.addEventListener("visibilitychange", syncImmersiveMotion);
applyMotion();
requestScrollUpdate();
