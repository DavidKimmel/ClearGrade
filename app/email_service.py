"""Email service using Resend and Jinja2 templates."""

from __future__ import annotations

import os
from typing import Any

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ---------------------------------------------------------------------------
# Configuration (all from environment)
# ---------------------------------------------------------------------------

resend.api_key = os.environ.get("RESEND_API_KEY", "")

ADMIN_EMAIL: str = os.environ.get("ADMIN_EMAIL", "admin@cleargrade.co")
CLEARGRADE_DOMAIN: str = os.environ.get("CLEARGRADE_DOMAIN", "https://cleargrade.co")
FROM_EMAIL: str = os.environ.get("FROM_EMAIL", "noreply@cleargrade.co")

# Template loader — templates live in C:/ClearGrade/templates/
_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
_jinja_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


def _render_template(template_name: str, context: dict[str, Any]) -> str:
    """Render an HTML template with the given context."""
    template = _jinja_env.get_template(template_name)
    return template.render(context)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def send_admin_notification(job: dict[str, Any]) -> dict[str, Any]:
    """Email the admin when an audit completes or fails.

    Expects a Jinja2 template at templates/admin_notification.html.
    """
    # TODO: Customise subject line per status (completed vs failed)
    subject = (
        f"[ClearGrade] Audit {job.get('status', 'update')}: "
        f"{job.get('business_name', 'Unknown')}"
    )

    html_body = _render_template(
        "notify_admin.html",
        {
            "job": job,
            "domain": CLEARGRADE_DOMAIN,
        },
    )

    params: resend.Emails.SendParams = {
        "from": FROM_EMAIL,
        "to": [ADMIN_EMAIL],
        "subject": subject,
        "html": html_body,
    }

    response = resend.Emails.send(params)
    return dict(response) if response else {}


def send_prospect_report(job: dict[str, Any]) -> dict[str, Any]:
    """Email the prospect their dashboard link after admin approval.

    Expects a Jinja2 template at templates/prospect_report.html.
    """
    recipient_email: str = job.get("email", "")
    if not recipient_email:
        raise ValueError("Job is missing an email address for the prospect.")

    dashboard_url: str = job.get(
        "dashboard_url",
        f"{CLEARGRADE_DOMAIN}/report/{job.get('slug', '')}",
    )

    # TODO: Add business-specific personalisation to the subject line
    subject = f"Your ClearGrade Website Audit is Ready — {job.get('business_name', '')}"

    html_body = _render_template(
        "deliver_report.html",
        {
            "job": job,
            "dashboard_url": dashboard_url,
            "domain": CLEARGRADE_DOMAIN,
        },
    )

    params: resend.Emails.SendParams = {
        "from": FROM_EMAIL,
        "to": [recipient_email],
        "subject": subject,
        "html": html_body,
    }

    response = resend.Emails.send(params)
    return dict(response) if response else {}
