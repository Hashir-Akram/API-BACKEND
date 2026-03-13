# Master Test Cases - API Backend

## Scope
This document contains comprehensive test cases for all backend features in this repository.

Covered modules:
- Utility endpoints
- Authentication and profile
- User management
- Project management
- Task management
- Comments
- Analytics
- Audit logs
- Validation, pagination, sorting, filtering
- Security, reliability, and regression flows

Related frontend repo (separate): https://github.com/Hashir-Akram/REACT_FRONTEND_API_TESTING.git

## Test Environment
- Base URL: http://localhost:5000
- Database: SQLite (users.db)
- Auth: JWT Bearer token
- Seed users:
  - admin@example.com / Admin@123
  - john@example.com / John@123
  - sara@example.com / Sara@123

## Common Headers
- Content-Type: application/json
- Authorization: Bearer <token> (for protected routes)

## Priority Legend
- P0: critical
- P1: high
- P2: medium
- P3: low

## Type Legend
- Positive
- Negative
- Boundary
- Security
- Integration
- Reliability

---

## 1) Utility Endpoints

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| UTL-001 | GET /health | Valid request | Positive | P0 | 200, status=success, data.status=healthy |
| UTL-002 | GET /health | Response schema check | Integration | P1 | Has timestamp, version, features[] |
| UTL-003 | GET /health | Method not allowed (POST) | Negative | P2 | 405 |
| UTL-004 | GET /error | Trigger simulated exception | Reliability | P1 | 500 with standardized error response |
| UTL-005 | POST /reset | Reset works without auth | Positive | P1 | 200 success and seed data restored |
| UTL-006 | POST /reset | Method not allowed (GET) | Negative | P2 | 405 |

---

## 2) Authentication & Profile

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| AUTH-001 | POST /register | Valid new user | Positive | P0 | 201, user created, role=user |
| AUTH-002 | POST /register | Duplicate email | Negative | P0 | 409 DUPLICATE_EMAIL |
| AUTH-003 | POST /register | Missing body | Negative | P0 | 400 MISSING_BODY |
| AUTH-004 | POST /register | Missing required field name | Negative | P0 | 400 MISSING_FIELD |
| AUTH-005 | POST /register | Invalid email format | Negative | P0 | 400 INVALID_EMAIL |
| AUTH-006 | POST /register | Name length < 3 | Boundary | P1 | 400 INVALID_NAME |
| AUTH-007 | POST /register | Name length = 3 | Boundary | P2 | 201 |
| AUTH-008 | POST /register | Name length > 100 | Boundary | P1 | 400 INVALID_NAME |
| AUTH-009 | POST /register | Age < 18 | Boundary | P0 | 400 INVALID_AGE |
| AUTH-010 | POST /register | Age = 18 | Boundary | P1 | 201 |
| AUTH-011 | POST /register | Age > 150 | Boundary | P1 | 400 INVALID_AGE |
| AUTH-012 | POST /register | Password < 8 chars | Boundary | P0 | 400 INVALID_PASSWORD |
| AUTH-013 | POST /register | Password missing uppercase | Negative | P0 | 400 INVALID_PASSWORD |
| AUTH-014 | POST /register | Password missing lowercase | Negative | P0 | 400 INVALID_PASSWORD |
| AUTH-015 | POST /register | Password missing digit | Negative | P0 | 400 INVALID_PASSWORD |
| AUTH-016 | POST /register | Password missing special char | Negative | P0 | 400 INVALID_PASSWORD |
| AUTH-017 | POST /register | Password with spaces | Negative | P1 | 400 INVALID_PASSWORD |
| AUTH-018 | POST /register | Password length > 128 | Boundary | P1 | 400 INVALID_PASSWORD |
| AUTH-019 | POST /register | Attempt role=admin in payload | Security | P0 | Created user role remains user |
| AUTH-020 | POST /login | Valid admin credentials | Positive | P0 | 200 with JWT token and user |
| AUTH-021 | POST /login | Valid user credentials | Positive | P0 | 200 with JWT token |
| AUTH-022 | POST /login | Missing body | Negative | P0 | 400 MISSING_BODY |
| AUTH-023 | POST /login | Missing email | Negative | P0 | 400 MISSING_FIELD |
| AUTH-024 | POST /login | Invalid email format | Negative | P0 | 400 INVALID_EMAIL |
| AUTH-025 | POST /login | Wrong password | Security | P0 | 401 INVALID_CREDENTIALS |
| AUTH-026 | POST /login | Unknown email | Security | P0 | 401 INVALID_CREDENTIALS |
| AUTH-027 | GET /me | Valid token | Positive | P0 | 200 current user profile |
| AUTH-028 | GET /me | No token | Security | P0 | 401 MISSING_TOKEN/UNAUTHORIZED |
| AUTH-029 | GET /me | Invalid token string | Security | P0 | 401 invalid token error |
| AUTH-030 | GET /me | Expired token | Security | P1 | 401 token expired |
| AUTH-031 | PUT /me | Update own name/email/age/password | Positive | P0 | 200 updated profile |
| AUTH-032 | PUT /me | Missing body | Negative | P0 | 400 MISSING_BODY |
| AUTH-033 | PUT /me | Duplicate email to another user | Negative | P0 | 409 DUPLICATE_EMAIL |
| AUTH-034 | PUT /me | Invalid age format string | Negative | P1 | 400 INVALID_AGE |
| AUTH-035 | PUT /me | Payload contains role=admin | Security | P0 | Role must not change |
| AUTH-036 | PUT /me | Update password with weak policy | Negative | P0 | 400 INVALID_PASSWORD |

