"""Run a ClearGrade audit via the Claude Code CLI."""

from __future__ import annotations

import logging
import os
import subprocess
from typing import Any, TypedDict

logger = logging.getLogger(__name__)

CLAUDE_CODE_PATH: str = os.environ.get("CLAUDE_CODE_PATH", "claude")
AUDIT_OUTPUT_DIR: str = os.environ.get("AUDIT_OUTPUT_DIR", "./audits")
TIMEOUT_SECONDS: int = 30 * 60  # 30 minutes


class AuditResult(TypedDict):
    success: bool
    dashboard_url: str | None
    error: str | None


def _build_command(job: dict[str, Any]) -> list[str]:
    """Construct the Claude Code CLI command for an audit.

    # -----------------------------------------------------------------------
    # TODO: The exact CLI invocation below needs calibration to match the
    # existing audit pipeline.  Key unknowns:
    #   - Which prompt template / system prompt file to pass
    #   - Which model flags (--model, --max-tokens) are appropriate
    #   - Whether we should stream output or run in batch mode
    #   - How the output directory structure maps to the dashboard URL
    #   - Whether additional env vars (API keys, etc.) must be forwarded
    #
    # For now, this constructs a *plausible* invocation that should be
    # reviewed and adjusted once the prompt and output format are finalised.
    # -----------------------------------------------------------------------
    """
    slug: str = job["slug"]
    output_dir: str = os.path.join(AUDIT_OUTPUT_DIR, slug)

    return [
        CLAUDE_CODE_PATH,
        "--print",
        "--output-dir", output_dir,
        "--business-name", job["business_name"],
        "--website-url", job["website_url"],
        "--industry", job["industry"],
    ]


def run_audit(job: dict[str, Any]) -> AuditResult:
    """Execute the audit subprocess and return a result dict.

    Returns an immutable-style ``AuditResult`` dict with:
      - ``success``: whether the audit completed without error
      - ``dashboard_url``: public URL of the generated dashboard (on success)
      - ``error``: captured stderr / exception message (on failure)
    """
    slug: str = job["slug"]
    command = _build_command(job)
    domain: str = os.environ.get("CLEARGRADE_DOMAIN", "https://cleargrade.co")
    dashboard_url: str = f"{domain}/audits/{slug}/index.html"

    logger.info("Running audit command: %s", " ".join(command))

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        if completed.returncode == 0:
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
