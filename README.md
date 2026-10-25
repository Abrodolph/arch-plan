# arch-plan

Real-world architectural floor plan images with labels, for testing floor plan reading software.
Most images are messy real house-plan drawings: room names, dimensions in feet and inches, door swings,
stairs, fixtures, patios, dashed outlines, and varied drawing styles and resolutions.

## At a glance

| Subset | Images | What they look like | Labels |
|---|---|---|---|
| `bridge_d2` | 3,137 | Real house-plan drawings (JPEG, mostly ~1024 px, greyscale) | Symbol boxes; 435 also have region captions |
| `bridge_d1` | 1,639 | Real house-plan drawings (GIF, smaller, often coloured backgrounds) | Symbol boxes; 406 also have region captions |
| `bridge_captioned` | 352 | Real house-plan drawings, same style as d1 | Region captions only |
| `robin_clean` | 510 | Clean schematic plans with furniture symbols, no text | Symbol boxes; 190 have region captions |
| `robin_handdrawn` | 510 | Hand-drawn redraws of the ROBIN layouts | None (folder = room count) |
| **Total** | **6,148** | | **86,563 symbol boxes, 5,372 caption regions** |

5,128 of the images are real plans; the rest are ROBIN schematics and hand-drawn versions.

## Layout

```
images/<subset>/<id>.<gif|jpeg|jpg>
annotations/
  symbols_coco.json          all symbol boxes, COCO format, 16 normalised classes
  captions.jsonl             one line per captioned region: plan_id, image, bbox_xyxy, caption
  voc_symbols/<subset>/*.xml original Pascal-VOC symbol annotations, unchanged
  voc_captions/<subset>/*.xml original region-caption annotations, unchanged
index.csv                    one row per image: subset, kind, size, box and caption counts, per-class counts
scripts/build_repo.py        rebuilds this repo from the source clones
SOURCES.md                   research notes: what exists, what was used, what could not be reached
```

## Symbol classes (`symbols_coco.json`)

door 33,474 · window 19,175 · large_sink 6,858 · small_sink 6,485 · stairs 5,814 · tub 4,507 ·
bed 1,774 · small_sofa 1,568 · twin_sink 1,439 · coffee_table 1,381 · large_sofa 1,185 ·
kitchen_bar 834 · sink 788 · dining_table 779 · round_table 286 · armchair 216

Raw labels were normalised: `windows` → `window`, `small sink` → `small_sink`, and so on, plus a few typos.
The VOC files keep the original labels. The mapping is `CLASS_FIX` in `scripts/build_repo.py`.

## Example caption (`captions.jsonl`)

```json
{"plan_id": "bridge_d2_21001", "image": "images/bridge_d2/21001.jpeg",
 "bbox_xyxy": [73, 797, 453, 1139],
 "caption": "bedroom has a private bathroom with sink and bathing space"}
```

## Known label quirks

- Annotations are as published and not exhaustive. Some doors and windows have no box.
- In BRIDGE, toilets are generally boxed as `large_sink`.
- Room names and dimensions are printed on the images but are **not** annotated as text. Use OCR if you need them.

## Quick use (PowerShell)

```powershell
git clone https://github.com/Abrodolph/arch-plan
cd arch-plan
Import-Csv index.csv | Where-Object { $_.kind -eq "real" -and [int]$_.stairs -gt 0 } | Select-Object -First 20 plan_id, image
```

## Sources and licences

- **BRIDGE**: Goyal, Mistry, Chattopadhyay, Bhatnagar, "BRIDGE: Building Plan Repository for Image Description
  Generation, and Evaluation", ICDAR 2019, doi:10.1109/ICDAR.2019.00174. github.com/gesstalt/BRIDGE.
  The repository has **no licence file**. The plan images originally come from house-plan websites, and their
  copyright stays with the original designers. Use them for research and testing only, and keep this repo private.
- **ROBIN / ROBIN++**: Sharma, Gupta, Chattopadhyay, Mehta, "DANIEL: A Deep Architecture for Automatic Analysis
  and Retrieval of Building Floor Plans", ICDAR 2017. github.com/gesstalt/ROBIN, GPL-3.0 (see `LICENSE_ROBIN_GPL3.txt`).
