Contributing to Jane OS

Thank you for contributing! To contribute modules, fixes, or tests:

1. Fork the repository and create a feature branch named `feat/<short-desc>` or `fix/<short-desc>`.
2. Run the smoke test locally: `./tests/smoke_test.sh` and add/adjust tests in `tests/`.
3. Add a module under `modules/` with a `manifest.json` and implementation files.
4. Commit with a descriptive message and open a Pull Request against `beansbrannagan-redesigned-system`.
5. CI will run the smoke test and basic checks. If your change affects manifests, update `docs/manifest.md`.

If you need help, open an issue or contact the maintainers listed in IDEA.md.
