"""Flask application for the ClearGrade API."""

from __future__ import annotations

import os
import re
from functools import wraps
from typing import Any, Callable, Tuple

from flask import Flask, Response, jsonify, request

from app.database import init_db
from app.email_service import send_prospect_report
from app.models import create_job, get_job, get_jobs, update_job

# TODO: Add rate limiting (flask-limiter)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_slug(business_name: str) -> str:
    """Lowercase, replace spaces with hyphens, strip non-alphanumeric except hyphens."""
    slug = business_name.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    # Collapse consecutive hyphens
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def _require_api_key(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that rejects requests without a valid X-API-Key header."""
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        admin_key = os.environ.get("ADMIN_API_KEY", "")
        provided_key = request.headers.get("X-API-Key", "")
        if not admin_key or provided_key != admin_key:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Initialise database on first request context
    with app.app_context():
        init_db()

    # ------------------------------------------------------------------
    # CORS — apply to every response
    # ------------------------------------------------------------------
    @app.after_request
    def _add_cors_headers(response: Response) -> Response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
        return response

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @app.route("/api/submit", methods=["POST"])
    def submit() -> Tuple[Response, int]:
        """Accept a new audit request from the public form."""
        data: dict[str, Any] = request.get_json(silent=True) or {}

        # Honeypot check — reject bots that fill the hidden field
        if data.get("honeypot"):
            return jsonify({"error": "Invalid submission"}), 422

        required_fields = ("business_name", "website_url", "industry",
                           "contact_name", "email")
        missing = [f for f in required_fields if not data.get(f, "").strip()]
        if missing:
            return jsonify({
                "error": "Missing required fields",
                "fields": missing,
            }), 400

        slug = _generate_slug(data["business_name"])

        # TODO: Validate email format
        # TODO: Validate website_url format
        # TODO: Check for duplicate submissions (same email + website)

        job = create_job(
            business_name=data["business_name"].strip(),
            website_url=data["website_url"].strip(),
            industry=data["industry"].strip(),
            contact_name=data["contact_name"].strip(),
            email=data["email"].strip(),
            slug=slug,
        )

        # TODO: Enqueue background audit job (trigger worker)

        return jsonify({"success": True, "job": job}), 201

    @app.route("/api/jobs", methods=["GET"])
    @_require_api_key
    def list_jobs() -> Tuple[Response, int]:
        """List all jobs, optionally filtered by ?status=."""
        status_filter = request.args.get("status")
        jobs = get_jobs(status=status_filter)
        return jsonify({"jobs": jobs}), 200

    @app.route("/api/jobs/<int:job_id>/approve", methods=["POST"])
    @_require_api_key
    def approve_job(job_id: int) -> Tuple[Response, int]:
        """Approve a completed audit and send the report to the prospect."""
        job = get_job(job_id)
        if job is None:
            return jsonify({"error": "Job not found"}), 404

        # TODO: Verify job status is "completed" before approving
        from datetime import datetime, timezone

        updated_job = update_job(
            job_id,
            status="approved",
            approved_at=datetime.now(timezone.utc).isoformat(),
        )

        # Send the prospect their dashboard link
        try:
            send_prospect_report(updated_job)  # type: ignore[arg-type]
            update_job(job_id, status="sent", sent_at=datetime.now(timezone.utc).isoformat())
        except Exception as exc:
            # TODO: Log error properly; do not expose internals to caller
            update_job(job_id, error_log=str(exc))
            return jsonify({
                "error": "Approved but email delivery failed",
                "job": get_job(job_id),
            }), 500

        return jsonify({"success": True, "job": get_job(job_id)}), 200

    return app


# ---------------------------------------------------------------------------
# Convenience entry-point for `python -m app.server`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
