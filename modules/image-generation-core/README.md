# Image Generation Core Module

**Extends:** Hermes: image generation core module (Phase 1)
**Dependencies:** python3
**Permissions:** filesystem, network


Phase 1 module for Jane OS. Provides core image generation capabilities for
Hermes Agent using local diffusion models.

## Current Status
This is a **scaffold** — the manifest and directory structure are in place.
The actual generation logic will be implemented in subsequent iterations.

## Manifest Fields
- **name**: `image-generation-core`
- **extends**: Hermes image generation capability
- **dependencies**: `python3`
- **permissions**: `filesystem`, `network`
- **description**: Diffusion-based image synthesis support

## Usage
```bash
python3 src/cli.py install image-generation-core
python3 src/cli.py uninstall image-generation-core
```
