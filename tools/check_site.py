#!/usr/bin/env python3
"""Static checks for the site. Run:  python3 tools/check_site.py

Fails (exit 1) on:
  - a local link, image or stylesheet that points at a missing file
  - a link to a #fragment that does not exist on the target page
  - JSON-LD that is not valid JSON
  - an indexable page missing <title>, meta description, canonical or exactly one <h1>
  - two indexable pages sharing a title or description
  - hreflang alternates that do not point back at each other
  - a sitemap URL with no matching file
Standard library only.
"""
import json
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://andrade.construction'
SKIP_DIRS = {'.git', 'Project Images', 'cloudflare', 'tools', 'node_modules'}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.ld, self.alts = [], set(), [], {}
        self.title = self.desc = self.canonical = None
        self.h1 = 0
        self.robots = ''
        self._in = None
        self._buf = ''

    def handle_starttag(self, tag, attrs):
        at = dict(attrs)
        if 'id' in at:
            self.ids.add(at['id'])
        for key in ('href', 'src', 'data-src'):
            if at.get(key):
                self.refs.append(at[key])
        for m in re.finditer(r"url\(['\"]?([^'\")]+)", at.get('style', '')):
            self.refs.append(m.group(1))
        if tag == 'h1':
            self.h1 += 1
        if tag == 'meta' and at.get('name') == 'description':
            self.desc = at.get('content')
        if tag == 'meta' and at.get('name') == 'robots':
            self.robots = at.get('content', '')
        if tag == 'link' and at.get('rel') == 'canonical':
            self.canonical = at.get('href')
        if tag == 'link' and at.get('rel') == 'alternate' and at.get('hreflang'):
            self.alts[at['hreflang']] = at.get('href')
        if tag == 'title' or (tag == 'script' and at.get('type') == 'application/ld+json'):
            self._in, self._buf = tag, ''

    def handle_data(self, data):
        if self._in:
            self._buf += data

    def handle_endtag(self, tag):
        if tag == self._in:
            if tag == 'title':
                self.title = self._buf.strip()
            else:
                self.ld.append(self._buf)
            self._in = None


def html_files():
    for p in sorted(ROOT.rglob('*.html')):
        rel = p.relative_to(ROOT)
        if not SKIP_DIRS.intersection(rel.parts):
            yield p


def url_for(path):
    rel = path.relative_to(ROOT).as_posix()
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('index.html')]
    return '/' + rel


def resolve(ref, page_path):
    """Map a reference to (file Path, fragment) or None for external refs."""
    if ref.startswith(SITE):
        ref = ref[len(SITE):] or '/'
    if ref == '#' or re.match(r'^(?:[a-z]+:|//)', ref):
        return None
    ref, _, frag = ref.partition('#')
    ref = ref.split('?')[0]
    if ref == '':
        return page_path, frag
    ref = urllib.parse.unquote(ref)
    target = ROOT / ref.lstrip('/') if ref.startswith('/') else page_path.parent / ref
    target = Path(str(target.resolve()))
    if ref.endswith('/'):
        target = target / 'index.html'
    return target, frag


def main():
    errors = []
    pages = {p: Page() for p in html_files()}
    for p, parsed in pages.items():
        parsed.feed(p.read_text())

    seen_titles, seen_desc = {}, {}
    for p, pg in pages.items():
        rel = p.relative_to(ROOT).as_posix()
        for ref in pg.refs:
            r = resolve(ref, p)
            if not r:
                continue
            target, frag = r
            if not target.exists():
                errors.append(f'{rel}: broken reference {ref}')
            elif frag and target.suffix == '.html' and target in pages and frag not in pages[target].ids:
                errors.append(f'{rel}: missing anchor {ref}')
        for block in pg.ld:
            try:
                json.loads(block)
            except ValueError as e:
                errors.append(f'{rel}: invalid JSON-LD ({e})')
        if rel.startswith('legal/'):
            continue  # disallowed in robots.txt
        if not pg.title:
            errors.append(f'{rel}: no <title>')
        if not pg.desc:
            errors.append(f'{rel}: no meta description')
        if pg.canonical != SITE + url_for(p):
            errors.append(f'{rel}: canonical is {pg.canonical}, expected {SITE + url_for(p)}')
        if pg.h1 != 1:
            errors.append(f'{rel}: {pg.h1} <h1> elements')
        if not pg.ld:
            errors.append(f'{rel}: no JSON-LD')
        for key, seen, val in (('title', seen_titles, pg.title), ('description', seen_desc, pg.desc)):
            if val and val in seen:
                errors.append(f'{rel}: same {key} as {seen[val]}')
            seen[val] = rel
        # hreflang reciprocity
        for lang, href in pg.alts.items():
            r = resolve(href, p)
            if not r or not r[0].exists():
                errors.append(f'{rel}: hreflang {lang} points at missing {href}')
                continue
            other = pages.get(r[0])
            if other and lang != 'x-default' and other.alts and other.alts.get(lang) != href:
                errors.append(f'{rel}: hreflang {lang} -> {href}, but that page lists {other.alts.get(lang)}')
            if other and SITE + url_for(p) not in other.alts.values():
                errors.append(f'{rel}: {href} does not link back with hreflang')

    sitemap = (ROOT / 'sitemap.xml').read_text()
    for loc in re.findall(r'<loc>([^<]+)</loc>', sitemap):
        r = resolve(loc, ROOT / 'index.html')
        if not r or not r[0].exists():
            errors.append(f'sitemap.xml: {loc} has no file')

    for e in errors:
        print('ERROR', e)
    print(f'Checked {len(pages)} pages: {len(errors)} problem(s).')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
