# GitHub Copilot and Codex Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
- Establish a consistent, secure, and high-quality experience when using GitHub Copilot and Codex as pair programmers for the Trading Bot Swarm.
- Define behavioral guardrails: assistants act as cautious collaborators who respect project standards, security defaults, and observability requirements.
- Cover setup, coding conventions, automation pipelines, and contributor expectations so every change remains testable, reviewable, and auditable.

## Configuration Overview
- **Testing & Linting**: Always add or update unit/integration tests for code changes; run the test suite and linters before pushing. Treat lint or test failures as blockers.
- **Code Style**: Follow Python type hints, clear docstrings, small composable functions, and avoid try/except around imports. Keep public APIs stable; prefer dependency injection over globals.
- **Async Patterns**: Use `async`/`await` only when IO-bound; avoid blocking calls in async paths. Ensure graceful cancellation and timeouts for external calls.
- **Security Defaults**: Principle of least privilege for credentials and secrets; prefer environment variables and secret stores. Validate and sanitize inputs; enforce rate limits and authentication on endpoints.
- **Logging & Observability**: Use structured logging with request/trace IDs. Emit metrics for latency, error rates, and throughput. Prefer OpenTelemetry-friendly instrumentation.
- **CI/CD Integration**: Every PR runs lint, test, and security scans. Block merges on failures; publish artifacts for reproducibility.
- **Version Control**: Small, focused commits with descriptive messages. Require reviews for behavioral or interface changes. Avoid committing generated files or secrets.

## Custom Instruction Behavior (Copilot & Codex)
- Treat assistants as **pair programmers with strict guardrails**: suggest tests first, refuse insecure patterns, and call out missing validations.
- Prefer minimal diffs that preserve readability and traceability.
- Decline to invent APIs; request clarification when requirements are ambiguous.

### Example Instruction Snippets
- **Rules**
  - Propose test updates with each code change; skip tests only for documentation-only edits.
  - Flag use of global state, silent exception handling, or unbounded loops.
  - Ensure new endpoints include auth, rate limiting, and structured logging.

- **Conceptual YAML for Full Instructions**
  ```yaml
  copilot:
    role: "pair programmer with safety guardrails"
    priorities:
      - propose tests and linters for every code change
      - enforce secure defaults (auth, rate limits, input validation)
      - keep diffs small, clear, and typed
    discouraged_patterns:
      - global mutable state without locks
      - broad except blocks or swallowing errors
      - blocking calls in async handlers
    ignore_if_only: ["docs"]
  codex:
    role: "review-focused assistant"
    actions:
      - surface code smells, missing tests, and perf risks
      - suggest observability hooks (logs, metrics, traces)
      - ensure CI/CD steps are updated when dependencies change
    quality_gates:
      run_tests: true
      run_linters: true
      skip_when_only_docs_change: true
  ```

## GitHub Workflow: Lint and Test Automation
- **Triggers**: `pull_request` and `push` on main branches; optional `workflow_dispatch` for manual runs.
- **Quality Gate Steps**:
  1. Check out code and set up Python with caching.
  2. Install dependencies with `poetry install --no-root`.
  3. Run `ruff` (or `flake8`) for linting.
  4. Run `pytest` with coverage output.
  5. Upload coverage and test artifacts.

```yaml
name: quality-gate
on:
  push:
    branches: ["main", "release/*"]
  pull_request:
    branches: ["main", "release/*"]
  workflow_dispatch: {}

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "poetry"
      - run: pip install poetry
      - run: poetry install --no-root
      - name: Lint
        run: poetry run ruff .
      - name: Test
        run: poetry run pytest --maxfail=1 --disable-warnings -q
      - name: Coverage artifact
        if: always()
        run: mkdir -p artifacts && cp ./.coverage artifacts/ || true
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: quality-artifacts
          path: artifacts
```

## Best Practices: Semantic Release & Version Tagging
- Use conventional commits to drive automated semantic versioning.
- Tag releases via CI after successful quality gates.
- Generate changelogs automatically and attach build artifacts.

```yaml
name: semantic-release
on:
  push:
    branches: ["main"]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm install -g semantic-release @semantic-release/changelog @semantic-release/git
      - run: semantic-release
```

## Security and Dependency Scanning
- Include daily/PR scans for vulnerabilities and license issues.
- Fail builds on high/critical CVEs; open tracking issues for medium/low.

```yaml
name: security-scan
on:
  schedule:
    - cron: "0 2 * * *"
  pull_request:
    branches: ["main", "release/*"]

jobs:
  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install pip-audit
      - name: Scan dependencies
        run: pip-audit -r requirements.txt || true
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: pip-audit.json
```

## Contributor Guidelines
- **Proposing Changes**: Open an issue with context, risks, and testing plan. Use small PRs with clear descriptions and checklists for lint/test/security.
- **Review Criteria**: Tests updated, observability added, security defaults enforced, performance impact assessed, and documentation aligned.
- **Validation Process**: CI must pass; reviewers confirm logs/metrics are meaningful; deployments must include rollout/rollback notes.

## Troubleshooting and Optimization
- If Copilot/Codex suggests outdated APIs, sync the workspace and re-run linters to surface real interfaces.
- For flaky tests, add deterministic fixtures and tighten timeouts.
- When CI is slow, enable dependency caching and parallelize lint/test jobs.
- For noisy logs, standardize log levels and ensure correlation IDs propagate across services.

## Maintenance Schedule
- **Quarterly**: Refresh Copilot/Codex instruction YAML, update lint/test tool versions, and revalidate CI workflows.
- **Before Releases**: Verify semantic-release configuration, tag naming, and changelog generation.
- **After Security Advisories**: Prioritize dependency patches and rerun full scans.

## Closing Note
Standardizing excellence in automation, testing, and security strengthens the reliability, performance, and safety of the Trading Bot Swarm ecosystem. Keep assistants aligned with these guardrails to ensure every change meets production-grade expectations.
