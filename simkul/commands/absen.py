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
def absen(
    auto: bool = typer.Option(False, "--auto", help="Mode daemon: absen otomatis sesuai jadwal.")
):
    """Lakukan absensi sekarang, atau jalankan mode otomatis dengan --auto."""

    if not is_logged_in():
        console.print("\n[yellow]Kamu belum login. Jalankan [bold]simkul login[/bold] dulu.[/yellow]")
        raise typer.Exit()

    if auto:
        _mode_auto()
    else:
        _mode_manual()


def _mode_manual():
    """Absen sekali sekarang."""
    console.print("\n[bold green]Memulai absensi...[/bold green]")

    driver = _get_driver_dengan_session()
    if not driver:
        console.print("[red]Session tidak valid. Silakan login ulang dengan [bold]simkul login[/bold].[/red]")
        raise typer.Exit()

    try:
        hasil = do_absen(driver)

        if hasil["tidak_ada_jadwal"]:
            console.print(Panel(
                "[yellow]Tidak ada jadwal absen saat ini.[/yellow]",
                title="Info",
                expand=False,
            ))
            kirim_notif("info", "Tidak Ada Jadwal", "Bot berjalan, tapi tidak ada jadwal absen.")
        else:
            console.print(Panel(
                f"[bold green]✓ {hasil['pesan']}[/bold green]\n"
                "[dim]Harap verifikasi manual di SimKuliah.[/dim]",
                title="Absen Berhasil",
                expand=False,
            ))
            kirim_notif("sukses", "Absen Berhasil", hasil["pesan"])

    except Exception as e:
        console.print(f"\n[red]Error saat absen: {e}[/red]")
        kirim_notif("error", "Absen ERROR", str(e))

    finally:
        driver.quit()


def _mode_auto():
    """
    Daemon mode: scrape jadwal hari ini, tunggu sampai jam mulai, lalu absen.
    """
    from simkul.core.scraper import get_jadwal_semester, get_jadwal_aktif_hari_ini
    from datetime import datetime
    from zoneinfo import ZoneInfo

    WIB = ZoneInfo("Asia/Jakarta")

    console.print("\n[bold green]Mode Auto Aktif[/bold green]")
    console.print("[dim]Mengambil jadwal hari ini...[/dim]\n")

    driver = _get_driver_dengan_session()
    if not driver:
        console.print("[red]Session tidak valid. Silakan login ulang.[/red]")
        raise typer.Exit()

    try:
        jadwal_semester = get_jadwal_semester(driver)
        jadwal_hari_ini = get_jadwal_aktif_hari_ini(jadwal_semester)

        if not jadwal_hari_ini:
            console.print("[yellow]Tidak ada jadwal kuliah hari ini.[/yellow]")
            kirim_notif("info", "Tidak Ada Jadwal", "Tidak ada MK hari ini.")
            return

        for mk in jadwal_hari_ini:
            console.print(f"[bold]{mk['nama_mk']}[/bold] — {mk['jam']} — {mk['ruang']}")

        # Ambil jam mulai MK pertama
        jam_str = jadwal_hari_ini[0]["jam"].split("-")[0].strip()  # e.g. "08:00"
        jam_mulai = datetime.strptime(jam_str, "%H:%M").replace(
            year=datetime.now(WIB).year,
            month=datetime.now(WIB).month,
            day=datetime.now(WIB).day,
            tzinfo=WIB,
        )

        now = datetime.now(WIB)
        selisih = (jam_mulai - now).total_seconds()

        if selisih > 0:
            console.print(f"\n[dim]Menunggu {int(selisih // 60)} menit sebelum absen...[/dim]")
            time.sleep(selisih)

        # Absen
        hasil = do_absen(driver)
        console.print(f"\n[bold green]✓ {hasil['pesan']}[/bold green]")
        kirim_notif("sukses", "Absen Berhasil (Auto)", hasil["pesan"])

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        kirim_notif("error", "Absen ERROR", str(e))

    finally:
        driver.quit()