import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture
def driver():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.maximize_window()

    yield driver

    driver.quit()


# -------------------------------------------------
# Test 1 - Login page loads correctly
# -------------------------------------------------
def test_login_page_loads(driver):
    driver.get(f"{BASE_URL}/login")

    assert "login" in driver.page_source.lower()

    assert driver.find_element(By.NAME, "username")
    assert driver.find_element(By.NAME, "password")


# -------------------------------------------------
# Test 2 - Valid login redirects to dashboard
# -------------------------------------------------
def test_valid_login_redirects_to_dashboard(driver):
    driver.get(f"{BASE_URL}/login")

    driver.find_element(By.NAME, "username").send_keys("testuser1")

    driver.find_element(By.NAME, "password").send_keys("Testuser1")

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


# -------------------------------------------------
# Test 3 - Invalid login shows error message
# -------------------------------------------------
def test_invalid_login_shows_error_message(driver):
    driver.get(f"{BASE_URL}/login")

    driver.find_element(By.NAME, "username").send_keys("wronguser")

    driver.find_element(By.NAME, "password").send_keys("wrongpassword")

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert (
        "username or password incorrect"
        in driver.page_source.lower()
    )


# -------------------------------------------------
# Test 4 - Empty login form stays on login page
# -------------------------------------------------
def test_empty_login_form_stays_on_login_page(driver):
    driver.get(f"{BASE_URL}/login")

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    assert "/login" in driver.current_url


# -------------------------------------------------
# Test 5 - Logout redirects back to login
# -------------------------------------------------
def test_logout_redirects_to_login(driver):
    driver.get(f"{BASE_URL}/login")

    driver.find_element(By.NAME, "username").send_keys("testuser1")

    driver.find_element(By.NAME, "password").send_keys("Testuser1")

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    driver.get(f"{BASE_URL}/logout")

    WebDriverWait(driver, 5).until(
        EC.url_contains("/login")
    )

    assert "/login" in driver.current_url