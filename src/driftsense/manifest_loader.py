"""Manifest discovery helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence

import yaml

SUPPORTED_EXTENSIONS: Sequence[str] = (".yml", ".yaml")


@dataclass(frozen=True)
class LoadedManifest:
    """Represents a manifest loaded from disk."""

    source: Path
    content: Dict


def iter_manifest_files(root: Path) -> Iterator[Path]:
    """Yield manifest files under root respecting SUPPORTED_EXTENSIONS."""
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def _load_yaml_documents(path: Path) -> Iterable[Dict]:
    with path.open("r", encoding="utf-8") as handle:
        documents = yaml.safe_load_all(handle)
        for doc in documents:
            if doc:
                yield doc


def load_manifests(root: Path) -> List[LoadedManifest]:
    """Load all YAML manifests from directory."""
    manifests: List[LoadedManifest] = []
    for file_path in iter_manifest_files(root):
        for doc in _load_yaml_documents(file_path):
            manifests.append(LoadedManifest(source=file_path, content=doc))
    return manifests


def ensure_directory(path_str: str) -> Path:
    """Validate and return a directory Path."""
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Expected a directory: {path}")
    return path
