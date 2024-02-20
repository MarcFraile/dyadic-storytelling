#!/usr/bin/env python3


from pathlib import Path
import json


def main():
    root = Path("img/categories")
    assert root.is_dir()

    category_dirs = [ file for file in root.iterdir() if file.is_dir() ]
    category_dirs.sort()

    categories = {}

    for dir in category_dirs:
        name = dir.stem

        images = [ file for file in dir.iterdir() if file.is_file() and file.suffix == ".jpg" ]
        images.sort()

        data = {
            "character" : [ str(file) for file in images if file.stem.startswith("character") ],
            "object"    : [ str(file) for file in images if file.stem.startswith("object"   ) ],
            "place"     : [ str(file) for file in images if file.stem.startswith("place"    ) ],
        }

        categories[name] = data

    with open("categories.json", "w") as out_file:
        json.dump(categories, out_file, indent=4)


if __name__ == "__main__":
    main()
