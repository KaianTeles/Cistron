#!/usr/bin/env python3
"""Repository hygiene: nothing private, nothing stale, nothing half-renamed.

This exists because the workbook that ships with the repo is the easiest way
to publish unpublished research by accident - it is a real file people edit
in place. These checks assert the shipped data is the demo data, and that no
machine-specific path or address made it into the tree.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
import cistron as M                                             # noqa: E402

P, F = [], []
def ok(n, d=""):  P.append((n, d))
def bad(n, d=""): F.append((n, d))

TEXT = (".py", ".md", ".txt", ".cff", ".yml", ".yaml", ".toml", ".cfg", ".in")

SELF = os.path.abspath(__file__)


def text_files():
    """Every tracked text file except this one - it names the forbidden
    tokens on purpose, so scanning itself would always fail."""
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in
                   ("__pycache__", ".git", ".venv", "venv", "examples")]
        for f in files:
            full = os.path.join(base, f)
            if f.endswith(TEXT) and os.path.abspath(full) != SELF:
                yield full

# ------------------------------------------------- no machine-specific paths
hits = []
for p in text_files():
    s = open(p, encoding="utf-8", errors="replace").read()
    for pat, why in [
        (r"/Users/[A-Za-z0-9._-]+/", "absolute macOS home path"),
        (r"/home/[A-Za-z0-9._-]+/", "absolute Linux home path"),
        (r"[A-Za-z]:\\\\Users\\\\", "absolute Windows home path"),
        (r"[\w.+-]+@[\w-]+\.[\w.]+", "email address"),
    ]:
        for m in re.finditer(pat, s):
            # the MIT text and CI config legitimately mention neither
            hits.append((os.path.relpath(p, ROOT), why, m.group(0)[:40]))
(ok if not hits else bad)("no machine paths or addresses in tracked text",
                          "" if not hits else f"{hits[:3]}")

# ------------------------------------------- the shipped workbook is the demo
EXPECTED_CASSETTES = {"Variant A", "Variant B", "Variant C"}
EXPECTED_LABELS = {
    "5' homology", "3' homology", "Promoter 1", "Promoter 2",
    "Transit peptide", "Epitope tag", "Marker", "Recombination site",
    "Enzyme A", "Enzyme B", "Enzyme C",
}
wb_path = os.path.join(ROOT, M.DEFAULT_WORKBOOK)
if not os.path.exists(wb_path):
    bad("the default workbook ships with the repo", M.DEFAULT_WORKBOOK)
else:
    _, _, cons = M.load_workbook_config(wb_path)
    names = {c["name"] for c in cons}
    labels = {p["label"] for c in cons for p in c["parts"] if p["label"]}
    (ok if names == EXPECTED_CASSETTES else bad)(
        "shipped workbook holds only the demo constructs",
        "" if names == EXPECTED_CASSETTES else f"unexpected: {names - EXPECTED_CASSETTES}")
    extra = labels - EXPECTED_LABELS
    (ok if not extra else bad)("shipped workbook holds only the demo labels",
                               "" if not extra else f"unexpected: {sorted(extra)[:6]}")

    import openpyxl
    sheets = set(openpyxl.load_workbook(wb_path).sheetnames)
    allowed = {"Start here", "cassettes", "settings", "colors", "reference", "lists"}
    stray = sheets - allowed
    (ok if not stray else bad)("shipped workbook has no extra sheets",
                               "" if not stray else f"stray: {sorted(stray)}")

# -------------------------------------------------------- no stray artefacts
junk = []
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
    for f in files:
        if f.startswith("~$") or f == ".DS_Store" or f.endswith(".pyc"):
            junk.append(os.path.relpath(os.path.join(base, f), ROOT))
(ok if not junk else bad)("no lock files or OS cruft", str(junk[:4]))

# ------------------------------------------------------- the rename is total
old = []
for p in text_files():
    s = open(p, encoding="utf-8", errors="replace").read()
    for token in ("cassette_drawer", "cassette-drawer", "cassette_template"):
        if token in s:
            old.append((os.path.relpath(p, ROOT), token))
(ok if not old else bad)("no references to the old project name", str(old[:3]))

# ------------------------------------------------------ version is coherent
vers = {}
vers["cistron.py"] = M.__version__
for f, pat in (("CITATION.cff", r'^version:\s*"?([\d.]+)"?'),
               ("CHANGELOG.md", r"^##\s*([\d.]+)")):
    fp = os.path.join(ROOT, f)
    if os.path.exists(fp):
        m = re.search(pat, open(fp).read(), re.M)
        if m:
            vers[f] = m.group(1)
(ok if len(set(vers.values())) == 1 else bad)(
    "one version everywhere", ", ".join(f"{k}={v}" for k, v in vers.items()))

# --------------------------------------------------------- essential files
missing = [f for f in ("README.md", "LICENSE", "requirements.txt",
                       "QUICKSTART.txt", ".gitignore", "CITATION.cff",
                       "CHANGELOG.md", "KNOWN_ISSUES.md", M.DEFAULT_WORKBOOK)
           if not os.path.exists(os.path.join(ROOT, f))]
(ok if not missing else bad)("every expected file is present", str(missing))

print()
for n, d in P: print(f"  PASS  {n:46} {d}")
for n, d in F: print(f"  FAIL  {n:46} {d}")
print(f"\n{len(P)} passed, {len(F)} failed")
sys.exit(1 if F else 0)
