import typer
import time
from rich.console import Console
from rich.panel import Panel

from simkul.core.browser import create_driver, inject_cookies, is_session_valid
from simkul.core.scraper import do_absen
from simkul.core.session import load_session, is_logged_in
from simkul.utils.notify import kirim_notif

app = typer.Typer()
console = Console()


def _get_driver_dengan_session():
    """
    Helper: buat driver, inject session cookies, cek validitas.
    Return driver jika valid, None jika tidak.
    """
    session = load_session()
    if not session:
        return None

    driver = create_driver(headless=True)
    inject_cookies(driver, session["cookies"])

    if not is_session_valid(driver):
        driver.quit()
        return None

    return driver

@app.command()
def absen():
    if not is_logged_in():
        console.print("\n[yellow]Kamu belum login. Jalankan [bold]simkul login[/bold] dulu.[/yellow]")
        raise typer.Exit()

    _mode_manual()


def _mode_manual():
    from simkul.core.cache import load_jadwal_cache
    from simkul.core.scraper import get_jadwal_aktif_hari_ini
    from InquirerPy import inquirer

    console.print("\n[bold green]Memulai absensi...[/bold green]")

    cache = load_jadwal_cache()
    if cache:
        jadwal_hari_ini = get_jadwal_aktif_hari_ini(cache)
        if not jadwal_hari_ini:
            console.print("\n[yellow]Tidak ada jadwal kuliah hari ini berdasarkan cache.[/yellow]")
            lanjut = inquirer.confirm(
                message="Tetap mau coba absen?", default=False
            ).execute()
            if not lanjut:
                return
        else:
            # Ada jadwal hari ini, tapi cek apakah sudah waktunya
            from datetime import datetime
            from zoneinfo import ZoneInfo
            WIB = ZoneInfo("Asia/Jakarta")
            now = datetime.now(WIB)
            
            # Ambil jam mulai MK pertama hari ini
            jam_str = jadwal_hari_ini[0]["jam"].split("-")[0].strip().replace(".", ":")
            jam_mulai = datetime.strptime(jam_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=WIB
            )
            
            if now < jam_mulai:
                selisih_menit = int((jam_mulai - now).total_seconds() // 60)
                console.print(f"\n[yellow]Jadwal terdekat: {jadwal_hari_ini[0]['nama_mk']} jam {jadwal_hari_ini[0]['jam']}[/yellow]")
                console.print(f"[yellow]Masih {selisih_menit} menit lagi.[/yellow]")
                lanjut = inquirer.confirm(
                    message="Tetap mau coba absen sekarang?", default=False
                ).execute()
                if not lanjut:
                    return


    # Lanjut absen
    driver = _get_driver_dengan_session()
    if not driver:
        console.print("[red]Session tidak valid. Silakan login ulang.[/red]")
        raise typer.Exit()

    try:
        hasil = do_absen(driver)
        if hasil["tidak_ada_jadwal"]:
            console.print(Panel(
                "[yellow]Tidak ada tombol absen yang tersedia.[/yellow]",
                title="Info", expand=False,
            ))
            kirim_notif("info", "Tidak Ada Jadwal", "Tidak ada tombol absen.")
        else:
            console.print(Panel(
                f"[bold green]✓ {hasil['pesan']}[/bold green]\n"
                "[dim]Harap verifikasi manual di SimKuliah.[/dim]",
                title="Absen Berhasil", expand=False,
            ))
            kirim_notif("sukses", "Absen Berhasil", hasil["pesan"])
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        kirim_notif("error", "Absen ERROR", str(e))
    finally:
        driver.quit()
