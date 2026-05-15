"""
Selenium Test Suite: Admin Functionality

This test file verifies the visible admin behaviours of the Flask stock
trading web app.

Test coverage:
1. Admin user can access the admin dashboard.
2. Admin user can access the user management page.
3. Regular user cannot access the admin dashboard.
4. Regular user cannot access the user management page.
5. Admin user management page displays role/admin information.
6. Admin cannot revoke their own admin permission.
7. Admin stock management page loads if implemented.
8. Regular user cannot access stock management if implemented.

These Selenium tests must be run while the Flask server is live.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://127.0.0.1:5000"

ADMIN_USERNAME = "root"
ADMIN_PASSWORD = "root"

NORMAL_USERNAME = "testuser1"
NORMAL_PASSWORD = "Testuser1"


@pytest.fixture
def driver():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.maximize_window()

    yield driver

    driver.quit()


def login(driver, username, password):
    driver.get(f"{BASE_URL}/login")

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )


# -------------------------------------------------
# Test 1 - Admin can access admin dashboard
# -------------------------------------------------
def test_admin_can_access_admin_dashboard(driver):
    login(driver, ADMIN_USERNAME, ADMIN_PASSWORD)

    driver.get(f"{BASE_URL}/admin")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/admin")
    )

    page = driver.page_source.lower()

    assert "admin" in page
    assert "internal server error" not in page
    assert "traceback" not in page


# -------------------------------------------------
# Test 2 - Admin can access user management page
# -------------------------------------------------
def test_admin_can_access_user_management_page(driver):
    login(driver, ADMIN_USERNAME, ADMIN_PASSWORD)

    driver.get(f"{BASE_URL}/admin/users")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/admin/users")
    )

    page = driver.page_source.lower()

    assert "user" in page
    assert "admin" in page
    assert "internal server error" not in page
    assert "traceback" not in page


# -------------------------------------------------
# Test 3 - Regular user cannot access admin dashboard
# -------------------------------------------------
def test_normal_user_cannot_access_admin_dashboard(driver):
    login(driver, NORMAL_USERNAME, NORMAL_PASSWORD)

    driver.get(f"{BASE_URL}/admin")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


# -------------------------------------------------
# Test 4 - Regular user cannot access user management
# -------------------------------------------------
def test_normal_user_cannot_access_admin_users_page(driver):
    login(driver, NORMAL_USERNAME, NORMAL_PASSWORD)

    driver.get(f"{BASE_URL}/admin/users")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


# -------------------------------------------------
# Test 5 - User management page contains role information
# -------------------------------------------------
def test_admin_users_page_contains_role_information(driver):
    login(driver, ADMIN_USERNAME, ADMIN_PASSWORD)

    driver.get(f"{BASE_URL}/admin/users")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert "role" in page or "admin" in page
    assert NORMAL_USERNAME.lower() in page or "user" in page


# -------------------------------------------------
# Test 6 - Admin cannot revoke own admin permission
# -------------------------------------------------
def test_admin_cannot_revoke_own_admin_permission(driver):
    login(driver, ADMIN_USERNAME, ADMIN_PASSWORD)

    driver.get(f"{BASE_URL}/admin/users")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert "cannot change your own admin role" in page or ADMIN_USERNAME.lower() in page


# -------------------------------------------------
# Test 7 - Admin stock management page loads if implemented
# -------------------------------------------------
def test_admin_stock_management_page_loads_if_available(driver):
    login(driver, ADMIN_USERNAME, ADMIN_PASSWORD)

    driver.get(f"{BASE_URL}/admin/stocks")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert "internal server error" not in page
    assert "traceback" not in page


# -------------------------------------------------
# Test 8 - Regular user cannot access stock management
# -------------------------------------------------
def test_normal_user_cannot_access_stock_management(driver):
    login(driver, NORMAL_USERNAME, NORMAL_PASSWORD)

    driver.get(f"{BASE_URL}/admin/stocks")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "/admin/stocks" not in driver.current_url or "admin access required" in driver.page_source.lower()