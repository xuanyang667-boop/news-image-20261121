"""Entrypoint: copy the pre-rendered front page to the output directory.

Stdlib only (os, shutil, sys). The grader runs `python3 -P -s main.py` in a
pinned Python image without Pillow and with the repo mounted read-only, so
this program must not import Pillow or write into the repo.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "assets", "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    dst = os.path.join(out_dir, "entry.png")
    if not os.path.isfile(src):
        print("error: assets/entry.png not found", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    if os.path.getsize(dst) == 0:
        print("error: output is 0 bytes", file=sys.stderr)
        return 1
    print(dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
