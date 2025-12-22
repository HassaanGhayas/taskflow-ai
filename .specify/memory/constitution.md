<!--
Sync Impact Report:
- Version change: 1.0.0 → 2.0.0
- Principles added/modified:
  * I-VII: Core Principles - PRESERVED
  * VIII. Security Standards - NEW
  * IX. Performance Standards - NEW
  * X. Error Handling & Observability - NEW
  * XI. Versioning & Compatibility - NEW
  * XII. Operational Standards - NEW
  * XIII. Code Quality & Verification - NEW
  * XIV. Dependency & Supply Chain Management - NEW
  * XV. Agent Boundaries & Authority - UPDATED (was AI Tooling Rules)
- New sections:
  * Security Standards (secret management, vulnerability scanning, auth, PII) - NEW
  * Performance Standards (response times, resource limits, scalability) - NEW
  * Error Handling & Observability (logging, error classification, health checks) - NEW
  * Versioning & Compatibility (semver, breaking changes, deprecation) - NEW
  * Operational Standards (deployment, rollbacks, monitoring) - NEW
  * Code Quality & Verification (coverage, reviews, static analysis) - NEW
  * Dependency & Supply Chain Management (pinning, licenses, lockfiles) - NEW
- Templates requiring updates:
  ✅ plan-template.md - Constitution Check section now validates security, performance, observability
  ✅ spec-template.md - Requirements now include security, performance, operational concerns
  ✅ tasks-template.md - Task phases include security hardening, observability, testing coverage
- Follow-up TODOs:
  * Define concrete security scanning tools and CI integration
  * Establish baseline performance benchmarks per phase
  * Configure observability stack (logging, metrics, tracing)
  * Set up dependency scanning and license compliance tooling
-->

# TaskFlow AI Constitution

## Core Principles

### I. Spec Supremacy (Non-Negotiable)

All work in this repository is governed by written specifications.
No code, configuration, infrastructure, or automation may be created, modified, or deleted unless it is explicitly required by an approved specification.

**Exceptions**:
- Security patches addressing HIGH or CRITICAL vulnerabilities
- Dependency updates required for security compliance
- Emergency bug fixes that prevent system operation (must be retroactively specified within 48 hours)

Specifications are the single source of truth.
If behavior is not specified, it does not exist.

**Approval Mechanism**: Specifications are approved via pull request merge to the `main` branch with at least one human review approval.

### II. Constitution → Spec → Plan → Tasks → Implementation

The development lifecycle is strictly ordered and must never be bypassed:

1. Constitution defines immutable laws
2. Specifications define *what* must exist
3. Plans define *how* specifications are realized
4. Tasks authorize execution
5. Implementation follows tasks exactly

Skipping or reordering steps is a violation of project law.

**Exception**: Emergency security patches may bypass this flow but must be documented retroactively within 48 hours.

### III. Agent-First Development

AI agents (Claude Code, MCP tools, sub-agents) are first-class contributors.

Agents:
- MUST obey specifications exactly
- MUST NOT invent features, APIs, or behaviors not explicitly specified
- MUST NOT refactor or optimize without explicit instruction in specifications
- MUST treat ambiguity as a request for clarification, not permission to proceed
- MAY suggest improvements but MUST NOT implement without approval

Human contributors are held to the same standards.

### IV. Test-First Execution (Mandatory)

All functional behavior MUST be validated by tests.

Rules:
- Tests are derived directly from specifications
- For new features: tests MUST fail before implementation begins (red-green-refactor)
- For bug fixes: tests MUST reproduce the bug, then pass after fix
- For refactoring: existing tests MUST pass throughout
- Passing tests define completion, not visual inspection

Code that cannot be tested cannot exist.

**Minimum Coverage**: 80% for core logic (enforced in CI).

### V. Controlled Evolution Across Phases

The project evolves across phases:

- Console
- Web
- AI Agent
- Kubernetes
- Event-Driven Cloud System

Evolution is additive and traceable.
Earlier phase functionality MUST NOT be broken unless explicitly deprecated in specifications.

**Deprecation Process**:
- Deprecated features MUST be documented in specifications
- Deprecation MUST include migration path
- Deprecated features MUST remain functional for at least one MINOR release

Phases change *capabilities*, not *laws*.

### VI. Determinism Over Convenience

Systems MUST behave predictably.

- Explicit inputs produce explicit outputs
- Side effects MUST be intentional and observable
- Hidden behavior, magic defaults, and implicit state are forbidden
- All configuration MUST be explicit (no environment-dependent implicit behavior)

**Measurement**: All system behavior must be reproducible from version-controlled configuration and inputs.

Debuggability is a feature.

### VII. Simplicity and Justified Complexity

The simplest valid solution is always preferred.

