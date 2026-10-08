# Phase 1 Implementation Plan

## Goal

Implement the minimum SaaS Foundation required before the first Business Module.

Phase 1 should establish a foundation that is:

- secure,
- correct,
- understandable,
- maintainable by one person,
- reproducible in development,
- testable continuously,
- and sufficiently deployment-ready to proceed confidently into the first Business Module.

Phase 1 must not become a general-purpose platform or a production-scale DevOps project.

---

## Scope

Phase 1 includes:

- Organization context,
- Authentication,
- User management,
- Minimal authorization / permissions,
- Strong tenant isolation.

Supporting implementation and delivery readiness includes:

- reproducible local development,
- database migrations,
- automated tests,
- minimal continuous integration,
- progressive security regression coverage,
- and a non-production deployment rehearsal before Phase 1 closure.

These delivery concerns support implementation of the accepted SaaS Foundation.

They do not expand the product scope defined by DEC-001.

---

## Non-Goals

Phase 1 does not include:

- Billing / subscription / packaging,
- Business Modules,
- Advanced permission builders,
- Teams / departments,
- Complex approval hierarchies,
- Enterprise SSO,
- Multi-company enterprise capabilities,
- Custom workflow engines,
- Production-scale DevOps infrastructure,
- Kubernetes,
- Infrastructure-as-Code without a validated need,
- High-availability architecture,
- Enterprise observability,
- Automatic production deployment,
- Final production cloud architecture unless required by validated evidence.

---

## Delivery Principle

Infrastructure and delivery readiness should evolve incrementally with the application.

Phase 1 should establish:

- reproducible development,
- continuous integration,
- reliable migration execution,
- security-focused automated testing,
- and basic deployment readiness,

without prematurely introducing production-scale operational complexity.

CI should become stronger as security and application behavior are implemented.

Production deployment architecture and CD policy should be finalized when Kijflow approaches real customer use and sufficient operational requirements are known.

Technology providers such as GitHub Actions, cloud vendors, and deployment platforms are implementation choices rather than architectural requirements unless explicitly accepted later.

---

# Implementation Milestones

## Milestone 1 — Project Bootstrap

### Goal

Create the minimum runnable, reproducible development foundation required for Phase 1 implementation.

### Scope

#### Backend

- FastAPI application.
- Clear application entry point.
- Basic health endpoint.
- PostgreSQL connectivity.
- Migration foundation.
- Backend test foundation.

#### Frontend

- Next.js application.
- Minimum runnable frontend foundation.

No business UI is required.

#### Development Reproducibility

Establish enough repository-controlled configuration that development setup does not depend on configuration remembered only by the Founder.

This includes:

- Git repository,
- dependency definitions,
- environment-variable configuration,
- secret hygiene,
- `.env` development convention,
- example environment configuration where appropriate,
- PostgreSQL development environment,
- Docker Compose for local PostgreSQL where appropriate,
- documented startup and migration commands.

Development reproducibility does not require a one-command development platform.

#### Minimal Continuous Integration

After the local test foundation works, establish minimal CI.

The initial CI responsibility is:

```text
push / pull request
        ↓
setup application dependencies
        ↓
run automated tests
        ↓
pass / fail
```

Once database-backed tests and migrations are ready, CI should also be capable of using a temporary PostgreSQL instance.

CI is a required development capability.

A specific CI provider is an implementation choice.

### Non-Goals

Milestone 1 does not include:

- Organization model,
- User model,
- Registration,
- Authentication,
- Authorization,
- Tenant isolation,
- RLS policies,
- Business Modules,
- Production deployment,
- Production CD,
- Production database architecture,
- Cloud-provider commitment,
- Kubernetes,
- Terraform,
- Monitoring platform,
- Backup architecture,
- Generic repository frameworks,
- Event buses,
- Microservices,
- speculative abstractions.

### Acceptance Criteria

Milestone 1 is complete when:

