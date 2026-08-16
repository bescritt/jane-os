#!/usr/bin/env python3
"""
Image generation core — Phase 1 scaffold.

Provides a minimal entry point for diffusion-based image synthesis
through local models (e.g. llama.cpp + GGUF).

Full implementation deferred to a subsequent iteration.
"""
import sys
import os
import json
import hashlib
from datetime import datetime, timezone

CONFIG_PATH = os.path.expanduser("~/.jane/image-generation-core.json")
DEFAULT_CONFIG = {
    "model": "placeholder",
    "output_dir": os.path.expanduser("~/.jane/images"),
    "max_width": 512,
    "max_height": 512,
}


def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg.update(json.load(f))
    return cfg


def generate_image(prompt, output_path=None, cfg=None):
    """
    Generate an image from a text prompt.

    Full implementation: loads GGUF model via llama.cpp, runs inference,
    saves PNG/WebP to output_path with provenance metadata.

    Phase 1 scaffold: validates inputs, creates output dir, writes a
    provenance placeholder.
    """
    if cfg is None:
        cfg = load_config()

    out_dir = cfg.get("output_dir", "~/.jane/images")
    out_dir = os.path.expanduser(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    if output_path is None:
        slug = hashlib.sha256(prompt.encode()).hexdigest()[:12]
        output_path = os.path.join(out_dir, f"gen-{slug}.png")

    # Scaffold: write a provenance metadata file alongside a placeholder
    meta_path = output_path + ".meta.json"
    metadata = {
        "prompt": prompt,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": cfg.get("model", "placeholder"),
        "status": "scaffold — not yet generated",
        "width": cfg.get("max_width", 512),
        "height": cfg.get("max_height", 512),
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Image generation scaffold — prompt: {prompt}")
    print(f"  output: {output_path}")
    print(f"  metadata: {meta_path}")
    print("  Status: Phase 1 scaffold — full generation deferred to subsequent iteration.")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Image generation core scaffold (Phase 1 — stub)"
    )
    parser.add_argument("prompt", nargs="?", help="Text prompt for image generation")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--config", "-c", help="Config file path (overrides default)")
    args = parser.parse_args()

    cfg = load_config()
    if args.config and os.path.isfile(args.config):
        with open(args.config) as f:
            cfg.update(json.load(f))

    if args.prompt:
        generate_image(args.prompt, args.output, cfg)
    else:
        print("Image generation core — Phase 1 scaffold.")
        print("Install: python3 src/cli.py install image-generation-core")
        print("Usage:  python3 modules/image-generation-core/scripts/main.py <prompt> [--output <path>]")
        print(f"Config: {CONFIG_PATH}")
        print("Status: scaffold — full generation logic deferred to subsequent iteration.")


if __name__ == "__main__":
    main()
