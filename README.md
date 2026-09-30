# SASD Board Notes

A public static reference site for SASD Board-meeting notes. Each meeting is published as both a readable HTML page and its original Markdown source.

## Important record-status notice

This site is an unofficial reference. It may contain audio-transcript-derived notes and packet summaries. **Official Board minutes remain authoritative** for formal action, names, vote counts, and exact motion language.

## Add a meeting

1. Copy a reviewed Markdown note into `notes/` using a date-led filename, for example:
   ```text
   notes/2026-10-26-board-meeting.md
   ```
2. Include front matter such as:
   ```yaml
   ---
   title: SASD Board Meeting Notes — October 26, 2026
   meeting_date: 2026-10-26
   status: draft-from-audio; verify formal motions and names against official minutes
   ---
   ```
3. Run `python3 scripts/build.py`.
4. Review `docs/`, commit the source note and generated files, then push to `main`.

The deploy workflow also builds the site from `notes/` automatically before publishing.

## Publishing to GitHub Pages

1. Create a **public** GitHub repository and push this project.
2. In repository settings, open **Pages** and set the source to **GitHub Actions**.
3. In Cloudflare DNS, create a CNAME for `boardnotes.saltyoldgeek.com` pointing to the GitHub Pages hostname shown in Pages settings.
4. Add `boardnotes.saltyoldgeek.com` as the custom domain in GitHub Pages, then enable HTTPS once DNS validates.

This public-site design intentionally does not use Cloudflare Access. GitHub Pages remains publicly reachable through its `github.io` address, so Cloudflare Access would not be a complete access boundary.

## Local preview

```bash
python3 scripts/build.py
python3 -m http.server 8080 --directory docs
```

Open `http://127.0.0.1:8080`.
