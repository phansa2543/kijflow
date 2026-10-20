# Phase 1 Implementation Plan

## Goal

Implement the minimum self-service SaaS Foundation required before the first Business Module.

Phase 1 should establish a Foundation that is:

- secure,
- correct,
- understandable,
- maintainable by one person,
- realistic for self-service SaaS usage,
- reproducible in development,
- continuously testable,
- and sufficiently deployment-ready to proceed confidently into the first Business Module.

Phase 1 must not become:

- a general-purpose SaaS platform,
- a multi-company ERP platform,
- an enterprise IAM system,
- or a production-scale DevOps project.

---


# Current Status

Milestone 1 — Project Bootstrap is complete.

Milestone 2 — Identity / Organization / Membership Foundation is complete.

Milestone 3 — Registration & Authentication is the current milestone.

The approved M3 implementation-level design has completed Tech Lead design, QA review, Engineering Mentor review, and Founder approval.

DEC-008 and DEC-009 remain accepted decisions.

## M3 Implementation Progress

### Verified M3 Progress — 2026-10-21

This current snapshot supersedes the dated 2026-10-18 implementation-status reports below. Historical local test counts and earlier pending-work statements are retained only as historical evidence.

- Registration HTTP API, runtime registration dependency wiring, public-safe error handling, atomic global User + PasswordCredential registration, password screening, Argon2id, and PostgreSQL-backed registration rate limiting are implemented.
- Registration counter cleanup, its separate manual runner, and Alembic index `990acb220a2c` are implemented. It does not run inside the Registration request path.
- Registration Counter Cleanup **B2 Implementation is CLOSED** following the independent QA final closure. Conditions C1 (24-hour retention measured from **window expiry**) and C2 (20-batch runner ceiling and warning) passed. The cleanup test module has **7 tests**.
- Verified source baseline: GitHub `main` commit `ff6bfa2d72a940c9596db1bab9b87771ada9b6c0`. GitHub Actions run https://github.com/phansa2543/kijflow/actions/runs/39455823132 passed with **205 passed, 1 skipped**.
- Cleanup implementation defaults: **24-hour retention after window expiry**, **500 rows per batch**, **20 batches per execution** (at most 10,000 rows). Cleanup uses PostgreSQL time and `FOR UPDATE SKIP LOCKED`. Uncaught runner errors propagate; reaching the batch limit warns but may exit with code 0 **while backlog remains**.
- Production scheduler, failure alerting, backlog/retention monitoring and database access verification remain **DEFERRED to a Pre-External-Use Gate** tracked under AQ-014. An **hourly external job** is a provisional future cadence, not deployed infrastructure. These items do not reopen B2 implementation or block internal M3 Login API.
- Next M3 implementation task: **Login API** under the existing accepted M3 design, followed by safe password-rehash database persistence, PostgreSQL-backed sessions, logout, login abuse/enumeration protection, cookies/CSRF, minimum browser authentication workflows and final security/integration QA. M3 remains **IN PROGRESS**.
- The separate independent Password Screening Technical Security/QA acceptance and third-party pre-external-release verification under AQ-016 are not implicitly closed by B2 QA.

As of 2026-10-18, Engineering Mentor reviewed the implementation against GitHub `main` at commit `b3e7ab4`.

**Implemented**

- Authentication credential and session persistence models, migrations, and persistence tests
- Email canonicalization and validation
- Password NFC normalization
- Password length validation (8–128 Unicode code points)
- Local common-password checker and dataset loader
- Password SHA-1 prefix/suffix helpers
- HIBP Range API client and response parser
- HIBP error handling and fail-closed behavior
- Integrated Password Screening Pipeline (`backend/app/auth/screening.py`)
- Deterministic screening tests
- Separate opt-in live HIBP integration test (`backend/tests/test_hibp_live.py`)

**Verification**

- Local live HIBP integration test: 1 passed in 1.09s (Founder-reported).
- Local full backend regression: 131 passed, 1 skipped in 1.09s (Founder-reported).
- GitHub Actions CI: 131 passed, 1 skipped.
- Password Screening baseline CI commit: `b3e7ab4`.
- GitHub Actions run: https://github.com/phansa2543/kijflow/actions/runs/39093928975

The Engineering Mentor verified the committed source code and GitHub Actions result. The live HIBP execution result was reported by the Founder and was not independently executed by the Engineering Mentor.

Password Screening implementation and automated verification have progressed beyond the previous Step 7.25.1 status.

Independent Technical Security/QA review remains pending before formal Password Blocklist subtask closure.

Milestone 3 remains in progress.

### Argon2id Hashing & Verification — Local Implementation Progress

As of 2026-10-18, the Founder reports completion of the
Argon2id hashing and verification unit-level implementation.

Implemented:
- Argon2id v=19, memory_cost=19456 KiB, time_cost=2,
  parallelism=1.
- Password hashing with randomly generated salts.
- Password verification with safe handling of invalid hashes.
- Detection of outdated Argon2id parameters.
- Preparation of replacement hashes only after successful
  password verification.
- Best-effort handling of hashing failures during rehash.
- Unicode NFC interoperability when normalization is
  performed by the calling authentication layer.

Local verification (Founder-reported):
- Argon2id unit tests: 13 passed.
- Full backend regression: 144 passed, 1 skipped in 1.38s.
- Hash benchmark: 23.3 ms per operation.
- Verify benchmark: 25.0 ms per operation.
- Benchmark method: Python timeit, 20 loops, 3 repetitions,
  reporting the best repetition.
- Python environment: backend/.venv, Python 3.13.15.
- Dependency: argon2-cffi==25.1.0, pinned in requirements.txt.

Limitations:
- These are local development results, not production benchmarks.
- GitHub Actions CI: PASS.
- Verified commit: `e81107d`.
- GitHub Actions run: https://github.com/phansa2543/kijflow/actions/runs/39109587718
- Database persistence of replacement hashes has not been tested.
- Password Screening is integrated into the Registration service.
- Registration HTTP endpoint and runtime dependency wiring remain pending.
- Independent security review remains pending.

Next implementation task:
Review M3 Authentication module boundaries and dependencies
under DEC-011, including Tech Lead and QA review.

Refactor the existing Authentication implementation incrementally
before resuming Registration HTTP API integration.

### Atomic Registration — Service/Persistence Implementation

Status: Implemented and locally tested.

Implemented:
- Global User and PasswordCredential creation in one database transaction.
- Email canonicalization before password processing.
- Integration with the approved Password Screening Pipeline.
- Argon2id hashing before database persistence.
- Transaction ownership through `engine.begin()`.
- Automatic rollback when credential persistence fails.
- Database-enforced canonical email uniqueness.
- No Organization or Membership creation.

Local verification (Founder-reported):
- Registration tests: 9 passed.
- Full backend regression: 153 passed, 1 skipped.
- Concurrent duplicate registration: PASS.
- Production commit and rollback tests: PASS.
- Invalid email and HIBP unavailable failure tests: PASS.

Limitations:
- Registration HTTP endpoint is not yet implemented.
- Public-safe duplicate-email error mapping remains pending.
- Runtime screening dependency wiring remains pending.
- Registration abuse protection remains pending.
- GitHub Actions CI verification for this change is pending.
- Independent Security/QA review remains pending.

## Current Implementation Step

**Next: M3 Login API.** Registration Cleanup B2 Implementation received final QA **CLOSED**; C1/C2, the 7 cleanup tests and the exact-commit backend CI are verified. No further B2 QA round or production scheduler is required to begin internal Login implementation.

The Engineering Mentor should inspect the existing login/session-related code and approved M3 acceptance criteria, then guide the Founder through Login API implementation. Retain the approved security and architecture boundaries and do not introduce M4 Organization/Membership behavior or unrelated Production Infrastructure.

## Password Screening — Development Status and Release Gates

DEC-009 remains accepted, including the Founder Clarification dated 2026-10-17.

The Founder has explicitly approved continued internal development using the selected SecLists NCSC password dataset, including retaining the existing Git commit.

The dataset commit was intentional. Its existence alone is not a repository discrepancy and does not justify Git history rewriting or remediation.

Real HIBP Pwned Passwords Range API integration testing may proceed during internal development, subject to applicable published terms and reasonable operational limits.

Additional confirmation from the relevant dataset rights holders and HIBP regarding commercial SaaS usage is a pre-external-release requirement, not an automatic blocker for internal M3 development or technical completion.

Before any external-user access, including free beta or commercial launch:

- Confirm applicable dataset rights and attribution requirements.
- Clarify applicable HIBP commercial SaaS terms.
- Obtain owner/provider confirmation or guidance where required.
- Resolve any identified incompatible terms.

Known evidence of incompatible third-party terms must be escalated when discovered.

The current Password Screening verification status is:

- Integrated Password Screening Pipeline: implemented.
- Deterministic automated tests: implemented and passing.
- Separate live HIBP integration test: local PASS reported by the Founder.
- Normal GitHub Actions CI: PASS at commit `b3e7ab4`.
- Independent Technical Security/QA review: pending.

The Password Blocklist subtask must not be marked formally complete until the required independent Technical Security/QA review is recorded.

Password Screening is integrated into the Registration service before Argon2id hashing. Registration HTTP API integration and runtime dependency wiring remain pending.

The DEC-009 Founder Clarification and the pre-external-release requirements under AQ-016 remain unchanged.

## Phase 1 Functional Frontend Requirement

DEC-010 was accepted by the Founder on 2026-10-17 following Product/UX, Tech Lead, and QA review.

Phase 1 must deliver the minimum functional browser frontend connected to the real Next.js, FastAPI, and PostgreSQL-backed Kijflow application.

Approved customer-facing Foundation workflows must be operable without Swagger/Postman.

Frontend delivery and browser integration testing proceed incrementally through M3–M7.

M8 consolidates browser E2E, security, usability, and non-production deployment validation.

Backend security authority and all previously accepted Foundation invariants remain unchanged.

Milestone 3 remains the current implementation milestone.

Business Modules, Billing, and Marketing Site remain outside Phase 1.

---

# Scope

