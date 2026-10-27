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

### M3 Same-Origin Next.js Rewrite/Proxy — 2026-10-24 (Founder Closure)

**Status: CLOSED — Independent QA PASS / Founder APPROVED. Accepted implementation commit `ed75f6320ea13b50e9dff75bf3c4ae1cb2cdce92`. M3 Browser Authentication Integration and M3 overall remain OPEN / IN PROGRESS.**

- Development topology: Browser `http://localhost:3000` → Next.js rewrite of `/auth/:path` → FastAPI `http://127.0.0.1:8000`; `TRUSTED_FRONTEND_ORIGIN=http://localhost:3000`. This is not a production deployment topology decision.
- GitHub Actions run https://github.com/phansa2543/kijflow/actions/runs/40079051775 **SUCCESS** at accepted commit. Changes limited to `frontend/next.config.ts`, `frontend/package.json` and `frontend/package-lock.json`. Independent QA PASS accepted the focused source/framework review and Founder-reported browser evidence, with no confirmed blocker for this development slice.
- Backend Cookie/CSRF Security remains CLOSED; Origin validation, authoritative PostgreSQL session behavior and HttpOnly/Secure/SameSite=Lax/Path=/ cookie contract were not changed.
- **Open browser follow-up:** minimum real Next.js Registration/Login/Logout UI; authenticated pre-tenant state; session expiry/recovery; automated frontend build and browser regression; adversarial real-browser CSRF checks. Browser security and M3 have **not** received final acceptance.
- Non-blocking follow-ups: CI currently validates backend but not `npm ci` / `npm run build`; Next.js proxy can collapse backend SOURCE network identity to proxy/loopback for shared/deployed topologies (never blindly trust `X-Forwarded-For`); Safari may not honor Secure cookie on HTTP localhost; `eslint-config-next` is 16.4.0 while runtime Next.js is 16.4.3. Revisit in their applicable M3 integration / deployment-maintenance gates, not by reopening this closed slice.
- Other session-related Independent QA and Password Screening Technical Security remain pending unless accepted separately. Step 6 and Registration Cleanup B2 stay CLOSED. No M4 or speculative infrastructure.

### Cookie / CSRF Backend Security — 2026-10-24 (Founder Closure)

**Status: CLOSED — Independent Security QA PASS / Founder APPROVED. Accepted implementation baseline `aee8453e7efeab7c51d21894b1d1932e82fd222d`. M3 remains IN PROGRESS.**

- Strict trusted Origin validation on `POST /auth/register`, `POST /auth/login` and `POST /auth/logout` rejects untrusted/missing/null/duplicate Origin before the authentication handlers. Backend cross-site Login/Registration persistence-negative tests and Logout session-preservation tests were accepted by Independent QA.
- PostgreSQL SOURCE abuse-counter accounting on CSRF rejection was independently reviewed and accepted; missing/invalid `TRUSTED_FRONTEND_ORIGIN` fails startup before engine creation. Required backend session-cookie contract: HttpOnly, Secure, SameSite=Lax, Path=/.
- Implementation `0d5816c342937b04586b18fda846ed15a3bc30d3`, test configuration CI remediation `52ce266835868ea6a4ab0958cb456cd16ff4cf50` and focused security regression `aee8453e7efeab7c51d21894b1d1932e82fd222d`. GitHub Actions https://github.com/phansa2543/kijflow/actions/runs/40073114863 **SUCCESS** on accepted baseline; Founder-reported local regression **447 passed, 1 skipped**.
- Historical Login SOURCE counter discrepancy was not reproducible on the accepted baseline; no verified production defect was established. No need to reopen CLOSED Step 6 Login Abuse Protection or Registration Counter Cleanup B2.
- **Closure boundary:** backend Cookie/CSRF Security only. **OPEN:** Next.js Same-Origin Rewrite/Proxy, real-browser registration/login/logout, browser cookies, Origin forwarding and browser CSRF/security regression, authenticated pre-tenant state and session expiry/recovery. Do not claim M3 or browser acceptance.
- **Approved M3 development direction (not production topology):** Browser `http://localhost:3000` → Next.js same-origin rewrite/proxy → FastAPI `http://127.0.0.1:8000`; `TRUSTED_FRONTEND_ORIGIN=http://localhost:3000`. Browser integration must verify actual Origin/Cookie/Set-Cookie handling and Secure cookie behavior on localhost.
- Session Lifetime, Session Validation Persistence, Raw Token/Resolution, Trusted Current-User HTTP Dependency, Logout/Revocation and Password Screening Technical Security retain their respective Independent QA gates unless separately accepted. AQ-014/AQ-016 pre-external-use gates unchanged; no M4 or additional architecture.

### Current-session Logout / Server-side Revocation — 2026-10-24

**Status: Founder-implemented / pushed / GitHub CI SUCCESS / Independent QA PENDING — NOT CLOSED. M3 remains IN PROGRESS.**

- GitHub `main` exact implementation commit `b6ff4007600efa16aa8edbf0fc6d183b3c8eb1df` (`feat(auth): implement current-session logout and revocation`); GitHub Actions https://github.com/phansa2543/kijflow/actions/runs/40056785711 **SUCCESS** at the exact SHA.
- Founder implemented PostgreSQL current-session revocation (`revoke_current_session`), raw-token revocation (`revoke_session_by_raw_token`) and `POST /auth/logout` using the authoritative session-cookie/token digest path. An eligible current Session is revoked transactionally before a successful Logout response clears its cookie; other concurrent Sessions remain valid. Invalid/expired/revoked tokens return HTTP 401; database failures return HTTP 503. This implementation still needs independent QA verification.
- Founder-reported focused results: Session Persistence **9 passed**, Session Resolution **18 passed**, Logout HTTP **10 passed**; full local backend regression **380 passed, 1 skipped**. These are local evidence, not Independent QA acceptance.
- **Pending QA:** Session Lifetime (`a378230`), Session Validation Persistence (`5a36cc2`), Raw Session Token Validation/Resolution (`f1ca0cc`), Trusted Current-User HTTP Dependency (`f742d4f`), this Logout/Revocation slice (`b6ff400`) and independent Password Screening technical security.
- **Next authorized M3 task:** Cookie / CSRF Security. Validate all state-changing browser authentication entry points (registration, login, logout) against untrusted cross-site requests; maintain secure HttpOnly, Secure, SameSite=Lax, Path=/ cookie contract. SameSite alone is insufficient. Test safe Origin/CSRF policy against intended Next.js/FastAPI deployment topology and avoid new infrastructure or expanding architecture.
- **Still pending:** Next.js Registration/Login/Logout and pre-tenant UI, browser session expiry/recovery, browser integration and final M3 QA. Login Abuse Protection Step 6 and Registration Counter Cleanup B2 remain CLOSED. AQ-014/AQ-016 external-release gates unchanged.

### Trusted Current-User HTTP Dependency — 2026-10-24

**Status: Founder-implemented / pushed / GitHub CI SUCCESS / Independent QA PENDING — NOT CLOSED. M3 remains IN PROGRESS.**

