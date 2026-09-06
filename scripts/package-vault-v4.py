#!/usr/bin/env python3
"""Add silent closed-loop GIF/WebP artwork and two new stills to the vault."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path("/Users/tbr/Documents/GitHub/zyclop")
VAULT = ROOT / "media-vault"
BASE = "https://zyclops.xyz/media-vault/"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jpeg_asset(ident: str, creative_id: str, title: str, caption: str, alt: str, tags: list[str]) -> dict:
    path = f"images/zyclops-{ident}-v1.jpg"
    thumb = f"thumbs/zyclops-{ident}-v1.jpg"
    file = VAULT / path
    with Image.open(file) as image:
        width, height = image.size
        assert (width, height) == (1200, 1200), ident
    return {
        "id": f"zyclops-{ident}-v1",
        "creative_id": creative_id,
        "title": title,
        "theme": "artwork",
        "collection": "artwork",
        "media_type": "image",
        "path": path,
        "url": BASE + path,
        "mime_type": "image/jpeg",
        "width": width,
        "height": height,
        "bytes": file.stat().st_size,
        "sha256": sha256(file),
        "thumbnail_path": thumb,
        "thumbnail_url": BASE + thumb,
        "captions": [caption, caption + "\n\n$ZYCL"],
        "alt_text": alt,
        "tags": tags,
        "suggested_context": "Holder artwork to share with your own caption.",
        "suggested_cooldown_hours": 72,
        "topic": creative_id,
        "release": 4,
    }


def loop_asset(
    ident: str,
    creative_id: str,
    title: str,
    caption: str,
    alt: str,
    tags: list[str],
) -> dict:
    gif_rel = f"gif/zyclops-{ident}-v1.gif"
    webp_rel = f"webp/zyclops-{ident}-v1.webp"
    thumb = f"thumbs/zyclops-{ident}-v1.jpg"
    gif = VAULT / gif_rel
    webp = VAULT / webp_rel
    with Image.open(gif) as image:
        width, height = image.size
        frames = image.n_frames
        image.seek(0)
        first = image.convert("RGB")
        image.seek(frames - 1)
        last = image.convert("RGB")
        assert first.tobytes() == last.tobytes(), ident
        assert image.info.get("duration", 125)
    duration = round(frames * 0.125, 3)
    return {
        "id": f"zyclops-{ident}-v1",
        "creative_id": creative_id,
        "title": title,
        "theme": "artwork",
        "collection": "artwork",
        "media_type": "image",
        "path": gif_rel,
        "url": BASE + gif_rel,
        "mime_type": "image/gif",
        "width": width,
        "height": height,
        "bytes": gif.stat().st_size,
        "sha256": sha256(gif),
        "thumbnail_path": thumb,
        "thumbnail_url": BASE + thumb,
        "captions": [caption, caption + "\n\n$ZYCL"],
        "alt_text": alt,
        "tags": tags + ["loop"],
        "suggested_context": "Silent looping holder artwork. First frame matches last. No audio.",
        "suggested_cooldown_hours": 72,
        "topic": creative_id,
        "release": 4,
        "duration_seconds": duration,
        "fps": 8,
        "animation_type": "cinemagraph",
        "has_audio": False,
        "loop": True,
        "alternates": [
            {
                "format": "webp",
                "mime_type": "image/webp",
                "path": webp_rel,
                "url": BASE + webp_rel,
                "width": 600,
                "height": 600,
                "fps": 8,
                "bytes": webp.stat().st_size,
                "sha256": sha256(webp),
            }
        ],
    }


LOOPS = [
    (
        "night-watch",
        "zyclops-night-watch-v1",
        loop_asset(
            "night-watch-loop",
            "night-watch",
            "Night watch · loop",
            "one eye on the night. absolutely no useful observations.",
            "Silent looping illustration: rain falls past the moon while ZYCLOPS stands still on a rooftop.",
            ["artwork", "night", "holder-art"],
        ),
    ),
    (
        "the-blind-spot",
        "zyclops-the-blind-spot-v1",
        loop_asset(
            "the-blind-spot-loop",
            "the-blind-spot",
            "The blind spot · loop",
            "there's a place for you in the blind spot.",
            "Silent looping illustration: steam curls from the coffee while rain streaks the cafe window.",
            ["artwork", "community", "holder-art"],
        ),
    ),
    (
        "rainy-alley",
        "zyclops-rainy-alley-v1",
        loop_asset(
            "rainy-alley-loop",
            "rainy-alley",
            "After the rain · loop",
            "low visibility. ideal conditions.",
            "Silent looping illustration: rain falls and puddles ripple while hooded ZYCLOPS stands still.",
            ["artwork", "rain", "holder-art"],
        ),
    ),
    (
        "the-forge",
        "zyclops-the-forge-v1",
        loop_asset(
            "the-forge-loop",
            "the-forge",
            "Made in the blind spot · loop",
            "built by hand. inspected by one eye.",
            "Silent looping illustration: furnace fire and gold sparks move while ZYCLOPS stays at the bench.",
            ["artwork", "craft", "holder-art"],
        ),
    ),
    (
        "campfire",
        "zyclops-campfire-v1",
        loop_asset(
            "campfire-loop",
            "campfire",
            "Off the grid · loop",
            "off the grid. still in the group chat.",
            "Silent looping illustration: campfire flames and coffee steam move while ZYCLOPS sits still.",
            ["artwork", "campfire", "holder-art"],
        ),
    ),
    (
        "redacted-world",
        "zyclops-redacted-world-v1",
        loop_asset(
            "redacted-world-loop",
            "redacted-world",
            "Nothing to see here · loop",
            "the view is classified. the company is good.",
            "Silent looping illustration: redacted papers drift through the archive while ZYCLOPS holds still.",
            ["artwork", "privacy", "holder-art"],
        ),
    ),
]

NEW_STILLS = [
    jpeg_asset(
        "first-snow",
        "first-snow",
        "First snow",
        "the coffee is still warmer than the forecast.",
        "ZYCLOPS sits on a cabin porch in falling snow with a gold lantern and coffee.",
        ["artwork", "snow", "holder-art"],
    ),
    jpeg_asset(
        "the-lantern",
        "the-lantern",
        "The lantern",
        "one light. no audience.",
        "ZYCLOPS sits in a brick vault holding a gold lantern among stored boxes.",
        ["artwork", "lantern", "holder-art"],
    ),
]

NEW_STILL_LOOPS = [
    loop_asset(
        "first-snow-loop",
        "first-snow",
        "First snow · loop",
        "the coffee is still warmer than the forecast.",
        "Silent looping illustration: snow falls and the lantern flame flickers on the cabin porch.",
        ["artwork", "snow", "holder-art"],
    ),
    loop_asset(
        "the-lantern-loop",
        "the-lantern",
        "The lantern · loop",
        "one light. no audience.",
        "Silent looping illustration: the lantern flame flickers and gold dust drifts in the vault.",
        ["artwork", "lantern", "holder-art"],
    ),
]


def main() -> None:
    manifest = json.loads((VAULT / "manifest.json").read_text())
    assets = list(manifest["assets"])
    by_id = {asset["id"]: index for index, asset in enumerate(assets)}
    inserted = 0
    for _, after_id, loop in reversed(LOOPS):
        index = by_id[after_id] + 1
        assets.insert(index, loop)
        inserted += 1
    # After reversing inserts, find redacted still (now followed by its loop)
    redacted_index = next(i for i, asset in enumerate(assets) if asset["id"] == "zyclops-redacted-world-v1")
    # still, its loop, then new stills+loops at end of that cluster
    loop_index = redacted_index + 1
    assert assets[loop_index]["id"] == "zyclops-redacted-world-loop-v1"
    tail = NEW_STILLS[0:1] + NEW_STILL_LOOPS[0:1] + NEW_STILLS[1:2] + NEW_STILL_LOOPS[1:2]
    for offset, asset in enumerate(tail):
        assets.insert(loop_index + 1 + offset, asset)
        inserted += 1

    ids = [asset["id"] for asset in assets]
    assert len(ids) == len(set(ids))
    loops = [asset for asset in assets if asset.get("animation_type") == "cinemagraph"]
    stills = [asset for asset in assets if asset.get("animation_type") != "cinemagraph"]
    assert len(loops) == 8 and len(stills) == 26

    manifest["library_version"] = "2026-09-06.4"
    manifest["assets"] = assets
    manifest["counts"] = {
        "images": len(stills),
        "videos": 0,
        "loops": len(loops),
        "gif_alternates": 0,
        "webp_alternates": len(loops),
    }
    (VAULT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    fields = [
        "id",
        "creative_id",
        "title",
        "collection",
        "release",
        "media_type",
        "mime_type",
        "url",
        "width",
        "height",
        "bytes",
        "duration_seconds",
        "animation_type",
        "caption",
        "alt_text",
        "tags",
    ]
    with (VAULT / "catalog.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for asset in assets:
            row = {key: asset.get(key, "") for key in fields}
            row.update(caption=asset["captions"][0], tags="|".join(asset["tags"]))
            writer.writerow(row)

    include = {
        "index.html",
        "vault.css",
        "vault.js",
        "manifest.json",
        "catalog.csv",
        "BOT-README.md",
        "meta/prompts.json",
        "meta/ARTWORK.md",
    }
    for asset in assets:
        include.update([asset["path"], asset["thumbnail_path"]])
        include.update(alt["path"] for alt in asset.get("alternates", []))

    bundle = VAULT / "zyclops-media-pack-v4.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for relative in sorted(include):
            archive.write(VAULT / relative, "media-vault/" + relative)
    for version in (1, 2, 3):
        shutil.copyfile(bundle, VAULT / f"zyclops-media-pack-v{version}.zip")
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
    print(
        json.dumps(
            {
                "assets": len(assets),
                "stills": len(stills),
                "loops": len(loops),
                "zip_bytes": bundle.stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
