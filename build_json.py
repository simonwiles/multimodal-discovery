#!/usr/bin/env python3

import json
import logging
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

import cv2
import sewar

IMG_PATH = Path("imgs")

METRICS = [
    "rmse",
    "psnr",
    "sam",
]


def main():
    """Command-line entry-point."""

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    images = [
        {
            "id": i,
            "name": img_path.stem,
            "path": str(img_path),
            "img": cv2.imread(str(img_path)),
        }
        for i, img_path in enumerate(IMG_PATH.glob("*.jpg"))
    ]

    links = []
    for img1, img2 in combinations(images, 2):
        link = {
            "source": img1["id"],
            "target": img2["id"],
            "img-sim": {},
        }
        for metric in METRICS:
            logging.info(f"Comparing {img1['name']} and {img2['name']} ({metric})...")
            link["img-sim"][metric] = getattr(sewar.full_ref, metric)(
                img1["img"], img2["img"]
            )

        link["name-sim"] = SequenceMatcher(None, img1["name"], img2["name"]).ratio()

        links.append(link)

    nodes = [{k: v for k, v in img.items() if k != "img"} for img in images]

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
