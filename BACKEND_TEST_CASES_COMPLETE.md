# Backend Test Cases - Complete Documentation

This document provides complete backend API test coverage with step-by-step execution guidance.
Use this file for manual API testing, Postman collections, or automation frameworks (pytest, requests, REST Assured).

## 1. Scope

Covered areas:
- Authentication and profile
- Role-based access control (RBAC)
- Users, Projects, Tasks, Comments CRUD
- Analytics and audit logs
- Lab endpoints (echo/status/delay/flaky/headers/paginate/upload/versioning/sanity)
- Security and error behavior

## 2. Environment Setup

- Base URL (local): `http://127.0.0.1:5000/api`
- Health URL: `http://127.0.0.1:5000/health`
- Admin user: `admin@example.com / Admin@123`
- User user: `john@example.com / User@123`
- Tester user: `sara@example.com / Tester@123`

### 2.1 Get JWT Token

```bash
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin@123"}'
```

Use returned token in all protected calls:

`Authorization: Bearer <token>`

## 3. Authentication Test Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-AUTH-001 | `POST /api/register` | Send valid name/email/age/password payload. | `201` and created user object returned. |
| BE-AUTH-002 | `POST /api/register` | Re-register with same email. | `409` duplicate/validation error. |
| BE-AUTH-003 | `POST /api/login` | Login with valid admin credentials. | `200`, token + user details. |
| BE-AUTH-004 | `POST /api/login` | Login with invalid password. | `401` unauthorized error. |
| BE-AUTH-005 | `GET /api/me` | Send valid token in Authorization header. | `200`, current user profile. |
| BE-AUTH-006 | `GET /api/me` | Call without token. | `401` missing auth token. |
| BE-AUTH-007 | `PUT /api/me` | Update own profile (name/age/email). | `200`, updated profile returned. |
| BE-AUTH-008 | `PUT /api/me` | Update with invalid email or weak password. | `400` validation failure. |

## 4. RBAC and Access Control Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-RBAC-001 | `GET /api/users` | Call with admin token. | `200` users list returned. |
| BE-RBAC-002 | `GET /api/users` | Call with non-admin token. | `403` forbidden. |
| BE-RBAC-003 | `POST /api/users` | Non-admin attempts user creation. | `403` forbidden. |
| BE-RBAC-004 | `POST /reset` | Call without token. | `401` unauthorized. |
| BE-RBAC-005 | `POST /reset` | Call with non-admin token. | `403` forbidden. |
| BE-RBAC-006 | `POST /reset` | Call with admin token. | `200`, reset success message. |

## 5. Users API Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-USR-001 | `GET /api/users?page=1&per_page=10` | Call as admin. | `200`, paginated users + metadata. |
| BE-USR-002 | `GET /api/users?sort_by=name&sort_order=asc` | Sort by field. | `200`, sorted list. |
| BE-USR-003 | `GET /api/users?role=user` | Filter by role. | `200`, only matching roles. |
| BE-USR-004 | `POST /api/users` | Create user with valid payload. | `201`, user created. |
| BE-USR-005 | `GET /api/users/{id}` | Read existing user. | `200`, user details. |
| BE-USR-006 | `PUT /api/users/{id}` | Update selected fields. | `200`, fields updated. |
| BE-USR-007 | `DELETE /api/users/{id}` | Delete a normal user. | `200`, delete success. |
| BE-USR-008 | `DELETE /api/users/{id}` | Delete non-existing ID. | `404` not found. |

## 6. Projects API Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-PRJ-001 | `GET /api/projects` | Call with token. | `200`, project list. |
| BE-PRJ-002 | `GET /api/projects?q=website` | Search by keyword. | `200`, filtered projects. |
| BE-PRJ-003 | `POST /api/projects` | Create project with valid payload. | `201`, project created. |
| BE-PRJ-004 | `GET /api/projects/{id}` | Read one project. | `200`, project details. |
| BE-PRJ-005 | `PUT /api/projects/{id}` | Update title/description/status. | `200`, updated project. |
| BE-PRJ-006 | `PATCH /api/projects/{id}/archive` | Archive active project. | `200`, status archived. |
| BE-PRJ-007 | `DELETE /api/projects/{id}` | Delete project. | `200`, deletion success. |
| BE-PRJ-008 | `PUT /api/projects/{id}` | Invalid status value. | `400` validation error. |

## 7. Tasks API Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-TSK-001 | `GET /api/tasks` | Call with token. | `200`, task list. |
| BE-TSK-002 | `GET /api/tasks?status=todo&priority=high` | Filter tasks. | `200`, filtered tasks. |
| BE-TSK-003 | `POST /api/tasks` | Create task with valid project and assignee. | `201`, task created. |
| BE-TSK-004 | `GET /api/tasks/{id}` | Read task by ID. | `200`, task detail. |
| BE-TSK-005 | `PUT /api/tasks/{id}` | Update title/status/priority. | `200`, updated task returned. |
| BE-TSK-006 | `PATCH /api/tasks/{id}/status` | Patch status/priority only. | `200`, status updated. |
| BE-TSK-007 | `PATCH /api/tasks/bulk-update` | Admin bulk update multiple IDs. | `200`, affected count returned. |
| BE-TSK-008 | `DELETE /api/tasks/{id}` | Delete task. | `200`, deletion success. |

