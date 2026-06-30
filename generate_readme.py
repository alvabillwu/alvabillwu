#!/usr/bin/env python3
"""Generate the portfolio README from project-queue.json.

Keeps the profile README in sync with the actual project list so it never
drifts. Run after publishing/maintaining projects:

    python generate_readme.py --queue ../project-queue.json --out README.md
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CATEGORY_EMOJI = {
    "devtools": "🛠️",
    "prompt-engineering": "🔄",
    "agent-safety": "🛡️",
    "agents": "🤖",
    "mcp": "🔌",
    "RAG": "📊",
    "AI/LLM": "🧠",
}

LANG_BADGE = {
    "Python": "Python-3776AB",
    "TypeScript": "TypeScript-3178C6",
    "Node.js": "Node.js-339933",
}


def _lang_for(tech: list[str]) -> str:
    for t in tech:
        if t in LANG_BADGE:
            return t
    return ""


def _tests_badge(slug: str, n: int) -> str:
    return f"![tests](https://img.shields.io/badge/tests-{n}-success)"


def render(projects: list[dict], stats: dict, pr_count: int, generated_at: str) -> str:
    lines: list[str] = []
    lines.append("# Hi, I'm alvabillwu 👋")
    lines.append("")
    lines.append(
        "I build open-source tools for the **AI/LLM developer stack** — retrieval "
        "evaluation, prompt engineering, agent observability, MCP tooling, and supply-chain "
        "security. This profile indexes my published work."
    )
    lines.append("")
    lines.append("## 📦 Projects")
    lines.append("")
    lines.append("| Project | Category | Lang | What it does | Tests |")
    lines.append("|---------|----------|------|--------------|:-----:|")
    # Sort: M-complexity first, then by completion date.
    sorted_proj = sorted(
        projects,
        key=lambda p: (p.get("complexity") != "M", p.get("completed_at", "")),
    )
    for p in sorted_proj:
        slug = p["slug"]
        cat = p.get("category", "")
        emoji = CATEGORY_EMOJI.get(cat, "•")
        lang = _lang_for(p.get("tech", []))
        title = p.get("title") or p.get("slug")
        # Shorten title to a one-liner (drop the "Name —" prefix if present).
        desc = title.split(" — ", 1)[-1] if " — " in title else title
        if len(desc) > 70:
            desc = desc[:67] + "…"
        tests = p.get("tests_passing", 0)
        link = f"[`{slug}`]({p['url']})"
        lines.append(
            f"| {link} | {emoji} {cat} | {lang} | {desc} | {_tests_badge(slug, tests)} |"
        )
    lines.append("")

    # Stats summary
    total_tests = sum(p.get("tests_passing", 0) for p in projects)
    cats = sorted({p.get("category", "") for p in projects})
    langs = sorted({_lang_for(p.get("tech", [])) for p in projects if _lang_for(p.get("tech", []))})
    m_done = sum(1 for p in projects if p.get("complexity") == "M")
    ci = sum(1 for p in projects if p.get("ci"))
    lines.append("## 📈 At a glance")
    lines.append("")
    lines.append(f"- **{len(projects)} published projects** · {total_tests} tests passing")
    lines.append(f"- **{m_done} medium-complexity** project shipped to v1.0 (ragbench)")
    lines.append(f"- **{pr_count} external PR(s)** to upstream open source")
    lines.append(f"- **{ci}/{len(projects)} repos** with CI (GitHub Actions)")
    lines.append(f"- Categories: {', '.join(cats)}")
    lines.append(f"- Languages: {', '.join(langs)}")
    lines.append("")

    # Contribution philosophy
    lines.append("## 🧭 How this work is produced")
    lines.append("")
    lines.append(
        "Projects are built and maintained by an autonomous AI agent loop: it scouts "
        "trends, builds tested tools with docs + CI, contributes upstream PRs, and "
        "keeps every repo active. Each project ships with a README, LICENSE, tests, "
        "and (progressively) GitHub Actions CI. See any repo's commit history for the "
        "trail."
    )
    lines.append("")

    # Open source contributions
    lines.append("## 🤝 Open-source contributions")
    lines.append("")
    lines.append(
        "- [modelcontextprotocol/servers#4439](https://github.com/modelcontextprotocol/servers/pull/4439) — "
        "docs(time): fix example responses to match actual server output (verified against source)."
    )
    lines.append("")

    lines.append("## 🔭 Currently")
    lines.append("")
    lines.append("- Shipping more AI/LLM devtools and contributing upstream PRs on a steady cadence.")
    lines.append("- Backfilling CI across all repos and adding a web-UI project for shape diversity.")
    lines.append("")
    lines.append("---")
    lines.append(f"<sub>Portfolio README generated from project-queue.json · {generated_at}</sub>")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the portfolio README.")
    ap.add_argument("--queue", default="../project-queue.json", help="path to project-queue.json")
    ap.add_argument("--out", default="README.md", help="output README path")
    args = ap.parse_args()

    data = json.loads(Path(args.queue).read_text(encoding="utf-8"))
    projects = data.get("completed", [])
    stats = data.get("stats", {})
    pr_count = stats.get("prs_contributed", 0)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    readme = render(projects, stats, pr_count, now)
    Path(args.out).write_text(readme, encoding="utf-8")
    print(f"wrote {args.out} ({len(readme)} bytes, {len(projects)} projects)")


if __name__ == "__main__":
    main()
