import hashlib
import json
from pathlib import Path
from typing import Any

CHUNK_SIZE = 1024 * 1024


def build_manifest(root: Path) -> dict[str, str]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"scan path is not a directory: {root}")

    manifest = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        relative_path = path.relative_to(root).as_posix()
        digest = hashlib.sha256()
        with path.open("rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(CHUNK_SIZE), b""):
                digest.update(chunk)
        manifest[relative_path] = digest.hexdigest()
    return manifest


def save_manifest(manifest: dict[str, str], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_manifest(source: Path) -> dict[str, str]:
    value: Any = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or any(
        not isinstance(path, str)
        or not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
        for path, digest in value.items()
    ):
        raise ValueError("baseline must be a JSON object of relative paths to SHA-256 hex digests")
    return value


def compare_manifests(baseline: dict[str, str], current: dict[str, str]) -> dict[str, list[str]]:
    baseline_paths = set(baseline)
    current_paths = set(current)
    return {
        "added": sorted(current_paths - baseline_paths),
        "changed": sorted(path for path in baseline_paths & current_paths if baseline[path] != current[path]),
        "missing": sorted(baseline_paths - current_paths),
    }
