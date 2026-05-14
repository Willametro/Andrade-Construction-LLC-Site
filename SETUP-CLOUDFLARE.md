# Setup walkthrough — Cloudflare Worker visitor logger

This site posts a small JSON blob to a Cloudflare Worker on every page load
(and unload). The Worker enriches the data with Cloudflare's edge geo/network
info and forwards a Discord embed to the `#andrade-construction` channel.

You need **one Worker for this site**. The Clean The Capital site uses a
separate Worker (different name, different channel) — same procedure, just
with that site's webhook URL.

---

## What you need

- A Cloudflare account (free tier — Workers free plan = 100,000 requests/day)
- The Discord webhook URL for the **#andrade-construction** channel:
  `https://discord.com/api/webhooks/1504513037338546267/HRtODd6KrE343jfAMZWO3RyCKUVPlwNtlKyTRUMCvhtrSGda6Ah8rplWsLz1I1bHZbnq`
  *(Keep this URL secret — it goes into a Cloudflare encrypted secret, never into source code.)*
- 10 minutes

---

## 1. Create the Worker (dashboard method)

1. Sign in at **https://dash.cloudflare.com**
2. Left sidebar → **Workers & Pages** → **Create application** → **Create Worker**
3. **Name:** `andrade-visitor-logger`
   - URL becomes `https://andrade-visitor-logger.<your-account>.workers.dev/`
   - `tracker.js` in this repo expects `andrade-visitor-logger.jacobhulk2002.workers.dev`. If your workers.dev subdomain is different, update line 6 of `tracker.js`.
4. Click **Deploy** to ship the boilerplate Worker (just to allocate the URL).

## 2. Replace the Worker source

1. Click **Edit code** (top right)
2. Delete everything in the editor
3. Paste the contents of **`cloudflare/worker.js`** from this repo
4. **Save and deploy**

## 3. Add the Discord webhook as a secret

The Worker reads the webhook URL from `env.DISCORD_WEBHOOK`. **Never** hard-code
the webhook in the source — anyone who reads the Worker could spam your channel.

1. Worker → **Settings** tab → **Variables and Secrets**
2. **Add** → set:
   - **Variable type:** `Secret` *(critical — not "plain text")*
   - **Variable name:** `DISCORD_WEBHOOK`
   - **Value:** `https://discord.com/api/webhooks/1504513037338546267/HRtODd6KrE343jfAMZWO3RyCKUVPlwNtlKyTRUMCvhtrSGda6Ah8rplWsLz1I1bHZbnq`
3. **Save**

## 4. (Optional) Lock down CORS

Default config accepts any origin. To restrict to production domains, edit `worker.js`:

```js
const allowed = ['https://andrade.construction', 'https://www.andrade.construction'];
const requestOrigin = request.headers.get('Origin') || '';
const origin = allowed.includes(requestOrigin) ? requestOrigin : 'null';
```

Redeploy. Skip for v1 — permissive makes local testing easier.

## 5. Verify

1. Open `https://andrade.construction/` in a private window
2. Within 1–3 seconds, a Discord embed should arrive in `#andrade-construction`:
   ```
   🔨 Visitor arrived
   Page:    https://andrade.construction/
   Geo:     Salem, Oregon, US
   IP:      ...
   Network: ...
   ```
3. Close the tab — a follow-up `👋 Visitor left` embed should arrive with session duration.

If silent, see **Troubleshooting** below.

---

## Deploy via wrangler CLI (alternative)

```bash
cd cloudflare
npm i -g wrangler
wrangler login
wrangler deploy
wrangler secret put DISCORD_WEBHOOK
# paste the webhook URL when prompted
```

## Privacy note

Visitors are not anonymized — full IP, geo, and fingerprinting fields are logged
to a private Discord channel. Fine for an LLC marketing site; revisit if you
ever publish a privacy policy that promises otherwise.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| No embeds in Discord | Worker **Logs** tab → if `env.DISCORD_WEBHOOK is undefined`, re-add the secret as **Secret** (not plain text). |
| `CORS error` in console | Worker URL in `tracker.js` doesn't match the deployed Worker URL. Compare carefully. |
| `Geo: unknown` | Request proxied through something that strips `request.cf`. Usually fine for real visitors. |
| Spammed by your own visits | Add an early-return in the Worker for your home IP. |
| Hit Cloudflare free tier | Won't happen on a small site. If it does, the $5/mo plan = 10M req/day. |

## Quick checklist

- [ ] Cloudflare account ready
- [ ] Worker `andrade-visitor-logger` deployed
- [ ] `worker.js` source pasted in and deployed
- [ ] `DISCORD_WEBHOOK` added as a **Secret** (not plain var)
- [ ] Test visit produces a Discord embed in `#andrade-construction`
- [ ] (Optional) CORS locked to production domains
