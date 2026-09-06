const grid = document.getElementById('asset-grid');
const search = document.getElementById('search');
const format = document.getElementById('format');
const count = document.getElementById('result-count');
const loading = document.getElementById('load-state');
const toast = document.getElementById('toast');
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
  toastTimer = setTimeout(() => { toast.hidden = true; }, 3000);
}
async function copy(text, message) {
  try { await navigator.clipboard.writeText(text); notice(message); }
  catch { notice('Copy is unavailable in this browser. Open the manifest to select the text.'); }
}
function card(asset) {
  const item = el('article','asset');
  const media = el('div','media');
  if (asset.media_type === 'video') {
    const video = el('video');
    video.controls = true;
    video.playsInline = true;
    video.loop = true;
    video.muted = true;
    video.preload = 'none';
    video.poster = asset.poster_path;
    video.setAttribute('aria-label',asset.alt_text);
    const source = el('source'); source.src = asset.path; source.type = asset.mime_type;
    video.append(source);
    video.addEventListener('play', () => grid.querySelectorAll('video').forEach(v => { if (v !== video) v.pause(); }));
    media.append(video);
  } else {
    const link = el('a'); link.href = asset.path; link.target = '_blank'; link.rel = 'noopener';
    link.setAttribute('aria-label',`Open ${asset.title}`);
    const img = el('img'); img.src = asset.thumbnail_path; img.alt = asset.alt_text; img.loading = 'lazy'; img.width = 480; img.height = 480;
    link.append(img); media.append(link);
  }
  const meta = el('div','asset-meta');
  meta.append(el('span','',asset.media_type==='video' ? `${asset.duration_seconds}s / MP4` : 'JPG / SQUARE'),el('span','',`${asset.width} × ${asset.height}`));
  const actions = el('div','asset-actions');
  const download = el('a','', 'Download ↓'); download.href = asset.path; download.download = asset.path.split('/').pop();
  const url = el('button','','Copy URL'); url.type = 'button'; url.addEventListener('click',()=>copy(asset.url,'Production file URL copied.'));
  const caption = el('button','','Copy caption'); caption.type = 'button'; caption.addEventListener('click',()=>copy(asset.captions[0],'Caption copied.'));
  actions.append(download,url,caption);
  item.append(media,meta,el('h2','',asset.title),el('p','caption',asset.captions[0]),actions,el('p','tags',asset.tags.map(t=>'#'+t).join('  ')));
  if (asset.media_type==='video') item.append(el('p','motion-note',asset.animation_type==='character_loop'?'Character animation · silent loop':'Motion poster · gentle camera movement'));
  return item;
}
function render() {
  grid.querySelectorAll('video').forEach(v=>v.pause());
  const query = search.value.trim().toLowerCase();
  const assets = library.assets.filter(a => (format.value==='all'||format.value===a.media_type) && (!query||[a.title,a.id,...a.tags,...a.captions].join(' ').toLowerCase().includes(query)));
  grid.replaceChildren(...assets.map(card));
  count.textContent = `${assets.length} / ${library.assets.length} assets`;
  if (!assets.length) grid.append(el('p','empty','Nothing in this drawer. Try another reaction.'));
}
search.addEventListener('input',()=>{if(library)render();});
format.addEventListener('change',()=>{if(library)render();});
document.querySelector('.filters').addEventListener('submit',event=>event.preventDefault());
document.addEventListener('visibilitychange',()=>{if(document.hidden)grid.querySelectorAll('video').forEach(v=>v.pause());});
fetch('manifest.json').then(response=>{if(!response.ok)throw new Error('Manifest unavailable');return response.json();}).then(data=>{
  if (!Array.isArray(data.assets)) throw new Error('Invalid manifest');
  library=data;loading.hidden=true;document.getElementById('library-count').textContent=`${data.assets.length} post assets`;render();
}).catch(()=>{loading.textContent='The vault could not load. Try refreshing, or download the collection above.';});
