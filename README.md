# SkyKids NGO

**Children’s Support Initiative in Ukraine**

SkyKids is a structured support system dedicated to helping vulnerable children through daily care, education, mentorship, and a safe community environment.

We work on the ground every day to ensure that no child is left without support, attention, or opportunity.

---

## 🌍 About

SkyKids is more than a project — it is a living ecosystem designed to support children and teenagers facing difficult life circumstances.

We create a stable, safe, and engaging environment where children receive not only basic care, but also the opportunity to grow, learn, and build a better future.

Our approach is holistic — addressing physical, emotional, and developmental needs simultaneously.

---

## 🧩 What We Do

- 🍲 Provide daily hot meals for children in need  
- 📚 Support education and learning development  
- 🤝 Build mentorship and community support systems  
- 🧠 Offer emotional and psychological support  
- 🎯 Create a safe after-school environment  

---

## 🎯 Mission

To provide children with consistent support, care, and development opportunities — helping them build a stable foundation for a better future.

---

## 🔭 Vision

To build a generation of confident, supported, and capable young people who understand their value and are equipped to shape their future and their communities.

---

## 📊 Impact

- 10,000+ meals served  
- 20+ children supported daily  
- Active volunteer engagement  
- Continuous community development  

---

## 🚀 Project Scope

SkyKids operates as a scalable model that can expand into multiple directions:

- Sky Kitchen — daily nutrition support  
- Sky Gifts — humanitarian aid  
- Sky Academy — education & development  
- Sky Recovery — emotional support  

---

## 🛠 Tech Overview

Static website (HTML5, CSS3, vanilla JavaScript) served by **GitHub Pages** at
[skykids.com.ua](https://skykids.com.ua). There is no framework and no runtime build step:
every page is a plain `.html` file.

### Project structure

```
*.html                  pages (index, skykitchen, skygifts, skyacademy, skyrecovery, …)
partials/               shared blocks: header, footer, donate modal
assets/css/site.css     styles of the shared blocks (prefixed `sk-`)
assets/js/site.js       shared behaviour: UA/EN language, menu, modals, copy buttons
assets/img/             images (WebP): brand/, team/, events/, photos/, icons/, game/
assets/brand/           original PNG logos for the media kit
tools/site.json         per-page settings: header style, translation on/off, SEO description
tools/build.py          inserts partials into pages, generates <head> SEO tags, sitemap.xml, robots.txt
tools/check_links.py    checks internal links, files, anchors and image alt texts
```

### Editing

| What to change | Where |
| --- | --- |
| Menu, footer, contacts | `partials/header.html`, `partials/footer.html` |
| Bank details, Monobank jar | `partials/donate-modal.html` |
| Page text | the page itself (`skykitchen.html`, …) — outside the `<!-- sk:… -->` blocks |
| Page description for Google / social previews | `<meta name="description">` in the page |
| Domain, OG image | `tools/site.json` |

After changing anything in `partials/`, `assets/css/site.css`, `assets/js/site.js` or `tools/site.json`, run:

```bash
python3 tools/build.py        # updates all pages, sitemap.xml and robots.txt
python3 tools/check_links.py  # checks links and files
```

Content between `<!-- sk:… -->` and `<!-- /sk:… -->` markers is generated — do not edit it by hand,
it will be overwritten. The GitHub Action in `.github/workflows/check.yml` runs both scripts on every
push and fails if pages were not rebuilt or a link is broken. On January 1 it will ask for one rebuild
to update the year in the footer.

### Translations

Translatable elements carry both versions: `data-uk="…" data-en="…"`. The chosen language is remembered
between pages. Pages without English text set `"i18n": false` in `tools/site.json`, which hides the switch.

### Adding images

Put images into `assets/img/…` as WebP (≈1200 px wide for posters, 400×400 px for team photos) and use
file names without spaces, e.g. `assets/img/events/new-event.webp`.

---

## ⚠️ Usage & Rights

This repository is publicly available for **transparency and demonstration purposes only**.

All rights to the code, design, branding, and content belong to **SkyKids NGO**.

❗ Unauthorized use, copying, modification, or distribution is strictly prohibited without prior written permission.

---

## 🤝 Get Involved

We are open to collaboration with:
- partners  
- volunteers  
- donors  
- organizations  

If you want to contribute or support the initiative — reach out.

---

## 📬 Contact

### General Contact

Email: officeskydoor@gmail.com
Location: Dnipro, Ukraine
Phone: +38 (056) 789-33-23
Phone: +38 (095) 159-80-63
Phone: +38 (063) 725-54-23


### 🤝 Partnerships & Grants / Fundraising
Evgen Chernov — Fundraiser / Partnerships Manager (SkyKids NGO)
Responsible for partnerships, grants, donor relations, and organizational collaboration.

Email: skykids.partner@gmail.com
Phone / WhatsApp: +38 (098) 492-79-48
Telegram: https://t.me/son_of_god_evgen

---

## ❤️ Support the Mission

Every action matters.

By supporting SkyKids, you directly impact children's lives — providing care, stability, and real opportunities for the future.
