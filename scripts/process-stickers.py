#!/usr/bin/env python3
"""Key magenta (or corner-black) backgrounds and emit 512px Telegram stickers."""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(
    "/Users/tbr/.grok/sessions/%2FUsers%2Ftbr%2FDocuments%2FGitHub%2Fzyclop/01a07707-7ae0-75c0-b8d6-fce83d1043f4/images"
)
OUT = ROOT / "assets" / "stickers"
PACK = ROOT / "assets" / "zyclops-sticker-pack.zip"
SIZE = 512

# filename -> (source, emoji, title)
PACK_MAP = [
    ("01-scowl.jpg", ROOT / "assets" / "stickers" / "head.jpg", "😐", "The stare"),
    ("02-gm.jpg", SRC / "13.jpg", "👋", "GM"),
    ("03-diamond.jpg", SRC / "10.jpg", "💎", "Diamond hands"),
    ("04-wagmi.jpg", SRC / "28.jpg", "👍", "WAGMI"),
    ("05-ser.jpg", SRC / "26.jpg", "👉", "Ser"),
    ("06-copium.jpg", SRC / "25.jpg", "😭", "Copium"),
    ("07-fine.jpg", SRC / "15.jpg", "🔥", "This is fine"),
    ("08-shh.jpg", SRC / "11.jpg", "🤫", "Shielded"),
    ("09-laser.jpg", SRC / "12.jpg", "😤", "Laser eye"),
    ("10-ngmi.jpg", SRC / "21.jpg", "🤦", "NGMI"),
    ("11-rekt.jpg", SRC / "23.jpg", "😵", "Rekt"),
    ("12-blink.jpg", SRC / "19.jpg", "😉", "The blink"),
    ("13-peek.jpg", SRC / "22.jpg", "🫣", "Redacted"),
    ("14-based.jpg", SRC / "24.jpg", "😍", "Based"),
    ("15-moon.jpg", SRC / "18.jpg", "🌙", "Wen moon"),
    ("16-hodl.jpg", SRC / "20.jpg", "🗿", "HODL"),
]


def key_magenta(arr: np.ndarray) -> np.ndarray:
    r, g, b = arr[..., 0].astype(np.int16), arr[..., 1].astype(np.int16), arr[..., 2].astype(np.int16)
    magenta = (r > 150) & (b > 150) & (g < 120) & (np.abs(r - b) < 70)
    pink_shadow = (r > 90) & (b > 90) & (g < 90) & ((r + b) / 2 - g > 50)
    arr[..., 3] = np.where(magenta | pink_shadow, 0, arr[..., 3])
    return arr


def flood_black(arr: np.ndarray, limit: int = 28) -> np.ndarray:
    h, w = arr.shape[:2]
    vis = np.zeros((h, w), dtype=bool)
    stack = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    while stack:
        y, x = stack.pop()
        if vis[y, x]:
            continue
        r, g, b, a = arr[y, x]
        if int(r) + int(g) + int(b) > limit * 3:
            continue
        vis[y, x] = True
        arr[y, x, 3] = 0
        if y > 0:
            stack.append((y - 1, x))
        if y + 1 < h:
            stack.append((y + 1, x))
        if x > 0:
            stack.append((y, x - 1))
        if x + 1 < w:
            stack.append((y, x + 1))
    return arr


def tight_512(im: Image.Image) -> Image.Image:
    bbox = im.getbbox()
    if not bbox:
        return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cropped = im.crop(bbox)
    pad = int(max(cropped.size) * 0.06)
    padded = Image.new(
        "RGBA", (cropped.width + pad * 2, cropped.height + pad * 2), (0, 0, 0, 0)
    )
    padded.paste(cropped, (pad, pad), cropped)
    padded.thumbnail((SIZE, SIZE), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas.paste(
        padded, ((SIZE - padded.width) // 2, (SIZE - padded.height) // 2), padded
    )
    return canvas


def process(src: Path, black: bool = False) -> Image.Image:
    im = Image.open(src).convert("RGBA")
    arr = np.array(im)
    arr = flood_black(arr) if black else key_magenta(arr)
    return tight_512(Image.fromarray(arr, "RGBA"))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pngs: list[Path] = []
    manifest = ["# ZYCLOPS sticker pack\n", "| File | Emoji | Title |", "|---|---|---|"]
    for name, src, emoji, title in PACK_MAP:
        png_name = name.replace(".jpg", ".png")
        dest = OUT / png_name
        img = process(src, black=src.name == "head.jpg")
        img.save(dest, "PNG", optimize=True)
        size = dest.stat().st_size
        print(f"{png_name:18} {img.size} {size // 1024}KB {emoji} {title}")
        if size > 512_000:
            img.save(dest, "PNG", optimize=True, compress_level=9)
        pngs.append(dest)
        manifest.append(f"| `{png_name}` | {emoji} | {title} |")

    sheet_w, sheet_h = 4, 4
    tile = 256
    sheet = Image.new("RGBA", (sheet_w * tile, sheet_h * tile), (12, 10, 8, 255))
    for i, png in enumerate(pngs):
        im = Image.open(png).convert("RGBA").resize((tile, tile), Image.Resampling.LANCZOS)
        x, y = (i % sheet_w) * tile, (i // sheet_w) * tile
        sheet.paste(im, (x, y), im)
    sheet.convert("RGB").save(OUT / "pack-sheet.jpg", "JPEG", quality=88)

    with zipfile.ZipFile(PACK, "w", zipfile.ZIP_DEFLATED) as zf:
        for png in pngs:
            zf.write(png, png.name)
        zf.writestr("EMOJI.txt", "\n".join(f"{p.name}\t{e}\t{t}" for p, (_, _, e, t) in zip(pngs, PACK_MAP)))
    (ROOT / "assets" / "stickers" / "README.txt").write_text(
        "\n".join(manifest)
        + "\n\nUpload via Telegram @Stickers → Create new pack → static stickers.\n"
        "Use the emoji in the table for each file. 512×512 PNG, transparent.\n",
        encoding="utf-8",
    )
    print("zip", PACK, PACK.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