- Exact implementation commit `f742d4f1386ef63395cdc215ab4f126beb17d5e8` (`feat(auth): add trusted current-user HTTP dependency`) is on GitHub `main`. GitHub Actions run https://github.com/phansa2543/kijflow/actions/runs/40055301574 completed **SUCCESS** at that exact head SHA.
- `backend/app/auth/presentation/current_user.py` introduces `require_current_user_id(request: Request) -> UUID` and the authentication-cookie-only path to global User ID through existing authoritative PostgreSQL Session Resolution. Invalid authentication produces HTTP 401, and authoritative persistence unavailability is surfaced as HTTP 503. No client body/query/header identity claim can override the session-based User.
- Founder-reported local focused HTTP integration: **10 passed**. Founder-reported full backend regression: **360 passed, 1 skipped**. These results and CI success do not constitute Independent QA acceptance.
- Independent QA remains **PENDING** for Session Lifetime (`a378230`), Session Validation Persistence (`5a36cc2`), Raw Session Token Validation and Session Resolution (`f1ca0cc`), and this HTTP dependency (`f742d4f`). Password Screening independent technical-security acceptance also remains pending.
- **Next authorized M3 slice:** Current-session Logout / Server-side Revocation. Reuse the authoritative PostgreSQL Session model. Successful logout must revoke only the current Session and render its original raw token unusable; cookie deletion alone is insufficient. Other concurrent Sessions for the same User must remain valid. Include PostgreSQL and HTTP/security regression, fail-closed behavior and cookie/CSRF review within the accepted M3 contract.
- Registration Cleanup B2 and Step 6 Login Abuse Protection remain CLOSED. Do not introduce M4, new session frameworks, Redis, JWT, refresh tokens, or unrelated authentication scope.

### Raw Session Token Validation and Session Resolution — 2026-10-24

**Status: Founder-implemented / pushed / GitHub CI SUCCESS / Independent QA PENDING. NOT CLOSED. M3 remains IN PROGRESS.**

- Exact implementation commit on `main`: `f1ca0cc5a9f2c1b4ab975452e9072a91b8b94eb1` (`feat(auth): resolve authenticated user from session token`). GitHub Actions run https://github.com/phansa2543/kijflow/actions/runs/40054387449 **SUCCESS** at that same commit.
- `backend/app/auth/infrastructure/session_token.py` introduces raw token format validation, rejecting missing, malformed, incorrect-type and oversized values; the existing session SHA-256 digest function is reused.
- `backend/app/auth/infrastructure/session_resolution.py` resolves a validated raw token through SHA-256 digest and authoritative PostgreSQL session lookup into global User ID or `None`. This is **infrastructure-level** resolution; FastAPI cookie extraction and trusted current-User HTTP dependency are **not implemented by this slice**.
- Founder-reported local verification: **17 token tests passed**, **11 resolver integration tests passed**, **350 passed, 1 skipped** full backend regression. Local counts are not independent QA evidence.
- Test setup corrections address isolated startup-secret configuration and revoked-session timestamp constraints. No database schema migration or new infrastructure was introduced.
- **Next Engineering Mentor task authorized:** inspect current code and implement Trusted Current-User HTTP Dependency using exclusively the authentication cookie, the existing resolver, fail-closed behavior for invalid/expired/revoked sessions and tests preventing client-supplied identity override.
- Independent QA reviews remain pending for Session Lifetime, Session Validation Persistence and this new raw-token/resolution slice. Do not mark these subtasks CLOSED until their acceptance gates are satisfied.

### Session Validation Persistence — 2026-10-23 (CI Verified; QA Pending)

**Status:** Founder implemented and pushed Session Validation Persistence at GitHub `main` commit `5a36cc274ddb3c9b653ef114c8a0b9f30e1b1a58` (`feat(auth): validate active sessions`). GitHub Actions run https://github.com/phansa2543/kijflow/actions/runs/39972021451 completed **SUCCESS** at that exact commit. **Independent QA acceptance PENDING; do not mark this subtask CLOSED. M3 remains IN PROGRESS.**

- `backend/app/auth/infrastructure/session_persistence.py` implements `find_valid_session_user_id(connection, *, token_digest) -> UUID | None`. The lookup verifies matching token digest, non-expired and non-revoked session, and existing referenced User via an INNER JOIN. Unknown/invalid session returns `None`. This is digest-level persistence validation, **not** raw cookie/token validation or Trusted Current-User Resolution.
- `backend/tests/test_session_persistence.py` includes six focused cases covering valid, expired, revoked, unknown-digest, referenced-User foreign-key and multiple-session independence behavior. Founder reports **6 focused tests passed** and **325 passed, 1 skipped** in local full regression. These counts are Founder-reported, not independent QA sign-off.
- **Parallel QA assignments requested:** independent focused reviews for Session Validation Persistence at the exact reviewed commit and the previous Session Lifetime change at `a37823064e490e444a4b2e39c5171ebea433061e`. CI success for either does not close its acceptance gate.
- **Configuration follow-up resolved by source inspection:** root `.env.example` contains `SESSION_LIFETIME_SECONDS=86400`; no change required for this example entry.
- **Authorized next slice:** Raw Session Token validation and SHA-256 digest resolution, then Trusted Global Current-User Resolution and fail-closed tests. Continue logout/revocation, cookie/CSRF and Next.js integration within existing M3 acceptance criteria. No M4 or new framework/infrastructure.
- Step 6 Login Abuse Protection and Registration Cleanup B2 remain CLOSED.

### Session Lifetime Implementation — 2026-10-23 (Verification Pending Independent QA)

**Status: Founder-implemented, pushed and GitHub CI-confirmed; independent Session Lifetime QA/acceptance PENDING.** This checkpoint is newer than the Step 6 closure snapshot below; **M3 remains IN PROGRESS**.

- Latest reviewed source on GitHub `main`: `a37823064e490e444a4b2e39c5171ebea433061e` (`fix(auth): configure consistent session lifetime`). GitHub Actions run https://github.com/phansa2543/kijflow/actions/runs/39960308775 completed **SUCCESS** at that exact head SHA.
- `SESSION_LIFETIME_SECONDS` is a validated positive-integer runtime setting, initially **86400 seconds (24 hours)**. Login applies the configured duration to persisted Session expiry and the cookie `max_age`; invalid configuration fails startup before database-engine creation. These implementation statements are supported by the pushed source and tests, but are **not independent QA acceptance**.
- Founder-reported local evidence: **6 session-lifetime tests passed**; full backend regression **321 passed, 1 skipped**. This full-suite count is Founder-reported and is not substituted for an independent QA review.
- **Documentation/reproducibility follow-up:** the latest root `.env.example` was inspected and does **not** list `SESSION_LIFETIME_SECONDS`, contrary to the Engineer Mentor handoff. Verify/add this optional runtime setting to the example and relevant setup guidance, with no secret value.
- **Next:** Engineering Mentor to obtain focused review of Session Lifetime and configuration example, then proceed within approved M3 scope to **Session Validation / Expiration**, trusted current-User resolution, current-session logout/revocation, browser cookie/CSRF integration and required regression/security QA. Do not mark Session Lifetime formally CLOSED until its applicable acceptance gate passes.
- Step 6 Login Abuse Protection and Registration Counter Cleanup B2 remain CLOSED; no M4 or unrelated infrastructure work.

### Current M3 Progress — 2026-10-23 (Step 6 Founder Closure)