Phase 1 includes:

- Global Kijflow User Identity
- Organization
- Membership
- Self-service User registration
- Self-service Organization creation
- Authentication
- Trusted Organization context
- Minimum Membership lifecycle
- Invitation-based Membership onboarding
- Owner / Admin / Member Foundation authorization
- Organization ownership protection and transfer
- Minimal capability-oriented authorization
- Strong tenant/data isolation

Supporting implementation and delivery readiness includes:

- reproducible local development,
- database migrations,
- automated testing,
- minimal continuous integration,
- progressive security regression coverage,
- and at least one non-production deployment rehearsal before Phase 1 closure.

These delivery concerns support implementation of the accepted SaaS Foundation.

They do not expand product scope.

---

# Non-Goals

Phase 1 does not include:

- Billing / subscription / packaging implementation
- Payment-provider integration
- Business Modules
- Advanced permission builders
- Customer-defined roles
- Direct per-user permission overrides
- Complex approval hierarchies
- Enterprise SSO
- Teams / Departments without validated requirements
- Parent/subsidiary hierarchy
- Group-company hierarchy
- Consolidated multi-company reporting
- Shared inventory across Organizations
- Shared business data across Organizations
- Inter-company transactions
- Custom workflow engines
- Customer-offboarding export implementation
- Data-retention purge implementation
- Production-scale DevOps infrastructure
- Kubernetes
- Infrastructure-as-Code without validated need
- High-availability architecture
- Enterprise observability
- Automatic production deployment
- Final production cloud architecture unless justified by validated requirements

---

# Delivery Principle

Infrastructure and delivery readiness should evolve incrementally with the application.

Phase 1 should establish:

- reproducible development,
- continuous integration,
- reliable migration execution,
- security-focused automated testing,
- and basic deployment readiness,

without prematurely introducing production-scale operational complexity.

CI should become stronger as security and Foundation behavior are implemented.

Production deployment architecture and CD policy should be finalized when Kijflow approaches real customer use and sufficient operational requirements are known.

Technology providers such as GitHub Actions, cloud vendors, and deployment platforms are implementation choices rather than architectural requirements unless explicitly accepted later.

---

# Functional Frontend Delivery — DEC-010

Phase 1 must provide the minimum browser-operable interface for all approved customer-facing Foundation workflows through the real Next.js frontend, FastAPI backend, and PostgreSQL-backed state.

Frontend implementation proceeds incrementally with the milestone that introduces each Foundation workflow.

- M3: Registration, Login, Logout, authenticated pre-tenant state, and authentication error/recovery behavior.
- M4: Zero-Organization experience, Organization creation, discovery, selection, switching, current Organization visibility, and minimal application shell.
- M5: Safe tenant-context switching, stale-context recovery, and tenant-aware frontend state/cache isolation.
- M6: Authorization-aware actions, navigation, and Access Denied handling.
- M7: Invitation, Membership lifecycle, authorized profile management, Owner protection, and ownership transfer.
- M8: Consolidated real-backend Browser E2E, security, usability, non-production deployment validation, and defect closure.

Frontend must not establish independent authentication or authorization authority.

Browser-selected Organization identifiers are selection intent only. Trusted Organization context requires backend Membership validation.

Protected client state must not leak across Organization, User, session, Membership, or authorization-context changes.

Cookie-authenticated state-changing Foundation operations require CSRF protection appropriate to the approved security outcome.

Browser tests complement, not replace, backend/PostgreSQL security tests.

A milestone introducing a customer-facing Foundation workflow is not complete until the minimum browser integration for that workflow has been exercised against the real backend.

Exact routes, layouts, component architecture, cache library, API contracts, and deferred milestone implementation mechanisms are not decided by DEC-010.

Business Modules, Billing, Marketing Site, and speculative frontend infrastructure remain outside Phase 1.

# Implementation Milestones

## Milestone 1 — Project Bootstrap

### Status

Complete.

### Goal

Create the minimum runnable and reproducible development foundation required for Phase 1 implementation.

### Scope

#### Backend

- FastAPI application
- Clear application entry point
- Basic health endpoint
- PostgreSQL connectivity
- Migration foundation
- Backend test foundation

#### Frontend

- Next.js application
- Minimum runnable frontend foundation

No business UI is required.

#### Development Reproducibility

Establish enough repository-controlled configuration that development setup does not depend on configuration remembered only by the Founder.

This includes:

- Git repository
- dependency definitions
- environment-variable configuration
- secret hygiene
- `.env` development convention
- example environment configuration where appropriate
- PostgreSQL development environment
- Docker Compose for local PostgreSQL where appropriate
- documented startup and migration commands

Development reproducibility does not require a one-command development platform.

#### Minimal Continuous Integration

Establish minimal CI after the local test foundation works.

Initial responsibility:

```text
push / pull request
        ↓
setup application dependencies
        ↓
run migrations where required
        ↓
run automated tests
        ↓
pass / fail
```

CI is a development capability.

The specific CI provider is an implementation choice.

### Non-Goals

Milestone 1 does not include:

- User Identity model
- Organization model
- Membership model
- registration
- authentication
- authorization
- tenant isolation
- RLS policies
- Business Modules
- production deployment
- production CD
- production database architecture
- cloud-provider commitment
- Kubernetes
- Terraform
- monitoring platform
- backup architecture
- generic repository frameworks
- event buses
- microservices
- speculative abstractions

### Acceptance Criteria

Milestone 1 is complete when:

- backend runs,
- `GET /health` returns successfully,
- PostgreSQL connectivity works,
- migrations can be applied successfully,
- backend tests run successfully,
- frontend runs,
- development secrets are not committed,
- required local configuration is documented or repository-controlled,
- a clean development setup can be reproduced without undocumented configuration,
- minimal CI executes the available migrations/tests,
- CI reports clear pass/fail status.

### Relevant Decisions

- DEC-001

---

## Milestone 2 — Identity / Organization / Membership Foundation

### Status

Complete.

The Milestone 2 implementation-level technical design was reviewed and approved before implementation.

The approved persistence model has been implemented and validated.

Validation completed includes:

- clean migration from the Milestone 1 baseline to Milestone 2,
- downgrade from Milestone 2 to Milestone 1,
- re-upgrade to Milestone 2,
- PostgreSQL-backed persistence invariant tests,
- full backend test-suite validation,
- and successful CI execution of migrations and automated tests.

### Goal

Implement the minimum persistent Foundation model required by revised DEC-002 and DEC-003 without prematurely implementing workflows belonging to later milestones.

### Scope

Establish the minimum persistent representation for:

- global User Identity,
- Organization,
- Membership,
- Membership-specific Foundation profile:
  - Owner,
  - Admin,
  - Member,
- minimum Organization ownership representation,
- minimum Membership lifecycle state required by later Phase 1 security behavior.

The persistent model must support:

- one User having Memberships in multiple Organizations,
- one Organization having multiple Memberships,
- at most one Membership for a given User/Organization pair,
- independent Membership behavior across Organizations,
- Membership-specific authorization profile,
- exactly one Owner when an Organization is in its usable/active state,
- global User Identity existing independently from any specific Organization.

Schema changes must use the migration foundation established in Milestone 1.

### Approved M2 Implementation-Level Design

The Founder has approved the following implementation-level persistence design for Milestone 2.

#### Tables

Milestone 2 introduces only:

```text
users
organizations
memberships
```

No authentication, invitation, permission, configurable-role, active-Organization-context, or Business Module tables are introduced in Milestone 2.

#### Identifier Strategy

`User`, `Organization`, and `Membership` use PostgreSQL `UUID` primary keys.

UUID values are generated by the application using UUIDv4.

UUID identifiers are not security or authorization boundaries.

#### User Persistence

Minimum Milestone 2 representation:

```text
users
────────────────────────────
id               UUID PK NOT NULL
created_at       TIMESTAMPTZ NOT NULL
updated_at       TIMESTAMPTZ NOT NULL
```

User remains a global Kijflow Identity.

User does not contain:

- `organization_id`,
- globally persisted `active_organization_id`,
- authentication-specific fields that belong to Milestone 3.

#### Organization Persistence

Minimum Milestone 2 representation:

```text
organizations
────────────────────────────
id               UUID PK NOT NULL
name             TEXT NOT NULL
created_at       TIMESTAMPTZ NOT NULL
updated_at       TIMESTAMPTZ NOT NULL
```

Organization name:

- is required,
- must not be empty after trimming,
- is not globally unique.

Milestone 2 does not introduce Organization lifecycle status, ownership foreign keys, subscription data, or speculative settings fields.

#### Membership Persistence

Minimum Milestone 2 representation:

```text
memberships
────────────────────────────
id               UUID PK NOT NULL
user_id          UUID NOT NULL
organization_id  UUID NOT NULL
profile          TEXT NOT NULL
status           TEXT NOT NULL
created_at       TIMESTAMPTZ NOT NULL
updated_at       TIMESTAMPTZ NOT NULL
```

Membership profile values are:

```text
OWNER
ADMIN
MEMBER
```

Membership status values are:

```text
ACTIVE
DISABLED
REVOKED
```

Profile and status use `TEXT` plus database `CHECK` constraints.

They do not use PostgreSQL native ENUM types or lookup tables.

Profile and status have no implicit defaults. Creation code must select both values intentionally.

#### Membership Identity

The database enforces:

```text
UNIQUE(user_id, organization_id)
```

A Membership therefore represents one durable User–Organization relationship across its lifecycle.

For example:

```text
ACTIVE
→ DISABLED
→ ACTIVE
→ REVOKED
```

does not create a new Membership identity.

If future requirements require separate participation episodes, that history must be modeled deliberately rather than creating duplicate Membership rows under the current model.

#### Ownership Persistence Rules

The database enforces:

```text
OWNER ⇒ ACTIVE
```

and:

```text
Organization Owner count <= 1
```

through an appropriate database constraint/index.

Milestone 2 intentionally does not enforce that every raw Organization row always has an Owner.

A raw persistence state may therefore temporarily contain:

```text
Organization exists
Owner count = 0
```

