"""ClearGrade audit worker — polls for queued jobs and runs audits."""

from __future__ import annotations

import logging
import os
import signal
import sys
import time
from typing import Any

# Add parent directory so we can import app modules.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import models  # noqa: E402
from app import email_service  # noqa: E402
from worker import audit_runner  # noqa: E402

POLL_INTERVAL_SECONDS: int = 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Module-level flag for graceful shutdown — only mutated by the signal handler.
_shutdown_requested: bool = False


def _handle_shutdown(signum: int, _frame: Any) -> None:
    """Set the shutdown flag so the polling loop exits cleanly."""
    global _shutdown_requested
    logger.info("Received signal %s — shutting down after current cycle.", signum)
    _shutdown_requested = True


def _process_job(job: dict[str, Any]) -> None:
    """Run a single audit job and update its status accordingly."""
    job_id: int = job["id"]
    logger.info("Starting job %s for %s (%s)", job_id, job["business_name"], job["website_url"])

    models.update_job(job_id, status="running")

    result = audit_runner.run_audit(job)

    if result["success"]:
        logger.info("Job %s completed successfully.", job_id)
        models.update_job(
            job_id,
            status="completed",
            dashboard_url=result["dashboard_url"],
        )
    else:
        logger.error("Job %s failed: %s", job_id, result["error"])
        models.update_job(
            job_id,
            status="failed",
            error_log=result["error"],
        )

    # Build a snapshot dict for the email template
    notification_job: dict[str, Any] = {
        **job,
        "status": "completed" if result["success"] else "failed",
        "dashboard_url": result.get("dashboard_url"),
        "error_log": result.get("error"),
    }
    email_service.send_admin_notification(notification_job)


def poll_loop() -> None:
    """Poll the database for queued jobs and process them one at a time."""
    logger.info("Worker started — polling every %s seconds.", POLL_INTERVAL_SECONDS)

    while not _shutdown_requested:
        try:
            job = models.get_next_queued_job()
        except Exception:
            logger.exception("Error fetching next queued job.")
            job = None

        if job is not None:
            try:
                _process_job(job)
            except Exception:
                logger.exception("Unhandled error processing job %s.", job.get("id"))
        else:
            logger.debug("No queued jobs found.")

        # Sleep in small increments so we can respond to shutdown quickly.
        for _ in range(POLL_INTERVAL_SECONDS):
            if _shutdown_requested:
                break
            time.sleep(1)

    logger.info("Worker shut down cleanly.")


def main() -> None:
    """Register signal handlers and start the polling loop."""
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    poll_loop()


if __name__ == "__main__":
    main()
