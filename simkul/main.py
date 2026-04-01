import typer
from rich.console import Console
from InquirerPy import inquirer

import random
from datetime import datetime
from zoneinfo import ZoneInfo
from rich.console import Console
from rich.text import Text

from simkul.commands.auth import app as auth_app, login, logout, whoami
from simkul.commands.absen import app as absen_app, absen
from simkul.commands.jadwal import app as jadwal_app, jadwal, tampilkan_jadwal
from simkul.utils.notify import setup_notif


app = typer.Typer(
    name="simkul",
    help="CLI tool untuk SimKuliah USK — absensi otomatis, jadwal, dan lebih.",
    no_args_is_help=False,
)

console = Console()

# Daftarkan subcommands
app.command(name="login")(login)
app.command(name="logout")(logout)
app.command(name="whoami")(whoami)
app.command(name="absen")(absen)
app.command(name="jadwal")(jadwal)


@app.command(name="config")
def config_cmd():
    """Setup konfigurasi simkul (notifikasi, preferensi)."""
    setup_notif()

LOGO = """
  ███████╗██╗███╗   ███╗██╗  ██╗██╗   ██╗██╗      
  ██╔════╝██║████╗ ████║██║ ██╔╝██║   ██║██║      
  ███████╗██║██╔████╔██║█████╔╝ ██║   ██║██║      
  ╚════██║██║██║╚██╔╝██║██╔═██╗ ██║   ██║██║      
  ███████║██║██║ ╚═╝ ██║██║  ██╗╚██████╔╝███████╗ 
  ╚══════╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝"""

WARNA = ["cyan", "green", "blue", "magenta", "yellow"]

def show_banner():
    from simkul.utils.config import get as config_get
    from simkul.core.session import is_logged_in
    from simkul.core.cache import load_jadwal_cache
    from simkul.core.scraper import get_jadwal_aktif_hari_ini

    warna = random.choice(WARNA)
    WIB = ZoneInfo("Asia/Jakarta")
    now = datetime.now(WIB)

    # Logo
    console.print(f"[{warna}]{LOGO}[/{warna}]")
    console.print()
    console.print(f"  [dim]CLI tool untuk SimKuliah USK  v0.1.0[/dim]")
    console.print(f"  [dim]{'─' * 45}[/dim]")

    # Info user
    if is_logged_in():
        npm = config_get("npm", "-")
        console.print(f"  [white]User     [/white][{warna}]{npm}[/{warna}]")
    else:
        console.print(f"  [white]User     [/white][dim]Belum login[/dim]")

    # Hari
    hari_str = now.strftime("%A, %d %B %Y").replace(
        "Monday", "Senin").replace("Tuesday", "Selasa").replace(
        "Wednesday", "Rabu").replace("Thursday", "Kamis").replace(
        "Friday", "Jumat").replace("Saturday", "Sabtu").replace(
        "Sunday", "Minggu").replace("January", "Januari").replace(
        "February", "Februari").replace("March", "Maret").replace(
        "April", "April").replace("May", "Mei").replace(
        "June", "Juni").replace("July", "Juli").replace(
        "August", "Agustus").replace("September", "September").replace(
        "October", "Oktober").replace("November", "November").replace(
        "December", "Desember")
    console.print(f"  [white]Hari     [/white][dim]{hari_str}[/dim]")

    # Jadwal hari ini
    cache = load_jadwal_cache()
    if cache:
        jadwal_hari_ini = get_jadwal_aktif_hari_ini(cache)
        if jadwal_hari_ini:
            for i, mk in enumerate(jadwal_hari_ini):
                jam = mk['jam'].split('-')[0].strip()
                if i == 0:
                    console.print(f"  [white]Jadwal   [/white][dim]{mk['nama_mk']} {jam}[/dim]")
                else:
                    console.print(f"  [white]         [/white][dim]{mk['nama_mk']} {jam}[/dim]")
        else:
            console.print(f"  [white]Jadwal   [/white][dim]Tidak ada jadwal hari ini[/dim]")
    else:
        console.print(f"  [white]Jadwal   [/white][dim]Cache belum ada[/dim]")

    console.print(f"  [dim]{'─' * 45}[/dim]")
    console.print()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Jalankan simkul tanpa subcommand untuk masuk mode interaktif."""
    if ctx.invoked_subcommand is not None:
        return
    
    show_banner()

    pilihan = inquirer.select(
        message="Mau ngapain?",
        choices=[
            "Login",
            "Absen Sekarang",
            "Jadwal Hari Ini",
            "Jadwal Semester",
            "Update Jadwal",   
            "Setup Notifikasi",
            "Whoami",
            "Logout",
            "Keluar",
        ],
    ).execute()

    if pilihan == "Login":
        login()
    elif pilihan == "Absen Sekarang":
        absen(auto=False)
    elif pilihan == "Jadwal Hari Ini":
        tampilkan_jadwal(semester=False, refresh=False)
    elif pilihan == "Jadwal Semester":
        tampilkan_jadwal(semester=True, refresh=False)
    elif pilihan == "Update Jadwal":
        tampilkan_jadwal(semester=True, refresh=True)
    elif pilihan == "Setup Notifikasi":
        setup_notif()
    elif pilihan == "Whoami":
        whoami()
    elif pilihan == "Logout":
        logout()
    elif pilihan == "Keluar":
        raise typer.Exit()


if __name__ == "__main__":
    app()