However:

> Organization row existence does not by itself mean that the Organization is usable or operational.

A committed usable Organization must have exactly one active Owner.

Milestone 4 Organization bootstrap must establish Organization creation and initial Owner Membership as one atomic operation so that a successful normal bootstrap cannot commit a usable Organization without an Owner.

Ownership-transfer lifecycle and concurrency behavior remain the responsibility of Milestone 7.

#### Foreign-Key and Deletion Behavior

Membership references:

```text
memberships.user_id
→ users.id

memberships.organization_id
→ organizations.id
```

Deletion behavior is restrictive.

Deletion behavior uses ON DELETE RESTRICT for both Membership foreign keys.

Hard-delete lifecycle policy remains outside Milestone 2.

#### Indexes and Constraints

Milestone 2 includes:

- primary-key indexes,
- unique `(user_id, organization_id)`,
- an index on `memberships.organization_id`,
- a partial unique index enforcing at most one Owner per Organization,
- explicit names for important constraints and indexes.

Additional speculative indexes are not required.

#### Timestamp Behavior

All three entities use:

```text
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Initial timestamp values use database-side defaults.

The application layer is responsible for updating `updated_at` when an entity is mutated.

Milestone 2 does not introduce an automatic database update trigger.

`updated_at` is not a security version or stale-context protection mechanism.

#### Migration Boundary

The initial Milestone 2 persistence model is implemented as one coherent Alembic migration revision.

Migration validation must include:

```text
clean database
→ upgrade to M2
→ validate schema and invariants
→ downgrade to pre-M2
→ upgrade to M2 again
```

Ownership-transfer concurrency testing is intentionally deferred to Milestone 7.

### Membership Lifecycle Representation

Phase 1 product semantics eventually require:

- Pending
- Active
- Disabled
- Revoked / Former

Milestone 2 establishes only the persistent representation needed to support later lifecycle and security behavior.

Milestone 2 Membership status therefore includes:

- Active
- Disabled
- Revoked

It must not prematurely decide that every lifecycle concept must be represented by a Membership row.

In particular, invitation/Pending representation remains an implementation-design question for the relevant milestone.

### Design Constraints

- User Identity must not be owned by one Organization.
- Organization remains the tenant/data-isolation boundary.
- Membership represents participation in one Organization.
- A User may have zero usable Memberships.
- Foundation authorization profile belongs to Membership context.
- Membership state in one Organization must not implicitly affect another Organization.
- Multi-Organization Membership must not introduce multi-company business behavior.
- Active Organization context must not be modeled prematurely as a global persistent User property.
- Organization ownership invariants must be enforceable without introducing a generic role framework.
- The model must remain understandable and maintainable by one person.

### Non-Goals

Milestone 2 does not implement:

- public registration workflow,
- login,
- session/token mechanics,
- Organization-selection UX,
- trusted tenant-context establishment,
- PostgreSQL RLS enforcement,
- capability evaluation,
- invitation workflow,
- Membership administration workflow,
- ownership-transfer workflow,
- Business Module entities,
- billing/subscription behavior.

### Acceptance Criteria

Milestone 2 is complete when:

- User Identity can be persisted independently from Organization,
- Organization can be persisted,
- Membership can associate User Identity with Organization,
- one User can hold Memberships in multiple Organizations,
- one Organization can contain multiple Memberships,
- duplicate User/Organization Membership is rejected,
- Membership supports Owner/Admin/Member Foundation-profile semantics,
- the persistent model can represent usable versus non-usable Membership states required by later security behavior,
- the model can preserve exactly-one-Owner semantics for a usable/active Organization,
- Organization A Membership does not imply Organization B Membership,
- User Identity remains valid independently from Membership removal/revocation,
- migrations successfully build the schema from a clean database,
- automated tests validate essential Identity/Organization/Membership invariants,
- CI executes the relevant migration and test coverage.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003

---

## Milestone 3 — Registration & Authentication

### Status

Implementation — Current.

The Milestone 3 implementation-level technical design has been completed, reviewed, and approved before implementation.

The design was:

- proposed and revised by the Tech Lead / Software Architect,
- challenged through multiple QA review rounds,
- given final QA PASS with no remaining blocker or required Tech Lead revision,
- reviewed with the Founder by the Engineering Mentor,
- and explicitly approved by the Founder.

The password minimum-length portion of that design was subsequently revised by Founder Decision DEC-008.

Founder implementation is now the current step.

#### Implementation Progress

**Authentication Persistence Foundation — Implemented**

- Implemented password-credential and authentication-session persistence models and Alembic migration.
- Added PostgreSQL-backed persistence invariant tests.
- Atomic Registration Service/Persistence is implemented and locally tested.
- Registration HTTP API, login, and runtime session workflows remain pending.

**Email Canonicalization & Validation — Implemented and Tested Locally**

- Implemented `canonicalize_email()` in `backend/app/auth/email.py`.
- Uses compiled Python Regex and explicit Python validation.
- Supports the selected conventional ASCII dot-atom local-part syntax and hostname-style domain labels.
- Trims surrounding whitespace and lowercases both local part and domain.
- Preserves dots and plus tags without provider-specific rewriting.
- Rejects invalid syntax and unsupported Non-ASCII/EAI email addresses.
- Validates length limits: 64 characters for local part, 63 per domain label, and 254 for the complete email address.
- Added 29 automated tests in `backend/tests/test_email.py`.
- Full backend regression suite: 59 tests passed locally at completion of this subtask.
- Email canonicalization changes passed GitHub Actions CI on commit `d438bea`, as confirmed by the Founder.

**Password NFC Normalization — Implemented, Tested Locally, and CI Confirmed**

- Implemented `normalize_password()` in `backend/app/auth/password.py`.
- Uses Python `unicodedata.normalize("NFC", raw_password)`.
- Preserves leading/trailing whitespace and case sensitivity.
- Supports Unicode passwords, including Thai characters.
- Added `backend/tests/test_password.py` with 5 automated tests covering whitespace preservation, Unicode NFC equivalence, case sensitivity, Thai characters, and idempotence.
- At completion of NFC normalization, 5 password normalization tests passed locally.
- At completion of NFC normalization, the full backend regression run passed 64 tests locally.
- Password NFC normalization changes on commit `c6281e7` passed GitHub Actions CI, as confirmed by the Founder.
- The subsequent password length validation work is tracked separately below.
- At the time of this NFC normalization subtask, common/compromised-password screening and Argon2id implementation were not yet complete. Their subsequent progress is tracked separately below.

**Password Length Validation — Complete; CI Confirmed**

- Founder implemented `prepare_password(raw_password: str) -> str` in `backend/app/auth/password.py`.
- The implementation performs Unicode NFC normalization before password length validation.
- DEC-008 requires a minimum of 8 and maximum of 128 Unicode code points after NFC normalization.
- Passwords outside the allowed length range are rejected using `ValueError`.
- Password validation preserves Unicode, case sensitivity, and leading/trailing whitespace.
- Passwords are not silently truncated.
- Plaintext passwords are not included in validation error messages.
- The existing `normalize_password()` function remains unchanged in behavior.
- Founder added 11 automated tests to `backend/tests/test_password.py`.
- New tests cover 7/8/9 and 128/129 code-point boundaries, NFC-normalized length changes, leading/trailing whitespace, case sensitivity, Thai/Non-ASCII passwords, and no silent truncation.
- Latest local password test suite: 16/16 passed.
- Latest local full backend regression: 75/75 passed.
- Local failed tests: 0.
- Engineering Mentor reviewed `backend/app/auth/password.py`, `backend/tests/test_password.py`, and the relevant source-of-truth documents.
- Engineering Mentor reported that implementation logic and tests passed review.
- `git diff --check` reported no remaining whitespace errors.
- A Windows LF-to-CRLF warning for `docs/DECISION_LOG.txt` and minor formatting observations were reported as non-blocking.
- Documentation synchronization is complete and has been reviewed by Command Center.
- Committed on `main` as `fb36c12` (`feat(auth): add password length validation`).
- Push succeeded; GitHub Actions CI PASS, as confirmed by the Founder.
- Git working tree was clean at Engineering Mentor handoff.
- This subtask covers NFC normalization and length validation only; blocklist screening, Argon2id, and registration/login integration remain separate M3 tasks.

**Common / Compromised Password Blocklist — Implemented; Independent QA Pending**

DEC-009 remains the accepted screening strategy.

The Engineering Mentor verified the following implementation on GitHub `main`:

- `backend/app/auth/password.py`:
  - Local common-password checker
  - Local dataset loader
  - SHA-1 prefix/suffix helpers
  - NFC normalization and length validation
- `backend/app/auth/hibp.py`:
  - HIBP response parser
  - HIBP Range API client
  - Compromised-password lookup
  - Fail-closed handling of provider errors
- `backend/app/auth/screening.py`:
  - Integrated normalization, validation, local screening, and HIBP screening
- `backend/tests/test_screening.py`:
  - 17 automated screening tests
- `backend/tests/test_hibp_live.py`:
  - Separate opt-in real HIBP integration test

**Verification Results — 2026-10-18**

- Local live HIBP integration: 1 passed (Founder-reported).
- Local full backend regression: 131 passed, 1 skipped (Founder-reported).
- GitHub Actions CI: 131 passed, 1 skipped.
- Latest verified commit: `b3e7ab4`.
- The live HIBP test is skipped by default unless `RUN_LIVE_HIBP=1`.

The Engineering Mentor completed a preliminary code review of the screening implementation and its automated tests.

Independent Technical Security/QA review and formal subtask acceptance remain pending.

The screening functions accept injected dependencies and are integrated into the Atomic Registration Service/Persistence workflow. Registration HTTP API integration and runtime dependency wiring remain pending.

The implementation must continue to preserve fail-closed behavior and prevent sensitive exception-context leakage through future application logging.

The Founder intentionally committed the selected SecLists NCSC password dataset during internal development.

The DEC-009 Founder Clarification dated 2026-10-17 confirms that continued internal use and retention of this Git commit are approved under the current development approach, subject to applicable published terms.

The existing Git commit is not, by itself, evidence of a licensing violation or a reason to initiate repository remediation.

Additional dataset rights confirmation and applicable HIBP commercial SaaS terms remain pre-external-release verification requirements.

Pending commercial-launch clarification does not automatically block internal M3 technical acceptance.

DEC-009 remains accepted. Its technical security requirements and pre-external-release gates remain unchanged.

**Remaining M3 Work**

- Obtain independent Technical Security/QA review and formal acceptance of the Password Blocklist implementation.
- Integrate safe Argon2id rehash persistence into Login,
  ensuring failed updates preserve the existing valid credential.
- Integrate the approved Password Screening Pipeline into the Registration HTTP API through runtime dependency wiring.
- Expose the implemented Atomic Registration Service/Persistence workflow through the Registration HTTP API with safe public error handling.
- Implement login and authentication failure handling.
- Implement PostgreSQL-backed session issuance, validation, expiry, and logout.
- Implement authentication abuse protection and account-enumeration resistance.
- Implement secure cookie handling, CSRF protection, and remaining authentication security controls.
- Implement the minimum functional M3 browser workflows for registration, login, logout, session expiry/recovery, and authenticated pre-tenant state.
- Complete required backend, browser integration, and adversarial regression tests.
- Obtain final M3 acceptance after all required criteria are met.

Dataset rights confirmation and applicable HIBP commercial SaaS terms remain separate mandatory pre-external-release requirements under AQ-016.

**Open Consideration**

- The current validator accepts single-label domains such as `alice@localhost`.
- Public SaaS domain policy remains unresolved.
- Email syntax validation does not verify mailbox ownership. Email verification remains outside M3.

### Goal

Establish global User self-service registration and trusted authenticated User Identity.

### Scope

Implement:

- self-service User registration,
- secure password-credential establishment,
- authentication,
- authoritative server-side session establishment,
- trusted current-User identity,
- current-session logout/revocation,
- authentication failure behavior,
- login and registration abuse protection,
- browser authentication security required by the approved design,
- and minimum authenticated Foundation behavior.

Registration creates a global User Identity plus its password credential as one atomic operation.

Organization creation belongs to Milestone 4.

A User with zero usable Memberships is a valid Foundation state and must be able to authenticate normally.

### Product Flow Boundary

Milestone 3 is an implementation boundary, not the final customer journey.

The intended completed Foundation flow remains:

```text
Register
→ Authenticate
→ Create first Organization
→ Create Membership
→ Creator becomes Owner
→ Start using Kijflow
```

The Organization portion is implemented in Milestone 4.

Milestone 3 authentication establishes only trusted global User Identity.

It does not establish or imply:

- Organization Membership,
- trusted Organization context,
- tenant access,
- Owner / Admin / Member profile,
- Foundation capabilities,
- or verified mailbox ownership.

### Approved M3 Implementation-Level Design

The Founder has approved the following implementation-level Registration & Authentication design for Milestone 3, subject to the subsequent minimum-password-length revision recorded in DEC-008.

#### Authentication Persistence Boundary

The existing global `users` table remains the authoritative global User Identity persistence established in Milestone 2.

Milestone 3 does not add authentication-specific fields directly to `users`.

A valid M2 User may exist without password credentials.

Such a User:

```text
exists globally
+
no user_password_credentials row
→ cannot authenticate using password
```

Do not create fake credentials merely because a global User exists.

Milestone 3 introduces separate password-credential and server-session persistence.

#### Password Credential Persistence

Minimum approved representation:

```text
user_password_credentials
────────────────────────────
user_id          UUID PK NOT NULL
email            TEXT NOT NULL UNIQUE
password_hash    TEXT NOT NULL
created_at       TIMESTAMPTZ NOT NULL
updated_at       TIMESTAMPTZ NOT NULL
```

Rules:

- `user_id` references the global `users` identity,
- one password credential exists at most once per User,
- `email` stores the canonical Phase 1 global login identifier,
- canonical email uniqueness is database-enforced,
- `password_hash` stores only the Argon2id representation,
- plaintext passwords are never persisted,
- and credential deletion behavior must remain deliberate while global User hard-delete semantics remain unresolved.

The global login email is credential/login data.

It does not make the User belong to an Organization.

#### Email Canonicalization

Phase 1 uses email as the global password-login identifier.

Canonicalization is deterministic:

1. trim surrounding whitespace,
2. accept conventional ASCII email syntax,
3. lowercase the local part,
4. lowercase the domain,
5. use the resulting canonical email for database uniqueness and login lookup.

Do not perform provider-specific rewriting such as:

- Gmail dot removal,
- `+tag` removal,
- provider-specific alias expansion.

Native Unicode/EAI email support is outside the Milestone 3 design.

For example:

```text
Alice@Example.COM
 alice@example.com
