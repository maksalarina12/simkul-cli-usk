import typer
from rich.console import Console
from rich.table import Table

from simkul.core.browser import create_driver, inject_cookies, is_session_valid
from simkul.core.scraper import get_jadwal_semester, get_jadwal_aktif_hari_ini
from simkul.core.session import load_session, is_logged_in
from simkul.core.cache import save_jadwal_cache, load_jadwal_cache, get_cache_info

app = typer.Typer()
console = Console()


def _get_driver_dengan_session():
    """Helper: buat driver, inject session, cek validitas."""
    session = load_session()
    if not session:
        return None

    driver = create_driver(headless=True)
    inject_cookies(driver, session["cookies"])

    if not is_session_valid(driver):
        driver.quit()
        return None

    return driver


def _tampilkan_tabel(judul: str, jadwal: list[dict]):
    """Render jadwal sebagai tabel Rich di terminal."""
    if not jadwal:
        console.print(f"\n[yellow]Tidak ada jadwal untuk ditampilkan.[/yellow]")
        return

    table = Table(title=judul, show_lines=True)
    table.add_column("Pertemuan", style="dim", justify="center")
    table.add_column("Tanggal", style="cyan")
    table.add_column("Mata Kuliah", style="bold white")
    table.add_column("Jam", style="green")
    table.add_column("Ruang", style="yellow")
    table.add_column("Dosen", style="magenta")

    for mk in jadwal:
        table.add_row(
            str(mk.get("pertemuan", "-")),
            mk.get("tanggal_str", "-"),
            mk.get("nama_mk", "-"),
            mk.get("jam", "-"),
            mk.get("ruang", "-"),
            mk.get("dosen", "-"),
        )

    console.print()
    console.print(table)


def _scrape_dan_cache(driver) -> list[dict]:
    """Scrape jadwal semester dan simpan ke cache."""
    console.print("\n[dim]Mengambil jadwal dari SimKuliah...[/dim]")
    jadwal = get_jadwal_semester(driver)
    save_jadwal_cache(jadwal)
    info = get_cache_info()
    console.print(f"[dim]Jadwal disimpan ke cache ({info['jumlah']} pertemuan).[/dim]")
    return jadwal


@app.command()
def jadwal(
    semester: bool = typer.Option(False, "--semester", "-s"),
    refresh: bool = typer.Option(False, "--refresh", "-r"),
):
    if not is_logged_in():
        console.print("\n[yellow]Belum login.[/yellow]")
        raise typer.Exit()

    cache = load_jadwal_cache()
    print("DEBUG cache:", type(cache), len(cache) if cache else None)

    if cache and not refresh:
        # STOP DI SINI — jangan buka browser sama sekali
        info = get_cache_info()
        console.print(f"\n[dim]Pakai cache (disimpan: {info['scraped_at'][:16].replace('T', ' ')})[/dim]")
        jadwal_data = cache
    else:
        driver = _get_driver_dengan_session()  # baru buka browser di sini
        if not driver:
            console.print("[red]Session tidak valid.[/red]")
            raise typer.Exit()
        try:
            jadwal_data = _scrape_dan_cache(driver)
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            raise typer.Exit()
        finally:
            driver.quit()

    if semester:
        _tampilkan_tabel("Jadwal Kuliah Semester", jadwal_data)
    else:
        jadwal_hari_ini = get_jadwal_aktif_hari_ini(jadwal_data)
        _tampilkan_tabel("Jadwal Kuliah Hari Ini", jadwal_hari_ini)
        
def tampilkan_jadwal(semester: bool = False, refresh: bool = False):
    """Versi non-Typer dari jadwal(), dipanggil langsung dari TUI."""
    if not is_logged_in():
        console.print("\n[yellow]Belum login.[/yellow]")
        return

    cache = load_jadwal_cache()

    if cache and not refresh:
        info = get_cache_info()
        console.print(f"\n[dim]Pakai cache (disimpan: {info['scraped_at'][:16].replace('T', ' ')})[/dim]")
        jadwal_data = cache
    else:
        driver = _get_driver_dengan_session()
        if not driver:
            console.print("[red]Session tidak valid.[/red]")
            return
        try:
            jadwal_data = _scrape_dan_cache(driver)
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            return
        finally:
            driver.quit()

    if semester:
        _tampilkan_tabel("Jadwal Kuliah Semester", jadwal_data)
    else:
        jadwal_hari_ini = get_jadwal_aktif_hari_ini(jadwal_data)
        _tampilkan_tabel("Jadwal Kuliah Hari Ini", jadwal_hari_ini)