Complexity is allowed only when:
- Explicitly required by a specification
- Justified by measurable system constraints (performance, scale, security)
- Documented in architecture or design specs with rationale

**Complexity Metrics**:
- Prefer solutions with fewer dependencies (count)
- Prefer solutions with lower cyclomatic complexity (<10 per function)
- Prefer solutions with fewer abstractions (count layers)

YAGNI is enforced by default.

## Security Standards (Non-Negotiable)

### Secret Management

- No secrets may be committed to source control
- Secrets MUST be injected via environment variables or approved secret managers (e.g., AWS Secrets Manager, HashiCorp Vault)
- Any detected plaintext secret is a **blocking violation** that prevents merge

**Enforcement**: Pre-commit hooks and CI scans MUST detect secrets.

### Dependency Vulnerability Management

- All dependencies MUST be scanned for vulnerabilities
- Builds MUST fail on **HIGH or CRITICAL** severity findings
- Exceptions are allowed **only** for:
  - Vulnerabilities actively mitigated at the application layer (documented in ADR)
  - Vulnerabilities with no available patch and documented risk acceptance

**Tools**: Dependency scanning MUST run in CI (e.g., `npm audit`, `pip-audit`, Snyk, Dependabot).

### Authentication & Authorization

- All user-facing or network-exposed services MUST enforce authentication
- Authorization checks MUST be explicit and test-covered
- Implicit trust between services is forbidden (zero-trust architecture)

**Verification**: Every protected endpoint MUST have a test verifying authentication and authorization.

### Data Privacy & PII

- PII MUST NEVER appear in logs
- Stored PII MUST be minimal, justified in specifications, and documented
- Access to sensitive data MUST be auditable (logged with user/time/action)

**Definition of PII**: Email addresses, names, phone numbers, IP addresses, payment information, or any data subject to GDPR/CCPA.

## Performance Standards

### Response Time Targets

- CLI operations: p95 < 200ms for standard commands
- API endpoints: p95 < 500ms unless otherwise specified in feature specifications
- Background jobs: MUST complete within specified timeouts

**Measurement**: Performance tests MUST be included in CI for critical paths.

### Resource Consumption

- Services MUST define CPU and memory limits in deployment configurations
- Unbounded resource usage (infinite loops, memory leaks, unbounded queues) is forbidden

**Enforcement**: Load testing MUST validate resource limits before production deployment.

### Scalability

- All services MUST be horizontally scalable unless explicitly exempted by specification
- Scalability assumptions (e.g., "supports up to 10K users") MUST be documented in specifications

**Verification**: Scalability limits MUST be tested and documented.

## Error Handling & Observability

### Logging

- Structured logging is mandatory (JSON format preferred)
- Logs MUST include:
  - Request IDs for correlation
  - Timestamps (ISO 8601)
  - Error codes and classifications
- Silent failures are forbidden (all errors MUST be logged)

**Enforcement**: Code reviews MUST verify logging for error paths.

### Error Handling

- Errors MUST be classified:
  - **User Error**: Invalid input, validation failures (HTTP 4xx)
  - **System Error**: Application bugs, unhandled exceptions (HTTP 5xx)
  - **Dependency Error**: External service failures (HTTP 503)
- Recovery behavior MUST be explicit (retry, fallback, fail-fast)

**Testing**: Error scenarios MUST be tested.

### Observability

All services MUST expose:
- **Logs**: Structured, searchable, with retention policy
- **Metrics**: Request rates, error rates, latencies (RED method)
- **Health Checks**: `/health` and `/ready` endpoints

Missing observability is a production blocker.

**Standards**: OpenTelemetry or equivalent instrumentation preferred.

## Versioning & Compatibility

### Versioning Strategy

- APIs MUST follow semantic versioning: `MAJOR.MINOR.PATCH`
- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward-compatible additions)
- **PATCH**: Bug fixes (backward-compatible fixes)

### Breaking Changes

Breaking changes require:
- Specification update documenting the change
- Explicit migration plan in documentation
- Deprecation notice for at least one MINOR release (unless security-critical)

**Definition of Breaking Change**: Any change that requires clients to modify code to maintain functionality.

### Deprecation

- Deprecated features MUST remain supported for at least one MINOR release unless security-critical
- Deprecation MUST include:
  - Clear notice in release notes
  - Migration guide
  - Timeline for removal

## Operational Standards

### Deployment

- All deployments MUST be reproducible from version-controlled artifacts (infrastructure as code)
- Manual production changes are forbidden
- Deployment configurations MUST be tested in staging before production

**Tools**: CI/CD pipelines MUST automate deployments.

### Rollbacks

- Rollback criteria MUST be defined per service (e.g., error rate > 5%, latency > 2s)
- Rollbacks MUST be executable without code changes (configuration or version revert)

**Testing**: Rollback procedures MUST be tested in staging.