ALICE@example.com
```

canonicalize to:

```text
alice@example.com
```

Milestone 3 does not include email verification.

Therefore:

> Registration with an email address does not prove that the User controls or owns that mailbox.

Future invitation, recovery, or other mailbox-sensitive behavior must not silently treat an unverified login email as verified mailbox ownership.

#### Password Processing Contract

Password processing must be deterministic.

Approved pipeline:

```text
raw password
→ Unicode NFC normalization
→ length / policy validation
→ common / compromised password blocklist evaluation
→ Argon2id
```

Login applies the same NFC normalization before password verification.

Milestone 3 does not perform additional password normalization:

- no trimming,
- no lowercasing,
- no case folding,
- no whitespace collapsing.

Leading and trailing whitespace remain part of the password.

After NFC normalization:

- minimum length is **8 Unicode code points**,
- maximum length is 128 Unicode code points,
- over-maximum input is rejected,
- silent truncation is forbidden,
- Unicode and spaces are allowed.

The minimum was revised from 15 to 8 by DEC-008.

This revision deliberately accepts a lower password-strength floor for password-only authentication. It does not meet the NIST SP 800-63B-4 minimum of 15 characters for passwords used as a single authentication factor.

The Founder has accepted that trade-off.

Password establishment must reject passwords identified by the approved policy as:

- common,
- known-compromised.

The original M3 security requirement is an effective common/compromised-password screening outcome; an external breach-service integration was not a prerequisite of that requirement. DEC-009 subsequently selects local common-password screening plus HIBP Range API for the current implementation approach, subject to its third-party gates and reconsideration triggers.

DEC-009 screening contract:

- Check the NFC-normalized, length-validated password using exact-match local common-password screening. Preserve whitespace and case; do not silently modify user input.
- For HIBP, compute SHA-1 solely for the range lookup, send only the first five hexadecimal characters over HTTPS, and match suffixes and nonzero occurrence counts locally. Do not send plaintext, email, or a full hash; SHA-1 is not used for stored credentials.
- Request response padding (`Add-Padding: true`) where supported, and do not treat padded zero-count entries as compromised.
- Use bounded network calls and safe response validation; on unavailable/malformed required HIBP results, fail closed with a generic retryable error.
- Keep the provider boundary small and replaceable; do not introduce a generic integration/plugin framework.

The chosen provider and dataset remain replaceable through a reviewed decision if new evidence changes their suitability. DEC-008 continues to govern the unchanged password-length, Argon2id, abuse-protection, and authentication-security requirements.

#### Argon2id Policy

Milestone 3 uses Argon2id for password hashing.

Initial approved baseline:

```text
Algorithm:   Argon2id
Version:     19
Memory:      19456 KiB / 19 MiB
Time cost:   2
Parallelism: 1
```

This is the initial security floor and should be benchmarked against the intended runtime before Milestone 3 completion.

The normal stored Argon2 representation contains its algorithm, version, salt, and parameter metadata.

No separate salt column is required.

After successful password verification:

```text
stored Argon2 policy outdated?
→ safely rehash using current policy
→ replace old hash
```

Rehash rules:

- rehash only after successful authentication,
- failed authentication never rehashes,
- rehash failure must not destroy the previous valid credential.

#### Registration Flow

Conceptually:

```text
receive untrusted email / password
        ↓
request / resource bounds
        ↓
canonicalize + validate email
        ↓
NFC normalize password
        ↓
password length / policy validation
        ↓
password blocklist check
        ↓
registration abuse control
        ↓
Argon2id hashing
        ↓
BEGIN TRANSACTION
        ↓
create global User
        ↓
create PasswordCredential
        ↓
COMMIT
```

Successful registration creates only:

```text
global User
+
PasswordCredential
```

Registration must not create:

- Organization,
- Membership,
- trusted Organization context,
- Foundation profile,
- Foundation capability authority.

User and PasswordCredential persistence form one atomic registration operation.

If either persistence step fails, the registration transaction must roll back rather than leave a partial account state.

#### Duplicate Registration

Canonical email uniqueness is database-enforced.

Concurrent registrations using the same canonical email must not create multiple accounts.

When the canonical email already exists:

- registration fails,
- no duplicate User or credential is created,
- no internal User ID, Membership information, or internal account state is exposed,
- public failure messaging remains generic,
- registration abuse protection still applies.

Milestone 3 accepts the residual possibility that registration success-versus-failure can reveal some account-existence information.

Milestone 3 does not introduce fake-success or email-verification workflow solely to eliminate that residual inference.

#### Login Flow

Conceptually:

```text
receive untrusted email / password
        ↓
canonicalize email
        ↓
NFC normalize password
        ↓
online-guessing protection
        ↓
credential lookup
        ↓
Argon2 verification
(or verification-class work when account is absent)
        ↓
success?
  ├─ no → generic authentication failure
  └─ yes
       ↓
       optional safe Argon2 rehash
       ↓
       generate fresh opaque session token
       ↓
       persist session-token digest / authoritative session state
       ↓
       issue secure HttpOnly cookie
```

Failed authentication must never create a session.

#### Account-Enumeration Resistance

Unknown email and wrong password must not have an obvious cheap-path timing difference.

Conceptually:

```text
existing account
→ verify real Argon2 hash

nonexistent account
→ perform password-verification-class work
   against a pre-generated dummy current-policy hash