**Step 6 — Login Abuse Protection: CLOSED — Founder Approved.** Independent QA focused delta review **PASS** on exact GitHub `main` commit `b7aac2eae0b8bbf8f163992e2f3eda9f62f4d952`; corresponding GitHub Actions https://github.com/phansa2543/kijflow/actions/runs/39890237054 **SUCCESS — 315 passed, 1 skipped**. Founder explicitly authorized Step 6 closure on 2026-10-23. **M3 remains IN PROGRESS**; this closure is only for Step 6.

- PostgreSQL-backed Login `SOURCE` and `ACCOUNT` throttling is implemented, with independently committed reservations, fail-closed persistence, HMAC-SHA256 account keys, generic known/unknown failure handling, successful-session ACCOUNT reservation release and separate Login counter cleanup.
- Default thresholds are SOURCE **30 attempts/60 seconds** and ACCOUNT **10 attempts/900 seconds**, now adjustable using validated positive runtime configuration.
- **F1, F2, F3: RESOLVED.** Test DB isolation protects against alternate URL spellings; exact pushed source was independently reviewed; PostgreSQL `SKIP LOCKED` test confirms locked-row skipping and subsequent deletion after unlock. The original 47 passed was Founder-reported local evidence, not independent acceptance.
- **B1, B2, B3: RESOLVED / QA PASS.** Root `.env` loads before secret and limiter configuration validation and before database engine creation; missing/invalid HMAC secret fails closed; database engine creates/disposes exactly once. Rate thresholds/windows load from runtime settings and are exercised in HTTP tests. Adversarial repeated known/unknown account attempts produce equivalent 401 through attempts 1–10 and 429 on attempt 11, without session issuance or account-enumeration disclosure.
- **No remaining Step 6 blockers.** The QA PASS is limited to Step 6 and is not final M3 Session, browser/CSRF, Password Screening, or full M3 acceptance.
- **Next Engineering Mentor work:** review the remaining accepted M3 Session contract and existing source before new implementation. In particular, resolve the known mismatch: current session lifetime and cookie `max_age` are **7 days**, whereas the approved default is approximately **24 hours**, configurable, with consistent authoritative server expiry and cookie lifetime. Then continue session validation/expiry, trusted current-User, current-session logout/revocation, CSRF and minimum browser auth integration with their required tests/QA. Do not imply that any of those are already complete.
- Registration Counter Cleanup B2 remains CLOSED. External Registration/Login cleanup scheduling and monitoring remain the AQ-014 Pre-External-Use Gate; no new worker/scheduler framework, M4, or architecture change is authorized.

### Verified M3 Progress — 2026-10-21 (Step 5.9 Cut-off)

The current snapshot supersedes dated implementation-status entries below. The 2026-10-18 records are retained as historical test evidence, not as the current task/status list.

**Registration baseline (unchanged):**

- Registration HTTP API, runtime registration wiring, public-safe error handling, atomic global User + PasswordCredential persistence, approved password screening/Argon2id and PostgreSQL registration rate limiting are implemented.
- Registration Counter Cleanup **B2 Implementation is QA CLOSED**. C1 retention-from-window-expiry and C2 20-batch warning checks are covered by 7 cleanup tests. Cleanup runs outside the request path. Its provisional 24-hour post-window retention, 500 rows/batch and 20 batches/run remain unchanged.
- External cleanup scheduling (provisionally hourly), deployment monitoring/alerting, backlog and retention observations, and DB permissions verification remain **DEFERRED to the Pre-External-Use Gate** under AQ-014; these do not block internal M3 work.

**Step 5.9 — Login Core and Session Creation (committed and CI-verified):**

- Login application/core handles canonical email lookup, NFC password normalization and Argon2id verification, including an unknown-email dummy-hash verification path.
- Login infrastructure provides credential lookup, conditional password-rehash persistence using compare-and-swap (CAS), and credential revalidation/locking. The approved requirement to use a pre-generated dummy Argon2id hash in the eventual production runtime is **not yet verified by HTTP/runtime integration**.
- Session infrastructure generates a cryptographically random 256-bit token, persists its SHA-256 digest (not the raw token), and supports configurable absolute expiration. Session creation verifies the expected credential hash under `SELECT FOR UPDATE` and persists the session in the same transaction as final credential revalidation.
- Committed PostgreSQL integration tests cover successful Login + Session creation, invalid password/no session, and credential change before session creation/no session. Additional tests cover credential locks/concurrency and CAS replacement behavior; these do not prove every possible session race.
- Verified GitHub `main` implementation commit: `aa22bae8568fc926f847db1b3085acab43d1e0db` (`feat(auth): implement login core and session creation`).
- GitHub Actions run https://github.com/phansa2543/kijflow/actions/runs/39584813876 **PASS: 238 passed, 1 skipped**, including PostgreSQL tests. This verifies the committed suite, **not final M3 Security QA or browser integration**.

**Current boundary and next work:**

- M3 remains **IN PROGRESS**. There is not yet a complete public Login HTTP endpoint, production cookie/CSRF flow, or finished session lifecycle.
- Resume at **Step 6 — Login Abuse Protection**, first reviewing existing Registration Rate Limiting for appropriate reuse. Login protection must cover account identifier and request source; registration's IP-only counter alone does not establish the accepted Login control.
- Remaining M3 delivery: runtime Login + Session orchestration; session validation, expiry and logout/revocation; Login HTTP endpoint, safe errors and secure cookies; enumeration resistance and CSRF; minimum browser authentication workflows; complete regression, adversarial/security and integration QA.
- Reconfirm whether existing sessions must be revoked on credential changes under the accepted M3 design; do not implement password-change functionality here. Separate Password Screening independent security acceptance and DEC-009/AQ-016 pre-external-release verification remain open.
- Global User authentication in M3 does **not** grant Organization Membership, trusted tenant context or M4+ authorization.

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

**M3 remains IN PROGRESS.** Step 6 Login Abuse Protection remains **CLOSED** (Independent QA PASS; Founder Approved). Registration Counter Cleanup B2 remains CLOSED.

**Session Lifetime:** implemented at `a37823064e490e444a4b2e39c5171ebea433061e`, CI successful; Independent QA acceptance pending. Default `SESSION_LIFETIME_SECONDS=86400` and synchronized session expiry/cookie lifetime are implemented. The root `.env.example` now includes the setting.

**Session Validation Persistence:** implemented at `5a36cc274ddb3c9b653ef114c8a0b9f30e1b1a58`, GitHub Actions run `39972021451` SUCCESS; Independent QA pending. The current function validates an already-computed digest, not the raw cookie/token. Founder reports 6 focused tests and local full regression 325 passed, 1 skipped.

