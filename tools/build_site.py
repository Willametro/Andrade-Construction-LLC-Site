#!/usr/bin/env python3
"""Build the generated parts of andrade.construction.

    python3 tools/build_site.py           # write pages
    python3 tools/build_site.py --check   # exit 1 if anything is out of date (CI)

What it writes:
  services/<slug>.html, areas/<city>.html, areas/index.html,
  projects/<job>.html                       English landing pages
  es/...                                    Spanish versions of every page
  sitemap.xml                               with hreflang alternates

What it patches in the hand-written pages (index, services, portfolio, about,
contact, legal/*): the SEO block in <head> between the SEO:BEGIN/SEO:END
markers (canonical, hreflang, Open Graph, JSON-LD), the EN/ES toggle, and
links to the new pages. Everything else in those files stays hand-edited.

Content lives in tools/site_data.py. Standard library only.
"""
import argparse
import hashlib
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_data import SITE, BUSINESS, SERVICES, CITIES, PROJECTS, CATEGORIES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
B = BUSINESS

# Pages load style.css / script.js / tracker.js as "?v=<hash of their contents>",
# so browsers and Cloudflare fetch the new files the moment they change instead
# of pairing new HTML with a cached old stylesheet.
ASSETS = ('style.css', 'script.js', 'tracker.js')
ASSET_V = hashlib.sha1(b''.join((ROOT / f).read_bytes() for f in ASSETS)).hexdigest()[:8]
ASSET_RE = re.compile(r'((?:href|src)="(?:/|\.\./)?(?:' + '|'.join(re.escape(f) for f in ASSETS) + r'))(?:\?v=[0-9a-f]*)?"')


def versioned(src):
    return ASSET_RE.sub(lambda m: f'{m.group(1)}?v={ASSET_V}"', src)


def t(s):
    """Escape text content."""
    return html.escape(s, quote=False)


def a(s):
    """Escape an attribute value."""
    return html.escape(s, quote=True)


def img(path):
    """Site-absolute URL for a file path that may contain spaces."""
    return '/' + urllib.parse.quote(path)


def file_for(url):
    rel = url.lstrip('/')
    return rel + 'index.html' if rel == '' or rel.endswith('/') else rel


# ── UI strings ────────────────────────────────────────────────────────────
UI = {
    'en': {
        'skip': 'Skip to main content', 'home': 'Home',
        'nav': [('Services', '/services.html'), ('Portfolio', '/portfolio.html'),
                ('About', '/about.html'), ('Contact', '/contact.html')],
        'estimate': 'Free Estimate', 'contact': '/contact.html', 'call_text': 'Call or Text',
        'call_anytime': 'Call or text anytime', 'hours_h': 'Hours', 'hours': 'Mon – Sun: 9 AM – 6 PM',
        'f_services': 'Services', 'f_company': 'Company', 'f_contact': 'Contact',
        'company': [('About Us', '/about.html'), ('Portfolio', '/portfolio.html'),
                    ('Service Areas', '/areas/'), ('Contact', '/contact.html'),
                    ('Privacy Policy', '/legal/privacy.html'), ('Terms of Service', '/legal/terms.html')],
        'tagline': 'Family-owned remodeling &amp; construction in the Salem, OR area since 2008.',
        'lic': 'Oregon CCB #182464 · Licensed · Bonded · Insured',
        'rights': 'Andrade Construction LLC. All rights reserved.',
        'privacy': 'Privacy', 'terms': 'Terms',
        'cta_h': 'Ready to Start Your Project?', 'cta_p': 'Contact us today for a free, no-pressure estimate.',
        'cta_btn': 'Get Free Estimate', 'cta_call': 'Call or Text (503) 999-9277',
        'services': 'Services', 'services_url': '/services.html',
        'portfolio': 'Portfolio', 'portfolio_url': '/portfolio.html',
        'areas': 'Service Areas', 'areas_url': '/areas/',
        'learn_more': 'Learn More', 'view_project': 'View Project', 'photos': 'photos',
        'start': 'Start', 'finish': 'Finish',
        'lang_label': 'Language', 'home_aria': 'Andrade Construction LLC — home',
        'mobile_call': 'Call / Text', 'toggle_nav': 'Toggle navigation',
        'close': 'Close image', 'prev': 'Previous image', 'next': 'Next image', 'viewer': 'Image viewer',
        'trust': [('⏳', 'Since 2008', 'Over 15 years of building and remodeling homes across the Salem area.'),
                  ('🪪', 'CCB Licensed', 'Oregon CCB #182464 — licensed, bonded, and insured for your protection.'),
                  ('👨‍👩‍👧', 'Family-Owned', 'Rudy and Pam Andrade run every job personally. Your home gets their full attention.'),
                  ('📋', 'Free Estimates', 'No-pressure, no-obligation estimates. We walk the job with you before anything is signed.')],
        'steps_h': 'How a Project Works', 'steps_eyebrow': 'What to Expect',
        'steps': [('Free estimate', 'Call, text or send the form. We walk the job with you in person, at no cost.'),
                  ('Honest number', 'You get the real price upfront: no hidden fees and no change orders you did not approve.'),
                  ('The build', 'Rudy leads the work on site, Pam keeps you updated, and we clean up at the end of every day.'),
                  ('Final walkthrough', 'We walk the finished project with you and make sure everything is right.')],
    },
    'es': {
        'skip': 'Saltar al contenido principal', 'home': 'Inicio',
        'nav': [('Servicios', '/es/servicios.html'), ('Portafolio', '/es/portafolio.html'),
                ('Nosotros', '/es/nosotros.html'), ('Contacto', '/es/contacto.html')],
        'estimate': 'Estimado Gratis', 'contact': '/es/contacto.html', 'call_text': 'Llame o Escriba',
        'call_anytime': 'Llame o envíe mensaje', 'hours_h': 'Horario', 'hours': 'Lun – Dom: 9 AM – 6 PM',
        'f_services': 'Servicios', 'f_company': 'Empresa', 'f_contact': 'Contacto',
        'company': [('Nosotros', '/es/nosotros.html'), ('Portafolio', '/es/portafolio.html'),
                    ('Áreas de Servicio', '/es/areas/'), ('Contacto', '/es/contacto.html'),
                    ('Política de Privacidad (inglés)', '/legal/privacy.html'), ('Términos de Servicio (inglés)', '/legal/terms.html')],
        'tagline': 'Construcción y remodelación familiar en el área de Salem, OR desde 2008.',
        'lic': 'Oregon CCB #182464 · Con Licencia · Fianza · Seguro',
        'rights': 'Andrade Construction LLC. Todos los derechos reservados.',
        'privacy': 'Privacidad', 'terms': 'Términos',
        'cta_h': '¿Listo para Comenzar su Proyecto?', 'cta_p': 'Contáctenos hoy para un estimado gratis y sin presión.',
        'cta_btn': 'Estimado Gratis', 'cta_call': 'Llame o Escriba (503) 999-9277',
        'services': 'Servicios', 'services_url': '/es/servicios.html',
        'portfolio': 'Portafolio', 'portfolio_url': '/es/portafolio.html',
        'areas': 'Áreas de Servicio', 'areas_url': '/es/areas/',
        'learn_more': 'Ver Más', 'view_project': 'Ver Proyecto', 'photos': 'fotos',
        'start': 'Inicio', 'finish': 'Final',
        'lang_label': 'Idioma', 'home_aria': 'Andrade Construction LLC — inicio',
        'mobile_call': 'Llamar', 'toggle_nav': 'Abrir menú',
        'close': 'Cerrar imagen', 'prev': 'Imagen anterior', 'next': 'Imagen siguiente', 'viewer': 'Visor de imágenes',
        'trust': [('⏳', 'Desde 2008', 'Más de 15 años construyendo y remodelando hogares en el área de Salem.'),
                  ('🪪', 'Licencia CCB', 'Oregon CCB #182464 — con licencia, fianza y seguro para su protección.'),
                  ('👨‍👩‍👧', 'Empresa Familiar', 'Rudy y Pam Andrade supervisan cada trabajo personalmente. Su hogar recibe toda su atención.'),
                  ('📋', 'Estimados Gratis', 'Estimados sin presión ni compromiso. Revisamos el trabajo con usted antes de firmar nada.')],
        'steps_h': 'Cómo Funciona un Proyecto', 'steps_eyebrow': 'Qué Esperar',
        'steps': [('Estimado gratis', 'Llame, escriba o envíe el formulario. Revisamos el trabajo con usted en persona, sin costo.'),
                  ('Precio honesto', 'Le damos el precio real desde el principio: sin cargos ocultos ni cambios que usted no haya aprobado.'),
                  ('La obra', 'Rudy dirige el trabajo en sitio, Pam le mantiene informado y limpiamos al final de cada día.'),
                  ('Revisión final', 'Revisamos con usted el proyecto terminado para asegurarnos de que todo esté bien.')],
    },
}

