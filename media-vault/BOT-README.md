# ZYCLOPS media vault · volume 1

This unlisted collection contains 16 newly generated square meme pictures and eight silent MP4 loops: five motion posters and three character animations adapted from the existing ZYCLOPS sticker pack.

## Entry points

- Gallery: `https://zyclops.xyz/media-vault/`
- Manifest: `https://zyclops.xyz/media-vault/manifest.json`
- CSV catalogue: `https://zyclops.xyz/media-vault/catalog.csv`
- Download: `https://zyclops.xyz/media-vault/zyclops-media-pack-v1.zip`

These production URLs become available when this folder is deployed. Before deployment, serve the repository and open `/media-vault/` locally.

The directory is omitted from the public site's navigation, disallowed in `robots.txt`, and carries `X-Robots-Tag: noindex, nofollow, noarchive` on Vercel. This discourages discovery and indexing; it is not access control. Do not put credentials, private drafts or personal data here.

## Manifest contract

`schema_version` describes the JSON format. `library_version` identifies this collection. `assets` contains one record per postable file. Each record includes:

- `id`: stable, unique asset identifier.
- `creative_id`: shared by a still and its motion-poster variant. Use this for repeat avoidance.
- `media_type`: `image` or `video`.
- `path`: relative to this manifest, for same-origin or local consumption.
- `url`: the absolute production file URL. It points to media bytes, not a gallery page.
- `mime_type`, `width`, `height`, `bytes`, `sha256`: upload and integrity information.
- `duration_seconds` and `animation_type` on videos. `motion_poster` means camera movement applied to a still; `character_loop` means the character or its scene elements move.
- `thumbnail_path` / `thumbnail_url`, and a `poster_path` / `poster_url` for videos.
- `captions`: ready-to-use English copy in ZYCLOPS's dry voice; the second version includes `$ZYCL`.
- `alt_text`: visual description for accessible posting.
- `tags`, `theme`, `suggested_context`, and `suggested_cooldown_hours`: selection hints. The cooldown is a configurable starting point, not a growth claim.

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

Pictures are 1200 × 1200 JPEGs under 5 MB. Videos are 720 × 720 H.264 MP4, 30 fps, YUV 4:2:0, six seconds, with no audio. Videos are prepared for X; an actual X upload still depends on your account and API access. [X media upload specifications](https://docs.x.com/x-api/media/quickstart/best-practices).

The images were created with the built-in image-generation tool using the existing ZYCLOPS illustration as a character/style reference. Exact prompts, scene notes and captions are in `meta/prompts.json`; production notes are in `meta/ARTWORK.md`.

The original public website remains the home for the token's official links. Captions here make no claims about current price, returns or platform security. Add links when relevant to your post rather than appending the same link and account mentions to every reaction.

## Updates

Keep existing `-v1` media URLs unchanged. Add new media with a new ID/version, update the manifest, and rebuild the ZIP. This avoids a bot downloading different artwork under an old saved asset ID. The gallery reads the manifest automatically.
