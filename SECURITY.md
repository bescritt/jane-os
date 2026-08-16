# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in Jane OS, please report it privately:

1. Email: `opensource@bescritt.com`
2. Include: description of the vulnerability, steps to reproduce, potential impact, and any suggested fixes

You can encrypt your message using our PGP key (available on request).

## What to Expect

- **Acknowledgment:** Within 3 business days
- **Status update:** Within 7 business days
- **Resolution timeline:** Depends on severity — critical issues prioritized

## Security Best Practices for Contributors

When contributing to Jane OS:

1. **Never commit secrets** (API keys, tokens, passwords) — use environment variables
2. **Validate all user input** — never trust data from external sources
3. **Use parameterized queries** — never concatenate strings into SQL
4. **Keep dependencies updated** — run `pip audit` or equivalent before submitting PRs
5. **Follow the principle of least privilege** — modules declare minimal permissions in their manifest

## Security Scanning

All PRs should pass the project's smoke test (`bash tests/smoke_test.sh`). Future CI enhancements will add automated secret scanning via the `osint/secret-hygiene` skill pattern.

## Disclosure Policy

When a vulnerability is fixed, we will:

1. Credit the reporter (with their permission)
2. Publish a security advisory
3. Update this policy if needed
