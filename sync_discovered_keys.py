#!/usr/bin/env python3
"""Sync discovered mappings into deobfuscated and legacy hash files.

Outputs machine-readable lines consumed by discover-version.sh:
- ADDED=<count>
- MOVED=<count>
- DEOBF_CHANGED=<0|1>
- LEGACY_CHANGED=<0|1>

Pass --legacy-only to add discovered names into deobfuscated_legacy.py for
hashes already listed in hashes_legacy.txt, without moving device keys.

On failure, prints:
- ERROR <message>
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


DISCOVER_FILE = Path("discover-obfuscated-mapped.txt")
HASHES_FILE = Path("hashes.txt")
LEGACY_FILE = Path("hashes_legacy.txt")
DEOBFUSCATED_FILE = Path("deobfuscated.py")
DEOBFUSCATED_LEGACY_FILE = Path("deobfuscated_legacy.py")


def read_set(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text().splitlines() if line.strip()}


def shell_sort(values: list[str], *, fold_case: bool = True, unique: bool = False) -> list[str]:
    if not values:
        return []

    args = ["sort"]
    if fold_case:
        args.append("-f")
    if unique:
        args.append("-u")

    payload = "".join(f"{value}\n" for value in values)
    result = subprocess.run(args, input=payload, text=True, capture_output=True, check=True)
    return [line for line in result.stdout.splitlines() if line]


def load_dict(path: Path, variable_name: str) -> dict[str, str]:
    module = ast.parse(path.read_text())

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == variable_name:
                value = ast.literal_eval(node.value)
                if not isinstance(value, dict):
                    raise ValueError(f"{variable_name} is not a dictionary")
                return {str(k): str(v) for k, v in value.items()}

    raise ValueError(f"{variable_name} dictionary not found in {path}")


def load_discovered(path: Path) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        hash_value, key_name = line.split(":", 1)
        hash_value = hash_value.strip()
        key_name = key_name.strip()
        if hash_value and key_name:
            mapped[hash_value] = key_name
    return mapped


def write_dict(path: Path, variable_name: str, values: dict[str, str]) -> bool:
    ordered_keys = shell_sort(list(values.keys()), fold_case=True, unique=True)

    output_lines = [f"{variable_name} = {{"]
    for hash_value in ordered_keys:
        key_name = values[hash_value]
        escaped_hash = hash_value.replace("\\", "\\\\").replace('"', '\\"')
        escaped_key = key_name.replace("\\", "\\\\").replace('"', '\\"')
        output_lines.append(f'    "{escaped_hash}": "{escaped_key}",')
    output_lines.append("}")
    new_content = "\n".join(output_lines) + "\n"

    old_content = path.read_text()
    changed = old_content != new_content
    if changed:
        path.write_text(new_content)

    return changed


def sync_legacy_only(mapped: dict[str, str], existing: dict[str, str], existing_legacy: dict[str, str], legacy_hashes: set[str]) -> int:
    """Add discovered names for legacy hashes without touching device mappings."""
    added = 0
    pending_additions: list[tuple[str, str]] = []
    for hash_value, key_name in mapped.items():
        if hash_value not in legacy_hashes:
            continue
        if hash_value in existing or hash_value in existing_legacy:
            continue
        pending_additions.append((hash_value, key_name))

    for hash_value, key_name in sorted(pending_additions, key=lambda item: item[0].lower()):
        existing_legacy[hash_value] = key_name
        added += 1

    deobf_legacy_changed = write_dict(DEOBFUSCATED_LEGACY_FILE, "keys_legacy", existing_legacy)
    print(f"ADDED={added}")
    print("MOVED=0")
    print(f"DEOBF_CHANGED={1 if deobf_legacy_changed else 0}")
    print("LEGACY_CHANGED=0")
    return 0


def main() -> int:
    try:
        legacy_only = "--legacy-only" in sys.argv

        if not DISCOVER_FILE.exists():
            raise FileNotFoundError(f"{DISCOVER_FILE} not found")
        if not DEOBFUSCATED_FILE.exists():
            raise FileNotFoundError(f"{DEOBFUSCATED_FILE} not found")
        if not DEOBFUSCATED_LEGACY_FILE.exists():
            raise FileNotFoundError(f"{DEOBFUSCATED_LEGACY_FILE} not found")

        hashes = read_set(HASHES_FILE)
        legacy_hashes = read_set(LEGACY_FILE)
        existing = load_dict(DEOBFUSCATED_FILE, "keys")
        existing_legacy = load_dict(DEOBFUSCATED_LEGACY_FILE, "keys_legacy")
        mapped = load_discovered(DISCOVER_FILE)

        if legacy_only:
            return sync_legacy_only(mapped, existing, existing_legacy, legacy_hashes)

        added = 0
        pending_additions: list[tuple[str, str]] = []
        for hash_value, key_name in mapped.items():
            if hash_value in existing:
                continue
            if hash_value in hashes:
                pending_additions.append((hash_value, key_name))

        for hash_value, key_name in sorted(pending_additions, key=lambda item: item[0].lower()):
            existing[hash_value] = key_name
            added += 1

        missing_known = {hash_value for hash_value in existing if hash_value not in hashes}
        moved_candidates_in_order = [
            hash_value for hash_value in list(existing.keys()) if hash_value in missing_known
        ]

        for hash_value in moved_candidates_in_order:
            key_name = existing.pop(hash_value, None)
            if key_name is not None and hash_value not in existing_legacy:
                existing_legacy[hash_value] = key_name

        legacy_before = len(legacy_hashes)
        legacy_hashes.update(missing_known)

        legacy_added = len(legacy_hashes) - legacy_before

        legacy_ordered = shell_sort(list(legacy_hashes), fold_case=True, unique=True)
        legacy_target_content = "".join(f"{value}\n" for value in legacy_ordered)
        legacy_current_content = LEGACY_FILE.read_text() if LEGACY_FILE.exists() else ""
        legacy_changed = legacy_current_content != legacy_target_content
        if legacy_changed:
            LEGACY_FILE.write_text(legacy_target_content)

        deobf_changed = write_dict(DEOBFUSCATED_FILE, "keys", existing)
        deobf_legacy_changed = write_dict(DEOBFUSCATED_LEGACY_FILE, "keys_legacy", existing_legacy)

        print(f"ADDED={added}")
        print(f"MOVED={legacy_added}")
        print(f"DEOBF_CHANGED={1 if deobf_changed or deobf_legacy_changed else 0}")
        print(f"LEGACY_CHANGED={1 if legacy_changed else 0}")
        return 0
    except Exception as exc:
        print(f"ERROR {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
