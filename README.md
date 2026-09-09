# ZYCLOPS — $ZYCL on Solana

One eye. Zero visibility.

Official site: https://zyclops.xyz/

## Live token

The project owner supplied these launch details on 9 September 2026:

- Network: Solana mainnet
- Quote token: SOL
- Transfer fee: 1% (100 basis points), confirmed in the Raydium mint record on 9 September 2026; network and swap fees may also apply.
- Exchange: Raydium
- Mint: `HmqgjXRp9jz7W233TZ4EvdmKgXWa6yp7ZQ7FX6Tn1BCL`
- Pool: `BkRJJB41cpg2KHGgUQcJwa2UP1NVR16agyWHv7mZ1vKY`
- Starting market cap: $5,000 **at launch**, not a current quote or liquidity figure
- X: https://x.com/zyclopssol
- Telegram: https://t.me/zyclopscoin

`token.json` records the official identifiers and trade links. Keep those values consistent with the homepage. Do not infer supply, holder counts, taxes, liquidity locks, ownership renunciation or current prices from the starting market cap.

## Website

Static HTML, CSS and JavaScript; no build dependencies. Run `python3 -m http.server 4174` and open http://localhost:4174/.

The homepage includes Raydium and Jupiter links, a SOL buying guide, copyable mint and pool addresses, the approved modern mascot, 12 downloadable memes, a playful expression test, and community links. Page motion has a pause control and respects reduced-motion preferences. Reading, navigation, buying links and artwork downloads remain available without JavaScript.

Artwork uses the owner's approved charcoal cyclops, one ivory-and-gold eye, a solid gold brow, black hoodie and short beard. The full-resolution coin PNG retains transparency and is below 2 MB. All previous shipped artwork has been retired. Historical sources are backed up outside the website.

## Media vault

The unlisted `/media-vault/` gallery contains the current modern collection. It is public by URL, not access-controlled. Search indexing is disabled with page metadata, robots.txt and Vercel headers. Bots should refresh `/media-vault/manifest.json` before selecting an asset.

The vault now contains 44 assets. The six-file Pairing Department pack is browsable at `/media-vault/?pack=stonk#library` and downloadable separately. It includes three Stonk-themed jokes, two reactions and one blank caption template. The original 38 modern assets remain available.

Rebuild the gallery, catalog and ZIP with `python3 scripts/build-media-vault.py` (requires Pillow for asset validation). See the vault's `BOT-README.md` and `meta/CHARACTER-PROMPT.md` for the schema and artwork direction.

Publishing uses the existing GitHub → Vercel setup for zyclops.xyz. `.vercelignore` keeps local source utilities and untracked archival sticker files out of deployment.
