"""Run a ClearGrade audit via the Claude Code CLI.

Audit output is organised by business slug with timestamped run directories:

    audits/
    └── joes-plumbing/
        ├── latest/          ← symlink → 2026-03-29/
        ├── 2026-03-29/
        └── 2026-02-15/
"""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import datetime, timezone
from typing import Any, TypedDict

logger = logging.getLogger(__name__)

CLAUDE_CODE_PATH: str = os.environ.get("CLAUDE_CODE_PATH", "claude")
AUDIT_OUTPUT_DIR: str = os.environ.get("AUDIT_OUTPUT_DIR", "./audits")
TIMEOUT_SECONDS: int = 30 * 60  # 30 minutes


class AuditResult(TypedDict):
    success: bool
    dashboard_url: str | None
    error: str | None


def _ensure_output_dir(slug: str) -> tuple[str, str]:
    """Create the timestamped output directory for this run.

    Returns (run_dir, date_stamp) where run_dir is the full path to the
    new timestamped directory (e.g. audits/joes-plumbing/2026-03-29/).
    """
    date_stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    business_dir = os.path.join(AUDIT_OUTPUT_DIR, slug)
    run_dir = os.path.join(business_dir, date_stamp)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir, date_stamp


def _update_latest_symlink(slug: str, date_stamp: str) -> None:
    """Point the ``latest`` symlink to the most recent run directory."""
    business_dir = os.path.join(AUDIT_OUTPUT_DIR, slug)
    latest_link = os.path.join(business_dir, "latest")

    # Remove existing symlink or directory named 'latest'
    if os.path.islink(latest_link):
        os.remove(latest_link)
    elif os.path.isdir(latest_link):
        os.remove(latest_link)

    # Relative symlink so it works regardless of mount path
    os.symlink(date_stamp, latest_link)
    logger.info("Updated latest symlink: %s → %s", latest_link, date_stamp)


def _build_command(job: dict[str, Any], run_dir: str) -> list[str]:
    """Construct the Claude Code CLI command for an audit.

    # -----------------------------------------------------------------------
    # TODO: The exact CLI invocation below needs calibration to match the
    # existing audit pipeline.  Key unknowns:
    #   - Which prompt template / system prompt file to pass
    #   - Which model flags (--model, --max-tokens) are appropriate
    #   - Whether we should stream output or run in batch mode
    #   - Whether additional env vars (API keys, etc.) must be forwarded
    #
    # For now, this constructs a *plausible* invocation that should be
    # reviewed and adjusted once the prompt and output format are finalised.
    # -----------------------------------------------------------------------
    """
    return [
        CLAUDE_CODE_PATH,
        "--print",
        "--output-dir", run_dir,
        "--business-name", job["business_name"],
        "--website-url", job["website_url"],
        "--industry", job["industry"],
    ]


def run_audit(job: dict[str, Any]) -> AuditResult:
    """Execute the audit subprocess and return a result dict.

    Creates a timestamped subdirectory under ``audits/<slug>/`` and updates
    the ``latest`` symlink on success.

    Returns an immutable-style ``AuditResult`` dict with:
      - ``success``: whether the audit completed without error
      - ``dashboard_url``: public URL of the generated dashboard (on success)
      - ``error``: captured stderr / exception message (on failure)
    """
    slug: str = job["slug"]
    run_dir, date_stamp = _ensure_output_dir(slug)
    command = _build_command(job, run_dir)
    domain: str = os.environ.get("CLEARGRADE_DOMAIN", "https://cleargrade.co")
    dashboard_url: str = f"{domain}/audits/{slug}/latest/index.html"

    logger.info("Running audit command: %s", " ".join(command))
    logger.info("Output directory: %s", run_dir)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        if completed.returncode == 0:
            _update_latest_symlink(slug, date_stamp)
            logger.info("Audit for '%s' finished successfully.", slug)
            return AuditResult(
                success=True,
                dashboard_url=dashboard_url,
                error=None,
            )

        error_output = (completed.stderr or completed.stdout or "Unknown error").strip()
        logger.error("Audit for '%s' exited with code %s: %s", slug, completed.returncode, error_output)
        return AuditResult(
            success=False,
            dashboard_url=None,
            error=f"Exit code {completed.returncode}: {error_output[:2000]}",
        )

    except subprocess.TimeoutExpired:
        msg = f"Audit timed out after {TIMEOUT_SECONDS} seconds."
        logger.error(msg)
        return AuditResult(success=False, dashboard_url=None, error=msg)

    except OSError as exc:
        msg = f"Failed to start audit process: {exc}"
        logger.error(msg)
        return AuditResult(success=False, dashboard_url=None, error=msg)
