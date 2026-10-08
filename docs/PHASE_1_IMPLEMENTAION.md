# Phase 1 Implementation Plan

## Goal

Implement the minimum SaaS Foundation required before the first Business Module.

## Scope

- Organization context
- Authentication
- User management
- Minimal authorization / permissions
- Strong tenant isolation

## Non-Goals

- Billing / subscription / packaging
- Business Modules
- Advanced permissions
- Teams / departments
- Enterprise features

## Implementation Milestones

### Milestone 1 — Project Bootstrap

Goal:
Create the minimum runnable development foundation.

Includes:
- FastAPI backend
- PostgreSQL connection
- migrations
- backend test foundation
- Next.js frontend

Acceptance Criteria:
- backend runs
- `/health` returns successfully
- PostgreSQL connection works
- migrations work
- tests run
- frontend runs

Relevant Decisions:
- DEC-001

---

### Milestone 2 — Organization and User Foundation

Goal:
Implement the minimum Organization/User model defined by DEC-002.

Acceptance Criteria:
...

Relevant Decisions:
- DEC-002

### Milestone 3 — Registration Bootstrap

#### Goal

Provide the trusted bootstrap flow that creates a new Organization together with its first Organization Admin.

#### Scope

- Create a new Organization.
- Create the first User for that Organization.
- Assign the first User as Organization Admin through trusted system-controlled logic.
- Ensure Organization and first Admin creation form one valid operation.

#### Non-Goals

- Invitation flow.
- Additional User creation.
- Billing or subscription setup.
- Custom roles or permissions.
- Organization switching.

#### Acceptance Criteria

- A new Organization can be created with its first User.
- The first User belongs to the newly created Organization.
- The first User becomes Organization Admin through trusted system logic.
- Client input alone cannot grant Admin authority.
- Registration cannot leave a partially created Organization/User state.

#### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003

---

### Milestone 4 — Authentication

#### Goal

Establish a trusted authenticated User identity that later tenant-isolation and authorization decisions can rely on.

#### Scope

- User authentication.
- Trusted current-User identity.
- Authentication failure behavior.
- Minimum authenticated-user access required by the Foundation.

#### Non-Goals

- Enterprise SSO.
- Social login.
- Multi-Organization switching.
- Advanced session-management features.
- Business Module authorization.

#### Acceptance Criteria

- A valid User can authenticate.
- Invalid authentication is rejected.
- The backend can reliably determine the authenticated User.
- Authentication state cannot be established through arbitrary client identity claims.
- The authenticated User can be linked to exactly one Organization according to DEC-002.

#### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003

---

### Milestone 5 — Tenant Isolation

#### Goal

Enforce the Organization boundary established by DEC-002 and DEC-005 before significant tenant-owned functionality is built on top of it.

#### Scope

- Trusted Organization context derived from authenticated/system state.
- Explicit application/service tenant scoping.
- Effective PostgreSQL Row-Level Security for normal tenant-owned relational access.
- Fail-closed tenant behavior.
- Prevention of cross-tenant reads and writes.
- Minimum same-tenant relationship-integrity mechanism required by the implemented Foundation data model.

#### Non-Goals

- Cross-tenant administrative tooling.
- Tenant migration.
- Multi-Organization membership.
- Business Module tenant rules.
- Generic infrastructure for hypothetical future storage systems.

#### Acceptance Criteria

- Organization A cannot read Organization B's tenant-owned data.
- Organization A cannot modify or delete Organization B's tenant-owned data.
- Manipulating resource IDs does not cross the tenant boundary.
- Missing or invalid trusted tenant context fails closed.
- Organization Admin does not bypass tenant isolation.
- Normal application relational access remains subject to effective RLS.
- Database execution context does not leak tenant identity between units of work.
- Tenant-inconsistent relationships cannot become valid persistent state.

#### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-005

---

### Milestone 6 — Foundation Authorization

#### Goal

Implement the minimum capability-oriented authorization required by the SaaS Foundation.

#### Scope

- Organization Admin and Member authorization profiles.
- Foundation-owned capabilities required by implemented Foundation workflows.
- Kijflow-defined profile-to-capability mappings.
- Explicit capability evaluation.
- Default-deny behavior.

#### Non-Goals

- Custom roles.
- Per-user permission overrides.
- Organization-defined permission mappings.
- Business Module capability catalogs.
- ABAC or policy engines.
- Advanced permission-builder UI.

#### Acceptance Criteria

- Every implemented named Foundation capability has a deterministic result for Admin and Member.
- Explicit grant allows access.
- Missing or unknown capability mapping denies access.
- Organization Admin does not receive implicit universal access.
- Authorization never expands the tenant boundary.
- Authorization behavior is testable independently from authentication and tenant isolation.

#### Relevant Decisions

- DEC-001
- DEC-003
- DEC-004
- DEC-005

---

### Milestone 7 — User Management

#### Goal

Allow an Organization to manage its Users safely within the accepted tenant and authorization rules.

#### Scope

- Minimum User-management operations required by Phase 1.
- Organization-scoped User access.
- Admin/Member profile assignment and authorized profile changes.
- Active-Admin lifecycle invariants.

#### Non-Goals

- Teams or Departments.
- Custom roles.
- Per-user permission overrides.
- Moving Users between Organizations as an ordinary operation.
- Billing-per-user behavior.
- Advanced invitation/onboarding workflows unless required for the minimum Foundation flow.

#### Acceptance Criteria

- Authorized Organization Admins can perform the supported User-management actions within their own Organization.
- Members cannot perform privileged User-management actions unless explicitly granted by Foundation capability policy.
- Users from another Organization cannot be viewed or modified.
- Ordinary profile editing cannot self-promote a User to Admin.
- Removing, disabling, or demoting the final active Admin is rejected.
- Concurrent privileged changes cannot leave an active Organization with zero active Admins.
- Organization membership cannot be reassigned through ordinary User updates.

#### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-004
- DEC-005

---

### Milestone 8 — Phase 1 Security and QA Closure

#### Goal

Verify that the SaaS Foundation satisfies the accepted Phase 1 requirements before beginning the first Business Module.

#### Scope

- Authentication validation.
- Authorization validation.
- Tenant-isolation adversarial testing.
- User-management lifecycle testing.
- Failure-path testing.
- Phase 1 regression coverage.
- Documentation/status synchronization.

#### Non-Goals

- Sales Management testing.
- Performance optimization without evidence of a problem.
- Enterprise-scale load testing.
- Future Business Module architecture.

#### Acceptance Criteria

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
- the Foundation can support the first Business Module without redesigning its core tenant/authentication/authorization boundaries.

All relevant Phase 1 documentation must reflect the implemented state before the milestone is considered complete.

#### Relevant Decisions

- DEC-001
- DEC-002
- DEC-003
- DEC-004
- DEC-005