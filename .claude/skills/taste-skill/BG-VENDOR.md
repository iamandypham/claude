# Vendored copy (BusinessGrowR)

- Source: https://github.com/Leonxlnx/taste-skill, folder `skills/taste-skill`, MIT (LICENSE here).
- Pinned at commit f624f37a8c650b9cc550253104925efe4c8de246 (14 Oct 2026). Copied unchanged; this file is the only addition.
- Requested by Andy, 16 Oct 2026. Update by re-copying a newer commit on purpose, not by auto-update.
- Cloud boxes run as root: Chrome refuses to start without `--no-sandbox`. Point `CHROME_PATH` at a
  wrapper that adds it, e.g. `printf '#!/bin/sh\nexec /opt/pw-browsers/chromium-*/chrome-linux/chrome --no-sandbox "$@"\n'`.
- BG pages: house rules (no gradients, no eyebrows, etc.) are the skill's taste, not BG brand rules. Never use it to edit the live VSL/funnel directly; build side by side and bring it to Andy.
