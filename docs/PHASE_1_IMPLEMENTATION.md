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

### Goal

Establish global User self-service registration and trusted authenticated User Identity.

### Scope

Implement:

- self-service User registration,
- secure credential establishment,
- authentication,
- trusted current-User identity,
- authentication failure behavior,
- minimum authenticated Foundation behavior.

Registration creates a global User Identity.

Organization creation belongs to Milestone 4.

A User with zero usable Memberships is a valid Foundation state.

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

### Security Requirements

- User establishes their own credentials.
- Arbitrary client identity claims cannot establish authenticated identity.
- Authentication must not imply Membership in any Organization.
- Authentication must not automatically establish tenant context.
- Global User Identity must remain separate from Organization authority.

### Non-Goals

- Social login
- Enterprise SSO
- advanced session-management features
- Organization invitation acceptance
- full Organization switching
- tenant-isolation enforcement
- Business Module authorization
- billing/subscription onboarding

### Acceptance Criteria

Milestone 3 is complete when:

- a new User can register a global Identity,
- registration does not require an existing Organization,
- credentials are established securely through the User's own flow,
- a valid User can authenticate,
- invalid authentication is rejected,
- backend can reliably determine the authenticated User,
- arbitrary client claims cannot establish another User's identity,
- authentication remains independent from Organization membership,
- a User with zero Memberships can remain a valid authenticated identity,
- relevant automated tests run in CI.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003

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

The approved Milestone 2 persistence subset is defined in the Milestone 2 implementation-level design above.

Implementation details belonging to later milestones remain intentionally deferred, including:

- authentication-specific User fields,
- additional Organization lifecycle fields,
- Invitation persistence model,
- Pending-state representation,
- lifecycle/audit representation beyond the approved M2 Membership state,
- active Organization-context storage,
- JWT versus other session representation,
- exact authentication-token mechanics,
- exact RLS policies,
- PostgreSQL application roles,
- `FORCE ROW LEVEL SECURITY`,
- database tenant-context mechanism,
- FastAPI middleware/dependency structure,
- connection-pool context handling,
- transaction mechanics,
- exact same-tenant foreign-key/constraint/trigger technique,
- exact ownership-transfer database enforcement,
- exact Foundation capability catalog,
- exact capability naming convention,
- API `403` versus `404` policy,
- Organization closure implementation,
- retention/purge mechanics,
- billing/subscription mechanics,
- Business Module roles,
- Business Module capability catalogs,
- privileged maintenance tooling,
- production deployment topology,
- CD implementation.

These should be decided only when the relevant milestone or validated requirement requires them.

---

# Architecture Escalation Rule

Implementation must preserve DEC-001 through DEC-005.

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