#!/usr/bin/env python3
"""
SkyKids — зменшені копії картинок для швидкого завантаження.

Для кожного файлу в assets/img/events/ та assets/img/photos/ робить копію
шириною 640 px поруч: poster.webp -> poster-640.webp.
tools/build.py потім сам додає до <img> атрибути srcset/sizes, і браузер
на телефоні чи в картці бере меншу копію, а на великих екранах — повну.

Також робить маленькі версії логотипа для шапки й підвалу.

Як користуватись (після додавання нових фото):
    pip install pillow      # один раз
    python3 tools/images.py
    python3 tools/build.py
"""
import glob
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMALL = 640
FOLDERS = ['assets/img/events', 'assets/img/photos']
FIXED = {  # логотипи: (джерело, результат, ширина)
    'logo': ('assets/img/brand/logo.webp', 'assets/img/brand/logo-96.webp', 96),
    'wordmark': ('assets/img/brand/wordmark.webp', 'assets/img/brand/wordmark-200.webp', 200),
}


def resize(src, dst, width, quality=78):
    im = Image.open(src)
    if im.width <= width:
        return False
    h = round(im.height * width / im.width)
    im.resize((width, h), Image.LANCZOS).save(dst, 'WEBP', quality=quality, method=6)
    return True


def main():
    made = 0
    for folder in FOLDERS:
        for src in sorted(glob.glob(os.path.join(ROOT, folder, '*.webp'))):
            if src.endswith('-%d.webp' % SMALL):
                continue
            dst = src[:-5] + '-%d.webp' % SMALL
            if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
                continue
            if resize(src, dst, SMALL):
                made += 1
                print('%-55s %4d КБ -> %3d КБ' % (os.path.relpath(dst, ROOT), os.path.getsize(src) // 1024, os.path.getsize(dst) // 1024))
    for src, dst, width in FIXED.values():
        src, dst = os.path.join(ROOT, src), os.path.join(ROOT, dst)
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            resize(src, dst, width, quality=85)
            made += 1
            print('%-55s %3d КБ' % (os.path.relpath(dst, ROOT), os.path.getsize(dst) // 1024))
    print('Готово, нових файлів: %d. Тепер запустіть python3 tools/build.py' % made)
    return 0


if __name__ == '__main__':
    sys.exit(main())
