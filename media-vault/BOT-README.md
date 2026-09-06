# ZYCLOPS media vault · volume 3

24 curated still images: 16 reaction memes and eight holder illustrations. All use the same illustrated charcoal, gold and cream treatment. Animations and the six mismatched older meme versions have been retired.

## Entry points

- Gallery: https://zyclops.xyz/media-vault/
- Manifest: https://zyclops.xyz/media-vault/manifest.json
- CSV: https://zyclops.xyz/media-vault/catalog.csv
- Download: https://zyclops.xyz/media-vault/zyclops-media-pack-v3.zip

The gallery is unlisted and excluded from indexing, but anyone with its URL can access it. Share it with holders to download pictures and copy captions. The ZIP includes the same curated collection. Existing ZIP links serve the same current, still-image pack.

## Bot integration

Fetch the current manifest before selecting artwork. `schema_version` remains `1.0`; `library_version` is `2026-09-06.3`. The `assets` array is the current posting inventory. Every entry is an `image` with MIME type `image/jpeg`. Do not continue using an older cached inventory: `retired_asset_ids` lists the 25 removed entries. Remove them from pending queues and local caches.

Each retained image keeps its existing `id`, `creative_id`, `path`, `url` and SHA-256. Selection fields include `collection` (`meme` or `artwork`), `tags`, `captions`, `alt_text`, and `suggested_cooldown_hours`. Use `creative_id` and your own posting history to avoid repeats. Captions are evergreen character jokes, not reports of prices or market events.

Download the file bytes from `url`, check the response and SHA-256, then pass those bytes to your existing X uploader. A URL alone does not attach native media to an X post. Keep bot credentials and posting history outside this public folder.

## Files and maintenance

Pictures are 1200 × 1200 JPEGs below 5 MB; gallery thumbnails are 480 × 480. The pack contains no videos or GIFs. Kept files have not been recompressed or restyled.

Run `python3 scripts/build-media-vault.py` to validate the curated manifest and rebuild the CSV and ZIP. It uses Python's standard library and does not generate media or restore retired files. Edit the curated manifest deliberately when adding new artwork, keep existing file IDs stable, and give replacement artwork a new ID.

The submitted generation prompts are in `meta/prompts.json`; the visual direction is recorded in `meta/ARTWORK.md`.