---

## 3) User Management

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| USR-001 | GET /users | Admin gets paginated users | Positive | P0 | 200 users[], pagination |
| USR-002 | GET /users | Normal user tries access | Security | P0 | 403 FORBIDDEN |
| USR-003 | GET /users | No token | Security | P0 | 401 |
| USR-004 | GET /users | role filter=admin | Positive | P1 | 200 only admin users |
| USR-005 | GET /users | role filter invalid | Negative | P1 | 400 INVALID_FILTER |
| USR-006 | GET /users | page=0 | Boundary | P1 | 400 INVALID_PAGE |
| USR-007 | GET /users | per_page=0 | Boundary | P1 | 400 INVALID_PER_PAGE |
| USR-008 | GET /users | per_page=101 | Boundary | P1 | 400 INVALID_PER_PAGE |
| USR-009 | GET /users | sort_by unsupported field | Negative | P1 | 400 INVALID_SORT_BY |
| USR-010 | POST /users | Admin creates user valid payload | Positive | P0 | 201 user created |
| USR-011 | POST /users | Non-admin tries create | Security | P0 | 403 |
| USR-012 | POST /users | Duplicate email | Negative | P0 | 409 DUPLICATE_EMAIL |
| USR-013 | GET /users/:id | Admin can fetch any user | Positive | P0 | 200 user object |
| USR-014 | GET /users/:id | User fetches own ID | Positive | P0 | 200 |
| USR-015 | GET /users/:id | User fetches other user ID | Security | P0 | 403 FORBIDDEN |
| USR-016 | GET /users/:id | Invalid ID (abc) | Negative | P1 | 400 INVALID_USER_ID |
| USR-017 | GET /users/:id | ID not found | Negative | P1 | 404 USER_NOT_FOUND |
| USR-018 | PUT /users/:id | Admin updates role user->admin | Positive | P0 | 200 role updated |
| USR-019 | PUT /users/:id | Non-admin update attempt | Security | P0 | 403 |
| USR-020 | PUT /users/:id | Update duplicate email | Negative | P0 | 409 DUPLICATE_EMAIL |
| USR-021 | DELETE /users/:id | Admin deletes existing user | Positive | P0 | 200 deleted user |
| USR-022 | DELETE /users/:id | Non-admin delete attempt | Security | P0 | 403 |
| USR-023 | DELETE /users/:id | Delete non-existing user | Negative | P1 | 404 USER_NOT_FOUND |
| USR-024 | DELETE /users/:id | Invalid ID (<1) | Boundary | P1 | 400 INVALID_USER_ID |