PHONE_SVG = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
             '<path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 10.8a19.79 19.79 0 01-3.07-8.7A2 2 0 012.18 0h3a2 '
             '2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.91 7.09a16 16 0 006 6l.46-.46a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 '
             '2 0 0122 14.92z"/></svg>')


# ── Data derived from portfolio.html ─────────────────────────────────────
def load_jobs():
    src = (ROOT / 'portfolio.html').read_text()
    jobs = {}
    for m in re.finditer(r'<article class="job-block" id="job-([^"]+)" data-cat="([^"]+)">(.*?)</article>', src, re.S):
        body = m.group(3)
        photos = [urllib.parse.unquote(p) for p in re.findall(r'data-src="([^"]+)"', body)]
        jobs[m.group(1)] = {
            'id': m.group(1), 'cat': m.group(2), 'photos': photos,
            'title': html.unescape(re.search(r'job-block__title">([^<]*)', body).group(1)),
        }
    return jobs


JOBS = load_jobs()
SVC = {s['slug']: s for s in SERVICES}
CITY = {c['slug']: c for c in CITIES}


def svc_url(s, lang):
    return f"/services/{s['slug']}.html" if lang == 'en' else f"/es/servicios/{s['es_slug']}.html"


def city_url(c, lang):
    return f"/areas/{c['slug']}.html" if lang == 'en' else f"/es/areas/{c['slug']}.html"


def proj_url(job_id, lang):
    return f'/projects/{job_id}.html' if lang == 'en' else f'/es/proyectos/{job_id}.html'


def job_link(job_id, lang):
    """Case-study page when there is one, otherwise the portfolio anchor."""
    if job_id in PROJECTS:
        return proj_url(job_id, lang)
    return f'/portfolio.html#job-{job_id}'


def jobs_for_service(s):
    ids = [j for j in JOBS if JOBS[j]['cat'] in s['cats']] + s['jobs']
    seen = []
    for j in ids:
        if j in JOBS and j not in seen:
            seen.append(j)
    # case studies first, keep order otherwise
    return sorted(seen, key=lambda j: j not in PROJECTS)


# ── JSON-LD ──────────────────────────────────────────────────────────────
def business_ld(lang):
    return {
        '@type': 'GeneralContractor',
        '@id': SITE + '/#business',
        'name': B['name'],
        'url': SITE + '/',
        'logo': SITE + '/logo.png',
        'image': SITE + '/og-image.jpg',
        'description': ('Family-owned remodeling and construction contractor in Salem, Oregon since 2008.'
                        if lang == 'en' else
                        'Contratista familiar de remodelación y construcción en Salem, Oregón, desde 2008.'),
        'telephone': '+1-503-999-9277',
        'email': B['email'],
        'foundingDate': B['founded'],
        'founder': [{'@type': 'Person', 'name': n} for n in B['founders']],
        'address': {'@type': 'PostalAddress', 'addressLocality': B['city'],
                    'addressRegion': B['region'], 'addressCountry': 'US'},
        'areaServed': ([{'@type': 'City', 'name': f'{c}, OR'} for c in B['area_cities']] +
                       [{'@type': 'AdministrativeArea', 'name': f'{c}, OR'} for c in B['counties']]),
        'openingHoursSpecification': {
            '@type': 'OpeningHoursSpecification',
            'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'opens': '09:00', 'closes': '18:00'},
        'knowsLanguage': ['en', 'es'],
        'hasCredential': {
            '@type': 'EducationalOccupationalCredential',
            'credentialCategory': 'license',
            'name': f"Oregon Construction Contractors Board license #{B['ccb']}",
            'recognizedBy': {'@type': 'GovernmentOrganization', 'name': 'Oregon Construction Contractors Board',
                             'url': 'https://www.oregon.gov/ccb/'}},
        'hasOfferCatalog': {
            '@type': 'OfferCatalog',
            'name': 'Services' if lang == 'en' else 'Servicios',
            'itemListElement': [{'@type': 'Offer', 'itemOffered': {
                '@type': 'Service', 'name': s[lang]['name'], 'url': SITE + svc_url(s, lang)}} for s in SERVICES]},
    }


def page_ld(page):
    lang = page['lang']
    url = SITE + page['url']
    graph = [business_ld(lang), {
        '@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': B['name'],
        'inLanguage': ['en-US', 'es-US'], 'publisher': {'@id': SITE + '/#business'}}]
    webpage = {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': page['title'],
               'description': page['desc'], 'inLanguage': 'en-US' if lang == 'en' else 'es-US',
               'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#business'}}
    if page.get('crumbs'):
        webpage['breadcrumb'] = {'@id': url + '#breadcrumb'}
        graph.append({'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': name, 'item': SITE + u}
            for i, (name, u) in enumerate(page['crumbs'])]})
    graph.insert(2, webpage)
    graph += page.get('ld', [])
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)
    return data.replace('</', '<\\/')


def seo_block(page, prefix=''):
    """Canonical, hreflang, Open Graph and JSON-LD. `prefix` is the relative
    path back to the site root for hand-written pages (icons only)."""
    lang = page['lang']
    url = SITE + page['url']
    lines = ['<!-- SEO:BEGIN — generated by tools/build_site.py; edit there, not here -->',
             f'<link rel="canonical" href="{a(url)}">']
    alt = page.get('alt', {})
    if 'en' in alt and 'es' in alt:
        lines += [f'<link rel="alternate" hreflang="en" href="{a(SITE + alt["en"])}">',
                  f'<link rel="alternate" hreflang="es" href="{a(SITE + alt["es"])}">',
                  f'<link rel="alternate" hreflang="x-default" href="{a(SITE + alt["en"])}">']
    og_img = SITE + page.get('og_image', '/og-image.jpg')
    lines += [
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{a(B["name"])}">',
        f'<meta property="og:locale" content="{"en_US" if lang == "en" else "es_US"}">',
        f'<meta property="og:locale:alternate" content="{"es_US" if lang == "en" else "en_US"}">',
        f'<meta property="og:title" content="{a(page["og_title"] if "og_title" in page else page["title"])}">',
        f'<meta property="og:description" content="{a(page["desc"])}">',
        f'<meta property="og:url" content="{a(url)}">',
        f'<meta property="og:image" content="{a(og_img)}">',
    ]
    if 'og_image' not in page:
        lines += ['<meta property="og:image:width" content="1200">',
                  '<meta property="og:image:height" content="630">',
                  f'<meta property="og:image:alt" content="{a(B["name"] + " — Salem, OR remodeling")}">']
    lines += ['<meta name="twitter:card" content="summary_large_image">',
              f'<link rel="icon" href="{prefix}favicon.ico" sizes="any">',
              f'<link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">']
    for h in page.get('preload', []):
        lines.append(f'<link rel="preload" as="image" href="{a(h)}">')
    lines += ['<script type="application/ld+json">' + page_ld(page) + '</script>',
              '<!-- SEO:END -->']
    return '\n'.join('  ' + ln for ln in lines)


# ── Shared chrome ────────────────────────────────────────────────────────
def lang_toggle(page):
    alt = page.get('alt', {})
    en = alt.get('en', '/')
    es = alt.get('es', '/es/')
    cur = page['lang']
    return ('<div class="lang-toggle" role="group" aria-label="Language / Idioma">\n'
            f'      <a href="{a(en)}" hreflang="en" lang="en"{" aria-current=\"true\"" if cur == "en" else ""}>EN</a>\n'
            f'      <a href="{a(es)}" hreflang="es" lang="es"{" aria-current=\"true\"" if cur == "es" else ""}>ES</a>\n'
            '    </div>')


def header(page):
    u = UI[page['lang']]
    nav = '\n'.join(f'        <li><a href="{a(href)}">{t(label)}</a></li>' for label, href in u['nav'])
    home = '/' if page['lang'] == 'en' else '/es/'
    return f'''<a class="skip-link" href="#main">{t(u['skip'])}</a>

<header class="site-header" role="banner">
  <div class="container site-header__inner">

    <a href="{home}" class="brand" aria-label="{a(u['home_aria'])}">
      <span class="brand__mark" aria-hidden="true">A</span>
      <span class="brand__name">
        ANDRADE
        <small>Construction LLC</small>
      </span>
    </a>

    <nav class="site-nav" role="navigation" aria-label="{'Main navigation' if page['lang'] == 'en' else 'Navegación principal'}">
      <ul>
{nav}
      </ul>
    </nav>

    <a href="tel:{B['phone_e164']}" class="header-phone" aria-label="{a(u['call_text'] + ' ' + B['phone_display'])}">
      {PHONE_SVG.replace('18', '16')}
      {B['phone_display']}
    </a>

    <a href="{u['contact']}" class="btn btn--primary header-cta">{t(u['estimate'])}</a>

    {lang_toggle(page)}

    <button class="nav-toggle" aria-expanded="false" aria-label="{a(u['toggle_nav'])}">
      <span></span><span></span><span></span>
    </button>

  </div>
</header>'''


