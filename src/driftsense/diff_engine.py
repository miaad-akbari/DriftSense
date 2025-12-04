"""Core drift comparison logic."""

from __future__ import annotations

import difflib
import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

from .manifest_loader import LoadedManifest

CLUSTER_SCOPE = "cluster"


@dataclass(frozen=True, order=True)
class ResourceKey:
    """Unique identifier for a Kubernetes resource."""

    kind: str
    name: str
    namespace: str = CLUSTER_SCOPE

    @classmethod
    def from_manifest(cls, manifest: Mapping) -> "ResourceKey":
        metadata = manifest.get("metadata", {})
        namespace = metadata.get("namespace") or CLUSTER_SCOPE
        return cls(
            kind=str(manifest.get("kind", "Unknown")),
            name=str(metadata.get("name", "unnamed")),
            namespace=str(namespace),
        )

    def human(self) -> str:
        ns = self.namespace if self.namespace != CLUSTER_SCOPE else "(cluster)"
        return f"{self.kind}/{self.name} [{ns}]"


@dataclass
class ManifestRecord:
    key: ResourceKey
    manifest: Mapping
    source: str


@dataclass
class ChangedResource:
    key: ResourceKey
    diff: str
    desired_source: str
    actual_source: str


@dataclass
class DriftReport:
    missing: List[ManifestRecord] = field(default_factory=list)
    extra: List[ManifestRecord] = field(default_factory=list)
    changed: List[ChangedResource] = field(default_factory=list)

    def has_drift(self) -> bool:
        return any((self.missing, self.extra, self.changed))

    def to_dict(self) -> Dict:
        return {
            "missing": [record.key.__dict__ for record in self.missing],
            "extra": [record.key.__dict__ for record in self.extra],
            "changed": [
                {
                    "key": change.key.__dict__,
                    "diff": change.diff,
                    "desired_source": change.desired_source,
                    "actual_source": change.actual_source,
                }
                for change in self.changed
            ],
        }

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def index_manifests(
    manifests: Sequence[LoadedManifest], ignore_kinds: Iterable[str]
) -> Dict[ResourceKey, ManifestRecord]:
    ignore = {kind.lower() for kind in ignore_kinds}
    index: Dict[ResourceKey, ManifestRecord] = {}
    for loaded in manifests:
        manifest = loaded.content
        kind = str(manifest.get("kind", "")).strip()
        if not kind or kind.lower() in ignore:
            continue
        key = ResourceKey.from_manifest(manifest)
        index[key] = ManifestRecord(
            key=key,
            manifest=manifest,
            source=str(loaded.source),
        )
    return index


EPHEMERAL_FIELDS = {
    ("metadata", "annotations", "kubectl.kubernetes.io/last-applied-configuration"),
    ("metadata", "creationTimestamp"),
    ("metadata", "resourceVersion"),
    ("metadata", "generation"),
    ("metadata", "managedFields"),
    ("metadata", "uid"),
}


def sanitize_manifest(manifest: Mapping) -> MutableMapping:
    """Return a shallow copy without noisy fields."""
    def drop_path(target: MutableMapping, path: Sequence[str]) -> None:
        current = target
        for segment in path[:-1]:
            if not isinstance(current, MutableMapping):
                return
            current = current.get(segment)
            if current is None:
                return
        if isinstance(current, MutableMapping):
            current.pop(path[-1], None)

    sanitized = json.loads(json.dumps(manifest))  # deep copy
    for path in EPHEMERAL_FIELDS:
        drop_path(sanitized, path)
    sanitized.pop("status", None)
    return sanitized


def render_diff(desired: Mapping, actual: Mapping) -> str:
    desired_text = json.dumps(desired, indent=2, sort_keys=True).splitlines()
    actual_text = json.dumps(actual, indent=2, sort_keys=True).splitlines()
    diff = difflib.unified_diff(
        desired_text,
        actual_text,
        fromfile="desired",
        tofile="actual",
        lineterm="",
        n=3,
    )
    return "\n".join(diff)


def compare(
    desired_manifests: Sequence[LoadedManifest],
    actual_manifests: Sequence[LoadedManifest],
    *,
    ignore_kinds: Iterable[str] = (),
) -> DriftReport:
    desired_index = index_manifests(desired_manifests, ignore_kinds)
    actual_index = index_manifests(actual_manifests, ignore_kinds)

    desired_keys = set(desired_index)
    actual_keys = set(actual_index)

    missing_keys = desired_keys - actual_keys
    extra_keys = actual_keys - desired_keys
    shared_keys = desired_keys & actual_keys

    report = DriftReport()
    for key in sorted(missing_keys):
        report.missing.append(desired_index[key])
    for key in sorted(extra_keys):
        report.extra.append(actual_index[key])

    for key in sorted(shared_keys):
        desired_manifest = sanitize_manifest(desired_index[key].manifest)
        actual_manifest = sanitize_manifest(actual_index[key].manifest)
        if desired_manifest != actual_manifest:
            diff = render_diff(desired_manifest, actual_manifest)
            report.changed.append(
                ChangedResource(
                    key=key,
                    diff=diff,
                    desired_source=desired_index[key].source,
                    actual_source=actual_index[key].source,
                )
            )
    return report
