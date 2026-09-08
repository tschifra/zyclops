# ZYCLOPS media vault · volume 10

A complete replacement in the approved modern character style: 24 meme posters, 6 text-free reactions, 4 text-free illustrations, 2 wide banners and 2 brand PNGs. 38 assets total. Every file is below 2 MB. There are no animations in this release.

## Entry points

- Gallery: https://zyclops.xyz/media-vault/
- Manifest: https://zyclops.xyz/media-vault/manifest.json
- CSV: https://zyclops.xyz/media-vault/catalog.csv
- ZIP: https://zyclops.xyz/media-vault/zyclops-media-pack-v10.zip

The gallery is unlisted and excluded from search indexing. It is publicly accessible to anyone with the URL. Never put passwords, API keys, private prompts, or posting logs in this folder.

## Updating a posting bot

Fetch `manifest.json` before selecting artwork. `schema_version` stays `1.0`; `library_version` is `2026-09-09.10`, `pack_version` is `10`, and `style_version` is `locked-face-modern-v10`. Replace the cached inventory when the library version changes. Every old artwork ID is retired; old file paths must not be used for new posts.

The current inventory is only the `assets` array. Do not select files by recursively listing this directory or by opening an old ZIP. `replaces_all_previous_assets: true` invalidates the entire old inventory; `retired_pack_versions` lists retired releases. Never merge this manifest with previously cached assets.

Each asset provides `id`, `creative_id`, `collection`, `path`, `url`, `mime_type`, `width`, `height`, `bytes`, `sha256`, `thumbnail_url`, `captions`, `alt_text`, `tags`, and `suggested_cooldown_hours`. Supported collections are `meme`, `reaction`, `artwork`, `banner`, and `brand`. Existing `collection === "meme"` and `collection === "artwork"` filters still work. Include `reaction` if you want the new expression set. Reserve `banner` and `brand` for profile and campaign use.

Download the bytes from `url`, check the successful response and SHA-256, and pass those bytes to your uploader. A URL in post text does not attach native media. JPEGs are ready for X; the PNG coin logo has a real transparent exterior and is below 2 MB. Dimensions vary by asset; read the manifest rather than assuming every image is square.

Use `creative_id` to avoid repetition, and keep a posting history outside the website. The suggested 72-hour cooldown is a default for a single creative, not a schedule to post all images automatically. Choose a relevant meme and edit its caption for the actual conversation. Keep the character's deadpan voice and do not invent launches, partnerships, prices or returns.

## Current token facts

The manifest's `project` object contains the official Solana mint, Raydium pool, SOL quote currency and community links. The canonical configuration is also available at https://zyclops.xyz/token.json.

ZYCLOPS is live on Solana. The starting market cap was $5,000 at launch; that is not a live market quote. The current token transfer fee is 1%, separately from any network or exchange fees. Read the configuration's source and check date before reusing time-sensitive information. Do not turn the launch market cap into a profit promise or a current valuation.

Meme captions are intentionally character-led and avoid time-sensitive trading claims. Add the canonical website link when context calls for it.

## Download compatibility

The website redirects old ZIP names (`v1`–`v9`) and `zyclops-media-pack.zip` to the current v10 ZIP. Only one ZIP is stored, so retired artwork cannot leak through an old bundle. Direct paths to retired images and animations are removed.

## Maintenance

Run `python3 scripts/build-media-vault.py` from the repository to validate all assets and rebuild the gallery, CSV and ZIP. It does not generate artwork. The HTML template lives at `scripts/media-vault-template.html`; gallery styles and interactions live in this folder. The validator rejects animation files, missing assets, oversized images, duplicate IDs, stale hashes, and an incomplete file inventory.

The submitted generation prompts are in `meta/prompts.json`, the reusable character brief is in `meta/CHARACTER-PROMPT.md`, and the artwork notes are in `meta/ARTWORK.md`. Source images were generated with the built-in image generation tool; exports preserve their composition. Original full-resolution generation files and the old vault backup are stored outside the published website.