---

## 4) Projects

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| PRJ-001 | GET /projects | Auth user gets project list | Positive | P0 | 200 projects[] + pagination |
| PRJ-002 | GET /projects | No token | Security | P0 | 401 |
| PRJ-003 | GET /projects | status=active filter | Positive | P1 | Only active projects |
| PRJ-004 | GET /projects | invalid status filter | Negative | P1 | 400 INVALID_STATUS |
| PRJ-005 | GET /projects | owner_id invalid string | Negative | P1 | 400 INVALID_USER_ID |
| PRJ-006 | GET /projects | q search keyword | Positive | P2 | Matching title/description set |
| PRJ-007 | POST /projects | Valid create by user | Positive | P0 | 201 owner_id=current user |
| PRJ-008 | POST /projects | Missing title | Negative | P0 | 400 MISSING_FIELD |
| PRJ-009 | POST /projects | Title length < 3 | Boundary | P1 | 400 INVALID_TITLE |
| PRJ-010 | POST /projects | Description length < 10 | Boundary | P1 | 400 INVALID_DESCRIPTION |
| PRJ-011 | GET /projects/:id | Existing project | Positive | P0 | 200 project object |
| PRJ-012 | GET /projects/:id | Non-existing project | Negative | P1 | 404 PROJECT_NOT_FOUND |
| PRJ-013 | PUT /projects/:id | Owner updates own project | Positive | P0 | 200 updated |
| PRJ-014 | PUT /projects/:id | Admin updates any project | Positive | P0 | 200 updated |
| PRJ-015 | PUT /projects/:id | Non-owner/non-admin update | Security | P0 | 403 FORBIDDEN |
| PRJ-016 | PUT /projects/:id | Non-admin attempts owner_id change | Security | P1 | owner_id remains unchanged |
| PRJ-017 | PUT /projects/:id | Admin updates status=archived | Positive | P1 | 200 with archived status |
| PRJ-018 | DELETE /projects/:id | Owner deletes own project | Positive | P0 | 200 deleted |
| PRJ-019 | DELETE /projects/:id | Admin deletes project | Positive | P0 | 200 deleted |
| PRJ-020 | DELETE /projects/:id | Non-owner/non-admin delete | Security | P0 | 403 FORBIDDEN |
| PRJ-021 | PATCH /projects/:id/archive | Owner archives project | Positive | P0 | 200 status archived |
| PRJ-022 | PATCH /projects/:id/archive | Unauthorized user archives | Security | P0 | 403 FORBIDDEN |
| PRJ-023 | PATCH /projects/:id/archive | Invalid project id | Negative | P1 | 400 INVALID_USER_ID |

---

