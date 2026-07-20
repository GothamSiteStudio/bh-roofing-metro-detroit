# BUILD BRIEF — BH Roofing Metro Detroit

**Business:** BH Roofing Metro Detroit — residential & commercial roofing
**Service area:** Metro Detroit + suburbs within 35 miles (Wayne, Oakland, Macomb counties)
**Phone:** _not live yet_  |  **Email:** info@bhroofingmetrodetroit.com
**Model:** Service-area business — **NO storefront, NO public street address**
**Primary domain:** bhroofingmetrodetroit.com

Sister site to **BH Door Solutions Metro Detroit** — same brand family, same metro, same build system,
same trust/data-integrity rules. No street address anywhere on the site or in schema.

---

## 1. SITE ARCHITECTURE

```
/ (Homepage)
/services/            (Services hub — grid linking to all 10 service pages, grouped)
/service-areas/       (Area hub — county columns + linked city grid)
  └─ /service-areas/{city}/   (18 city pages)
/about/
/contact/             (form + service-area note; NO address)
/reviews/             (honest — invites real Google reviews, no fabricated testimonials)
/gallery/
/financing/
/faq/                 (master FAQ list)
/thank-you/  /404.html
```

## 2. SERVICE PAGES (10, grouped)

| # | Page | Slug | Group |
|---|------|------|-------|
| 1 | **Roof Replacement** (primary money page) | `/services/roof-replacement/` | Roofing |
| 2 | **Roof Repair** | `/services/roof-repair/` | Repair |
| 3 | **Storm & Hail Damage** (+ honest insurance-claim help) | `/services/storm-damage-roof-repair/` | Repair |
| 4 | **Roof Inspections** | `/services/roof-inspection/` | Roofing |
| 5 | **Flat & Commercial Roofing** (TPO/EPDM/mod-bit) | `/services/flat-commercial-roofing/` | Commercial |
| 6 | **Metal Roofing** (standing-seam) | `/services/metal-roofing/` | Roofing |
| 7 | **Gutters & Gutter Guards** | `/services/gutter-installation/` | Exterior |
| 8 | **Siding** (vinyl / fiber-cement) | `/services/siding-installation/` | Exterior |
| 9 | **Ventilation, Skylights & Ice-Dam Prevention** | `/services/attic-ventilation-skylights/` | Exterior |
| 10 | **Roof Replacement & Repair Cost Guide** (money page) | `/services/roof-replacement-cost/` | Planning |

## 3. SERVICE-AREA CITY PAGES (18)

Warren, Sterling Heights, Dearborn, Troy, Livonia, Canton, Farmington Hills, Rochester Hills, Novi, Southfield,
Royal Oak, St. Clair Shores, Shelby Township, Clinton Township, Birmingham, Ferndale, Grosse Pointe Woods, Northville.
Each has a **unique local roof hook** (housing stock / roof age / storm exposure) and city×service intersection links —
never a templated city swap.

## 4. PRIMARY KEYWORDS

- **Home:** roofing metro Detroit / roof replacement & repair metro Detroit
- **Service pages:** roof replacement metro Detroit, roof repair near me, storm damage roof repair, roof inspection,
  commercial flat roof, metal roofing, seamless gutters, siding installation, attic ventilation / ice dam, roof
  replacement cost — each metro Detroit-qualified.
- **City pages:** `roof replacement {City} MI` (H1), also targeting `roof repair {City}` and `roofing {City} MI`.

## 5. BRAND VOICE, VALUE PROPS & TRUST SIGNALS

Confident, local, plain-spoken, reassuring — a trusted neighbor-tradesman. Lead with the customer's problem, and be
Michigan-weather-aware throughout (freeze-thaw, ice dams, snow load, spring wind & hail, lake-effect).

**Core value props:** fast/reliable scheduling · local metro Detroit roofers · every roofing service one team ·
honest upfront pricing (repair-vs-replace straight talk) · licensed/insured/guaranteed with full cleanup & nail sweep ·
curb appeal & home value.

**Trust signals:** licensed & insured (placeholder — client to confirm) · workmanship guarantee + manufacturer-backed
material warranties (generic) · free no-obligation estimates · financing available · brands installed (GAF, Owens
Corning, CertainTeed, IKO, Malarkey, Velux).

> **Data-integrity rules (enforced in the copy):** NO fabricated phone number, license #, "since [year]", review
> counts/ratings, testimonials, or named certifications (no "Master Elite" etc.). Storm page: help document damage &
> navigate the insurance claim, but **the homeowner pays their own deductible** — never promise "free" insurance roofs
> or waived deductibles. Cost figures are typical market ranges pointing to a free exact estimate. No AggregateRating/
> Review schema until real reviews exist.

## 6. TECHNICAL SEO

- Service-area business schema: **RoofingContractor / HomeAndConstructionBusiness / GeneralContractor**, `areaServed`
  = 18 cities + 3 counties + Metropolitan Detroit, **GeoCircle** (~35 mi radius), **no `streetAddress`**, hours,
  `knowsAbout` roofing topics. `telephone` is omitted until the number is live.
- Per-page unique title/description/canonical; one H1 per page; clean directory slugs.
- `Service` schema per service page, `FAQPage` on home + every service/city page, `BreadcrumbList` throughout.
- XML sitemap + robots; Open Graph + Twitter cards; self-hosted fonts + WebP; mobile-first; accessible semantics.
- Matomo analytics site ID **22** on every page.

## 7. INTERNAL LINKING

Hub-and-spoke: Home → services hub + areas hub → individual pages; related-service cross-links; city↔service
intersection links (each city surfaces the 4 services its housing stock needs most + 3 neighbor cities). Every page
carries a primary "Free Estimate" CTA and a repeating CTA band; the cost guide is linked from every service page.

## 8. BUILD SYSTEM

Static generator: `scripts/build.py` (business data, templates, JSON-LD, shared copy) + `scripts/_copy.json`
(all page copy, generated by the copywriting workflow). Imagery via `scripts/generate_images.py` (Gemini +
PIL favicons). Hosted on GitHub Pages with `CNAME`. See **README.md** and **CONTENT-TODO.md**.
