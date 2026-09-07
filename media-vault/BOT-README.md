# ZYCLOPS media vault · volume 9

65 still images and 8 silent looping scenes. Still artwork is 1200 × 1200 JPEG. Loops are closed palindromes: the first frame matches the last, there is no audio, and they are shipped as GIF (exact loop, good for X) with a smaller WebP alternate.

## Entry points

- Gallery: https://zyclops.xyz/media-vault/
- Manifest: https://zyclops.xyz/media-vault/manifest.json
- CSV: https://zyclops.xyz/media-vault/catalog.csv
- Download: https://zyclops.xyz/media-vault/zyclops-media-pack-v9.zip

The gallery is unlisted and excluded from indexing, but anyone with its URL can access it. Share it with holders to download pictures, copy captions, and grab a loop. Older ZIP links (`v1`–`v8`) serve the current pack.

## Bot integration

Fetch the current manifest before selecting artwork. `schema_version` remains `1.0`; `library_version` is `2026-09-07.9`. The `assets` array is the current posting inventory. `retired_asset_ids` lists older Ken Burns / sticker loops that stay retired.

Each retained still keeps its existing `id`, `creative_id`, `path`, `url` and SHA-256. Volume 9 adds ten still memes: Proof of work, Cold wallet, Gas fees, Rug check, Whale alert, Token burn, Hard fork, Liquid staking, Private key, and Roadmap. Filter `release: 9` for this batch. The lounge poster remains under `release: 8`. Existing artwork and loops remain available. Selection fields include `collection` (`meme` or `artwork`), `tags`, `captions`, `alt_text`, and `suggested_cooldown_hours`. Use `creative_id` to pair a still with its loop and to avoid repeats.

Loop entries have `animation_type: cinemagraph`, `has_audio: false`, `loop: true`, `mime_type: image/gif`. The `alternates` array holds the WebP. Prefer the GIF when posting to X; WebP is smaller for the web.

Download the file bytes from `url`, check the response and SHA-256, then pass those bytes to your existing uploader. A URL alone does not attach native media to an X post. Keep bot credentials and posting history outside this public folder.

## Files and maintenance

Stills are 1200 × 1200 JPEGs below 5 MB; gallery thumbnails are 480 × 480. Loops are 400 × 400 GIF at 8 fps, about six seconds, palindrome-closed, no sound. WebP alternates are 600 × 600.

Run `python3 scripts/build-media-vault.py` to validate the manifest and rebuild the CSV and ZIP. It does not generate media. To rebuild loops from source clips, run `python3 scripts/build-loop-artwork.py` first.

The submitted generation prompts are in `meta/prompts.json`; the visual direction is recorded in `meta/ARTWORK.md`.