```

Public authentication failure behavior must be materially equivalent.

Perfect request-wide constant-time execution is not required, but obvious enumeration shortcuts are forbidden.

Anti-abuse behavior must also preserve this boundary.

For repeated failed login attempts, materially observable behavior for known and nonexistent identifiers must remain materially equivalent, including as applicable:

- throttling behavior,
- delays,
- retry / lockout behavior,
- HTTP status,
- response body,
- other externally observable anti-abuse behavior.

Anti-abuse controls must not become a new account-enumeration side channel.

#### Login and Registration Abuse Protection

Repeated failed authentication must eventually trigger effective online-guessing protection.

Protection must consider at least:

- canonical account/login identifier,
- request source / network dimension.

Do not rely solely on permanent account lockout.

Registration also requires abuse/resource-exhaustion protection because it performs expensive or state-changing work including:

- validation,
- password blocklist evaluation,
- Argon2 hashing,
- database writes.

The approved design does not require a particular abuse-control infrastructure such as:

- Redis,
- a specific database-counter design,
- a gateway,
- CAPTCHA,
- or fixed thresholds.

The mechanism may be selected during implementation, but it must satisfy the approved security and enumeration-resistance outcomes before Milestone 3 is complete.

#### Server-Side Session Persistence

Milestone 3 uses PostgreSQL-backed opaque server sessions.

Minimum approved representation:

```text
auth_sessions
────────────────────────────
id             UUID PK NOT NULL
user_id        UUID NOT NULL
token_digest   BYTEA NOT NULL UNIQUE
created_at     TIMESTAMPTZ NOT NULL
expires_at     TIMESTAMPTZ NOT NULL
revoked_at     TIMESTAMPTZ NULL
```

Required persistence/security invariants include:

```text
user_id references a valid User

token_digest NOT NULL
token_digest UNIQUE

created_at NOT NULL
expires_at NOT NULL

expires_at > created_at

revoked_at IS NULL
OR revoked_at >= created_at
```

`auth_sessions` does not contain:

- `organization_id`,
- `membership_id`,
- `active_organization_id`,
- Owner / Admin / Member profile,
- Foundation capabilities.

A session represents authenticated global User Identity only.

#### Session Token Security

The session token is:

- opaque,
- server-generated,
- cryptographically random,
- designed with approximately 256 bits of entropy,
- returned to the browser only through the authentication cookie.

The database persists only the SHA-256 digest of the raw token.

The raw session token must never be persisted.

The token itself encodes no trusted claims about:

- User,
- Organization,
- Membership,
- profile,
- capability.

Authenticated identity is resolved through authoritative server-side session state.

#### Session Validity

The initial absolute session lifetime is configurable, with approximately 24 hours as the initial default.

A session is valid only when:

```text
token digest is recognized
AND referenced User exists
AND revoked_at IS NULL
AND current time < expires_at
```

The following fail closed:

- missing token,
- malformed token,
- unknown token,
- expired session,
- revoked session,
- invalid referenced identity.

Multiple sessions for one User are allowed.

Milestone 3 does not introduce refresh tokens.

#### Trusted Current User

Trusted current User identity resolves conceptually as:

```text
cookie raw token
        ↓
SHA-256 digest
        ↓
valid authoritative AuthSession
        ↓
auth_sessions.user_id
        ↓
global User
```

Untrusted identity claims such as:

```text
body.user_id
query user_id
X-User-ID
arbitrary client email identity
```

must never establish or override authenticated User identity.

For example:

```text
valid session = User A
client claim  = User B
```

must resolve as:

```text
Trusted User = User A
```

#### Logout Semantics

Logout revokes the current session server-side.

Required invariant:

```text
token valid
→ logout succeeds
→ current session becomes revoked
→ same raw token is presented again
→ authentication fails
```

Clearing the browser cookie alone is not sufficient logout behavior.

Current-session logout must not accidentally revoke unrelated sessions belonging to the same User.

Logout-all-devices is outside Milestone 3.

#### Cookie Security

Production-like session-cookie requirements are:

```text
HttpOnly
Secure
SameSite=Lax
Path=/
```

Host-only / `__Host-` semantics should be preferred when deployment topology permits.

The authentication bearer token must not be stored in:

- `localStorage`,
- `sessionStorage`,
- URLs or query strings.

#### CSRF Boundary

`SameSite=Lax` is defense in depth, not the complete CSRF solution.

State-changing browser authentication operations require intentional CSRF/security treatment.

Milestone 3 operations include at least:

- registration,
- login,
- logout.

Required security outcome:

> An untrusted cross-site browser origin must not be able to trigger a security-sensitive authentication state transition as though it came from trusted Kijflow frontend interaction.

The exact mechanism may be selected during implementation according to the actual frontend/backend deployment boundary.

Possible mechanisms may include:

- Origin validation,
- CSRF tokens,
- double-submit patterns,
- or a suitable combination.

SameSite alone must not be treated as proof that the CSRF requirement is satisfied.

#### Secret Leakage Prohibition

The following secrets must never appear in database persistence or normal observability/output paths:

```text
plaintext password
raw session token
```

They must not be emitted to:

- normal logs,
- structured request-body logs,
- traces,
- exception messages,
- debug output,
- analytics/events,
- CI/test failure output.

Password hashes and session digests should also not be routinely emitted into logs.

Authentication endpoints must support appropriate sensitive-field redaction or exclusion from generic request logging.

### Approved M3 Boundary

Milestone 3 must not establish or imply:

```text
Authentication
≠ Organization Membership
≠ trusted Organization context
≠ tenant access
≠ Owner / Admin / Member profile
≠ Foundation capabilities
```

A User with zero Memberships must be able to complete this flow:

```text
register
→ authenticate
→ trusted current User resolves
→ no Organization context exists
```

This is valid Milestone 3 behavior.

### Implementation-Level Choices Still Open Within M3

The approved design intentionally leaves several mechanism-level choices open provided the required outcomes above are satisfied before Milestone 3 completion:

- exact abuse-control storage technology,
- exact throttling thresholds,
- exact licensed local password dataset/version under DEC-009 and provider-interface implementation details (subject to the accepted local + HIBP strategy or Founder-reviewed change),
- exact CSRF mechanism consistent with the actual deployment boundary,
- deployment-dependent host-only / `__Host-` cookie applicability.

These are implementation choices, not permission to weaken the approved security invariants.

### Non-Goals

Milestone 3 does not implement:

- Organization creation or bootstrap,
- Membership discovery,
- Organization selection,
- trusted Organization context,
- Organization switching,
- tenant-isolation enforcement,
- PostgreSQL RLS,
- Foundation capability authorization,
- invitation / Pending Membership workflow,
- full Membership administration,
- ownership transfer,
- password change,
- password reset / recovery,
- email verification,
- MFA,
- social login,
- enterprise SSO,
- refresh tokens,
- token rotation infrastructure,
- session/device-management UI,
- logout-all-devices,
- Organization/profile/capability state in authentication sessions,
- native internationalized/EAI login-email support,
- Business Module behavior or authorization,
- billing/subscription onboarding.

DEC-008 does not expand these M3 boundaries.

### Required Automated / Adversarial Validation

At minimum, Milestone 3 testing must cover the following classes.

#### Email / Registration

- canonical email case variants,
- surrounding-whitespace normalization,
- canonical duplicate rejection,
- concurrent duplicate registration,
- unsupported EAI/Unicode email rejection deterministically,
- atomic registration rollback on partial persistence failure,
- registration creates zero Organization/Membership rows,
- existing global User without password credential cannot authenticate by password.

#### Password

- common password rejected,
- known-compromised password rejected,
- minimum-length boundary under DEC-008:
  - 7 Unicode code points after NFC normalization are rejected,
  - 8 Unicode code points meet the minimum-length rule, subject to other policy checks,
  - 9 Unicode code points meet the minimum-length rule, subject to other policy checks,
- maximum-length boundary:
  - 128 Unicode code points after NFC normalization meet the maximum-length rule, subject to other policy checks,
  - 129 Unicode code points after NFC normalization are rejected,
- over-maximum rejection,
- no silent truncation,
- leading/trailing whitespace preserved and counted,
- deterministic Unicode NFC behavior,
- length validation performed after NFC normalization,
- Unicode inputs whose code-point count changes under NFC are evaluated using the normalized value,
- canonically equivalent Unicode password verifies consistently,
- passwords meeting the length rule remain subject to common/compromised-password blocklist screening,
- same plaintext password produces independently salted Argon2 representations.

#### Password Blocklist — Mock and Live Integration

- Local common-password exact match rejects blocked values without silently trimming/case-folding the NFC-normalized password.
- Mocked/fake HIBP provider deterministically covers compromised match, clean response, positive versus zero padding counts, malformed response, timeout, provider error, and fail-closed behavior.
- Mocked tests check no plaintext password, email address, or full SHA-1 hash is sent to HIBP, and no secrets appear in ordinary logs/errors or CI output.
- Separate live HIBP integration test confirms HTTPS connectivity, correct five-character prefix request, valid response parsing, and rejection of a known-compromised test password.
- Mocked blocklist tests run in normal CI; the live test is run separately and has a recorded PASS before the blocklist subtask closes. A live HIBP outage must not falsely imply that deterministic Kijflow code tests failed.
- New or replacement third-party password datasets must have their specific provenance and applicable rights verified before being committed or redistributed.
- The existing SecLists NCSC dataset commit (`d6dc883`) was intentionally performed by the Founder and is covered by the DEC-009 Founder Clarification dated 2026-10-17. Its existence alone does not block internal M3 technical acceptance or require repository remediation. Applicable third-party rights and release requirements remain subject to verification before external-user access.
- The local-list value/maintenance review and any material provider or dataset strategy change must return to the Founder for review.
- External-user release, including free beta, is blocked until applicable third-party data rights and HIBP terms have been clarified, regardless of technical test results.

#### Argon2id

- current-policy hash verifies,
- wrong password fails,
- outdated valid hash authenticates and safely rehashes,
- failed authentication never rehashes,
- malformed stored credential fails safely.

#### Login / Abuse / Enumeration

- valid login,
- wrong password,
- nonexistent email,
- nonexistent-account path performs password-verification-class work,
- public known-account and nonexistent-account failure behavior is materially equivalent,
- repeated failed attempts for known and unknown identifiers have materially equivalent observable anti-abuse behavior,
- failed login creates no session,
- login throttling/abuse protection activates,
- registration throttling/abuse protection activates,
- abuse controls do not become unsafe permanent lockout or accidental account destruction.

#### Session

- valid session resolves the correct global User,
- missing token denied,
- malformed token denied,
- unknown token denied,
- expired token denied,
- revoked token denied,
- invalid timestamp ordering rejected by persistence constraints,
- raw token absent from database persistence,
- multiple sessions can coexist,
- current-session logout leaves unrelated session valid,
- logout makes the original raw token unusable.

#### Browser Security / CSRF

- required cookie security attributes are present,
- raw authentication token is inaccessible to frontend JavaScript,
- untrusted cross-site login cannot establish an unintended authenticated session,
- cross-site logout cannot revoke the victim's session as though it were a trusted Kijflow action,
- SameSite is not accepted as the sole CSRF control.

#### Secret Leakage

- plaintext password is not logged,
- raw session token is not logged,
- sensitive fields are excluded/redacted from structured request logs,
- exceptions/debug output do not reveal plaintext password or raw session token,
- CI/test failure output does not reveal these secrets.

#### Architecture Boundary

```text
User with zero Memberships
→ login succeeds
→ current User resolves
→ no Organization context exists
```

Registration and login must not:

- create Organization,
- create or modify Membership,
- establish trusted Organization context,
- establish Owner / Admin / Member profile,
- evaluate or grant Foundation capability authority.

### Acceptance Criteria

Milestone 3 is complete when:

- a new User can register a global Identity with password credentials,
- User + PasswordCredential registration is atomic,
- registration does not require or create an Organization/Membership,
- canonical login email uniqueness is enforced,
- password processing follows the approved NFC / length / blocklist / Argon2id policy, including the 8–128 Unicode-code-point limits established by DEC-008,
- password hashes rather than plaintext passwords are persisted,
- valid credentials can authenticate,
- invalid credentials are rejected without creating a session,
- nonexistent-account login does not take an obvious cheap path,
- abuse controls protect login and registration without creating a material account-enumeration distinction,
- successful authentication establishes an authoritative PostgreSQL-backed opaque server session,
- only the SHA-256 digest of the session token is persisted,
- missing, malformed, unknown, expired, or revoked sessions fail closed,
- backend can reliably resolve the authenticated global User from authoritative session state,
- arbitrary client identity claims cannot establish or override another User's identity,
- current-session logout revokes server-side session state and the old raw token cannot be reused,
- authentication remains independent from Organization Membership and tenant context,
- a User with zero Memberships can remain a valid authenticated identity,
- required cookie and CSRF security outcomes are validated,
- plaintext passwords and raw session tokens do not leak through persistence, logs, traces, errors, debug output, analytics, or CI/test output,
- the required automated/adversarial authentication regressions run in CI,
- DEC-009 mock and separate real HIBP integration tests pass before the blocklist subtask is closed,
- the selected SecLists NCSC dataset is integrated into the internal M3 password-screening implementation under the DEC-009 Founder Clarification dated 2026-10-17, without treating the intentional existing Git commit as an independent technical acceptance blocker,
- any new or replacement third-party password dataset has undergone the required provenance and rights review before being committed or redistributed,
- any dataset or provider substitution that materially changes the accepted DEC-009 approach has received Founder review,
- third-party rights/terms verification remains a mandatory release gate before any external-user access, including beta,
- implementation remains within the accepted M3 boundary and preserves DEC-001 through DEC-005, DEC-008, and DEC-009.
- registration, login, logout, session expiry/recovery, and authenticated pre-tenant behavior work through the real browser and backend,
- browser authentication integration validates the approved cookie and CSRF security outcomes.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-005
- DEC-008
- DEC-009
- DEC-010
- DEC-011

---

## Milestone 4 — Organization Bootstrap & Trusted Organization Context

### Goal

Enable authenticated Users to create Organizations through self-service and establish trusted Organization context only through validated Membership.

### Scope

Implement self-service Organization creation.

#### First Organization

```text
Authenticated User
        ↓
