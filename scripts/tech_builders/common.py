"""Common utilities and templating for generating comprehensive technical blog articles."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TECH_BLOG_DIR = BASE_DIR / "blog" / "technical"

def ensure_tech_dir():
    TECH_BLOG_DIR.mkdir(parents=True, exist_ok=True)

def write_tech_article(filename: str, content: str):
    ensure_tech_dir()
    filepath = TECH_BLOG_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [CREATED] {filename} ({len(content.split())} words)")
