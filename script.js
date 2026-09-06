const nav = document.getElementById("site-nav");
const toggle = document.getElementById("nav-toggle");
const iris = document.getElementById("iris");
const year = document.getElementById("year");
const copyBtn = document.getElementById("copy-id");
const marketId = document.getElementById("market-id");

if (year) year.textContent = String(new Date().getFullYear());

if (toggle && nav) {
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  });
  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open menu");
    });
  });
}

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (iris && !reduceMotion) {
  window.addEventListener(
    "pointermove",
    (event) => {
      const rect = iris.parentElement.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = Math.max(-1, Math.min(1, (event.clientX - cx) / 80));
      const dy = Math.max(-1, Math.min(1, (event.clientY - cy) / 80));
      iris.style.transform = `translate(${dx * 6}px, ${dy * 4}px)`;
    },
    { passive: true }
  );
}

if (copyBtn && marketId) {
  copyBtn.addEventListener("click", async () => {
    const id = marketId.textContent.trim();
    try {
      await navigator.clipboard.writeText(id);
      copyBtn.textContent = "Copied";
    } catch {
      copyBtn.textContent = "Select & copy";
    }
    window.setTimeout(() => {
      copyBtn.textContent = "Copy id";
    }, 1600);
  });
}
