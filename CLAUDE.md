# ClearGrade

AI-powered marketing audit service for small businesses.

## Product
- **Domain:** cleargrade.co
- **GitHub:** https://github.com/DavidKimmel/ClearGrade
- **Stack:** Flask + SQLite + pure HTML/CSS/JS, Resend email, DigitalOcean
- **Pricing:** Free grade (score + 3 quick wins) / $199 full audit

## Audit Generation

### Running an Audit
Use `/market audit` to generate a full marketing audit. The pipeline is:

1. **Phase 1 — Discovery**: WebFetch homepage + key pages for raw HTML
2. **Phase 2 — Browser Pre-Flight Scan** (CRITICAL): Use Chrome browser
   automation to capture JS-rendered content WebFetch misses
3. **Phase 3 — Parallel Analysis**: Launch 5 agents with BOTH WebFetch
   data AND browser enrichment data
4. **Phase 4 — Assembly**: Compile reports, generate PDF via `market-report-pdf`

### Browser Pre-Flight Enrichment (MANDATORY)

**Why:** WebFetch only returns initial HTML before JavaScript executes.
Review widgets (Fera, Judge.me, Yotpo, Stamped, Loox), popup offers,
Instagram embeds, star ratings, and lazy-loaded content are invisible
to WebFetch. This caused critical errors in early audits (reporting
"zero reviews" when a site had 112 reviews).

**Rule: Never report "zero reviews" or "no social proof" based on
WebFetch alone. Browser enrichment data always takes precedence.**

**Scan sequence** (~30 seconds, 8 browser tool calls):

```
1. Navigate to homepage, wait for JS widgets to load
2. Execute extraction JavaScript (reviews, popups, social, trust signals)
3. Get full rendered page text via get_page_text
4. Navigate to one product page, repeat extraction
5. Navigate to about page, get rendered text
6. Compile browser_enrichment JSON payload
```

**What to extract per page:**

| Category | What to Look For |
|---|---|
| Reviews & Ratings | Widget containers (Fera, Judge.me, Yotpo, Stamped, Loox, Okendo), star elements, review count, average rating, sample review text |
| Popups & Modals | Email capture, discount offers, exit-intent, cookie consent. Check elements with `position:fixed`, `z-index>100` |
| Social Feeds | Instagram/TikTok embeds, UGC galleries, social proof notifications |
| Trust Signals | Badge images, certification logos, payment icons |
| Lazy Content | Scroll page to trigger lazy loads before extraction |

**JavaScript extraction selectors** (platform-agnostic):
```javascript
// Reviews
'.fera-widget, .jdgm-widget, .yotpo, .stamped-container,
 .loox-reviews, .okeReviews, .spr-container,
 [data-reviews], [data-review-count], [class*="review"]'

// Star ratings
'[class*="star"], [class*="rating"], [data-rating]'

// Popups
'[class*="popup"], [class*="modal"], .privy-popup,
 .klaviyo-form, .omnisend-form, .justuno'

// Social
'[class*="instagram"], [class*="tiktok"],
 iframe[src*="instagram"], .fomo-notification'

// Trust
'img[src*="trust"], img[src*="badge"], img[src*="secure"]'
```

**Output format** — pass this JSON to all 5 agents:
```json
{
  "browser_enrichment": {
    "reviews": {
      "platform": "fera",
      "count": 112,
      "avg_rating": 5.0,
      "locations": ["homepage", "product_pages"],
      "sample_reviews": ["..."]
    },
    "popups": [{"type": "email_capture", "incentive": "10% off"}],
    "social_feeds": {"instagram_embed": true, "tiktok_embed": false},
    "trust_signals": {"badges": [], "payment_icons": ["visa","mastercard"]},
    "rendered_text": {"homepage": "...", "product": "...", "about": "..."}
  }
}
```

**Agent injection**: When passing context to each of the 5 parallel agents,
prepend: "BROWSER-VERIFIED DATA: The following was gathered by a browser
that executes JavaScript and supersedes any WebFetch findings for reviews,
ratings, popups, social feeds, and trust signals."

