"""Assemble the arch-plans repo from the BRIDGE and ROBIN source clones.

Usage: python scripts/build_repo.py <path/to/BRIDGE> <path/to/ROBIN-extracted>
Writes images/, annotations/ and index.csv next to this scripts/ folder.
"""
import csv
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
BRIDGE = Path(sys.argv[1]) / "dataset_bridge"
ROBIN_PP = Path(sys.argv[2])  # folder containing ROBIN++/<n>_rooms/*.jpg

# raw label -> normalised class; None drops the box (typos with no clear meaning)
CLASS_FIX = {
    "windows": "window", "dow": "door", "stair": "stairs", "tib": "tub",
    "small sink": "small_sink", "large sink": "large_sink", "twin sink": "twin_sink",
    "kitchen bar": "kitchen_bar", "Kitchen_bar": "kitchen_bar",
    "small sofa": "small_sofa", "large sofa": "large_sofa",
    "dining table": "dining_table", "dining-table": "dining_table",
    "round table": "round_table", "coffee table": "coffee_table", "arm_chair": "armchair",
    "dog": None, "small": None, "cavity": None,
}
SUM_CLASSES = ["door", "window", "stairs", "tub", "sink", "small_sink", "large_sink",
               "twin_sink", "kitchen_bar", "bed", "small_sofa", "large_sofa",
               "dining_table", "round_table", "coffee_table", "armchair"]


def parse_voc(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None
    objs = []
    for o in root.iter("object"):
        b = o.find("bndbox")
        if b is None:
            continue
        box = [int(float(b.findtext(k))) for k in ("xmin", "ymin", "xmax", "ymax")]
        objs.append({"label": (o.findtext("name") or "").strip(), "bbox_xyxy": box})
    return objs


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main():
    subsets = [
        # name, image dir, image ext, symbol xml dir, caption xml dir, kind
        ("bridge_d1", BRIDGE / "Symbol_spotting/d1_sym", "gif",
         BRIDGE / "Symbol_spotting/d1_sym", BRIDGE / "region_wise_captions/Region_wise_annotations1", "real"),
        ("bridge_d2", BRIDGE / "Symbol_spotting/d2_sym", "jpeg",
         BRIDGE / "Symbol_spotting/d2_sym", BRIDGE / "region_wise_captions/Region_wise_annotations2", "real"),
        # captioned plans that are not in d1
        ("bridge_captioned", BRIDGE / "region_wise_captions/Region_wise_annotations1", "gif",
         None, BRIDGE / "region_wise_captions/Region_wise_annotations1", "real"),
        ("robin_clean", BRIDGE / "Symbol_spotting/ROBIN_symbol", "jpg",
         BRIDGE / "Symbol_spotting/ROBIN_symbol", BRIDGE / "region_wise_captions/Robin_regions", "schematic"),
    ]
    d1_ids = {p.stem for p in (BRIDGE / "Symbol_spotting/d1_sym").glob("*.gif")}

    coco = {"images": [], "annotations": [], "categories": []}
    cat_ids = {}
    captions = []
    rows = []
    raw_labels = Counter()

    for name, img_dir, ext, sym_dir, cap_dir, kind in subsets:
        for img in sorted(img_dir.glob(f"*.{ext}"), key=lambda p: p.stem):
            if name == "bridge_captioned" and img.stem in d1_ids:
                continue
            pid = f"{name}_{img.stem}"
            rel_img = Path("images") / name / img.name
            copy(img, REPO / rel_img)
            with Image.open(img) as im:
                w, h = im.size

            syms = []
            if sym_dir and (sym_dir / f"{img.stem}.xml").exists():
                src = sym_dir / f"{img.stem}.xml"
                copy(src, REPO / "annotations/voc_symbols" / name / src.name)
                syms = parse_voc(src) or []
            caps = []
            if cap_dir and (cap_dir / f"{img.stem}.xml").exists():
                src = cap_dir / f"{img.stem}.xml"
                copy(src, REPO / "annotations/voc_captions" / name / src.name)
                caps = parse_voc(src) or []

            image_id = len(coco["images"]) + 1
            coco["images"].append({"id": image_id, "file_name": str(rel_img), "width": w,
                                   "height": h, "plan_id": pid, "subset": name})
            counts = Counter()
            for s in syms:
                raw_labels[s["label"]] += 1
                label = CLASS_FIX.get(s["label"], s["label"])
                if not label:
                    continue
                counts[label] += 1
                if label not in cat_ids:
                    cat_ids[label] = len(cat_ids) + 1
                x0, y0, x1, y1 = s["bbox_xyxy"]
                coco["annotations"].append({
                    "id": len(coco["annotations"]) + 1, "image_id": image_id,
                    "category_id": cat_ids[label], "bbox": [x0, y0, x1 - x0, y1 - y0],
                    "area": (x1 - x0) * (y1 - y0), "iscrowd": 0})
            for c in caps:
                captions.append({"plan_id": pid, "image": str(rel_img),
                                 "bbox_xyxy": c["bbox_xyxy"], "caption": c["label"]})

            rows.append({"plan_id": pid, "source": "BRIDGE" if name.startswith("bridge") else "ROBIN",
                         "subset": name, "kind": kind, "image": str(rel_img), "width": w, "height": h,
                         "symbol_boxes": sum(counts.values()), "caption_regions": len(caps),
                         **{c: counts.get(c, 0) for c in SUM_CLASSES}})

    # ROBIN++: hand-drawn redraws of the ROBIN layouts, no box labels
    for img in sorted(ROBIN_PP.glob("*_rooms/*.jpg")):
        rel_img = Path("images/robin_handdrawn") / img.name
        copy(img, REPO / rel_img)
        with Image.open(img) as im:
            w, h = im.size
        rows.append({"plan_id": f"robin_handdrawn_{img.stem}", "source": "ROBIN++",
                     "subset": "robin_handdrawn", "kind": "hand-drawn", "image": str(rel_img),
                     "width": w, "height": h, "symbol_boxes": 0, "caption_regions": 0,
                     **{c: 0 for c in SUM_CLASSES}})

    coco["categories"] = [{"id": i, "name": n} for n, i in cat_ids.items()]
    out = REPO / "annotations"
    out.mkdir(exist_ok=True)
    (out / "symbols_coco.json").write_text(json.dumps(coco))
    with open(out / "captions.jsonl", "w") as f:
        for c in captions:
            f.write(json.dumps(c) + "\n")
    with open(REPO / "index.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)

    print("images", len(rows), Counter(r["subset"] for r in rows))
    print("symbol boxes", len(coco["annotations"]), "classes", len(cat_ids))
    print("caption regions", len(captions))
    print("raw labels", raw_labels.most_common())


if __name__ == "__main__":
    main()
