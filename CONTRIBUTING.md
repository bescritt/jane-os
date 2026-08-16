# Contributing to Jane OS

Thank you for your interest in contributing to Jane OS! This document outlines
the process for submitting changes.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Module Development](#module-development)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct
This project follows the Hermes Agent community standards. Treat others with respect, be constructive, and assume good faith in all interactions.

## Getting Started
Jane OS is a lightweight overlay for Hermes Agent. To start:

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/jane-os.git
   cd jane-os
   ```
3. Run the smoke test to verify your environment:
   ```bash
   bash tests/smoke_test.sh
   ```

## Development Workflow
1. Create a branch for your feature or bugfix:
   ```bash
   git checkout -b feature/my-feature
   ```
2. Make your changes
3. Run tests (see [Testing](#testing))
4. Commit your changes with a clear message
5. Push to your fork and open a pull request

## Module Development
Jane OS is modular. See `IDEA.md` for the roadmap and `modules/sample_module/`
for the manifest format.

Each module must declare:
- `name` — module identifier
- `extends` — which Hermes capability it provides
- `dependencies` — external requirements
- `permissions` — what access the module needs
- `install` / `uninstall` — how to install/remove
- `description` — human-readable summary

## Testing
All changes must pass the smoke test before merging:
```bash
bash tests/smoke_test.sh
```

## Pull Request Process
1. Ensure tests pass
2. Use the PR template — fill out the description and checklist
3. Request review from a maintainer
4. Address review feedback
5. Once CI runs green and you have approval, a maintainer merges

## Questions?
Open an issue if you have questions, concerns, or proposals.