### Audit Directory Structure
```
audits/{business-slug}/{YYYY-MM-DD}/
  index.html              — dashboard
  marketing-audit.html    — full 6-dimension audit
  seo-audit.html          — technical SEO audit
  competitor-report.html  — competitive intelligence
  marketing-report.pdf    — executive summary PDF
  report_data.json        — structured audit data
  CLAUDE.md               — per-audit target and instructions
```

### Per-Audit CLAUDE.md Template
Each audit directory gets a CLAUDE.md with target business info:
```markdown
# ClearGrade Audit — {Business Name}

## Target
- **Business:** {name}
- **Website:** {url}
- **Industry:** {industry}

## Instructions
You are running a ClearGrade marketing audit. Use the market audit
skill to analyze this business. Follow the standardized template
defined in the project-level CLAUDE.md.

## Output Files
Write all output to the current directory (lowercase filenames):
- `index.html` — dashboard (Resurgent template standard)
- `marketing-audit.html` — full 6-dimension marketing audit
- `seo-audit.html` — detailed SEO audit
- `competitor-report.html` — competitive intelligence report
- `marketing-report.pdf` — executive summary PDF (via `market-report-pdf` skill)
- `report_data.json` — structured audit data
```

### Dashboard Template Standard (index.html)
The dashboard uses the Resurgent Sports Rehab template — do NOT customize
fonts, colors, or layout per business.

- **Fonts:** Bebas Neue (headings), Barlow (body), Barlow Condensed (labels)
- **Colors:** Standardized navy palette:
  - Backgrounds: `#070b14` / `#0c1220` / `#111a2e`
  - Accents: cyan `#00c6ff`, orange `#ff6b35`, green `#00e87b`, yellow `#ffd23f`, red `#ff3d5a`
- **Effects:** Noise overlay, ambient glow circles, fadeSlideUp animations, animated score gauge
- **Structure:** Header > Score banner (gauge + details + 6 category bars) > 4 report cards (2x2) > 3 quick wins > Footer
- **Icons:** SVG line icons on report cards (not unicode)
- **Footer:** "ClearGrade"
- **Score gauge:** `stroke-dasharray: 377`, offset = `377 * (1 - score/100)`
- **Score colors:** >=70 green, 50-69 yellow, 40-49 orange, <40 red
- **Reference implementation:** C:\Resurgent\site\index.html

### Sub-Report Template (marketing-audit, seo-audit, competitor-report)
Simpler dark-mode CSS with system-ui fonts:
- `--bg: #0f172a`, `--card: #1e293b`, `--border: #334155`
- `--accent: #3b82f6`, `--green: #22c55e`, `--yellow: #eab308`, `--red: #ef4444`
- Components: score-hero, score-grid, summary-box, before-after, win-card, tables
- Reference: C:\Resurgent\site\marketing-audit.html

### Scoring Methodology
| Category | Weight | Measures |
|---|---|---|
| Content & Messaging | 25% | Copy quality, value props, CTAs, brand voice |
| Conversion Optimization | 20% | Social proof, forms, friction, urgency, checkout |
| SEO & Discoverability | 20% | On-page, technical, content strategy, local SEO |
| Competitive Positioning | 15% | Differentiation, pricing, market awareness |
| Brand & Trust | 10% | Design, trust signals, social proof, consistency |
| Growth & Strategy | 10% | Pricing, channels, retention, expansion |

Composite = weighted average of all 6 categories.

## Git & Deployment

Audits are gitignored from the main repo (`audits/*/` in `.gitignore`).
Each audit is deployed as its own GitHub Pages repo:

1. Generate audit files in `audits/{business-slug}/{date}/`
2. Create a new GitHub repo (e.g., `DavidKimmel/pastureandpetal`)
3. Init git in the audit directory, commit all deliverables, push to `main`
4. Enable GitHub Pages on the repo (deploy from `main` branch root)
5. Public URL: `https://davidkimmel.github.io/{repo-name}/`

**Main repo** (`DavidKimmel/ClearGrade`): landing page, backend, templates, configs
**Audit repos** (one per client): standalone static sites with all deliverables

## Project Structure
```
ClearGrade/
  public/           — landing page (GitHub Pages via docs/)
  docs/             — mirrors public/ for GitHub Pages
  templates/        — email templates (Jinja2)
  worker/           — audit runner (Python)
  deploy/           — nginx, systemd configs
  audits/           — generated audit deliverables (gitignored, tracked separately)
```
