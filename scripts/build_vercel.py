from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "apps" / "frontend"
PUBLIC_DIR = ROOT_DIR / "public"


def main() -> None:
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)

    shutil.copytree(
        FRONTEND_DIR,
        PUBLIC_DIR,
        ignore=shutil.ignore_patterns("runtime-config.js"),
    )

    (PUBLIC_DIR / "runtime-config.js").write_text(
        "window.API_BASE_URL = " + json.dumps("/api") + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
