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
    .matchMedia("(min-width: 901px)")
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
