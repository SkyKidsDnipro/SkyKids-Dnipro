/* ==========================================================================
   SkyKids — спільний скрипт сайту
   Мова (UA/EN), шапка та мобільне меню, модальні вікна, копіювання реквізитів.
   Старі виклики зі сторінок (setLang, openDonateModal, copyCard, data-action=...)
   продовжують працювати.
   ========================================================================== */
(function () {
    'use strict';

    var LANG_KEY = 'skyKidsLang';
    var body = document.body;
    var root = document.documentElement;
    var i18nEnabled = body.getAttribute('data-i18n') !== 'off';

    /* ---------- Сховище (може бути недоступне в приватному режимі) ---------- */
    function store(key, value) {
        try {
            if (value === undefined) return window.localStorage.getItem(key);
            window.localStorage.setItem(key, value);
        } catch (e) { return null; }
    }

    /* ---------- Мова ---------- */
    function currentLang() {
        return root.getAttribute('lang') === 'en' ? 'en' : 'uk';
    }

    function translateElement(el, lang) {
        var text = el.getAttribute('data-' + lang);
        if (text === null) return;
        if (text.indexOf('<') !== -1) { el.innerHTML = text; return; }

        var children = el.children;
        if (!children.length) { el.textContent = text; return; }

        // Елемент з іконками: залишаємо <i>, замінюємо лише текст
        var onlyIcons = true;
        for (var i = 0; i < children.length; i++) {
            if (children[i].tagName !== 'I') { onlyIcons = false; break; }
        }
        if (onlyIcons) {
            Array.prototype.slice.call(el.childNodes).forEach(function (n) {
                if (n.nodeType === 3) el.removeChild(n);
            });
            el.appendChild(document.createTextNode(' ' + text));
        } else {
            el.textContent = text;
        }
    }

    function setLang(lang, skipText) {
        lang = lang === 'en' ? 'en' : 'uk';
        if (!i18nEnabled) lang = 'uk';
        root.setAttribute('lang', lang);
        store(LANG_KEY, lang);

        if (!skipText) {
            document.querySelectorAll('[data-uk]').forEach(function (el) { translateElement(el, lang); });
            document.querySelectorAll('[data-uk-aria]').forEach(function (el) {
                el.setAttribute('aria-label', el.getAttribute('data-' + lang + '-aria'));
            });
        }

        // Новий перемикач
        document.querySelectorAll('.sk-lang').forEach(function (sw) {
            sw.classList.toggle('is-en', lang === 'en');
            sw.querySelectorAll('button[data-lang]').forEach(function (b) {
                b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === lang));
            });
        });
        // Старі перемикачі, якщо десь залишились
        document.querySelectorAll('.lang-switch').forEach(function (sw) {
            sw.classList.toggle('en', lang === 'en');
            sw.querySelectorAll('button').forEach(function (b) {
                var bl = b.getAttribute('data-lang') || (b.id === 'btn-en' ? 'en' : b.id === 'btn-uk' ? 'uk' : null);
                if (bl) b.classList.toggle('active', bl === lang);
            });
        });

        document.dispatchEvent(new CustomEvent('sk:langchange', { detail: { lang: lang } }));
    }

    /* ---------- Сповіщення ---------- */
    var toastEl, toastTimer;
    function toast(message) {
        if (!toastEl) {
            toastEl = document.createElement('div');
            toastEl.className = 'sk-toast';
            toastEl.setAttribute('role', 'status');
            toastEl.setAttribute('aria-live', 'polite');
            body.appendChild(toastEl);
        }
        toastEl.textContent = message;
        toastEl.classList.add('is-visible');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () { toastEl.classList.remove('is-visible'); }, 1800);
    }

    /* ---------- Копіювання ---------- */
    function writeClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        }
        return new Promise(function (resolve, reject) {
            var ta = document.createElement('textarea');
            ta.value = text;
            ta.setAttribute('readonly', '');
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            body.appendChild(ta);
            ta.select();
            try { document.execCommand('copy') ? resolve() : reject(); } catch (e) { reject(e); }
            body.removeChild(ta);
        });
    }

    function copyFrom(btn, text) {
        // Номери карток та IBAN копіюємо без пробілів — так їх легше вставити в банк
        var value = text.trim();
        if (/^[A-Z]{0,2}[\d\s]+$/.test(value)) value = value.replace(/\s+/g, '');
        writeClipboard(value).then(function () {
            toast(currentLang() === 'en' ? 'Copied' : 'Скопійовано');
            var icon = btn && btn.querySelector('i');
            if (icon) {
                var prev = icon.className;
                icon.className = 'ph-bold ph-check';
                btn.classList.add('is-done');
                setTimeout(function () { icon.className = prev; btn.classList.remove('is-done'); }, 1600);
            }
        }).catch(function () {
            toast(currentLang() === 'en' ? 'Copy failed — select the text manually' : 'Не вдалося скопіювати — виділіть текст вручну');
        });
    }

    function copyById(id, btn) {
        var el = document.getElementById(id);
        if (el) copyFrom(btn, el.innerText);
    }

    /* ---------- Модальні вікна ---------- */
    var lastFocus = null;
    var FOCUSABLE = 'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';

    function openModal(id) {
        var modal = document.getElementById(id);
        if (!modal) return;
        lastFocus = document.activeElement;
        if (modal.classList.contains('sk-modal')) {
            modal.classList.add('is-open');
            modal.setAttribute('aria-hidden', 'false');
            body.classList.add('sk-modal-open');
            var first = modal.querySelector('.sk-modal__close') || modal.querySelector(FOCUSABLE);
            if (first) setTimeout(function () { first.focus(); }, 30);
        } else {
            modal.classList.add('show');
            body.classList.add('modal-open');
        }
        closeMenu();
    }

    function closeModal(modal) {
        if (!modal) return;
        if (modal.classList.contains('sk-modal')) {
            modal.classList.remove('is-open');
            modal.setAttribute('aria-hidden', 'true');
        } else {
            modal.classList.remove('show');
        }
        if (!document.querySelector('.sk-modal.is-open')) body.classList.remove('sk-modal-open');
        if (!document.querySelector('.modal.show')) body.classList.remove('modal-open');
        if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    function closeAllModals() {
        document.querySelectorAll('.sk-modal.is-open, .modal.show').forEach(closeModal);
    }

    /* ---------- Шапка та меню ---------- */
    var header = document.querySelector('.sk-header');
    var burger = document.querySelector('.sk-burger');

    function closeMenu() {
        if (!header || !header.classList.contains('is-menu-open')) return;
        header.classList.remove('is-menu-open');
        body.classList.remove('sk-menu-open');
        if (burger) burger.setAttribute('aria-expanded', 'false');
    }

    function toggleMenu() {
        var open = !header.classList.contains('is-menu-open');
        header.classList.toggle('is-menu-open', open);
        body.classList.toggle('sk-menu-open', open);
        burger.setAttribute('aria-expanded', String(open));
    }

    if (header) {
        var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 10); };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    /* ---------- Делегування кліків ---------- */
    document.addEventListener('click', function (e) {
        var t = e.target;

        // Клік по фону модалки
        if (t.classList && (t.classList.contains('sk-modal') || (t.classList.contains('modal') && t.classList.contains('show')))) {
            closeModal(t);
            return;
        }

        var el = t.closest ? t.closest('[data-action], [data-open-modal], [data-close-modal], [data-copy], .sk-burger, .sk-nav a, .sk-lang button') : null;
        if (!el) return;

        if (el.classList.contains('sk-burger')) { toggleMenu(); return; }
        if (el.matches('.sk-nav a')) { closeMenu(); return; }

        if (el.hasAttribute('data-open-modal')) { e.preventDefault(); openModal(el.getAttribute('data-open-modal')); return; }
        if (el.hasAttribute('data-close-modal')) { e.preventDefault(); closeModal(el.closest('.sk-modal, .modal')); return; }
        if (el.hasAttribute('data-copy')) { e.preventDefault(); copyById(el.getAttribute('data-copy'), el); return; }

        // Сумісність зі старою розміткою сторінок
        var action = el.getAttribute('data-action');
        var target = el.getAttribute('data-target');
        if (action === 'switch-lang' || el.matches('.sk-lang button')) setLang(el.getAttribute('data-lang'));
        else if (action === 'open-modal') { e.preventDefault(); openModal(target); }
        else if (action === 'close-modal') { e.preventDefault(); closeAllModals(); }
        else if (action === 'copy') { e.preventDefault(); copyById(target, el); }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { closeAllModals(); closeMenu(); return; }

        // Утримуємо фокус усередині відкритої модалки
        if (e.key === 'Tab') {
            var modal = document.querySelector('.sk-modal.is-open');
            if (!modal) return;
            var items = Array.prototype.filter.call(modal.querySelectorAll(FOCUSABLE), function (x) { return x.offsetParent !== null; });
            if (!items.length) return;
            var first = items[0], last = items[items.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
    });

    window.addEventListener('resize', function () { if (window.innerWidth > 960) closeMenu(); });

    /* ---------- Публічні функції (для onclick у сторінках) ---------- */
    window.SkyKids = { setLang: setLang, openModal: openModal, closeModal: closeModal, copy: copyById, toast: toast, lang: currentLang };
    window.setLang = setLang;
    window.openDonateModal = function () { openModal('donateModal'); };
    window.closeDonateModal = function () { closeModal(document.getElementById('donateModal')); };
    window.copyCard = function () { copyById('skCard', document.querySelector('[data-copy="skCard"]')); };
    window.copyIBAN = function () { copyById('skIban', document.querySelector('[data-copy="skIban"]')); };

    /* ---------- Старт ---------- */
    // Сторінка вже українською в HTML, тож текст перекладаємо лише для EN
    var saved = store(LANG_KEY);
    if (i18nEnabled && saved === 'en') setLang('en');
    else setLang('uk', true);

    // Відкрити донат за посиланням виду ...#donate
    if (location.hash === '#donate') openModal('donateModal');
})();
