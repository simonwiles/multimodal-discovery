#!/usr/bin/env python3

import json
import logging
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
            "metrics": {},
        }
        for metric in METRICS:
            logging.info(f"Comparing {img1['name']} and {img2['name']} ({metric})...")
            link["metrics"][metric] = getattr(sewar.full_ref, metric)(
                img1["img"], img2["img"]
            )

        links.append(link)

    nodes = [{k: v for k, v in img.items() if k != "img"} for img in images]
    print(json.dumps({"nodes": nodes, "links": links}, indent=2))


if __name__ == "__main__":
    main()
