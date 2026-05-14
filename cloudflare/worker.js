/* Cloudflare Worker — Andrade Construction visitor logger.
   Receives a POST from /tracker.js on the site, enriches with Cloudflare
   request.cf geo data, and forwards a Discord embed to the configured webhook.

   Deploy:  see ../SETUP-CLOUDFLARE.md
   Secret:  DISCORD_WEBHOOK  (set via `wrangler secret put` or dashboard) */

export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get('Origin') || '*';
    const corsHeaders = {
      'Access-Control-Allow-Origin': origin,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
      'Vary': 'Origin'
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405, headers: corsHeaders });
    }

    let data;
    try { data = await request.json(); }
    catch { return new Response('Bad JSON', { status: 400, headers: corsHeaders }); }

    const cf = request.cf || {};
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    const ua = request.headers.get('User-Agent') || 'unknown';

    const geoLine = [cf.city, cf.region, cf.country].filter(Boolean).join(', ') || 'unknown';
    const event = String(data.event || 'visit').toLowerCase();
    const isUnload = event === 'unload';

    const flags = [];
    if (data.webdriver)             flags.push(':warning: navigator.webdriver = true');
    if (data.notChrome)             flags.push(':warning: missing window.chrome');
    if (Number(data.plugins) === 0) flags.push(':warning: 0 plugins');
    if (/bot|crawler|spider|headless|curl|wget|python|java/i.test(ua)) flags.push(':warning: UA looks automated');

    const trim = (s, n) => (s && s.length > n ? s.slice(0, n - 1) + '…' : s || '—');

    const embed = {
      title: isUnload ? '👋 Visitor left' : '🔨 Visitor arrived',
      color: isUnload ? 0x7a7a7a : 0xff6b1a,
      timestamp: new Date().toISOString(),
      footer: { text: 'andrade.construction · visitor logger' },
      fields: [
        { name: 'Page',     value: '```' + trim(data.url || '?', 200) + '```', inline: false },
        { name: 'Geo',      value: geoLine + (cf.timezone ? ` (${cf.timezone})` : ''), inline: true },
        { name: 'IP',       value: '`' + ip + '`', inline: true },
        { name: 'Network',  value: (cf.asOrganization || 'unknown') + (cf.asn ? ` · AS${cf.asn}` : ''), inline: false },
        { name: 'Referrer', value: trim(data.referrer || 'direct', 200), inline: false },
        { name: 'User-Agent', value: '```' + trim(ua, 240) + '```', inline: false },
        { name: 'Device',   value: `${data.platform || '?'} · ${data.cores || '?'} cores · ${data.mem || '?'} GB · touch ${data.touch || 0}`, inline: false },
        { name: 'Screen → Viewport', value: `${data.screen || '?'} → ${data.viewport || '?'} (DPR ${data.dpr || '?'})`, inline: false },
        { name: 'Locale · TZ', value: `${data.lang || '?'} · ${data.tz || '?'}`, inline: true },
        { name: 'Session',  value: '`' + String(data.sid || '?').slice(0, 8) + '`', inline: true },
        { name: 'Duration', value: (data.duration || 0) + 's', inline: true }
      ]
    };
    if (flags.length) embed.fields.push({ name: 'Flags', value: flags.join('\n'), inline: false });

    if (env.DISCORD_WEBHOOK) {
      ctx.waitUntil(
        fetch(env.DISCORD_WEBHOOK, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ embeds: [embed] })
        }).catch(() => {})
      );
    }

    return new Response(null, { status: 204, headers: corsHeaders });
  }
};