def footer(lang):
    u = UI[lang]
    svcs = '\n'.join(f'          <li><a href="{svc_url(s, lang)}">{t(s[lang]["name"])}</a></li>' for s in SERVICES)
    comp = '\n'.join(f'          <li><a href="{href}">{t(label)}</a></li>' for label, href in u['company'])
    home = '/' if lang == 'en' else '/es/'
    return f'''<footer class="site-footer" role="contentinfo">
  <div class="container">
    <div class="footer-grid">

      <div>
        <a href="{home}" class="brand" style="margin-bottom:1rem;display:inline-flex;">
          <span class="brand__mark" aria-hidden="true">A</span>
          <span class="brand__name" style="color:#fff;">ANDRADE<small style="color:rgba(255,255,255,.6)">Construction LLC</small></span>
        </a>
        <p style="margin-top:.75rem">{u['tagline']}</p>
        <p style="font-size:.82rem;color:rgba(255,255,255,.55);margin-top:.5rem">{u['lic']}</p>
      </div>

      <div>
        <h4>{t(u['f_services'])}</h4>
        <ul>
{svcs}
        </ul>
      </div>

      <div>
        <h4>{t(u['f_company'])}</h4>
        <ul>
{comp}
        </ul>
      </div>

      <div>
        <h4>{t(u['f_contact'])}</h4>
        <ul>
          <li>
            <a href="tel:{B['phone_e164']}">📞 {B['phone_display']}</a><br>
            <span style="font-size:.82rem;color:rgba(255,255,255,.5)">{t(u['call_anytime'])}</span>
          </li>
          <li style="margin-top:.75rem">
            <a href="mailto:{B['email']}">✉ {B['email']}</a>
          </li>
          <li style="margin-top:.75rem">
            <strong style="color:#fff;">{t(u['hours_h'])}</strong><br>
            {t(u['hours'])}
          </li>
        </ul>
      </div>

    </div>

    <div class="footer-bottom">
      <span>© <span id="yr">2026</span> {t(u['rights'])}</span>
      <span>
        <a href="/legal/privacy.html">{t(u['privacy'])}</a> ·
        <a href="/legal/terms.html">{t(u['terms'])}</a>
      </span>
    </div>
  </div>
</footer>

<div class="mobile-actions" role="navigation" aria-label="Quick contact">
  <a href="tel:{B['phone_e164']}" aria-label="{a(u['call_text'] + ' ' + B['phone_display'])}">
    {PHONE_SVG}
    {t(u['mobile_call'])}
  </a>
  <a href="{u['contact']}" class="is-primary">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
    {t(u['estimate'])}
  </a>
</div>

<div class="lightbox" role="dialog" aria-modal="true" aria-label="{a(u['viewer'])}">
  <img src="" alt="">
  <button class="lightbox__close" aria-label="{a(u['close'])}">✕</button>
  <button class="lightbox__prev" aria-label="{a(u['prev'])}">‹</button>
  <button class="lightbox__next" aria-label="{a(u['next'])}">›</button>
</div>'''


GTM_HEAD = '''  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  })(window,document,'script','dataLayer','GTM-W3HV966K');</script>
  <!-- End Google Tag Manager -->'''

GTM_BODY = '''<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-W3HV966K"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->'''


def render(page):
    return f'''<!DOCTYPE html>
<html lang="{page['lang']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t(page['title'])}</title>
  <meta name="description" content="{a(page['desc'])}">
{seo_block(page, '/')}

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500;600;700&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">

{GTM_HEAD}

  <link rel="stylesheet" href="/style.css">
{page.get('head_extra', '')}
  <script defer src="/tracker.js"></script>
</head>
<body>

{GTM_BODY}

<!-- Generated by tools/build_site.py from tools/site_data.py. Edit those, then rebuild. -->
{header(page)}

<main id="main">
{page['body']}
</main>

{footer(page['lang'])}

<script>document.getElementById('yr').textContent = new Date().getFullYear();</script>
<script src="/script.js"></script>
</body>
</html>
'''


