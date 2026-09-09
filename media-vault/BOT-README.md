# ZYCLOPS media vault · volume 11

44 assets in the approved modern character style: 27 finished meme posters, one blank meme template, eight reactions, four illustrations, two wide banners and two brand PNGs. Volume 11 adds six Stonk community files and retains all 38 approved volume-10 assets. Every file is below 2 MB. There are no animations in this release.

## Entry points

- Gallery: https://zyclops.xyz/media-vault/
- Manifest: https://zyclops.xyz/media-vault/manifest.json
- CSV: https://zyclops.xyz/media-vault/catalog.csv
- ZIP: https://zyclops.xyz/media-vault/zyclops-media-pack-v11.zip
- Stonk pack: https://zyclops.xyz/media-vault/?pack=stonk#library
- Six-file ZIP: https://zyclops.xyz/media-vault/zyclops-stonk-community-pack-v1.zip

The gallery is unlisted and excluded from search indexing. It is publicly accessible to anyone with the URL. Never put passwords, API keys, private prompts, or posting logs in this folder.

## Updating a posting bot

Fetch `manifest.json` before selecting artwork. `schema_version` stays `1.0`; `library_version` is `2026-09-09.11`, `pack_version` is `11`, and the unchanged mascot `style_version` is `locked-face-modern-v10`. Replace the cached inventory when the library version changes. Volume-10 artwork IDs remain valid. IDs explicitly listed in `retired_asset_ids` are retired and must not be posted.

The current inventory is only the `assets` array. Do not select files by recursively listing this directory or by opening an old ZIP. `replaces_all_previous_assets: false` records this additive release; `retired_pack_versions` lists superseded full ZIP releases, not individual current asset IDs. Always replace a cached inventory with this complete manifest.

The optional `pack` field groups assets into a community pack. The six new files use `stonk-community-v1`; `community_packs` contains the pack download and guide. The blank template has `requires_caption: true`: do not automatically publish that image unfinished. The other five images are ready to use. The new reaction cards include short text; the six older reaction portraits remain text-free.

Each asset provides `id`, `creative_id`, `collection`, `path`, `url`, `mime_type`, `width`, `height`, `bytes`, `sha256`, `thumbnail_url`, `captions`, `alt_text`, `tags`, and `suggested_cooldown_hours`. Supported collections are `meme`, `reaction`, `artwork`, `banner`, and `brand`. Existing `collection === "meme"` and `collection === "artwork"` filters still work. Include `reaction` if you want the new expression set. Reserve `banner` and `brand` for profile and campaign use.

Download the bytes from `url`, check the successful response and SHA-256, and pass those bytes to your uploader. A URL in post text does not attach native media. JPEGs are ready for X; the PNG coin logo has a real transparent exterior and is below 2 MB. Dimensions vary by asset; read the manifest rather than assuming every image is square.

Use `creative_id` to avoid repetition, and keep a posting history outside the website. The suggested 72-hour cooldown is a default for a single creative, not a schedule to post all images automatically. Choose a relevant meme and edit its caption for the actual conversation. Keep the character's deadpan voice and do not invent launches, partnerships, prices or returns.

## Current token facts

The manifest's `project` object contains the official Solana mint, Raydium pool, SOL quote currency and community links. The canonical configuration is also available at https://zyclops.xyz/token.json.

ZYCLOPS is live on Solana. The starting market cap was $5,000 at launch; that is not a live market quote. The current token transfer fee is 1%, separately from any network or exchange fees. Read the configuration's source and check date before reusing time-sensitive information. Do not turn the launch market cap into a profit promise or a current valuation.

Meme captions are intentionally character-led and avoid time-sensitive trading claims. Add the canonical website link when context calls for it.

## Download compatibility

The website redirects old full ZIP names (`v1`–`v10`) and `zyclops-media-pack.zip` to the current v11 ZIP. One current full bundle and one six-file Stonk pack are stored. Direct paths to retired images and animations remain removed.

## Maintenance

Run `python3 scripts/build-media-vault.py` from the repository to validate all assets and rebuild the gallery, CSV and ZIP. It does not generate artwork. The HTML template lives at `scripts/media-vault-template.html`; gallery styles and interactions live in this folder. The validator rejects animation files, missing assets, oversized images, duplicate IDs, stale hashes, and an incomplete file inventory.

The submitted generation prompts are in `meta/prompts.json`, the reusable character brief is in `meta/CHARACTER-PROMPT.md`, and the artwork notes are in `meta/ARTWORK.md`. Source images were generated with the built-in image generation tool; exports preserve their composition. Original full-resolution generation files and the old vault backup are stored outside the published website.
