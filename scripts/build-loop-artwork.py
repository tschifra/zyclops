#!/usr/bin/env python3
"""Build silent closed-loop WebP + GIF artwork from generated clips.

Each loop is a palindrome: forward frames plus reverse, with the first frame
repeated at the end so the file opens and closes on the same picture. No audio.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path("/Users/tbr/Documents/GitHub/zyclop")
VAULT = ROOT / "media-vault"
SESSION = Path(
    "/Users/tbr/.grok/sessions/%2FUsers%2Ftbr%2FDocuments%2FGitHub%2Fzyclop"
    "/01a07707-7ae0-75c0-b8d6-fce83d1043f4"
)
WORK = Path("/tmp/zycl-loop-build")
FPS = 8
FRAME_MS = 125  # 8 fps
WEB_SIZE = 600
GIF_SIZE = 400
WEBP_Q = 55
STILL_SIZE = 1200

CLIPS = [
    ("2.mp4", "campfire-loop"),
    ("4.mp4", "the-forge-loop"),
    ("3.mp4", "rainy-alley-loop"),
    ("1.mp4", "the-blind-spot-loop"),
    ("5.mp4", "redacted-world-loop"),
    ("6.mp4", "night-watch-loop"),
    ("7.mp4", "first-snow-loop"),
    ("8.mp4", "the-lantern-loop"),
]

STILLS = [
    ("35.jpg", "first-snow"),
    ("36.jpg", "the-lantern"),
]


def run(args: list[str]) -> None:
    result = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.decode()[-2500:] or "command failed")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def square_jpeg(source: Path, dest: Path, size: int, quality: int) -> None:
    image = Image.open(source).convert("RGB")
    if image.size != (size, size):
        image = image.resize((size, size), Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest, quality=quality, subsampling=0, optimize=True)


def extract_forward(src: Path, dest_dir: Path) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for leftover in dest_dir.glob("fwd_*.png"):
        leftover.unlink()
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(src),
            "-an",
            "-t",
            "3",
            "-vf",
            f"fps={FPS},scale={WEB_SIZE}:{WEB_SIZE}:flags=lanczos,format=rgb24",
            str(dest_dir / "fwd_%03d.png"),
        ]
    )
    frames = sorted(dest_dir.glob("fwd_*.png"))
    if len(frames) < 8:
        raise RuntimeError(f"too few frames from {src.name}: {len(frames)}")
    return frames


def palindrome(frames: list[Path], dest_dir: Path) -> list[Path]:
    """Forward plus reverse, first picture == last picture."""
    order = frames + frames[-2::-1]
    paths = []
    for index, source in enumerate(order, start=1):
        target = dest_dir / f"pal_{index:03d}.png"
        if target.exists():
            target.unlink()
        shutil.copyfile(source, target)
        paths.append(target)
    first = Image.open(paths[0]).convert("RGB")
    last = Image.open(paths[-1]).convert("RGB")
    if ImageChops.difference(first, last).getbbox() is not None:
        raise RuntimeError(f"loop is not closed: {dest_dir}")
    return paths


def write_webp(frames: list[Path], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    args = ["img2webp", "-loop", "0", "-min_size"]
    for frame in frames:
        args += ["-d", str(FRAME_MS), "-lossy", "-q", str(WEBP_Q), "-m", "4", str(frame)]
    args += ["-o", str(dest)]
    run(args)


def write_gif(frames: list[Path], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    scaled = dest.parent / f".gifbuild-{dest.stem}"
    if scaled.exists():
        shutil.rmtree(scaled)
    scaled.mkdir()
    for index, frame in enumerate(frames, start=1):
        image = Image.open(frame).convert("RGB").resize(
            (GIF_SIZE, GIF_SIZE), Image.Resampling.LANCZOS
        )
        image.save(scaled / f"{index:03d}.png")
    palette = scaled / "palette.png"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(scaled / "%03d.png"),
            "-vf",
            "palettegen=max_colors=48:stats_mode=diff",
            str(palette),
        ]
    )
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(scaled / "%03d.png"),
            "-i",
            str(palette),
            "-lavfi",
            "paletteuse=dither=bayer:bayer_scale=5",
            "-loop",
            "0",
            str(dest),
        ]
    )
    shutil.rmtree(scaled)


def build_clip(src_name: str, ident: str) -> dict:
    src = SESSION / "videos" / src_name
    work = WORK / ident
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    forward = extract_forward(src, work)
    loop_frames = palindrome(forward, work)
    webp = VAULT / "webp" / f"zyclops-{ident}-v1.webp"
    gif = VAULT / "gif" / f"zyclops-{ident}-v1.gif"
    thumb = VAULT / "thumbs" / f"zyclops-{ident}-v1.jpg"
    write_webp(loop_frames, webp)
    write_gif(loop_frames, gif)
    square_jpeg(loop_frames[0], thumb, 480, 85)
    assert webp.stat().st_size < 2_500_000, webp
    assert gif.stat().st_size < 4_000_000, gif
    print(
        f"{ident}: {len(loop_frames)} frames, "
        f"webp={webp.stat().st_size:,} gif={gif.stat().st_size:,}",
        flush=True,
    )
    return {
        "id": ident,
        "frames": len(loop_frames),
        "webp": webp,
        "gif": gif,
        "thumb": thumb,
        "webp_sha": sha256(webp),
        "gif_sha": sha256(gif),
        "webp_bytes": webp.stat().st_size,
        "gif_bytes": gif.stat().st_size,
    }


def build_still(src_name: str, ident: str) -> None:
    source = SESSION / "images" / src_name
    image = VAULT / "images" / f"zyclops-{ident}-v1.jpg"
    thumb = VAULT / "thumbs" / f"zyclops-{ident}-v1.jpg"
    square_jpeg(source, image, STILL_SIZE, 94)
    square_jpeg(source, thumb, 480, 85)
    print(f"still {ident}: {image.stat().st_size:,} bytes", flush=True)


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    for folder in ("webp", "gif", "thumbs", "images"):
        (VAULT / folder).mkdir(exist_ok=True)
    for src_name, ident in STILLS:
        build_still(src_name, ident)
    for src_name, ident in CLIPS:
        build_clip(src_name, ident)


if __name__ == "__main__":
    main()
