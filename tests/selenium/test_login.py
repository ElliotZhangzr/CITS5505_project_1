"""
Selenium Test Suite: Login and Logout Functionality

This test file verifies the main authentication behaviours of the Flask web app.

Test coverage:
1. Login page loads correctly.
2. User can log in with a valid username and password.
3. User can log in with a valid email and password.
4. Invalid username/password login shows an error message.
5. Non-existent email login is rejected.
6. Empty login form stays on the login page.
7. Unauthenticated users are redirected to login when accessing dashboard.
8. Logout redirects user back to login.
9. Dashboard cannot be accessed after logout.

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

USERNAME = "testuser1"
USER_EMAIL = "testuser1@gmail.com"
PASSWORD = "Testuser1"


@pytest.fixture
def driver():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.maximize_window()

    yield driver

    driver.quit()


def login(driver, username_or_email=USERNAME, password=PASSWORD):
    driver.get(f"{BASE_URL}/login")

    driver.find_element(By.NAME, "username").send_keys(username_or_email)
    driver.find_element(By.NAME, "password").send_keys(password)

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()


# -------------------------------------------------
# Test 1 - Login page loads correctly
# -------------------------------------------------
def test_login_page_loads(driver):
    driver.get(f"{BASE_URL}/login")

    assert "login" in driver.page_source.lower()

    assert driver.find_element(By.NAME, "username")
    assert driver.find_element(By.NAME, "password")


# -------------------------------------------------
# Test 2 - Valid username login redirects to dashboard
# -------------------------------------------------
def test_valid_username_login_redirects_to_dashboard(driver):
    login(driver, USERNAME, PASSWORD)

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


# -------------------------------------------------
# Test 3 - Valid email login redirects to dashboard
# -------------------------------------------------
def test_valid_email_login_redirects_to_dashboard(driver):
    login(driver, USER_EMAIL, PASSWORD)

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


# -------------------------------------------------
# Test 4 - Invalid login shows error message
# -------------------------------------------------
def test_invalid_login_shows_error_message(driver):
    login(driver, "wronguser", "wrongpassword")

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "/login" in driver.current_url
    assert (
        "username or password incorrect"
        in driver.page_source.lower()
    )


# -------------------------------------------------
# Test 5 - Non-existent email cannot login
# -------------------------------------------------
def test_non_existent_email_cannot_login(driver):
    login(driver, "notexist@example.com", PASSWORD)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "/login" in driver.current_url
    assert (
        "username or password incorrect"
        in driver.page_source.lower()
    )


# -------------------------------------------------
# Test 6 - Empty login form stays on login page
# -------------------------------------------------
def test_empty_login_form_stays_on_login_page(driver):
    driver.get(f"{BASE_URL}/login")

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    assert "/login" in driver.current_url


# -------------------------------------------------
# Test 7 - Unauthenticated user redirects to login
# -------------------------------------------------
def test_unauthenticated_user_redirected_to_login(driver):
    driver.get(f"{BASE_URL}/dashboard")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )

    assert "/login" in driver.current_url


# -------------------------------------------------
# Test 8 - Logout redirects back to login
# -------------------------------------------------
def test_logout_redirects_to_login(driver):
    login(driver, USERNAME, PASSWORD)

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    driver.get(f"{BASE_URL}/logout")

    WebDriverWait(driver, 5).until(
        EC.url_contains("/login")
    )

    assert "/login" in driver.current_url


# -------------------------------------------------
# Test 9 - Dashboard cannot be accessed after logout
# -------------------------------------------------
def test_dashboard_blocked_after_logout(driver):
    login(driver, USERNAME, PASSWORD)

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    driver.get(f"{BASE_URL}/logout")

    WebDriverWait(driver, 5).until(
        EC.url_contains("/login")
    )

    driver.get(f"{BASE_URL}/dashboard")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )

    assert "/login" in driver.current_url