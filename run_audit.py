#!/usr/bin/env python3
"""
ClearGrade CLI — Run a marketing audit for a business.

Usage:
    python run_audit.py "Business Name" "https://example.com" "industry"

Creates a timestamped output directory under audits/<slug>/<date>/,
copies the ai-marketing-claude toolkit into it, and launches Claude Code
to run the full marketing audit suite.

After completion, updates the 'latest' symlink so the most recent
report is always at audits/<slug>/latest/.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
AUDITS_DIR = SCRIPT_DIR / "audits"
TOOLKIT_DIR = Path("C:/Resurgent/ai-marketing-claude")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_slug(business_name: str) -> str:
    """Lowercase, hyphenated, alphanumeric-only slug."""
    slug = business_name.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def setup_audit_dir(slug: str) -> tuple[Path, str]:
    """Create the timestamped audit directory and return (run_dir, date_stamp)."""
    date_stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    business_dir = AUDITS_DIR / slug
    run_dir = business_dir / date_stamp

    if run_dir.exists():
        print(f"  Directory already exists: {run_dir}")
        print(f"  Re-running will overwrite previous results from today.")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir, date_stamp


def install_toolkit(run_dir: Path) -> None:
    """Copy the ai-marketing-claude toolkit into the audit run directory."""
    toolkit_dest = run_dir / "ai-marketing-claude"
    if toolkit_dest.exists():
        shutil.rmtree(toolkit_dest)

    if not TOOLKIT_DIR.exists():
        print(f"  WARNING: Toolkit not found at {TOOLKIT_DIR}")
        print(f"  You can clone it manually or the audit will run without skills.")
        return

    shutil.copytree(TOOLKIT_DIR, toolkit_dest, ignore=shutil.ignore_patterns(".git"))
    print(f"  Toolkit installed: {toolkit_dest}")


def setup_claude_config(run_dir: Path, business_name: str, website_url: str, industry: str) -> None:
    """Create a .claude/ directory with project-specific settings."""
    claude_dir = run_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)

    # CLAUDE.md with audit instructions
    claude_md = run_dir / "CLAUDE.md"
    claude_md.write_text(
        f"# ClearGrade Audit — {business_name}\n"
        f"\n"
        f"## Target\n"
        f"- **Business:** {business_name}\n"
        f"- **Website:** {website_url}\n"
        f"- **Industry:** {industry}\n"
        f"\n"
        f"## Instructions\n"
        f"You are running a ClearGrade marketing audit. Use the ai-marketing-claude\n"
        f"toolkit skills to analyze this business.\n"
        f"\n"
        f"## Output Files\n"
        f"Write all output to the current directory:\n"
        f"- `report_data.json` — structured audit data\n"
        f"- `MARKETING-AUDIT.html` — main marketing audit report\n"
        f"- `SEO-AUDIT.html` — detailed SEO audit\n"
        f"- `COMPETITOR-REPORT.html` — competitive intelligence report\n",
        encoding="utf-8",
    )
    print(f"  CLAUDE.md created for {business_name}")


def update_latest_symlink(slug: str, date_stamp: str) -> None:
    """Point the 'latest' symlink to the most recent run directory."""
    business_dir = AUDITS_DIR / slug
    latest_link = business_dir / "latest"

    # Remove existing symlink
    if latest_link.is_symlink() or latest_link.exists():
        if latest_link.is_dir() and not latest_link.is_symlink():
            shutil.rmtree(latest_link)
        else:
            latest_link.unlink()

    # Create relative symlink
    os.symlink(date_stamp, latest_link)
    print(f"  latest -> {date_stamp}")


def run_claude_audit(run_dir: Path, business_name: str, website_url: str, industry: str) -> int:
    """Launch Claude Code in the audit directory to run the marketing audit."""
    prompt = (
        f"Run a full ClearGrade marketing audit for {business_name} ({website_url}). "
        f"Industry: {industry}. "
        f"Use /market audit to run the full audit suite. "
        f"Save all reports (MARKETING-AUDIT.html, SEO-AUDIT.html, "
        f"COMPETITOR-REPORT.html, report_data.json) to the current directory."
    )

    cmd = [
        "claude",
        "--print",
        "--dangerously-skip-permissions",
        "-p", prompt,
    ]

    print(f"\n  Running Claude Code audit...")
    print(f"  Working directory: {run_dir}")
    print(f"  Command: {' '.join(cmd[:3])} ...")
    print(f"  {'=' * 60}\n")

    result = subprocess.run(
        cmd,
        cwd=str(run_dir),
        timeout=30 * 60,  # 30 minute timeout
    )

    return result.returncode


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a ClearGrade marketing audit for a business.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python run_audit.py "Resurgent Sports Rehab" "https://resurgentsports.com" "physical therapy"\n'
            '  python run_audit.py "Joe\'s Plumbing" "https://joesplumbing.com" "plumbing"\n'
            "\n"
            "Output:\n"
            "  audits/<slug>/<date>/MARKETING-AUDIT.html\n"
            "  audits/<slug>/<date>/SEO-AUDIT.html\n"
            "  audits/<slug>/<date>/COMPETITOR-REPORT.html\n"
            "  audits/<slug>/<date>/report_data.json\n"
            "  audits/<slug>/latest/ -> <date>/\n"
        ),
    )
    parser.add_argument("business_name", help="Business name (e.g. 'Resurgent Sports Rehab')")
    parser.add_argument("website_url", help="Website URL (e.g. 'https://resurgentsports.com')")
    parser.add_argument("industry", help="Industry/vertical (e.g. 'physical therapy')")
    parser.add_argument("--skip-toolkit", action="store_true", help="Skip copying the toolkit (if already present)")
    parser.add_argument("--setup-only", action="store_true", help="Create directory and config but don't run Claude")

    args = parser.parse_args()

    slug = generate_slug(args.business_name)

    print(f"\n  ClearGrade Audit Runner")
    print(f"  {'=' * 40}")
    print(f"  Business:  {args.business_name}")
    print(f"  Website:   {args.website_url}")
    print(f"  Industry:  {args.industry}")
    print(f"  Slug:      {slug}")

    # Set up directory
    run_dir, date_stamp = setup_audit_dir(slug)
    print(f"  Output:    {run_dir}")
    print()

    # Install toolkit
    if not args.skip_toolkit:
        install_toolkit(run_dir)

    # Create Claude config
    setup_claude_config(run_dir, args.business_name, args.website_url, args.industry)

    if args.setup_only:
        print(f"\n  Setup complete. To run the audit manually:")
        print(f"    cd {run_dir}")
        print(f"    claude")
        return

    # Run the audit
    returncode = run_claude_audit(run_dir, args.business_name, args.website_url, args.industry)

    if returncode == 0:
        update_latest_symlink(slug, date_stamp)
        print(f"\n  Audit complete!")
        print(f"  Reports:  {run_dir}")
        print(f"  Latest:   {AUDITS_DIR / slug / 'latest'}")
    else:
        print(f"\n  Audit failed (exit code {returncode}).")
        print(f"  Partial output may be in: {run_dir}")
        sys.exit(1)


if __name__ == "__main__":
    main()
