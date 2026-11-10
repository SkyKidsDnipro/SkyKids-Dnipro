#!/usr/bin/env python3
"""
SkyKids — власні шрифти іконок Phosphor лише з тих іконок, що є на сайті.

Повні шрифти Phosphor важать ~440 КБ (3 начертання). Скрипт знаходить іконки,
які реально використовуються (у сторінках, partials/ та assets/js/), і збирає
маленькі шрифти + CSS:

    assets/fonts/phosphor-bold.woff2, phosphor-fill.woff2, phosphor-duotone.woff2
    assets/css/icons.css

Коли додаєте нову іконку (наприклад, <i class="ph-bold ph-star">), запустіть:

    pip install fonttools brotli      # один раз
    python3 tools/icons.py
    python3 tools/build.py

Список усіх іконок: https://phosphoricons.com
`python3 tools/build.py --check` (і CI) підкаже, якщо іконки немає в зібраному шрифті.
"""
import glob
import io
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = '2.1.2'
CDN = 'https://cdn.jsdelivr.net/npm/@phosphor-icons/web@%s/src/{w}/{f}' % VERSION
WEIGHTS = {'bold': 'Phosphor-Bold', 'fill': 'Phosphor-Fill', 'duotone': 'Phosphor-Duotone'}
TOKEN = re.compile(r'ph-[a-z0-9]+(?:-[a-z0-9]+)*')


def used_icons():
    """{weight: set(icon names)} з усіх файлів сайту."""
    files = glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, 'partials', '*.html')) \
        + glob.glob(os.path.join(ROOT, 'assets', 'js', '*.js'))
    used = {w: set() for w in WEIGHTS}
    for path in files:
        text = open(path, encoding='utf-8').read()
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S)  # CSS-правила на кшталт .ph-bold — не іконки
        # будь-який рядок класів: class="...", 'ph-bold ph-check', "ph-fill ph-x"
        for chunk in re.findall(r'["\'`]([^"\'`<>]*\bph-(?:bold|fill|duotone)\b[^"\'`<>]*)["\'`]', text):
            tokens = TOKEN.findall(chunk)
            weights = [t[3:] for t in tokens if t[3:] in WEIGHTS]
            names = [t[3:] for t in tokens if t[3:] not in WEIGHTS]
            for w in weights:
                used[w].update(names)
    return used


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def parse_css(css):
    """{name: [(pseudo, codepoint, extra_css)]} з офіційного CSS Phosphor."""
    out = {}
    for name, pseudo, body in re.findall(r'\.ph-[a-z]+\.ph-([a-z0-9-]+):(before|after)\s*\{([^}]*)\}', css):
        cp = re.search(r'content:\s*"\\([0-9a-f]+)"', body)
        extra = re.sub(r'content:\s*"[^"]*";?', '', body).strip()
        extra = ' '.join(l.strip() for l in extra.splitlines() if l.strip())
        out.setdefault(name, []).append((pseudo, int(cp.group(1), 16), extra))
    return out


def main():
    import logging
    logging.getLogger('fontTools').setLevel(logging.ERROR)
    from fontTools import subset
    from fontTools.ttLib import TTFont

    used = used_icons()
    os.makedirs(os.path.join(ROOT, 'assets', 'fonts'), exist_ok=True)
    css_out = [
        '/* Згенеровано tools/icons.py — не редагуйте вручну.',
        '   Phosphor Icons %s (MIT), лише іконки, що використовуються на сайті. */' % VERSION,
    ]
    missing = []
    for w, family in WEIGHTS.items():
        names = sorted(used[w])
        if not names:
            continue
        src_css = fetch(CDN.format(w=w, f='style.css')).decode('utf-8')
        mapping = parse_css(src_css)
        codepoints = set()
        rules = []
        for n in names:
            if n not in mapping:
                missing.append('ph-%s ph-%s' % (w, n))
                continue
            for pseudo, cp, extra in mapping[n]:
                codepoints.add(cp)
                decl = 'content: "\\%x";' % cp + ((' ' + extra) if extra else '')
                rules.append('.ph-%s.ph-%s:%s { %s }' % (w, n, pseudo, decl))

        font = TTFont(io.BytesIO(fetch(CDN.format(w=w, f=family + '.woff2'))))
        opts = subset.Options()
        opts.flavor = 'woff2'
        opts.layout_features = []
        opts.name_IDs = ['*']
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=sorted(codepoints))
        sub.subset(font)
        out_path = os.path.join(ROOT, 'assets', 'fonts', 'phosphor-%s.woff2' % w)
        font.flavor = 'woff2'
        font.save(out_path)

        css_out += [
            '',
            '@font-face { font-family: "%s"; src: url("../fonts/phosphor-%s.woff2") format("woff2"); '
            'font-weight: normal; font-style: normal; font-display: block; }' % (family, w),
            '.ph-%s { font-family: "%s" !important; speak: never; font-style: normal; font-weight: normal; '
            'font-variant: normal; text-transform: none; line-height: 1; letter-spacing: 0; '
            '-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }' % (w, family),
        ]
        css_out += rules
        print('%-8s %3d іконок, %5.1f КБ' % (w, len(names), os.path.getsize(out_path) / 1024))

    with open(os.path.join(ROOT, 'assets', 'css', 'icons.css'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(css_out) + '\n')
    if missing:
        print('Таких іконок немає в Phosphor %s (перевірте назву): %s' % (VERSION, ', '.join(missing)))
        return 1
    print('Готово: assets/css/icons.css. Тепер запустіть python3 tools/build.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
