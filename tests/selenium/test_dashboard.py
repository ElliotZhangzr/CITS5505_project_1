"""
Selenium Test Suite: Dashboard, Portfolio, and Trading UI

This test file verifies the visible dashboard behaviours of the Flask stock
trading web app.

Test coverage:
1. Authenticated user can access the dashboard.
2. Dashboard stock display areas load correctly.
3. Buy/sell interaction section is visible.
4. Portfolio holdings area is visible.
5. Portfolio summary values are displayed.
6. Market overview area is visible.
7. Dashboard API endpoints return accessible data for logged-in users.
8. Unauthenticated users cannot access dashboard-related API data.

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
# Test 1 - Dashboard page loads for logged-in user
# -------------------------------------------------
def test_dashboard_page_loads_after_login(driver):
    login(driver)

    assert "/dashboard" in driver.current_url
    assert "stock trading dashboard" in driver.page_source.lower()


# -------------------------------------------------
# Test 2 - Dashboard shows stock chart/display area
# -------------------------------------------------
def test_dashboard_stock_display_area_visible(driver):
    login(driver)

    page = driver.page_source.lower()

    assert "stock chart area" in page
    assert "$0.00" in page or "current price" in page


# -------------------------------------------------
# Test 3 - Buy/Sell interaction area is visible
# -------------------------------------------------
def test_dashboard_buy_sell_area_visible(driver):
    login(driver)

    page = driver.page_source.lower()

    assert "buy/sell interaction area" in page
    assert "stock symbol" in page
    assert "quantity" in page
    assert "buy" in page
    assert "sell" in page


# -------------------------------------------------
# Test 4 - Portfolio holdings area is visible
# -------------------------------------------------
def test_dashboard_portfolio_holdings_area_visible(driver):
    login(driver)

    page = driver.page_source.lower()

    assert "portfolio holdings area" in page
    assert "symbol" in page
    assert "qty" in page
    assert "avg price" in page
    assert "current price" in page
    assert "market value" in page


# -------------------------------------------------
# Test 5 - Portfolio summary values are visible
# -------------------------------------------------
def test_dashboard_portfolio_summary_visible(driver):
    login(driver)

    page = driver.page_source.lower()

    assert "stock value" in page
    assert "total assets" in page
    assert "realized p/l" in page
    assert "unrealized p/l" in page
    assert "total p/l" in page


# -------------------------------------------------
# Test 6 - Market overview area is visible
# -------------------------------------------------
def test_dashboard_market_overview_area_visible(driver):
    login(driver)

    assert "market overview area" in driver.page_source.lower()


# -------------------------------------------------
# Test 7 - Logged-in user can access stock API data
# -------------------------------------------------
def test_logged_in_user_can_access_stocks_api(driver):
    login(driver)

    driver.get(f"{BASE_URL}/api/stocks")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert "login" not in page
    assert "unauthorized" not in page


# -------------------------------------------------
# Test 8 - Logged-in user can access portfolio API data
# -------------------------------------------------
def test_logged_in_user_can_access_portfolio_api(driver):
    login(driver)

    driver.get(f"{BASE_URL}/api/portfolio")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert "cash" in page
    assert "stock" in page or "holdings" in page or "total" in page


# -------------------------------------------------
# Test 9 - Unauthenticated user cannot access dashboard
# -------------------------------------------------
def test_unauthenticated_user_cannot_access_dashboard(driver):
    driver.get(f"{BASE_URL}/dashboard")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )

    assert "/login" in driver.current_url