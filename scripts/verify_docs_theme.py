from __future__ import annotations

import argparse
from pathlib import Path


def verify_docs_theme(build_dir: Path) -> None:
    index_path = build_dir / "index.html"
    theme_css_path = build_dir / "_static" / "css" / "theme.css"
    theme_js_path = build_dir / "_static" / "js" / "theme.js"

    missing = [
        str(path)
        for path in (index_path, theme_css_path, theme_js_path)
        if not path.exists()
    ]
    if missing:
        raise SystemExit(f"Missing expected Sphinx RTD theme files: {', '.join(missing)}")

    index_html = index_path.read_text(encoding="utf-8")
    required_markers = {
        "_static/css/theme.css": "RTD theme stylesheet",
        "wy-nav-side": "RTD side navigation",
        "sphinx_rtd_theme": "RTD theme attribution",
    }
    absent = [
        description
        for marker, description in required_markers.items()
        if marker not in index_html
    ]
    if absent:
        raise SystemExit(
            "Built docs do not look like the Sphinx Read the Docs theme: "
            + ", ".join(absent)
        )

    forbidden_markers = {
        "minima": "Jekyll minima theme",
        "jekyll-theme": "Jekyll theme marker",
    }
    found_forbidden = [
        description
        for marker, description in forbidden_markers.items()
        if marker in index_html.lower()
    ]
    if found_forbidden:
        raise SystemExit(
            "Built docs contain fallback-site markers: "
            + ", ".join(found_forbidden)
        )

    print(f"Verified Sphinx Read the Docs themed artifact: {build_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify that built docs use the Sphinx Read the Docs theme."
    )
    parser.add_argument(
        "build_dir",
        nargs="?",
        default="_build/html",
        help="Built Sphinx HTML directory.",
    )
    args = parser.parse_args()
    verify_docs_theme(Path(args.build_dir))


if __name__ == "__main__":
    main()
