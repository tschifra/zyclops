(() => {
  'use strict';
  const data = JSON.parse(document.querySelector('#vault-data').textContent);
  const assets = new Map(data.assets.map(asset => [asset.id, asset]));
  const cards = [...document.querySelectorAll('.card')];
  const filters = [...document.querySelectorAll('.filter')];
  const search = document.querySelector('#search');
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#empty');
  const dialog = document.querySelector('#preview');
  const toast = document.querySelector('#toast');
  let category = 'all';
  let currentId = null;
  let toastTimer;
  let previousFocus;

  function notify(message) {
    clearTimeout(toastTimer);
    if (dialog.open) { document.querySelector('#preview-status').textContent = message; return; }
    toast.textContent = message;
    toast.hidden = false;
    toastTimer = setTimeout(() => { toast.hidden = true; }, 3200);
  }

  function applyFilter() {
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const matches = (category === 'all' || card.dataset.collection === category)
        && (!query || card.dataset.search.includes(query));
      card.hidden = !matches;
      if (matches) visible++;
    });
    count.textContent = `${visible} ${visible === 1 ? 'file' : 'files'}${query || category !== 'all' ? ' found' : ' ready to share'}`;
    empty.hidden = visible !== 0;
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
  }

  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    applyFilter();
  }));
  search.addEventListener('input', applyFilter);
  document.querySelector('#reset').addEventListener('click', () => {
    category = 'all'; search.value = ''; applyFilter(); search.focus();
  });

  async function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const field = document.createElement('textarea');
        field.value = text;
        field.setAttribute('aria-label', 'Caption to copy');
        field.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
        (dialog.open ? dialog : document.body).append(field);
        field.select();
        const copied = document.execCommand('copy');
        field.remove();
        if (!copied) throw new Error('Clipboard unavailable');
      }
      notify('Caption copied. Make it everyone’s problem.');
    } catch {
      notify('Copy unavailable here. Select the caption text to copy it.');
    }
  }

  function visibleIds() { return cards.filter(card => !card.hidden).map(card => card.dataset.id); }

  function showAsset(id) {
    const asset = assets.get(id);
    if (!asset) return;
    currentId = id;
    document.querySelector('#preview-status').textContent = '';
    toast.hidden = true;
    const image = document.querySelector('#preview-image');
    image.src = asset.path;
    image.alt = asset.alt_text;
    document.querySelector('#preview-title').textContent = asset.title;
    document.querySelector('#preview-category').textContent = asset.collection;
    document.querySelector('#preview-caption').textContent = asset.captions[0];
    const download = document.querySelector('#preview-download');
    download.href = asset.path;
    download.download = asset.path.split('/').pop();
    download.textContent = `Download ${asset.mime_type === 'image/png' ? 'PNG' : 'JPG'} ↗`;
    document.querySelector('#preview-details').textContent = `${asset.width} × ${asset.height} · ${(asset.bytes / 1000000).toFixed(2)} MB${asset.has_alpha ? ' · transparent background' : ''}`;
    const ids = visibleIds();
    const index = ids.indexOf(id);
    document.querySelector('#preview-position').textContent = `${index + 1} / ${ids.length}`;
    document.querySelector('#previous').disabled = index <= 0;
    document.querySelector('#next').disabled = index >= ids.length - 1;
    if (!dialog.open) {
      previousFocus = document.activeElement;
      dialog.showModal();
      document.body.style.overflow = 'hidden';
    }
  }

  function navigate(direction) {
    const ids = visibleIds();
    const id = ids[ids.indexOf(currentId) + direction];
    if (id) showAsset(id);
  }

  document.querySelector('#gallery-grid').addEventListener('click', event => {
    const copy = event.target.closest('[data-copy]');
    if (copy) {
      const asset = assets.get(copy.dataset.copy);
      if (asset) copyText(asset.captions[0]);
      return;
    }
    const link = event.target.closest('[data-preview]');
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || typeof dialog.showModal !== 'function') return;
    event.preventDefault();
    showAsset(link.dataset.preview);
  });
  document.querySelector('#close-preview').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = '';
    if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
  });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); navigate(-1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); navigate(1); }
  });
  document.querySelector('#previous').addEventListener('click', () => navigate(-1));
  document.querySelector('#next').addEventListener('click', () => navigate(1));
  document.querySelector('#preview-copy').addEventListener('click', () => {
    const asset = assets.get(currentId);
    if (asset) copyText(asset.captions[0]);
  });
  document.querySelectorAll('[data-copy]').forEach(button => { button.hidden = false; });
  document.querySelector('#controls').hidden = false;
  applyFilter();
})();
