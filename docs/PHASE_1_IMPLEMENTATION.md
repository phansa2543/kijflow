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

Before Milestone 2 implementation began, the Foundation architecture was re-evaluated against Founder-approved Product Directions.

The revised Phase 1 architecture establishes:

- global Kijflow User Identity,
- multi-Organization Membership,
- Organization as the tenant/data-isolation boundary,
- Owner / Admin / Member Foundation profiles,
- self-service registration,
- self-service Organization creation,
- Membership lifecycle,
- Organization ownership lifecycle,
- capability-oriented authorization,
- and revised tenant-context rules for multi-Organization Membership.

The revised architecture is defined by DEC-001 through DEC-005.

Implementation must proceed from the revised architecture rather than the superseded one-User/one-Organization model.

Milestone 2 — Identity / Organization / Membership Foundation is complete.

Milestone 3 — Registration & Authentication is the current milestone.

The Milestone 3 authentication persistence foundation and email canonicalization/validation component have been implemented and tested locally.

The latest full backend regression test run passed 64 tests, including 29 email canonicalization tests.

Registration, login, remaining password processing, and runtime authentication/session workflows remain incomplete.

The Milestone 3 implementation-level technical design has been:

- completed by the Tech Lead / Software Architect,
- challenged and revised through QA review,
- given final QA PASS,
- reviewed with the Founder by the Engineering Mentor,
- and explicitly approved by the Founder.

Founder implementation is now the current Milestone 3 step.

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

Founder implementation is now the current step.

#### Implementation Progress

**Authentication Persistence Foundation — Implemented**

- Implemented password-credential and authentication-session persistence models and Alembic migration.
- Added PostgreSQL-backed persistence invariant tests.
- Registration, login, and runtime session workflows are not yet implemented.

**Email Canonicalization & Validation — Implemented and Tested Locally**

- Implemented `canonicalize_email()` in `backend/app/auth/email.py`.
- Uses compiled Python Regex and explicit Python validation.
- Supports the selected conventional ASCII dot-atom local-part syntax and hostname-style domain labels.
- Trims surrounding whitespace and lowercases both local part and domain.
- Preserves dots and plus tags without provider-specific rewriting.
- Rejects invalid syntax and unsupported Non-ASCII/EAI email addresses.
- Validates length limits: 64 characters for local part, 63 per domain label, and 254 for the complete email address.
- Added 29 automated tests in `backend/tests/test_email.py`.
- Full backend regression suite: 59 tests passed locally.
- Email canonicalization changes passed GitHub Actions CI on commit `d438bea`, as confirmed by the Founder.

**Password NFC Normalization — Implemented and Tested Locally**

- Implemented `normalize_password()` in `backend/app/auth/password.py`.
- Uses Python `unicodedata.normalize("NFC", raw_password)`.
- Preserves leading/trailing whitespace and case sensitivity.
- Supports Unicode passwords, including Thai characters.
- Added `backend/tests/test_password.py` with 5 automated tests covering whitespace preservation, Unicode NFC equivalence, case sensitivity, Thai characters, and idempotence.
- Latest password normalization test run: 5 passed locally.
- Latest full backend regression run: 64 passed locally.
- Password length/policy validation, blocklist checks, Argon2id hashing, and verification remain incomplete.
- CI validation for this new password normalization work has not yet been confirmed.

**Remaining M3 Work**

- Password length/policy validation, common/compromised-password screening, Argon2id hashing and verification
- Atomic user registration
- Login and authentication failure handling
- Server-side session issuance, validation, and logout
- Authentication abuse protection
- Cookie security, CSRF protection, and remaining security tests

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

The Founder has approved the following implementation-level Registration & Authentication design for Milestone 3.

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

- minimum length is 15 Unicode code points,
- maximum length is 128 Unicode code points,
- over-maximum input is rejected,
- silent truncation is forbidden,
- Unicode and spaces are allowed.

Password establishment must reject passwords identified by the approved policy as:

- common,
- known-compromised.

An external breach-service integration is not required for Milestone 3.

The exact local/versioned dataset or suitable established dependency remains an implementation choice as long as the approved security outcome is met.

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
- exact password blocklist dataset/dependency,
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
- minimum-length boundary,
- maximum-length boundary,
- over-maximum rejection,
- no silent truncation,
- leading/trailing whitespace preserved,
- deterministic Unicode NFC behavior,
- canonically equivalent Unicode password verifies consistently,
- same plaintext password produces independently salted Argon2 representations.

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
- password processing follows the approved NFC / length / blocklist / Argon2id policy,
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
- implementation remains within the accepted M3 boundary and preserves DEC-001 through DEC-005.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-005

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
- Creator becomes Owner through trusted system-controlled behavior.
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

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-005

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

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-005

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

### Relevant Decisions

- DEC-001
- DEC-003
- DEC-004
- DEC-005

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

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-004
- DEC-005

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

All relevant Phase 1 source-of-truth documentation must reflect the implemented state before closure.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-004
- DEC-005

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
- exact password blocklist dataset/dependency,
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

Implementation must preserve DEC-001 through DEC-006.

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
2. Revised DEC-001 through DEC-005 remain preserved.
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

Phase 1 completion does not mean Kijflow is production-ready for paying customers.

Production readiness must be established separately before real customer use.