## 5) Tasks

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| TSK-001 | GET /tasks | Auth user gets tasks | Positive | P0 | 200 tasks[] + pagination |
| TSK-002 | GET /tasks | Filter by project_id | Positive | P1 | Only matching tasks |
| TSK-003 | GET /tasks | Filter by assigned_to | Positive | P1 | Only assigned tasks |
| TSK-004 | GET /tasks | status valid filter | Positive | P1 | Only selected status |
| TSK-005 | GET /tasks | status invalid | Negative | P1 | 400 INVALID_STATUS |
| TSK-006 | GET /tasks | priority valid filter | Positive | P1 | Only selected priority |
| TSK-007 | GET /tasks | priority invalid | Negative | P1 | 400 INVALID_PRIORITY |
| TSK-008 | GET /tasks | overdue=true | Positive | P2 | Only overdue tasks |
| TSK-009 | GET /tasks | sort_by invalid | Negative | P1 | 400 INVALID_SORT_BY |
| TSK-010 | POST /tasks | Valid create task | Positive | P0 | 201 created_by=current user |
| TSK-011 | POST /tasks | Missing required project_id | Negative | P0 | 400 MISSING_FIELD |
| TSK-012 | POST /tasks | Project does not exist | Negative | P0 | 404 PROJECT_NOT_FOUND |
| TSK-013 | POST /tasks | Title < 3 | Boundary | P1 | 400 INVALID_TITLE |
| TSK-014 | POST /tasks | Description < 5 | Boundary | P1 | 400 INVALID_DESCRIPTION |
| TSK-015 | POST /tasks | Status invalid enum | Negative | P1 | 400 INVALID_TASK_STATUS |
| TSK-016 | POST /tasks | Priority invalid enum | Negative | P1 | 400 INVALID_TASK_PRIORITY |
| TSK-017 | POST /tasks | assigned_to empty string | Boundary | P2 | accepted as null |
| TSK-018 | POST /tasks | estimated_hours negative | Boundary | P1 | 400 INVALID_ESTIMATED_HOURS |
| TSK-019 | POST /tasks | estimated_hours > 1000 | Boundary | P1 | 400 INVALID_ESTIMATED_HOURS |
| TSK-020 | POST /tasks | due_date invalid format | Negative | P1 | 400 INVALID_DUE_DATE |
| TSK-021 | POST /tasks | tags as CSV string | Positive | P2 | stored as normalized list |
| TSK-022 | POST /tasks | tags as array | Positive | P2 | stored as trimmed list |
| TSK-023 | POST /tasks | tags invalid type number | Negative | P1 | 400 INVALID_TAGS |
| TSK-024 | GET /tasks/:id | Existing task | Positive | P0 | 200 task |
| TSK-025 | GET /tasks/:id | Non-existing task | Negative | P1 | 404 TASK_NOT_FOUND |
| TSK-026 | PUT /tasks/:id | Creator updates full task | Positive | P0 | 200 updated |
| TSK-027 | PUT /tasks/:id | Admin updates full task | Positive | P0 | 200 updated |
| TSK-028 | PUT /tasks/:id | Assignee but not creator/admin tries full update | Security | P0 | 403 FORBIDDEN |
| TSK-029 | PUT /tasks/:id | project_id changed to invalid project | Negative | P1 | 404 PROJECT_NOT_FOUND |
| TSK-030 | PATCH /tasks/:id/status | Assignee updates status | Positive | P0 | 200 updated |
| TSK-031 | PATCH /tasks/:id/status | Creator updates status | Positive | P0 | 200 updated |
| TSK-032 | PATCH /tasks/:id/status | Admin updates status | Positive | P0 | 200 updated |
| TSK-033 | PATCH /tasks/:id/status | Unauthorized user updates status | Security | P0 | 403 FORBIDDEN |
| TSK-034 | PATCH /tasks/:id/status | Payload includes title (disallowed) | Negative | P1 | 400 INVALID_STATUS_UPDATE |
| TSK-035 | PATCH /tasks/:id/status | Empty body | Negative | P1 | 400 MISSING_BODY |
| TSK-036 | PATCH /tasks/bulk-update | Admin bulk update valid task IDs | Positive | P0 | 200 count matches updates |
| TSK-037 | PATCH /tasks/bulk-update | Non-admin bulk update | Security | P0 | 403 FORBIDDEN |
| TSK-038 | PATCH /tasks/bulk-update | task_ids not array | Negative | P1 | 400 INVALID_TASK_IDS |
| TSK-039 | PATCH /tasks/bulk-update | task_ids empty array | Boundary | P1 | 400 INVALID_TASK_IDS |
| TSK-040 | PATCH /tasks/bulk-update | updates missing | Negative | P1 | 400 MISSING_UPDATE_FIELDS |
| TSK-041 | PATCH /tasks/bulk-update | project_id in updates should be ignored | Security | P1 | No project_id change |
| TSK-042 | DELETE /tasks/:id | Creator deletes task | Positive | P0 | 200 deleted |
| TSK-043 | DELETE /tasks/:id | Admin deletes task | Positive | P0 | 200 deleted |
| TSK-044 | DELETE /tasks/:id | Non-creator/non-admin deletes | Security | P0 | 403 FORBIDDEN |
| TSK-045 | DELETE /tasks/:id | Invalid ID | Negative | P1 | 400 INVALID_USER_ID |

