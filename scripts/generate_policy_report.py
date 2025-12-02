#!/usr/bin/env python3
"""
Aggregate key documentation into a single policy report that highlights
security posture, architecture constraints, and research risk framing.
"""
from __future__ import annotations

import datetime
from pathlib import Path

DOC_PATHS = [
    ("Architecture Overview", "docs/architecture.md"),
    ("Secure Architecture Considerations", "docs/architecture_secure.md"),
    ("ATO/STIG Checklist", "docs/ato_and_stig_checklist.md"),
    ("Barrier Reference", "docs/barriers_reference.md"),
    ("Research Outline", "docs/research_outline.md"),
]


def render_section(title: str, content: str) -> str:
    return f"# {title}\n\n{content.strip()}\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report_lines = [
        "# Persuadable Defender Policy Report",
        "",
        f"_Generated: {datetime.datetime.utcnow().isoformat()}Z_",
        "",
        "This report consolidates the current security and research documentation.",
        "",
    ]

    for title, rel_path in DOC_PATHS:
        path = repo_root / rel_path
        if path.exists():
            report_lines.append(render_section(title, path.read_text()))
        else:
            report_lines.append(f"# {title}\n\n> Missing source document: {rel_path}\n")

    output_path = repo_root / "policy_report.md"
    output_path.write_text("\n".join(report_lines))
    print(f"Policy report written to {output_path}")


if __name__ == "__main__":
    main()

