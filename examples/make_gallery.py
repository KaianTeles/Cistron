#!/usr/bin/env python3
"""Regenerate the gallery images in this folder.

Not needed to use cistron — this only rebuilds the pictures in the README.

    pip install cairosvg matplotlib pillow
    python3 examples/make_gallery.py

Everything here is invented demo data. Keep it that way: these images go
into a public repository.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

import cistron as C                                              # noqa: E402

try:
    import cairosvg
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("needs: pip install cairosvg pillow")

OUT = HERE
TMP = os.path.join(HERE, "_tmp")
os.makedirs(TMP, exist_ok=True)


# ----------------------------------------------------------- demo material
def constructs(spec):
    out = []
    for name, parts in spec:
        rows = []
        for t, l, sz, d, j in parts:
            canon = C.ALIASES.get(t.lower())
            if canon is None:
                raise SystemExit(f"unknown part type in demo data: {t!r}")
            rows.append({"type": canon, "label": l, "size": sz or None,
                         "dir": d or "fwd", "join": bool(j), "color": ""})
        out.append({"name": name, "parts": rows})
    return out


def variant(gene, promoter, tag=True):
    p = [("HA", "5' homology", "M", "", 0),
         ("prom", promoter, "", "", 0),
         ("ctp", "Transit peptide", "XS", "", 1),
         ("cds", gene, "L", "", 1)]
    if tag:
        p.append(("tag", "Epitope tag", "XS", "", 1))
    p += [("term", "", "", "", 0),
          ("prom", "Promoter 2", "", "", 0),
          ("cds", "Marker", "M", "rev", 0),
          ("loxp", "Recombination site", "", "", 0),
          ("HA", "3' homology", "M", "", 0)]
    return p


PANEL = constructs([
    ("Variant A", variant("Enzyme A", "Promoter 1")),
    ("Variant B", variant("Enzyme B", "Promoter 1")),
    ("Variant C", variant("Enzyme C", "Promoter 3")),
])

# Every part type in the registry, grouped the way the README groups them.
# Built from PART_TYPES so this sheet cannot drift out of date.
VOCAB_GROUPS = [
    ("transcription", ["promoter", "enhancer", "operator", "silencer",
                       "insulator", "terminator", "polya", "attenuator"]),
    ("translation",   ["rbs", "kozak", "ires", "utr5", "utr3", "stop_codon"]),
    ("coding",        ["cds", "marker", "reporter", "ctp", "nls", "tag",
                       "degron", "p2a", "linker", "protease_site", "intron",
                       "exon"]),
    ("RNA",           ["ncrna", "sgrna", "shrna", "ribozyme", "riboswitch",
                       "aptamer"]),
    ("vector",        ["homology_arm", "backbone", "ori", "orit",
                       "restriction_site", "overhang", "scar", "spacer",
                       "mcs", "primer", "barcode", "engineered_region",
                       "locus"]),
    ("recombination", ["loxp", "ltr", "itr", "transposon_end", "tdna_border",
                       "pam"]),
    ("chromosome",    ["cen", "telomere", "ars", "unspecified"]),
]

_listed = [t for _, g in VOCAB_GROUPS for t in g]
assert sorted(_listed) == sorted(C.PART_TYPES), (
    "VOCAB_GROUPS is out of sync with PART_TYPES: "
    f"missing {sorted(set(C.PART_TYPES) - set(_listed))}, "
    f"unknown {sorted(set(_listed) - set(C.PART_TYPES))}")

VOCAB = constructs([
    (g, [(t, t.replace("_", " "), "", "", 0) for t in types])
    for g, types in VOCAB_GROUPS
])


def draw(cons, name, **over):
    s = dict(C.SETTINGS)
    s.update(theme="journal", labels="outside", label_repeat="once",
             row_titles="left", show_legend="auto", figure_width_cm=18,
             figure_height_cm=None, palette_mode="theme",
             _basedir=TMP, outfile=f"{name}.svg")
    s.update(over)
    st, pal, _, pal_name = C.resolve_theme(s)
    res = C.assign_palette(cons, {}, pal, "theme")
    path = C.build_figure(cons, s, res, st)[0]
    return Image.open(io.BytesIO(cairosvg.svg2png(url=path, output_width=1500)))


def _font(size, bold=True):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf",
              "/System/Library/Fonts/Supplemental/DejaVuSans%s.ttf"):
        try:
            return ImageFont.truetype(p % ("-Bold" if bold else ""), size)
        except OSError:
            continue
    return ImageFont.load_default()


CAP_F, TIT_F = _font(26), _font(34)
PAD, GUT, CAP_H, BORDER = 34, 34, 42, "#DDE1E4"


def grid(panels, cols, out, title, cell_w=720):
    """Lay panels out on a plain white sheet, each scaled to cell_w."""
    ims = []
    for cap, im in panels:
        h = max(1, round(im.height * cell_w / im.width))
        ims.append((cap, im.resize((cell_w, h), Image.LANCZOS)))

    rows = [ims[i:i + cols] for i in range(0, len(ims), cols)]
    row_h = [max(im.height for _, im in r) + CAP_H for r in rows]
    top = PAD + (54 if title else 0)
    W = PAD * 2 + cols * cell_w + (cols - 1) * GUT
    H = top + sum(row_h) + GUT * (len(rows) - 1) + PAD

    sheet = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((PAD, PAD - 6), title, font=TIT_F, fill="#15181B")

    y = top
    for r, rh in zip(rows, row_h):
        x = PAD
        for cap, im in r:
            if cap:
                d.text((x + 2, y + 4), cap, font=CAP_F, fill="#2B3034")
            sheet.paste(im, (x, y + CAP_H))
            d.rectangle([x, y + CAP_H, x + im.width - 1,
                         y + CAP_H + im.height - 1], outline=BORDER)
            x += cell_w + GUT
        y += rh + GUT

    sheet.save(os.path.join(OUT, out), optimize=True)
    print("wrote", out, sheet.size)


# ------------------------------------------------------------------ themes
grid([(f"theme = {t}", draw(PANEL, f"t_{t}", theme=t))
      for t in ["journal", "publication", "poster", "slides",
                "lineart", "swiss", "midnight", "blueprint"]],
     2, "gallery_themes.png",
     "themes — one word in the settings sheet")

# ---------------------------------------------------------------- palettes
grid([(f"palette = {p}", draw(PANEL, f"p_{p}", palette=p, style="classic"))
      for p in ["spectrum", "nature", "okabe-ito", "tol-muted",
                "vivid", "deep", "earth", "pastel", "viridis",
                "cividis", "ocean", "grayscale"]],
     2, "gallery_palettes.png",
     "palettes — okabe-ito, tol-muted and cividis are colour-blind safe")

# ------------------------------------------------------------------ labels
grid([("labels = inside  (glyph widens to fit)", draw(PANEL, "l_in", labels="inside")),
      ("labels = below", draw(PANEL, "l_bel", labels="below")),
      ("labels = outside  (stacked in tiers)", draw(PANEL, "l_out", labels="outside")),
      ("labels = none  (legend only)", draw(PANEL, "l_none", labels="none",
                                            show_legend="TRUE"))],
     2, "gallery_labels.png", "label placement")

# ------------------------------------------- repeat policy and row titles
grid([("label_repeat = all", draw(PANEL, "r_all", label_repeat="all")),
      ("label_repeat = once  (only what varies)", draw(PANEL, "r_once",
                                                       label_repeat="once")),
      ("row_titles = left", draw(PANEL, "rt_left", row_titles="left")),
      ("row_titles = above", draw(PANEL, "rt_above", row_titles="above"))],
     2, "gallery_labelling.png",
     "how often a name is printed, and where the construct name goes")

# ------------------------------------------------------------- part types
grid([("", draw(VOCAB, "vocab", figure_width_cm=30, cassette_spacing=76,
                 label_pt=8.5, labels="outside", label_repeat="all",
                 anchor_side="left"))],
     1, "gallery_parts.png",
     f"all {len(C.PART_TYPES)} part types, across "
     f"{len(set(v['glyph'] for v in C.PART_TYPES.values()))} glyph shapes",
     cell_w=1460)

# ----------------------------------------- join, dir and anchor_side
def _fuse(join):
    return [("prom", "Promoter", "", "", 0),
            ("ctp", "Signal", "XS", "", join),
            ("cds", "Enzyme", "L", "", join),
            ("tag", "Tag", "XS", "", join),
            ("term", "", "", "", 0)]


FUSE_OFF = constructs([("blank", _fuse(0))])
FUSE_ON = constructs([("yes", _fuse(1))])

DIRS = constructs([("dir blank", [("prom", "Promoter", "", "", 0),
                                  ("cds", "Enzyme", "L", "", 0),
                                  ("loxp", "Site", "", "", 0)]),
                   ("dir = rev", [("prom", "Promoter", "", "rev", 0),
                                  ("cds", "Enzyme", "L", "rev", 0),
                                  ("loxp", "Site", "", "rev", 0)])])

# anchor_side only shows itself when the constructs differ in length
RAGGED = constructs([
    ("Long",   [("ha", "5' arm", "M", "", 0), ("prom", "Promoter", "", "", 0),
                ("cds", "Enzyme", "L", "", 0), ("term", "", "", "", 0),
                ("ha", "3' arm", "M", "", 0)]),
    ("Medium", [("ha", "5' arm", "M", "", 0), ("prom", "Promoter", "", "", 0),
                ("cds", "Enzyme", "M", "", 0)]),
    ("Short",  [("ha", "5' arm", "M", "", 0), ("loxp", "Site", "", "", 0)]),
])

LAY = dict(figure_width_cm=15, labels="outside", label_repeat="all",
           cassette_spacing=108)
ONE = dict(LAY, cassette_spacing=94)
grid([("join = blank \u2014 parts spaced along the backbone",
       draw(FUSE_OFF, "j_off", row_titles="none", **ONE)),
      ("join = yes \u2014 flush against the previous part, a fusion",
       draw(FUSE_ON, "j_on", row_titles="none", **ONE)),
      ("anchor_side = right (default) \u2014 ragged left, aligned right",
       draw(RAGGED, "a_r", row_titles="left", anchor_side="right", **LAY)),
      ("anchor_side = left \u2014 aligned left, ragged right",
       draw(RAGGED, "a_l", row_titles="left", anchor_side="left", **LAY)),
      ("dir \u2014 blank points right, rev points left",
       draw(DIRS, "dirs", row_titles="left", **LAY))],
     2, "gallery_layout.png",
     "fusing parts, pointing them backwards, and lining rows up",
     cell_w=740)

# ------------------------------------------------- what you type -> what you get
WALK_HEAD = ["cassette", "order", "type", "label", "size", "dir", "join"]
WALK_ROWS = [
    ["Reporter line", "1", "prom",  "Promoter 1",      "",   "",    ""],
    ["",              "2", "rbs",   "",                "",   "",    ""],
    ["",              "3", "cds",   "Reporter",        "L",  "",    ""],
    ["",              "4", "tag",   "Epitope tag",     "XS", "",    "yes"],
    ["",              "5", "term",  "",                "",   "",    ""],
    ["",              "6", "prom",  "Promoter 2",      "",   "",    ""],
    ["",              "7", "cds",   "Marker",          "M",  "rev", ""],
    ["",              "8", "loxp",  "Recombination site", "", "",   ""],
]
WALK = constructs([("Reporter line", [(r[2], r[3], r[4], r[5], r[6] == "yes")
                                      for r in WALK_ROWS])])

TBL_H, TBL_F, TBL_B = 46, _font(24, False), _font(24, True)
COL_W = [250, 100, 120, 330, 95, 95, 95]


def table_image(head, rows):
    w = sum(COL_W) + 2
    h = TBL_H * (len(rows) + 1) + 2
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    y = 0
    for j, (txt, cw) in enumerate(zip(head, COL_W)):
        x = sum(COL_W[:j])
        d.rectangle([x, y, x + cw, y + TBL_H], fill="#EDF0F2", outline="#C8CED3")
        d.text((x + 12, y + 11), txt, font=TBL_B, fill="#22272B")
    for i, row in enumerate(rows):
        y = TBL_H * (i + 1)
        for j, (txt, cw) in enumerate(zip(row, COL_W)):
            x = sum(COL_W[:j])
            d.rectangle([x, y, x + cw, y + TBL_H], fill="white", outline="#DDE1E4")
            d.text((x + 12, y + 11), txt, font=TBL_F, fill="#22272B")
    return im


grid([("the cassettes sheet", table_image(WALK_HEAD, WALK_ROWS)),
      ("what cistron draws from it",
       draw(WALK, "walk", figure_width_cm=16, labels="outside",
            label_repeat="all", row_titles="none", cassette_spacing=112))],
     1, "gallery_walkthrough.png",
     "eight rows in, one figure out", cell_w=1240)

# the headline image: one construct set, the default look
im = draw(PANEL, "hero")        # the default look, no overrides
im.save(os.path.join(OUT, "example_figure.png"))
import shutil
shutil.copy(os.path.join(TMP, "hero.svg"), os.path.join(OUT, "example_figure.svg"))
print("wrote example_figure.png / .svg")

shutil.rmtree(TMP, ignore_errors=True)
print("\ngallery rebuilt")
