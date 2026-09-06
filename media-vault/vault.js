const grid = document.getElementById("asset-grid");
const search = document.getElementById("search");
const collection = document.getElementById("collection");
const count = document.getElementById("result-count");
const loading = document.getElementById("load-state");
const toast = document.getElementById("toast");
let library;
let toastTimer;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function notice(message) {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.hidden = false;
  toastTimer = setTimeout(() => {
    toast.hidden = true;
  }, 3000);
}

async function copy(text, message) {
  try {
    await navigator.clipboard.writeText(text);
    notice(message);
  } catch {
    notice(
      "Copy is unavailable in this browser. Open the manifest to select the text.",
    );
  }
}

function card(asset) {
  const item = el("article", "asset");
  const media = el("div", "media");
  const link = el("a");
  link.href = asset.path;
  link.target = "_blank";
  link.rel = "noopener";
  link.setAttribute("aria-label", `Open ${asset.title}`);
  const img = el("img");
  img.src = asset.thumbnail_path;
  img.alt = asset.alt_text;
  img.loading = "lazy";
  img.width = 480;
  img.height = 480;
  link.append(img);
  media.append(link);

  const meta = el("div", "asset-meta");
  meta.append(
    el("span", "", "JPG / SQUARE"),
    el("span", "", `${asset.width} × ${asset.height}`),
  );
  const actions = el("div", "asset-actions");
  const download = el("a", "", "Download ↓");
  download.href = asset.path;
  download.download = asset.path.split("/").pop();
  const url = el("button", "", "Copy URL");
  url.type = "button";
  url.addEventListener("click", () => copy(asset.url, "File URL copied."));
  const caption = el("button", "", "Copy caption");
  caption.type = "button";
  caption.addEventListener("click", () =>
    copy(asset.captions[0], "Caption copied."),
  );
  actions.append(download, url, caption);
  item.append(
    media,
    meta,
    el("h2", "", asset.title),
    el("p", "caption", asset.captions[0]),
    actions,
    el("p", "tags", asset.tags.map((t) => "#" + t).join("  ")),
  );
  return item;
}

function render() {
  const query = search.value.trim().toLowerCase();
  const assets = library.assets.filter(
    (a) =>
      (collection.value === "all" || collection.value === a.collection) &&
      (!query ||
        [a.title, a.id, ...a.tags, ...a.captions]
          .join(" ")
          .toLowerCase()
          .includes(query)),
  );
  grid.replaceChildren(...assets.map(card));
  count.textContent = `${assets.length} / ${library.assets.length} pictures`;
  if (!assets.length)
    grid.append(
      el("p", "empty", "Nothing in this drawer. Try another reaction."),
    );
}

search.addEventListener("input", () => {
  if (library) render();
});
collection.addEventListener("change", () => {
  if (library) render();
});
document
  .querySelector(".filters")
  .addEventListener("submit", (event) => event.preventDefault());
fetch("manifest.json")
  .then((response) => {
    if (!response.ok) throw new Error("Manifest unavailable");
    return response.json();
  })
  .then((data) => {
    if (
      !Array.isArray(data.assets) ||
      data.assets.some((a) => a.media_type !== "image")
    )
      throw new Error("Invalid still-image manifest");
    library = data;
    loading.hidden = true;
    document.getElementById("library-count").textContent =
      `${data.assets.length} pictures`;
    render();
  })
  .catch(() => {
    loading.textContent =
      "The vault could not load. Try refreshing, or download the collection above.";
  });
