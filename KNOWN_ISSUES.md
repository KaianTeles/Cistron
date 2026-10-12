# Known issues

Everything here is reproduced and measured, not suspected. None of it
affects a figure drawn with the default settings — each one needs a setting
pushed well past where it is useful, or is a limit of the thing itself
rather than a mistake. They are written down because finding them yourself
and wondering whether you had done something wrong is worse.

Numbers are in the drawing's own units, where a glyph body is 30 tall and
the default `label_pt` is 11.

---

### 1. An inside label spills out of its glyph above `label_pt` 28

With `labels = inside`, a glyph grows **sideways** to fit its name but never
taller, so from about `label_pt = 28` the descenders of letters like `g`, `p`
and `y` hang below the glyph. At 36 they are 5.5 units out and sit on the
white of the page.

*Measured*: `label_pt` 28 → descender at 64.0, glyph bottom at 63.0.

**Use instead**: `labels = outside`, which has no ceiling, or keep
`label_pt` at or below 24 with `inside`. Nothing warns about this yet.

---

### 2. A long row title can meet the labels above `label_pt` 36

`row_titles = left` writes the construct name beside the row but is given no
vertical budget of its own, so at very large label sizes a tall title can
come within a label's height of the first tier of outside labels.

*Measured*: at `label_pt = 36`, the title baseline is 35.2 from the nearest
label baseline.

**Use instead**: `row_titles = above`, which is budgeted properly, or a
shorter construct name.

---

### 3. Fusing a point feature does not look fused

`join = yes` removes the backbone between two parts, which is what a fusion
means. A few glyphs are drawn narrower than the slot they occupy, so fusing
one still shows a short length of backbone:

| part | gap left on each side |
|---|---|
| `polya` | about 12.8 |
| `scar`, `stop_codon` | about 4.3 |
| `restriction_site`, `protease_site` | about 4.0 |
| `insulator` | about 3.6 |
| `promoter`, `terminator` | about 2.5 |

Every length-bearing part — `cds`, `ctp`, `nls`, `tag`, `p2a`, `linker`,
`spacer` — fuses with no gap at all, and those are the ones a fusion is
normally made of. The likely case to notice is a `stop_codon` joined to a
CDS.

---

### 4. One warning suggests a width that does not fix it

When the legend grows tall relative to the constructs, the sanity check
says *"widen figure_width_cm to about N cm"*. That N is a rough multiple
rather than a solved value, and at N the legend can still be over the
threshold. The other fix offered in the same sentence — turn the legend off
and name the glyphs with `labels = outside` — does work.

Every other piece of advice the sanity check gives has been checked to
clear the warning it belongs to when followed exactly.

---

### 5. Colour cannot separate everything, and the figure says so

Past roughly a dozen parts, no palette has enough distinct hues, and the
tool extends it with tints and shades of its own colours. Beyond that the
sanity check reports the pairs that have ended up close rather than
pretending otherwise. The ordered ramps — `viridis`, `cividis`, `ocean`,
`grayscale` — are the earliest to run out, because their steps are meant to
resemble each other.

This is a limit, not a defect: **name the glyphs** (`labels = outside`)
rather than reaching for a bigger palette.

Related, and by design: keeping every colour in a figure distinct is a
property of the whole figure, so adding a part can change a colour
elsewhere — a median of 3 to 35 per cent of them, depending on the palette,
and none at all when nothing was too close. Pin anything that must never
move in the `colors` sheet; a pin is never touched.

---

## Reporting something else

If a figure comes out wrong, `python3 cistron.py --check` prints what the
tool thinks it is drawing without writing anything, which is usually enough
to tell a settings problem from a drawing one. An issue with the workbook
attached, or just the rows that reproduce it, is the most useful report.
