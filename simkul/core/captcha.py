import ddddocr
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ocr = ddddocr.DdddOcr(show_ad=False)

def get_captcha_image(driver) -> bytes:
    """Ambil gambar CAPTCHA tai """
    wait = WebDriverWait(driver, 10)
    captcha_img = wait.until(
        EC.presence_of_element_located((By.ID, "captcha-img"))
    )
    return captcha_img.screenshot_as_png

def solve_captcha(image_bytes: bytes) -> str:
    """Solve CAPTCHA """
    result = ocr.classification(image_bytes)
    return result.strip().replace(" ", "")