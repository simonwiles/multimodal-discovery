#!/usr/bin/env python3

import json
import logging
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

import cv2
import sewar

METRICS = [
    "rmse",
    "psnr",
    "sam",
]


def main():
    """Command-line entry-point."""

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    suac_items = json.load(open("data/SUAC/SUAC_metadata.json", "r"))
    img_base = Path("data/SUAC")

    items = [
        {
            "id": item["item_id"],
            "description": item["description"],
            "path": item["image_paths"][0],
            "img": cv2.imread(str(img_base / item["image_paths"][0])),
        }
        for item in suac_items
    ]

    links = []
    for img1, img2 in combinations(items, 2):
        link = {
            "source": img1["id"],
            "target": img2["id"],
            "img-sim": {},
        }

        if img1["img"].shape != img2["img"].shape:
            print(img1["img"].shape, img2["img"].shape)
            img2_cmp = cv2.resize(img2["img"], img1["img"].shape[:2][::-1])
        else:
            img2_cmp = img2["img"]
        for metric in METRICS:
            logging.info(f"Comparing {img1['id']} and {img2['id']} ({metric})...")
            link["img-sim"][metric] = getattr(sewar.full_ref, metric)(
                img1["img"], img2_cmp
            )

        link["name-sim"] = SequenceMatcher(
            None, img1["description"], img2["description"]
        ).ratio()

        links.append(link)

    nodes = [{k: v for k, v in item.items() if k != "img"} for item in items]

    min_max = {
        metric: {
            "min": min(link["img-sim"][metric] for link in links),
            "max": max(link["img-sim"][metric] for link in links),
        }
        for metric in METRICS
    }

    def norm_metrics(metrics):
        nm = {}
        for k, v in metrics.items():
            nm[k] = (v - min_max[k]["min"]) / (min_max[k]["max"] - min_max[k]["min"])
        return nm

    links = [
        {
            "source": link["source"],
            "target": link["target"],
            "img-sim": norm_metrics(link["img-sim"]),
            "name-sim": link["name-sim"],
        }
        for link in links
    ]
    print(json.dumps({"nodes": nodes, "links": links}, indent=2))


if __name__ == "__main__":
    main()
