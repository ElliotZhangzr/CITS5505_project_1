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

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )


def test_admin_can_access_admin_dashboard(driver):
    login(driver, ADMIN_USERNAME, ADMIN_PASSWORD)

    driver.get(f"{BASE_URL}/admin")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/admin")
    )

    assert "admin" in driver.page_source.lower()


def test_admin_can_access_user_management_page(driver):
    login(driver, ADMIN_USERNAME, ADMIN_PASSWORD)

    driver.get(f"{BASE_URL}/admin/users")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/admin/users")
    )

    assert "registered users" in driver.page_source.lower()
    assert "user management" in driver.page_source.lower()


def test_normal_user_cannot_access_admin_dashboard(driver):
    login(driver, NORMAL_USERNAME, NORMAL_PASSWORD)

    driver.get(f"{BASE_URL}/admin")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


def test_normal_user_cannot_access_admin_users_page(driver):
    login(driver, NORMAL_USERNAME, NORMAL_PASSWORD)

    driver.get(f"{BASE_URL}/admin/users")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


def test_admin_users_page_contains_role_information(driver):
    login(driver, ADMIN_USERNAME, ADMIN_PASSWORD)

    driver.get(f"{BASE_URL}/admin/users")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert "role" in page
    assert "admin" in page or "normal user" in page