- the backend runs,
- `GET /health` returns successfully,
- PostgreSQL connectivity works,
- migrations can be applied successfully,
- the backend test suite runs successfully,
- the frontend runs,
- development secrets are not committed to source control,
- required local configuration is documented or represented in the repository,
- a fresh development setup can be reproduced without relying on undocumented configuration,
- minimal CI runs the available automated tests,
- CI reports a clear pass/fail result.

The milestone does not require all later database integration tests to exist yet.

### Relevant Decisions

- DEC-001

---

## Milestone 2 — Organization and User Foundation

### Goal

Implement the minimum Organization/User foundation required by DEC-002 without introducing registration, authentication, or advanced authorization behavior prematurely.

### Scope

Implement the minimum persistent representation required for:

- Organization,
- User,
- one Organization having multiple Users,
- each User belonging to exactly one Organization.

Organization represents both:

- the SME/business using Kijflow,
- and the tenant/data-isolation boundary.

The implementation must make Organization ownership explicit enough for later tenant-isolation enforcement.

Organization membership must be treated as security-sensitive.

Schema changes must be introduced through the migration system established in Milestone 1.

The model may include only the minimum supporting fields required for later Phase 1 milestones.

### Non-Goals

Milestone 2 does not include:

- User registration flow,
- Login,
- Session/token behavior,
- Tenant-context establishment,
- PostgreSQL RLS enforcement,
- Capability evaluation,
- User-management workflows,
- Multi-Organization membership,
- Organization switching,
- Teams,
- Departments,
- multi-company structures,
- Business Module entities.

Moving a User between Organizations is not treated as an ordinary update operation.

### Acceptance Criteria

Milestone 2 is complete when:

- an Organization can be persisted,
- a User can be persisted,
- one Organization can be associated with multiple Users,
- every User belongs to exactly one Organization,
- a User cannot exist in an ambiguous multi-Organization state,
- Organization membership is represented explicitly,
- ordinary model behavior does not treat Organization reassignment as a normal profile update,
- database migrations create the required schema successfully,
- migrations can be executed in a clean development database,
- automated tests verify the essential Organization/User relationship,
- CI executes the relevant tests and migration validation.

### Relevant Decisions

- DEC-001
- DEC-002

---

## Milestone 3 — Registration Bootstrap

### Goal

Provide the trusted bootstrap flow that creates a new Organization together with its first Organization Admin.

### Scope

- Create a new Organization.
- Create the first User for that Organization.
- Assign the first User as Organization Admin through trusted system-controlled logic.
- Ensure Organization and first Admin creation form one valid operation.
- Protect the bootstrap path from arbitrary privilege assignment.

The registration/bootstrap behavior should build on the Organization/User foundation rather than bypass it.

### Non-Goals

- Invitation flow.
- Additional User management.
- Billing or subscription setup.
- Custom roles.
- Custom permissions.
- Organization switching.
- Full Business Module onboarding.

### Acceptance Criteria

Milestone 3 is complete when:

- a new Organization can be created together with its first User,
- the first User belongs to the newly created Organization,
- the first User becomes Organization Admin through trusted system logic,
- arbitrary client input cannot independently grant Admin authority,
- registration cannot leave a partially created Organization/User state,
- failed bootstrap operations leave the system in a valid state,
- relevant automated tests pass,
- CI verifies the registration/bootstrap behavior.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003

---

## Milestone 4 — Authentication

### Goal

Establish a trusted authenticated User identity that later tenant-isolation and authorization decisions can rely on.

### Scope

- User authentication.
- Trusted current-User identity.
- Authentication failure behavior.
- Minimum authenticated-user access required by the Foundation.
- Reliable association between authenticated User and exactly one Organization.

Authentication design should provide the trusted identity required by later tenant-context establishment.

### Non-Goals

- Enterprise SSO.
- Social login.
- Multi-Organization switching.
- Advanced session-management features.
- Business Module authorization.
- Cross-tenant system administration.
- Final production identity infrastructure unless required by the selected implementation.

### Acceptance Criteria

Milestone 4 is complete when:

