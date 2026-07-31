# Andrade Construction Site — SEO/Performance Work: Decisions Log & Open Items

This documents the second round of work on the SEO/performance overhaul (branch `seo-perf-improvements`, PR #1 on GitHub). For every open question raised after the first round, I either (a) made a best-practice call and applied it, or (b) left it alone because it genuinely needs your input, business records, or account access. This file explains which is which and why, so future updates (by me or anyone else) have the reasoning on record.

**Keep this file in the repo** (it's committed at `/DECISIONS.md`) so it survives as project memory, not just a one-time download.

---

## Decisions made and applied

### CCB #182464 — verified
Checked against BuildZoom's aggregated Oregon CCB data (a third-party mirror of the state database, since the official `ccb.state.or.us` search portal isn't scriptable). As of December 2025: **status Active**, bonded for $15,000 through Western Surety Company, insured for $1,000,000 general liability through Preferred Contractors Insurance. This matches what the site already claims. *Recommend a quick spot-check on the official state portal periodically* since license status can change and it's now baked into structured data on every page.

### City landing pages — built 1, not 18
I checked the actual portfolio data instead of guessing. Only **Keizer** has a real, photographed, named project (the "Keizer Kitchen Remodel" job block, 12 photos). Every other city in the service-area list has zero project evidence — it's just the area we say we cover. Building 17 near-identical thin city pages with swapped city names is a well-known Google spam pattern ("doorway pages") that can hurt rankings rather than help. So: **one strong Keizer page** (`keizer-or-remodeling-contractor.html`), built around the real project, with an honest FAQ. Additional city pages should only get built once there's a real photographed job in that city to anchor them — that's organic, defensible growth instead of manufactured content.

### Dedicated service pages — built 4 of 10
Split out the four highest search-intent services into their own pages, each with unique title/meta, an FAQ block with schema, a real photo gallery, and `Service` + `BreadcrumbList` structured data:
- `bathroom-remodeling-salem-or.html`
- `kitchen-remodeling-salem-or.html`
- `water-damage-restoration-salem-or.html`
- `home-additions-salem-or.html`

The other 6 services (decks, flooring, full remodels, painting, siding, carpentry) still live on `services.html` as before — nothing was removed, and `services.html` now links out to the 4 dedicated pages ("Read the full guide →") while remaining the hub for everything else. All internal links (nav-adjacent footer lists, homepage service cards) were updated to point at the new pages; the old `services.html#anchor` links still work too since the anchor sections are untouched.

**Content note:** the paragraph/bullet copy on these pages was drafted by me, closely following what was already on `services.html` (same claims, same scope — I did not invent new capabilities, warranties, or specifics). The FAQ answers are all restatements of facts already on the site (licensing, free estimates, insurance-claim support, etc.), not new claims. Worth a quick read-through since it's now your public-facing copy, but nothing here should surprise you.

### Portfolio restructuring — not done
Left `portfolio.html` as a single page rather than splitting it into category pages. It's already lazy-loaded and, post-WebP-conversion (see PR #1), reasonably fast. Splitting it is a bigger, riskier markup change for less lead-gen upside than the service/city pages above. Revisit if the page ever feels slow in practice.

### Spanish pages — built 3 of 5 (real, indexable pages)
Built `/es/index.html`, `/es/services.html`, and `/es/contact.html` as genuine standalone Spanish pages — not the old JS text-swap, which Google never indexed. Added proper `hreflang` tags (`en`/`es`/`x-default`) on both language versions so Google knows they're translations of each other, not duplicate content. The homepage's language toggle now does real navigation to the Spanish site instead of an in-place partial text swap.

Did **not** build Spanish versions of `about.html`, the portfolio, or the 4 new dedicated service pages / Keizer page — that's a larger translation job I scoped down to the 3 highest-traffic pages (home, services overview, contact/lead form) to keep this batch shippable. The English `script.js` translation strings (already used for the old toggle) formed the base for the homepage; the services and contact pages needed new Spanish copy I wrote directly.

**Translation quality flag:** I'm not a certified bilingual reviewer. The translations follow the register and phrasing already established in the site's own `script.js` (which reads as solid, professionally-written Spanish, not machine output), and I self-checked for leftover English and broken links programmatically. But this is customer-facing content tied to licensing/legal language (CCB #, SMS consent text) — **I'd recommend a quick native-speaker read-through before or shortly after this goes live**, especially the SMS opt-in consent line and form field labels on `/es/contact.html`.

### `tracker.js` — kept, now disclosed
Decided to keep the visitor-logging script (it's functioning infrastructure you're presumably using for lead awareness) rather than rip it out, but the privacy policy never actually disclosed what it collects — screen/viewport size, timezone, browser language, device signals, referrer, and time-on-page, sent to a Discord channel via a Cloudflare Worker. Added an accurate "Internal visitor log" disclosure to `legal/privacy.html` and bumped the "Last updated" date. No behavior changed, just honesty about what's already happening.

### `priceRange` in structured data — kept as `$$`
Used as a reasonable placeholder for a mid-market residential remodeling contractor in the JSON-LD. Change it in the `hasCredential`/business block on every page if `$` or `$$$` fits better — it's a cosmetic Google-facing signal, not a real pricing commitment.

### `og-image.jpg` — kept as generated
The branded share-image (kitchen photo + logo mark + tagline) generated in the first round is live. No changes made here since nothing new came up requiring a swap.

---

## What I could NOT decide for you — genuinely open

These need either information only you have, an account I don't have access to, or a judgment call about the business that isn't mine to make.

### 1. Real client testimonials
Still the biggest trust-signal gap. The testimonials section is disabled (commented out in the code, not deleted) rather than showing fake quotes. **A ready-to-send review-request text is at the bottom of this file** — send it to a handful of recent happy clients, then send me (or paste into) the actual quotes and I'll re-enable the section with real content and matching Google review schema.

### 2. Google Business Profile / Facebook page URLs
If you have a claimed Google Business Profile or a Facebook business page, send me the URLs. I'll add them to the site's structured data (`sameAs` field) — this is a real, if modest, local-SEO signal, and I didn't want to guess or fabricate a link.

### 3. Cloudflare Pages migration
The repo already has `SETUP-CLOUDFLARE.md` and a commented-out Cloudflare Web Analytics snippet. Moving off GitHub Pages to Cloudflare Pages would get you real cache control, redirects, and analytics — but needs your Cloudflare account. Let me know when you want to do this and I can walk through it with you or do it directly if you hand off temporary access.

### 4. Formspree as the long-term lead form
Not touched — it's working infrastructure. Flagging only because it's the single point of failure for every "Get a Free Estimate" submission on the site. Worth occasionally checking your Formspree dashboard for spam volume or missed submissions.

### 5. GTM conversion tracking
I don't have access to your Google Tag Manager container (`GTM-W3HV966K`). If you want form-submit and click-to-call conversions tracked (so you can actually see which channels produce leads), that needs either GTM access from you or a spec I write up for whoever manages it.

---

## Review-request text template

Use this to solicit the real testimonials from item #1 above. Send individually (not a mass blast) to clients from finished jobs, ideally within a week or two of project completion when it's freshest:

> Hi [Name], it's Rudy/Pam from Andrade Construction — hope you're still loving the [kitchen/bathroom/etc.]! If you have 60 seconds, a quick Google review would mean a lot to our small business and helps other homeowners in the area find us: [Google review link]. Thank you either way — it was great working with you!

Once you have 3–5 real quotes (from Google reviews or direct messages), send them over — I'll re-enable the testimonials section with real content, proper attribution (first name + project type + city, matching what's already on the page design), and Review/AggregateRating structured data if you have enough volume to support it honestly.

---

*Generated as part of the SEO/performance work on branch `seo-perf-improvements`. See PR #1 on GitHub for the full commit history and file-level detail.*
