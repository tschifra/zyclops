#!/usr/bin/env python3
"""Validate the curated vault manifest and package its exact inventory."""

from pathlib import Path
import csv
import hashlib
import json
import shutil
import zipfile

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "media-vault"


def main():
    manifest = json.loads((VAULT / "manifest.json").read_text())
    assets = manifest["assets"]
    retired = set(manifest.get("retired_asset_ids", []))
    ids = [asset["id"] for asset in assets]
    assert assets and len(set(ids)) == len(ids), "Empty inventory or duplicate IDs"
    assert not retired.intersection(ids), "Retired artwork remains in inventory"
    stills = [asset for asset in assets if asset.get("animation_type") != "cinemagraph"]
    loops = [asset for asset in assets if asset.get("animation_type") == "cinemagraph"]
    webp_alts = sum(len(asset.get("alternates", [])) for asset in loops)
    assert manifest["counts"]["images"] == len(stills)
    assert manifest["counts"]["videos"] == 0
    assert manifest["counts"]["loops"] == len(loops)
    assert manifest["counts"]["webp_alternates"] == webp_alts
    paths = {
        "manifest.json",
        "catalog.csv",
        "BOT-README.md",
        "index.html",
        "vault.css",
        "vault.js",
        "meta/prompts.json",
        "meta/ARTWORK.md",
    }
    allowed = {
        "image/jpeg": {".jpg"},
        "image/gif": {".gif"},
        "image/webp": {".webp"},
    }
    for asset in assets:
        assert asset["media_type"] == "image"
        assert asset["mime_type"] in allowed, asset["id"]
        for key in ("path", "thumbnail_path"):
            relative = Path(asset[key])
            assert not relative.is_absolute() and ".." not in relative.parts
            assert (VAULT / relative).is_file(), str(relative)
            paths.add(str(relative))
        suffix = Path(asset["path"]).suffix.lower()
        assert suffix in allowed[asset["mime_type"]], asset["id"]
        data = (VAULT / asset["path"]).read_bytes()
        assert len(data) == asset["bytes"] and len(data) < 5_000_000, asset["id"]
        assert hashlib.sha256(data).hexdigest() == asset["sha256"], asset["id"]
        if asset.get("animation_type") == "cinemagraph":
            assert asset["mime_type"] == "image/gif"
            assert asset.get("has_audio") is False
            assert asset.get("loop") is True
            with Image.open(VAULT / asset["path"]) as image:
                assert image.n_frames >= 8
                image.seek(0)
                first = image.convert("RGB")
                image.seek(image.n_frames - 1)
                last = image.convert("RGB")
                assert ImageChops.difference(first, last).getbbox() is None, asset["id"]
            for alt in asset.get("alternates", []):
                relative = Path(alt["path"])
                assert (VAULT / relative).is_file(), str(relative)
                paths.add(str(relative))
                assert hashlib.sha256((VAULT / relative).read_bytes()).hexdigest() == alt["sha256"]
        else:
            assert asset["mime_type"] == "image/jpeg"
            assert not asset.get("alternates")
            assert Path(asset["path"]).suffix.lower() == ".jpg"
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
    bundle = VAULT / "zyclops-media-pack-v4.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for relative in sorted(paths):
            archive.write(VAULT / relative, "media-vault/" + relative)
    for version in (1, 2, 3):
        shutil.copyfile(bundle, VAULT / f"zyclops-media-pack-v{version}.zip")
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
    print(
        f"Validated {len(stills)} stills and {len(loops)} silent loops. "
        f"ZIP: {bundle.stat().st_size:,} bytes."
    )


if __name__ == "__main__":
    main()
