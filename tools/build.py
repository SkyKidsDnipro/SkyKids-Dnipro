#!/usr/bin/env python3
"""
SkyKids — збирання спільних частин сайту.

Сторінки залишаються звичайними HTML-файлами (GitHub Pages віддає їх як є).
Скрипт оновлює в кожній сторінці блоки між мітками:

    <!-- sk:head -->          ... <!-- /sk:head -->          SEO, іконки, спільний CSS
    <!-- sk:header -->        ... <!-- /sk:header -->        шапка   (partials/header.html)
    <!-- sk:footer -->        ... <!-- /sk:footer -->        підвал  (partials/footer.html)
    <!-- sk:donate-modal -->  ... <!-- /sk:donate-modal -->  модалка донату
    <!-- sk:scripts -->       ... <!-- /sk:scripts -->       спільний JS

а також генерує sitemap.xml і robots.txt.

Як користуватись:
    python3 tools/build.py          # оновити всі сторінки
    python3 tools/build.py --check  # лише перевірити (для CI), нічого не змінює

Щоб змінити меню, підвал чи реквізити — редагуйте файли в partials/,
потім запустіть build.py. Налаштування сторінок — у tools/site.json.
"""
import datetime
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_PARTS = ['assets/css/fonts.css', 'assets/css/icons.css', 'assets/css/site.css']  # збираються в assets/css/bundle.css
ASSET_VERSION_FILES = CSS_PARTS + ['assets/js/site.js']


