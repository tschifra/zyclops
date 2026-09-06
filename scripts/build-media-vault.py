#!/usr/bin/env python3
"""Assemble /media-vault/ stills, thumbs, videos, manifest, catalog and zip."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC_VAULT = Path(
    "/Users/tbr/Documents/Codex/2026-09-06/referenced-chatgpt-conversation-this-is-an/work/zyclops-media-library"
)
CODEX_IMG = Path("/Users/tbr/.codex/generated_images/01a076ba-9f0e-72e3-a8b1-c69c20a6394f")
GROK_IMG = Path(
    "/Users/tbr/.grok/sessions/%2FUsers%2Ftbr%2FDocuments%2FGitHub%2Fzyclop/01a07707-7ae0-75c0-b8d6-fce83d1043f4/images"
)
OUT = ROOT / "media-vault"
BASE = "https://zyclops.xyz/media-vault"

STILLS = {
    "gm": CODEX_IMG / "exec-1b6efbd9-da36-4285-9f3c-fbd523011e15.png",
    "gn": CODEX_IMG / "exec-5079085b-35e6-41a2-bfcf-64a03d603407.png",
    "hodl": CODEX_IMG / "exec-0735a958-2104-4b7d-88bc-108f7c6fcd4d.png",
    "diamond-hands": CODEX_IMG / "exec-ac07b27a-fa5d-4860-9c0f-32b1ac750990.png",
    "pump": CODEX_IMG / "exec-68e587ee-df33-4179-84dc-34e8c518efd9.png",
    "the-dip": CODEX_IMG / "exec-3d601246-23e8-42c0-96d2-d5e5e199ab39.png",
    "this-is-fine": CODEX_IMG / "exec-75d86476-57f8-43f7-82a4-bb5eca26fd7f.png",
    "rekt": CODEX_IMG / "exec-a9774ca6-3840-46bf-acf9-bccd1656f2f7.png",
    "lurking": CODEX_IMG / "exec-9a19b7ed-2e6f-4d08-abbf-874fe1f18f21.png",
    "copium": CODEX_IMG / "exec-c67f1cde-c7d1-4610-b32e-6d117da57690.png",
    "touch-grass": GROK_IMG / "34.jpg",
    "based": GROK_IMG / "33.jpg",
    "wen-moon": GROK_IMG / "29.jpg",
    "wagmi": GROK_IMG / "32.jpg",
    "ngmi": GROK_IMG / "31.jpg",
    "ser": GROK_IMG / "30.jpg",
}

MOTION = ["gm", "this-is-fine", "hodl", "lurking", "pump"]
LOOPS = {
    "gm": ROOT / "assets/animated/gm.webm",
    "pump": ROOT / "assets/animated/pump.webm",
    "this-is-fine": ROOT / "assets/animated/fine.webm",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def captions(item: dict) -> list[str]:
    one = item["caption"].strip()
    two = one if "$ZYCL" in one else f"{one} $ZYCL"
    return [one, two]


def jpeg_square(src: Path, dest: Path, size: int, quality: int = 88) -> None:
    im = Image.open(src).convert("RGB")
    im = im.resize((size, size), Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def ken_burns(still: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        "scale=880:880,"
        "zoompan=z='min(1.12,1+0.00115*on)':x='iw/2-(iw/zoom/2)':"
        "y='ih/2-(ih/zoom/2)':d=180:s=720x720:fps=30,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(still),
            "-vf",
            vf,
            "-t",
            "6",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def webm_loop(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=0x090a09:s=720x720:r=30",
            "-i",
            str(src),
            "-filter_complex",
            "[1:v]scale=640:640:force_original_aspect_ratio=decrease[fg];"
            "[0:v][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p",
            "-t",
            "6",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def file_record(item: dict, path: Path, **extra) -> dict:
    rel = path.relative_to(OUT).as_posix()
    rec = {
        "id": extra.pop("id", item["id"]),
        "creative_id": extra.pop("creative_id", item["id"]),
        "title": extra.pop("title", item["title"]),
        "media_type": extra.get("media_type", "image"),
        "path": rel,
        "url": f"{BASE}/{rel}",
        "mime_type": extra.pop("mime_type", "image/jpeg"),
        "width": extra.pop("width", 1200),
        "height": extra.pop("height", 1200),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "captions": captions(item),
        "alt_text": item["alt"],
        "tags": item["tags"],
        "theme": extra.pop("theme", item.get("kind", "meme")),
        "suggested_context": extra.pop("suggested_context", "timeline reaction"),
        "suggested_cooldown_hours": 48,
    }
    rec.update(extra)
    return rec


def main() -> None:
    prompts = {
        p["id"]: p
        for p in json.loads((SRC_VAULT / "media-vault/meta/prompts.json").read_text())
        if p["id"] in STILLS
    }
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(
        SRC_VAULT / "media-vault",
        OUT,
        ignore=shutil.ignore_patterns("images", "video", "thumbs"),
    )
    (OUT / "images").mkdir()
    (OUT / "thumbs").mkdir()
    (OUT / "video").mkdir()
    shutil.copy2(SRC_VAULT / "vercel.json", ROOT / "vercel.json")
    shutil.copy2(SRC_VAULT / "robots.txt", ROOT / "robots.txt")

    assets = []
    for asset_id, src in STILLS.items():
        item = prompts[asset_id]
        jpg = OUT / "images" / f"{asset_id}.jpg"
        thumb = OUT / "thumbs" / f"{asset_id}.jpg"
        jpeg_square(src, jpg, 1200)
        jpeg_square(src, thumb, 480, quality=80)
        rec = file_record(item, jpg, thumbnail_path=f"thumbs/{asset_id}.jpg", thumbnail_url=f"{BASE}/thumbs/{asset_id}.jpg")
        assets.append(rec)
        print(f"still {asset_id:16} {jpg.stat().st_size//1024}KB")

    for asset_id in MOTION:
        item = prompts[asset_id]
        still = OUT / "images" / f"{asset_id}.jpg"
        mp4 = OUT / "video" / f"{asset_id}-motion.mp4"
        ken_burns(still, mp4)
        rec = file_record(
            item,
            mp4,
            id=f"{asset_id}-motion",
            creative_id=asset_id,
            title=f"{item['title']} (motion)",
            media_type="video",
            mime_type="video/mp4",
            width=720,
            height=720,
            duration_seconds=6,
            animation_type="motion_poster",
            thumbnail_path=f"thumbs/{asset_id}.jpg",
            thumbnail_url=f"{BASE}/thumbs/{asset_id}.jpg",
            poster_path=f"images/{asset_id}.jpg",
            poster_url=f"{BASE}/images/{asset_id}.jpg",
        )
        assets.append(rec)
        print(f"motion {asset_id:16} {mp4.stat().st_size//1024}KB")

    for asset_id, webm in LOOPS.items():
        item = prompts[asset_id]
        mp4 = OUT / "video" / f"{asset_id}-loop.mp4"
        webm_loop(webm, mp4)
        rec = file_record(
            item,
            mp4,
            id=f"{asset_id}-loop",
            creative_id=asset_id,
            title=f"{item['title']} (loop)",
            media_type="video",
            mime_type="video/mp4",
            width=720,
            height=720,
            duration_seconds=6,
            animation_type="character_loop",
            thumbnail_path=f"thumbs/{asset_id}.jpg",
            thumbnail_url=f"{BASE}/thumbs/{asset_id}.jpg",
            poster_path=f"images/{asset_id}.jpg",
            poster_url=f"{BASE}/images/{asset_id}.jpg",
        )
        assets.append(rec)
        print(f"loop   {asset_id:16} {mp4.stat().st_size//1024}KB")

    manifest = {
        "schema_version": "1.0",
        "library_version": "v1",
        "name": "ZYCLOPS media vault",
        "home": "https://zyclops.xyz/",
        "gallery": f"{BASE}/",
        "assets": assets,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with (OUT / "catalog.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["id", "creative_id", "title", "media_type", "path", "url", "bytes", "sha256"],
        )
        writer.writeheader()
        for a in assets:
            writer.writerow({k: a[k] for k in writer.fieldnames})

    zip_path = OUT / "zyclops-media-pack-v1.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(OUT.rglob("*")):
            if path.is_file() and path.name != zip_path.name:
                zf.write(path, path.relative_to(OUT))
    print("assets", len(assets), "zip", zip_path.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