## 8. Comments API Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-CMT-001 | `GET /api/tasks/{id}/comments` | Read comments for a task. | `200`, comments list. |
| BE-CMT-002 | `POST /api/tasks/{id}/comments` | Add comment content. | `201`, comment created. |
| BE-CMT-003 | `DELETE /api/comments/{id}` | Delete own/admin comment. | `200`, comment deleted. |
| BE-CMT-004 | `POST /api/tasks/{id}/comments` | Empty content payload. | `400` validation error. |

## 9. Analytics and Audit Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-ANA-001 | `GET /api/analytics/summary` | Call as authenticated user. | `200`, dashboard stats object. |
| BE-ANA-002 | `GET /api/audit-logs` | Call as admin. | `200`, audit log list and metadata. |
| BE-ANA-003 | `GET /api/audit-logs?action=created` | Filter audit action. | `200`, filtered result set. |
| BE-ANA-004 | `GET /api/audit-logs` | Call as non-admin. | `403` forbidden. |

## 10. Lab Endpoint Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-LAB-001 | `GET /api/echo?foo=bar` | Send query params. | `200`, method/url/query reflected. |
| BE-LAB-002 | `POST /api/echo` | Send JSON body. | `200`, body reflected in response. |
| BE-LAB-003 | `GET /api/status/404` | Request status simulator. | HTTP response code is exactly `404`. |
| BE-LAB-004 | `GET /api/status/999` | Unsupported status code. | `400`, unsupported code message. |
| BE-LAB-005 | `GET /api/delay/3` | Measure elapsed time. | Response arrives after about 3 seconds. |
| BE-LAB-006 | `GET /api/delay/15` | Out-of-range delay. | `400` invalid delay. |
| BE-LAB-007 | `GET /api/flaky?fail_rate=0.5` | Execute 10 times. | Mixed success/failure responses. |
| BE-LAB-008 | `GET /api/headers` | Send custom header `X-Test: qa`. | Header is visible in reflected response. |
| BE-LAB-009 | `GET /api/paginate?page=2&per_page=5` | Paginated fetch. | `200`, page metadata + 5 items. |
| BE-LAB-010 | `POST /api/upload` | Upload allowed file type. | `200`, filename/type/size metadata. |
| BE-LAB-011 | `POST /api/upload` | Upload unsupported extension. | `400` invalid file type. |
| BE-LAB-012 | `POST /api/sanity` | Send SQLi/XSS-like payload fields. | `200`, flagged_fields contains risky keys. |
| BE-LAB-013 | `GET /api/v1/users` | Call with admin token. | `200`, minimal user fields only. |
| BE-LAB-014 | `GET /api/v2/users` | Call with admin token. | `200`, full fields + pagination/changelog. |
| BE-LAB-015 | `GET /api/v1/users` | Call with non-admin token. | `403` forbidden. |

## 11. Health and Error Handling Cases

| Case ID | Endpoint | How To Do It | Expected Result |
|---|---|---|---|
| BE-OPS-001 | `GET /health` | Call without token. | `200`, service health details. |
| BE-OPS-002 | Invalid route `/api/unknown` | Send request to unknown path. | `404` not found error body. |
| BE-OPS-003 | Protected endpoint without token | Call `/api/users` without auth header. | `401` unauthorized. |

## 12. Suggested Execution Order

1. Health check
2. Login and token capture
3. RBAC checks (admin vs user)
4. CRUD flows (Users -> Projects -> Tasks -> Comments)
5. Analytics/Audit checks
6. Lab endpoints and resiliency tests
7. Negative and security test payloads

## 13. Minimal cURL Examples

### Create project

```bash
curl -X POST http://127.0.0.1:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"QA Project","description":"Backend test run","status":"active"}'
```

### Create task

```bash
curl -X POST http://127.0.0.1:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"API validation","description":"Run contract checks","project_id":1,"status":"todo","priority":"high"}'
```

### Lab security sanity check

```bash
curl -X POST http://127.0.0.1:5000/api/sanity \
  -H "Content-Type: application/json" \
  -d '{"name":"<script>alert(1)</script>","query":"\" OR 1=1 --"}'
```

## 14. Pass/Fail Criteria

- Pass when actual status code, response schema, and business behavior match expected result.
- Fail when status code mismatches, response contract breaks, auth checks fail open, or validation does not trigger.
- Always capture request payload, response body, headers, and timestamp for failures.
