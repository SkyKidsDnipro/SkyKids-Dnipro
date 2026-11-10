#!/usr/bin/env python3
"""
Перевірка внутрішніх посилань і файлів сайту SkyKids.

Знаходить:
  • посилання на сторінки чи файли, яких немає в репозиторії (href, src, url(...), onclick);
  • якорі (#section), яких немає на сторінці;
  • картинки без атрибута alt;
  • дубльовані id на сторінці.

Запуск:  python3 tools/check_links.py
Повертає код 1, якщо є помилки (так CI зупиняє збірку).
"""
import glob
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_SCHEMES = ('http:', 'https:', 'mailto:', 'tel:', 'data:', 'javascript:', '//', 'blob:')


def main():
    os.chdir(ROOT)
    errors = []
    pages = sorted(glob.glob('*.html'))
    ids_by_page = {}
    for page in pages:
        s = open(page, encoding='utf-8').read()
        ids = re.findall(r'\sid="([^"]+)"', s)
        ids_by_page[page] = set(ids)
        dup = sorted({i for i in ids if ids.count(i) > 1})
        if dup:
            errors.append('%s: дубльовані id: %s' % (page, ', '.join(dup)))

    for page in pages:
        s = re.sub(r'<!--.*?-->', '', open(page, encoding='utf-8').read(), flags=re.S)
        base = '' if '<base href="/">' in s else os.path.dirname(page)
        # без <script> з шаблонними рядками JS (`${...}`)
        refs = re.findall(r'(?:href|src)="([^"]*)"', s)
        refs += re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", s)
        refs += re.findall(r"openEventModal\('([^']+)'", s)
        for ref in refs:
            ref = ref.strip()
            if not ref or ref.startswith(SKIP_SCHEMES) or '${' in ref:
                continue
            path, _, frag = ref.partition('#')
            path = urllib.parse.unquote(path.split('?')[0])
            if not path:  # якір на цій же сторінці
                if frag and frag not in ids_by_page[page] and frag not in ('donate', 'top'):
                    errors.append('%s: якір #%s не знайдено' % (page, frag))
                continue
            target = os.path.normpath(os.path.join(base, path.lstrip('/')))
            if path.endswith('/'):
                target = os.path.join(target, 'index.html')
            if not os.path.exists(target):
                errors.append('%s: немає файлу «%s»' % (page, ref))
            elif frag and target.endswith('.html') and frag not in ids_by_page.get(target, set()):
                errors.append('%s: у %s немає якоря #%s' % (page, target, frag))

        for img in re.findall(r'<img\b[^>]*>', s):
            if not re.search(r'\salt="', img):
                errors.append('%s: картинка без alt: %s' % (page, img[:90]))

    if errors:
        print('Знайдено проблем: %d' % len(errors))
        for e in errors:
            print('  -', e)
        return 1
    print('OK: %d сторінок, усі посилання та файли на місці' % len(pages))
    return 0


if __name__ == '__main__':
    sys.exit(main())