**Raw Session Token Validation + Session Resolution:** implemented at `f1ca0cc5a9f2c1b4ab975452e9072a91b8b94eb1`; CI run `40054387449` SUCCESS; Independent QA PENDING. These functions validate/resolve at infrastructure level and do not yet extract the HTTP session cookie. Founder-reported local regression: 350 passed, 1 skipped. **Trusted Current-User HTTP Dependency:** implemented and CI SUCCESS at `f742d4f1386ef63395cdc215ab4f126beb17d5e8` (run `40055301574`); Independent QA PENDING. **Current-session Logout / Revocation:** implemented and CI SUCCESS at `b6ff4007600efa16aa8edbf0fc6d183b3c8eb1df` (run `40056785711`), independent QA PENDING. **Cookie/CSRF Backend Security:** CLOSED — Independent Security QA PASS / Founder Approved at `aee8453e7efeab7c51d21894b1d1932e82fd222d`; CI run `40073114863` SUCCESS. **Next:** M3 Next.js Same-Origin Rewrite/Proxy and browser authentication integration. Browser security acceptance and M3 remain OPEN; do not mark other pending session QA subtasks CLOSED or expand to M4.

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

Password Screening is integrated into the Registration service before Argon2id hashing. Registration HTTP API and runtime dependency wiring are now implemented; the independent Password Screening Technical Security/QA acceptance remains pending.

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

---

# M3 Browser UI Foundation — Founder-Approved Design & Implementation Authorization (2026-10-24)

Founder explicitly APPROVED the M3 Frontend Design Package and authorized **Founder-led implementation within approved M3 scope** following Tech Lead review (PASS WITH CONDITIONS), Product/UX focused revision and Independent QA focused condition verification (PASS; F1/F2/F3 RESOLVED). This supersedes the 2026-10-24 frontend pause and pending-design-approval checkpoints. **M3 remains IN PROGRESS; browser implementation and acceptance are not yet complete. M4 remains NOT AUTHORIZED.**

- **UI foundation:** Material UI (MUI) v9 with Emotion and supported Next.js App Router integration (`AppRouterCacheProvider`); a single custom Kijflow MUI Theme, Modern Minimal Purple, Light Mode First. No Tailwind alongside MUI during M3; no custom theme engine or speculative wrappers/frameworks.
- **Visual baseline:** Primary `#6D28D9`, background `#F8F7FC`, surface `#FFFFFF`, Noto Sans Thai with fallbacks, maximum auth form width 420px, input/button radius 10px and auth surface radius 16px. Revised active TextField borders: normal `#858C99` (3.382:1 versus white), hover `#667085` (4.975:1), focus `#6D28D9` (7.105:1).
- **FD-1 state handling:** `204` authenticated; initial/unknown `401` generic sign-in, later `401` after authoritative prior browser verification may show session-no-longer-active copy; `503`/network failure means uncertain/retry, not logged out or authenticated. Logout `503`/network uncertainty blocks protected content and uses `GET /auth/session` to reconcile; `401` leads to Login, `204` supports Retry Logout, unavailable stays uncertain.
- **Implementation gates remain:** rendered border/focus-ring contrast after alpha blending, Thai/English font loading, mobile keyboard/touch/keyboard accessibility, backend authoritative NFC-normalized Unicode code-point password limits (do not substitute JavaScript string.length/HTML maxlength), and actual FD-1/CSRF/cookie/browser regression. No raw session token access or frontend authentication authority.
- **Next:** Engineering Mentor guides Founder to verify package versions, install MUI/Emotion official App Router integration, implement one theme and verify `npm ci`, `npm run lint`, `npm run build` prior to incremental M3 Register/Login/Pre-tenant/Logout/recovery interfaces. FD-1 contract was design-approved separately; verify its implementation before frontend session-state integration. Independent implementation/browser QA and Founder closure are still required.


---

# M3 Frontend — Theme Foundation Implementation Checkpoint / Founder Pause (2026-10-24)

**Current status:** M3 IN PROGRESS; Founder requested IMPLEMENTATION PAUSE. MUI Theme Foundation code is pushed but **Independent QA / closure PENDING**. This supersedes any implication in the prior Design Authorization checkpoint that installation is still the next task; that design approval remains valid.

**Implementation commit:** `5fb676bfaab0ba7e54436243b36104d691c47074` on `main` (frontend/app/globals.css, layout.tsx, page.tsx, theme.ts, package.json, package-lock.json). The temporary MUI Theme Smoke Test is not an Auth screen. Founder reports Next 16.4.3, React 19.3.0, MUI/MUI Next.js 9.5.0, Emotion 11.14.x and working MUI Theme/Next.js integration with Noto Sans Thai.

**Reported local verification:** `npm ci`, `npm run lint`, `npm run build` PASS; dev-browser Typography, TextField, Button, purple/light theme and Thai text render; desktop/mobile (375x812) initial visual smoke checks no visible horizontal overflow. Desktop height measures 1014px without overflow. Mobile overflow has not been independently measured. Browser `sw.js` error cleared after old service-worker unregistration; no verified MUI defect. Local reports are not independent QA. CI outcome is not established here.

**Next task upon explicit Founder resumption — Focus State / Accessibility Verification:** inspect actual normal/hover/focus TextField borders and focus ring including alpha-blended contrast, keyboard focus visibility, accessible labels; remaining responsive/mobile keyboard and SSR/hydration checks; inspect diff/CI and obtain Independent QA acceptance. Do not repeat already verified setup/build without a specific trigger.

**Gate:** Theme Foundation may close only after evidence and Independent QA. Do not start Registration/Login/Logout screens until gate is satisfied. Do not implement M4 Organization/Membership/Tenant UI or introduce Tailwind, MUI X, theme engine, new auth authority or other unapproved changes during pause.

---

# M3 Theme Foundation — Focus Ring Pushed / Independent QA Pending (2026-10-25)

Founder resumed the M3 Theme Foundation verification slice and pushed keyboard focus styling at implementation commit `0332d86510986a84afbe7d4b8389bbc27481c72c` on `main`. The commit changes only `frontend/app/theme.ts`, adding `MuiButton` `.Mui-focusVisible` with `outline: 3px solid #6D28D9` and `outlineOffset: 3px`. The original Theme Foundation implementation remains `5fb676bfaab0ba7e54436243b36104d691c47074`.