Create Organization
        ↓
Create Membership
        ↓
Creator becomes Owner
        ↓
Organization becomes usable
```

#### Additional Organization

```text
Authenticated existing User
        ↓
Create another Organization
        ↓
Create new Membership
        ↓
Creator becomes Owner
```

Implement the minimum Organization-selection/context behavior required by later tenant isolation.

Implement the minimum authenticated pre-tenant Membership discovery required for Organization selection.

This discovery path must:

- return only Organizations accessible through the authenticated User's own usable Memberships,
- not expose another User's Memberships,
- not expose tenant-owned Business Module data,
- remain a Foundation-specific access path rather than a generic cross-tenant query mechanism.

### Expected Product Behavior

If a User has:

- one usable Organization → product may enter it directly,
- multiple usable Organizations → product should require or provide deliberate selection,
- zero usable Organizations → product must not invent or assume tenant context.

The current Organization must be clearly identifiable when tenant-scoped functionality exists.

Exact UX implementation remains subject to UX design.

### Trusted Context Principle

Organization ID from the client represents selection intent only.

Conceptually:

```text
Authenticated User
        ↓
Requested Organization
        ↓
Validate usable Membership
        ↓
Trusted Organization Context
```

Client input alone cannot establish trusted Organization context.

### Security Requirements

- Organization creation and Owner establishment form one valid operation.
- Creator becomes Owner through trusted system behavior.
- Arbitrary client input cannot assign Owner authority.
- User cannot establish normal Organization context without valid usable Membership.
- Membership in Organization A cannot establish Organization B context.
- pre-tenant Membership discovery must be limited to the authenticated User's own Memberships.
- failure must not leave invalid partial Organization/ownership state.

### Non-Goals

- invitation workflow
- full Membership administration
- ownership-transfer workflow
- full RLS enforcement
- Business Module behavior
- billing/subscription setup
- multi-company switching semantics
- generic cross-tenant Foundation queries

### Acceptance Criteria

Milestone 4 is complete when:

- authenticated User can create their first Organization,
- creator receives Owner Membership through trusted system behavior,
- existing authenticated User can create an additional Organization,
- each new Organization has independent ownership and Membership,
- failed bootstrap does not leave invalid partial state,
- system can identify Organizations the authenticated User is permitted to access,
- pre-tenant Membership discovery returns only the authenticated User's own accessible Organizations,
- another User's Memberships cannot be discovered through the normal Organization-selection path,
- Organization selection requires valid usable Membership,
- arbitrary Organization ID cannot independently establish trusted context,
- zero-Membership User does not receive fabricated Organization context,
- relevant bootstrap/context tests run in CI.
- the browser supports zero-Organization state, first/additional Organization creation, accessible Organization discovery, selection, and switching,
- the current Organization is clearly visible only after backend validation of trusted Organization context.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-005
- DEC-010

---

## Milestone 5 — Tenant Isolation

### Goal

Enforce Organization as the tenant/data-isolation boundary under the revised multi-Organization Membership model.

### Scope

Implement the accepted tenant-isolation chain:

```text
Authenticated User Identity
        ↓
Organization selection intent
        ↓
Validate usable Membership
        ↓
Trusted Organization Context
        ↓
Application / service tenant scoping
        ↓
Effective PostgreSQL RLS
        ↓
