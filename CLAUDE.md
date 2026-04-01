# ClearGrade

AI-powered marketing audit service for small businesses.

## Product
- **Domain:** cleargrade.co
- **GitHub:** https://github.com/DavidKimmel/ClearGrade
- **Stack:** Flask + SQLite + pure HTML/CSS/JS, Resend email, DigitalOcean
- **Pricing:** Free grade (score + 3 quick wins) / $199 full audit

## Audit Generation

### Running an Audit
Use `/market audit` to generate a full marketing audit. Each audit runs
5 parallel analysis agents (content, conversion, competitive, SEO, brand/strategy),
then assembles the deliverables. Always generate the PDF executive summary
via the `market-report-pdf` skill as the final step.

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