def read(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return f.read()


def write(path, content):
    with open(os.path.join(ROOT, path), 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def asset_version():
    """Коротка версія за вмістом спільних файлів — щоб браузер не тримав старий кеш."""
    import hashlib
    h = hashlib.sha1()
    for p in ASSET_VERSION_FILES:
        h.update(read(p).encode('utf-8'))
    return h.hexdigest()[:8]


def replace_block(page, name, content, path):
    pattern = re.compile(r'(<!-- sk:%s -->)(.*?)(<!-- /sk:%s -->)' % (re.escape(name), re.escape(name)), re.S)
    if not pattern.search(page):
        raise SystemExit('%s: немає мітки <!-- sk:%s -->' % (path, name))
    return pattern.sub(lambda m: m.group(1) + '\n' + content.strip('\n') + '\n' + m.group(3), page, count=1)


def page_meta(page, path, cfg, site):
    title = re.search(r'<title>(.*?)</title>', page, re.S)
    title = html.unescape(title.group(1).strip()) if title else site['site_name']
    desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', page)
    desc = html.unescape(desc.group(1)) if desc else cfg.get('description') or site['default_description']
    return title, desc


def head_block(path, title, desc, cfg, site, version):
    url = site['domain'] + '/' + ('' if path == 'index.html' else path)
    og_image = site['domain'] + '/' + site['og_image']
    e = lambda s: html.escape(s, quote=True)
    lines = []
    if cfg.get('noindex'):
        lines.append('<meta name="robots" content="noindex">')
    else:
        lines.append('<link rel="canonical" href="%s">' % url)
    lines.append('<meta name="theme-color" content="%s">' % site['theme_color'])
    lines += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="%s">' % e(site['site_name']),
        '<meta property="og:locale" content="uk_UA">',
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:title" content="%s">' % e(title),
        '<meta property="og:description" content="%s">' % e(desc),
        '<meta property="og:image" content="%s">' % og_image,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % e(title),
        '<meta name="twitter:description" content="%s">' % e(desc),
        '<meta name="twitter:image" content="%s">' % og_image,
        '<link rel="icon" href="favicon.ico" sizes="any">',
        '<link rel="icon" type="image/png" sizes="32x32" href="assets/img/brand/favicon-32.png">',
        '<link rel="apple-touch-icon" href="assets/img/brand/apple-touch-icon.png">',
        '<link rel="manifest" href="site.webmanifest">',
        '<link rel="preload" href="assets/fonts/inter-cyrillic.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="assets/fonts/phosphor-bold.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="stylesheet" href="assets/css/bundle.css?v=%s">' % version,
    ]
    return '\n'.join('    ' + l for l in lines)


def ensure_description(page, desc):
    if re.search(r'<meta\s+name="description"', page):
        return page
    tag = '<meta name="description" content="%s">\n    ' % html.escape(desc, quote=True)
    return page.replace('<!-- sk:head -->', tag + '<!-- sk:head -->', 1)


def set_body_i18n(page, enabled):
    value = 'on' if enabled else 'off'
    def fix(m):
        tag = re.sub(r'\sdata-i18n="[^"]*"', '', m.group(0))
        return tag[:-1] + ' data-i18n="%s">' % value
    return re.sub(r'<body\b[^>]*>', fix, page, count=1)


def mark_current(header_html, path):
    out = header_html
    # пункт меню поточної сторінки
    out = re.sub(r'(<a\b[^>]*href="%s"[^>]*?)(>)' % re.escape(path),
                 lambda m: m.group(1) + ('' if 'aria-current' in m.group(1) else ' aria-current="page"') + m.group(2),
                 out)
    # логотип не позначаємо як поточний пункт
    out = out.replace('class="sk-logo" aria-label="SkyKids — на головну" aria-current="page"',
                      'class="sk-logo" aria-label="SkyKids — на головну"')
    if path in ('skykitchen.html', 'skygifts.html', 'skyacademy.html', 'skyrecovery.html'):
        out = out.replace('class="sk-nav__toggle"', 'class="sk-nav__toggle is-current"', 1)
    return out


IMG_SIZES = '(max-width: 600px) 92vw, 500px'


def add_srcset(page):
    """<img src="assets/img/(events|photos)/x.webp"> -> додає srcset, якщо є x-640.webp (tools/images.py)."""
    def fix(m):
        tag, src = m.group(0), m.group(1)
        if 'srcset=' in tag:
            return tag
        small = src[:-5] + '-640.webp'
        if not os.path.exists(os.path.join(ROOT, small)):
            return tag
        from PIL import Image  # noqa: F401  (лише для перевірки ширини оригіналу)
        width = Image.open(os.path.join(ROOT, src)).width
        extra = ' srcset="%s 640w, %s %dw" sizes="%s"' % (small, src, width, IMG_SIZES)
        return tag[:-1].rstrip('/').rstrip() + extra + '>'
    return re.sub(r'<img\b[^>]*?\ssrc="(assets/img/(?:events|photos)/[a-z0-9-]+(?<!-640)\.webp)"[^>]*>', fix, page)


def build(check=False):
    site = json.loads(read('tools/site.json'))
    version = asset_version()
    year = str(datetime.date.today().year)
    partials = {
        'header': read('partials/header.html'),
        'footer': read('partials/footer.html').replace('{{YEAR}}', year),
        'donate-modal': read('partials/donate-modal.html'),
    }
    scripts = '<script src="assets/js/site.js?v=%s" defer></script>' % version

    changed = []
    for path, cfg in site['pages'].items():
        original = read(path)
        page = original
        title, desc = page_meta(page, path, cfg, site)
        page = ensure_description(page, desc)
        page = replace_block(page, 'head', head_block(path, title, desc, cfg, site, version), path)
        if not cfg.get('standalone'):
            mod = ' sk-header--overlay' if cfg.get('header') == 'overlay' else ''
            header = mark_current(partials['header'].replace('{{HEADER_MOD}}', mod), path)
            page = replace_block(page, 'header', header, path)
            page = replace_block(page, 'footer', partials['footer'], path)
            page = replace_block(page, 'donate-modal', partials['donate-modal'], path)
            page = replace_block(page, 'scripts', scripts, path)
            page = set_body_i18n(page, cfg.get('i18n', False))
        page = add_srcset(page)
        if page != original:
            changed.append(path)
            if not check:
                write(path, page)

    # один CSS-файл замість трьох: менше запитів, що блокують показ сторінки
    bundle = '/* Згенеровано tools/build.py з %s — редагуйте ці файли, не цей. */\n' % ', '.join(CSS_PARTS)
    bundle += '\n'.join(read(p) for p in CSS_PARTS)
    current = read('assets/css/bundle.css') if os.path.exists(os.path.join(ROOT, 'assets/css/bundle.css')) else None
    if current != bundle:
        changed.append('assets/css/bundle.css')
        if not check:
            write('assets/css/bundle.css', bundle)

    # sitemap.xml + robots.txt
    today = datetime.date.today().isoformat()
    urls = []
    for path, cfg in site['pages'].items():
        if cfg.get('noindex'):
            continue
        loc = site['domain'] + '/' + ('' if path == 'index.html' else path)
        urls.append('  <url>\n    <loc>%s</loc>\n    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>'
                    % (loc, cfg.get('changefreq', 'monthly'), cfg.get('priority', '0.5')))
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % '\n'.join(urls))
    robots = 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % site['domain']
    for path, content in (('sitemap.xml', sitemap), ('robots.txt', robots)):
        current = read(path) if os.path.exists(os.path.join(ROOT, path)) else None
        if current != content:
            changed.append(path)
            if not check:
                write(path, content)

    # усі іконки зі сторінок мають бути у зібраному шрифті (tools/icons.py)
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from icons import used_icons
    icons_css = read('assets/css/icons.css')
    absent = sorted('ph-%s ph-%s' % (w, n) for w, names in used_icons().items() for n in names
                    if '.ph-%s.ph-%s:' % (w, n) not in icons_css)
    if absent:
        print('Іконок немає в assets/fonts — запустіть python3 tools/icons.py: ' + ', '.join(absent))
        return 1

    if check:
        if changed:
            print('Не зібрано після змін у partials/ або site.json. Запустіть: python3 tools/build.py')
            for p in changed:
                print('  -', p)
            return 1
        print('OK: усі сторінки актуальні')
        return 0
    print('Оновлено: %s' % (', '.join(changed) if changed else 'нічого (усе актуально)'))
    return 0


if __name__ == '__main__':
    sys.exit(build(check='--check' in sys.argv))
