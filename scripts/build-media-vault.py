#!/usr/bin/env python3
"""Validate the curated still-image manifest and package its exact inventory."""

from pathlib import Path
import csv
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "media-vault"


def main():
    manifest = json.loads((VAULT / "manifest.json").read_text())
    assets = manifest["assets"]
    retired = set(manifest.get("retired_asset_ids", []))
    ids = [asset["id"] for asset in assets]
    assert assets and len(set(ids)) == len(ids), "Empty inventory or duplicate IDs"
    assert not retired.intersection(ids), "Retired artwork remains in inventory"
    assert manifest["counts"] == {"images": len(assets), "videos": 0, "gif_alternates": 0}
    paths = {
        "manifest.json", "catalog.csv", "BOT-README.md",
        "index.html", "vault.css", "vault.js", "meta/prompts.json", "meta/ARTWORK.md",
    }
    for asset in assets:
        assert asset["media_type"] == "image" and asset["mime_type"] == "image/jpeg"
        assert not asset.get("alternates"), "Still collection cannot contain animation alternatives"
        for key in ("path", "thumbnail_path"):
            relative = Path(asset[key])
            assert not relative.is_absolute() and ".." not in relative.parts
            assert relative.suffix.lower() == ".jpg"
            assert (VAULT / relative).is_file(), str(relative)
            paths.add(str(relative))
        data = (VAULT / asset["path"]).read_bytes()
        assert len(data) == asset["bytes"] and len(data) < 5_000_000, asset["id"]
        assert hashlib.sha256(data).hexdigest() == asset["sha256"], asset["id"]
    assert not any(p.suffix.lower() in {".mp4", ".webm", ".gif"} for p in VAULT.rglob("*")), "Animation file remains in the vault"
    fields = ["id", "creative_id", "title", "collection", "media_type", "url", "mime_type", "width", "height", "bytes", "caption", "alt_text", "tags"]
    with (VAULT / "catalog.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for asset in assets:
            row = {key: asset.get(key, "") for key in fields}
            row.update(caption=asset["captions"][0], tags="|".join(asset["tags"]))
            writer.writerow(row)
    bundle = VAULT / "zyclops-media-pack-v3.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for relative in sorted(paths):
            archive.write(VAULT / relative, "media-vault/" + relative)
    for version in (1, 2):
        shutil.copyfile(bundle, VAULT / f"zyclops-media-pack-v{version}.zip")
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
    print(f"Validated and packaged {len(assets)} still images; no animations. ZIP: {bundle.stat().st_size:,} bytes.")


if __name__ == "__main__":
    main()
