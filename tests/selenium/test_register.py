import time
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


def unique_user():
    timestamp = int(time.time())
    return {
        "username": f"seleniumuser{timestamp}",
        "email": f"seleniumuser{timestamp}@example.com",
        "password": "Testuser1"
    }


def test_register_page_loads(driver):
    driver.get(f"{BASE_URL}/register")

    assert "register" in driver.page_source.lower()
    assert driver.find_element(By.NAME, "username")
    assert driver.find_element(By.NAME, "email")
    assert driver.find_element(By.NAME, "password")


def test_valid_registration_redirects_to_dashboard(driver):
    user = unique_user()

    driver.get(f"{BASE_URL}/register")

    driver.find_element(By.NAME, "username").send_keys(user["username"])
    driver.find_element(By.NAME, "email").send_keys(user["email"])
    driver.find_element(By.NAME, "password").send_keys(user["password"])

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


def test_duplicate_username_or_email_shows_error(driver):
    driver.get(f"{BASE_URL}/register")

    driver.find_element(By.NAME, "username").send_keys("testuser1")
    driver.find_element(By.NAME, "email").send_keys("testuser1@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("Testuser1")

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "flash-msg"))
    )

    page = driver.page_source.lower()

    assert (
        "username already exists" in page
        or "email already exists" in page
    )


def test_empty_register_form_stays_on_register_page(driver):
    driver.get(f"{BASE_URL}/register")

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    assert "/register" in driver.current_url


def test_register_page_has_login_link(driver):
    driver.get(f"{BASE_URL}/register")

    assert "login" in driver.page_source.lower()