---

## 6) Comments

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| CMT-001 | GET /tasks/:id/comments | Existing task comments list | Positive | P1 | 200 comments[] |
| CMT-002 | GET /tasks/:id/comments | Task not found | Negative | P1 | 404 TASK_NOT_FOUND |
| CMT-003 | POST /tasks/:id/comments | Valid comment | Positive | P0 | 201 comment created |
| CMT-004 | POST /tasks/:id/comments | Missing body | Negative | P1 | 400 MISSING_BODY |
| CMT-005 | POST /tasks/:id/comments | Missing content | Negative | P1 | 400 MISSING_FIELD |
| CMT-006 | POST /tasks/:id/comments | content length < 2 | Boundary | P1 | 400 INVALID_CONTENT |
| CMT-007 | POST /tasks/:id/comments | content length > 2000 | Boundary | P1 | 400 INVALID_CONTENT |
| CMT-008 | DELETE /comments/:id | Author deletes own comment | Positive | P0 | 200 deleted |
| CMT-009 | DELETE /comments/:id | Admin deletes any comment | Positive | P0 | 200 deleted |
| CMT-010 | DELETE /comments/:id | Other user deletes comment | Security | P0 | 403 FORBIDDEN |
| CMT-011 | DELETE /comments/:id | Non-existing comment | Negative | P1 | 404 COMMENT_NOT_FOUND |

---

## 7) Analytics & Audit Logs

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| ANL-001 | GET /analytics/summary | Admin token returns global summary | Positive | P0 | users/projects/tasks/audit_logs sections present |
| ANL-002 | GET /analytics/summary | User token returns user-centric summary | Positive | P0 | profile/projects/tasks sections present |
| ANL-003 | GET /analytics/summary | No token | Security | P0 | 401 |
| ANL-004 | GET /analytics/summary | Schema contract for totals non-negative | Integration | P1 | all counters are integers >= 0 |
| AUD-001 | GET /audit-logs | Admin token valid | Positive | P0 | 200 logs[] + pagination |
| AUD-002 | GET /audit-logs | Non-admin token | Security | P0 | 403 FORBIDDEN |
| AUD-003 | GET /audit-logs | actor_id invalid | Negative | P1 | 400 INVALID_USER_ID |
| AUD-004 | GET /audit-logs | filter by entity_type and action | Positive | P2 | logs filtered correctly |
| AUD-005 | GET /audit-logs | sort/order/page/per_page params valid | Positive | P2 | pagination deterministic |

---

## 8) Cross-Cutting Validation Tests

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| VAL-001 | IDs | ID="abc" across all /:id routes | Negative | P1 | 400 invalid ID error |
| VAL-002 | IDs | ID=0 across all /:id routes | Boundary | P1 | 400 invalid ID error |
| VAL-003 | Pagination | page=-1 for list endpoints | Boundary | P1 | 400 INVALID_PAGE |
| VAL-004 | Pagination | per_page=101 for list endpoints | Boundary | P1 | 400 INVALID_PER_PAGE |
| VAL-005 | Sorting | sort_order invalid (up/down) | Negative | P1 | 400 INVALID_SORT_ORDER |
| VAL-006 | Content-Type | Missing JSON content-type but JSON body | Integration | P2 | handled consistently |
| VAL-007 | Empty body | {} for required payload endpoints | Negative | P1 | proper MISSING_FIELD errors |
| VAL-008 | Whitespace fields | name/title/content with only spaces | Boundary | P1 | validation error |
| VAL-009 | Unicode text | non-ASCII in title/content | Positive | P3 | accepted and returned safely |
| VAL-010 | Large payload | long allowed max strings | Boundary | P2 | accepted at exact max |

