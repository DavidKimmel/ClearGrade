"""Data-access functions for the jobs table.

All functions return plain dicts (not mutable Row objects) to keep the
interface immutable-friendly.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from app.database import get_db


def _row_to_dict(row: Any) -> dict[str, Any] | None:
    """Convert a sqlite3.Row to a plain dict, or return None."""
    if row is None:
        return None
    return dict(row)


def create_job(
    business_name: str,
    website_url: str,
    industry: str,
    contact_name: str,
    email: str,
    slug: str,
) -> dict[str, Any]:
    """Insert a new job and return it as a dict."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO jobs (business_name, website_url, industry,
                              contact_name, email, slug, status)
            VALUES (?, ?, ?, ?, ?, ?, 'queued')
            """,
            (business_name, website_url, industry, contact_name, email, slug),
        )
        job_id: int = cursor.lastrowid  # type: ignore[assignment]

    # Re-fetch to get all default columns (created_at, etc.)
    return get_job(job_id)  # type: ignore[return-value]


def get_job(job_id: int) -> dict[str, Any] | None:
    """Return a single job by ID, or None if not found."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_dict(row)


def get_jobs(status: Optional[str] = None) -> list[dict[str, Any]]:
    """Return all jobs, optionally filtered by status."""
    with get_db() as conn:
        if status is not None:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def get_next_queued_job() -> dict[str, Any] | None:
    """Return the oldest queued job, or None if the queue is empty."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at ASC LIMIT 1"
        ).fetchone()
    return _row_to_dict(row)


def update_job(job_id: int, **fields: Any) -> dict[str, Any] | None:
    """Update specified fields on a job and return the updated dict.

    Only columns that are explicitly passed as keyword arguments are changed.
    Returns None if the job does not exist.
    """
    if not fields:
        return get_job(job_id)

    allowed_columns = {
        "business_name", "website_url", "industry", "contact_name",
        "email", "slug", "status", "started_at", "completed_at",
        "approved_at", "sent_at", "error_log", "dashboard_url",
    }
    invalid = set(fields.keys()) - allowed_columns
    if invalid:
        raise ValueError(f"Invalid columns: {invalid}")

    set_clause = ", ".join(f"{col} = ?" for col in fields)
    values = list(fields.values()) + [job_id]

    with get_db() as conn:
        conn.execute(
            f"UPDATE jobs SET {set_clause} WHERE id = ?",
            values,
        )

    return get_job(job_id)
