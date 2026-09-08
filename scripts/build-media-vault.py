#!/usr/bin/env python3
"""Validate the current still-image inventory and build its gallery and ZIP."""
import argparse
from collections import Counter
import csv
import hashlib
import html
import json
from pathlib import Path
import re
import zipfile
from PIL import Image


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault', type=Path, default=root / 'media-vault')
    parser.add_argument('--template', type=Path, default=root / 'scripts/media-vault-template.html')
    args = parser.parse_args()
    vault = args.vault.resolve()
    manifest = json.loads((vault / 'manifest.json').read_text())
    assets = manifest['assets']
    ids = [asset['id'] for asset in assets]
    assert assets and len(ids) == len(set(ids)), 'Empty inventory or duplicate IDs'
    assert not set(ids).intersection(manifest.get('retired_asset_ids', [])), 'Retired IDs in current inventory'
    assert manifest['counts']['images'] == len(assets)
    assert manifest['counts']['videos'] == manifest['counts']['loops'] == manifest['counts']['webp_alternates'] == 0
    category_counts = Counter(asset['collection'] for asset in assets)
    category_names = {'meme':'Memes','reaction':'Reactions','artwork':'Artwork','banner':'Banners','brand':'Brand'}
    expected_counts = {'meme':'memes','reaction':'reactions','artwork':'artwork','banner':'banners','brand':'brand'}
    for category, key in expected_counts.items():
        assert manifest['counts'][key] == category_counts[category], category

    bundle_name = f"zyclops-media-pack-v{manifest['pack_version']}.zip"
    paths = {'manifest.json','catalog.csv','BOT-README.md','index.html','vault.css','vault.js','meta/prompts.json','meta/ARTWORK.md','meta/CHARACTER-PROMPT.md'}
    hashes = set()
    for asset in assets:
        assert asset['media_type'] == 'image'
        assert asset['mime_type'] in ('image/jpeg','image/png')
        assert not asset.get('alternates') and not asset.get('animation_type')
        assert asset['collection'] in category_names
        assert asset['captions'] and asset['alt_text'] and asset['tags']
        assert all(len(caption) <= 280 for caption in asset['captions']), asset['id']
        assert re.fullmatch(r'[a-z0-9-]+',asset['id']), asset['id']
        for key in ('path','thumbnail_path'):
            relative = Path(asset[key])
            assert not relative.is_absolute() and '..' not in relative.parts
            assert (vault / relative).is_file(), relative
            paths.add(str(relative))
        data = (vault / asset['path']).read_bytes()
        assert len(data) == asset['bytes'] and len(data) < 2_000_000, asset['id']
        digest = hashlib.sha256(data).hexdigest()
        assert digest == asset['sha256'], asset['id']
        assert digest not in hashes, f"Duplicate file content: {asset['id']}"
        hashes.add(digest)
        with Image.open(vault / asset['path']) as image:
            assert image.size == (asset['width'],asset['height'])
            assert getattr(image,'n_frames',1) == 1
            assert Image.MIME[image.format] == asset['mime_type']
            if asset.get('has_alpha'):
                assert 'A' in image.getbands()
                alpha = image.getchannel('A')
                assert alpha.getextrema() == (0,255), 'Expected genuine transparency'
                assert alpha.getpixel((0,0)) == 0
        assert asset['url'] == 'https://zyclops.xyz/media-vault/' + asset['path']

    fields = ['id','creative_id','title','collection','release','style_version','media_type','mime_type','url','width','height','bytes','sha256','caption','alt_text','tags']
    with (vault / 'catalog.csv').open('w',newline='') as file:
        writer = csv.DictWriter(file,fieldnames=fields,lineterminator='\n')
        writer.writeheader()
        for asset in assets:
            row = {key:asset.get(key,'') for key in fields}
            row.update(caption=asset['captions'][0],tags='|'.join(asset['tags']))
            writer.writerow(row)

    escape = html.escape
    cards = []
    for index, asset in enumerate(assets,1):
        search = ' '.join([asset['title'],asset['captions'][0],*asset['tags']]).lower()
        filetype = 'PNG' if asset['mime_type'] == 'image/png' else 'JPG'
        cards.append(f'''<article class="card" data-id="{escape(asset['id'])}" data-collection="{escape(asset['collection'])}" data-search="{escape(search,quote=True)}">
  <a class="card-art" href="{escape(asset['path'])}" data-preview="{escape(asset['id'])}" aria-label="Preview {escape(asset['title'],quote=True)}"><img src="{escape(asset['thumbnail_path'])}" width="{asset['width']}" height="{asset['height']}" alt="{escape(asset['alt_text'],quote=True)}" loading="lazy" decoding="async"><span class="preview-tag" aria-hidden="true">OPEN FILE ↗</span></a>
  <div class="card-body"><div class="card-meta"><span>{escape(category_names[asset['collection']])} / {index:03}</span><span>{asset['width']} × {asset['height']} · {filetype}</span></div><h3>{escape(asset['title'])}</h3><p class="card-caption">{escape(asset['captions'][0])}</p><div class="card-actions"><a href="{escape(asset['path'])}" download="{escape(Path(asset['path']).name)}" aria-label="Download {escape(asset['title'],quote=True)}">Download {filetype} ↘</a><button type="button" data-copy="{escape(asset['id'])}" aria-label="Copy caption for {escape(asset['title'],quote=True)}" hidden>Copy caption ⧉</button></div></div>
</article>''')
    filters = [f'<button class="filter" type="button" data-filter="all" aria-pressed="true">All files <span>{len(assets)}</span></button>']
    for category, label in category_names.items():
        if category_counts[category]:
            filters.append(f'<button class="filter" type="button" data-filter="{category}" aria-pressed="false">{label} <span>{category_counts[category]}</span></button>')
    inline = json.dumps({'assets':assets},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    page = args.template.read_text().replace('@@TOTAL@@',str(len(assets))).replace('@@CARDS@@','\n'.join(cards)).replace('@@FILTERS@@','\n'.join(filters)).replace('@@DATA@@',inline)
    assert '@@' not in page, 'Unreplaced template placeholders'
    (vault / 'index.html').write_text(page)

    actual = {str(file.relative_to(vault)) for file in vault.rglob('*') if file.is_file() and file.name != '.DS_Store'}
    expected = paths | {bundle_name}
    assert not (actual - expected), f"Unlisted or retired files remain: {sorted(actual - expected)}"
    assert not (paths - actual), f"Missing bundle inputs: {sorted(paths - actual)}"
    with zipfile.ZipFile(vault / bundle_name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for relative in sorted(paths):
            archive.write(vault / relative,'media-vault/' + relative)
    with zipfile.ZipFile(vault / bundle_name) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(paths)
        assert json.loads(archive.read('media-vault/manifest.json')) == manifest
    print(f"Validated {len(assets)} assets: {dict(category_counts)}. ZIP {(vault / bundle_name).stat().st_size:,} bytes. No retired files or animations.")


if __name__ == '__main__':
    main()