---

## 9) Security Test Cases

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| SEC-001 | JWT | Missing Authorization header | Security | P0 | 401 |
| SEC-002 | JWT | Authorization header malformed | Security | P0 | 401 |
| SEC-003 | JWT | Tampered token signature | Security | P0 | 401 |
| SEC-004 | JWT | Token from deleted user | Security | P1 | 404/401 handled safely |
| SEC-005 | AuthZ | User escalates role in /me update | Security | P0 | role unchanged |
| SEC-006 | AuthZ | Non-admin accesses admin endpoints | Security | P0 | 403 |
| SEC-007 | AuthZ | User accesses others' user record | Security | P0 | 403 |
| SEC-008 | Input | SQL injection string in q/filter inputs | Security | P1 | no crash, safe error/sanitized output |
| SEC-009 | Input | XSS payload in comments/title | Security | P1 | stored/retrieved as plain text, no execution |
| SEC-010 | Error handling | Internal errors expose stack traces | Security | P1 | generic error messages only |
| SEC-011 | Brute force | repeated invalid login attempts | Security | P2 | consistent 401 responses, no data leakage |

---

## 10) Reliability and Data Integrity

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| REL-001 | Consistency | Create->Read->Update->Delete user flow | Integration | P0 | state transitions are correct |
| REL-002 | Consistency | Create project then tasks under project | Integration | P0 | task links valid project_id |
| REL-003 | Integrity | Delete task then fetch comments list | Integration | P1 | no orphan behavior errors |
| REL-004 | Audit | Verify audit entries for create/update/delete | Integration | P1 | expected action rows present |
| REL-005 | Reset | Mutate data then POST /reset | Reliability | P0 | seed state restored predictably |
| REL-006 | Idempotency | Re-delete already deleted record | Reliability | P2 | 404 deterministic |
| REL-007 | Parallel updates | Two updates on same task quickly | Reliability | P2 | no corruption; last write deterministic |
| REL-008 | Date handling | due_date timezone boundary around midnight | Boundary | P3 | consistent storage and filtering |

---

## 11) End-to-End Regression Flows

| ID | Flow | Steps | Priority | Expected Result |
|---|---|---|---|---|
| E2E-001 | New user onboarding | register -> login -> GET /me -> create project -> create task -> add comment | P0 | All operations succeed and objects are linked correctly |
| E2E-002 | Admin lifecycle | admin login -> create user -> promote role -> list users -> delete user | P0 | All admin operations succeed with proper audit logs |
| E2E-003 | Project lifecycle | login -> create project -> update -> archive -> delete | P0 | Status transitions and permissions enforced |
| E2E-004 | Task lifecycle | login -> create task -> update -> patch status -> bulk update (admin) -> delete | P0 | Valid transitions and role restrictions enforced |
| E2E-005 | Access control | user tries admin endpoints and foreign resources | P0 | All blocked with 403 |

---

## 12) Suggested Automation Split

- API smoke pack: UTL-001, AUTH-020, AUTH-027, USR-001, PRJ-001, TSK-001, ANL-001
- Auth & security pack: AUTH-022..AUTH-036, SEC-001..SEC-011
- CRUD regression pack: USR, PRJ, TSK, CMT full positive + key negative
- Contract pack: response schema checks for all list/detail endpoints
- Data reset pack: REL-005 + E2E-001 rerun after reset

---

## Execution Notes

1. Run `POST /reset` before every major suite for deterministic data.
2. Keep separate tokens for admin and normal user.
3. Validate both HTTP status and response body fields (`status`, `message`, `data`, `error_code`).
4. Capture request/response evidence for failed tests (payload, headers, timestamp).
5. Re-run P0/P1 cases on every release candidate.

