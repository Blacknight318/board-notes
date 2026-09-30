#!/usr/bin/env python3
"""Build a dependency-free static site from board-meeting Markdown files."""
from __future__ import annotations

import html
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs"
ASSETS = ROOT / "assets"


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="noopener noreferrer">\1</a>', text)
    return text


def split_front_matter(raw: str) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    if not raw.startswith("---\n"):
        return metadata, raw
    _, block, body = raw.split("---\n", 2)
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata, body.lstrip("\n")


def render_markdown(raw: str) -> str:
    _, body = split_front_matter(raw)
    lines = body.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_stack: list[int] = []
    in_quote = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline(' '.join(x.strip() for x in paragraph))}</p>")
            paragraph = []

    def close_lists(target: int = 0) -> None:
        while len(list_stack) > target:
            output.append("</ul>")
            list_stack.pop()

    def close_quote() -> None:
        nonlocal in_quote
        if in_quote:
            flush_paragraph()
            output.append("</blockquote>")
            in_quote = False

    for line in lines:
        if not line.strip():
            flush_paragraph()
            close_quote()
            continue
        if re.match(r"^---+$", line.strip()):
            flush_paragraph(); close_quote(); close_lists(); output.append("<hr>"); continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph(); close_quote(); close_lists()
            level = len(heading.group(1)); output.append(f"<h{level}>{inline(heading.group(2))}</h{level}>"); continue
        if line.startswith("> "):
            flush_paragraph(); close_lists()
            if not in_quote:
                output.append("<blockquote>"); in_quote = True
            output.append(f"<p>{inline(line[2:])}</p>"); continue
        bullet = re.match(r"^(\s*)[-*+]\s+(.+)$", line)
        if bullet:
            flush_paragraph(); close_quote()
            level = len(bullet.group(1).expandtabs(2)) // 2 + 1
            while len(list_stack) < level:
                output.append("<ul>"); list_stack.append(level)
            close_lists(level)
            output.append(f"<li>{inline(bullet.group(2))}</li>"); continue
        close_lists()
        paragraph.append(line)
    flush_paragraph(); close_quote(); close_lists()
    return "\n".join(output)


def page(title: str, description: str, content: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta name=\"description\" content=\"{html.escape(description, quote=True)}\">
  <title>{html.escape(title)} | SASD Board Notes</title>
  <link rel=\"stylesheet\" href=\"/assets/site.css\">
</head>
<body>
  <header class=\"site-header\"><div class=\"wrap\"><a class=\"brand\" href=\"/\">SASD Board Notes</a><p>Meeting notes and source Markdown</p></div></header>
  <main class=\"wrap\">{content}</main>
  <footer class=\"wrap\">Unofficial reference notes compiled from public meeting materials. Official Board minutes remain authoritative.</footer>
</body>
</html>"""


def main() -> None:
    if DOCS.exists(): shutil.rmtree(DOCS)
    (DOCS / "notes").mkdir(parents=True)
    shutil.copytree(ASSETS, DOCS / "assets")
    (DOCS / "CNAME").write_text((ROOT / "CNAME").read_text(encoding="utf-8"), encoding="utf-8")
    entries = []
    for md in sorted(NOTES.glob("*.md"), reverse=True):
        raw = md.read_text(encoding="utf-8")
        meta, _ = split_front_matter(raw)
        title = meta.get("title", md.stem.replace("-", " ").title())
        date = meta.get("meeting_date", "")
        slug = md.stem
        destination = DOCS / "notes" / slug
        destination.mkdir(parents=True)
        (destination / "index.html").write_text(page(title, "Rendered SASD Board meeting notes.", f"<article class=\"note\"><p class=\"back\"><a href=\"/\">← All notes</a></p><p class=\"notice\">This is an unofficial working reference. Verify formal actions, names, and vote language against official minutes.</p><p><a class=\"download\" href=\"./source.md\" download>Download Markdown source</a></p>{render_markdown(raw)}</article>"), encoding="utf-8")
        (destination / "source.md").write_text(raw, encoding="utf-8")
        entries.append((title, date, slug, meta.get("status", "")))
    cards = "".join(f"<article class=\"card\"><p class=\"date\">{html.escape(date)}</p><h2><a href=\"/notes/{slug}/\">{html.escape(title)}</a></h2><p>{html.escape(status.replace('-', ' '))}</p><p><a href=\"/notes/{slug}/\">Read rendered notes →</a> · <a href=\"/notes/{slug}/source.md\" download>Markdown</a></p></article>" for title, date, slug, status in entries)
    (DOCS / "index.html").write_text(page("Meeting index", "Public SASD Board meeting note index.", f"<section class=\"intro\"><p class=\"eyebrow\">PUBLIC REFERENCE</p><h1>School Board Meeting Notes</h1><p>Readable meeting notes with downloadable Markdown source files. These are unofficial working references; official minutes remain the formal record.</p></section><section class=\"cards\">{cards or '<p>No notes published yet.</p>'}</section>"), encoding="utf-8")
    print(f"Built {len(entries)} note(s) into {DOCS}")

if __name__ == "__main__":
    main()