Same-tenant relationship integrity
```

Include:

- trusted Organization-context enforcement,
- explicit application/service tenant scoping,
- effective PostgreSQL Row-Level Security,
- fail-closed behavior,
- prevention of cross-tenant reads,
- prevention of cross-tenant writes,
- resource-ID manipulation protection,
- Organization switching safety,
- stale Membership/context handling,
- database execution-context safety,
- same-tenant relationship integrity,
- hardening and database-backed validation of pre-tenant Membership discovery.

### Pre-Tenant Foundation Access

Milestone 4 establishes the minimum pre-tenant Membership discovery required for Organization selection.

Milestone 5 hardens and validates this path as part of the tenant-isolation model.

Example:

```text
Authenticated User
→ Which Organizations may this User access?
```

Such paths must:

- operate against explicitly classified Foundation/security data,
- expose only information belonging to or discoverable by the authenticated User,
- not allow enumeration of another User's Memberships,
- not expose arbitrary tenant-owned Business Module data,
- not become a generic RLS bypass.

Milestone 5 must verify that this pre-tenant path remains safe even though trusted tenant context has not yet been established.

### Membership State and Tenant Access

Normal tenant access requires a usable Membership.

At minimum:

- Active Membership may establish normal context, subject to authorization.
- Disabled Membership cannot establish normal tenant access.
- Revoked/Former Membership cannot establish normal tenant access.
- stale Membership/context fails closed.

Exact handling of Pending/invitation state must follow its implementation semantics.

### Database-Backed Security Testing

Tenant-isolation behavior that depends on PostgreSQL must be tested using real PostgreSQL.

CI should test:

- RLS behavior,
- trusted context establishment,
- cross-tenant reads,
- cross-tenant writes,
- relationship integrity,
- context switching,
- database-context reuse where relevant,
- pre-tenant Membership-discovery isolation where relevant.

Tests that depend on PostgreSQL security semantics must not be replaced solely by mocks or a different database engine.

### Required Adversarial Cases

At minimum:

- Organization A cannot read Organization B tenant-owned data,
- Organization A cannot modify/delete Organization B tenant-owned data,
- User cannot select an Organization without usable Membership,
- Disabled Membership cannot establish normal access,
- Revoked Membership cannot establish normal access,
- stale context after revocation fails,
- Organization A → B switching does not retain A context,
- client Organization-ID manipulation does not bypass validation,
- User cannot enumerate another User's Memberships,
- pre-tenant discovery cannot expose Organizations inaccessible to the authenticated User,
- Owner cannot bypass tenant isolation,
- Admin cannot bypass tenant isolation,
- reused database execution context does not leak tenant identity.

### Non-Goals

- cross-tenant administrative tooling
- tenant migration
- group-company shared data
- Business Module-specific tenant rules
- generic isolation infrastructure for hypothetical future storage systems
- final production privileged-maintenance tooling

### Acceptance Criteria

Milestone 5 is complete when:

- trusted Organization context requires authenticated identity plus usable Membership,
- arbitrary client Organization IDs cannot establish trusted context,
- cross-tenant reads are denied,
- cross-tenant writes are denied,
- ID manipulation cannot cross the tenant boundary,
- missing/invalid/stale context fails closed,
- Disabled and Revoked Memberships cannot establish normal tenant access,
- Organization switching revalidates destination Membership,
- Owner/Admin cannot bypass tenant isolation,
- normal relational tenant access remains subject to effective RLS,
- database execution context does not leak across tenant-scoped units of work,
- tenant-inconsistent relationships cannot persist,
- rejected tenant-inconsistent operations do not leave partial invalid state,
- pre-tenant Membership discovery remains limited to the authenticated User's own accessible Organizations,
- another User's Memberships cannot be enumerated,
- PostgreSQL-backed isolation tests run in CI,
- deliberate tenant-isolation regressions are detected by tests.
- browser integration validates safe Organization switching, stale/inaccessible context recovery, and prevention of cross-tenant client-state leakage.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-005
- DEC-010

---

## Milestone 6 — Foundation Authorization

### Goal

Implement capability-oriented Foundation authorization within Organization Membership context.

### Scope

Implement:

- Owner profile
- Admin profile
- Member profile
- Foundation-owned capabilities required by implemented Foundation workflows
- Kijflow-defined profile-to-capability mappings
- explicit capability evaluation
- deterministic authorization behavior
- default-deny semantics

Authorization is evaluated against the relevant Membership.

Conceptually:

```text
Authenticated User
AND usable Membership
AND trusted Organization context
AND target belongs to Organization
AND required capability granted
→ operation may proceed
```

### Ownership Rules

Genuine ownership/lifecycle operations may use explicit Owner semantics.

Example:

- transfer Organization ownership

Ownership-specific rules must:

- be explicit,
- be documented,
- be testable,
- remain limited to Organization ownership/lifecycle behavior.

Owner semantics must never become a hidden Business Module authorization bypass.

### Capability Rules

- explicit grant → allow
- absent grant → deny
- missing mapping → deny
- unknown capability → deny
- Owner does not bypass capability evaluation
- Admin does not bypass capability evaluation
- profiles are not assumed to form implicit hierarchy
- capabilities never expand tenant boundary

### CI / Regression Coverage

Tests should cover:

- Owner mapping behavior,
- Admin mapping behavior,
- Member mapping behavior,
- explicit grants,
- explicit denials,
- missing mappings,
- unknown capabilities,
- ownership-only actions,
- interaction between authorization and tenant isolation.

### Non-Goals

- customer-defined roles
- per-user overrides
- Sales Manager
- Inventory Manager
- Accountant
- Business Module capability catalogs
- general-purpose ABAC
- generic policy engines
- permission-builder UI

### Acceptance Criteria

Milestone 6 is complete when:

- every implemented named Foundation capability has deterministic behavior for Owner/Admin/Member,
- explicit grants allow,
- missing grants deny,
- missing mappings deny,
- unknown capabilities deny,
- Owner does not universally bypass capability checks,
- Admin does not universally bypass capability checks,
- ownership-specific behavior is explicitly separated from general capability bypass,
- authorization never expands tenant boundary,
- authorization is testable independently from authentication and tenant isolation,
- authorization regression tests run in CI.
- browser integration validates authorization-aware actions, safe Access Denied behavior, and recovery after authoritative privilege reduction without relying on frontend checks as security enforcement.

### Relevant Decisions

- DEC-001
- DEC-003
- DEC-004
- DEC-005
- DEC-010

---

## Milestone 7 — Membership & Ownership Lifecycle

### Goal

Allow Organizations to manage participation safely while preserving global User Identity, historical attribution, authorization boundaries, and Organization ownership invariants.

### Scope

Implement the minimum Phase 1 workflow for:

- invitations,
- joining an Organization,
- Membership activation,
- Membership disabling,
- restoring Membership where appropriate,
- Membership revocation,
- Former-member semantics,
- Admin/Member profile management,
- Owner protection,
- ownership transfer.

### Invitation Principle

Organization manages Membership.

Organization does not create or own another person's global User credentials.

#### User Without Kijflow Identity

```text
Invitation
        ↓
User registers own Identity
        ↓
Invitation accepted
        ↓
Membership becomes usable
```

#### Existing Kijflow User

```text
Invitation
        ↓
Use existing global Identity
        ↓
Invitation accepted
        ↓
New Membership becomes usable
```

Do not create duplicate User Identity for an existing User.

Admin/Owner must not create another User's password or credentials.

The exact technical representation of:

- Invitation,
- Pending state,
- invitation token,
- expiration,

belongs to Milestone 7 implementation design.

### Membership Lifecycle

Minimum product semantics:

#### Active

Membership is usable subject to tenant isolation and authorization.

#### Disabled

Access is temporarily suspended.

The User remains known to the Organization.

#### Revoked / Former

The User is no longer an active Organization participant.

Revocation:

- prevents Organization access,
- does not delete global User Identity,
- does not affect other Organization Memberships,
- preserves historical attribution.

### Historical Attribution

Revoked Membership must not erase historical business meaning.

Past records may continue to show the former participant.

Example:

```text
Somchai Jaidee (Former member)
```

Former members may remain discoverable for administrative/historical contexts but should not normally appear as active selectable participants.

No blanket rule that every entity uses soft delete is introduced.

Deletion/lifecycle semantics remain domain-specific.

### Profile Management

Authorized Foundation administration may manage:

- Admin
- Member

according to capability policy.

Profile change is security-sensitive.

Ordinary account/profile editing must not grant elevated Foundation authority.

### Ownership Invariants

- an active Organization has exactly one Owner,
- Owner has an active Membership,
- Admin cannot remove Owner through ordinary management,
- Admin cannot disable Owner through ordinary management,
- Admin cannot revoke Owner through ordinary management,
- Admin cannot demote Owner through ordinary management,
- Owner must transfer ownership before leaving,
- ownership transfer cannot produce zero Owners,
- ownership transfer cannot produce multiple Owners,
- concurrent ownership changes must preserve ownership invariants.

### Organization Independence

Changing Membership in Organization A must not implicitly change Membership in Organization B.

This includes:

- disable,
- restore,
- revoke,
- profile changes,
- ownership state.

### Non-Goals

- Teams
- Departments
- customer-defined roles
- Business Module role management
- billing-per-user
- multi-company employee management
- blanket soft-delete framework
- Organization closure/purge implementation
- customer-offboarding export implementation

### Acceptance Criteria

Milestone 7 is complete when:

- invitations support new Users without Founder-created credentials,
- invitations support existing Users without duplicate Identity,
- accepted invitation can establish usable Membership,
- Membership in one Organization changes independently from another,
- Disabled Membership cannot access the Organization,
- Revoked Membership cannot access the Organization,
- global User Identity survives Membership revocation,
- historical attribution remains possible,
- Former members are not treated as ordinary active selectable members,
- authorized profile management follows Foundation capabilities,
- ordinary account editing cannot self-promote,
- Admin cannot remove/disable/revoke/demote Owner,
- Owner cannot leave without valid ownership transfer,
- ownership transfer preserves exactly one Owner,
- concurrent ownership transitions cannot create invalid ownership state,
- cross-Organization Membership-management attempts fail,
- Membership/ownership lifecycle regressions run in CI.
- browser integration validates approved invitation, Membership lifecycle, and ownership-transfer workflows, including denied actions, access revocation, and Owner protection.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-004
- DEC-005
- DEC-010

---

## Milestone 8 — Phase 1 Security, QA & Deployment Closure

### Goal

Verify that the revised SaaS Foundation satisfies the accepted Phase 1 architecture and demonstrate basic deployment readiness before beginning the first Business Module.

### Scope

#### Foundation Validation

Validate:

- global User Identity
- multi-Organization Membership
- registration
- authentication
- self-service Organization bootstrap
- trusted Organization-context establishment
- Organization switching
- tenant isolation
- capability authorization
- Membership lifecycle
- Owner lifecycle
- historical attribution
- failure paths
- concurrency-sensitive invariants
- Phase 1 regression coverage
- documentation synchronization

### Required Security / Adversarial Matrix

At minimum verify:

- invalid authentication,
- Organization selection without Membership,
- disabled Membership access attempt,
- revoked Membership access attempt,
- stale tenant context after Membership change,
- Organization A → B context switching,
- arbitrary Organization-ID manipulation,
- another User's Membership enumeration,
- cross-tenant read,
- cross-tenant write,
- cross-tenant relationship mutation,
- Owner cross-tenant attempt,
- Admin cross-tenant attempt,
- missing capability,
- unknown capability,
- Admin privilege escalation attempt,
- Owner privilege misuse outside ownership semantics,
- Admin attempt to remove/disable/revoke Owner,
- Owner leaving without transfer,
- concurrent ownership transfer,
- historical attribution after Membership revocation.

### Deployment Readiness

Review whether the Foundation can operate outside the Founder's local development machine.

Validate:

- application configuration,
- environment-variable handling,
- secret handling,
- process startup,
- database connectivity,
- migration execution,
- health-check behavior,
- required CI checks.

### Non-Production Deployment Rehearsal

Deploy the Phase 1 Foundation to a real non-production environment at least once.

The rehearsal should demonstrate:

```text
repository / build
        ↓
non-production runtime
        ↓
application starts
        ↓
configuration loads
        ↓
secrets load
        ↓
database connects
        ↓
migrations execute
        ↓
health check succeeds
        ↓
