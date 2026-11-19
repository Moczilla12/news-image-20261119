#!/usr/bin/env python3
"""news-image-20261119 entry: write the finished front page to the output.

The entry image is the pre-rendered newspaper front page (front-page.jpg,
1024x1024 JPEG) held in this repository. This program copies it to the
output directory as entry.png, then checks the copy is a real, non-empty
JPEG before reporting where it wrote it and how big it is.

Output directory: $MAKEFUN_OUTPUT_DIR when set, otherwise /output.
The program uses only the Python standard library and performs no I/O
besides reading the bundled image and writing the single output file.
"""
import hashlib
import os
import shutil
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(REPO_DIR, "front-page.jpg")


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, "entry.png")

    # The bundled front page must exist and be a JPEG before we copy it.
    if not os.path.isfile(SOURCE):
        print("error: bundled image missing: " + SOURCE, file=sys.stderr)
        return 1
    with open(SOURCE, "rb") as handle:
        head = handle.read(2)
    if head != b"\xff\xd8":
        print("error: bundled image is not a JPEG: " + SOURCE, file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SOURCE, target)

    with open(target, "rb") as handle:
        payload = handle.read()
    if not payload:
        print("error: output is empty: " + target, file=sys.stderr)
        return 1
    if payload[:2] != b"\xff\xd8":
        print("error: output is not a JPEG (bad magic bytes): " + target,
              file=sys.stderr)
        return 1

    digest = hashlib.sha256(payload).hexdigest()
    print("wrote " + target)
    print("bytes " + str(len(payload)))
    print("sha256 " + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
