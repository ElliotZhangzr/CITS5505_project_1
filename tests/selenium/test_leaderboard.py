"""
Selenium Test Suite: Leaderboard Functionality

This test file verifies the visible leaderboard behaviours of the Flask stock
trading web app.

Test coverage:
1. Authenticated user can access the leaderboard page.
2. Total assets ranking tab loads without crashing.
3. Cash ranking tab loads without crashing.
4. Profit ranking tab loads without crashing.
5. Return ranking tab loads without crashing.
6. Leaderboard displays ranking/user information.
7. Current logged-in user's cash or account information is visible.
8. Invalid leaderboard type does not crash the page.

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
PASSWORD = "Testuser1"


@pytest.fixture
def driver():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.maximize_window()

    yield driver

    driver.quit()


def login(driver):
    driver.get(f"{BASE_URL}/login")

    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )


# -------------------------------------------------
# Test 1 - Leaderboard page loads for logged-in user
# -------------------------------------------------
def test_leaderboard_page_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/leaderboard")
    )

    page = driver.page_source.lower()

    assert "leaderboard" in page
    assert "rank" in page or "ranking" in page


# -------------------------------------------------
# Test 2 - Total assets ranking tab loads
# -------------------------------------------------
def test_total_assets_tab_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=assets")

    WebDriverWait(driver, 10).until(
        EC.url_contains("type=assets")
    )

    page = driver.page_source.lower()

    assert "total assets" in page
    assert "leaderboard" in page


# -------------------------------------------------
# Test 3 - Cash ranking tab loads
# -------------------------------------------------
def test_cash_tab_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=cash")

    WebDriverWait(driver, 10).until(
        EC.url_contains("type=cash")
    )

    page = driver.page_source.lower()

    assert "cash" in page
    assert "leaderboard" in page


# -------------------------------------------------
# Test 4 - Profit ranking tab loads
# -------------------------------------------------
def test_profit_tab_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=profit")

    WebDriverWait(driver, 10).until(
        EC.url_contains("type=profit")
    )

    page = driver.page_source.lower()

    assert "profit" in page
    assert "leaderboard" in page


# -------------------------------------------------
# Test 5 - Return ranking tab loads
# -------------------------------------------------
def test_return_tab_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=return")

    WebDriverWait(driver, 10).until(
        EC.url_contains("type=return")
    )

    page = driver.page_source.lower()

    assert "return" in page
    assert "leaderboard" in page


# -------------------------------------------------
# Test 6 - Leaderboard displays user/ranking data
# -------------------------------------------------
def test_leaderboard_displays_user_or_ranking_data(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=assets")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert USERNAME.lower() in page or "user" in page
    assert "rank" in page or "ranking" in page or "#" in page


# -------------------------------------------------
# Test 7 - Current user cash/account information is visible
# -------------------------------------------------
def test_current_user_cash_or_account_info_visible(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=cash")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert USERNAME.lower() in page or "cash" in page
    assert "$" in page or "cash" in page


# -------------------------------------------------
# Test 8 - Invalid leaderboard type does not crash page
# -------------------------------------------------
def test_invalid_leaderboard_type_does_not_crash(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=invalid")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/leaderboard")
    )

    page = driver.page_source.lower()

    assert "leaderboard" in page
    assert "internal server error" not in page
    assert "traceback" not in page