# ClearGrade

AI-powered marketing audit service for small businesses. A business owner submits their website URL, we run an automated audit using Claude, and deliver an interactive HTML dashboard with a full marketing audit, SEO audit, competitor intelligence report, and PDF executive summary.

## Architecture

```
                         ┌──────────────┐
                         │   Browser    │
                         │  (Prospect)  │
                         └──────┬───────┘
                                │
                    ┌───────────▼────────────┐
                    │    Nginx (port 80)     │
                    │  - Static landing page │
                    │  - /api → Flask proxy  │
                    │  - /audits → static    │
                    └──┬────────────┬────────┘
                       │            │
          ┌────────────▼──┐   ┌────▼───────────────┐
          │  public/      │   │  Flask API (:8000)  │
          │  Landing page │   │  POST /api/submit   │
          │  HTML/CSS/JS  │   │  GET  /api/jobs     │
          └───────────────┘   │  POST /api/jobs/:id │
                              │       /approve      │
                              └────────┬────────────┘
                                       │
                              ┌────────▼────────────┐
                              │   SQLite Database   │
                              │   (jobs table)      │
                              └────────┬────────────┘
                                       │
                              ┌────────▼────────────┐
                              │   Worker Process    │
                              │  Polls for queued   │
                              │  jobs, runs Claude  │
                              │  Code CLI audits    │
                              └────────┬────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
           ┌───────▼──────┐  ┌────────▼───────┐  ┌──────▼──────┐
           │ audits/slug/ │  │ Resend Email   │  │ Admin Email │
           │ Dashboard    │  │ to Prospect    │  │ Notification│
           │ HTML files   │  │ (after review) │  │ (on complete│
           └──────────────┘  └────────────────┘  └─────────────┘
```

## Directory Structure

```
cleargrade/
├── run_audit.py         CLI entry point — run an audit for any business
├── public/              Static landing page (served by Nginx)
│   ├── index.html       Landing page with intake form
│   ├── css/styles.css   Styles
│   ├── js/main.js       Form handler + scroll animations
│   └── assets/          Images, favicon
├── app/                 Flask backend
│   ├── server.py        API routes
│   ├── database.py      SQLite setup
│   ├── models.py        Data access layer
│   └── email_service.py Resend integration
├── worker/
│   ├── worker.py        Job queue processor
│   └── audit_runner.py  Claude Code CLI wrapper
├── templates/           Jinja2 email templates
├── deploy/              Nginx + systemd configs
└── audits/              Generated reports (one dir per business, timestamped runs)
    └── <slug>/
        ├── latest/      Symlink to most recent successful run
        └── YYYY-MM-DD/  Individual run with full report set
```

## Quick Start — Running an Audit

The fastest way to run a marketing audit for a business:

```bash
python run_audit.py "Business Name" "https://their-website.com" "industry"
```

### Examples

```bash
# Full automated audit
python run_audit.py "Resurgent Sports Rehab" "https://resurgentsports.com" "physical therapy"

# Setup only — creates the directory, then you run Claude interactively
python run_audit.py "Joe's Plumbing" "https://joesplumbing.com" "plumber" --setup-only
cd audits/joes-plumbing/2026-03-29
claude

# Re-run without re-copying the toolkit
python run_audit.py "Resurgent Sports Rehab" "https://resurgentsports.com" "physical therapy" --skip-toolkit
```

### What `run_audit.py` does

1. Creates `audits/<slug>/<date>/` (e.g. `audits/resurgent-sports-rehab/2026-03-29/`)
2. Copies the `ai-marketing-claude` toolkit (agents, skills, scripts) into that directory
3. Writes a `CLAUDE.md` with the business name, URL, and industry
4. Launches Claude Code to run the full audit suite (`/market audit`)
5. On success, sets a `latest` symlink so the most recent report is always at `audits/<slug>/latest/`

### Output structure

```
audits/
├── resurgent-sports-rehab/
│   ├── latest/              -> 2026-03-29 (symlink)
│   ├── 2026-03-15/          Previous run preserved
│   └── 2026-03-29/
│       ├── CLAUDE.md
│       ├── ai-marketing-claude/
│       ├── report_data.json
│       ├── MARKETING-AUDIT.html
│       ├── SEO-AUDIT.html
│       └── COMPETITOR-REPORT.html
└── joes-plumbing/
    ├── latest/              -> 2026-03-29
    └── 2026-03-29/
```

### Tips

- Use `--setup-only` when you want to steer the audit interactively (recommended while dialing in prompts)
- Re-running on the same day overwrites that day's output; previous days are preserved
- The `latest` symlink only updates on a successful run, so a failed re-run won't break the previous good report
- Reports are self-contained HTML files — open directly in a browser or host on GitHub Pages

## Local Development Setup

### Prerequisites

- Python 3.12+
- Claude Code CLI installed and authenticated
- A Resend account and API key (for email delivery)

### Install

```bash
# Clone the repo
git clone <repo-url> cleargrade
cd cleargrade

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your actual values
```

### Run Locally

```bash
# Run an audit (the main workflow)
python run_audit.py "Business Name" "https://example.com" "industry"

# Or start the full web stack:
# Terminal 1: Flask API
source .venv/bin/activate
python -m app.server

# Terminal 2: Worker (optional, for processing audits via the web form)
source .venv/bin/activate
python -m worker.worker
```

The landing page static files are in `public/` — open `public/index.html` directly or serve with:

```bash
python -m http.server 3000 --directory public
```

## Deployment (DigitalOcean Droplet)

### 1. Provision

- Ubuntu 24.04 LTS, $12/month droplet
- Point `cleargrade.co` DNS A record to droplet IP

### 2. Install Dependencies

```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv nginx certbot python3-certbot-nginx
```

### 3. Deploy Application

```bash
sudo mkdir -p /var/www/cleargrade
# Copy project files to /var/www/cleargrade

cd /var/www/cleargrade
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with production values
```

### 4. Configure Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/cleargrade
sudo ln -s /etc/nginx/sites-available/cleargrade /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### 5. Configure systemd Services

```bash
sudo cp deploy/cleargrade-web.service /etc/systemd/system/
sudo cp deploy/cleargrade-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cleargrade-web cleargrade-worker
```

### 6. SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d cleargrade.co -d www.cleargrade.co
```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `RESEND_API_KEY` | Resend API key for sending emails | `re_xxxxxxxxxxxx` |
| `ADMIN_EMAIL` | Email for admin notifications | `david@cleargrade.co` |
| `ADMIN_API_KEY` | API key for protected endpoints | `your-secret-key-here` |
| `CLEARGRADE_DOMAIN` | Public domain for dashboard URLs | `https://cleargrade.co` |
| `CLAUDE_CODE_PATH` | Path to Claude Code CLI binary | `/usr/local/bin/claude` |
| `AUDIT_OUTPUT_DIR` | Directory for generated dashboards | `/var/www/cleargrade/audits` |
| `DATABASE_PATH` | Path to SQLite database file | `/var/www/cleargrade/app/cleargrade.db` |