---

## 13) Frontend Test Cases (for separate frontend repo)

Use these against the frontend repository: https://github.com/Hashir-Akram/REACT_FRONTEND_API_TESTING.git

| ID | Feature | Scenario | Type | Priority | Expected Result |
|---|---|---|---|---|---|
| FE-001 | Login page | Valid admin login | Positive | P0 | Redirect to dashboard, token stored |
| FE-002 | Login page | Valid user login | Positive | P0 | Redirect to user dashboard |
| FE-003 | Login page | Invalid password | Negative | P0 | Error alert shown, no token saved |
| FE-004 | Login page | Missing email/password | Negative | P1 | Inline or API validation error shown |
| FE-005 | Routing | Open protected route without token | Security | P0 | Redirect to login |
| FE-006 | Routing | Expired/invalid token in storage | Security | P0 | User logged out and redirected |
| FE-007 | Navbar/Logout | Click logout | Positive | P0 | Token cleared, redirected to login |
| FE-008 | Dashboard | Admin sees admin metrics/widgets | Positive | P1 | Admin cards and counts rendered |
| FE-009 | Dashboard | User sees user-specific metrics | Positive | P1 | User cards rendered correctly |
| FE-010 | Profile | Update profile valid data | Positive | P1 | Success message and updated values |
| FE-011 | Profile | Update with duplicate email | Negative | P1 | API error surfaced correctly |
| FE-012 | Users page | Admin list users | Positive | P0 | Table loads with pagination |
| FE-013 | Users page | Non-admin opens /users | Security | P0 | Access blocked/redirected |
| FE-014 | Users page | Admin create user valid | Positive | P1 | New user appears in list |
| FE-015 | Users page | Admin create invalid payload | Negative | P1 | Form/API validation errors |
| FE-016 | Users page | Admin edit user role | Positive | P1 | Role updated in UI |
| FE-017 | Users page | Admin delete user | Positive | P1 | Row removed and success toast |
| FE-018 | Projects page | Load projects list | Positive | P0 | Projects displayed with statuses |
| FE-019 | Projects page | Create project valid | Positive | P1 | Project appears in list |
| FE-020 | Projects page | Update project as owner | Positive | P1 | Changes persisted |
| FE-021 | Projects page | Archive project | Positive | P1 | Status becomes archived |
| FE-022 | Tasks page | Load tasks with filters | Positive | P0 | Filtered tasks shown correctly |
| FE-023 | Tasks page | Create task valid | Positive | P1 | Task appears in list |
| FE-024 | Tasks page | Create task invalid | Negative | P1 | Validation error shown |
| FE-025 | Tasks page | Update task status | Positive | P1 | Status badge updates |
| FE-026 | Tasks page | Bulk update (admin only) | Security | P1 | Visible and functional only for admin |
| FE-027 | Comments | Add comment on task | Positive | P1 | Comment appears instantly |
| FE-028 | Comments | Delete own comment | Positive | P1 | Comment removed |
| FE-029 | Activity logs | Admin opens logs page | Positive | P1 | Logs loaded with filters |
| FE-030 | Activity logs | Non-admin logs access | Security | P0 | Access denied/redirected |
| FE-031 | About page | Endpoint documentation visible | Positive | P3 | Endpoint groups render correctly |
| FE-032 | Error handling | Backend 500 response | Reliability | P1 | Friendly error message shown |
| FE-033 | Error handling | Backend offline/unreachable | Reliability | P0 | Network error handled, app does not crash |
| FE-034 | Responsiveness | Mobile viewport major pages | Integration | P2 | Layout usable without overlap |
| FE-035 | Browser compat | Chrome/Edge/Firefox smoke | Integration | P2 | Core flows pass in each browser |
| FE-036 | Accessibility | Keyboard-only navigation | Integration | P2 | Focus order and controls usable |

