from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .rules import RULES, validate_config


def _check_file(path: Path) -> bool:
    try:
        with path.open(encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR INPUT $: {path}: {error}")
        return False

    if not isinstance(config, dict):
        print(f"ERROR INPUT $: {path}: top level must be a JSON object.")
        return False

    issues = validate_config(config)
    print(f"CHECK {path}")
    for issue in issues:
        print(f"ERROR {issue.rule_id} {issue.path}: {issue.message}")
    if not issues:
        print(f"PASS {path}: no errors ({len(RULES)} checks)")
    else:
        print(f"FAIL {path}: {len(issues)} error(s)")
    return not issues


def _check_folder(folder: Path) -> bool:
    paths = sorted(folder.glob("*.json"))
    if not paths:
        print(f"ERROR INPUT $: no JSON files found in {folder}")
        return False
    results = [_check_file(path) for path in paths]
    passed = sum(results)
    print(f"SUMMARY {passed}/{len(paths)} files clean")
    return all(results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="campaign_check", description="Check campaign JSON before launch.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="check one file or every JSON file in a folder")
    check.add_argument("file", nargs="?", type=Path, help="campaign JSON file")
    check.add_argument("--all", dest="folder", type=Path, help="folder containing campaign JSON files")

    subparsers.add_parser("rules", help="list the checks")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "rules":
        for rule in RULES:
            print(f"{rule.rule_id}  {rule.name}: {rule.description}")
        return 0

    if bool(args.file) == bool(args.folder):
        print("ERROR: provide one file or use --all with one folder.")
        return 2
    return 0 if (_check_folder(args.folder) if args.folder else _check_file(args.file)) else 1

