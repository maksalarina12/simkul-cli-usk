import typer
from rich.console import Console
from InquirerPy import inquirer

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


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Jalankan simkul tanpa subcommand untuk masuk mode interaktif."""
    if ctx.invoked_subcommand is not None:
        return

    console.print("\n[bold green]Selamat datang di simkul-cli![/bold green]")
    console.print("[dim]CLI tool untuk SimKuliah USK[/dim]\n")

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