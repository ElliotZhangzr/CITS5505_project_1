"""
Selenium Test Suite: Profile Functionality

Test coverage:
1. Logged-in user can access the profile page.
2. Profile page displays username.
3. Email is hidden by default and reveal button is visible.
4. Assets & Holdings section is visible.
5. Bio section and save button are visible.
6. Achievements section is visible.
7. Delete account button and modal are available.
8. Unauthenticated users are redirected to login.

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
# Test 1 - Profile page loads for logged-in user
# -------------------------------------------------
def test_profile_page_loads(driver):
    login(driver)

    driver.get(f"{BASE_URL}/profile")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/profile")
    )

    assert "/profile" in driver.current_url
    assert "profile" in driver.page_source.lower()


# -------------------------------------------------
# Test 2 - Profile page displays username
# -------------------------------------------------
def test_profile_displays_username(driver):
    login(driver)

    driver.get(f"{BASE_URL}/profile")

    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "profile-username"))
    )

    assert USERNAME.lower() in username.text.lower()


# -------------------------------------------------
# Test 3 - Email is hidden by default and reveal button exists
# -------------------------------------------------
def test_profile_email_hidden_by_default(driver):
    login(driver)

    driver.get(f"{BASE_URL}/profile")

    email_text = driver.find_element(By.ID, "emailText")
    reveal_button = driver.find_element(By.ID, "revealEmailBtn")

    assert "••••" in email_text.text
    assert reveal_button.is_displayed()
    assert "show" in reveal_button.text.lower()


# -------------------------------------------------
# Test 4 - Assets and holdings section is visible
# -------------------------------------------------
def test_profile_assets_and_holdings_visible(driver):
    login(driver)

    driver.get(f"{BASE_URL}/profile")

    page = driver.page_source.lower()

    assert "assets" in page
    assert "holdings" in page
    assert "available cash" in page
    assert "stock value" in page
    assert "total assets" in page
    assert "total p/l" in page


# -------------------------------------------------
# Test 5 - Bio section is visible
# -------------------------------------------------
def test_profile_bio_section_visible(driver):
    login(driver)

    driver.get(f"{BASE_URL}/profile")

    bio_textarea = driver.find_element(By.ID, "bioText")
    save_button = driver.find_element(By.ID, "saveBioBtn")

    assert bio_textarea.is_displayed()
    assert save_button.is_displayed()
    assert "save" in save_button.text.lower()


# -------------------------------------------------
# Test 6 - Achievements section is visible
# -------------------------------------------------
def test_profile_achievements_section_visible(driver):
    login(driver)

    driver.get(f"{BASE_URL}/profile")

    page = driver.page_source.lower()

    assert "achievements" in page
    assert "unlock progress" in page


# -------------------------------------------------
# Test 7 - Delete account button and modal exist
# -------------------------------------------------
def test_profile_delete_account_modal_available(driver):
    login(driver)

    driver.get(f"{BASE_URL}/profile")

    delete_button = driver.find_element(By.ID, "deleteAccountBtn")
    delete_modal = driver.find_element(By.ID, "deleteModal")

    assert delete_button.is_displayed()
    assert "delete account" in delete_button.text.lower()
    assert delete_modal is not None


# -------------------------------------------------
# Test 8 - Unauthenticated user cannot access profile
# -------------------------------------------------
def test_unauthenticated_user_cannot_access_profile(driver):
    driver.get(f"{BASE_URL}/profile")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )

    assert "/login" in driver.current_url