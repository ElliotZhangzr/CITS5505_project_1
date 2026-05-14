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
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )


def test_leaderboard_page_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/leaderboard")
    )

    assert "leaderboard" in driver.page_source.lower()


def test_total_assets_tab_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=assets")

    WebDriverWait(driver, 10).until(
        EC.url_contains("type=assets")
    )

    assert "total assets" in driver.page_source.lower()


def test_cash_tab_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=cash")

    WebDriverWait(driver, 10).until(
        EC.url_contains("type=cash")
    )

    assert "cash" in driver.page_source.lower()


def test_profit_tab_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=profit")

    WebDriverWait(driver, 10).until(
        EC.url_contains("type=profit")
    )

    assert "profit" in driver.page_source.lower()


def test_return_tab_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/leaderboard?type=return")

    WebDriverWait(driver, 10).until(
        EC.url_contains("type=return")
    )

    assert "return" in driver.page_source.lower()