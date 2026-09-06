# ZYCLOPS media vault · volume 2

This unlisted collection contains 24 newly generated square pictures (16 memes and eight caption-free holder illustrations), plus 12 silent MP4 loops: five motion posters, four animated illustrated scenes, and three character animations adapted from the existing ZYCLOPS sticker pack. The seven scene/character loops also have lightweight GIF alternatives.

## Entry points

- Gallery: `https://zyclops.xyz/media-vault/`
- Manifest: `https://zyclops.xyz/media-vault/manifest.json`
- CSV catalogue: `https://zyclops.xyz/media-vault/catalog.csv`
- Download: `https://zyclops.xyz/media-vault/zyclops-media-pack-v2.zip`

Share the gallery with holders for individual downloads and ready-to-copy captions. The ZIP contains all pictures, videos, GIF alternatives, captions and the offline gallery.

The directory is omitted from the public site's navigation, disallowed in `robots.txt`, and carries `X-Robots-Tag: noindex, nofollow, noarchive` on Vercel. This discourages discovery and indexing; it is not access control. Do not put credentials, private drafts or personal data here.

## Manifest contract

`schema_version` describes the JSON format. `library_version` identifies this collection. `assets` contains one record per postable file. Each record includes:

- `id`: stable, unique asset identifier.
- `creative_id`: shared by a still and its motion-poster variant. Use this for repeat avoidance.
- `collection`: `meme` or `artwork`; `release`: 1 or 2. New additions appear first.
- `alternates`: optional GIF delivery files, each with its own URL, size and hash. These are alternatives to the primary video, not separate creatives.
- `media_type`: `image` or `video`. `collection` distinguishes memes from holder artwork.
- `alternates`: optional GIF versions of a video, including their own URLs, dimensions, sizes and hashes. Use the GIF MIME type and upload category when choosing an alternate.
- `path`: relative to this manifest, for same-origin or local consumption.
- `url`: the absolute production file URL. It points to media bytes, not a gallery page.
- `mime_type`, `width`, `height`, `bytes`, `sha256`: upload and integrity information.
- `duration_seconds` and `animation_type` on videos. `motion_poster` means camera movement applied to a still; `character_loop` means a character sticker moves; `cinemagraph` means selected elements of an illustrated scene move.
- `thumbnail_path` / `thumbnail_url`, and a `poster_path` / `poster_url` for videos.
- `captions`: ready-to-use English copy in ZYCLOPS's dry voice; the second version includes `$ZYCL`.
- `alt_text`: visual description for accessible posting.
- `tags`, `theme`, `suggested_context`, and `suggested_cooldown_hours`: selection hints. The cooldown is a configurable starting point, not a growth claim.

GIF alternatives are 480 × 480, 12 fps, loop silently and stay below 5 MB. Use MP4 for sharper video playback or GIF for a reaction image.

Keep your posting history and credentials outside this folder. Record `creative_id` after a successful post, then choose a different creative for the next post. Do not count a failed upload as a successful post.

## Use from a bot

1. Fetch `manifest.json` and check `schema_version`.
2. Select by topic, format and your own posting history. These are evergreen fictional reaction memes; they do not report current prices or events.
3. Download the selected asset's `url` (or resolve `path` against the manifest URL). Confirm the HTTP response, MIME type and SHA-256 before uploading.
4. Upload the **file bytes** to X's media endpoint. A website URL alone does not attach the file as native media.
5. For video, follow X's asynchronous upload flow and wait for successful processing. Add the supplied alt text where the API supports it, then post with the resulting media ID and a selected caption.
6. Record the successful post and asset/creative ID in your bot's own storage.

Read-only selection example, with no X credentials or posting action:

```js
const manifestUrl = "https://zyclops.xyz/media-vault/manifest.json";
const response = await fetch(manifestUrl);
if (!response.ok) throw new Error(`Manifest HTTP ${response.status}`);
const library = await response.json();
if (library.schema_version !== "1.0") throw new Error("Unsupported schema");
const asset = library.assets.find(a => a.media_type === "image" && a.tags.includes("gm"));
if (!asset) throw new Error("No matching artwork");
const mediaResponse = await fetch(new URL(asset.path, manifestUrl));
if (!mediaResponse.ok) throw new Error(`Media HTTP ${mediaResponse.status}`);
const bytes = new Uint8Array(await mediaResponse.arrayBuffer());
// Pass bytes, asset.mime_type, asset.captions[0], and asset.alt_text to your existing uploader.
```

## Exports and provenance

Pictures are 1200 × 1200 JPEGs under 5 MB. Videos are 720 × 720 H.264 MP4, 30 fps, YUV 4:2:0, three to six seconds, with no audio. Videos are prepared for X; an actual X upload still depends on your account and API access. [X media upload specifications](https://docs.x.com/x-api/media/quickstart/best-practices).

The images were created with the built-in image-generation tool using the existing ZYCLOPS illustration as a character/style reference. Volume 2 exact prompts, scene notes and captions are in `meta/prompts-v2.json`; production notes are in `meta/ARTWORK-v2.md`. First-edition metadata remains available.

The original public website remains the home for the token's official links. Captions here make no claims about current price, returns or platform security. Add links when relevant to your post rather than appending the same link and account mentions to every reaction.

## Updates

Keep every existing media URL and asset ID unchanged, including unversioned first-edition filenames. Add new media with a new ID/version, update the manifest, and rebuild the ZIP. This avoids a bot downloading different artwork under an old saved asset ID. The gallery reads the manifest automatically.

To rebuild volume 2 metadata and the ZIP from the checked-in delivery files: `python3 scripts/build-media-vault-v2.py --package-only`. The renderer also accepts a private `--source-map` JSON of theme IDs to original generated image paths. Keep that source map outside the public folder. Rebuilding requires Pillow, NumPy, SciPy and ffmpeg/ffprobe; the website has no new runtime dependency.
