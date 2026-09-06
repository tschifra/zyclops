# ZYCLOPS — $ZYCL

One eye. Zero visibility. A cyclops memecoin on Zcash.

Live site: [zyclops.xyz](https://zyclops.xyz/)

## Local

```bash
python3 -m http.server 4173
```

Open [http://localhost:4173](http://localhost:4173).

## Links

- Site: https://zyclops.xyz/
- Market: https://shld.fun/coin?a=2b3e27cd7b740a48a9036e20be3c40a8a814cc6e59c237a3db03203a6a398994
- X: https://x.com/ZYCLOPSzec
- Telegram: https://t.me/zyclopszec
- Stickers: `assets/zyclops-sticker-pack.zip` (16 × 512px PNG)

## Design and artwork

- Character-led black/gold design with a responsive layout and concise ZYCLOPS voice.
- Four-step buying guide, official market ID copy control, and SHLD privacy context.
- Meme viewer with keyboard dismissal, captions and full-size downloads.
- Sticker-pack download plus all 16 individual PNGs.
- Optimized WebP delivery images, lazy loading, reduced-motion support and accessible navigation.
- New archive illustration and its generation brief: [assets/ARTWORK.md](assets/ARTWORK.md).

This is a static site with no build dependencies. Serve the repository using the local command above. Publishing uses the existing hosting setup.

## Motion and animated stickers

- Hero portrait parallax and breathing, rotating gold orbit, drifting sparks and metallic headline shimmer.
- A scrolling brand strip that fills wide screens, gentle archive-image parallax, community rings, section reveals and hover feedback.
- Soft animated lighting on the hero, a restrained pointer tilt on meme artwork, and short menu and artwork-viewer entrance transitions. All respect the motion controls.
- Interactive SVG eye: pointer-following gaze, a blink control and a playful vision test with five rotating character responses.
- Scroll progress and active section navigation; mobile menu includes the motion control.
- The navigation motion control pauses page effects and videos, and remembers the visitor's choice.
- Reduced-motion preferences default to still content. Individual video controls allow intentional playback.
- Video previews load and play only when visible, pause off-screen or in a hidden tab, and use still posters otherwise.
- Ambient loops pause outside the viewport or in a hidden tab. Eye-test controls remain usable with reduced motion, and any active test completes when motion is paused.
- No animation framework or new runtime dependency. Navigation and downloads work without JavaScript.
- Three Telegram video stickers: [download ZIP](assets/zyclops-animated-stickers.zip). Each is 512 × 512, 3 seconds, 24 fps, transparent VP9 WEBM, no audio and below 256 KB. The pack still needs publishing through @Stickers.
- [Source artwork, animation method and generation prompt](assets/animated/ARTWORK.md).
- To regenerate: install Python's Pillow, NumPy and SciPy, plus ffmpeg/ffprobe, then run `python3 scripts/render-animated-stickers.py`. On systems without macOS Impact, set `ZYCLOPS_STICKER_FONT` to a suitable installed bold display font. The site itself has no Python dependency.
