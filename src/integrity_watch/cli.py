import argparse
import json
import sys
from pathlib import Path

from integrity_watch.monitor import build_manifest, compare_manifests, load_manifest, save_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="integrity-watch", description="Create or compare a local file hash baseline.")
    commands = parser.add_subparsers(dest="command", required=True)
    baseline_command = commands.add_parser("baseline", help="create a SHA-256 baseline")
    baseline_command.add_argument("directory", type=Path)
    baseline_command.add_argument("--output", type=Path, required=True)
    scan_command = commands.add_parser("scan", help="compare a scan with a saved baseline")
    scan_command.add_argument("directory", type=Path)
    scan_command.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "baseline":
            manifest = build_manifest(args.directory)
            save_manifest(manifest, args.output)
            print(f"Saved {len(manifest)} file hashes to {args.output}")
            return 0

        baseline = load_manifest(args.baseline)
        changes = compare_manifests(baseline, build_manifest(args.directory))
        print(json.dumps(changes, indent=2))
        return 1 if any(changes.values()) else 0
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"integrity-watch: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
