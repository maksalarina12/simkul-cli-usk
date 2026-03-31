from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time

BASE_URL = "https://simkuliah.usk.ac.id"

def create_driver(headless: bool = False) -> webdriver.Chrome:
    """Buat dan return Chrome WebDriver."""
    options = Options()

    if headless:
        options.add_argument("--headless")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    return driver

def create_wait(driver: webdriver.Chrome, timeout: int = 10) -> WebDriverWait:
    """Buat WebDriverWait dengan timeout tertentu."""
    return WebDriverWait(driver, timeout)

def inject_cookies(driver: webdriver.Chrome, cookies: list):
    """Inject cookies ke driver."""
    driver.get(BASE_URL)
    time.sleep(2)
    for cookie in cookies:
        try:
            cookie.pop("sameSite", None)
            driver.add_cookie(cookie)
        except Exception as e:
            pass
    # Navigate ulang setelah inject
    driver.get(BASE_URL)
    time.sleep(2)

def is_session_valid(driver: webdriver.Chrome) -> bool:
    """Cek apakah session masih valid — cukup cek URL sekarang."""
    current = driver.current_url.lower()
    print("DEBUG is_session_valid URL:", current)
    return "login" not in current