#!/usr/bin/env python3
"""
Module marketplace package + search engine for Jane OS Phase 4.

Provides:
  - Manifest validation (required fields)
  - Module packaging (.tar.gz with SHA256 content hash)
  - Local registry (JSON index at ~/.jane/registry/)
  - Search by name / tag / description

Usage:
  publish <module-name>   Validate + package + register a module
  search <query>          Search the local registry
  list                    List all registered modules

CLI integration: invoked via `python3 src/cli.py publish|search <args>`
Direct usage:     python3 modules/module-marketplace/scripts/package.py publish obsidian-adapter
"""
import sys
import os
import json
import hashlib
import tarfile
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────────

JANE_ROOT = Path(__file__).resolve().parents[3]  # repo root (file is 3 dirs deep: modules/module-marketplace/scripts/)
REGISTRY_DIR = Path(os.path.expanduser("~/.jane/registry"))
REGISTRY_INDEX = REGISTRY_DIR / "index.json"
MODULES_DIR = JANE_ROOT / "modules"
PACKAGES_DIR = REGISTRY_DIR / "packages"

# ── Manifest validation (P4-1.3) ────────────────────────────────────────────

REQUIRED_FIELDS = ["name", "extends", "dependencies", "permissions"]


def validate_manifest(manifest_path):
    """Validate a module's manifest.json. Returns (is_valid, errors)."""
    errors = []

    if not os.path.isfile(manifest_path):
        return False, ["manifest.json not found"]

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: '{field}'")

    # Validate types
    if "dependencies" in manifest and not isinstance(manifest["dependencies"], list):
        errors.append("'dependencies' must be a list")
    if "permissions" in manifest and not isinstance(manifest["permissions"], list):
        errors.append("'permissions' must be a list")
    if "name" in manifest and not isinstance(manifest["name"], str):
        errors.append("'name' must be a string")

    is_valid = len(errors) == 0
    return is_valid, errors


def extract_tags(manifest):
    """Extract searchable tags from manifest (name, phase from extends, etc.)."""
    tags = []
    name = manifest.get("name", "")
    if name:
        tags.append(name)

    # Extract phase from 'extends' field (e.g. "Phase 1" → "phase1")
    extends = manifest.get("extends", "")
    import re
    phase_match = re.search(r"Phase (\d+)", extends)
    if phase_match:
        tags.append(f"phase{int(phase_match.group(1))}")

    # Extract type hints from extends
    if "adapter" in extends.lower():
        tags.append("adapter")
    if "export" in extends.lower():
        tags.append("export")
    if "scheduler" in extends.lower():
        tags.append("scheduler")
    if "marketplace" in extends.lower():
        tags.append("marketplace")
    if "export" in extends.lower() and "chat" in extends.lower():
        tags.append("chat-export")

    return tags


# ── Content hashing (Tenet 9) ───────────────────────────────────────────────

def compute_content_hash(module_dir):
    """Compute SHA256 hash of all files in a module directory (Tenet 9)."""
    h = hashlib.sha256()
    for root, dirs, files in sorted(os.walk(module_dir)):
        dirs.sort()
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, module_dir)
            h.update(relpath.encode())
            h.update(b"\x00")
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            h.update(b"\x00")
    return h.hexdigest()


# ── Packaging (P4-1.3) ──────────────────────────────────────────────────────

def package_module(module_name):
    """Validate, hash, and package a module into .tar.gz. Returns package info."""
    module_dir = MODULES_DIR / module_name

    if not module_dir.is_dir():
        return None, f"Module '{module_name}' not found in {MODULES_DIR}"

    manifest_path = module_dir / "manifest.json"
    is_valid, errors = validate_manifest(manifest_path)

    if not is_valid:
        return None, "Manifest validation failed: " + "; ".join(errors)

    with open(manifest_path) as f:
        manifest = json.load(f)

    sha256 = compute_content_hash(str(module_dir))
    tags = extract_tags(manifest)

    # Build .tar.gz package
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    package_filename = f"{module_name}-{sha256[:8]}.tar.gz"
    package_path = PACKAGES_DIR / package_filename

    with tarfile.open(package_path, "w:gz") as tar:
        tar.add(str(module_dir), arcname=module_name)

    package_size = package_path.stat().st_size

    info = {
        "name": module_name,
        "version": "1.0.0",
        "sha256": sha256,
        "package_file": package_filename,
        "package_size_bytes": package_size,
        "tags": tags,
        "description": manifest.get("description", ""),
        "published_at": datetime.now(timezone.utc).isoformat(),
        "manifest": manifest,
    }

    return info, None


