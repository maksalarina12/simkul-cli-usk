import typer
import time
from rich.console import Console
from rich.panel import Panel
from InquirerPy import inquirer

from simkul.core.browser import create_driver, create_wait, is_session_valid, inject_cookies
from simkul.core.captcha import get_captcha_image, solve_captcha
from simkul.core.session import save_session, delete_session, load_session, is_logged_in
from simkul.utils.config import set as config_set, get as config_get, clear as config_clear

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

app = typer.Typer()
console = Console()

BASE_URL = "https://simkuliah.usk.ac.id"

@app.command()
def login():
    """Login ke SimKuliah dan simpan session."""

    if is_logged_in():
        npm = config_get("npm", "Unknown")
        console.print(f"\n[yellow]Kamu sudah login sebagai [bold]{npm}[/bold].[/yellow]")
        konfirmasi = inquirer.confirm(
            message="Mau login ulang?", default=False
        ).execute()
        if not konfirmasi:
            return

    console.print("\n[bold green]Login SimKuliah[/bold green]\n")

    npm = inquirer.text(message="NPM:").execute()
    password = inquirer.secret(message="Password:").execute()

    console.print("\n[dim]Membuka browser...[/dim]")
    driver = create_driver(headless=True)

    try:
        driver.get(BASE_URL)
        wait = create_wait(driver)

        # Isi form login
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(npm)
        driver.find_element(By.NAME, "password").send_keys(password)

        # Solve CAPTCHA
        console.print("[dim]Menyelesaikan CAPTCHA...[/dim]")
        captcha_bytes = get_captcha_image(driver)
        captcha_text = solve_captcha(captcha_bytes)
        console.print(f"[dim]CAPTCHA terbaca: {captcha_text}[/dim]")

        # Isi field CAPTCHA
        driver.find_element(By.NAME, "captcha_answer").send_keys(captcha_text)

        # Klik tombol login
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        ).click()
        time.sleep(3)

        # Cek apakah login berhasil
        if "login" in driver.current_url.lower():
            console.print("\n[red]Login gagal! Cek NPM, password, atau CAPTCHA salah terbaca.[/red]")
            console.print("[dim]Tips: Coba jalankan simkul login lagi.[/dim]")
            return

        # Simpan session dan config
        cookies = driver.get_cookies()
        save_session(cookies, npm)
        config_set("npm", npm)

        console.print(f"\n[bold green]✓ Login berhasil sebagai {npm}![/bold green]")

    except Exception as e:
        console.print(f"\n[red]Terjadi error: {e}[/red]")

    finally:
        driver.quit()


@app.command()
def logout():
    """Hapus session dan logout."""
    if not is_logged_in():
        console.print("\n[yellow]Kamu belum login.[/yellow]")
        return

    npm = config_get("npm")
    delete_session()
    config_clear()
    console.print(f"\n[bold green]✓ Logout berhasil. Sampai jumpa, {npm}![/bold green]")


@app.command()
def whoami():
    """Tampilkan info akun yang sedang login."""
    if not is_logged_in():
        console.print("\n[yellow]Kamu belum login. Jalankan [bold]simkul login[/bold] dulu.[/yellow]")
        return

    session = load_session()
    console.print(Panel(
        f"[bold]NPM:[/bold] {session['npm']}\n"
        f"[bold]Login sejak:[/bold] {session['saved_at']}\n"
        f"[bold]Session expire:[/bold] {session['expires_at']}",
        title="[bold green]Info Akun[/bold green]",
        expand=False,
    ))