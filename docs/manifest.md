# Module manifest specification

This document describes the minimal manifest fields used by Jane OS modules.

Fields
- name: string — human-readable module name
- version: string — semantic version (e.g. 0.1.0)
- description: string — short description
- entry: string — relative path to the module's entrypoint (e.g. lib/index.py)
- author: string — author or organization
- license: string — license identifier (e.g. MIT)
- dependencies: object — map of dependency names to versions (optional)
- scripts: object — map of script names to commands (optional)
- permissions: array — list of required permissions or capabilities (optional)

Example
See modules/sample_module/manifest.json for a concrete example.

Notes
- Manifests are intentionally small in Phase 0: they declare metadata used by the installer and basic validation. Keep backward-compatible changes only.
