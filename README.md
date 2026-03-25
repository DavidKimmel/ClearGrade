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
└── audits/              Generated dashboards (one subdir per business)
```

## Local Development Setup

### Prerequisites

- Python 3.12+
- A Resend account and API key

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
# Terminal 1: Flask API
source .venv/bin/activate
python -m app.server

# Terminal 2: Worker (optional, for processing audits)
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
