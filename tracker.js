/* Andrade Construction LLC — visitor logger client.
   POSTs a small JSON blob to the Cloudflare Worker on each page load and again
   on unload (with session duration). The Worker forwards a Discord embed to
   the #andrade-construction channel. */
(function () {
  var W = 'https://andrade-visitor-logger.jacobhulk2002.workers.dev/';
  var sid;
  try {
    sid = localStorage.getItem('_sid');
    if (!sid) {
      sid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = crypto.getRandomValues(new Uint8Array(1))[0] % 16;
        return (c === 'x' ? r : r & 0x3 | 0x8).toString(16);
      });
      localStorage.setItem('_sid', sid);
    }
  } catch (e) { sid = 'x'; }

  var t0 = Date.now();

  function send(evt) {
    var d = {
      sid: sid, event: evt,
      screen: screen.width + 'x' + screen.height,
      viewport: window.innerWidth + 'x' + window.innerHeight,
      dpr: window.devicePixelRatio,
      tz: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
      lang: navigator.language,
      platform: navigator.platform,
      cores: navigator.hardwareConcurrency,
      mem: navigator.deviceMemory,
      touch: navigator.maxTouchPoints,
      referrer: document.referrer || 'direct',
      url: location.href,
      webdriver: !!navigator.webdriver,
      plugins: navigator.plugins.length,
      notChrome: typeof window.chrome === 'undefined',
      duration: Math.round((Date.now() - t0) / 1000)
    };
    try {
      fetch(W, {
        method: 'POST', keepalive: true, cache: 'no-store',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(d)
      });
    } catch (e) {}
  }

  if (document.readyState === 'complete') { send('load'); }
  else { window.addEventListener('load', function () { send('load'); }); }

  window.addEventListener('beforeunload', function () {
    try {
      navigator.sendBeacon(W, new Blob(
        [JSON.stringify({ sid: sid, event: 'unload', duration: Math.round((Date.now() - t0) / 1000), url: location.href })],
        { type: 'application/json' }
      ));
    } catch (e) {}
  });
})();
