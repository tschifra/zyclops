(() => {
  'use strict';
  const root = document.documentElement;
  root.classList.add('js');
  document.getElementById('year').textContent = String(new Date().getFullYear());
  const nav = document.getElementById('site-nav');
  const navButton = document.getElementById('nav-toggle');
  navButton.hidden = false;
  function closeMenu(focus = false) {
    nav.classList.remove('open');
    navButton.setAttribute('aria-expanded', 'false');
    navButton.setAttribute('aria-label', 'Open menu');
    if (focus) navButton.focus();
  }
  navButton.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    navButton.setAttribute('aria-expanded', String(open));
    navButton.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.classList.contains('open')) closeMenu(true);
  });
  document.addEventListener('click', event => {
    if (!nav.contains(event.target) && !navButton.contains(event.target)) closeMenu();
  });
  window.matchMedia('(min-width: 901px)').addEventListener('change', event => { if (event.matches) closeMenu(); });
  const motionButton = document.getElementById('motion-toggle');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let motion;
  try { motion = localStorage.getItem('zyclops-motion'); } catch { /* Session preference still works. */ }
  let motionEnabled = !reducedMotion.matches && motion !== 'off';
  function applyMotion() {
    root.dataset.motion = motionEnabled ? 'on' : 'off';
    motionButton.textContent = motionEnabled ? 'Motion on' : 'Motion off';
    motionButton.setAttribute('aria-pressed', String(motionEnabled));
    motionButton.setAttribute('aria-label', motionEnabled ? 'Pause animations' : 'Enable animations');
  }
  motionButton.hidden = false;
  motionButton.addEventListener('click', () => {
    motionEnabled = !motionEnabled && !reducedMotion.matches;
    try { localStorage.setItem('zyclops-motion', motionEnabled ? 'on' : 'off'); } catch { /* Optional storage. */ }
    applyMotion();
  });
  reducedMotion.addEventListener('change', () => { motionEnabled = !reducedMotion.matches; applyMotion(); });
  document.addEventListener('visibilitychange', () => { root.dataset.pageHidden = String(document.hidden); });
  applyMotion();
  const dialog = document.getElementById('meme-dialog');
  const status = document.getElementById('copy-status');
  const dialogStatus = document.getElementById('dialog-status');
  let toastTimer;
  function notify(message) {
    clearTimeout(toastTimer);
    if (dialog.open) { dialogStatus.textContent = message; return; }
    status.textContent = message;
    status.hidden = false;
    toastTimer = setTimeout(() => { status.hidden = true; }, 3500);
  }
  async function copy(text, label, selectable) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(text);
      notify(label + ' copied.');
    } catch {
      if (selectable) {
        const range = document.createRange();
        range.selectNodeContents(selectable);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        selectable.focus();
      }
      notify('Select the ' + label.toLowerCase() + ' and use your device’s Copy action.');
    }
  }
  document.querySelectorAll('[data-copy-target]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      const target = document.getElementById(button.dataset.copyTarget);
      copy(target.textContent.trim(), button.dataset.copyLabel, target);
    });
  });
  let lastArtworkLink;
  document.querySelectorAll('.meme-open').forEach(link => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || typeof dialog.showModal !== 'function') return;
    event.preventDefault();
    lastArtworkLink = link;
    document.getElementById('dialog-image').src = link.href;
    document.getElementById('dialog-image').alt = link.querySelector('img').alt;
    document.getElementById('dialog-title').textContent = link.dataset.title;
    document.getElementById('dialog-caption').textContent = link.dataset.caption;
    const download = document.getElementById('dialog-download');
    download.href = link.href;
    download.download = new URL(link.href).pathname.split('/').pop();
    dialogStatus.textContent = '';
    status.hidden = true;
    dialog.showModal();
    document.body.classList.add('modal-open');
  }));
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('modal-open');
    lastArtworkLink?.focus({preventScroll:true});
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  document.getElementById('copy-caption').addEventListener('click', () => {
    const caption = document.getElementById('dialog-caption');
    copy(caption.textContent, 'Caption', caption);
  });
  const test = document.getElementById('vision-test');
  const surprise = document.getElementById('vision-surprise');
  const verdict = document.getElementById('vision-verdict');
  const portrait = document.getElementById('vision-image');
  const outcomes = [
    ['confused', 'Vision: questionable. Confidence: absolute.'],
    ['unimpressed', 'He has reviewed the situation. He would like a coffee.'],
    ['delighted', 'A brilliant thought. It has already left.'],
    ['panicked', 'The eye has seen enough.'],
    ['sleepy', 'Still looking. Spiritually buffering.'],
    ['smug', 'He knew the answer. Allegedly.'],
  ];
  let outcomeIndex = 0;
  test.hidden = surprise.hidden = false;
  test.addEventListener('click', () => {
    const [emotion, text] = outcomes[outcomeIndex++ % outcomes.length];
    portrait.src = `assets/reactions/${emotion}-v11.webp`;
    portrait.alt = `The one-eyed ZYCLOPS mascot looks ${emotion}.`;
    verdict.textContent = text;
    test.textContent = 'Test again ↗';
  });
  surprise.addEventListener('click', () => {
    portrait.src = 'assets/reactions/panicked-v11.webp';
    portrait.alt = 'ZYCLOPS looks panicked, with his hands against his cheeks.';
    verdict.textContent = 'He was not expecting that. Neither was the eye.';
  });
})();