# ── Building blocks ──────────────────────────────────────────────────────
def crumbs_html(crumbs):
    items = []
    for i, (name, url) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            items.append(f'<li aria-current="page">{t(name)}</li>')
        else:
            items.append(f'<li><a href="{a(url)}">{t(name)}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def page_hero(eyebrow, h1, lede, crumbs=None, extra=''):
    bc = crumbs_html(crumbs) if crumbs else ''
    return f'''
  <div class="page-hero">
    <div class="container">
      {bc}
      <p class="eyebrow" style="color:var(--orange)">{t(eyebrow)}</p>
      <h1>{t(h1)}</h1>
      <p>{t(lede)}</p>{extra}
    </div>
  </div>'''


def section_head(eyebrow, h2, center=True, sub=''):
    cls = 'section-head section-head--center' if center else 'section-head'
    sub_html = f'\n        <p style="color:var(--steel)">{t(sub)}</p>' if sub else ''
    return f'''      <div class="{cls}">
        <p class="eyebrow">{t(eyebrow)}</p>
        <h2>{t(h2)}</h2>{sub_html}
      </div>'''


def card(href, image, title, text, more):
    return f'''        <a href="{a(href)}" class="service-card">
          <div class="service-card__img" style="background-image:url('{a(img(image))}')" role="img" aria-label="{a(title)}"></div>
          <div class="service-card__body">
            <h3>{t(title)}</h3>
            <p>{t(text)}</p>
            <span class="service-card__more" aria-hidden="true">{t(more)} →</span>
          </div>
        </a>'''


def service_cards(lang, exclude=None):
    u = UI[lang]
    return '\n'.join(card(svc_url(s, lang), s['image'], s[lang]['name'], s[lang]['lede'], u['learn_more'])
                     for s in SERVICES if s['slug'] != exclude)


def project_card(job_id, lang):
    job = JOBS[job_id]
    p = PROJECTS.get(job_id)
    title = p[lang]['title'] if p else job['title']
    sub = p[lang]['sub'] if p else f"{len(job['photos'])} {UI[lang]['photos']}"
    return card(job_link(job_id, lang), job['photos'][-1], title, sub, UI[lang]['view_project'])


def cta_banner(lang):
    u = UI[lang]
    return f'''
  <section class="cta-banner" aria-label="Call to action">
    <div class="container">
      <h2>{t(u['cta_h'])}</h2>
      <p>{t(u['cta_p'])}</p>
      <div class="cta-banner__buttons">
        <a href="{u['contact']}" class="btn btn--primary btn--lg">
          <span>{t(u['cta_btn'])}</span>
          <span class="arrow" aria-hidden="true">→</span>
        </a>
        <a href="tel:{B['phone_e164']}" class="btn btn--ghost btn--lg">
          {PHONE_SVG}
          <span>{t(u['cta_call'])}</span>
        </a>
      </div>
    </div>
  </section>'''


def trust_grid(lang):
    items = '\n'.join(f'''        <div class="trust-item">
          <div class="trust-item__icon" aria-hidden="true">{icon}</div>
          <h3>{t(h)}</h3>
          <p>{t(p)}</p>
        </div>''' for icon, h, p in UI[lang]['trust'])
    return f'      <div class="trust-grid">\n{items}\n      </div>'


def steps(lang):
    u = UI[lang]
    items = '\n'.join(f'        <li><strong>{t(h)}</strong><p>{t(p)}</p></li>' for h, p in u['steps'])
    return f'''
  <section class="section section--cream">
    <div class="container">
{section_head(u['steps_eyebrow'], u['steps_h'])}
      <ol class="steps">
{items}
      </ol>
    </div>
  </section>'''


def area_pills(lang, only=None):
    pills = []
    linked = {c['name']: c for c in CITIES}
    names = only or B['area_cities']
    for name in names:
        if name in linked:
            pills.append(f'<a role="listitem" href="{city_url(linked[name], lang)}">{t(name)}</a>')
        else:
            pills.append(f'<span role="listitem">{t(name)}</span>')
    label = 'Cities and communities served' if lang == 'en' else 'Ciudades y comunidades que atendemos'
    joined = '\n        '.join(pills)
    return f'''      <div class="area-pills" role="list" aria-label="{a(label)}">
        {joined}
      </div>'''


def gallery(job_id, lang):
    job = JOBS[job_id]
    u = UI[lang]
    title = PROJECTS[job_id][lang]['title']
    n = len(job['photos'])
    out = []
    for i, p in enumerate(job['photos'], 1):
        step = u['start'] if i == 1 else u['finish'] if i == n else str(i)
        thumb = p[:-len('.webp')] + '-sm.webp'
        out.append(f'''        <a class="gallery__item" role="listitem" href="{a(img(p))}"
           data-src="{a(img(p))}" data-label="{a(f'{title} — {i} / {n}')}"
           aria-label="{a(f'{title}, {i} / {n}')}">
          <span class="gallery__item__step">{t(step)}</span>
          <img src="{a(img(thumb))}" alt="{a(f'{title} — {step}')}" loading="lazy">
        </a>''')
    return '      <div class="job-gallery" role="list">\n' + '\n'.join(out) + '\n      </div>'


# ── Generated pages ──────────────────────────────────────────────────────
def service_page(s, lang):
    u = UI[lang]
    d = s[lang]
    url = svc_url(s, lang)
    crumbs = [(u['home'], '/' if lang == 'en' else '/es/'), (u['services'], u['services_url']), (d['name'], url)]
    bullets = '\n'.join(f'          <li>{t(b)}</li>' for b in d['bullets'])
    jobs = jobs_for_service(s)[:6]
    what = 'What We Do' if lang == 'en' else 'Lo Que Hacemos'
    proj_h = ('Recent Projects', f"{d['name']} Projects") if lang == 'en' else ('Proyectos Recientes', f"Proyectos de {d['name']}")
    more_port = 'See the full portfolio' if lang == 'en' else 'Ver el portafolio completo'
    area_h = ('Service Area', f"{d['name']} Near You") if lang == 'en' else ('Área de Servicio', f"{d['name']} Cerca de Usted")
    area_note = (f"Based in Salem and serving Marion, Polk, Yamhill, Linn and Benton counties. Free, in-person estimates."
                 if lang == 'en' else
                 'Con base en Salem, atendemos los condados de Marion, Polk, Yamhill, Linn y Benton. Estimados gratis y en persona.')
    other_h = ('More Services', 'Other Work We Do') if lang == 'en' else ('Más Servicios', 'Otros Trabajos que Hacemos')
    body = page_hero(u['services'], d['title'], d['lede'], crumbs) + f'''

  <section class="section">
    <div class="container split">
      <div>
        <p class="eyebrow">{t(what)}</p>
        <h2>{t(d['name'])}</h2>
        <p>{t(d['intro'])}</p>
        <ul class="check-list">
{bullets}
        </ul>
        <a href="{u['contact']}" class="btn btn--primary" style="margin-top:1rem">
          {t(u['cta_btn'])} <span class="arrow" aria-hidden="true">→</span>
        </a>
      </div>
      <div class="split__img" style="background-image:url('{a(img(s['image']))}')" role="img" aria-label="{a(d['name'])}"></div>
    </div>
  </section>
{steps(lang)}'''
    if jobs:
        cards = '\n'.join(project_card(j, lang) for j in jobs)
        body += f'''

  <section class="section">
    <div class="container">
{section_head(proj_h[0], proj_h[1])}
      <div class="service-grid">
{cards}
      </div>
      <div class="text-center mt-2">
        <a href="{u['portfolio_url']}" class="btn btn--outline">{t(more_port)} <span class="arrow" aria-hidden="true">→</span></a>
      </div>
    </div>
  </section>'''
    body += f'''

  <section class="section section--cream">
    <div class="container">
{section_head(area_h[0], area_h[1])}
{area_pills(lang)}
      <p class="area-note">{t(area_note)}</p>
    </div>
  </section>

  <section class="section">
    <div class="container">
{section_head(other_h[0], other_h[1])}
      <div class="service-grid">
{service_cards(lang, exclude=s['slug'])}
      </div>
    </div>
  </section>
{cta_banner(lang)}'''
    ld = [{'@type': 'Service', '@id': SITE + url + '#service', 'name': d['name'], 'serviceType': s['en']['name'],
           'description': d['desc'], 'url': SITE + url, 'image': SITE + img(s['image']),
           'provider': {'@id': SITE + '/#business'},
           'areaServed': [{'@type': 'City', 'name': f'{c}, OR'} for c in B['area_cities']]}]
    return {'lang': lang, 'url': url, 'alt': {'en': svc_url(s, 'en'), 'es': svc_url(s, 'es')},
            'title': d['title'] + ' | Andrade Construction', 'og_title': d['title'], 'desc': d['desc'],
            'crumbs': crumbs, 'body': body, 'ld': ld, 'og_image': img(s['image']).replace('.webp', '.jpg')}


def city_page(c, lang):
    u = UI[lang]
    name = c['name']
    url = city_url(c, lang)
    crumbs = [(u['home'], '/' if lang == 'en' else '/es/'), (u['areas'], u['areas_url']), (name, url)]
    if lang == 'en':
        h1 = f'Remodeling Contractor in {name}, Oregon'
        lede = f'Family-owned since 2008 · Oregon CCB #{B["ccb"]} · Free, in-person estimates in {name}.'
        title = f'{name}, OR Remodeling Contractor | Andrade Construction'
        desc = (f'Bathroom and kitchen remodels, water damage repair, additions, decks, flooring and painting in {name}, OR '
                f'({c["county"]}). Family-owned, CCB #{B["ccb"]}. Free estimates: {B["phone_display"]}.')
        about = (f'Andrade Construction LLC is a family-owned remodeling contractor based in Salem and licensed by the Oregon '
                 f'Construction Contractors Board (CCB #{B["ccb"]}). We serve {name} and the rest of {c["county"]} with the same '
                 'crew, the same standards and the same free, no-pressure estimates. We speak English and Spanish.')
        svc_h = ('Services', f'What We Do in {name}')
        proj_h = ('Our Work', f'Projects in {name}' if c['jobs'] else 'Featured Projects')
        why_h = ('Why Andrade', f'Why {name} Homeowners Choose Us')
        near_h = ('Nearby', 'Other Areas We Serve')
        all_areas = 'All service areas'
    else:
        h1 = f'Contratista de Remodelación en {name}, Oregón'
        lede = f'Empresa familiar desde 2008 · Oregon CCB #{B["ccb"]} · Estimados gratis y en persona en {name}.'
        title = f'Contratista de Remodelación en {name}, OR | Andrade Construction'
        desc = (f'Remodelación de baños y cocinas, reparación por daño de agua, ampliaciones, terrazas, pisos y pintura en {name}, OR '
                f'({c["county_es"]}). Empresa familiar, CCB #{B["ccb"]}. Estimados gratis: {B["phone_display"]}.')
        about = (f'Andrade Construction LLC es una empresa familiar de remodelación con base en Salem y licencia de la Junta de '
                 f'Contratistas de Construcción de Oregón (CCB #{B["ccb"]}). Atendemos {name} y el resto de {c["county_es"]} con el '
                 'mismo equipo, los mismos estándares y los mismos estimados gratis y sin presión. Hablamos inglés y español.')
        svc_h = ('Servicios', f'Lo Que Hacemos en {name}')
        proj_h = ('Nuestro Trabajo', f'Proyectos en {name}' if c['jobs'] else 'Proyectos Destacados')
        why_h = ('Por Qué Andrade', f'Por Qué Nos Eligen en {name}')
        near_h = ('Cerca', 'Otras Áreas que Atendemos')
        all_areas = 'Todas las áreas de servicio'
    jobs = c['jobs'] or ['kitchen-favorites', 'basement-bathroom', 'exterior-repairs-paint']
    nearby = [CITY[n] for n in c['nearby']]
    near_pills = '\n        '.join(f'<a role="listitem" href="{city_url(n, lang)}">{t(n["name"])}</a>' for n in nearby)
    body = page_hero(u['areas'], h1, lede, crumbs) + f'''

  <section class="section">
    <div class="container prose">
      <p>{t(c[lang])}</p>
      <p>{t(about)}</p>
      <p><a href="{u['contact']}" class="btn btn--primary">{t(u['cta_btn'])} <span class="arrow" aria-hidden="true">→</span></a></p>
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{section_head(*svc_h)}
      <div class="service-grid">
{service_cards(lang)}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
{section_head(*proj_h)}
      <div class="service-grid">
{chr(10).join(project_card(j, lang) for j in jobs)}
      </div>
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{section_head(*why_h)}
{trust_grid(lang)}
    </div>
  </section>

  <section class="section">
    <div class="container">
{section_head(*near_h)}
      <div class="area-pills" role="list">
        {near_pills}
        <a role="listitem" href="{u['areas_url']}">{t(all_areas)}</a>
      </div>
    </div>
  </section>
{cta_banner(lang)}'''
    return {'lang': lang, 'url': url, 'alt': {'en': city_url(c, 'en'), 'es': city_url(c, 'es')},
            'title': title, 'og_title': h1, 'desc': desc, 'crumbs': crumbs, 'body': body}


def areas_index(lang):
    u = UI[lang]
    url = u['areas_url']
    crumbs = [(u['home'], '/' if lang == 'en' else '/es/'), (u['areas'], url)]
    if lang == 'en':
        h1, lede = 'Service Areas', 'Remodeling and construction across the Mid-Willamette Valley, based in Salem since 2008.'
        title = 'Service Areas: Salem, Keizer & the Mid-Valley | Andrade Construction'
        desc = ('Andrade Construction serves Salem, Keizer, Woodburn, Silverton, Stayton, Dallas, Independence, Monmouth and '
                'communities across Marion, Polk, Yamhill, Linn and Benton counties. CCB #182464.')
        intro = ('We primarily serve Marion, Polk, Yamhill, Linn, and Benton counties. We take projects outside this radius, '
                 'so call to discuss your location. Pick your city for local details.')
        h2 = ('Where We Work', 'Cities We Serve')
    else:
        h1, lede = 'Áreas de Servicio', 'Remodelación y construcción en el Valle Medio de Willamette, con base en Salem desde 2008.'
        title = 'Áreas de Servicio: Salem, Keizer y el Valle Medio | Andrade Construction'
        desc = ('Andrade Construction atiende Salem, Keizer, Woodburn, Silverton, Stayton, Dallas, Independence, Monmouth y '
                'comunidades de los condados de Marion, Polk, Yamhill, Linn y Benton. CCB #182464.')
        intro = ('Servimos principalmente los condados de Marion, Polk, Yamhill, Linn y Benton. También tomamos proyectos fuera '
                 'de esta área, así que llámenos para consultar. Elija su ciudad para ver más detalles.')
        h2 = ('Dónde Trabajamos', 'Ciudades que Atendemos')
    cards = '\n'.join(
        card(city_url(c, lang),
             JOBS[c['jobs'][0]]['photos'][-1] if c['jobs'] else SERVICES[i % len(SERVICES)]['image'],
             f'{c["name"]}, OR', c[lang].split('. ')[0] + '.', u['learn_more'])
        for i, c in enumerate(CITIES))
    body = page_hero(u['areas'], h1, lede, crumbs) + f'''

  <section class="section">
    <div class="container">
{section_head(*h2, sub=intro)}
      <div class="service-grid">
{cards}
      </div>
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{area_pills(lang)}
    </div>
  </section>
{cta_banner(lang)}'''
    return {'lang': lang, 'url': url, 'alt': {'en': '/areas/', 'es': '/es/areas/'},
            'title': title, 'og_title': h1, 'desc': desc, 'crumbs': crumbs, 'body': body}


def project_page(job_id, lang):
    u = UI[lang]
    p = PROJECTS[job_id]
    d = p[lang]
    job = JOBS[job_id]
    s = SVC[p['service']]
    url = proj_url(job_id, lang)
    crumbs = [(u['home'], '/' if lang == 'en' else '/es/'), (u['portfolio'], u['portfolio_url']), (d['title'], url)]
    cat = CATEGORIES[job['cat']][lang]
    n = len(job['photos'])
    loc = p.get('location')
    meta = [f'<span>{t(cat)}</span>', f'<span>{n} {t(u["photos"])}</span>']
    if loc:
        meta.append(f'<span>📍 {t(loc)}</span>')
    meta.append(f'<a href="{svc_url(s, lang)}">{t(s[lang]["name"])} →</a>')
    extra = '\n      <div class="project-meta">' + ' '.join(meta) + '</div>'
    if lang == 'en':
        title = f'{d["title"]}{" in " + loc if loc and "Keizer" not in d["title"] else ""} | Andrade Construction Project'
        desc = f'{d["title"]}: {d["sub"]}. {n} photos from start to finish by Andrade Construction LLC, Salem, OR (CCB #{B["ccb"]}).'
        over_h, photo_h = ('The Project', 'Overview'), ('Photos', 'Start to Finish')
        photo_sub = 'Click any photo to enlarge it.'
        rel_h = ('More Projects', f'More {s["en"]["name"]} Work')
        svc_line = f'Planning something similar? See our {s["en"]["name"].lower()} services or ask for a free estimate.'
    else:
        title = f'{d["title"]} | Proyecto de Andrade Construction'
        desc = f'{d["title"]}: {d["sub"]}. {n} fotos de principio a fin por Andrade Construction LLC, Salem, OR (CCB #{B["ccb"]}).'
        over_h, photo_h = ('El Proyecto', 'Resumen'), ('Fotos', 'De Principio a Fin')
        photo_sub = 'Haga clic en cualquier foto para ampliarla.'
        rel_h = ('Más Proyectos', f'Más Trabajos de {s["es"]["name"]}')
        svc_line = f'¿Planea algo similar? Vea nuestros servicios de {s["es"]["name"].lower()} o pida un estimado gratis.'
    related = [j for j in jobs_for_service(s) if j != job_id and j in PROJECTS][:3]
    body = page_hero(cat, d['title'], d['sub'], crumbs, extra) + f'''

  <section class="section">
    <div class="container prose">
      <p class="eyebrow">{t(over_h[0])}</p>
      <h2>{t(over_h[1])}</h2>
      <p>{t(d['body'])}</p>
      <p>{t(svc_line)}</p>
      <p>
        <a href="{svc_url(s, lang)}" class="btn btn--outline">{t(s[lang]['name'])} <span class="arrow" aria-hidden="true">→</span></a>
        <a href="{u['contact']}" class="btn btn--primary">{t(u['cta_btn'])} <span class="arrow" aria-hidden="true">→</span></a>
      </p>
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{section_head(*photo_h, sub=photo_sub)}
      <div class="job-block__progress"><span>{'Before' if lang == 'en' else 'Antes'}</span><span style="margin-left:auto">{'After' if lang == 'en' else 'Después'}</span></div>
{gallery(job_id, lang)}
    </div>
  </section>'''
    if related:
        body += f'''

  <section class="section">
    <div class="container">
{section_head(*rel_h)}
      <div class="service-grid">
{chr(10).join(project_card(j, lang) for j in related)}
      </div>
    </div>
  </section>'''
    body += cta_banner(lang)
    finish = job['photos'][-1]
    jpg = finish[:-len('.webp')] + '.jpg'
    return {'lang': lang, 'url': url, 'alt': {'en': proj_url(job_id, 'en'), 'es': proj_url(job_id, 'es')},
            'title': title, 'og_title': d['title'], 'desc': desc, 'crumbs': crumbs, 'body': body,
            'og_image': img(jpg)}


# ── Spanish versions of the hand-written core pages ─────────────────────
def es_home():
    u = UI['es']
    featured = ['kitchen-favorites', 'basement-bathroom', 'kitchen-keizer', 'bath-curbless-shower', 'exterior-repairs-paint', 'custom-hidden-doors']
    ba = [('kitchen1', 'Remodelación Completa de Cocina — Salem, OR', 'Cocina antes de la remodelación — gabinetes de maple',
           'Cocina después — gabinetes grises, isla negra y campana de acero', 'wide'),
          ('bath2', 'Remodelación de Baño — Regadera de Entrada Directa', 'Baño antes — encimera de madera y azulejo antiguo',
           'Baño después — regadera de azulejo gris y tocador de madera', 'wide')]
    sliders = '\n'.join(f'''        <div class="beforeafter beforeafter--{shape}" role="img" aria-label="Antes y después — {a(cap)}. Arrastre para comparar.">
          <img class="ba-before" src="/Project%20Images/2026/before-after/{key}-before.webp" alt="{a(alt_b)}" loading="lazy">
          <img class="ba-after"  src="/Project%20Images/2026/before-after/{key}-after.webp"  alt="{a(alt_a)}" loading="lazy">
          <div class="beforeafter__divider"></div>
          <div class="beforeafter__handle" role="presentation" aria-hidden="true">⟺</div>
          <span class="beforeafter__label beforeafter__label--before">Antes</span>
          <span class="beforeafter__label beforeafter__label--after">Después</span>
          <div class="beforeafter__caption">{t(cap)}</div>
        </div>''' for key, cap, alt_b, alt_a, shape in ba)
    body = f'''
  <section class="hero" aria-label="Portada">
    <div class="container hero__inner">
      <h1>Construido Bien.<br>Para Durar.</h1>
      <p class="hero__lede">Remodelación y construcción familiar en el área de Salem desde 2008. Remodelaciones, ampliaciones y restauraciones, hechas como deben hacerse.</p>
      <div class="hero__ctas">
        <a href="/es/contacto.html" class="btn btn--primary btn--lg">
          <span>Obtener Estimado Gratis</span>
          <span class="arrow" aria-hidden="true">→</span>
        </a>
        <a href="tel:{B['phone_e164']}" class="btn btn--ghost btn--lg">
          {PHONE_SVG}
          <span>Llame o Escriba {B['phone_display']}</span>
        </a>
      </div>
      <div class="hero__trust">
        <span><span class="check">✓</span> <span>CCB #182464</span></span>
        <span><span class="check">✓</span> <span>Con Licencia, Fianza y Seguro</span></span>
        <span><span class="check">✓</span> <span>Estimados Gratis</span></span>
        <span><span class="check">✓</span> <span>Hablamos Español</span></span>
      </div>
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{section_head('Lo Que Hacemos', 'Artesanía Experta en Cada Proyecto', center=False)}
      <div class="service-grid">
{service_cards('es')}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
{section_head('Nuestro Trabajo', 'Proyectos Recientes', center=False)}
      <div class="service-grid">
{chr(10).join(project_card(j, 'es') for j in featured)}
      </div>
      <div class="text-center mt-2">
        <a href="/es/portafolio.html" class="btn btn--outline">Ver Portafolio Completo <span class="arrow" aria-hidden="true">→</span></a>
      </div>
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{section_head('Transformaciones', 'Vea la Diferencia', sub='Arrastre el control (o toque y deslice) para ver el después.')}
      <div class="beforeafter-grid">
{sliders}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
{section_head('Por Qué Andrade', 'Un Nombre en el Que Puede Confiar')}
{trust_grid('es')}
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{section_head('Área de Servicio', 'Sirviendo la Región de Salem')}
{area_pills('es')}
      <p class="area-note">Servimos principalmente los condados de Marion, Polk, Yamhill, Linn y Benton. También tomamos proyectos fuera de esta área; llámenos para consultar.</p>
    </div>
  </section>
{cta_banner('es')}'''
    return {'lang': 'es', 'url': '/es/', 'alt': {'en': '/', 'es': '/es/'},
            'title': 'Andrade Construction LLC — Remodelación y Construcción en Salem, OR',
            'og_title': 'Andrade Construction LLC',
            'desc': ('Remodelación y construcción familiar en el área de Salem, Oregón, desde 2008. Baños, cocinas, ampliaciones y '
                     'reparación por daño de agua. CCB #182464. Estimados gratis: (503) 999-9277. Hablamos español.'),
            'body': body, 'preload': ['/Project%20Images/2026/hero/kitchen-maple-marble.webp']}


def es_services():
    u = UI['es']
    blocks = []
    for s in SERVICES:
        d = s['es']
        bl = '\n'.join(f'            <li>{t(b)}</li>' for b in d['bullets'])
        blocks.append(f'''      <div class="service-block" id="{s['anchor']}">
        <div class="service-block__img" style="background-image:url('{a(img(s['image']))}')" role="img" aria-label="{a(d['name'])}"></div>
        <div>
          <p class="eyebrow">{t(d['name'])}</p>
          <h2>{t(d['name'])}</h2>
          <p>{t(d['intro'])}</p>
          <ul>
{bl}
          </ul>
          <p class="service-block__more"><a href="{svc_url(s, 'es')}">Más sobre {t(d['name'].lower())} →</a></p>
          <a href="/es/contacto.html" class="btn btn--primary" style="margin-top:1rem">
            Obtener Estimado Gratis <span class="arrow" aria-hidden="true">→</span>
          </a>
        </div>
      </div>''')
    crumbs = [(u['home'], '/es/'), (u['services'], '/es/servicios.html')]
    body = page_hero('Lo Que Hacemos', 'Nuestros Servicios',
                     'Construcción y remodelación familiar en el área de Salem desde 2008. Cada proyecto, grande o pequeño, recibe el mismo cuidado y calidad.',
                     crumbs) + f'''

  <section class="section">
    <div class="container">
{chr(10).join(blocks)}
    </div>
  </section>
{cta_banner('es')}'''
    return {'lang': 'es', 'url': '/es/servicios.html', 'alt': {'en': '/services.html', 'es': '/es/servicios.html'},
            'title': 'Servicios — Andrade Construction LLC | Salem, OR', 'og_title': 'Servicios — Andrade Construction LLC',
            'desc': ('Remodelación de baños y cocinas, restauración por daño de agua, ampliaciones, terrazas, pisos, pintura y '
                     'carpintería en el área de Salem, OR. CCB #182464. Llame al (503) 999-9277.'),
            'crumbs': crumbs, 'body': body}


def es_about():
    u = UI['es']
    crumbs = [(u['home'], '/es/'), ('Nosotros', '/es/nosotros.html')]
    creds = [('#182464', 'Licencia CCB de Oregón'), ('2008', 'Año de Fundación'), ('15+', 'Años en el Negocio'), ('100%', 'Empresa Familiar')]
    cred_html = '\n'.join(f'''        <div class="cred">
          <span class="cred__num">{c}</span>
          <span class="cred__label">{t(lbl)}</span>
        </div>''' for c, lbl in creds)
    values = [('🤝', 'Estimados Honestos', 'Le damos el precio real desde el principio: sin cargos ocultos, sin cambios que usted no haya aprobado y sin sorpresas al final.'),
              ('📅', 'Llegamos a Tiempo', 'Respetamos su tiempo. Si decimos que llegamos a las 8 AM, llegamos a las 8 AM, con horarios constantes durante todo su proyecto.'),
              ('🧹', 'Obras Limpias', 'Limpiamos al final de cada día de trabajo. Usted vive en su casa y la tratamos con ese respeto.'),
              ('💬', 'Comunicación Clara', 'Siempre sabrá cómo va su proyecto. Pam le mantiene informado para que nunca se quede con dudas.')]
    val_html = '\n'.join(f'''        <div class="trust-item">
          <div class="trust-item__icon" aria-hidden="true">{i}</div>
          <h3>{t(h)}</h3>
          <p>{t(p)}</p>
        </div>''' for i, h, p in values)
    body = page_hero('Quiénes Somos', 'Sobre Andrade Construction',
                     'Empresa familiar en el área de Salem desde 2008. Tratamos cada proyecto, y a cada cliente, como quisiéramos que trataran nuestra propia casa.',
                     crumbs) + f'''

  <section class="section">
    <div class="container split">
      <div>
        <p class="eyebrow">Nuestra Historia</p>
        <h2>Construida en Familia, con Oficio</h2>
        <p>Andrade Construction LLC fue fundada en 2008 por Rudy y Pam Andrade con una idea sencilla: tratar a cada cliente como a un vecino y cada casa como si fuera la propia. Lo que empezó como una pequeña empresa de remodelación se ha convertido en un nombre de confianza en construcción residencial en el área de Salem.</p>
        <p>En más de 15 años hemos trabajado en los condados de Marion, Polk, Yamhill y alrededores, desde baños de un solo cuarto hasta transformaciones de casas completas. Construimos nuestra reputación proyecto por proyecto.</p>
        <p>Rudy dirige el trabajo en sitio todos los días, y Pam coordina los proyectos, la comunicación con los clientes y el calendario. Cuando contrata a Andrade, trata directamente con los dueños.</p>
      </div>
      <div class="split__img" style="aspect-ratio:4/5;background-image:url('/Project%20Images/2026/hero/kitchen-maple-marble.webp')" role="img" aria-label="Cocina remodelada por Andrade Construction"></div>
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{section_head('Credenciales', 'Con Licencia, Fianza y Seguro', sub='Mantenemos todas las credenciales requeridas por el estado de Oregón para que usted esté protegido en cada proyecto.')}
      <div class="creds-grid">
{cred_html}
      </div>
      <div style="max-width:680px;margin:2.5rem auto 0;text-align:center">
        <p>Nuestra licencia de contratista de Oregón (CCB #182464) está activa y vigente. Contamos con fianza y seguro de responsabilidad civil y de compensación laboral. Podemos mostrarle comprobantes antes de comenzar cualquier proyecto.</p>
        <a href="https://www.oregon.gov/ccb/Pages/verify.aspx" target="_blank" rel="noopener noreferrer" class="btn btn--outline" style="margin-top:1rem">Verificar Nuestra Licencia CCB →</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
{section_head('Cómo Trabajamos', 'Lo Que Nos Distingue')}
      <div class="trust-grid">
{val_html}
      </div>
    </div>
  </section>

  <section class="section section--cream">
    <div class="container">
{section_head('Área de Servicio', 'Sirviendo la Región de Salem')}
{area_pills('es')}
      <p class="area-note">Servimos principalmente los condados de Marion, Polk, Yamhill, Linn y Benton. También tomamos proyectos fuera de esta área; llámenos para consultar.</p>
    </div>
  </section>
{cta_banner('es')}'''
    return {'lang': 'es', 'url': '/es/nosotros.html', 'alt': {'en': '/about.html', 'es': '/es/nosotros.html'},
            'title': 'Nosotros — Andrade Construction LLC | Salem, OR', 'og_title': 'Nosotros — Andrade Construction LLC',
            'desc': ('Empresa familiar de remodelación y construcción en Salem, OR, desde 2008. Rudy y Pam Andrade — Oregon CCB #182464, '
                     'con licencia, fianza y seguro.'),
            'crumbs': crumbs, 'body': body}


def es_contact():
    u = UI['es']
    crumbs = [(u['home'], '/es/'), ('Contacto', '/es/contacto.html')]
    style = re.search(r'<style>.*?</style>', (ROOT / 'contact.html').read_text(), re.S).group(0)
    opts = [('Bathroom Remodel', 'Remodelación de baño'), ('Kitchen Remodel', 'Remodelación de cocina'),
            ('Water Damage Restoration', 'Restauración por daño de agua'), ('Home Addition', 'Ampliación'),
            ('Deck / Outdoor', 'Terraza / exteriores'), ('Flooring', 'Pisos'), ('Full Home Remodel', 'Remodelación completa'),
            ('Other', 'Otro / no estoy seguro')]
    opt_html = '\n'.join(f'                <option value="{a(v)}">{t(lbl)}</option>' for v, lbl in opts)
    body = page_hero('Contáctenos', 'Estimado Gratis y Contacto',
                     '¿Listo para empezar? Llene el formulario o comuníquese directamente. Le respondemos el mismo día.',
                     crumbs) + f'''

  <section class="section">
    <div class="container">
      <div class="contact-split">

        <div>
          <p class="eyebrow">Pida un Estimado Gratis</p>
          <h2 style="margin-bottom:1.5rem">Cuéntenos Sobre Su Proyecto</h2>
          <form class="lead-form" action="{B['formspree']}" method="POST" enctype="multipart/form-data" novalidate>
            <input type="hidden" name="language" value="es">
            <div class="hp-field" aria-hidden="true">
              <label for="hp_name">Deje esto en blanco</label>
              <input type="text" id="hp_name" name="_gotcha" tabindex="-1" autocomplete="off">
            </div>
            <div class="lead-form__row">
              <div class="field">
                <label for="fname">Nombre <span class="req" aria-label="obligatorio">*</span></label>
                <input type="text" id="fname" name="first_name" required autocomplete="given-name">
              </div>
              <div class="field">
                <label for="lname">Apellido <span class="req" aria-label="obligatorio">*</span></label>
                <input type="text" id="lname" name="last_name" required autocomplete="family-name">
              </div>
            </div>
            <div class="lead-form__row">
              <div class="field">
                <label for="phone">Teléfono <span class="req" aria-label="obligatorio">*</span></label>
                <input type="tel" id="phone" name="phone" required autocomplete="tel" placeholder="(503) 555-0100">
              </div>
              <div class="field">
                <label for="email">Correo electrónico</label>
                <input type="email" id="email" name="email" autocomplete="email" placeholder="usted@ejemplo.com">
              </div>
            </div>
            <div class="field">
              <label for="address">Ciudad o código postal del proyecto <span class="req" aria-label="obligatorio">*</span></label>
              <input type="text" id="address" name="project_location" required placeholder="Salem, OR 97301">
            </div>
            <div class="field">
              <label for="service">Tipo de proyecto <span class="req" aria-label="obligatorio">*</span></label>
              <select id="service" name="project_type" required>
                <option value="">— Seleccione un servicio —</option>
{opt_html}
              </select>
            </div>
            <div class="lead-form__row">
              <div class="field">
                <label for="budget">Presupuesto aproximado</label>
                <select id="budget" name="budget">
                  <option value="">— Opcional —</option>
                  <option value="Under $10k">Menos de $10,000</option>
                  <option value="$10k-$25k">$10,000 – $25,000</option>
                  <option value="$25k-$75k">$25,000 – $75,000</option>
                  <option value="$75k+">$75,000 o más</option>
                  <option value="Not Sure">No estoy seguro</option>
                </select>
              </div>
              <div class="field">
                <label for="timeline">¿Cuándo quiere empezar?</label>
                <select id="timeline" name="timeline">
                  <option value="">— Opcional —</option>
                  <option value="ASAP">Lo antes posible</option>
                  <option value="1-3 months">En 1 a 3 meses</option>
                  <option value="3-6 months">En 3 a 6 meses</option>
                  <option value="Just Exploring">Solo estoy explorando</option>
                </select>
              </div>
            </div>
            <div class="field">
              <label for="message">Descripción del proyecto</label>
              <textarea id="message" name="message" placeholder="Cuéntenos qué necesita, cualquier reto y lo que espera lograr..."></textarea>
            </div>
            <div class="field">
              <label for="photos">Fotos del proyecto o de inspiración (opcional)</label>
              <input type="file" id="photos" name="photos" accept="image/*" multiple>
            </div>
            <div class="consent">
              <input type="checkbox" id="sms_opt" name="sms_opt_in" value="yes">
              <label for="sms_opt">Acepto recibir mensajes de texto al número proporcionado. Pueden aplicar tarifas de mensajes y datos. Responda STOP para dejar de recibirlos en cualquier momento.</label>
            </div>
            <button type="submit" class="btn btn--primary btn--lg btn--block">
              Enviar Mi Solicitud <span class="arrow" aria-hidden="true">→</span>
            </button>
            <p class="form-note">Respondemos el mismo día en horario de trabajo. Nunca vendemos ni compartimos su información. <a href="/legal/privacy.html">Política de Privacidad</a> (en inglés).</p>
          </form>
        </div>

        <div class="contact-info">
          <p class="eyebrow">Comuníquese Directamente</p>
          <h2 style="margin-bottom:1rem">Con Gusto le Atendemos</h2>
          <p style="color:var(--steel)">¿Prefiere llamar o escribir? Hable directamente con Rudy o Pam: sin centro de llamadas ni esperas, solo las personas que harán el trabajo.</p>
          <div class="contact-direct-btns">
            <a href="tel:{B['phone_e164']}" aria-label="Llamar al {B['phone_display']}">
              <span class="icon" aria-hidden="true">{PHONE_SVG}</span>
              <span><strong>{B['phone_display']}</strong><small>Llame o escriba — 9 AM a 6 PM, 7 días</small></span>
            </a>
            <a href="mailto:{B['email']}" aria-label="Escribir a {B['email']}">
              <span class="icon" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              </span>
              <span><strong>{B['email']}</strong><small>Respondemos en pocas horas</small></span>
            </a>
          </div>
          <dl>
            <dt>Horario</dt>
            <dd>Lunes a domingo, 9 AM – 6 PM</dd>
            <dt>Área de servicio</dt>
            <dd>Salem y alrededores, hasta una hora de distancia, y más lejos según el proyecto</dd>
            <dt>Licencia CCB</dt>
            <dd>#182464 · Con licencia, fianza y seguro</dd>
            <dt>Idiomas</dt>
            <dd>Español e inglés</dd>
          </dl>
          <div style="margin-top:2rem;padding:1.25rem;background:var(--orange-soft);border:1.5px solid var(--orange);border-radius:var(--radius)">
            <strong style="font-family:var(--font-display);font-size:1.05rem;">Estimados Gratis</strong>
            <p style="margin:.5rem 0 0;font-size:.92rem;color:var(--charcoal)">Todos los estimados son gratis, sin compromiso y en persona. Revisamos el trabajo con usted antes de firmar nada.</p>
          </div>
        </div>

      </div>
    </div>
  </section>'''
    return {'lang': 'es', 'url': '/es/contacto.html', 'alt': {'en': '/contact.html', 'es': '/es/contacto.html'},
            'title': 'Contacto y Estimado Gratis — Andrade Construction LLC | Salem, OR',
            'og_title': 'Contacto — Andrade Construction LLC',
            'desc': ('Pida un estimado gratis a Andrade Construction LLC. Llame o escriba al (503) 999-9277 o llene nuestro '
                     'formulario. Contratista de remodelación en Salem, OR, CCB #182464. Hablamos español.'),
            'crumbs': crumbs, 'body': body, 'head_extra': '  ' + style}


def es_portfolio():
    u = UI['es']
    crumbs = [(u['home'], '/es/'), ('Portafolio', '/es/portafolio.html')]
    sections = []
    for cat, labels in CATEGORIES.items():
        ids = [j for j in PROJECTS if JOBS[j]['cat'] == cat]
        if not ids:
            continue
        sections.append(f'''
  <section class="section{' section--cream' if len(sections) % 2 else ''}">
    <div class="container">
{section_head('Portafolio', labels['es'], center=False)}
      <div class="service-grid">
{chr(10).join(project_card(j, 'es') for j in ids)}
      </div>
    </div>
  </section>''')
    body = page_hero('Nuestro Trabajo', 'Portafolio',
                     'Proyectos reales en el área de Salem, con fotos de cada trabajo de principio a fin.', crumbs) + \
        ''.join(sections) + f'''

  <section class="section">
    <div class="container text-center">
      <p>Vea todas las fotos, incluidos más proyectos, en el <a href="/portfolio.html" hreflang="en">portafolio completo</a> (en inglés).</p>
    </div>
  </section>
{cta_banner('es')}'''
    return {'lang': 'es', 'url': '/es/portafolio.html', 'alt': {'en': '/portfolio.html', 'es': '/es/portafolio.html'},
            'title': 'Portafolio — Andrade Construction LLC | Salem, OR', 'og_title': 'Portafolio — Andrade Construction LLC',
            'desc': ('Remodelaciones de baños y cocinas, pintura, revestimiento, pisos y más en el área de Salem, Oregón. '
                     'Fotos de cada proyecto de principio a fin. CCB #182464.'),
            'crumbs': crumbs, 'body': body}


# ── Hand-written English pages ──────────────────────────────────────────
HAND = {
    'index.html': {'url': '/', 'es': '/es/', 'preload': ['Project%20Images/2026/hero/kitchen-maple-marble.webp']},
    'services.html': {'url': '/services.html', 'es': '/es/servicios.html', 'crumb': 'Services'},
    'portfolio.html': {'url': '/portfolio.html', 'es': '/es/portafolio.html', 'crumb': 'Portfolio'},
    'about.html': {'url': '/about.html', 'es': '/es/nosotros.html', 'crumb': 'About'},
    'contact.html': {'url': '/contact.html', 'es': '/es/contacto.html', 'crumb': 'Contact'},
}
LEGAL = ['legal/privacy.html', 'legal/terms.html']

STRIP_HEAD = re.compile(r'^\s*<(?:link rel="canonical"|meta property="og:[^"]*"|meta name="twitter:[^"]*"|'
                        r'link rel="icon"|link rel="apple-touch-icon")[^>]*>\s*\n', re.M)
SEO_RE = re.compile(r'  <!-- SEO:BEGIN.*?<!-- SEO:END -->', re.S)
TOGGLE_RE = re.compile(r'<div class="lang-toggle"[^>]*>.*?</div>', re.S)


def patch_common(src, page, prefix):
    src = versioned(src)
    src = TOGGLE_RE.sub(lambda m: lang_toggle(page), src, count=1)
    # service anchors -> dedicated pages
    for s in SERVICES:
        src = re.sub(rf'href="((?:\.\./)?)services\.html#{s["anchor"]}"', rf'href="\1services/{s["slug"]}.html"', src)
    # footer: Service Areas link after Portfolio
    if 'areas/">Service Areas</a>' not in src:
        src = re.sub(r'(<li><a href="((?:\.\./)?)portfolio\.html">Portfolio</a></li>)',
                     r'\1\n          <li><a href="\2areas/">Service Areas</a></li>', src, count=1)
    return src


def patch_hand(path, cfg):
    src = (ROOT / path).read_text()
    title = html.unescape(re.search(r'<title>(.*?)</title>', src, re.S).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', src).group(1))
    page = {'lang': 'en', 'url': cfg['url'], 'alt': {'en': cfg['url'], 'es': cfg['es']},
            'title': title, 'desc': desc, 'preload': cfg.get('preload', [])}
    og_title = re.search(r'<meta property="og:title" content="([^"]*)"', src)
    if og_title:
        page['og_title'] = html.unescape(og_title.group(1))
    if 'crumb' in cfg:
        page['crumbs'] = [('Home', '/'), (cfg['crumb'], cfg['url'])]
    block = seo_block(page)
    if SEO_RE.search(src):
        # keep the og:title chosen when the block was first inserted
        prev = re.search(r'<meta property="og:title" content="([^"]*)"', SEO_RE.search(src).group(0))
        if prev:
            page['og_title'] = html.unescape(prev.group(1))
            block = seo_block(page)
        src = SEO_RE.sub(lambda m: block, src, count=1)
    else:
        src = STRIP_HEAD.sub('', src)
        src = re.sub(r'(<meta name="description"[^>]*>\n)', lambda m: m.group(1) + block + '\n', src, count=1)
    src = patch_common(src, page, '')

    city_names = {c['name']: c for c in CITIES}
    for name, c in city_names.items():
        src = src.replace(f'<span role="listitem">{name}</span>',
                          f'<a role="listitem" href="areas/{c["slug"]}.html">{name}</a>')

    if path == 'services.html':
        for s in SERVICES:
            m = re.search(rf'<div class="service-block" id="{s["anchor"]}">.*?</ul>\n', src, re.S)
            link = f'services/{s["slug"]}.html'
            if m and link not in m.group(0) and link not in src[m.end():m.end() + 200]:
                ins = (f'          <p class="service-block__more"><a href="{link}">'
                       f'More about {t(s["en"]["name"].lower())} →</a></p>\n')
                src = src[:m.end()] + ins + src[m.end():]
    if path == 'portfolio.html':
        for job_id in PROJECTS:
            m = re.search(rf'<article class="job-block" id="job-{job_id}".*?<p class="job-block__sub">[^<]*</p>\n', src, re.S)
            link = f'projects/{job_id}.html'
            if m and link not in src[m.end():m.end() + 200]:
                src = src[:m.end()] + (f'          <a class="job-block__link" href="{link}">'
                                       'Read the project write-up →</a>\n') + src[m.end():]
    return src


def patch_legal(path):
    src = (ROOT / path).read_text()
    page = {'lang': 'en', 'url': '/' + path, 'alt': {'en': '/' + path, 'es': '/es/'}}
    return patch_common(src, page, '../')


# ── Sitemap ─────────────────────────────────────────────────────────────
def sitemap(pages):
    rows = []
    for p in sorted(pages, key=lambda p: (p['url'].startswith('/es/'), p['url'])):
        alt = p.get('alt', {})
        links = ''
        if 'en' in alt and 'es' in alt:
            links = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{lg}" href="{SITE}{alt[lg]}"/>' for lg in ('en', 'es'))
            links += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{alt["en"]}"/>'
        rows.append(f'  <url>\n    <loc>{SITE}{p["url"]}</loc>{links}\n  </url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')


def build():
    out = {}
    pages = []
    for path, cfg in HAND.items():
        out[path] = patch_hand(path, cfg)
        pages.append({'url': cfg['url'], 'alt': {'en': cfg['url'], 'es': cfg['es']}})
    for path in LEGAL:
        out[path] = patch_legal(path)
    gen = [es_home(), es_services(), es_about(), es_contact(), es_portfolio(), areas_index('en'), areas_index('es')]
    for lang in ('en', 'es'):
        gen += [service_page(s, lang) for s in SERVICES]
        gen += [city_page(c, lang) for c in CITIES]
        gen += [project_page(j, lang) for j in PROJECTS]
    for p in gen:
        out[file_for(p['url'])] = versioned(render(p))
        pages.append(p)
    out['sitemap.xml'] = sitemap(pages)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='fail if any output is out of date')
    args = ap.parse_args()
    missing = [j for j in PROJECTS if j not in JOBS]
    if missing:
        sys.exit(f'PROJECTS refers to jobs missing from portfolio.html: {missing}')
    out = build()
    stale = []
    for rel, content in out.items():
        f = ROOT / rel
        if not f.exists() or f.read_text() != content:
            stale.append(rel)
            if not args.check:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(content)
    if args.check:
        if stale:
            print('Out of date (run python3 tools/build_site.py):\n  ' + '\n  '.join(stale))
            sys.exit(1)
        print(f'All {len(out)} generated files are up to date.')
    else:
        print(f'Wrote {len(stale)} of {len(out)} files.')


if __name__ == '__main__':
    main()
