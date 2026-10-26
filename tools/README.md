# Site tools

The site is plain HTML served by GitHub Pages; nothing builds on deploy. These
scripts are run by hand and their output is committed.

| Script | What it does |
|---|---|
| `build_site.py` | Writes the service pages (`services/`), city pages (`areas/`), project write-ups (`projects/`), every Spanish page (`es/`) and `sitemap.xml`. Also refreshes the SEO block (canonical, hreflang, Open Graph, JSON-LD schema) in the hand-written pages. Content lives in `site_data.py`. |
| `check_site.py` | Fails on broken links or images, invalid schema, missing titles/descriptions, duplicate titles, or hreflang pairs that don't match. CI runs it on every PR. |
| `optimize_images.py` | Makes `.webp` copies (and `-sm.webp` gallery thumbnails) of the JPEGs in `Project Images/2026` and `Project Images/jobs`. Needs Pillow. |

## Common edits

- **Change wording on a service, city or project page:** edit `site_data.py`, then `python3 tools/build_site.py`.
- **Edit index/services/portfolio/about/contact:** edit the HTML directly, but leave everything between `SEO:BEGIN` and `SEO:END` alone; run `build_site.py` afterwards so the Spanish links and schema stay in sync.
- **Add photos:** drop the JPEGs in, run `optimize_images.py`, and reference the `.webp` files.
- **Add a project write-up:** add its portfolio job id to `PROJECTS` in `site_data.py` (English and Spanish text), then rebuild.

Pages load `style.css`, `script.js` and `tracker.js` with a `?v=` hash of their contents, so visitors never get new HTML with an old cached stylesheet. **After editing any of those three files, run `build_site.py`** to bump the hash on every page.

Before pushing: `python3 tools/build_site.py --check && python3 tools/check_site.py`.