# ── Local registry (P4-1.4) ─────────────────────────────────────────────────

def load_registry():
    """Load the local registry index."""
    if not REGISTRY_INDEX.exists():
        return {"modules": [], "last_updated": None}
    try:
        with open(REGISTRY_INDEX) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"modules": [], "last_updated": None}


def save_registry(registry):
    """Save the local registry index."""
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    registry["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(REGISTRY_INDEX, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def register_module(info):
    """Add a packaged module to the local registry."""
    registry = load_registry()

    # Check if already registered (by name + sha256)
    existing = None
    for m in registry["modules"]:
        if m["name"] == info["name"] and m["sha256"] == info["sha256"]:
            existing = m
            break
        # Update if same name (new version)
        if m["name"] == info["name"]:
            registry["modules"].remove(m)
            break

    registry["modules"].append(info)
    save_registry(registry)
    return info


def search_registry(query):
    """Search the local registry by name, tag, or description."""
    registry = load_registry()
    query_lower = query.lower()

    results = []
    for m in registry["modules"]:
        # Search in name, tags, and description
        searchable = " ".join([
            m.get("name", ""),
            " ".join(m.get("tags", [])),
            m.get("description", "")
        ]).lower()

        if query_lower in searchable:
            results.append(m)

    return results


# ── CLI ─────────────────────────────────────────────────────────────────────

def do_publish(module_name):
    """Publish a module: validate, package, register."""
    info, error = package_module(module_name)
    if error:
        print(f"ERROR: {error}")
        return False

    register_module(info)
    print(f"Published '{module_name}':")
    print(f"  sha256: {info['sha256']}")
    print(f"  package: {info['package_file']} ({info['package_size_bytes']} bytes)")
    print(f"  tags: {', '.join(info['tags'])}")
    print(f"  registry: {REGISTRY_INDEX}")
    return True


def do_search(query):
    """Search the local registry."""
    results = search_registry(query)

    if not results:
        print(f"No modules found matching '{query}' in registry.")
        print(f"Registry: {REGISTRY_INDEX}")
        return True

    print(f"Found {len(results)} module(s) matching '{query}':")
    print()

    for m in results:
        tags = m.get("tags", [])
        if tags is None:
            tags = []
        print(f"  {m.get('name', '?')} v{m.get('version', '1.0.0')}")
        print(f"    sha256: {m.get('sha256', '')[:16]}...")
        print(f"    tags: {', '.join(tags)}")
        print(f"    desc: {m.get('description', '')[:100]}")
        print()

    return True


def do_list():
    """List all registered modules."""
    registry = load_registry()
    modules = registry.get("modules", [])

    if not modules:
        print("Registry is empty. Publish modules with: cli.py publish <module-name>")
        print(f"Registry: {REGISTRY_INDEX}")
        return

    print(f"Local registry ({len(modules)} modules):")
    print(f"Location: {REGISTRY_INDEX}")
    print()

    for m in modules:
        print(f"  {m['name']} v{m.get('version', '1.0.0')}")
        print(f"    sha256: {m['sha256'][:16]}...")
        print(f"    tags: {', '.join(m.get('tags', []))}")
        print(f"    published: {m.get('published_at', 'unknown')}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: package.py <publish|search|list> [args]")
        print("  publish <module-name>   Validate + package + register a module")
        print("  search <query>          Search the local registry")
        print("  list                    List all registered modules")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "publish":
        if len(sys.argv) < 3:
            print("ERROR: publish requires a module name")
            print("Usage: package.py publish <module-name>")
            sys.exit(1)
        success = do_publish(sys.argv[2])
        sys.exit(0 if success else 1)
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("ERROR: search requires a query")
            print("Usage: package.py search <query>")
            sys.exit(1)
        do_search(sys.argv[2])
    elif cmd == "list":
        do_list()
    else:
        print(f"ERROR: unknown command '{cmd}'")
        print("Available: publish, search, list")
        sys.exit(1)


if __name__ == "__main__":
    main()