- a valid User can authenticate,
- invalid authentication is rejected,
- the backend can reliably determine the authenticated User,
- authentication state cannot be established through arbitrary client identity claims,
- the authenticated User can be linked to exactly one Organization according to DEC-002,
- authentication failure does not accidentally establish trusted identity,
- relevant authentication tests run automatically,
- migrations and applicable automated tests continue to pass in CI.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003

---

## Milestone 5 — Tenant Isolation

### Goal

Enforce the Organization boundary established by DEC-002 and DEC-005 before significant tenant-owned functionality is built on top of it.

### Scope

Implement the accepted tenant-isolation architecture:

```text
Trusted identity / system context
        ↓
Trusted Organization context
        ↓
Application / service tenant scoping
        ↓
Effective PostgreSQL RLS
        ↓
Same-tenant relationship integrity
```

This includes:

- trusted Organization context derived from authenticated/system state,
- explicit application/service tenant scoping,
- effective PostgreSQL Row-Level Security for normal tenant-owned relational access,
- fail-closed tenant behavior,
- prevention of cross-tenant reads,
- prevention of cross-tenant writes,
- protection against ID manipulation,
- database execution-context safety,
- minimum same-tenant relationship-integrity enforcement required by the implemented Foundation data model.

Tenant isolation must remain separate from authorization.

Possessing an authorization capability must never expand the tenant boundary.

### Database-Backed Security Testing

Tenant-isolation testing must use a real PostgreSQL environment where PostgreSQL behavior is security-relevant.

CI should provide PostgreSQL-backed integration tests sufficient to exercise:

- RLS behavior,
- tenant context,
- cross-tenant reads,
- cross-tenant writes,
- relevant relationship integrity,
- database execution-context reuse where applicable.

Tests that depend on PostgreSQL security semantics must not be replaced solely by mocks or a different database engine.

### Non-Goals

- Cross-tenant administrative tooling.
- Tenant migration.
- Multi-Organization membership.
- Business Module tenant rules.
- Generic infrastructure for hypothetical future storage systems.
- Final production RLS operational procedures.
- Production maintenance tooling unless required to validate the architecture.

### Acceptance Criteria

Milestone 5 is complete when:

- Organization A cannot read Organization B's tenant-owned data,
- Organization A cannot modify or delete Organization B's tenant-owned data,
- manipulating resource IDs does not cross the tenant boundary,
- missing tenant context fails closed,
- invalid tenant context fails closed,
- conflicting tenant context fails closed,
- untrusted client input cannot establish tenant context,
- Organization Admin does not bypass tenant isolation,
- normal application relational access remains subject to effective PostgreSQL RLS,
- database execution context does not leak tenant identity between tenant-scoped units of work,
- tenant-inconsistent relationships cannot become valid persistent state,
- rejected tenant-inconsistent operations do not leave partially valid state,
- PostgreSQL-backed tenant-isolation tests run in CI,
- cross-tenant regression tests fail if isolation behavior is deliberately broken.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-005

---

## Milestone 6 — Foundation Authorization

### Goal

Implement the minimum capability-oriented authorization required by the SaaS Foundation.

### Scope

Implement:

- Organization Admin profile,
- Member profile,
- Foundation-owned capabilities required by implemented Foundation workflows,
- Kijflow-defined profile-to-capability mappings,
- explicit capability evaluation,
- deterministic authorization outcomes,
- default-deny behavior.

Authorization must remain separate from tenant isolation.

Conceptually:

```text
Authenticated
AND trusted Organization established
AND target resource belongs to that Organization
AND required capability granted
→ operation may proceed
```

Organization Admin must not become a universal authorization bypass.

### CI / Regression Coverage

CI should include authorization regression tests covering:

- explicit grants,
- explicit denials,
- missing mappings,
- unknown capabilities,
- Admin behavior,
- Member behavior,
- interaction between authorization and tenant boundaries.

### Non-Goals

- Custom roles.
- Per-user permission overrides.
- Organization-defined permission mappings.
- Business Module capability catalogs.
- ABAC or general policy engines.
- Advanced permission-builder UI.
- Universal Admin superuser behavior.

### Acceptance Criteria

