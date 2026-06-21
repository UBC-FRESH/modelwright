#!/usr/bin/env python3
"""Materialize the external FABLE Calculator benchmark workbooks locally.

The workbook binaries stay untracked. This helper downloads or consumes a local
Dropbox ZIP/directory, finds the expected files by checksum, and copies them to
the canonical ignored paths used by the rest of the benchmark scaffolding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "benchmarks" / "fable-calculator" / "manifest.json"
DEFAULT_DOWNLOAD_DIR = REPO_ROOT / "tmp" / "benchmark-downloads" / "fable-calculator"


class MaterializationError(RuntimeError):
    """Raised when benchmark workbooks cannot be materialized safely."""


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("benchmark_set") != "fable-calculator":
        raise MaterializationError(f"Unsupported benchmark manifest: {path}")
    if not isinstance(manifest.get("workbooks"), list):
        raise MaterializationError(f"Manifest has no workbook list: {path}")
    return manifest


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_workbooks(manifest: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    workbooks = manifest["workbooks"]
    if not all(isinstance(workbook, dict) for workbook in workbooks):
        raise MaterializationError("Manifest workbook entries must be objects.")
    return workbooks


def iter_source_files(source_dir: Path) -> Iterable[Path]:
    return (path for path in source_dir.rglob("*") if path.is_file())


def safe_repo_path(repo_root: Path, relative_path: str) -> Path:
    target = (repo_root / relative_path).resolve()
    root = repo_root.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise MaterializationError(f"Manifest path escapes repository root: {relative_path}") from exc
    return target


def dropbox_download_url(folder_url: str) -> str:
    parsed = urllib.parse.urlparse(folder_url)
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    query["dl"] = ["1"]
    return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query, doseq=True)))


def download_dropbox_zip(source_url: str, download_dir: Path) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)
    zip_path = download_dir / "fable-calculator-dropbox.zip"
    request = urllib.request.Request(
        dropbox_download_url(source_url),
        headers={"User-Agent": "modelwright-benchmark-materializer/1.0"},
    )
    print(f"Downloading FABLE benchmark folder to {zip_path}")
    with urllib.request.urlopen(request, timeout=120) as response:
        with zip_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    if not zipfile.is_zipfile(zip_path):
        raise MaterializationError(
            "Downloaded content is not a ZIP archive. Dropbox may have returned an HTML page; "
            "download the folder ZIP manually and rerun with --from-zip."
        )
    return zip_path


def extract_zip(zip_path: Path, extract_dir: Path) -> None:
    if not zipfile.is_zipfile(zip_path):
        raise MaterializationError(f"Not a ZIP archive: {zip_path}")
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_dir)


def index_files_by_sha256(source_dir: Path) -> dict[str, list[Path]]:
    if not source_dir.exists():
        raise MaterializationError(f"Source directory does not exist: {source_dir}")
    index: dict[str, list[Path]] = {}
    for path in iter_source_files(source_dir):
        index.setdefault(sha256_file(path), []).append(path)
    return index


def materialize_from_directory(
    source_dir: Path,
    manifest: Mapping[str, Any],
    repo_root: Path,
    *,
    force: bool = False,
) -> list[Path]:
    source_index = index_files_by_sha256(source_dir)
    copied_paths: list[Path] = []
    for workbook in expected_workbooks(manifest):
        expected_sha = str(workbook["sha256"])
        expected_size = int(workbook["bytes"])
        local_path = str(workbook["local_path"])
        destination = safe_repo_path(repo_root, local_path)
        matches = source_index.get(expected_sha, [])
        if not matches:
            filename = workbook.get("filename", local_path)
            raise MaterializationError(
                f"Could not find expected workbook payload for {filename} "
                f"with sha256 {expected_sha} under {source_dir}"
            )

        source = matches[0]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            existing_sha = sha256_file(destination)
            if existing_sha == expected_sha:
                print(f"Already present: {destination}")
                copied_paths.append(destination)
                continue
            if not force:
                raise MaterializationError(
                    f"Destination exists with the wrong checksum: {destination}. "
                    "Use --force to replace it."
                )

        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        actual_sha = sha256_file(destination)
        actual_size = destination.stat().st_size
        if actual_sha != expected_sha or actual_size != expected_size:
            raise MaterializationError(
                f"Materialized file failed verification: {destination} "
                f"(sha256={actual_sha}, bytes={actual_size})"
            )
        print(f"Materialized: {destination}")
        copied_paths.append(destination)
    return copied_paths


def materialize_from_zip(
    zip_path: Path,
    manifest: Mapping[str, Any],
    repo_root: Path,
    *,
    force: bool = False,
) -> list[Path]:
    with tempfile.TemporaryDirectory(prefix="modelwright-fable-benchmarks-") as temp_dir:
        extract_dir = Path(temp_dir) / "extracted"
        extract_dir.mkdir()
        print(f"Extracting {zip_path}")
        extract_zip(zip_path, extract_dir)
        return materialize_from_directory(extract_dir, manifest, repo_root, force=force)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download or copy the external FABLE Calculator benchmarks into tmp/private-workbooks/."
    )
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--from-zip", type=Path, help="Use an already downloaded Dropbox folder ZIP.")
    source_group.add_argument("--from-dir", type=Path, help="Use an already extracted/downloaded folder.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Benchmark manifest path.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repository root for local paths.")
    parser.add_argument("--download-dir", type=Path, default=DEFAULT_DOWNLOAD_DIR, help="Local ZIP download cache.")
    parser.add_argument("--source-url", help="Override the source Dropbox folder URL from the manifest.")
    parser.add_argument("--force", action="store_true", help="Replace existing canonical files with wrong checksums.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = load_manifest(args.manifest)
    try:
        if args.from_dir:
            materialized = materialize_from_directory(args.from_dir, manifest, args.repo_root, force=args.force)
        elif args.from_zip:
            materialized = materialize_from_zip(args.from_zip, manifest, args.repo_root, force=args.force)
        else:
            source_url = args.source_url or manifest["source"]["url"]
            zip_path = download_dropbox_zip(str(source_url), args.download_dir)
            materialized = materialize_from_zip(zip_path, manifest, args.repo_root, force=args.force)
    except MaterializationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Materialized {len(materialized)} FABLE benchmark workbook(s).")
    print("Verify with: sha256sum -c benchmarks/fable-calculator/checksums.sha256")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
