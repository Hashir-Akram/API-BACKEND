# Level 2 Practical Project - UI Automation Testing (Selenium + Python)

## 1. Project Objective
Build a practical UI automation framework for the provided frontend application using Selenium WebDriver with Python.

Students must automate critical user flows and advanced browser interaction scenarios while following production-style engineering practices.

Core objective:
- Create a maintainable framework.
- Automate realistic test cases.
- Run tests in parallel on Selenium Grid (3 nodes).
- Make execution CI/CD friendly.

---

## 2. Application Modules to Test
Automate the following modules:

1. Authentication Module
- Login with valid and invalid credentials
- Logout flow

2. Dashboard Module
- Verify post-login landing and role-based content

3. Projects and Tasks Module
- Create, search, update, and validate entities

4. Access Control Module
- Admin-only pages behavior for non-admin users

5. Browser Interaction Module (Test Scenarios page)
- Alerts (alert/confirm/prompt)
- Frames (iframe switching)
- Multiple tabs/windows (new tab + popup)

---

## 3. Required Automation Tasks
Students must implement all requirements below:

1. Framework Design
- Use Page Object Model
- Keep locators and test data reusable
- Separate concerns (tests/pages/utils/config)

2. Reusable Utilities
- WebDriver factory
- Wait helper (explicit waits)
- Logger helper
- Screenshot helper on failure

3. Parameterization
- Run at least one test with multiple input datasets (e.g., invalid login matrix)

4. Browser Interaction Coverage
- Handle alerts
- Handle iframes
- Handle multiple tabs/windows

5. Reporting and Debugging
- Attach screenshots on failure
- Store logs under logs/
- Generate Allure report

6. Parallel Execution
- Execute suite in parallel against Selenium Grid
- Must run on 3 nodes in parallel

---

## 4. Mandatory Test Cases (8)

### TC01 - Valid Admin Login
Objective: Verify successful login using admin credentials.

Steps:
1. Open login page.
2. Enter valid admin email/password.
3. Click Login.
4. Wait for dashboard.

Expected Result:
- Dashboard loads.
- Logged-in user/role indicator appears.

### TC02 - Invalid Login Matrix (Parameterized)
Objective: Validate login error behavior for multiple invalid inputs.

Steps:
1. Run test with data rows:
- invalid password
- invalid email format
- empty email/password
2. Submit form for each row.

Expected Result:
- Proper error message appears.
- User stays on login page.

### TC03 - Admin Users Page Access
Objective: Verify admin can access Users page.

Steps:
1. Login as admin.
2. Navigate to Users module.

Expected Result:
- Users table/list is visible.

### TC04 - Non-Admin Access Restriction
Objective: Verify non-admin cannot access admin-only page.

Steps:
1. Login as normal user.
2. Try to open Users or Activity page.

Expected Result:
- Access denied or redirected behavior.

### TC05 - Project Creation Flow
Objective: Verify user can create and validate a new project.

Steps:
1. Login.
2. Open Projects page.
3. Create project with valid data.
4. Search/filter for created project.

Expected Result:
- Project appears with expected values.

### TC06 - Task Status Update
Objective: Verify task status can be changed and persisted.

Steps:
1. Open Tasks page.
2. Select a task.
3. Change status (e.g., todo to in_progress).
4. Refresh/check list.

Expected Result:
- Updated status remains visible.

### TC07 - Alerts Handling
Objective: Validate alert, confirm, and prompt interactions on Test Scenarios page.

Steps:
1. Open Test Scenarios page.
2. Trigger alert and accept.
3. Trigger confirm and dismiss/accept.
4. Trigger prompt and enter text.

Expected Result:
- All dialogs handled successfully.
- Result labels update correctly.

### TC08 - Frames and Window/Tab Handling
Objective: Validate frame switching and multi-window handling.

Steps:
1. Open Test Scenarios page.
2. Switch into iframe and verify content.
3. Open new tab and validate URL/title.
4. Open popup window and switch back.

Expected Result:
- Correct context switching with no stale/no such window errors.

---

## 5. Framework Structure Expectations
Use this structure:

```text
ui-automation-level2/
  tests/
    test_auth.py
    test_dashboard.py
    test_projects_tasks.py
    test_access_control.py
    test_browser_interactions.py
  pages/
    base_page.py
    login_page.py
    dashboard_page.py
    users_page.py
    projects_page.py
    tasks_page.py
    test_scenarios_page.py
  utils/
    driver_factory.py
    wait_utils.py
    screenshot_utils.py
    logger.py
    data_loader.py
  config/
    settings.py
    locators.py
    test_data.json
    grid_config.json
  reports/
  logs/
  conftest.py
  pytest.ini
  requirements.txt
  README.md
```

---

## 6. CI/CD Friendly Requirements (Mandatory)
Framework must support non-interactive CI execution.

1. Headless-friendly driver execution.
2. Environment variable based configuration:
- BASE_URL
- GRID_URL
- BROWSER
- HEADLESS

3. Deterministic output :
- Allure results
- logs
- screenshots on failures

4. Exit with proper non-zero code on failure.

5. No hardcoded local paths.

6. No sleep-based synchronization for core checks (use explicit waits).

---

## 7. Selenium Grid Parallel Execution (3 Nodes - Mandatory)
Students must run tests in parallel against Selenium Grid with exactly 3 nodes.

### Example docker-compose for Grid
```yaml
version: '3.8'
services:
  selenium-hub:
    image: selenium/hub:4.21.0
    container_name: selenium-hub
    ports:
      - "4444:4444"

  chrome-node-1:
    image: selenium/node-chrome:4.21.0
    shm_size: 2gb
    depends_on:
      - selenium-hub
    environment:
      - SE_EVENT_BUS_HOST=selenium-hub
      - SE_EVENT_BUS_PUBLISH_PORT=4442
      - SE_EVENT_BUS_SUBSCRIBE_PORT=4443

  chrome-node-2:
    image: selenium/node-chrome:4.21.0
    shm_size: 2gb
    depends_on:
      - selenium-hub
    environment:
      - SE_EVENT_BUS_HOST=selenium-hub
      - SE_EVENT_BUS_PUBLISH_PORT=4442
      - SE_EVENT_BUS_SUBSCRIBE_PORT=4443

  chrome-node-3:
    image: selenium/node-chrome:4.21.0
    shm_size: 2gb
    depends_on:
      - selenium-hub
    environment:
      - SE_EVENT_BUS_HOST=selenium-hub
      - SE_EVENT_BUS_PUBLISH_PORT=4442
      - SE_EVENT_BUS_SUBSCRIBE_PORT=4443
```

### Expected execution command
```bash
pytest -n 3 --dist=loadscope --alluredir=reports/allure-results --junitxml=reports/junit.xml
```

---

## 8. Bonus Challenge (Optional)
Implement cross-browser parallel execution on Grid:
- Run same suite on Chrome and Edge in matrix mode.
- Compare pass rate and flaky behavior.

---

## 9. Deliverables
Students must submit:

1. Complete framework source code.
2. Test execution output (console summary + junit xml).
3. Failure screenshots.
4. logs/ folder.
5. Allure results and generated Allure HTML report.
6. README with setup and run commands (local + grid + CI).

---

## 10. Evaluation Rubric (Suggested)
- Framework design and code quality: 25%
- Test stability and wait strategy: 20%
- Browser interaction handling (alerts/frames/windows): 20%
- Parallel Grid execution (3 nodes): 15%
- Reporting/logging/screenshots: 10%
- CI/CD readiness and documentation: 10%

---

This assignment is intentionally realistic and aligned to industry-style UI automation delivery.