Milestone 6 is complete when:

- every implemented named Foundation capability has a deterministic result for Admin and Member,
- explicit grant allows access,
- absence of an explicit grant denies access,
- missing capability mapping denies access,
- unknown capability denies access,
- Organization Admin does not receive implicit universal access,
- authorization never expands the tenant boundary,
- authorization behavior is testable independently from authentication and tenant isolation,
- regression tests for Foundation authorization run in CI.

### Relevant Decisions

- DEC-001
- DEC-003
- DEC-004
- DEC-005

---

## Milestone 7 — User Management

### Goal

Allow an Organization to manage its Users safely within the accepted tenant, authentication, and authorization rules.

### Scope

Implement the minimum User-management operations required by Phase 1.

This includes:

- Organization-scoped User access,
- authorized User-management actions,
- Admin/Member profile assignment,
- security-sensitive profile changes,
- active-Admin lifecycle invariants,
- protection against ordinary Organization reassignment.

User-management actions must use the Foundation authorization capabilities established in Milestone 6.

### Admin Lifecycle Invariants

The implementation must preserve the accepted rules that:

- a live Organization with active Users must retain at least one active Organization Admin,
- a User cannot self-promote through an ordinary User update,
- demoting the final active Admin must fail,
- disabling the final active Admin must fail,
- removing the final active Admin must fail,
- self-demotion is allowed only when another active Admin remains,
- concurrent privileged changes must not result in zero active Admins.

### CI / Regression Coverage

CI should include User-management and lifecycle regression tests covering:

- Admin actions,
- Member restrictions,
- cross-tenant attempts,
- profile changes,
- last-Admin protection,
- concurrent privileged operations where relevant.

### Non-Goals

- Teams.
- Departments.
- Custom roles.
- Per-user permission overrides.
- Moving Users between Organizations as an ordinary operation.
- Billing-per-user behavior.
- Advanced invitation/onboarding workflows unless required for the minimum Foundation workflow.
- Multi-Organization accounts.

### Acceptance Criteria

Milestone 7 is complete when:

- authorized Organization Admins can perform the supported User-management actions within their own Organization,
- Members cannot perform privileged User-management actions unless explicitly granted by Foundation capability policy,
- Users from another Organization cannot be viewed or modified,
- ordinary profile editing cannot self-promote a User to Admin,
- removing the final active Admin is rejected,
- disabling the final active Admin is rejected,
- demoting the final active Admin is rejected,
- self-demotion is rejected when no other active Admin remains,
- concurrent privileged changes cannot leave an active Organization with zero active Admins,
- Organization membership cannot be reassigned through ordinary User updates,
- User-management security regressions run automatically in CI.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-004
- DEC-005

---

## Milestone 8 — Phase 1 Security and QA Closure

### Goal

Verify that the SaaS Foundation satisfies the accepted Phase 1 requirements and demonstrate basic deployment readiness before beginning the first Business Module.

### Scope

#### Foundation Validation

- Authentication validation.
- Authorization validation.
- Tenant-isolation adversarial testing.
- User-management lifecycle testing.
- Failure-path testing.
- Phase 1 regression coverage.
- Documentation/status synchronization.

#### Deployment Readiness

Review whether the Foundation can operate outside the Founder's local development environment.

Validate at minimum:

- application configuration,
- environment-variable handling,
- secrets handling,
- process startup,
- database connectivity,
- migration execution,
- health-check behavior.

