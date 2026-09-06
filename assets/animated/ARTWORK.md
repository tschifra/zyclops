# Animated ZYCLOPS stickers

- GM and This is fine use the existing original PNG sticker artwork.
- PUMP source: `pump-source.png`, created using the built-in image-generation tool. No CLI/API fallback was used.
- Character identity references: `../stickers/02-gm.png` and `../stickers/07-fine.png`.
- The three loops use local 2D deformation and compositing, not generated video. GM has a waving hand; PUMP has raised fists, a small eye pulse and gold sparkles; This is fine has flickering flames and drifting steam.
- `../../scripts/render-animated-stickers.py` renders the loops with premultiplied-alpha sampling and encodes them using ffmpeg. Its export checks cover codec, dimensions, frame rate, duration, file size and decoded transparency.
- Download files: `gm.webm`, `pump.webm`, `fine.webm`; bundle: `../zyclops-animated-stickers.zip`.
- `*-preview.webm` are separate opaque previews matching the site's dark panel color. `*.webp` are still posters. Original sources are retained.

## Final generation prompt

Use case: stylized-concept. Asset type: transparent Telegram sticker artwork, animation-ready source.
Create ONE new ZYCLOPS "PUMP" reaction sticker matching the two supplied reference stickers exactly in character identity and art direction. References are style/identity reference only, not edit targets. Geometric angular black and metallic gold bearded cyclops, exactly ONE luminous golden eye, sculpted faceted gold outlines, bold white cutout border. Black hood/shirt, no second eye.
Subject: upper-body cyclops looking exhilarated yet comically over-serious, huge wide-open single eye, mouth subtly delighted, both clenched gold/black fists held up close to his shoulders in celebration. Front-facing, symmetrical, readable as tiny emoji. Eye center in upper half, forehead and beard uncluttered. Clear separation of fists and face. The one eye has a clean round black pupil and bright gold iris.
Composition: centered single standalone sticker, full bust visible, generous transparent margin all around. Exactly square image. TRUE TRANSPARENT background with alpha, no checkerboard, no scenery, no floor, no separate objects, no chart, no arrows, no letters, no caption. Keep all hair, fists and white border within frame. Same bold 3D vector-like finish as references, no complex grain or tiny detail. No text or watermark.
