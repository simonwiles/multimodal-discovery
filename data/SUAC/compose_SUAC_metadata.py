#!/usr/bin/env python3

""" Module Description """


import json
import logging
from csv import DictReader
from pathlib import Path

IMG_PATH = Path("img")


def process_row(i, row):
    """Process a row from the metadata file."""
    item_id = f"SUAC_{i}"
    image_ids = row["CAPTION"].split(", ")

    image_paths = []
    for image_id in image_ids:
        image_path = list(IMG_PATH.glob(f"{image_id.lower().replace('.', '')}*.jpg"))
        try:
            assert len(image_path) == 1, f"Bad images for {image_id}: {image_path}!"
            image_paths.append(str(image_path[0]))
        except AssertionError:
            logging.error(f"Bad images for {image_id}: {image_path}!")

    if not image_paths:
        return None

    return {
        "item_id": item_id,
        "image_paths": image_paths,
        "description": row["DESCRIP"],
    }


def main():
    """Command-line entry-point."""

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    metadata = []

    with open("SUACDaggettObj.xlsx.csv", "r") as _fh:
        reader = DictReader(_fh)
        for i, row in enumerate(reader):
            if row["CAPTION"]:
                row_metadata = process_row(i, row)
                if row_metadata is not None:
                    metadata.append(row_metadata)

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
