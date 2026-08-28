#!/usr/bin/env python3
"""Generate a language-usage SVG from the owner's public GitHub repositories."""
from __future__ import annotations

import html
import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OWNER = "Mohannad-Mahdi-Dev"
API = "https://api.github.com"
OUTPUT = Path(__file__).resolve().parents[1] / "language-stats.svg"
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()

COLORS = {
    "JavaScript": "#F1E05A",
    "TypeScript": "#3178C6",
    "PHP": "#4F5D95",
    "C++": "#F34B7D",
    "Python": "#3572A5",
    "HTML": "#E34C26",
    "CSS": "#563D7C",
    "Blade": "#F05340",
    "Java": "#B07219",
    "C#": "#178600",
    "Go": "#00ADD8",
    "Rust": "#DEA584",
}


def get_json(path: str):
    url = path if path.startswith("http") else API + path
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Mohannad-Mahdi-Dev-profile-language-stats",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x: float, y: float, value: object, size: int, fill: str = "#E6EDF3", weight: str = "400", anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" '
        f'font-family="Arial,DejaVu Sans,sans-serif" font-size="{size}px" '
        f'font-weight="{weight}" text-anchor="{anchor}">{esc(value)}</text>'
    )


def main() -> None:
    repos = get_json(f"/users/{OWNER}/repos?per_page=100&type=owner&sort=updated")
    languages: Counter[str] = Counter()
    for repo in repos:
        if repo.get("private") or repo.get("fork"):
            continue
        language_url = repo.get("languages_url")
        if not language_url:
            continue
        try:
            languages.update({k: int(v) for k, v in get_json(language_url).items()})
        except Exception:
            continue

    total = sum(languages.values())
    top = languages.most_common(6)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="440" viewBox="0 0 1000 440" role="img" aria-labelledby="title desc">',
        '<title id="title">Most-used programming languages in public repositories</title>',
        '<desc id="desc">Automatically generated from public GitHub repository language-byte data.</desc>',
        '<rect width="1000" height="440" rx="18" fill="#0D1117"/>',
        '<rect x="1" y="1" width="998" height="438" rx="17" fill="none" stroke="#30363D"/>',
        text(34, 42, "github.com / Mohannad-Mahdi-Dev", 18, "#8B949E"),
        text(34, 78, "Most-used languages", 30, "#F0F6FC", "700"),
        text(966, 43, f"refreshed {generated}", 14, "#8B949E", "400", "end"),
    ]

    if not top or total == 0:
        pieces.append(text(34, 150, "No public language data available yet.", 18, "#F0F6FC", "700"))
    else:
        bar_x, bar_y, bar_w, bar_h = 34, 112, 932, 18
        current_x = bar_x
        for language, amount in top:
            width = bar_w * amount / total
            pieces.append(f'<rect x="{current_x:.2f}" y="{bar_y}" width="{max(width, 2):.2f}" height="{bar_h}" fill="{COLORS.get(language, "#8B949E")}"/>')
            current_x += width
        for index, (language, amount) in enumerate(top):
            y = 180 + index * 36
            percentage = amount / total * 100
            color = COLORS.get(language, "#8B949E")
            pieces.extend([
                f'<circle cx="44" cy="{y - 5}" r="6" fill="{color}"/>',
                text(62, y, language, 16, "#F0F6FC", "700"),
                text(310, y, f"{percentage:.1f}%", 16, "#C9D1D9", "700"),
                f'<rect x="400" y="{y - 16}" width="520" height="12" rx="6" fill="#21262D"/>',
                f'<rect x="400" y="{y - 16}" width="{max(8, 520 * percentage / 100):.2f}" height="12" rx="6" fill="{color}"/>',
            ])

    pieces.extend([
        text(34, 414, "Public repositories only • Based on GitHub language-byte data • Not a measure of skill", 13, "#8B949E"),
        "</svg>",
    ])
    OUTPUT.write_text("\n".join(pieces) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