Foundation validation succeeds
```

The purpose is to expose environment-specific problems that local development may not reveal.

### Provider Evaluation

Evaluate practical deployment/provider options based on evidence learned during Phase 1.

Evaluation may consider:

- implementation effort,
- operational complexity,
- managed PostgreSQL support,
- backup capabilities,
- monitoring capabilities,
- deployment workflow,
- rollback practicality,
- cost,
- debugging experience,
- one-person maintainability.

Phase 1 does not require permanent production-provider commitment if evidence is insufficient.

### Non-Goals

- Sales Management testing
- performance optimization without evidence
- enterprise-scale load testing
- future Business Module architecture
- production customer launch
- production auto-CD
- high-availability infrastructure
- Kubernetes
- full observability platform
- final production backup policy
- final production topology without validated requirements
- forced provider commitment solely to close Phase 1

### Acceptance Criteria

Phase 1 must demonstrate that:

- User can register a global Identity,
- User can authenticate,
- one Identity can participate in multiple Organizations,
- Membership state is Organization-specific,
- Organization access requires usable Membership,
- trusted Organization context is established safely,
- multiple Organizations can be selected/switched without context leakage,
- authorization is evaluated in Membership context,
- Owner/Admin/Member differences are enforced,
- unauthorized actions are denied,
- cross-tenant reads are denied,
- cross-tenant writes are denied,
- ID manipulation does not bypass isolation,
- Owner cannot cross tenant boundaries,
- Admin cannot cross tenant boundaries,
- Membership revocation does not delete global Identity,
- Membership revocation in A does not affect B,
- historical attribution remains possible,
- Owner lifecycle invariants hold,
- Foundation security regressions pass in CI,
- Foundation deploys successfully to at least one real non-production environment,
- runtime configuration works outside the local machine,
- migrations execute successfully in the rehearsal environment,
- health check succeeds,
- significant environment-specific failures are resolved or explicitly documented,
- Foundation can support the first Business Module without redesigning core identity, Membership, ownership, authorization, or tenant boundaries.
- a representative Browser E2E suite passes against the real Next.js frontend, FastAPI backend, and PostgreSQL-backed state,
- the suite covers successful and adversarial Foundation workflows, including security-context changes and stale client-state recovery,
- the core browser journey passes against the real non-production deployment, and browser testing does not replace existing backend/PostgreSQL security tests.

All relevant Phase 1 source-of-truth documentation must reflect the implemented state before closure.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-004
- DEC-005
- DEC-010

---

# Revised Phase 1 Sequence

```text
Milestone 1 — Project Bootstrap
              COMPLETE

        ↓

Milestone 2 — Identity / Organization / Membership Foundation
              COMPLETE

        ↓

Milestone 3 — Registration & Authentication
              CURRENT — FOUNDER IMPLEMENTATION

        ↓

Milestone 4 — Organization Bootstrap & Trusted Organization Context

        ↓

Milestone 5 — Tenant Isolation

        ↓

Milestone 6 — Foundation Authorization

        ↓

Milestone 7 — Membership & Ownership Lifecycle

        ↓

Milestone 8 — Security / QA / Deployment Closure
```

---

# CI Evolution Through Phase 1

CI evolves with the application rather than being designed as a complete platform during Milestone 1.

Expected progression:

```text
Milestone 1
Basic automated tests
Migration validation
        ↓

Milestone 2
Identity / Organization / Membership model tests
Persistence invariant tests
Migration checks
        ↓

Milestone 3
Registration tests
Authentication tests
        ↓

Milestone 4
Organization bootstrap tests
Trusted context-establishment tests
        ↓

Milestone 5
Real PostgreSQL-backed
tenant / RLS / context-switching
integration tests
        ↓

Milestone 6
Owner / Admin / Member
authorization regression tests
        ↓

Milestone 7
Membership lifecycle
ownership lifecycle
concurrency/security regressions
        ↓

Milestone 8
Complete Phase 1
security / regression validation
```

CI should remain understandable and maintainable by the Founder.

Additional CI complexity should be introduced only when it protects meaningful Foundation behavior.

---

# Before Real Customer Use

Phase 1 deployment readiness is not equivalent to production readiness.

Before Kijflow is used by real customers, the production operating model must be reviewed and the required production decisions made.

At minimum evaluate and finalize as appropriate:

- production hosting/provider,
- production application deployment model,
- production PostgreSQL,
- production secret management,
- database backup strategy,
- restore validation,
- application and infrastructure monitoring,
- error visibility,
- deployment procedure,
- database migration procedure,
- rollback/recovery strategy,
- production access control,
- operational security,
- CD policy.

A reasonable one-person default should favor controlled deployment:

```text
change
  ↓
CI passes
  ↓
Founder reviews / approves
  ↓
production deployment
```

Automatic push-to-production deployment is not required.

The final CD approach should follow actual operational risk rather than architectural fashion.

---

# Implementation Discipline

Milestones define implementation sequence and completion boundaries.

They do not pre-decide every implementation mechanism.

Only the current milestone should be designed in implementation-level detail.

Later milestones should remain bounded by:

- Goal
- Scope
- Non-Goals
- Acceptance Criteria
- Relevant Decisions

until they become current.

This prevents implementation planning from becoming speculative architecture design.

---

# Intentionally Deferred Implementation Decisions

The approved Milestone 2 persistence subset and the approved Milestone 3 Registration & Authentication design are defined in their milestone sections above.

The Milestone 3 password minimum-length requirement was revised separately by Founder Decision DEC-008. The M3 blocklist provider/development/testing/release-gate strategy is recorded separately by Founder Decision DEC-009.

Milestone 3 has resolved the password-credential and authentication-session direction, including:

- separate `user_password_credentials`,
- Argon2id password hashing,
- email as the Phase 1 global login identifier,
- PostgreSQL-backed opaque server sessions,
- SHA-256 session-token digest persistence,
- secure HttpOnly cookie transport,
- absolute server-side session expiry,
- and current-session logout/revocation.

Those are no longer unresolved authentication architecture questions.

Within Milestone 3, the implementation-level mechanism choices explicitly left open by the approved design remain limited to items such as:

- exact abuse-control storage technology,
- exact throttling thresholds,
- exact licensed local blocklist dataset/version and minimal provider-adapter mechanics under DEC-009,
- exact CSRF mechanism that satisfies the approved browser-security outcome,
- deployment-dependent host-only / `__Host-` cookie applicability.

Implementation details belonging to later milestones remain intentionally deferred, including:

- additional Organization lifecycle fields,
- Invitation persistence model,
- Pending-state representation,
- lifecycle/audit representation beyond the approved M2 Membership state,
- active Organization-context storage,
- exact relationship between authenticated global User state and later Organization-context representation,
- exact RLS policies,
- PostgreSQL application roles,
- `FORCE ROW LEVEL SECURITY`,
- database tenant-context mechanism,
- FastAPI middleware/dependency structure for tenant context,
- connection-pool tenant-context handling,
- tenant-scoped transaction mechanics,
- exact same-tenant foreign-key/constraint/trigger technique,
- exact ownership-transfer database enforcement,
- exact Foundation capability catalog,
- exact capability naming convention,
- API `403` versus `404` policy for later tenant/authorization behavior,
- Organization closure implementation,
- retention/purge mechanics,
- billing/subscription mechanics,
- Business Module roles,
- Business Module capability catalogs,
- privileged maintenance tooling,
- production deployment topology,
- CD implementation.

The following authentication features also remain outside Milestone 3 and must not be added merely because authentication now exists:

- password change,
- password reset/recovery,
- email verification,
- MFA,
- social login / enterprise SSO,
- refresh-token infrastructure,
- token rotation infrastructure,
- session/device-management UI,
- logout-all-devices,
- native internationalized/EAI login-email support.

These should be decided only when the relevant milestone or validated requirement requires them.

---

# Architecture Escalation Rule

Implementation must preserve all applicable Founder-accepted decisions, including DEC-001 through DEC-011.

If implementation evidence shows that an accepted decision:

- cannot be implemented safely,
- creates unacceptable one-person maintenance complexity,
- conflicts with another accepted invariant,
- or requires a workaround that weakens security,

the issue must be escalated for architecture review.

Do not silently work around an accepted decision.

---

# Working Process

For each milestone:

```text
Accepted Architecture
        ↓
Current Milestone
        ↓
Technical design / boundary review
        ↓
Founder understands the approach
        ↓
Founder implements
        ↓
Review
        ↓
Automated / adversarial testing
        ↓
Acceptance Criteria satisfied
        ↓
Documentation synchronized
        ↓
Next Milestone
```

The Founder writes implementation code by default.

AI advisory roles support:

- reasoning,
- architecture,
- education,
- review,
- challenge,
- planning,
- risk identification,
- and testing strategy.

---

# Phase 1 Exit Condition

Phase 1 is complete only when:

1. Milestones 1 through 8 satisfy their Acceptance Criteria.
2. All applicable Founder-accepted decisions, including DEC-001 through DEC-011, remain preserved.
3. Global Identity and multi-Organization Membership behavior are validated.
4. Authentication is validated.
5. Trusted Organization-context establishment is validated.
6. Tenant isolation is validated through real PostgreSQL-backed and adversarial testing.
7. Owner/Admin/Member authorization behavior is validated.
8. Membership lifecycle invariants are preserved.
9. Ownership lifecycle invariants are preserved.
10. Historical attribution survives Membership revocation.
11. Foundation security regressions pass in CI.
12. The Foundation has been exercised in a real non-production deployment.
13. Relevant source-of-truth documentation reflects the implemented state.
14. No known unresolved Foundation security issue prevents progression.
15. The first Business Module can begin without redesigning core identity, Membership, ownership, authorization, or tenant-isolation boundaries.
16. All approved customer-facing Foundation workflows are operable through the real browser frontend without Swagger/Postman.
17. Minimum Browser E2E and security-context recovery tests pass against the real Kijflow backend and PostgreSQL-backed state, without replacing existing backend security tests.
18. The core browser journey has been validated in the real non-production deployment, with no known frontend integration defect weakening accepted Foundation security invariants.

Phase 1 completion does not mean Kijflow is production-ready for paying customers.

Production readiness must be established separately before real customer use.