# GitHub Copilot & Codex Configuration Guide for Trading Bot Swarm

## Purpose and Scope
- Establish a single source of truth for configuring GitHub Copilot and Codex within the Trading Bot Swarm ecosystem.
- Treat Copilot as a disciplined pair programmer that follows strict behavior rules, supports reviewers, and never bypasses security or quality gates.
- Cover end-to-end guidance: local setup, behavioral instructions, CI/CD integration, testing and linting expectations, observability, security defaults, contributor workflow, and maintenance.

## Configuration Overview
1. **Testing & Linting**
   - Always run unit tests and linters for code changes; documentation-only changes can skip automated checks.
   - Prefer `pytest` with coverage reporting and fail builds on coverage regressions.
   - Enforce linting via `ruff` or `flake8` and type checks with `mypy` (or `pyright` for TypeScript modules).
2. **Code Style**
   - Use `ruff format` or `black` for Python; consistent import sorting via `ruff` or `isort`.
   - Maintain pure functions where possible; keep side effects explicit and minimized.
   - Enforce docstrings for public functions, clear naming, and avoid unused parameters/imports.
3. **Async Patterns**
   - Prefer `asyncio` with `async`/`await`; avoid blocking calls inside async flows.
   - Use `anyio`-compatible primitives when integrating across frameworks.
   - Apply timeouts, cancellation handling, and structured logging for async tasks.
4. **Security Defaults**
   - Never hardcode secrets; source from vault/`secrets` context; mask secrets in logs.
   - Validate inputs, sanitize file paths, and enforce least privilege on tokens and IAM roles.
   - Require dependency pinning and regular security scans (SAST/DAST/dependency checks).
5. **Logging & Observability**
   - Standardize on structured logging (`json` where possible) with correlation IDs.
   - Emit metrics for latency, error rates, retries, and cache hits; expose health/readiness endpoints.
   - Use OpenTelemetry where available for tracing async pipelines and external calls.
6. **CI/CD Integration**
   - Quality gates: lint + type check + tests + coverage + security scans before merge.
   - Require green checks for protected branches; enforce code owners for sensitive directories.
   - Use preview environments for feature branches when touching user-facing services.
7. **Version Control**
   - Conventional commits; semantic release tags (e.g., `v1.2.3`).
   - Short-lived feature branches with frequent rebases; avoid long-lived forks.

## Custom Instruction Behavior (Copilot & Codex)
- Position Copilot as a rule-following assistant that proposes minimal, safe diffs and cites files/lines when summarizing changes.
- Require suggestions to include test/lint commands to run when code changes occur; explicitly state that documentation-only changes skip tests.
- Encourage incremental commits with clear scopes and meaningful messages.

### Example Behavior Rules
- Keep changes small; prefer refactors that reduce cognitive load.
- Never generate credentials or disable security checks.
- Default to immutable data where possible; isolate side effects.
- Prefer dependency-free solutions unless a library is standard or already in the repo.

### Conceptual Custom Instructions (YAML)
```yaml
copilot:
  persona: "Disciplined pair programmer for Trading Bot Swarm"
  priorities:
    - enforce_security_defaults
    - preserve_code_quality
    - minimize_diff_surface
  responses:
    include:
      - rationale_for_changes
      - tests_to_run_when_code_changes
    exclude:
      - speculative_architecture_changes_without_issue
  behaviors:
    - avoid_generating_secrets_or_tokens
    - propose_retry_and_timeout_defaults_for_async_calls
    - suggest_logging_with_context_ids
    - skip_tests_only_when_change_is_docs_only
codex:
  persona: "Policy-aware automation engine"
  execution_rules:
    - require_lint_and_test_before_commit
    - allow_docs_changes_without_tests
    - block_merges_if_security_scan_fails
  formatting:
    - prefer_black_and_ruff
    - enforce_type_hints
```

## GitHub Workflow: Lint & Test Automation
- **Triggers**: `pull_request` (opened, synchronize, reopened) and `push` on `main`/release branches; skip when only docs change (`paths-ignore: ['**/*.md', 'docs/**']`).
- **Quality Gate Job** steps:
  1. Checkout with full history for semantic versioning.
  2. Set up Python with cached dependencies.
  3. Install project and dev deps (`pip install -e .[dev]`).
  4. Run linters (`ruff`, `mypy`), then tests with coverage (`pytest --cov`).
  5. Upload coverage artifact and (optionally) send to coverage service.
  6. Upload lint/test artifacts on failure for debugging.

### Example Workflow (lint + test)
```yaml
name: lint-and-test
on:
  push:
    branches: [main, release/*]
    paths-ignore: ['**/*.md', 'docs/**']
  pull_request:
    types: [opened, synchronize, reopened]
    paths-ignore: ['**/*.md', 'docs/**']
jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install deps
        run: pip install -e .[dev]
      - name: Lint
        run: ruff check . && mypy .
      - name: Test
        run: pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-xml
          path: coverage.xml
```

## Semantic Release & Version Tagging
- Use semantic versioning (`major.minor.patch`) driven by conventional commits.
- Automate release notes and tagging via `semantic-release` or `release-please` after quality gates pass.
- Protect main branch; releases only from main after green pipeline.

### Example Workflow (semantic release)
```yaml
name: semantic-release
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install release tooling
        run: pip install python-semantic-release
      - name: Run release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: semantic-release publish
```

## Security & Dependency Scanning
- Run SAST (CodeQL), dependency scanning, and secret scanning on a schedule and for PRs.
- Block merges on findings until triaged.

### Example Workflow (security scans)
```yaml
name: security-and-deps
on:
  schedule:
    - cron: '0 6 * * 1'
  pull_request:
    paths-ignore: ['**/*.md', 'docs/**']
jobs:
  codeql:
    uses: github/codeql-action/.github/workflows/codeql.yml@v3
  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install -e .[dev]
      - name: Dependency audit
        run: pip-audit
```

## Contributor Guidelines
- Open an issue or discussion describing the change; link to relevant trading bot components.
- Follow coding standards in this guide; keep PRs focused and well-scoped.
- Provide: rationale, before/after behavior, tests run, and risk notes (security, perf, backwards compatibility).
- Review criteria: clarity, safety (no secrets, secure defaults), performance impact, observability, and test/lint coverage.
- Validation: reviewers verify CI results, run targeted tests locally if needed, and confirm logging/metrics for new paths.

## Troubleshooting & Optimization
- **Flaky tests**: add retries with backoff in async code; inspect logs/artifacts from CI; quarantine only with issue link.
- **Slow pipelines**: cache virtualenv/`pip`; parallelize lint/test; run selective tests via `pytest -k` when iterating locally.
- **Mypy/ruff noise**: align config files with project conventions; add precise type hints rather than ignores.
- **Coverage gaps**: add focused tests for edge cases (timeouts, retries, error paths) before enabling stricter thresholds.

## Maintenance Schedule
- Review this guide quarterly and after major architecture, security, or tooling changes.
- Keep workflow versions current (actions, python versions, scanners) and deprecate unsupported practices promptly.

## Closing Note
Standardize excellence to strengthen reliability, performance, and safety across the trading ecosystem. This guide aligns Copilot and Codex to reinforce disciplined engineering habits and trustworthy automation.