#### Non-Production Deployment Rehearsal

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
relevant validation succeeds
```

The purpose is to expose environment-specific problems that may not appear during local development.

#### Provider Evaluation

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

Phase 1 does not require a permanent production-provider commitment if available evidence is insufficient.

### Non-Goals

- Sales Management testing.
- Performance optimization without evidence of a problem.
- Enterprise-scale load testing.
- Future Business Module architecture.
- Production customer launch.
- Production auto-CD.
- High-availability infrastructure.
- Kubernetes.
- Full observability platform.
- Final production backup policy.
- Final production topology unless sufficient requirements exist.
- Forced cloud/provider commitment solely to close Phase 1.

### Acceptance Criteria

Phase 1 must demonstrate that:

- a User can authenticate,
- the system determines the User's trusted Organization context,
- different authorization profiles can produce different authorization outcomes,
- unauthorized actions are denied,
- cross-tenant reads are denied,
- cross-tenant writes are denied,
- ID manipulation does not bypass tenant isolation,
- Organization Admin cannot cross tenant boundaries,
- tenant-isolation failures fail closed,
- the final active Admin invariant is preserved,
- Foundation security regressions run successfully in CI,
- the Foundation can support the first Business Module without redesigning its core tenant/authentication/authorization boundaries.

Deployment readiness must additionally demonstrate that:

- Kijflow can be deployed to at least one real non-production environment,
- runtime configuration works outside the local machine,
- secrets can be supplied safely,
- the application can connect to the non-production PostgreSQL environment,
- migrations can execute successfully,
- the application starts successfully,
- the health check succeeds,
- major environment-specific failures discovered during rehearsal are either resolved or explicitly documented before Phase 1 closure.

All relevant Phase 1 documentation must reflect the implemented state before the milestone is considered complete.

### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-004
- DEC-005

---

# CI Evolution Through Phase 1

CI should evolve with the application rather than being designed as a complete platform in Milestone 1.

Expected progression:

```text
Milestone 1
Basic automated tests
        ↓
Migration validation

Milestone 2–4
Organization/User tests
Registration tests
Authentication tests
Migration checks
        ↓

Milestone 5
Real PostgreSQL-backed
tenant / RLS integration tests
        ↓

Milestone 6
Authorization regression tests
        ↓

Milestone 7
User-management and Admin-lifecycle
regression tests
        ↓

Milestone 8
Complete Phase 1
security / regression validation
```

CI should remain understandable and maintainable by the Founder.

Additional CI complexity should be introduced only when it protects meaningful application behavior.

---

# Before Real Customer Use

Phase 1 deployment readiness is not equivalent to production readiness.

Before Kijflow is used by real customers, the production operating model must be reviewed and the required production decisions must be made.

At minimum, evaluate and finalize as appropriate:

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

The final CD approach should be selected based on the actual operational risk of Kijflow at that time.

---

# Implementation Discipline

The milestones define implementation sequence and completion boundaries.

They do not pre-decide every implementation mechanism.

Details should be designed when the relevant milestone is reached.

Examples of intentionally deferred implementation decisions include:

- exact authentication/session representation,
- exact RLS policies,
- PostgreSQL roles,
- `FORCE ROW LEVEL SECURITY`,
- database tenant-context mechanism,
- FastAPI middleware design,
- connection-pool mechanics,
- transaction mechanics,
- exact Organization/User schema details beyond accepted invariants,
- foreign-key / constraint / trigger techniques,
- privileged maintenance tooling,
- production deployment topology,
- CD implementation.

Implementation decisions must preserve DEC-001 through DEC-005.

If implementation evidence shows that an accepted architectural decision cannot be implemented safely or maintainably, the issue should be escalated for architectural review rather than silently worked around.

---

# Working Process

For each milestone:

```text
Implementation Plan
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

Only the current milestone should be designed in implementation-level detail.

Later milestones should remain high-level until they become current.

This prevents implementation planning from turning back into speculative architecture design.

---

# Phase 1 Exit Condition

Phase 1 is complete only when:

1. Milestones 1 through 8 satisfy their Acceptance Criteria.
2. DEC-001 through DEC-005 remain preserved by the implementation.
3. Authentication, authorization, and tenant isolation have been validated through relevant automated and adversarial testing.
4. The Foundation has been exercised in a real non-production deployment.
5. Relevant project documentation reflects the implemented state.
6. No known unresolved Phase 1 security issue prevents safe progression.
7. The Foundation is sufficiently stable to begin the first Business Module without redesigning its core tenant, identity, authorization, or isolation boundaries.

Phase 1 completion does not mean Kijflow is production-ready for paying customers.

Production readiness must be established before real customer use.