GitHub Actions run [40157448915](https://github.com/phansa2543/kijflow/actions/runs/40157448915) completed SUCCESS for the new implementation SHA. Engineering Mentor reported local keyboard and visual checks: TextField border states, control accessible names, button focus computed style, desktop/mobile 375×812 without measured horizontal overflow, initial SSR content and no observed hydration errors. `npm ci` and prior lint/build were Founder-reported; **final local lint/build after the focus change were not independently confirmed in the handoff**. The CI run being green is not proof of frontend lint/build unless those steps are present in its workflow.

**Current gate:** M3 IN PROGRESS; Theme Foundation implemented/pushed, **Independent QA PENDING — NOT CLOSED**. Next request focused Independent QA review of the exact final implementation SHA and browser accessibility/responsive evidence, including actual rendered focus-indicator contrast. `frontend/app/layout.tsx` still has starter `Create Next App` metadata; treat as a small follow-up, not an independently established accessibility blocker. Do not commence M3 Auth Screens or M4 until the Theme Foundation review/Founder closure gate is satisfied. No backend auth or architecture change.

---

# M3 Theme Foundation — Founder Closure (2026-10-25)

**Status: CLOSED — Founder APPROVED**, limited to the M3 MUI Theme Foundation slice. Independent QA reviewed frontend implementation SHA `0332d86510986a84afbe7d4b8389bbc27481c72c` and returned **PASS WITH CONDITIONS**; the remaining C1 evidence requirement has been satisfied and accepted by Command Center and Founder. C1 was executed locally by Founder at `bef754663d725926395959effcf1b0d7a9ebff74` (documentation-only descendants of the reviewed frontend source): clean working tree, reviewed SHA ancestor, and `git diff --exit-code 0332d86510986a84afbe7d4b8389bbc27481c72c bef754663d725926395959effcf1b0d7a9ebff74 -- frontend/` PASS, confirming tracked frontend source equivalence. Founder-reported `npm ci`, `npm run lint`, `npm run build`, production compilation and TypeScript build PASS. GitHub Actions run [40157448915](https://github.com/phansa2543/kijflow/actions/runs/40157448915) SUCCESS on implementation SHA but covers backend only; it is not independent frontend CI evidence. No code or architecture change is implied by closure.

**Separate open security follow-up:** `npm ci` reported **one HIGH-severity dependency vulnerability**, package/advisory and exposure not yet identified. Triage with `npm audit --json` or equivalent, determine affected dependency/runtime reachability, applicable patch and severity; do not run indiscriminate `npm audit fix --force`. This unresolved risk is **not waived** by Theme Foundation closure and must be assessed before real M3 Authentication UI/browser acceptance and definitely before external-user release. Escalate if analysis identifies a directly exploitable vulnerability.

**Non-blocking QA follow-ups for Auth UI:** use explicit deterministic field IDs/labels for SSR accessibility; validate real mobile keyboard/error/focus and hydration behavior with actual forms; replace `Create Next App` metadata before customer-facing auth UI acceptance. The temporary smoke test is not a real Auth screen.

**Next authorized M3 slice:** Incremental Registration/Login/Logout/pre-tenant session UI within the existing Founder-approved frontend design, with Engineering Mentor guidance and required frontend/browser security QA. **M3 remains IN PROGRESS, M4 NOT AUTHORIZED.**

---

# M3 Frontend Dependency Security Follow-up — Remediated (2026-10-25)

**Status: REMEDIATED / Founder local verification PASS; committed on main.** The previously reported one HIGH npm audit finding was identified as GitHub Advisory `GHSA-mrhx-c7xc-m3w5` affecting transitive development dependency `zod@4.6.5` via `eslint-config-next@16.4.0 → eslint-plugin-react-hooks@7.1.1`. Founder ran `npm audit fix`; pushed commit `c21731f765f746b7421042ae4e8fe06f5ba92955` changes only `frontend/package-lock.json`, upgrading `zod` from `4.6.5` to `4.6.7` (`dev: true`), with no application-code change. GitHub Actions [40160281412](https://github.com/phansa2543/kijflow/actions/runs/40160281412) SUCCESS at this SHA (backend CI only; does not validate frontend lint/build).

**Founder-reported local verification after fix:** `npm ls zod` shows `zod@4.6.7`; `npm audit` found **0 vulnerabilities**; `npm run lint` PASS; `npm run build` PASS (Next.js 16.4.3 production compilation, TypeScript validation and 4 static pages). This resolves the known Zod security follow-up on the audited dependency tree at that time, **not a permanent guarantee of zero future vulnerabilities**. No `npm audit fix --force` was used.

**Next:** proceed with approved M3 Registration Screen slice via Engineering Mentor, within previously approved M3 frontend design and backend authentication/CSRF boundaries. Keep real browser auth integration and remaining independently pending backend/security QA OPEN; M3 IN PROGRESS; Theme Foundation remains CLOSED; M4 NOT AUTHORIZED.

---

# M3 Registration Validation Feedback — Founder-approved Contract Change (2026-10-25)

**Status: IMPLEMENTATION AUTHORIZED — NOT YET IMPLEMENTED / INDEPENDENT QA PENDING.** Following Product/UX, Tech Lead and Independent Security QA PASS WITH CONDITIONS reviews, Founder approved a narrow public-safe Registration error-contract refinement and elected to **retain the existing Registration UX without Confirm Password**.

| Known outcome | HTTP | Public code | Frontend mapping |
|---|---:|---|---|
| Typed invalid email syntax | 422 | `INVALID_EMAIL` | Email field |
| Typed password length invalid after authoritative NFC normalization (8–128 Unicode code points) | 422 | `INVALID_PASSWORD_LENGTH` | Password field |
| Common OR compromised password screening rejection | 422 | `PASSWORD_REJECTED` | Password field; same code/message for both sources |
| RequestValidationError / malformed or missing fields | 422 | `REGISTRATION_FAILED` | Generic form error |
| Duplicate canonical email | 409 | `REGISTRATION_FAILED` | Generic form error (no account existence disclosure) |
| Oversized body | 413 | `REGISTRATION_FAILED` | Generic form error |
| Rate limited | 429 | `REGISTRATION_FAILED` | Generic form error; preserve Retry-After and no-store |
| Screening or limiter unavailable | 503 | `REGISTRATION_FAILED` | Temporary unavailable/retry; fail closed |
| Unexpected/internal exception | 500 | `REGISTRATION_FAILED` | Generic form error |

**Engineering requirements:** use explicit typed semantic failures for known email/length validation, with boundary-safe translation; do not classify by exception messages. Unexpected `ValueError` must not turn into field-specific 422. Preserve route-local sanitized Framework/Pydantic 422, existing CSRF 403 boundary, unchanged registration request (only email/password) and success 201 response, persistence atomicity, no-session-on-registration, rate-limit quota accounting, and no sensitive/provider/internal information in errors/logs. No new endpoint, table, framework, session/cookie or Architecture changes.

**UX:** keep existing Show/Hide Password design, do not add Confirm Password. Local required/email-format guidance and helpful Thai policy text may be displayed; backend remains sole policy authority for NFC-normalized Unicode code-point length and screening. Never use JS string.length or HTML maxlength as authoritative validation. Map recognized status+code to accessible inline errors; generic 422/unknown codes to form-level errors, 503 to temporary retry, 409 without asserting email exists, and 429 observing Retry-After. Deterministic input IDs, aria-invalid/describedby, keyboard focus and error announcements required.

**Required QA before closure:** backend tests for exact code mappings, normalized 7/8/128/129 password boundaries, common/HIBP rejection equivalence, screening unavailable 503, framework-generated 422 sanitization, unknown exception generic fallback, duplicate and concurrent registration, CSRF, rate-limiting/quota/Retry-After, oversized body, no leaked sensitive input, no partial persistence/session issuance; frontend lint/build and real-browser error/accessibility/security regression; independent implementation review and Founder acceptance. Founder-led implementation with Engineering Mentor authorized; **M3 remains OPEN, M4 NOT AUTHORIZED**.

---

## M3 Registration F3 UX Acceptance Correction — Founder Decision (2026-10-25)

**Status: F3 COPY REQUIREMENT SUPERSEDED BY FOUNDER.** Command Center's instruction that both Registration password helper and length-error text display the entire 8–128 range was **withdrawn**. Founder explicitly chooses minimum-only UI guidance rather than exposing an unrealistic maximum in ordinary Registration copy. The existing form messages (minimum 8 characters and advice to choose a hard-to-guess password; length-error text saying at least 8) are acceptable; QA must **not block on absence of “128” from either UI string**.

**Security/technical invariants unchanged:** authoritative Backend password length **8–128 Unicode code points after NFC**, rejection above 128, no silent truncation, existing common/compromised screening, approved `422 INVALID_PASSWORD_LENGTH` response, CSRF/rate-limit/persistence/session boundaries, and no frontend JS `string.length`/HTML `maxlength` as policy authority. Accepted UX trade-off: the one public password-length error code may display minimum-only guidance even for extraordinarily long inputs; do not silently modify backend policy or introduce new error codes. Keep no Confirm Password per Founder approval.

**Evidence and gate:** GitHub `main` source review at `fad7f69a1f6cb7b431c21e47223b26852d9d4423` confirmed F1 Confirm Password removal and the retained minimum-only wording; previous source review at `36a3b8168e3480eebd333a5f0eb279da41495598` confirmed F2 unexpected ValueError maps generic 500. CI run 40180968867 SUCCESS (backend only); frontend lint/build remains Founder-reported, not CI independently proven. Next: Independent QA on full M3 Registration public-safe error contract and browser/UI/security/accessibility. Neither this decision nor prior source checks constitute independent QA acceptance or M3 closure; M4 NOT AUTHORIZED.


---

## M3 Registration Independent QA FAIL — B1 Implementation and Founder-requested Pause (2026-10-25)

**Disposition: PAUSED by Founder after B1; Registration slice remains NOT ACCEPTED.** Independent QA reviewed the Registration Screen/Public-safe Error Contract at code commit `fad7f69a1f6cb7b431c21e47223b26852d9d4423` with `main` at `c73708f60d9811d5b5c40621bc8a94e17f1c9ede` and returned **FAIL** for combined acceptance. Backend public-safe mapping and security controls passed **source review only**, not a new independent local backend regression. Frontend B1 and B2 were blockers; C1 and N1 require follow-up. Full Next.js→FastAPI→PostgreSQL browser verification, screen-reader/mobile and frontend CI evidence were not established.

### B1 Password visibility — IMPLEMENTED / LOCAL PASS REPORTED / INDEPENDENT QA PENDING

- Verified pushed implementation `32136f3e6fabd3d9fb5eaed48d67c07f953da351` (`feat(auth): add accessible registration password visibility`), parent `c73708f60d9811d5b5c40621bc8a94e17f1c9ede`.
- Exact committed diff: `frontend/app/register/page.tsx`, `frontend/package.json`, `frontend/package-lock.json`. Uses `@mui/icons-material` Visibility/VisibilityOff, hidden password initially, `IconButton` to toggle, stateful accessible label, `aria-pressed`, and ordinary keyboard-usable button semantics. No Confirm Password; backend untouched.
- GitHub Actions [40185343630](https://github.com/phansa2543/kijflow/actions/runs/40185343630) **SUCCESS at exact B1 SHA**, but workflow runs **backend-only** tests, not frontend lint/build/browser.
- Founder/Engineering Mentor reported frontend lint/build PASS, rendered icon and accessible DOM evidence, Tab/Enter/Space keyboard PASS; these are **not independently executed QA**. B1 is **not CLOSED**.

### Remaining QA Findings — ON HOLD

| Finding | Status at Founder pause | Resume acceptance requirement |
|---|---|---|
| B2 — validation focus and dynamic error announcement | **PENDING / PARTIALLY PRESENT IN SOURCE** | B1 commit already adds input refs and local/backend focus calls; verify actual first-invalid focus, consistent email validation, MUI input-error association, dynamic screen-reader announcements and unnecessary focus movement in real browser before accepting |
| C1 — HTTP 429 Retry-After | **NOT STARTED** | Safely consume valid server `Retry-After` with fallback; no Backend limiter change or countdown framework |
| N1 — frontend/backend email-format consistency | **NOT STARTED / NON-BLOCKING** | Avoid locally rejecting backend-accepted email syntax; Backend remains validation authority |

**Accepted Founder decisions remain unchanged:** no Confirm Password; minimum **8-character-only** password UI guidance without mandatory 128-character wording; backend remains authoritative for NFC-normalized **8–128 Unicode code points** and approved screening; public-safe error codes, trusted Origin/CSRF, abuse controls and atomic registration unchanged.

**Resume gate:** only upon Founder instruction, Engineering Mentor supports Founder-led B2, C1 and N1 focused work; verify exact pushed diff/SHA and CI, local frontend lint/build, browser errors/focus/keyboard/mobile/screen reader, real Next.js→FastAPI→PostgreSQL and security cases; return to Independent QA for focused delta review, then obtain Founder Acceptance. Do not close Registration, M3, or start M4 while paused. Theme Foundation and previously CLOSED backend workstreams remain CLOSED.

---

## M3 Registration B2 — Pushed Checkpoint / Founder Pause (2026-10-25)

**Current: M3 IN PROGRESS; Founder has paused further development. B2 Focus/Error Announcement is IMPLEMENTED / PUSHED, Independent QA PENDING, NOT CLOSED. Registration Screen retains prior QA FAIL / REMEDIATION status. M4 NOT AUTHORIZED.**

GitHub `main` B2 commit: `9ad8ecb9e3199082c5c6494a559bfd7eda11df86`; changes only `frontend/app/register/page.tsx`. GitHub Actions run [40203623956](https://github.com/phansa2543/kijflow/actions/runs/40203623956) completed SUCCESS; this is not proof of frontend accessibility or frontend CI. Founder/Engineering Mentor report local lint/build PASS and visual focus checks for empty form, missing password, and repeated submit; independent browser and screen-reader verification remain outstanding.

Source confirms sequence-based `focusRequest` with an Effect for repeatable client-side focus, explicit MUI helper IDs / `aria-describedby`, clearing field-specific stale errors when edited and clearing a previous submit error on a new attempt. **Important residual verification:** backend validation branches still call `inputRef.current?.focus()` directly, so the submitted B2 source does not yet demonstrate that backend-error focus always waits until React renders updated error descriptions. Also verify screen-reader announcements, repeated identical backend errors, keyboard/password-visibility interaction, and rendered accessible descriptions. These are QA risks, not independently confirmed user-facing defects.

**Resume only on Founder instruction:** give the exact SHA to Independent QA for focused B2 source/browser/accessibility delta review; return verified defects to Engineering Mentor for Founder-led corrections. Only after B2 verification proceed to C1 HTTP 429 `Retry-After` (NOT STARTED). N1 email-format alignment remains NOT STARTED / NON-BLOCKING. Preserve no Confirm Password, minimum-only 8-character UI copy, backend NFC 8–128-code-point authority, public-safe error contracts, existing CSRF/session security and M3 scope. No M4.

---

## M3 Resumed — Founder Scope-Control Direction (2026-10-26)

**Founder explicitly resumes M3 Registration & Authentication at the existing checkpoint.** The prior Founder-requested implementation pause is lifted; M3 remains IN PROGRESS and M4 is NOT AUTHORIZED. No previously pending QA outcome becomes accepted by resumption.

**Next gate:** Independent QA focused review of B2 Registration Focus/Error Announcement at implementation SHA `9ad8ecb9e3199082c5c6494a559bfd7eda11df86` (client/backend validation focus, rendered accessible descriptions, actual screen-reader announcement, repeated errors, stale errors, keyboard/password visibility). Return only verified defects for Founder-led targeted remediation. B2 remains QA PENDING, Registration Screen remains NOT CLOSED. Once B2 passes, proceed to approved C1 `Retry-After` handling; N1 email-validation alignment remains NON-BLOCKING unless new evidence justifies reclassification. Finish accepted M3 frontend and backend QA/browser integration gates before requesting M3 closure.

**Founder scope-control instruction:** Proposals outside the accepted M3 scope are welcome but MUST be presented to Founder BEFORE any addition/implementation, with necessity, expected benefit, risks, development/maintenance impact, and alternatives within existing scope; only explicit Founder approval authorizes expansion. Fixing verified defects or meeting already approved M3 acceptance/security criteria is within scope, not silently a new feature. No automatic scope expansion, no M4 work, and no new technology/framework without review. Founder writes code; Engineering Mentor guides; Independent QA verifies; Command Center coordinates.

---

## M3 Registration B2-F1 — Source/CI Verified; Independent QA Pending (2026-10-26)

**M3 IN PROGRESS; B2-F1 IMPLEMENTED / PUSHED / SOURCE VERIFIED / CI SUCCESS; B2 and Registration Screen NOT CLOSED; M4 NOT AUTHORIZED.** Verified GitHub `main` head `18e9febb39655b8d352a5fdee06ba037f8644260` changes **only** `frontend/app/register/page.tsx`. Exact patch replaces direct `inputRef.current?.focus()` calls in backend validation-result branches (`INVALID_EMAIL`, `INVALID_PASSWORD_LENGTH`, `PASSWORD_REJECTED`) with existing sequence-based `requestFieldFocus("email" | "password")`. No backend or other UI implementation changes in this commit.

GitHub Actions [40291193143](https://github.com/phansa2543/kijflow/actions/runs/40291193143) completed SUCCESS; this does **not** establish frontend/browser or screen-reader accessibility acceptance. Engineering Mentor reports Founder-local `npm run lint` and `npm run build` PASS; not independently rerun here.

**Independent QA focused delta assignment (still pending, not a reported PASS):** verify client-side focus and repeated submits; backend validation focus after error render; repeated identical backend errors; rendered `aria-describedby` links / accessible descriptions; actual dynamic screen-reader error announcements; stale error clearing / unexpected focus movement; keyboard and Show/Hide Password interaction. Source sequencing reduces the specific B2-F1 timing risk but does not independently prove every rendered or assistive-technology behavior. Return only confirmed defects to Engineering Mentor for Founder-led targeted remediation; obtain Founder acceptance before marking B2 CLOSED.

**Following gate:** C1 HTTP 429 `Retry-After` remains NOT STARTED; N1 email-format alignment remains NON-BLOCKING / NOT STARTED. Preserve approved minimum-only 8-character UI wording (backend NFC-normalized 8–128 Unicode code points authoritative), no Confirm Password, approved registration public-error/CSRF/session boundaries, and no M4 or unapproved M3 scope expansion. New outside-scope proposals require explicit Founder review before implementation, including necessity, benefit, risks, effort/maintenance impact and in-scope alternative.

---

## M3 C1 Retry-After — QA PASS for C1-F1 / Real Integration Pending / Founder Pause (2026-10-26)

**Current milestone gate: M3 IN PROGRESS. Founder has paused development. M4 NOT AUTHORIZED.** Founder explicitly selected **Option A**: test real Next.js → FastAPI HTTP 429 `Retry-After` forwarding and Registration UI behavior **before proposing overall C1 closure**. This updates the previous historical "C1 NOT STARTED" checkpoint, not the underlying approved M3 scope.

### Completed implementation and verified delta

- Initial C1 frontend `Retry-After` consumption: `354b67f9bb04421b83ffdb2c2016013deceaee58` (`frontend/lib/api/registration.ts`, `frontend/app/register/page.tsx`). Supports positive integer seconds and canonical future HTTP-date, rejects unusable values to `null` and uses existing form-level generic error fallback; no countdown, backend change or new dependency.
- Independent QA found **C1-F1**: valid July HTTP-date rejected by missing `Jul` month regex branch.
- Founder-led correction `a4e9ffc3d0263a915cf8c83537e6d5e4b5513d8e`: only `frontend/lib/api/registration.ts`, one-line change adding `Jul`, no other logic/dependencies. **C1-F1 Independent QA PASS** at exact corrected SHA: independently executed parser regression **32/32 PASS**; mocked HTTP 429 mapping **4/4 PASS**. GitHub Actions [40302976718](https://github.com/phansa2543/kijflow/actions/runs/40302976718) **SUCCESS (backend job only)**.
- Engineering Mentor / Founder final handoff at the same SHA: tracked working tree **CLEAN**, frontend lint/build **PASS** and Chrome **mock** response cases (numeric 60, missing, invalid header) **3/3 PASS**, **Founder-reported**; not independently rerun or established by backend CI. No confirmed defects in tested C1 cases.

### Still OPEN — acceptance evidence

1. **Real browser end-to-end rate-limit:** run Next.js same-origin frontend and FastAPI backend (existing PostgreSQL test/development configuration), exercise real registration HTTP 429 in a controlled *local development* environment; inspect Chrome Network HTTP status, positive `Retry-After` response header through the rewrite, browser UI Thai retry guidance, visible Alert, keyboard and console/hydration behavior. Do not treat mocked Fetch/Chrome interception or direct-to-FastAPI requests as proof. No production/external-user load or security bypass.
2. **Actual screen-reader announcement:** NOT VERIFIED; keep explicitly open until independently tested or dispositioned through a subsequent, explicit Founder acceptance decision. MUI source `role="alert"` is not proof of actual announcement.
3. **Final C1 acceptance:** Independent QA reviews the real integration evidence, distinguishing Founder-reported from independent executions; Command Center presents actual remaining limits to Founder. **Overall C1 OPEN; no automatic closure.**

### Adjacent workstream status and pause boundary

- **B2 Focus/Error Announcement:** Independent QA found B2-F2/F3 at historical `18e9febb39655b8d352a5fdee06ba037f8644260`; source corrections are reported at `9b73b73373435f4c72792448135edc66c474dec8`. Subsequent Engineering Mentor and QA handoffs **report Founder-directed B2 closure by QA Exception**; however, the primary Founder acceptance record has not been verified in the currently indexed GitHub Project Sources. Treat as **reported closure pending provenance reconciliation**, not Independent QA PASS and not a reason to repeat already corrected code. No unrelated B2 re-opening without a confirmed new defect.
- **N1 email-validation alignment:** NON-BLOCKING, separately tracked; no scope expansion here. Registration Screen / broader M3 authentication, browser/security/independent QA gates remain OPEN as applicable.
- **Pause:** Founder requested no further development until explicitly resumed; Engineering Mentor guidance, Independent QA and Founder-controlled code ownership unchanged; M4 **NOT AUTHORIZED**.

**Next action upon Founder resumption:** use the previously approved "M3 C1 Real HTTP 429 Integration Verification" handoff. Collect actual local browser Network + UI evidence at the exact SHA; submit to Command Center and Independent QA; then separately seek explicit Founder C1 closure. Do not implement new test framework, rewrite, endpoint, limiter change, or additional feature without approved evidence and scope.

---

## M3 Authentication UI Polish — Founder Feedback / Scope Proposal (2026-10-26)

**Status: PROPOSED / UX REVIEW PENDING / NOT AUTHORIZED TO IMPLEMENT.** Founder describes the current Kijflow UI as visually plain. Command Center recommends exploring **limited polish of M3 Authentication screens**, not a comprehensive redesign. This is not an independently confirmed product defect, agreed design specification, or Founder-approved scope expansion.

**Candidate scope to evaluate:** improve visual hierarchy, typography, spacing, button/form finish, and Kijflow brand expression in the existing Registration/Login/authentication UI, ideally alongside work on unfinished M3 screens and using the already accepted MUI/Emotion Modern Minimal Purple foundation. Maintain accessibility, responsive behavior, clear Thai copy, and low solo-maintainer overhead.

**Explicit exclusions from this proposal:** new Theme Foundation or styling stack, standalone design-system framework, new UI libraries without proven need, non-authentication Dashboard or Business Module design, and broad visual redesign. No changes to authentication, privacy/security, or acceptance contracts.

**Required gate before implementation:** Product & UX Designer reviews the actual screens and provides a concrete minimal proposal, necessity/value, UX risks, estimated one-person development/maintenance burden, alternative of deferring visual polish, and accessibility/regression implications. Founder must explicitly approve any new work. QA then checks changed presentation against existing keyboard, error, screen-reader, and browser criteria; do not claim polish is mandatory to close M3 absent Founder acceptance.

**Priority:** C1 real Next.js → FastAPI HTTP 429 verification remains the exact authorized resume point. Founder-requested development pause remains active, C1 overall OPEN, M3 IN PROGRESS, M4 NOT AUTHORIZED. This proposal does not reorder the approved M3 work or authorize work during the pause.

---

## M3 C1 — Founder-Approved QA Exception Closure (2026-10-26)

**Current C1 status: CLOSED WITH QA EXCEPTION — FOUNDER APPROVED.** This supersedes historical C1 OPEN / pause checkpoints. M3 **IN PROGRESS**, Registration Overall Acceptance **OPEN**, M4 **NOT AUTHORIZED**.

**Evidence:** C1-F1 parser regression **32/32** and mocked HTTP 429 **4/4** were independently executed and PASS. Independent QA verified unchanged application code between baseline `a4e9ffc3d0263a915cf8c83537e6d5e4b5513d8e` and Founder-tested HEAD `813165aaae5f0127b8f44490575d72adc3ce9ab9` (only three documentation files changed). Real Windows/Chrome → Next.js same-origin `POST http://localhost:3000/auth/register` → FastAPI → PostgreSQL limiter testing was **Founder/Engineering Mentor-reported**: attempts 1–10 HTTP 422, attempt 11 HTTP 429, `Retry-After: 281`, `Cache-Control: no-store`, visible Thai Alert/retry guidance, no observed JS exception. **Independent QA did not directly reproduce browser behavior or inspect HAR/recording.** Final QA verdict: **PASS WITH EXPLICIT LIMITATIONS**. No new confirmed C1 application defect. Initial HTTP 503 was reportedly a local outdated Alembic revision, resolved by applying existing migrations.

**Accepted limitations / release gate:** Keyboard operation was not separately verified during final real HTTP 429; Independent QA did not require a repeat test for narrow C1 closure. Actual screen-reader announcement of MUI `role="alert"` on initial and repeated 429 is **UNVERIFIED**, **not accessibility QA PASS**. Founder explicitly accepted the risk for internal C1 closure; **real assistive-technology verification and remediation of confirmed defects are mandatory before any external-user access (including beta)**. Keep tracked in external-use acceptance checklist; never silently waive or call PASS.

**Next:** Remaining Registration Screen acceptance and M3 authentication UI/session integration plus outstanding backend/security QA. C1 is not reopened merely because browser evidence is Founder-led. UI Polish stays PROPOSED pending separate review/approval. This decision does not approve new code, new dependencies, M4 or general M3 closure.

---

## M3 Registration — Founder Internal Acceptance with Explicit QA Exceptions (2026-10-27)

**CURRENT REGISTRATION STATUS: CLOSED WITH EXPLICIT QA EXCEPTIONS — FOUNDER APPROVED, INTERNAL DEVELOPMENT ONLY.** This supersedes older Registration OPEN and evidence-blocked checkpoints; it does **not** close M3. M3 **IN PROGRESS**; M4 **NOT AUTHORIZED**.

**Acceptance evidence boundary:** Independent QA reviewed current source, public-safe 422 mappings, backend tests, B1/B2 corrections, and C1 tests. Founder-led real-browser / PostgreSQL evidence reports Registration 201, atomic User + PasswordCredential persistence, `INVALID_PASSWORD_LENGTH`, `PASSWORD_REJECTED`, generic duplicate 409, error clearing, focus stability, keyboard and Show/Hide Password outcomes. No new confirmed blocking implementation defect; browser behavior was not independently reproduced by QA. Tested implementation baseline `5badd183b1e509a87c42109f0729c28fbbfbf786`; follow-on docs-only commits do not themselves prove runtime results.

**Founder-approved EXCEPTIONS — NOT QA PASS:**
- Real HTTP 422 `INVALID_EMAIL` response displayed through actual Registration browser UI is UNVERIFIED (independent source/backend-test path verified; input `alice..smith@example.com` appears reachable).
- Rendered Email input `aria-describedby` and `register-email-error` DOM association is UNVERIFIED despite matching source IDs.
- Responsive layout at final Registration viewport 375×812 remains UNVERIFIED; existing source/mobile Theme Foundation evidence is supporting, not final-form runtime PASS.
- Actual assistive-technology/screen-reader announcements for Registration field/form errors and initial/repeated 429 remain UNVERIFIED.

**B1/B2 and ancillary disposition:** B1 Password Visibility accepted as part of Registration on source review + Founder-reported prior browser outcomes; no new separate B1 acceptance test. B2 source corrections verified; prior Founder-directed QA Exception closure reported but original primary acceptance record not found. Founder explicitly reaffirms this scoped internal B2 closure; do not call independent screen-reader PASS. Prior Chrome keyboard/focus evidence was Founder-reported, historical exact executed SHA incompletely proven and accepted with attribution limitation. Duplicate 409 body was not visible in DevTools, but prior backend response tests and generic UI were considered sufficient; no new duplicate persistence test mandatory. Screening 503 and browser CSRF negative accepted using previously approved backend/source evidence, not falsely called independently reproduced browser runs. N1 remains NON-BLOCKING.

**PRE-EXTERNAL-USER BLOCKING GATE (including beta):** Verify actual browser `INVALID_EMAIL` handling, rendered error association, final Registration 375×812 usability and real screen-reader announcements (initial/repeated validation/form/429); remedy verified defects. Retain other pre-external-user obligations (AQ-014, AQ-016, security and release acceptance). No exception authorizes external exposure before remediation and acceptance.

**Sequence:** Registration internal slice CLOSED; continue remaining M3 authentication work via explicit scoped coordination, starting with Login readiness/approved design review before Founder-led code. Do not treat this entry as authorization to begin coding Login or M4, or close Session/Logout/Password Screening independent QA still pending.
