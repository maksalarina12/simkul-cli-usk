from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
from zoneinfo import ZoneInfo
import re
import time

BASE_URL = "https://simkuliah.usk.ac.id"
WIB = ZoneInfo("Asia/Jakarta")


# ─────────────────────────────────────────
# HELPER: PARSE SEL PERTEMUAN
# ─────────────────────────────────────────

def _parse_sel_pertemuan(sel_text: str, kode_mk: str, nama_mk: str, nomor_pertemuan: int) -> dict | None:
    """
    Parse teks dalam satu sel pertemuan menjadi dict.
    Return None kalau sel kosong.
    """
    if not sel_text.strip():
        return None

    hasil = {
        "pertemuan": nomor_pertemuan,
        "kode_mk": kode_mk,
        "nama_mk": nama_mk,
        "dosen": "-",
        "tanggal_str": "-",
        "tanggal": None,
        "hari": "-",
        "ruang": "-",
        "jam": "-",
    }

    # Parse nama dosen
    match_nama = re.search(r"Nama\s*:\s*(.+)", sel_text)
    if match_nama:
        hasil["dosen"] = match_nama.group(1).strip()

    # Parse hari dan tanggal — format: "Rabu, 25-02-2026"
    match_tanggal = re.search(r"Hari, tanggal\s*:\s*(\w+),\s*(\d{2}-\d{2}-\d{4})", sel_text)
    if match_tanggal:
        hasil["hari"] = match_tanggal.group(1).strip()
        hasil["tanggal_str"] = match_tanggal.group(2).strip()
        try:
            hasil["tanggal"] = datetime.strptime(hasil["tanggal_str"], "%d-%m-%Y").date()
        except ValueError:
            pass

    # Parse ruang
    match_ruang = re.search(r"Ruang\s*:\s*(.+)", sel_text)
    if match_ruang:
        hasil["ruang"] = match_ruang.group(1).strip()

    # Parse jam — format: "14.00 - 15.40"
    match_jam = re.search(r"Jam\s*:\s*([\d.]+ - [\d.]+)", sel_text)
    if match_jam:
        hasil["jam"] = match_jam.group(1).strip()

    return hasil


# ─────────────────────────────────────────
# JADWAL SEMESTER
# ─────────────────────────────────────────

def get_jadwal_semester(driver) -> list[dict]:
    """
    Scrape tabel jadwal semester penuh.
    Return list of dict, satu dict per pertemuan per MK.
    """
    driver.get(f"{BASE_URL}/index.php/jadwal_kuliah/index")
    time.sleep(3)
    
    print("URL sekarang:", driver.current_url)
    print("Cookies aktif di driver:", driver.get_cookies())
    print("Jumlah rows ditemukan:", len(driver.find_elements(By.CSS_SELECTOR, "#simpletable tbody tr")))


    hasil = []

    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "#simpletable tbody tr")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 3:
                continue

            kode_mk = cols[0].text.strip()

            # Nama MK: ambil baris pertama saja (sebelum \n)
            nama_mk_full = cols[1].text.strip()
            nama_mk = nama_mk_full.split("\n")[0].strip()

            # Pertemuan 1–16 ada di cols[2] sampai cols[17]
            for i, sel in enumerate(cols[2:18], start=1):
                sel_text = sel.text.strip()
                record = _parse_sel_pertemuan(sel_text, kode_mk, nama_mk, i)
                if record:
                    hasil.append(record)

    except NoSuchElementException:
        pass

    return hasil


# ─────────────────────────────────────────
# JADWAL AKTIF HARI INI
# ─────────────────────────────────────────

def get_jadwal_aktif_hari_ini(jadwal_semester: list[dict]) -> list[dict]:
    """
    Filter jadwal semester berdasarkan tanggal hari ini.
    Cocokkan berdasarkan tanggal persis, bukan hanya hari.
    """
    hari_ini = datetime.now(WIB).date()

    return [
        mk for mk in jadwal_semester
        if mk.get("tanggal") == hari_ini
    ]


# ─────────────────────────────────────────
# ABSENSI
# ─────────────────────────────────────────

def do_absen(driver) -> dict:
    """
    Navigasi ke halaman absensi dan klik semua tombol absen yang tersedia.
    Return dict berisi status dan jumlah absen yang berhasil.
    """
    driver.get(f"{BASE_URL}/index.php/absensi")
    time.sleep(2)

    hasil = {
        "berhasil": 0,
        "tidak_ada_jadwal": False,
        "pesan": "",
    }

    for i in range(2):
        try:
            absen_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-success"))
            )
            driver.execute_script("arguments[0].click();", absen_button)
            time.sleep(2)

            konfirmasi = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "confirm"))
            )
            driver.execute_script("arguments[0].click();", konfirmasi)
            time.sleep(3)

            hasil["berhasil"] += 1

        except TimeoutException:
            break

    if hasil["berhasil"] == 0:
        hasil["tidak_ada_jadwal"] = True
        hasil["pesan"] = "Tidak ada tombol absen yang tersedia."
    else:
        hasil["pesan"] = f"{hasil['berhasil']} absensi berhasil dilakukan."

    return hasil