### Monitoring & Alerts

- Services MUST define SLOs (Service Level Objectives):
  - Availability (e.g., 99.9% uptime)
  - Latency (e.g., p95 < 500ms)
  - Error rate (e.g., < 1% of requests)
- Alerting MUST exist for SLO violations with clear on-call ownership

**Escalation**: Alerts MUST route to responsible teams.

## Code Quality & Verification

### Test Coverage

- Minimum coverage: **80%** for core logic
- Coverage thresholds are enforced in CI
- Exceptions require explicit justification in specifications

**Tools**: Coverage reports MUST be generated and reviewed in PRs.

### Reviews

- All changes require review approval from at least one human reviewer
- Self-approval is forbidden
- Reviewers MUST verify:
  - Compliance with Constitution
  - Test coverage
  - Security implications

### Static Analysis

- Linting and static analysis MUST pass with zero blocking issues
- Warnings MAY be allowed with explicit justification

**Tools**: ESLint, Pylint, Clippy, or language-appropriate linters configured in CI.

## Dependency & Supply Chain Management

### Dependency Policies

- Dependencies MUST be version-pinned in lockfiles (package-lock.json, Cargo.lock, requirements.txt with hashes)
- Libraries below v1.0 or with <100 GitHub stars require explicit approval documented in specifications or ADRs

**Rationale**: Reduce supply chain risk and ensure reproducible builds.

### License Compliance

- All dependencies MUST use compatible licenses (MIT, Apache 2.0, BSD)
- License violations block merges
- GPL/AGPL dependencies require explicit legal review

**Tools**: License scanning MUST run in CI (e.g., FOSSA, licensee).

### Supply Chain Security

- Lockfiles are mandatory for all dependency managers
- Dependency checksums MUST be verified during installation
- Transitive dependencies MUST be scanned for vulnerabilities

**Enforcement**: CI MUST fail on lockfile inconsistencies or checksum mismatches.

## Development Constraints

### Specification Requirements

- All specifications MUST exist before implementation
- Specifications MUST be unambiguous, testable, and scoped
- Changes to behavior require specification updates first

**Testability**: Every requirement MUST be verifiable through automated tests or documented manual procedures.

Outdated specifications are defects.

### Technology Constraints

- Technology choices MUST be justified in specifications or ADRs
- Experimental libraries (below v1.0 or <100 stars) require explicit approval
- Infrastructure is treated as code and MUST be specified

**Definition of Experimental**: Libraries without stable release (v1.0+) or with limited adoption (<100 stars, <10K downloads/month).

Tooling MUST serve the specification, never the reverse.

### Agent Boundaries & Authority

AI agents MAY:
- **Suggest** specification changes, improvements, or optimizations
- **Draft** documentation, tests, or implementation code
- **Analyze** code for issues, security vulnerabilities, or performance bottlenecks

AI agents MUST NOT:
- **Autonomously modify** specifications or the Constitution in production
- **Implement** features not explicitly specified
- **Approve** their own changes (human review required)

**Approval Mechanism**:
- Specifications and Constitution changes require:
  - Pull request with human review
  - Version increment
  - Amendment note in commit message

Human contributors override agent decisions.

## Development Workflow

### Task Authorization

- Every implementation MUST map to a task in `tasks.md`
- Tasks MUST reference the governing specification
- Completing a task means:
  - Specification requirements met
  - Tests pass (including new tests for new features)
  - Code review approved
  - No Constitution violations

Untracked work is invalid work.

### Review & Quality Gates

Before acceptance:
- Specifications MUST exist and be approved
- All tests MUST pass (unit, integration, contract)
- No Constitution or specification violations MAY exist
- Security scans MUST pass (no HIGH/CRITICAL findings)
- Coverage thresholds MUST be met (80%+ for core logic)

Code quality is secondary to correctness, but both are required.

### Documentation Discipline

- Architecture changes require ADR (Architecture Decision Record) creation
- Behavior changes require specification updates
- Historical context MUST be preserved in version control and ADRs

**ADR Creation**: Use `/sp.adr` command for significant architectural decisions.

Documentation is part of the system.

## Governance

This Constitution supersedes all other documents, tools, agents, and conventions.

Violations MUST be corrected immediately.

Amendments require:
- Written rationale (why the change is needed)
- Version increment (MAJOR for breaking changes, MINOR for additions, PATCH for clarifications)
- Clear effective phase (which project phase this applies to)
- Migration plan if behavior changes require code updates

No silent changes are permitted.

All PRs and reviews MUST verify compliance with this Constitution.
Complexity MUST be justified in specifications.
Use CLAUDE.md for runtime development guidance and agent instructions.

**Version**: 2.0.0 | **Ratified**: 2025-12-21 | **Last Amended**: 2025-12-23
