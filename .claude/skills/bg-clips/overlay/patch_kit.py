#!/usr/bin/env python3
"""Idempotent fixes BG applies to a fresh clone of the Vibe Editing kit (pinned commit 83c5ff6).

1. About 38 scripts call _pl.Path(...) but never import pathlib as _pl (lost when the kit was
   anonymised), so they crash on start with NameError. Insert the import after the bootstrap's
   `import os as _os, sys as _sys` line.
2. BG brand vocabulary for the caption formatter (the kit's "brand interview" step): keep our
   acronyms upper case and our brand words cased (ICT, VSL, DFY, Whop, Discord, BusinessGrowR ...).
3. The kit's sf-audit flags any capitalised word it doesn't know; add our brand words to its
   whitelist and write a "bg" brand vocab (run sf-audit with --client bg).
Usage: python3 patch_kit.py <path to vibe-editing/plugins/vibe-editing>
"""
import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
fixed = 0
for f in root.rglob("*.py"):
    if ".venv" in f.parts or "site-packages" in f.parts:
        continue  # never touch third-party code
    s = f.read_text(errors="ignore")
    if "_pl." not in s or re.search(r"\bas _pl\b", s):
        continue
    if "import os as _os, sys as _sys" in s:
        s = s.replace("import os as _os, sys as _sys", "import os as _os, sys as _sys\nimport pathlib as _pl  # BG patch", 1)
    else:
        lines = s.split("\n"); i = 1 if lines and lines[0].startswith("#!") else 0
        lines.insert(i, "import pathlib as _pl  # BG patch"); s = "\n".join(lines)
    f.write_text(s); fixed += 1
print(f"patched {fixed} files (pathlib import)")

# 2. BG caption vocabulary
sf = root / "skills/caption-clips/scripts/spice_format.py"
t = sf.read_text()
if "BG vocab" not in t:
    t = t.replace('    "linkedin": "LinkedIn",\n}', '    "linkedin": "LinkedIn",\n    # BG vocab\n    "ict": "ICT", "vsl": "VSL", "dfy": "DFY", "cpbc": "CPBC", "nq": "NQ", "smc": "SMC",\n    "whop": "Whop", "discord": "Discord", "businessgrowr": "BusinessGrowR", "hyros": "HYROS",\n}', 1)
    t = t.replace('    "AOV",', '    "AOV", "ICT", "VSL", "DFY", "CPBC", "NQ", "SMC", "HYROS",  # BG vocab\n   ', 1)
    t = t.replace('    "I",   # the pronoun must always be capital', '    "I",   # the pronoun must always be capital\n    "Whop", "Discord", "BusinessGrowR", "Instagram",  # BG vocab', 1)
    sf.write_text(t); print("patched caption vocabulary")
else:
    print("caption vocabulary already patched")

# 3. sf-audit whitelist + bg brand vocab
au = root / "skills/sf-audit/scripts/audit.py"
t = au.read_text()
if "BG vocab" not in t:
    t = t.replace('    "I", "I\'m", "I\'ll", "I\'ve", "I\'d",', '    "I", "I\'m", "I\'ll", "I\'ve", "I\'d",\n    "Discord", "Whop", "BusinessGrowR", "Andy", "Louis",  # BG vocab', 1)
    au.write_text(t); print("patched sf-audit whitelist")
vd = root / "vault/clients/bg"; vd.mkdir(parents=True, exist_ok=True)
(vd / "vocab.txt").write_text("\n".join(["ICT", "NQ", "SMC", "VSL", "DFY", "CPBC", "MRR", "Whop", "Discord",
    "BusinessGrowR", "HYROS", "ManyChat", "Andy", "Louis", "iFVG"]) + "\n")
print("wrote vault/clients/bg/vocab.txt")
